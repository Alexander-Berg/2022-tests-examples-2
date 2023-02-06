#!PRECMD SVN_SSH=/Berkanavt/bin/scripts/svn_ssh flock -w 60 /tmp/SVN_UP.LOCK svn export --force svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/robot/deprecated/gemini/testenv/scripts/gemini-test.sh /Berkanavt/clustermaster/scripts/gemini-test.sh
#!/usr/local/bin/bash

set -xue -o pipefail -o posix

#!+INCLUDES
. /Berkanavt/clustermaster/scripts/common-merge.sh

_scenario () {
    MAINHOST := !hostlist:MASTER

    MASTER              = !hostlist:MASTER shape=ellipse
    MASTERwalrus        = !hostlist:MASTERWALRUS !hostlist:MASTERWALRUS:clusters shape=ellipse
    GEMINI              = !hostlist:GEMINI shape=rectangle
    GEMINIclusters      = !hostlist:SEGMENTED !hostlist:SEGMENTED:clusters shape=hexagon
    GEMINIreplica       = !hostlist:REPLICA !hostlist:REPLICA:clusters shape=hexagon

    MASTER start_service_global:

    MASTER get_configs_global: start_service_global
    GEMINI get_configs_local: get_configs_global

    MASTER get_data_global: get_configs_local
    GEMINI get_data_local: get_data_global

    MASTER get_urlrules_global: get_data_local
    GEMINI get_urlrules_local: get_urlrules_global

    MASTER get_filterso: get_urlrules_local
    MASTER create_rfl_filter: get_filterso
    MASTER create_robots_filter: create_rfl_filter
    MASTER create_mapped_filters: create_robots_filter
    GEMINI get_filters_local: create_mapped_filters

    MASTER get_mirrors_global: get_filters_local
    MASTER build_test_mirrors: get_mirrors_global
    GEMINI get_mirrors_local: build_test_mirrors

    MASTERwalrus get_tables: get_mirrors_local
    MASTER backup_old_index_tables: get_tables

    MASTER create_new_index_tables: get_tables
    GEMINI get_base_info_local: create_new_index_tables
    MASTER data_and_conf_prepared: get_base_info_local
    GEMINI create_map: data_and_conf_prepared
    GEMINI replica_create_map: data_and_conf_prepared
    GEMINIclusters prep_base: create_map res=net:1/2
    GEMINIclusters index_main: prep_base
    GEMINIclusters compress_index: index_main res=cpu:1/4
    GEMINIreplica copy_base_to_replicas: replica_create_map compress_index [] res=net:1/2
    GEMINIreplica uncompress_index: copy_base_to_replicas
    MASTER all_replica_done: uncompress_index []
    GEMINI read_new_db: all_replica_done
    GEMINIclusters move_cur_prev: read_new_db res=io:1/10
    GEMINIclusters move_new_cur: move_cur_prev res=io:1/10
    GEMINIreplica replica_move_cur_prev: read_new_db res=io:1/10
    GEMINIreplica replica_move_new_cur: replica_move_cur_prev res=io:1/10
    GEMINI stop_castor: move_new_cur replica_move_new_cur []
    GEMINI start_castor: stop_castor
    GEMINI swap_db: start_castor []
    MASTER all_done: swap_db [] start_castor [] mailto=abolkhovityanov,yuryalekseev restart_on_success="*/5 * * * *"

    GEMINI check_pollux_alive: restart_on_success="*/2 * * * *" retry_on_failure="*/2 * * * *"
    GEMINI check_castors_alive: restart_on_success="*/2 * * * *" retry_on_failure="*/2 * * * *"

    GEMINI stop_pollux:
    GEMINI start_pollux:

    MASTER create_points_global:
    GEMINI get_points_local: create_points_global
}



############################ Environment ###########################


export PATH=/bin:/usr/bin:/usr/local/bin:/Berkanavt/bin:/Berkanavt/bin/scripts:/Berkanavt/mapreduce/bin:/Berkanavt/gemini/scripts:/Berkanavt/gemini/bin


host=$(hostname -s)
user=$(whoami)


datdir="/Berkanavt/gemini"
basedir="$datdir/BASE"
points="$datdir/configs/points"
web_basedir="$basedir/WEB"
web_datadir="/Berkanavt/gemini/data/WEB"


