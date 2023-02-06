#!/bin/bash
set -o errexit
set +e

function echoTitle {
    echo ""
    echo "******************************************"
    echo "   $1:"
    echo "******************************************"
}

echoTitle "Instal required packages"
dpkg --add-architecture i386 && apt-get update
apt-get install -y yandex-internal-root-ca
apt-get install -y libc6:i386 libncurses5:i386 libstdc++6:i386 zlib1g-dev:i386
apt-get install -y libxml2-utils
apt-get install -y lib32ncurses5
apt-get install -y lib32ncurses5-dev
apt-get install -y libncurses5
apt-get install -y libncurses5-dev
apt-get install -y lib32z1
apt-get install -y mingw-w64
apt-get install -y lib32readline6-dev
apt-get install -y flex
apt-get install -y bison
apt-get install -y gperf
apt-get install -y subversion
apt-get install -y git-core
apt-get install -y ccache
apt-get install -y gnupg
apt-get install -y build-essential
apt-get install -y zlib1g-dev
apt-get install -y libc6-dev
apt-get install -y x11proto-core-dev
apt-get install -y libx11-dev
apt-get install -y libfreetype6
apt-get install -y libfreetype6-dev
apt-get install -y gawk
apt-get install -y make
apt-get install -y automake
apt-get install -y libc6-dev-i386
apt-get install -y libssl-dev
apt-get install -y lib32z-dev
apt-get install -y libgl1-mesa-dev
apt-get install -y xsltproc
apt-get install -y gitg
apt-get install -y git-gui
apt-get install -y autoconf
apt-get install -y libtool
apt-get install -y doxygen
apt-get install -y joe
apt-get install -y libgmp3-dev
apt-get install -y libmpfr-dev
apt-get install -y lzop
apt-get install -y screen
apt-get install -y indent
apt-get install -y lftp
apt-get install -y lvm2
apt-get install -y realpath
apt-get install -y git-email
apt-get install -y enca
apt-get install -y elinks
apt-get install -y sshfs
apt-get install -y mingw32
apt-get install -y bonnie++
apt-get install -y libmpc-dev
apt-get install -y libcloog-ppl-dev
apt-get install -y procmail
apt-get install -y dos2unix
apt-get install -y bc
apt-get install -y libcurl4-openssl-dev
apt-get install -y gcc
apt-get install -y g++
apt-get install -y gcc-multilib
apt-get install -y g++-multilib

echoTitle "Install i386 libs"
apt-get -yqq update || true
apt-get install -qq --assume-yes --no-install-recommends \
daemon cpu-checker curl git ca-certificates zip unzip qemu-kvm libvirt-bin ubuntu-vm-builder bridge-utils \
libc6:i386 libncurses5:i386 libstdc++6:i386 zlib1g:i386 xvfb \
libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 \
libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 \
libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 \
libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 \
libnss3

echoTitle "Instal yandex-openjdk11"
apt-get install -y yandex-openjdk11

echoTitle "Instal Python 3.8"
apt-get install software-properties-common -y
add-apt-repository ppa:deadsnakes/ppa -y
apt-get update
apt-get install -y python-pip
apt-get install -y python-serial
apt-get install -y python

apt-get install -y python3.8
apt-get install -y python3.8-dev
apt-get install -y python3.8-distutils
python3.8 --version

echoTitle "change default python to version 3.8"
rm /usr/bin/python3 && ln -s /usr/bin/python3.8 /usr/bin/python3
rm /usr/bin/python && ln -s /usr/bin/python3.8 /usr/bin/python
ls -al /usr/bin/ | grep python
python -V

echoTitle "curl and python get-pip.py"
curl --verbose -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

echoTitle "python -m pip install --upgrade pip setuptools wheel"
python -m pip install --upgrade pip setuptools wheel

echoTitle "python -m pip install requests==2.27.1"
python -m pip install requests==2.27.1

echoTitle "python3 -m pip install requests==2.27.1"
python3 -m pip install requests==2.27.1
pip show requests

echoTitle "python -m pip install retrying==1.3.3"
python -m pip install retrying==1.3.3

echoTitle "python3 -m pip install retrying==1.3.3"
python3 -m pip install retrying==1.3.3
pip show retrying

echoTitle "fix No module named apt_pkg"
cd /usr/lib/python3/dist-packages
cp apt_pkg.cpython-35m-x86_64-linux-gnu.so apt_pkg.so
cd -

echoTitle "pip setuptools"
pip install setuptools

echoTitle "Install gradle"
wget https://artifactory.yandex.net/gradle-distributions/distributions/gradle-7.3.3-bin.zip -P /tmp
unzip -d /opt/gradle /tmp/gradle-*.zip
ls /opt/gradle/gradle-7.3.3

