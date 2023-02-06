#!/usr/bin/env bash

  ######################
  #    Preparations    #
  ######################

set -x

export MR_OPT="stderrlevel=5"
export YT_LOG_LEVEL="INFO"
export LEMUR_LOG_LEVEL="DEBUG"
export YT_USE_CLIENT_PROTOBUF=0

LEMUR_DIR=$(dirname $(dirname `realpath $0`))
cd "$LEMUR_DIR"

BASE_PREFIX_PROD="//home/lemur"
CLUSTER="arnold"

PATH_TO_YT="yt"
SHARD="00000000"
NUM_RECS=50000
CANONICAL_VINTAGE=""
OUTPUT_SUFFIX=

function print_help() {
    echo "Run vintage map on one shard in devel environment."
    echo "  -s <shard>     ShardId. Default: 0"
    echo "  -n <num>       Max number of records. Default: 50000"
    echo "  -y <yt-path>   Path to yt. Default: yt"
    echo "  -c <canonical> Path to canonical vintage. Default: none"
    echo "  -o <output-suffix> Path to canonical vintage. Default: none"
    echo "  -h             Print help message."
}

while getopts "s:n:y:c:o:h" OPT; do
    case $OPT in
        s ) SHARD=`printf "%08d" $OPTARG`;;
        n ) NUM_RECS=$OPTARG;;
        y ) PATH_TO_YT=$OPTARG;;
        c ) CANONICAL_VINTAGE="./$OPTARG";;
        o ) OUTPUT_SUFFIX="-$OPTARG";;
        h ) print_help ; exit 0;;
        * ) print_help ; exit 1;;
    esac
done

set -e
set -o pipefail

USERNAME=`whoami`
BASE_PREFIX="//home/robot-dev/lemur_$USERNAME"
BASE_PREFIX_TEST_DATA=$BASE_PREFIX"_test_data"

  ######################
  #      Get data      #
  ######################

# Clean Lemur instance
if [ `$PATH_TO_YT --proxy $CLUSTER exists $BASE_PREFIX` = "true" ] ; then
    $PATH_TO_YT --proxy $CLUSTER remove -r $BASE_PREFIX
fi

# Extract persistent data from production
./tools/extract_test_data/extract_test_data -p conf/conf-vla/instance_config_yt.pb.txt -d conf/conf-devel/instance_config_yt.pb.txt -m shard -c $NUM_RECS -s $SHARD

# Copy global data from production
$PATH_TO_YT --proxy $CLUSTER copy -r --source-path $BASE_PREFIX_PROD"/data/global" --destination-path $BASE_PREFIX"/data/global"

# Save test data for next run and set test time in case comparison mode is on
if [ $CANONICAL_VINTAGE ] ; then
    export TEST_TIME=`date +%s`
    $PATH_TO_YT --proxy $CLUSTER copy -r $BASE_PREFIX $BASE_PREFIX_TEST_DATA
fi

  ######################
  #        Work        #
  ######################

# Run vintage map and merge counters
./vintage/main/vintage -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/vintage_config.pb.txt -s $SHARD -m map
./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m merge

# Output counters to a proto file, continue otherwise
if [ -z $CANONICAL_VINTAGE ] ; then
    ./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m read -a vintage_map -s $SHARD --as-proto > vintage_map.counters$OUTPUT_SUFFIX

    ./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m read -a vintage_map -s $SHARD > vintage_map_new_json.counters$OUTPUT_SUFFIX

    exit 0
fi

# Save counters
./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m read -a vintage_map -s $SHARD > vintage_map_new_json.counters

# Move preserved test data to a working directory
$PATH_TO_YT --proxy $CLUSTER remove -r $BASE_PREFIX
$PATH_TO_YT --proxy $CLUSTER move -r $BASE_PREFIX_TEST_DATA $BASE_PREFIX

# Run canonical vintage map and merge counters
$CANONICAL_VINTAGE -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/vintage_config.pb.txt -s $SHARD -m map
./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m merge

# Save counters and compare them with the new ones
./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m read -a vintage_map -s $SHARD > vintage_map_old_json.counters
./tools/counters_diff_tool/counters_diff_tool vintage_map_old_json.counters vintage_map_new_json.counters > counters_diff
