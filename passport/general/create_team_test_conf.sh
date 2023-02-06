#!/bin/bash

set -eu -o pipefail

DIR_SRC=$(cd $(dirname $0)/..; pwd)
cd $DIR_SRC

bin/shardushka --config conf/team-test.json init

bin/shardushka --config conf/team-test.json create shard --id 1

bin/shardushka --config conf/team-test.json create rangeset --name normal --min 1100000000000000 --shard 1
