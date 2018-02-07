#!/bin/sh
#
# Automate ESXi VM configuration 
#

#Default VM settings
CPU=4
RAM=8192
SIZE=200
ISO=""
FLAG=true
ERROR=false
MACADDR="00:50:56:AA:00:00"
NAME="vm-default-create"

#########################################
#
# Create a partial .vmx file.
# ESX server will add more its when the 
# vm starts
#
#########################################

create_vm(){

    #Create vm folder
    echo "Creating VM Folder ${NAME}"
    mkdir ${NAME}

    #Create vmdk 
    echo "Create ${SIZE} G vmdk file $NAME/$NAME.vmdk"
    vmkfstools -c "${SIZE}"G -a lsilogic $NAME/$NAME.vmdk

    #Create configuration file
    echo "Create the configuration file  $NAME/$NAME.vmx"
    touch $NAME/$NAME.vmx

    #fill in configuration paramters
    cat << EOF > $NAME/$NAME.vmx
config.version = "8"
virtualHW.version = "8"
vmci0.present = "TRUE"
displayName = "${NAME}"
floppy0.present = "FALSE"
numvcpus = "${CPU}"
scsi0.present = "TRUE"
scsi0.sharedBus = "none"
scsi0.virtualDev = "lsilogic"
memsize = "${RAM}"
scsi0:0.present = "TRUE"
scsi0:0.fileName = "${NAME}.vmdk"
scsi0:0.deviceType = "scsi-hardDisk"
ide1:0.present = "TRUE"
ide1:0.fileName = "${ISO}"
ide1:0.deviceType = "cdrom-image"
pciBridge0.present = "TRUE"
pciBridge4.present = "TRUE"
pciBridge4.virtualDev = "pcieRootPort"
pciBridge4.functions = "8"
pciBridge5.present = "TRUE"
pciBridge5.virtualDev = "pcieRootPort"
pciBridge5.functions = "8"
pciBridge6.present = "TRUE"
pciBridge6.virtualDev = "pcieRootPort"
pciBridge6.functions = "8"
pciBridge7.present = "TRUE"
pciBridge7.virtualDev = "pcieRootPort"
pciBridge7.functions = "8"
ethernet0.pciSlotNumber = "32"
ethernet0.present = "TRUE"
ethernet0.virtualDev = "vmxnet3"
ethernet0.networkName = "VM Network"
ethernet0.generatedAddressOffset = "0"
ethernet0.addressType="static"
ethernet0.address = "${MACADDR}"
guestOS = "centos-64"
EOF

    #Adding Virtual Machine to VM register - modify your path accordingly!!
    MYVM=`vim-cmd solo/registervm /vmfs/volumes/datastore1/${NAME}/${NAME}.vmx`
    #Powering up virtual machine:
    vim-cmd vmsvc/power.on $MYVM

}


for i in "$@"
do
    case $i in 
        --cpu=*)
            CPU="${i#*=}"
            shift
            ;;

        --ram=*)
            RAM="${i#*=}"
            shift
            ;;

        --mac=*)
            MACADDR="${i#*=}"
            shift
            ;;

        --name=*)
            NAME="${i#*=}"
            shift
            ;;

        *)
            ;;
    esac
    shift
done

create_vm


