#!/bin/bash

if [[ $EUID -ne 0 ]]; then
    echo " "
    echo "*****************  This script must be executed as root *************" 1>&2
    exit 1
else
    echo " "
    echo " "
    echo "*********************************************************************"
    echo "*                                                                   *"
    echo "*        Now Installing Oracle Java Runtime 8 update 60             *"
    echo "*                                                                   *"
    echo "*********************************************************************"
fi

yum -y wget

wget --no-cookies --no-check-certificate --header "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com%2F; oraclelicense=accept-securebackup-cookie" "http://download.oracle.com/otn-pub/java/jdk/8u66-b17/jdk-8u66-linux-x64.rpm"

rpm -ivh jdk-8u66-linux-x64.rpm

echo "*********************************************************************"

