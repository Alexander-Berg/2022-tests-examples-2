FROM node:14-bullseye
ARG BRANCH="master"
ENV BRANCH=$BRANCH
ENV JSON_REPORT_PATH=/yharnam/test/autotests/hermione/autotests-reports/commonReport/report.json
ENV CHUNK=''
ENV PATTERN=''
ENV SET=''

COPY yharnam /yharnam
WORKDIR "/yharnam/server/apps/mockService/"
RUN npm ci
RUN npm run build
WORKDIR "/yharnam/test/autotests"
RUN npm ci
COPY start.sh start.sh
RUN chmod 777 start.sh

CMD ./start.sh
