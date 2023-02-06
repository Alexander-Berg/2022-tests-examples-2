WORKDIR /var/www/html
RUN npm run lint
RUN npm run test