mr_cluster_betula="betula00.search.yandex.net:8013"
mr_cluster_abies="abies00.search.yandex.net:8013"
mr_cluster_cedar="cedar00.search.yandex.net:8013"
mr_cluster_redwood="redwood00.search.yandex.net:8013"

# YT clusters
MR_YT_PLATO=plato.yt.yandex.net
MR_YT_ARISTOTLE=aristotle.yt.yandex.net
MR_YT_KANT=kant.yt.yandex.net

MR_YT_PROD=$MR_YT_ARISTOTLE

mr_user_robot="robot"
mr_base_path="robot/gemini_test"
mr_prev_base_path="robot/gemini_test_prev"
index_tables="strong_hash_2_main_url weak_hash_2_main_url"


pollux_port=30000
pollux_mon_port=31000


castor_mon_port=21000
castor_http_port=8080
castor_quota_port=25000
castor_msg_bus_port=20000


config_files="gemini.cfg points squota.gemini.xml simple_owners.lst urlsconvert.urls.re url_generators.def urlsconvert.thumbs.re thumbfromurl.re"
db_files="base.info common.hosts.index strong.hosts.index weak.hosts.index common.paths.index strong.paths.index weak.paths.index common.offsets.index strong.offsets.index weak.offsets.index"

tab=$(printf '\t')


rsyncoptions="-ar -v --timeout=300 --blocking-io"
export repeatrsync_rsynccmd="rsync $rsyncoptions"


rsync_gemini_secretfile="/Berkanavt/gemini/configs/secret.gemini"



##################### Common functions ####################


function prepare_base {
    local from
    local to
    local home=$5

    cat $2 | awk -v cl=$1 '{if($1==cl) print $0}' > $home/$1/new/temp.txt
    numrow=$(cat $home/$1/new/temp.txt | wc -l)
    for i in $(jot $numrow 1); do
        head -n $i $home/$1/new/temp.txt | tail -n 1 | awk '{print $2"\n"$3}' > $home/$1/new/temp.txt.2
        from=$(head -n 1 $home/$1/new/temp.txt.2)
        to=$(tail -n 1 $home/$1/new/temp.txt.2)
        mapreduce-dev -server $mr_cluster_cedar -stderrlevel 5 -subkey -read $3 -lowerkey $from -upperkey $to -opt net_table=ipv6 > $home/$1/new/index.tmp
        cat $home/$1/new/index.tmp >> $4
    done

    rm -f $home/$1/new/index.tmp
}


function prepare_base_common {
    mkdir -p $2/$1

    rm -rf $2/$1/new
    mkdir -p $2/$1/new

    mkdir -p $2/$1/cur

    mkdir -p $2/$1/prev

    prepare_base $1 $basedir/hash.map "$mr_base_path"/strong_hash_2_main_url $2/$1/new/strong.index $2
    prepare_base $1 $basedir/hash.map "$mr_base_path"/weak_hash_2_main_url $2/$1/new/weak.index $2
    cp $2/base.info $2/$1/new/
    rm -f $2/$1/new/temp.*
}


function prepare_index {
    local home=$1
    local weak=$home/weak.index
    local strong=$home/strong.index
    local common=$home/common.index
    local ncweak=$home/nc.weak.index
    local ncstrong=$home/nc.strong.index

    sort -u $weak -o $weak.nondup
    sort -u $strong -o $strong.nondup

    comm -12 $weak.nondup $strong.nondup > $common
    comm -23 $weak.nondup $strong.nondup > $ncweak
    comm -13 $weak.nondup $strong.nondup > $ncstrong

    gemini_indexer -i $common -h $home/common.hosts.index -p $home/common.paths.index -o $home/common.offsets.index
    gemini_indexer -i $ncstrong -h $home/strong.hosts.index -p $home/strong.paths.index -o $home/strong.offsets.index
    gemini_indexer -i $ncweak -h $home/weak.hosts.index -p $home/weak.paths.index -o $home/weak.offsets.index
}



######################## Targets ######################################


function target_get_configs_global {
    mkdir -p $datdir/configs/global

    SVN_SSH=/Berkanavt/bin/scripts/svn_ssh svn export --force svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/robot/deprecated/gemini/testenv/configs $datdir/configs/global
    SVN_SSH=/Berkanavt/bin/scripts/svn_ssh svn export --force svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/yweb/webscripts/video/canonize/config $datdir/configs/global
}


