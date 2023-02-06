WORKDIR /var/www/html/support-common-ui
RUN npm run lint
RUN npm run test

WORKDIR /var/www/html
RUN npm run lint
RUN npm run test
