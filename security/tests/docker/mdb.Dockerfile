FROM registry.yandex.net/rtc-base/bionic:stable

RUN set -ex; \
	echo "deb http://dist.yandex.net/mdb-bionic unstable/all/" >> /etc/apt/sources.list.d/mdb.list ; \
	echo "deb http://dist.yandex.net/mdb-bionic stable/all/"   >> /etc/apt/sources.list.d/mdb.list ; \
	echo "deb http://dist.yandex.net/common unstable/all/"     >> /etc/apt/sources.list.d/mdb.list ; \
	echo "deb http://dist.yandex.net/common stable/all/"       >> /etc/apt/sources.list.d/mdb.list ; \
    apt-get update -qq ; \
    apt-get install osquery-vanilla