function target_get_configs_local {
    for file in $config_files; do
        repeatrsync -L \
            rsync://$(fbhost $MAINHOST)/gemini/$datdir/configs/global/$file \
            $datdir/configs \
            --password-file=$rsync_gemini_secretfile
    done
}


function target_get_data_global {
    mkdir -p $datdir/data/global

    repeatrsync -t $(fbhost ya)::berkanavt/polyglot/poly.trie $datdir/data/global/poly.trie
}


function target_get_data_local {
    repeatrsync -L \
        rsync://$(fbhost $MAINHOST)/gemini/$datdir/data/global/poly.trie \
        $datdir/data \
        --password-file=$rsync_gemini_secretfile
}


function target_get_tables {
    srcTable="robot/mainurlinfo/mainurl.$1"
    dstTable="robot/mainurlinfo_test/mainurl.$1"

    MR_USER=$user mapreduce-dev \
        -stderrlevel 5 \
        -server $mr_cluster_cedar \
        -copy \
        -src $srcTable \
        -dst $dstTable \
        -opt net_table=fastbone

    mr_ls-dev -s $mr_cluster_cedar $dstTable > /dev/null
}


function target_backup_old_index_tables {
    for tbl in $index_tables; do
        MR_USER=$user mapreduce-dev -stderrlevel 5 -server $mr_cluster_cedar -copy -src "$mr_base_path"/$tbl -dst "$mr_prev_base_path"/$tbl
    done

    for tbl in $(mr_ls-dev -s $mr_cluster_cedar "$mr_base_path"/*); do
        MR_USER=$user mapreduce-dev -stderrlevel 5 -server $mr_cluster_cedar -drop $tbl
    done
}


function target_get_urlrules_global {
    mkdir -p $web_datadir

    SVN_SSH=/Berkanavt/bin/scripts/svn_ssh svn export --force svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/yweb/urlrules $web_datadir/urlrules
}


function target_get_urlrules_local {
    mkdir -p $web_datadir

    for file in areas.lst 2ld.list ungrouped.list; do
        repeatrsync -L \
            rsync://$(fbhost $MAINHOST)/gemini/$web_datadir/urlrules/$file \
            $web_datadir \
            --password-file=$rsync_gemini_secretfile
    done
}


function target_get_filterso {
    mkdir -p $web_datadir/global

    repeatrsync -t $(fbhost ya)::berkanavt/filter/filter.so $web_datadir/global/filter.so
}


function target_create_rfl_filter {
    mkdir -p $web_datadir/global

    repeatrsync -t $(fbhost ya)::berkanavt/paramstats/paramstats.rfl.all $web_datadir/global/paramstats.rfl

    SVN_SSH=/Berkanavt/bin/scripts/svn_ssh svn export --force svn+ssh://arcadia.yandex.ru/arc/trunk/data/robot/filter $web_datadir/robot_filter

    find $web_datadir/robot_filter/ -maxdepth 2 -name '*.rfl' -not -path '$web_datadir/robot_filter/nevada/*' |
        while read fileName; do
            cat $fileName
            echo
        done |
        python $datdir/scripts/merge_rfl.py > $web_datadir/robot_filter/filter.rfl.tmp

    mkdir -p $web_datadir/global

    mv $web_datadir/robot_filter/filter.rfl.tmp $web_datadir/global/filter.rfl

    mkdir -p $web_basedir/global

    filter_rfl_timestamp=$(stat -c %Y $web_datadir/global/filter.rfl)
    printf "rfl: %s\n" $filter_rfl_timestamp >> $web_basedir/global/base.info
}


function target_create_robots_filter {
    record_separator=$'\r\n'

    export MR_RUNTIME=YT
    export YT_PREFIX=//home/
    export MR_TMP=robot/deprecated/gemini/tmp/
    export YT_POOL=robot
    export YT_TOKEN=aff329fb80ec0a39c1f3cb45fe10569a #gemini_robot fake user
    export YT_PROXY=$MR_YT_PROD

    mkdir -p $web_datadir/global

    build_rfl \
        -s $MR_YT_PROD \
        -i robot/deprecated/gemini/aggregated/CleanParams \
        -o robot/gemini_test/db/clean_params \
        --record-separator "$record_separator" \
        -e 1

    mapreduce-yt -read robot/gemini_test/db/clean_params | \
        awk 'BEGIN {FS = "\t";}
        {
            printf("host:%s\n", $1);
            tokensNumber = split($0, tokens, "\t");
            for (i = 2; i <= tokensNumber; i++) {
                printf("clean-param: %s\n", tokens[i]);
            }
            printf("\n");
        }'\
        > $web_datadir/global/filter.robots.rfl.tmp

    cp $web_datadir/global/filter.robots.rfl.tmp $web_datadir/global/filter.robots.rfl.tmp"_uncompressed"

    rfl_compressor $web_datadir/global/filter.robots.rfl.tmp $web_datadir/global/filter.robots.rfl.tmp.compressed

    mv $web_datadir/global/filter.robots.rfl.tmp.compressed $web_datadir/global/filter.robots.rfl
    rm -f $web_datadir/global/filter.robots.rfl.tmp*
}


function target_create_mapped_filters {
    filter_build -h $web_datadir/global -f rfl -m map
}


function target_get_filters_local {
    for file in filter.so filter.rfl filter.robots.rfl filter.rfl.mapped filter.robots.rfl.mapped; do
        repeatrsync -L \
            rsync://$(fbhost $MAINHOST)/gemini/$web_datadir/global/$file \
            $web_datadir/ \
            --password-file=$rsync_gemini_secretfile
    done
}


function target_get_mirrors_global {
    repeatrsync -t sticker05::mirrors_db/all.res $web_datadir/global/test.mirrors.res
    repeatrsync -t $(fbhost ya)::berkanavt/webmaster/mirrors.trie $web_datadir/global/mirrors.trie
    repeatrsync -t $(fbhost ya)::berkanavt/bin/data/mirrors.trie $web_datadir/global/new.mirrors.trie

    mirrors_timestamp=$(stat -c %Y $web_datadir/global/mirrors.trie)
    printf "mirrors: %s\n" $mirrors_timestamp  >> $web_basedir/global/base.info
}


function target_build_test_mirrors {
    mirrmanip -l @m $web_datadir/global/test.mirrors.res -f @m $web_datadir/global/test.mirrors.res.nolang
    mirrmanip -t $web_datadir/global/test.mirrors.res.nolang $web_datadir/global/test.mirrors.trie /var/tmp
}


function target_get_mirrors_local {
    for file in  mirrors.trie test.mirrors.trie new.mirrors.trie; do
        repeatrsync -L \
            rsync://$(fbhost $MAINHOST)/gemini/$web_datadir/global/$file \
            $web_datadir/ \
            --password-file=$rsync_gemini_secretfile
    done
}


function target_create_new_index_tables {
    MR_USER=$user create_index_mr \
        -s $mr_cluster_cedar \
        -e 5 \
        -m web \
        -i robot/mainurlinfo_test/ \
        -o $mr_base_path/ \
        -h /Berkanavt/clustermaster/config/host.cfg \
        -f $web_datadir/global/filter.rfl.mapped \
        -r $web_datadir/global/filter.robots.rfl.mapped

    index_timestamp=$(date +%s)
    printf "index: %s\n" $index_timestamp >> $web_basedir/global/base.info
}


function target_get_base_info_local {
    repeatrsync -L \
        rsync://$(fbhost $MAINHOST)/gemini/$web_basedir/global/base.info \
        $web_basedir/ \
        --password-file=$rsync_gemini_secretfile
}


function target_create_map {
    gemini_lookup -m UsePoints -h $(hostname) -i $points -o $basedir/hash.map
    if [ ! -s $basedir/hash.map ]; then
        echo "Create zero length $basedir/hash.map file"
        return 1
    fi
}


function target_replica_create_map {
    gemini_lookup -m UsePoints -h $(hostname) -R -i $points -o $basedir/hash.replica.map
}


function target_prep_base {
    prepare_base_common $1 $web_basedir
}


function target_index_main {
    prepare_index $web_basedir/$1/new
}


function target_compress_index {
    db_tgz="$web_basedir/$1/new.tgz"
    cd $web_basedir/$1/new
    tar -cvzPf $db_tgz $db_files
}


function target_copy_base_to_replicas {
    mainrep=$(awk -v b=$1 'NR==(b+1)' $points | awk '{print $2}' | awk -F: '{print $1}')

    repeatrsync -L \
        rsync://$(fbhost $mainrep)/gemini/$web_basedir/$1/new.tgz \
        $web_basedir/$1/ \
        --password-file=$rsync_gemini_secretfile
}


function target_uncompress_index {
    mkdir -p $web_basedir/$1

    rm -rf $web_basedir/$1/new
    mkdir -p $web_basedir/$1/new

    mkdir -p $web_basedir/$1/cur

    mkdir -p $web_basedir/$1/prev

    cd $web_basedir/$1/new
    tar -xvf $web_basedir/$1/new.tgz
}


function target_read_new_db {
}


function target_move_cur_prev {
    find $web_basedir/$1/prev/ -mindepth 1 -maxdepth 1 | xargs rm -f
    find $web_basedir/$1/cur/ -mindepth 1 -maxdepth 1 | xargs -I % mv % $web_basedir/$1/prev/
}


function target_replica_move_cur_prev {
    find $web_basedir/$1/prev/ -mindepth 1 -maxdepth 1 | xargs rm -f
    find $web_basedir/$1/cur/ -mindepth 1 -maxdepth 1 | xargs -I % mv % $web_basedir/$1/prev/
}


function target_move_new_cur {
    find $web_basedir/$1/cur/ -mindepth 1 -maxdepth 1 | xargs rm -f
    find $web_basedir/$1/new/ -mindepth 1 -maxdepth 1 | xargs -I % mv % $web_basedir/$1/cur/
}


function target_replica_move_new_cur {
    find $web_basedir/$1/cur/ -mindepth 1 -maxdepth 1 | xargs rm -f
    find $web_basedir/$1/new/ -mindepth 1 -maxdepth 1 | xargs -I % mv % $web_basedir/$1/cur/
}


function target_swap_db {
}


function target_stop_castor {
    kill -15 $(pidof gemini_castor)

    while [ ! -z $(pidof gemini_castor) ]; do
        sleep 5
    done
}


function target_start_castor {
    gemini_castor \
        -c $datdir/configs/gemini.cfg \
        --verbose-main \
        -w 14 \
        -l \
        -p $castor_msg_bus_port \
        --http-port $castor_http_port \
        --mon-port $castor_mon_port \
        --mcast-port $castor_quota_port \
        --max-in-fl 50000

    until curl -s "localhost:${castor_mon_port}/summary" | grep "Initialized:" | grep -q "1"; do
        sleep 5
    done
}



################################# Placeholders ###################################


function target_start_service_global {
    rm -f $web_basedir/global/base.info
}


function target_data_and_conf_prepared {
    echo "OK"
}


function target_all_done {
    echo "OK"
}


function target_all_replica_done {
    echo "OK"
}

########################## Targets out of graph ##########################


function target_stop_pollux {
    kill -15 $(pidof gemini_pollux)

    while [ ! -z $(pidof gemini_pollux) ]; do
        sleep 5
    done
}


function target_start_pollux {
    gemini_pollux \
        -c $datdir/configs/gemini.cfg \
        --verbose-main \
        -w 12 \
        -l \
        -p $pollux_port \
        --mon-port $pollux_mon_port \
        --max-in-fl 10000

    until curl -s "localhost:${pollux_mon_port}/summary" | grep "Initialized:" | grep -q "1"; do
        sleep 5
    done
}


function target_check_pollux_alive {
    if [ -z $(pidof gemini_pollux) ]; then
        return 1
    fi
    return 0
}


function target_check_castors_alive {
    if [ -z $(pidof gemini_castor) ]; then
        return 1
    fi
    return 0
}


function target_create_points_global {
    gemini_lookup -m CreatePoints -c $datdir/configs/global/gemini.cfg -o $datdir/configs/global/points
}


function target_get_points_local {
    repeatrsync -L \
        rsync://$(fbhost $MAINHOST)/gemini/$datdir/configs/global/points \
        $datdir/configs \
        --password-file=$rsync_gemini_secretfile
}


TARGET=${1:-none}
pwd
umask
date '+%Y%m%dT%H%M%S'
lockfile="$datdir/locks/$TARGET.${2:-}.lock"
(
    flock 300
    target_$TARGET ${2:-}
) 300>"$lockfile"
rm -f "$lockfile"
date '+%Y%m%dT%H%M%S'

