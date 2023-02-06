ARG BUILD
WORKDIR /var/www/frontend

RUN BUILD=${BUILD} npm run lint
RUN BUILD=${BUILD} npm run test
