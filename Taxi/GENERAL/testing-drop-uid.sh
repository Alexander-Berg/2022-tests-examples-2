#!/bin/bash

PASSPORT_UID=$1
if [ -z "$PASSPORT_UID" ]; then
  echo >&2 "Usage: $0 UID"
  exit 1
fi

if [ -z "#EDA_TESTING_MYSQL_PASSWORD" ]; then
  echo >&2 "You have to set EDA_TESTING_MYSQL_PASSWORD env"
  exit 1
fi

query="UPDATE users SET passport_uid = NULL WHERE passport_uid = $PASSPORT_UID;"

mysql bigfood_staging \
	--user=bigfood --password=$EDA_TESTING_MYSQL_PASSWORD \
	--host testing.lxc.eda.tst.yandex.net \
	-e "$query"

