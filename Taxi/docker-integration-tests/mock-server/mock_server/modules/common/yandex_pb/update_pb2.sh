#!/bin/bash

# params
PATHS=(
    yandex/maps/proto/common2
    yandex/maps/proto/road_events
    yandex/maps/proto/driving
)

# main
ARCADIA_DIR=$(dirname "$0")
BASE_URL=svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/maps/doc/proto/

for file_name in ${PATHS[@]}
do
  OUT_DIR=$ARCADIA_DIR/$file_name
  URL=$BASE_URL$file_name

  printf 'Update %s\n' "$file_name"
  mkdir -p $OUT_DIR
  rm -f $OUT_DIR/*  # remove old files
  svn checkout --force --quiet $URL $OUT_DIR
  svn info $URL | tee $OUT_DIR/revision.info

  # cleanup
  rm -fr $OUT_DIR/.svn $OUT_DIR/debian $OUT_DIR/examples $OUT_DIR/mobile
  rm -f $OUT_DIR/Makefile $OUT_DIR/ya.make
done

printf 'Ok\n'
