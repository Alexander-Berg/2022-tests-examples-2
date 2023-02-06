WORKDIR /tmp/build/services/corp-corp-client

RUN npm run lint
RUN npm run test
