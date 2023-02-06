FROM ubuntu:18.04 AS build-spandsp
# debian build layer
RUN set -ex \
    && sed -i -- 's/# deb-src/deb-src/g' /etc/apt/sources.list \
    && sed -i -- 's/archive.ubuntu.com/mirror.yandex.ru/g' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
                gnupg2 \
                build-essential \
                cdbs \
                devscripts \
                equivs \
                fakeroot

# spandsp dependency
RUN apt-get install -y --no-install-recommends \
                libtiff-dev \
                dpatch \
                doxygen \
                xsltproc

COPY spandsp /opt/spandsp
WORKDIR /opt/spandsp
RUN mk-build-deps -ir -t "apt-get -o Debug::pkgProblemResolver=yes -y --no-install-recommends"
RUN debuild -b -uc -us


FROM ubuntu:18.04 AS build-sofia-sip
# debian build layer
RUN set -ex \
    && sed -i -- 's/# deb-src/deb-src/g' /etc/apt/sources.list \
    && sed -i -- 's/archive.ubuntu.com/mirror.yandex.ru/g' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
                gnupg2 \
                build-essential \
                cdbs \
                devscripts \
                equivs \
                fakeroot

# sofia-sip dependency
RUN apt-get install -y --no-install-recommends \
            libssl-dev

COPY sofia-sip /opt/sofia-sip
WORKDIR /opt/sofia-sip
RUN mk-build-deps -ir -t "apt-get -o Debug::pkgProblemResolver=yes -y --no-install-recommends"
RUN debuild -b -uc -us

FROM ubuntu:18.04 AS build-freeswitch-stack
# debian build layer
RUN set -ex \
    && sed -i -- 's/# deb-src/deb-src/g' /etc/apt/sources.list \
    && sed -i -- 's/archive.ubuntu.com/mirror.yandex.ru/g' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
                gnupg2 \
                build-essential \
                cdbs \
                devscripts \
                equivs \
                fakeroot
# yandex taxi deb
RUN set -ex \
    && echo "deb http://yandex-taxi-bionic.dist.yandex.ru/yandex-taxi-bionic stable/all/" > /etc/apt/sources.list.d/yandex-taxi.list \
    && echo "deb http://yandex-taxi-bionic.dist.yandex.ru/yandex-taxi-bionic stable/amd64/" >> /etc/apt/sources.list.d/yandex-taxi.list \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 7FCD11186050CD1A \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
                libyandex-taxi-c-ares-dev \
                libyandex-taxi-grpc++-dev \
                libyandex-taxi-protoc-dev \
                libyandex-taxi-protobuf-dev \
                yandex-taxi-protobuf-compiler \
                yandex-taxi-protobuf-compiler-grpc

# freeswitch-stack dependency
RUN apt-get install -y --no-install-recommends \
            git \
            libtool-bin \
            libssl-dev \
            libjpeg-dev \
            libjpeg8 \
            libtiff-dev \
            libtiff5

COPY freeswitch-stack /opt/noc/iptel/tanya/freeswitch-stack
COPY cloud /opt/cloud
COPY --from=build-spandsp /opt/libspandsp3*.deb /opt/deb/
COPY --from=build-sofia-sip /opt/libsofia-sip*.deb /opt/deb/
RUN dpkg -i \
    /opt/deb/libsofia-sip-ua0_1.13.5-1_amd64.deb \
    /opt/deb/libsofia-sip-ua-dev_1.13.5-1_amd64.deb \
    /opt/deb/libspandsp3_3.0.0-42_amd64.deb \
    /opt/deb/libspandsp3-dev_3.0.0-42_amd64.deb
WORKDIR /opt/noc/iptel/tanya/freeswitch-stack/debian
RUN set -ex \
    && grep -v '^#' ../build/modules.conf.in > modules.conf \
    && ./bootstrap.sh
WORKDIR /opt/noc/iptel/tanya/freeswitch-stack
RUN mk-build-deps -ir -t "apt-get -o Debug::pkgProblemResolver=yes -y --no-install-recommends"
RUN debuild -b -uc -us

FROM ubuntu:18.04 AS freeswitch-testsuite
# debian build layer
RUN set -ex \
    && sed -i -- 's/# deb-src/deb-src/g' /etc/apt/sources.list \
    && sed -i -- 's/archive.ubuntu.com/mirror.yandex.ru/g' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
                gnupg2 \
                build-essential \
                cdbs \
                curl \
                devscripts \
                swig \
                python3.8 \
                python3.8-dev \
                python3-distutils \
                python3-setuptools

# make Python 3.8 default, install pip
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
RUN update-alternatives  --set python3 /usr/bin/python3.8
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.8 get-pip.py

# install testsuite python dependencies
RUN python3 -m pip install grpcio protobuf aiohttp termcolor

COPY --from=build-spandsp /opt/libspandsp3*.deb /opt/deb/
COPY --from=build-sofia-sip /opt/libsofia-sip*.deb /opt/deb/
COPY --from=build-freeswitch-stack /opt/noc/iptel/tanya/*.deb /opt/deb/

# build pjsua2 library and python package
COPY pjproject /opt/noc/iptel/pjproject
WORKDIR /opt/noc/iptel/pjproject
RUN ./build-testsuite.sh
RUN ldconfig

# install FreeSWITCH to be tested
WORKDIR /opt/deb
RUN set -ex \
    && echo "deb http://yandex-taxi-bionic.dist.yandex.ru/yandex-taxi-bionic stable/amd64/" >> /etc/apt/sources.list.d/yandex-taxi.list \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 7FCD11186050CD1A \
    && apt-get update \
    && apt-get install -y \
    ./freeswitch-mod-cdr-csv_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-commands_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-console_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-db_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-dialplan-xml_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-distributor_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-dptools_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-enum_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-event-socket_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-expr_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-fifo_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-hash_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-httapi_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-ivr-dispatcher_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-local-stream_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-logfile_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-loopback_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-native-file_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-pgsql_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-rtc_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-sndfile_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-sofia_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-tone-stream_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-xml-rpc_1.2~rc2-1_amd64.deb \
    ./freeswitch-mod-ya-speechkit_1.2~rc2-1_amd64.deb \
    ./freeswitch-systemd_1.2~rc2-1_amd64.deb \
    ./freeswitch_1.2~rc2-1_amd64.deb \
    ./libfreeswitch1_1.2~rc2-1_amd64.deb \
    ./libsofia-sip-ua-glib3_1.13.5-1_amd64.deb \
    ./libsofia-sip-ua0_1.13.5-1_amd64.deb \
    ./libspandsp3_3.0.0-42_amd64.deb

# install testsuite python package and entrypoints
COPY freeswitch_testsuite /opt/noc/iptel/freeswitch_testsuite
WORKDIR /opt/noc/iptel/freeswitch_testsuite
RUN python3 ./setup.py install

# create mock CA and certificate for testsuite
RUN ./gen_cert.sh

# action!
CMD run_tests --path `which freeswitch`

