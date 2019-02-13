#!/bin/bash

BACKUPBASEDIR=/vm/backups
BAKDIR=$BACKUPBASEDIR/`date +%Y%m%d`
mkdir -p $BAKDIR
LOG_FILE=$BAKDIR/vm_backup_log
touch $LOG_FILE
EMAIL="eeadmin@cooper.edu"
FAILURE_COUNT=0

#Redirect output to LOG_FILE
exec > $LOG_FILE
exec 2>&1

failed () {
        cat /vm/scripts/backup_fail.template ${LOG_FILE} | /usr/sbin/sendmail $EMAIL
        #echo "Sending fail email"
}

success () {
        cat /vm/scripts/backup_success.template ${LOG_FILE} | /usr/sbin/sendmail $EMAIL
        #echo "Sending success email"
}

#connect to nas if not already connected
#iscsiadm -m discovery -t st -p archivist1.ee.cooper.edu
#iscsiadm -m node -T iqn.2018-01.edu.cooper.ee:archivist1.imgstore -p archivist1.ee.cooper.edu -l
mount /vm/backups


#Exclude VMs from backup with inverse grep
virsh list --name | grep -v "dg\|notch" | while read -r vm ; 
do
	if [ ! -z $vm ]
	then
		echo "Starting backup for $vm"

		echo "Dumping XML for $vm to $BAKDIR/$vm.xml"
		virsh dumpxml $vm > $BAKDIR/$vm.xml
		if [ $? -ne 0 ] ; then
			echo "Failed to backup XML for $vm"
			FAILURECOUNT=$((FAILURE_COUNT + 1))
		fi

		echo "Creating snapshot for $vm"
		virsh snapshot-create-as --domain $vm $vm --diskspec hda,file=/vm/disks/$vm-snapshot.qcow2 --disk-only --atomic
		if [ $? -ne 0 ] ; then
			echo "Failed to create snapshot for $vm"
			echo "Skipping to next vm"
			FAILURECOUNT=$((FAILURE_COUNT + 1))
			continue
		fi

		echo "Copying vm drive to NAS"
		cp /vm/disks/$vm.qcow2 $BAKDIR/$vm.qcow2
		if [ $? -ne 0 ] ; then
			echo "Failed to copy disk to NAS"
			FAILURE_COUNT=$((FAILURE_COUNT + 1))
		fi

		echo "Reverting $vm disk to original"
		virsh blockcommit $vm hda --active --pivot --shallow --verbose
		if [ $? -ne 0 ] ; then
			echo "Unable to revert to original disk for $vm"
			echo "Skipping to next vm"
			FAILURECOUNT=$((FAILURE_COUNT + 1))
			continue
		fi

		echo "Deleting snapshot"
		rm /vm/disks/$vm-snapshot.qcow2
		virsh snapshot-delete $vm $vm --metadata

	fi
done


if [ $FAILURE_COUNT -gt 0 ]
then
	failed
	exit -1
fi
success
