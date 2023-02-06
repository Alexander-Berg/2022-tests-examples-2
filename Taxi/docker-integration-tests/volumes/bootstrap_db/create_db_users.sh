#!/usr/bin/env bash

set -e

DB="dbpinstats dbtaxi dbarchive dbsmsconsent dbprocessing ordermessages dblogs stats dbmisc dbparks dbdrivers dbcars dbtariffs qc dbsubvention_reasons"

for db in ${DB}; do
    mongo mongodb://mongo.taxi.yandex:27017/ --quiet --eval \
        "db.getSiblingDB(\"$db\").createUser({user: \"mobile\", pwd: \
        \"mobile\", roles: [{role: \"readWrite\", db: \"$db\"}]})"

done

echo "Added mongo users"
