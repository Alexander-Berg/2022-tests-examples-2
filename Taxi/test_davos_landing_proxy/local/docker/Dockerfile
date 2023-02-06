FROM registry.yandex.net/ubuntu:xenial

COPY yandex-xenial.list /etc/apt/sources.list.d/

RUN apt-get update
RUN apt-get install -y python3-pytest python3-requests libperl5.22 nginx=1.14.2-1.yandex.47 dnsmasq

COPY dnsmasq.conf /etc/dnsmasq.conf
COPY ./nginx/listen ./nginx/listen_https ./nginx/nginx.conf /etc/nginx/
COPY ./nginx/01_localhost.conf /etc/nginx/test/
COPY ./nginx/test_upstream.conf ./nginx/ssl.conf /etc/nginx/conf.d/
COPY ./scripts/prepare.sh ./scripts/start.sh /

RUN /prepare.sh
CMD /start.sh
