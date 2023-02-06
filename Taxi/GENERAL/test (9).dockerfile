WORKDIR /var/www/html/

RUN npm run tsc
RUN npm run lint
RUN npm run test
