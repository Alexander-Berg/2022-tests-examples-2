#!/usr/bin/env bash

  ######################
  #    Preparations    #
  ######################

export MR_OPT="stderrlevel=5"
export YT_LOG_LEVEL="DEBUG"
export LEMUR_LOG_LEVEL="DEBUG"
export YT_USE_CLIENT_PROTOBUF=0 # good check for hidden YT io bugs
export TEST_TIME=`date +%s` # to reduce difference between runs
export TEST_RANDOM="TRUE" # # to use deterministic random gen

LEMUR_DIR=$(dirname $(dirname `realpath $0`))
cd "$LEMUR_DIR"

USERNAME=`whoami`
BASE_PREFIX="//home/robot-dev/lemur_$USERNAME"
BASE_PREFIX_PROD="//home/lemur"
CLUSTER="arnold"
export YT_PROXY=$CLUSTER

PATH_TO_YT="yt"
SHARD="00000000"
PART="0000"
NUM_RECS=100000

function print_help() {
    echo "Run everything on one shard in devel environment."
    echo "  -s <shard>     ShardId. Default: $SHARD"
    echo "  -p <part>      PartId for preparatprocessor. Default: $PART"
    echo "  -n <num>       Max number of records. Default: $NUM_RECS"
    echo "  -y <yt-path>   Path to yt. Default: $PATH_TO_YT"
    echo "  -m             Make all binaries used in script"
    echo "  -t             Test tools also"
    echo "  -h             Print help message."
}

DO_MAKE_BINARIES=0
DO_TEST_TOOLS=0

function make_binaries() {
    mk="ya make -r -j 20 "
    `$mk ./tools/extract_test_data`
    `$mk ./harvester/main`
    `$mk ./vintage/main`
    `$mk ./sendlinkprocessor/main`
    `$mk ./preparatprocessor/main`
    `$mk ./queueprocessor/main`
    `$mk ./exportprocessor/main`
    `$mk ./tools/counters_tool`

    if [ 1 -eq $DO_TEST_TOOLS ] ; then
        `$mk ./tools/prepare_gemini`
        `$mk ./tools/prepare_antispamseomark`
        `$mk ./tools/upload_canonization_data`
    fi
}

while getopts "s:p:n:y:h:mt" OPT; do
    case $OPT in
        s ) SHARD=`printf "%08d" $OPTARG`;;
        p ) PART=`printf "%04d" $OPTARG`;;
        n ) NUM_RECS=$OPTARG;;
        y ) PATH_TO_YT=$OPTARG;;
        h ) print_help ; exit 0;;
        m ) DO_MAKE_BINARIES=1;;
        t ) DO_TEST_TOOLS=1;;
        * ) print_help ; exit 1;;
    esac

    if [ 1 -eq $DO_MAKE_BINARIES ] ; then
        make_binaries
    fi
done

set -e
set -o pipefail
set -x

  ######################
  #      Get data      #
  ######################
:<<eoc
# Clean Lemur instance
if [ `$PATH_TO_YT --proxy $CLUSTER exists $BASE_PREFIX` = "true" ] ; then
    $PATH_TO_YT --proxy $CLUSTER remove -r $BASE_PREFIX
fi

# Extract persistent data from production as incoming
./tools/extract_test_data/extract_test_data -p conf/conf-vla/instance_config_yt.pb.txt -d conf/conf-devel/instance_config_yt.pb.txt -t ../../yweb/robot/ukrop/conf/conf-production/kiwi/triggers.pb.txt -m incoming -c $NUM_RECS -s $SHARD

# Extract renewed data from production
./tools/extract_test_data/extract_test_data -p conf/conf-vla/instance_config_yt.pb.txt -d conf/conf-devel/instance_config_yt.pb.txt -m renewed -s $SHARD -c $NUM_RECS

# Extract sendlink canonization data from production
./tools/extract_test_data/extract_test_data -p conf/conf-vla/instance_config_yt.pb.txt -d conf/conf-devel/instance_config_yt.pb.txt -m sendlink -s $SHARD -c $NUM_RECS

# Copy global data from production
$PATH_TO_YT --proxy $CLUSTER copy -r --source-path $BASE_PREFIX_PROD"/data/global" --destination-path $BASE_PREFIX"/data/global"

# Download webmasterhosts for preparatprocesor
$PATH_TO_YT --proxy $CLUSTER read --format yamr //home/webmaster/prod/export/webmaster-hosts > webmasterhosts.txt

  ######################
  #        Work        #
  ######################
# Harvest data from incoming/final
./harvester/main/harvester -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-common/harvester_config.pb.txt -t ../../yweb/robot/ukrop/conf/conf-production/kiwi/triggers.pb.txt

# Vintage
./vintage/main/vintage -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/vintage_config.pb.txt -s $SHARD -m delta
./vintage/main/vintage -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/vintage_config.pb.txt -s $SHARD -m host
./vintage/main/vintage -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/vintage_config.pb.txt -s $SHARD -m map
./vintage/main/vintage -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/vintage_config.pb.txt -s $SHARD -m combine
./vintage/main/vintage -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/vintage_config.pb.txt -s $SHARD -m global # Note: data/global is now replaced by cropped one

# Sendlink
./sendlinkprocessor/main/sendlinkprocessor -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/sendlinkprocessor_config.pb.txt -m hostcanon
./sendlinkprocessor/main/sendlinkprocessor -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/sendlinkprocessor_config.pb.txt -m gemini

# Preparat

lemur_conf_ext_dir=./
catfilter_url="JUPITER_FILTER_TRIE/filter.trie"
catfilter_file="${lemur_conf_ext_dir}/catfilter.trie"

