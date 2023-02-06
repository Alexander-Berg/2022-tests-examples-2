#!/usr/bin/env bash

TEST_HOST='http://billing-accounts.taxi.dev.yandex.docker'

echo "create record"
curl -d '{"external_id":"clid_uuid/1_111","kind":"client"}' -X POST "${TEST_HOST}/v1/entities/create" || exit 1
echo -e "\nRead record"
curl -d '{"external_id":"clid_uuid/1_111"}' -X POST "${TEST_HOST}/v1/entities/search" || exit 1
echo -e "\ndone"
