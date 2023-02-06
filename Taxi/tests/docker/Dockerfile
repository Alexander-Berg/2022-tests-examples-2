FROM registry.yandex.net/ubuntu:xenial

COPY yandex-xenial.list /etc/apt/sources.list.d/

RUN apt-get update
RUN apt-get install -y python3-pytest python3-requests libperl5.22 nginx=1.14.2-1.yandex.47

COPY listen listen_https nginx.conf /etc/nginx/
COPY ssl.conf /etc/nginx/conf.d/
COPY prepare.sh start.sh /

RUN /prepare.sh

CMD /start.sh
