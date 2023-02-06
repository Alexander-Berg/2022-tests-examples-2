#!/usr/bin/env bash

  ######################
  #    Preparations    #
  ######################

set -e
set -o pipefail

export MR_OPT="stderrlevel=5"
export YT_LOG_LEVEL="INFO"
export LEMUR_LOG_LEVEL="DEBUG"
export YT_USE_CLIENT_PROTOBUF=0

USERNAME=`whoami`
BASE_PREFIX="//home/robot-dev/lemur_$USERNAME"
BASE_PREFIX_PROD="//home/lemur"
CLUSTER="arnold"

PATH_TO_YT="yt"
HOST=""
SHARD=""
PART="0000"
MODE_STR=""
KEYTYPE="KT_DOC_DEF"
NUM_RECS=0 # 0 means no limit

RUN_SENDLINK=false
RUN_PREPARAT=false
RUN_LOOP=false

if (pwd | grep -v "arcadia/robot/lemur$" > /dev/null); then
    echo "Please, run me from arcadia/robot/lemur/"
    exit 1
fi

function print_help() {
    echo "Run vintage map on one host or one url in devel environment."
    echo "  -H <host>      Host. Specify host or url"
    echo "  -u <url>       Url. Specify host or url"
    echo "  -k <keytype>   KeyType. Default: $KEYTYPE"
    echo "  -p <part>      PartId for preparatprocessor. Default: $PART"
    echo "  -n <num>       Max number of records, 0 means unlimited. Default: $NUM_RECS"
    echo "  -S             Run sendlinkprocessor"
    echo "  -P             Run preparatprocessor"
    echo "  -L             Run one more loop harvester+vintage after first vintage map and all optional apps"
    echo "  -y <yt-path>   Path to yt. Default: $PATH_TO_YT"
    echo "  -h             Print help message."
}

while getopts "H:u:k:p:n:SPLy:h" OPT; do
    case $OPT in
        H ) MODE_STR="-m host -H $OPTARG"; HOST=$OPTARG;;
        u ) MODE_STR="-m url -u $OPTARG";;
        k ) KEYTYPE=$OPTARG;;
        p ) PART=`printf "%04d" $OPTARG`;;
        n ) NUM_RECS=$OPTARG;;
        S ) RUN_SENDLINK=true;;
        P ) RUN_PREPARAT=true;;
        L ) RUN_LOOP=true;;
        y ) PATH_TO_YT=$OPTARG;;
        h ) print_help ; exit 0;;
        * ) print_help ; exit 1;;
    esac
done

if [ -z "$MODE_STR" ] ; then
    echo "Please specify host or url."
    print_help
    exit 1
fi

  ######################
  #      Get data      #
  ######################

# Clean Lemur instance
if [ `$PATH_TO_YT --proxy $CLUSTER exists $BASE_PREFIX` = "true" ] ; then
    $PATH_TO_YT --proxy $CLUSTER remove -r $BASE_PREFIX
fi

# Extract persistent data from production
SHARD_STR=`./tools/extract_test_data/extract_test_data -p conf/conf-vla/instance_config_yt.pb.txt -d conf/conf-devel/instance_config_yt.pb.txt -k $KEYTYPE -c $NUM_RECS $MODE_STR | awk '{print $2}'`
SHARD=`printf "%08d" $SHARD_STR`

# Copy global data from production
$PATH_TO_YT --proxy $CLUSTER copy -r --source-path $BASE_PREFIX_PROD"/data/global" --destination-path $BASE_PREFIX"/data/global"

  ######################
  #        Work        #
  ######################

# Run vintage
./vintage/main/vintage -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/vintage_config.pb.txt -s $SHARD -m map
./vintage/main/vintage -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/vintage_config.pb.txt -s $SHARD -m combine

# Run sendlinkprocessor
if $RUN_SENDLINK ; then
    ./tools/extract_test_data/extract_test_data -p conf/conf-vla/instance_config_yt.pb.txt -d conf/conf-devel/instance_config_yt.pb.txt -m sendlink -c $NUM_RECS -H $HOST
    ./sendlinkprocessor/main/sendlinkprocessor -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/sendlinkprocessor_config.pb.txt -m hostcanon
    ./sendlinkprocessor/main/sendlinkprocessor -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/sendlinkprocessor_config.pb.txt -m gemini
fi

# Run preparatprocessor
if $RUN_PREPARAT ; then
    $PATH_TO_YT --proxy $CLUSTER read --format yamr //home/webmaster/prod/export/webmaster-hosts > webmasterhosts.txt
    ./preparatprocessor/main/preparatprocessor -i conf/conf-devel/instance_config_yt.pb.txt -l conf/conf-devel/preparatprocessor_config.pb.txt -m split -s $SHARD
    ./preparatprocessor/main/preparatprocessor -i conf/conf-devel/instance_config_yt.pb.txt -l conf/conf-devel/preparatprocessor_config.pb.txt -m reduce -b $PART -w webmasterhosts.txt
fi

# Merge and read counters
./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m merge
./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m read -a vintage_map -s $SHARD --as-proto > vintage_map.counters
./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m read -a vintage_combine -s $SHARD --as-proto > vintage_combine.counters
./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m read -a sendlinkprocessor_gemini --as-proto > sendlinkprocessor_gemini.counters

# Run second loop
if $RUN_LOOP ; then
    ./harvester/main/harvester -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-common/harvester_config.pb.txt -t ../../yweb/robot/ukrop/conf/conf-production/kiwi/triggers.pb.txt
    ./vintage/main/vintage -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/vintage_config.pb.txt -s $SHARD -m delta
    ./vintage/main/vintage -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/vintage_config.pb.txt -s $SHARD -m host
    ./vintage/main/vintage -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/vintage_config.pb.txt -s $SHARD -m map
    ./vintage/main/vintage -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/vintage_config.pb.txt -s $SHARD -m combine

    ./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m merge
    ./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m read -a vintage_host -s $SHARD --as-proto > vintage_host.loop.counters
    ./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m read -a vintage_map -s $SHARD --as-proto > vintage_map.loop.counters
    ./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m read -a vintage_combine -s $SHARD --as-proto > vintage_combine.loop.counters
fi
