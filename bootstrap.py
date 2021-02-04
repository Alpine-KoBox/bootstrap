import os
import requests

# KoBox bootstrapper
# Has to be run in the stock firmware. Hence, you'll need NiLuJe's stuff installed, or a cross-compiled Python binary.

# Strings
alpinedl = "https://dl-cdn.alpinelinux.org/alpine/v3.10/releases/armv7/alpine-minirootfs-3.10.5-armv7.tar.gz"
buildsh = "#!/bin/sh\n\nmkdir -p /kobox/rootfs /kobox/sysroot\ncd /root\ngit clone https://github.com/Alpine-KoBox/core && cd /root/core/musl\n./configure --prefix=/kobox/sysroot\nmake install\ncd /root/core/busybox\nC_INCLUDE_PATH=/usr/include make install\ncd /kobox/rootfs\nmkdir -p bin dev etc home lib mnt opt proc root run sbin sys tmp usr var\ncd /root && apk fetch -R apk-tools-static && cd /kobox/rootfs\ntar -xpf /root/apk-tools-static-*.apk\ntar -xpf /minirootfs.tar.gz ./lib/apk && tar -xpf /minirootfs.tar.gz ./usr/share/apk && tar -xpf /minirootfs.tar.gz ./etc/apk && tar -xpf /minirootfs.tar.gz ./var/lib/apk && tar -xpf /minirootfs.tar.gz ./var/cache/apk && tar -xpf /minirootfs.tar.gz ./etc/passwd\ntar -xpf /minirootfs.tar.gz ./etc/group\ntar cJpf /mnt/rootfs.txz ./\n"

print("\033[92;1m+++ KoBox bootstrapper. Sets up a basic environment with custom-built musl-libc and BusyBox, compatible with older kernel versions.\033[0m")

# Get image size
imgsize = input("\033[94;1m---\033[0m Desired image size, in MiB (minimum/recommended 1024) : ")
imgloc = input("\033[94;1m---\033[0m Location and name ( absolute path, e.g. /mnt/onboard/kobox.img ) : ")
imgmnt = input("\033[94;1m---\033[0m Image mountpoint (absolute path) : ")

# Create the image
print("\033[94;1m--- Creating the image with dd...\033[0m")
os.system("dd if=/dev/zero of='{0}' bs=1M count={1}".format(imgloc, imgsize))

# Format the image with mke2fs
print("\033[94;1m--- Formatting the image with mke2fs...\033[0m")
os.system("mke2fs -F {0}".format(imgloc))

# Mount the image and installing Alpine Linux base system -- Using v3.10, could change in the future if we used our own builds for that, which we'll probably do.
os.system("mount {0} {1}".format(imgloc, imgmnt))
os.chdir(imgmnt)

# Get the minirootfs
print("\033[94;1m--- Retrieving the staging Alpine Linux minirootfs...\033[0m")
r = requests.get(alpinedl)
open("minirootfs.tar.gz", "wb").write(r.content)

# Untar archive
print("\033[94;1m--- Unpacking the minirootfs...\033[0m")
os.system("tar -xpf minirootfs.tar.gz")

# Mount filesystems + enabling network access in the chroot
print("\033[94;1m--- Mounting filesystems...\033[0m")
os.system("mount --bind /dev {0}/dev".format(imgmnt))
os.system("mount --bind /dev/pts {0}/dev/pts".format(imgmnt))
os.system("mount --bind /mnt/onboard {0}/mnt".format(imgmnt))
os.system("mount -t proc proc {0}/proc".format(imgmnt))
os.system("mount -t sysfs sysfs {0}/sys".format(imgmnt))
os.system("mount -t tmpfs tmpfs {0}/tmp".format(imgmnt))
os.system("mount -t tmpfs tmpfs {0}/run".format(imgmnt))
os.system("mkdir -p {0}/dev/shm".format(imgmnt))
os.system("cp /etc/resolv.conf {0}/etc".format(imgmnt))

# chroot and install build essentials
print("\033[94;1m--- Installing the staging system and required utilities...\033[0m")
os.system("chroot {0} /sbin/apk 'add' 'alpine-sdk' 'binutils' 'linux-headers' 'xz'".format(imgmnt))

# chroot and build
print("\033[94;1m--- chrooting and building the base system... Please wait, this will take a while...\033[0m")
open("build.sh", "w").write(buildsh)

os.system("chmod +x {0}/build.sh".format(imgmnt))
os.system("chroot {0} /build.sh".format(imgmnt))

# Hopefully, nothing has gone wrong... ;)
print("\033[94;1m--- Done! Unmounting filesystems; some harmless warnings might show up...\033[0m")
os.system("umount -l -f {0}/*".format(imgmnt))
os.system("umount -l -f {0}".format(imgmnt))

print("\033[94;1m--- Re-formatting the image...\033[0m")
os.system("mke2fs -F {0}".format(imgloc))

print("\033[94;1m--- Extracting compiled base rootfs...\033[0m")
os.system("mount {0} {1}".format(imgloc, imgmnt))
os.system("cd {0} && tar -xpf /mnt/onboard/rootfs.txz".format(imgmnt))

print("\033[94;1m--- Mounting filesystems...\033[0m")
os.system("mount --bind /dev {0}/dev".format(imgmnt))
os.system("mount --bind /dev/pts {0}/dev/pts".format(imgmnt))
os.system("mount -t proc proc {0}/proc".format(imgmnt))
os.system("mount -t sysfs sysfs {0}/sys".format(imgmnt))
os.system("mount -t tmpfs tmpfs {0}/tmp".format(imgmnt))
os.system("mount -t tmpfs tmpfs {0}/run".format(imgmnt))
os.system("mkdir -p {0}/dev/shm".format(imgmnt))
os.system("cp /etc/resolv.conf {0}/etc".format(imgmnt))

print("\033[92;1m+++ Done! If all went according to plan, you should now have an image in mounted at {0} and created in {1} and a compiled base rootfs extracted in it! All that's left is chroot: 'chroot {2} /bin/sh'...\033[0m".format(imgmnt, imgloc, imgmnt))
