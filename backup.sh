#!/bin/bash
#set -x

#
# Backup script that will backup files in a 
# Logrotate style.
# Specify the file to backup, the number of backups to keep,
# and the target backup directory
#


BackupRotate() {
    local FILE="$1"
    local LIMIT="$2"
    local TARGETDIR="$3"
    local CUDATE=$(date +%Y-%m-%d)
    local BKFILE="${FILE%.*}-$CUDATE"

    if [ -z $LIMIT ]; then
        LIMIT=10
    fi
    if [ -z $TARGETDIR ]; then
        TARGETDIR=$(pwd)
    else
        if [ ! -d $TARGETDIR ]; then
            mkdir -p $TARGETDIR
        fi
    fi

    if [ -f ${FILE} ]; then
        COUNT=1
        let N_COUNT=$[COUNT+1]
        let P_COUNT=$[COUNT-1]
        if [ -f ${TARGETDIR}/${BKFILE}.${LIMIT}.${FILE##*.} ]; then
            rm ${TARGETDIR}/${BKFILE}.${COUNT}.${FILE##*.}
            while [[ ${COUNT} -lt ${LIMIT} ]]; do
                if [ -e ${TARGETDIR}/${BKFILE}.${N_COUNT}.${FILE##*.} ]; then     
                    mv ${TARGETDIR}/${BKFILE}.${N_COUNT}.${FILE##*.} ${TARGETDIR}/${BKFILE}.${COUNT}.${FILE##*.}
                fi
                let COUNT=$[COUNT+1]
                let N_COUNT=$[COUNT+1]
            done
        else
            while [[ $COUNT -lt $LIMIT ]]; do
                if [ -e "${TARGETDIR}/${BKFILE}.${COUNT}.${FILE##*.}" ]; then
                    let COUNT=$[COUNT+1]
                else
                    break
                fi
            done
        fi
        cp $FILE ${TARGETDIR}/${BKFILE}.${COUNT}.${FILE##*.} 
    fi
}

if [ -z $1 ]; then
    echo "Usage: Backup file <backup limit> <backup directory> "
    exit 1
fi

BackupRotate $1 $2 $3





