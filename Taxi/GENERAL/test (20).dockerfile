WORKDIR /var/www/frontend

RUN npm run lint
RUN npm run test
