# Dependencies For Manually compile FreeSwitch
if you want to manually compile the FreeSwitch from source code, you need
install dependencies for Debian based or RedHat based systems.

Debian based system
```bash
sudo apt-get install -y build-essential automake autoconf libtool libncurses5-dev libtiff-dev libjpeg-dev zlib1g-dev libssl-dev libsqlite3-dev libpcre3-dev libspeexdsp-dev libspeex-dev libcurl4-openssl-dev libopus-dev libldns-dev libedit-dev
```

Redhat based system
```bash
sudo yum install -y autoconf automake libtool gcc-c++ ncurses-devel make zlib-devel libjpeg-devel openssl-devel e2fsprogs-devel curl-devel pcre-devel speex-devel sqlite-devel
```