catfilter_mirrors_url="JUPITER_FILTER_TRIE/mirrors.trie"
catfilter_mirrors_file="${lemur_conf_ext_dir}/catfilter.mirrors.trie"

catfilter_geo_c2p_url="JUPITER_BASE_SEARCH_BUNDLE/geo.c2p"
catfilter_geo_c2p_file="${lemur_conf_ext_dir}/catfilter.geo.c2p"

function common_jupiter_downloader(){

    local _jupiter_base_path _src_path _dst_path _production_state

    _current_state="$(yt get '//home/jupiter/@jupiter_meta/yandex_current_state' | sed 's/\"//g')"
    _jupiter_base_path="//home/jupiter/delivery_snapshot/${_current_state}"
    _src_path="$1"
    _dst_path="$2"
    _formed_path="${_jupiter_base_path}/${_src_path}"

    echo Current state: ${_current_state}
    echo Formed path: ${_formed_path}

    yt download ${_formed_path} > $_dst_path

}

function target_get_catfilter_files {
    common_jupiter_downloader $catfilter_url $catfilter_file.tmp
    common_jupiter_downloader $catfilter_mirrors_url $catfilter_mirrors_file.tmp
    common_jupiter_downloader $catfilter_geo_c2p_url $catfilter_geo_c2p_file.tmp
    mv $catfilter_file.tmp $catfilter_file
    mv $catfilter_mirrors_file.tmp $catfilter_mirrors_file
    mv $catfilter_geo_c2p_file.tmp $catfilter_geo_c2p_file
}

function target_preparatprocessor_split {
    ./preparatprocessor/main/preparatprocessor \
        -i conf/conf-devel/instance_config_yt.pb.txt \
        -l conf/conf-devel/preparatprocessor_config.pb.txt \
        -v conf/conf-devel/vintage_config.pb.txt \
        -m split \
        -s $SHARD \
        --catfilter $catfilter_file \
        --mirrors $catfilter_mirrors_file \
        --c2p $catfilter_geo_c2p_file
}

function target_preparatprocessor_merge {
    ./preparatprocessor/main/preparatprocessor \
        -i conf/conf-devel/instance_config_yt.pb.txt \
        -l conf/conf-devel/preparatprocessor_config.pb.txt \
        -m merge \
        -w ./webmasterhosts.txt \
        -o conf/conf-devel/lookup_config.pb.txt \
        -b $PART \
        --switch auto
}

## to test preparat uncomment 3 lines below
#target_get_catfilter_files
#target_preparatprocessor_split
#target_preparatprocessor_merge

# Queue
./queueprocessor/main/queueprocessor -i conf/conf-devel/instance_config_yt.pb.txt -s $SHARD

# Exports
./exportprocessor/main/exportprocessor -i conf/conf-devel/instance_config_yt.pb.txt -c conf/conf-devel/export_config.pb.txt
eoc

# Merge and read counters
./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m merge
./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m read -a vintage_host -s $SHARD --as-proto > vintage_host.counters
./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m read -a vintage_map -s $SHARD --as-proto > vintage_map.counters
./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m read -a vintage_combine -s $SHARD --as-proto > vintage_combine.counters
./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m read -a sendlinkprocessor_gemini --as-proto > sendlinkprocessor_gemini.counters
./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m read -a sendlinkprocessor_hostcanon --as-proto > sendlinkprocessor_hostcanon.counters
./tools/counters_tool/counters_tool -i conf/conf-devel/instance_config_yt.pb.txt -m read -a exportprocessor --as-proto > exportprocessor.counters

# aux tool's checks
if [ 1 -eq $DO_TEST_TOOLS ] ; then
    yt create -r -i map_node $BASE_PREFIX/incoming/kiwi/final
    yt find $BASE_PREFIX_PROD/incoming/kiwi/final | grep Batch | tail -n 3 | while read t ; do
        yt copy -f $t $BASE_PREFIX/incoming/kiwi/final/`basename $t`
    done

    # prepare input table for prepare_gemini
    YT_POOL=robot-dev-pool yt map --format=yson --src //home/jupiter/gemini/`yt get "//home/jupiter/@jupiter_meta/production_current_state" 2>/dev/null | tr -d '"'`/duplicates --dst //tmp/gemini_duplicates --spec '{job_io = {table_reader = {sampling_rate = 0.001}}}' "cat" ; yt sort -r --sort-by "Host" --sort-by "Path" --sort-by "Region" --src //tmp/gemini_duplicates --dst $BASE_PREFIX/tmp/gemini_duplicates

    ./tools/prepare_gemini/prepare_gemini -i conf/conf-devel/instance_config_yt.pb.txt -t ../../yweb/robot/ukrop/conf/conf-production/kiwi/triggers.pb.txt -u "$BASE_PREFIX/sendlink/gemini_for_fresh" -g $BASE_PREFIX/tmp/gemini_duplicates -c CT_MONSTER --points ../../yweb/robot/ukrop/conf/conf-common/points/localpoints -l ./conf/conf-devel/lookup_config.pb.txt

    ./tools/prepare_antispamseomark/prepare_antispamseomark -s $CLUSTER -a "home/antispam/export/mascot/lemur" --host "$BASE_PREFIX/transfer/antispamseomark_host" --owner "$BASE_PREFIX/transfer/antispamseomark_owner" --dropna

    ./tools/upload_canonization_data/upload_canonization_data -i conf/conf-devel/instance_config_yt.pb.txt -t ../../yweb/robot/ukrop/conf/conf-production/kiwi/triggers.pb.txt

fi
