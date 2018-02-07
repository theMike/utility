#!/bin/bash

if [[ $EUID -ne 0 ]]; then
    echo " "
    echo "******************* This script must be executed as root ************" 1>&2
    echo " "
    exit 1
else
    echo " "
    echo " "
    echo "*********************************************************************"
    echo "*                                                                   *"
    echo "*                Installing JBoss  eap  6.4                         *"
    echo "*                                                                   *"
    echo "*********************************************************************"
fi

LOCALIP=$(ip -o -4 addr show | awk -F '[/ ]+' '/global/ {print $4}')

JBOSSDIR="/opt/jboss"
JBOSSAS=jboss-eap-6.3
JBOSSCFG="$JBOSSDIR/$JBOSSAS/standalone/configuration/standalone.xml" 
JBOSSLIB="$JBOSSDIR/jboss-ocs-libs"

yum -y install unzip

cd $JBOSSDIR

unzip $JBOSSAS.0.zip

# extract the ocs configurations
mkdir "$JBOSSDIR/$JBOSSAS/standalone/configuration/ocs"
 
unzip ocs.zip -d "$JBOSSDIR/$JBOSSAS/standalone/configuration/ocs"

unzip jboss-ocs-libs.zip

cp -r $JBOSSLIB/mysql $JBOSSDIR/$JBOSSAS/modules/system/layers/base/com/
cp -r $JBOSSLIB/3.6.2 $JBOSSDIR/$JBOSSAS/modules/system/layers/base/org/jboss/netty/
cp -r $JBOSSLIB/1.7.3 $JBOSSDIR/$JBOSSAS/modules/system/layers/base/org/slf4j/
cp -r $JBOSSLIB/logback $JBOSSDIR/$JBOSSAS/modules/system/layers/base/ch/qos/
cp -r $JBOSSLIB/oracle $JBOSSDIR/$JBOSSAS/modules/system/layers/base/


cp $JBOSSCFG $JBOSSCFG.$(date +%y%m%d-%H%M).bak
cp $JBOSSDIR/standalone.xml.base $JBOSSCFG

echo "**** Updating config files with local IP: SLOCALIP"

#Update IP in standalone.xml
find . -name 'standalone.xml' | xargs sed -i.bak -r "s/([0-9]{1,3}\.){3}([0-9]{1,3})/$LOCALIP/g"

#Update IP in OCS config files
find . -name 'SIGMA.CONFIG.*.json' | xargs sed -i.bak -r "s/([0-9]{1,3}\.){3}([0-9]{1,3})/$LOCALIP/g"

#Clean up
rm -rf $JBOSSLIB


useradd -r jboss -d $JBOSSDIR/$JBOSSAS
chown jboss: -R $JBOSSDIR/$JBOSSAS 

#
#Add jboss console user and app
#
expect setup-jboss-add-ocs-user.sh
expect setup-jboss-add-sigmaapp.sh

VMNAME=$(hostname)

echo "$LOCALIP   $VMNAME" >> /etc/hosts

#
## setup service configuration
## TODO: Update process to use new systemd config files
#

cat > /usr/lib/systemd/system/jboss.service <<EOF
[Unit]
Description=Jboss 6.3 EAP

[Service]
Type=simple
ExecStart=$JBOSSDIR/$JBOSSAS/bin/standalone.sh
ExecStop=$JBOSSDIR/$JBOSSAS/bin/jboss-cli.sh --connect command=:shutdown --controller=$LOCALIP:9999

[Install]
WantedBy=multi-user.target

EOF

systemctl enable jboss
systemctl start jboss

echo "*********************************************************************"


