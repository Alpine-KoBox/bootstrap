# bootstrap
Bootstrap scripts to create distribution or development images of KoBox

#### Core
This builds a minimal rootfs with the latest-stable musl-libc and BusyBox available. It also includes apk.static, which it is not at all recommended to use except for retrieving packages specifically compiled for your device.
You'll need Python on your Kobo and the latest firmware version. Ensure you're connected to Wi-Fi (and will stay connected), put the script in the root (/) of your Kobo and run
```
su root
```
to be sure you're the real root user and
```
python bootstrap.py
```
to build the rootfs. Please note that it could maybe brick it if you don't do things correctly, and I'm not at all responsible for any problem related to that that could occur. But normally, all should go well ;)
