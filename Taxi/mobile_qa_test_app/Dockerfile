ARG APP_ENV=production
FROM registry.yandex.net/taxi/rtc-baseimage/${APP_ENV}

#installing dart
RUN apt-get update && \
    apt install apt-transport-https
RUN sh -c 'wget -qO- https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -'
RUN sh -c 'wget -qO- https://storage.googleapis.com/download.dartlang.org/linux/debian/dart_stable.list > /etc/apt/sources.list.d/dart_stable.list'
RUN apt-get -qq update && \
    apt-get -qq install --no-install-recommends -y \
    nano \
    dart
RUN export PATH="$PATH:/usr/lib/dart/bin"

#installing models for server
WORKDIR /app/models
COPY /models .
RUN dart pub get


#installing server
WORKDIR /app/backend
COPY /backend .
ADD https://crls.yandex.net/YandexInternalRootCA.crt /app/backend/
ARG UNPAB_OAUTH
RUN echo $UNPAB_OAUTH | dart pub token add https://dart-unpub.taxi.yandex-team.ru &&  DART_VM_OPTIONS=--root-certs-file=/app/backend/YandexInternalRootCA.crt dart pub get
RUN rm /app/backend/YandexInternalRootCA.crt

COPY mobile-qa-app-supervisor.conf /etc/supervisor/conf.d/mobile-qa-app-supervisor.conf
COPY mobie-qa-app-nginx.conf /etc/nginx/sites-enabled/mobie-qa-app-nginx.conf

EXPOSE 80
