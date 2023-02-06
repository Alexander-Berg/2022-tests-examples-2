#!/usr/bin/env bash
set -e

wget --no-check-certificate -q https://s3.mds.yandex.net/eda-sql-dumps/last-minimal.sql.gz
gunzip last-minimal.sql.gz
mv last-minimal.sql volumes/bootstrap_db/mysql/initdb/db_data/00-schema-create.sql
