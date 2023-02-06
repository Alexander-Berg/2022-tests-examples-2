FROM registry.yandex.net/toolbox/nodejs:10-bionic

ENV NODE_ENV production
WORKDIR /app

COPY app.js /app/app.js
COPY package.json /app/package.json
COPY config /app/config
COPY bin /app/bin
COPY node_modules /app/node_modules
COPY public /app/public
COPY routes /app/routes
COPY utils /app/utils
COPY views /app/views

CMD npm start
