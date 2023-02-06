#!/usr/bin/env bash

if [ "$(whoami)" == "root" ]; then
  echo "WARNING: root usage detected!"
  chmod -R ugo+rw ../
  chmod -R 664 ../volumes/bootstrap_db/mysql/conf.d/custom.cnf
fi
