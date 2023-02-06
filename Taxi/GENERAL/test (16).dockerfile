WORKDIR /var/www/html/omnichat
RUN npm run lint
RUN npm run test

WORKDIR /var/www/html
RUN npm run lint:stage
RUN npm run test:stage
