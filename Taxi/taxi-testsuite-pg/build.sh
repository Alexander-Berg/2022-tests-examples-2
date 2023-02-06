#!/bin/env bash

mkdir $2/pg

mkdir $2/tmp

docker build -t pg-build:v1 build_image/

docker run --mount type=bind,source="$1",target=/postgres-source --mount type=bind,source="$2/tmp",target=/pg pg-build:v1

cp -r $2/tmp/* $2/pg/

sudo rm -rf $2/tmp
