#!/bin/bash
# Check argument
if [ -z "$1" ]; then
	echo "Usage: $0 <vm_name>"
	exit 1
fi

# Check if file already exists
if [ -e /vm/disks/$1.qcow2 ]; then
	echo "Error: Disk image "/vm/disks/$1.qcow2" already exists!"
	exit 2
fi

# Create the disk image
qemu-img create -f qcow2 /vm/disks/$1.qcow2 75G

# Install VM
virt-install \
	--name $1 \
	--ram 4096 \
	--disk path=/vm/disks/$1.qcow2,size=4 \
	--vcpus 4 \
	--cpu host \
	--arch x86_64 \
	--os-type windows \
	--os-variant win2k12r2 \
	--network bridge=br0,model=virtio,mac=c4:54:44:63:ef:70 \
        --graphics vnc,listen=0.0.0.0,port=6001 --noautoconsole \
	--console pty,target_type=serial \
	--cdrom /vm/isos/server16.iso \
	#--cdrom /vm/isos/17763.1.180914-1434.rs5_release_SERVER_EVAL_x64fre_en-us.iso \
	#--disk /vm/isos/virtio-win.iso,device=cdrom,bus=ide \
	#--extra-args 'console=ttyS0,115200n8 serial'
