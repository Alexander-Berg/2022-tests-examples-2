# https://github.com/gopher-net/dockerized-net-tools/tree/master/netflow-generator
# generate netflow data for netflow collector testing

FROM golang

MAINTAINER Brent Salisbury <brent.salisbury@gmail.com>

ADD . /go/src/github.com/nerdalert/nflow-generator

RUN go get github.com/Sirupsen/logrus \
    && go get github.com/jessevdk/go-flags \
    && go install github.com/nerdalert/nflow-generator

ENTRYPOINT ["/go/bin/nflow-generator", "-t", "$TARGET", "-p", "$PORT" ]