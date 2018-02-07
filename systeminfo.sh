#!/bin/bash

INFOFILE=/opt/systeminfo.txt

LOCALIP=$(ip  -o -4 addr show | awk -F '[/ ]+' '/global/ {print $4}')
echo " "
echo " "
echo "*******************************************************************************"
echo " "
echo "*  Updating System info file: $INFOFILE                                *"
echo "*  Node Name: $(uname -n)    IP: $LOCALIP                              *"
echo " "
echo "Node Name: $(uname -n)" >> $INFOFILE
echo "IP: $LOCALIP" >> $INFOFILE
echo "Filesystem: $(df -hT)" >> $INFOFILE
echo " "
echo "*******************************************************************************"
