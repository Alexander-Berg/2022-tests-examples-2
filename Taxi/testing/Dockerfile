FROM registry.yandex.net/taxi/rtc-baseimage-bionic/unstable:latest

COPY ./certs/ /etc/ssl/certs/
COPY ./files/ /

RUN chmod 0600 /etc/ssl/certs/lavka-s2s-proxy.in.yandex.net.key.pem && \
    chmod 0644 /etc/logrotate.d/s2s-proxy.conf && \
    ln -s /etc/nginx/sites-available/s2s.conf /etc/nginx/sites-enabled/s2s.conf
