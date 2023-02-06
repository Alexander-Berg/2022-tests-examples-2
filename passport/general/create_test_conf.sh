#!/bin/bash

set -eu -o pipefail

DIR_SRC=$(cd $(dirname $0)/..; pwd)
cd $DIR_SRC

bin/shardushka --config conf/test.json init

bin/shardushka --config conf/test.json create shard --id 1
bin/shardushka --config conf/test.json create shard --id 2

bin/shardushka --config conf/test.json create rangeset --name normal    --min 0                --shard 1
bin/shardushka --config conf/test.json create rangeset --name kinopoisk --min 1110000000000000 --shard 2
bin/shardushka --config conf/test.json create rangeset --name pdd       --min 1130000000000000 --shard 2