echoTitle "Instal yandex-passport-vault-client"
apt-get install -y yandex-passport-vault-client

echoTitle "Add android cmdline-tools"
curl --verbose --insecure -o sdk-tools.zip https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip
mkdir -p /usr/local/android-sdk-linux
unzip sdk-tools.zip -d /usr/local/android-sdk-linux
rm sdk-tools.zip

echoTitle "Add android licenses"
mkdir /usr/local/android-sdk-linux/cmdline-tools/latest
mkdir -p /usr/local/android-sdk-linux/cmdline-tools/latest/licenses
chmod -R 0777 /usr/local/android-sdk-linux
cp -r /usr/local/android-sdk-linux/cmdline-tools/bin /usr/local/android-sdk-linux/cmdline-tools/latest
cp -r /usr/local/android-sdk-linux/cmdline-tools/lib /usr/local/android-sdk-linux/cmdline-tools/latest
cp /usr/local/android-sdk-linux/cmdline-tools/NOTICE.txt /usr/local/android-sdk-linux/cmdline-tools/latest
cp /usr/local/android-sdk-linux/cmdline-tools/source.properties /usr/local/android-sdk-linux/cmdline-tools/latest
echo "24333f8a63b6825ea9c5514f83c2829b004d1fee" > "/usr/local/android-sdk-linux/cmdline-tools/latest/licenses/android-sdk-license"

echoTitle "Add env"
echo "export ANDROID_HOME=/usr/local/android-sdk-linux" >> /etc/profile
echo "export TEAMCITY_VERSION=1" >> /etc/profile

tee /etc/profile.d/66-android.sh << "EOF"
export ANDROID_SDK_ROOT=/usr/local/android-sdk-linux
export ANDROID_HOME=/usr/local/android-sdk-linux
export PATH=${PATH}:$ANDROID_HOME/platform-tools
export PATH=${PATH}:$ANDROID_HOME/emulator
export PATH=${PATH}:$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=${PATH}:$ANDROID_HOME/build-tools/31.0.0
export SHELL=/bin/bash
export LD_LIBRARY_PATH=$ANDROID_HOME/emulator/lib64/:$ANDROID_HOME/emulator/lib64/gles_mesa:$ANDROID_HOME/emulator/lib64/gles_swiftshader:$ANDROID_HOME/emulator/lib64/qt/lib/:$LD_LIBRARY_PATH
ldconfig
EOF

export GRADLE_HOME=/opt/gradle/gradle-7.3.3
export PATH=$GRADLE_HOME/bin:$PATH

ln -s $ANDROID_HOME/cmdline-tools/latest/bin/avdmanager /usr/bin/avdmanager

. /etc/profile
gradle -v

echoTitle "Install android packages"
. /etc/profile
yes | sdkmanager --licenses
yes | sdkmanager "tools"
yes | sdkmanager "platform-tools"
yes | sdkmanager "emulator" --channel=3

yes | sdkmanager "build-tools;29.0.2"
yes | sdkmanager "build-tools;30.0.2"
yes | sdkmanager "build-tools;30.0.3"
yes | sdkmanager "build-tools;31.0.0"

yes | sdkmanager "platforms;android-25"
yes | sdkmanager "platforms;android-28"
yes | sdkmanager "platforms;android-29"
yes | sdkmanager "platforms;android-30"
yes | sdkmanager "platforms;android-31"

yes | sdkmanager "system-images;android-28;google_apis;x86_64"
yes | sdkmanager "system-images;android-25;android-tv;x86"

MARATHON_VERSION=0.7.3
echoTitle "Install marathon $MARATHON_VERSION"
cd /opt
curl -L https://github.com/MarathonLabs/marathon/releases/download/${MARATHON_VERSION}/marathon-${MARATHON_VERSION}.zip -o marathon-commandline.zip
unzip marathon-commandline.zip
rm marathon-commandline.zip
ln -s /opt/marathon-${MARATHON_VERSION}/bin/marathon /usr/bin/marathon


ALLURE_VERSION=2.18.1
echoTitle "Install marathon $ALLURE_VERSION"
mkdir -p /opt
cd /opt
curl https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/${ALLURE_VERSION}/allure-commandline-${ALLURE_VERSION}.tgz -o allure-commandline.tgz
tar zxf allure-commandline.tgz
rm allure-commandline.tgz
ln -s /opt/allure-${ALLURE_VERSION}/bin/allure /usr/bin/allure

tee /etc/profile.d/55-java.sh << "EOF"
ls /usr/local
export JAVA_HOME=/usr/local/jdk-11
which java
EOF

set +e
echoTitle "Environment"
echo "PATH = $PATH"
python -V
python3 -V
java -version
pip -V
pip3 -V
echoTitle "avdmanager"
avdmanager
echoTitle "apksigner"
apksigner
echoTitle "The end"
set -e