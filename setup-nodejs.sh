#!/bin/bash

if [[ $EUID -ne 0 ]]; then
    echo " "
    echo "*****************  This script must be executed as root *************" 1>&2
    exit 1
else
    echo "*********************************************************************"
    echo "*                                                                   *"
    echo "*        Installing Node.js from EPEL repository                    *"
    echo "*                                                                   *"
    echo "*********************************************************************"
fi

yum -y install epel-release

yum -y install nodejs

yum -y install npm



