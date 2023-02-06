WORKDIR /tmp/build

RUN npm run lint
RUN npm run test
