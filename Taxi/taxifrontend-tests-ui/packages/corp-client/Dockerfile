FROM registry.yandex.net/taxi/taxi-integration-xenial-base


RUN apt-get update -y && apt-get -y install ca-certificates libgnutls30
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get update -y && apt-get -y install nodejs && node -v && npm -v && \
    apt-get -y install libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 libxtst6 xauth xvfb && \
    apt-get -y install chromium-browser

RUN mkdir -p /usr/src/cypress-tests/
COPY . /usr/src/cypress-tests/

WORKDIR /usr/src/cypress-tests/

RUN npm config set registry https://npm.yandex-team.ru && \
    cd packages/corp-client && npm install
