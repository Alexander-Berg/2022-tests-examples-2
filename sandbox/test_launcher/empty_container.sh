#!/usr/bin/env bash
set -o errexit
set -o xtrace

dpkg --add-architecture i386
apt-get -yqq update || true
apt-get install -qq --assume-yes --no-install-recommends daemon cpu-checker curl git ca-certificates unzip yandex-jdk8 qemu-kvm libvirt-bin ubuntu-vm-builder bridge-utils libxdamage1 libxfixes3 libc6:i386 libncurses5:i386 libstdc++6:i386 zlib1g:i386 xvfb

tee /etc/profile.d/66-android.sh << "EOF"
export DISPLAY=:1.0
export ANDROID_HOME=/usr/local/android-sdk-linux
export PATH=$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools:$ANDROID_HOME/tools/bin:$ANDROID_HOME/emulator:$PATH
EOF

tee /etc/profile.d/55-java.sh << "EOF"
export JAVA_HOME=/usr/local/java8
export JAVA_TOOL_OPTIONS="-Djava.net.preferIPv4Stack=false -Djava.net.preferIPv6Addresses=true"
EOF

. /etc/profile

##########################################
# Xvfb
##########################################

tee /usr/local/bin/Xvfb-start.sh << "EOF"
#!/bin/bash
. /etc/profile

LOGS_DIR=${1:-/var/log}
echo "Logs dir: $LOGS_DIR"

# create display to be able to run with -gpu mesa to make webview work
# set TMPDIR - workaround for bug:
# https://bugs.launchpad.net/ubuntu/+source/xorg-server/+bug/972324

TMPDIR=/var/tmp daemon --verbose --name Xvfb --unsafe --errlog=$LOGS_DIR/Xvfb.error.log --dbglog=$LOGS_DIR/Xvfb.debug.log --output=$LOGS_DIR/Xvfb.output.log --respawn -- Xvfb :1 -screen 0 800x600x16
EOF
chmod 755 /usr/local/bin/Xvfb-start.sh

tee /usr/local/bin/Xvfb-stop.sh << "EOF"
#!/bin/bash

daemon --stop --verbose --name Xvfb
EOF
chmod 755 /usr/local/bin/Xvfb-stop.sh

tee /usr/local/bin/Xvfb-status.sh << "EOF"
#!/bin/bash

daemon --running --verbose --name Xvfb
EOF
chmod 755 /usr/local/bin/Xvfb-stop.sh
