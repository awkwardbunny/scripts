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
qemu-img create -f qcow2 /vm/disks/$1.qcow2 8G

# Install VM
virt-install \
        --name $1 \
        --ram 2048 \
        --disk path=/vm/disks/$1.qcow2,size=4 \
        --vcpus 2 \
        --cpu host \
        --arch x86_64 \
        --os-type linux \
        --os-variant generic \
        --network bridge=br0,model=virtio,mac=c4:54:44:63:ef:65 \
	--network bridge=br1,model=virtio,mac=c4:54:44:63:ef:66 \
        --graphics vnc,listen=0.0.0.0 --noautoconsole \
        --console pty,target_type=serial \
        --cdrom=/vm/isos/pfsense.iso  \
        # --extra-args 'console=ttyS0,115200n8 serial'

