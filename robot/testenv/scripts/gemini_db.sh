#!/bin/bash
#!PRECMD SVN_SSH=/Berkanavt/bin/scripts/svn_ssh flock -w 60 /tmp/SVN_UP.LOCK svn export --force svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/robot/deprecated/gemini/db/testenv/scripts/gemini_db.sh /Berkanavt/clustermaster/geminidb/scripts/gemini_db.sh

set -xue -o pipefail -o posix

#!+INCLUDES
. common-start.sh
. cm-common.sh

_scenario() {
    MAIN              = sas-dev-gemini00.search.yandex.net shape=ellipse res=cpu:0
    #GEMINI            = gemini000..gemini099 shape=box
    MAINexport        = sas-dev-gemini00.search.yandex.net 01..10 shape=hexagon res=kiwi:0.51/1
    MAINexport_sasovo = sas-dev-gemini00.search.yandex.net 01..10 shape=hexagon res=kiwi_sasovo:0.51/1

    MAIN                gemini_db_start:
    MAIN                gemini_db_update_configs: gemini_db_start
    MAIN                gemini_db_update_data: gemini_db_start
    MAIN                gemini_db_backup_aggregated: gemini_db_start
    MAIN                gemini_db_actualize_ranking_data: gemini_db_backup_aggregated
    MAIN                gemini_db_actualize_clean_params: gemini_db_backup_aggregated
    MAIN                gemini_db_build_rfl: gemini_db_actualize_clean_params gemini_db_update_data
    MAIN                gemini_db_compress_rfl: gemini_db_build_rfl
    MAIN                gemini_db_actualize: gemini_db_actualize_ranking_data
    MAIN                gemini_db_append_rel_canonical: gemini_db_actualize
    MAIN                gemini_db_redirs_compressor: gemini_db_append_rel_canonical
    MAIN                gemini_db_reduct2mirrors: gemini_db_append_rel_canonical
    MAIN                gemini_db_filter_rfl: gemini_db_reduct2mirrors gemini_db_compress_rfl
    MAIN                gemini_db_filter_regexps: gemini_db_filter_rfl
    MAIN                gemini_db_cut_superdups: gemini_db_filter_regexps
    MAIN                gemini_db_apply_social_info: gemini_db_cut_superdups
    MAIN                gemini_db_urls2semidupsmr: gemini_db_apply_social_info
    MAIN                gemini_db_semidupsmr: gemini_db_urls2semidupsmr
    MAIN                gemini_db_process_big_groups: gemini_db_semidupsmr
    MAIN                gemini_db_semidupsmr2urls: gemini_db_semidupsmr
    MAIN                gemini_db_backup_gemini_db: gemini_db_semidupsmr2urls
    MAIN                gemini_db_stick_parts: gemini_db_backup_gemini_db gemini_db_redirs_compressor
    MAIN                gemini_db_info_incut: gemini_db_stick_parts gemini_db_actualize_ranking_data gemini_db_update_configs
    MAIN                gemini_db_clear_intermediate_tables: gemini_db_info_incut

    MAIN                ALHENA_create_index_mr: gemini_db_info_incut
    #GEMINI              ALHENA_touch_prepared: ALHENA_create_index_mr

    MAIN                gemini_db_create_index: gemini_db_info_incut
    MAIN                gemini_db_calc_sample_stats: gemini_db_info_incut
    MAIN                gemini_db_calc_relev_urls_sample_stats: gemini_db_info_incut
    MAIN                gemini_db_update_statistics: gemini_db_calc_relev_urls_sample_stats
    MAIN                gemini_db_send_mail: gemini_db_update_statistics gemini_db_calc_sample_stats
    MAIN                oxygen_calc_host_factors: gemini_db_actualize
    MAIN                gemini_db_finish: gemini_db_send_mail gemini_db_clear_intermediate_tables gemini_db_process_big_groups oxygen_calc_host_factors retry_on_failure="*/5 * * * *"
    MAIN                gemini_db_restart:

    MAIN                gemini_db_kiwi_sasovo_export_start:
    MAINexport_sasovo   gemini_db_kiwi_sasovo_export: gemini_db_kiwi_sasovo_export_start retry_on_failure="*/5 * * * *"
    MAIN                gemini_db_kiwi_sasovo_export_finish: gemini_db_kiwi_sasovo_export []
    MAIN                gemini_db_kiwi_sasovo_export_restart:

    #GEMINI              ALHENA_check_new_index:
    #GEMINI              ALHENA_get_index: ALHENA_check_new_index
    #GEMINI              ALHENA_index_base: ALHENA_get_index

    MAIN                gemini_db_prepare_aggregated:
}

export PATH=/bin:/usr/bin:/usr/sbin:/usr/local/bin:/Berkanavt/mapreduce/bin:/Berkanavt/gemini_db/bin:/Berkanavt/bin/scripts:/Berkanavt/kiwi/bin


# $cm_url is a global bash variable, required for proper work of /Berkanavt/webscripts/robot-common/common-start.sh (restart of subgraphs)
# XXX is a master_httpport from CM config
cm_url="http://sas-dev-gemini00.search.yandex.net:4140" #FIXME
host=$(hostname -s)
user=$(whoami)
locale
export LC_ALL=C
locale

HOME=/Berkanavt/gemini_db
BIN=$HOME/bin
CONFIGS=$HOME/configs
SCRIPTS=$HOME/scripts
DATA=$HOME/data
RFL=$DATA/rfl
LOCKS=$HOME/locks

DB_GENERATION=$DATA/db_generation
DELTAS_SIZE=$DATA/deltas_size
AGGREGATED_SIZE=$DATA/aggregated_size
REDIRECTS_COUNT=$DATA/redirects_count
NOT_MAINS_COUNT=$DATA/not_mains_count
GROUPS_COUNT=$DATA/groups_count
GROUPS_URLS_COUNT=$DATA/groups_urls_count
CHANGED_MAINS=$DATA/changed_mains
DB_SIZE=$DATA/db_size
FICTIVE_PERCENTS=$DATA/fictive_percents
DEL_LIST=$DATA/del_list
DOCS_COUNT_BY_LANG=$DATA/docs_count_by_lang

# target gemini_db_kiwi_export is clustered, number of clusters is defined there manually!
DB_EXPORT_PARTS_COUNT=10

GROUPS_SIZE_CONFIG=$CONFIGS/groups_size_config
BIG_HOSTS=$CONFIGS/big_hosts

FILTER_RFL=$DATA/filter.rfl
ROBOTS_FILTER_RFL=$DATA/filter.robots.rfl
ROBOTS_FILTER_RFL_NEW=$DATA/filter.robots.rfl.new
FILTER_REGEXPS=$DATA/semidups.rfl

SAMPLE_UNF=$DATA/sample_unf
SAMPLE_DIFF=$DATA/sample_diff
SAMPLE_STATS=$DATA/sample_stats
RELEV_URLS_STATS=$DATA/relev_urls_stats
RELEV_URLS_DIFF_STATS=$DATA/relev_urls_diff_stats

DB_GENERATION_TIME=$DATA/db_generation_time
DB_EXPORT_TIME=$DATA/db_export_time

MR_GEMINI_DB=GeminiDB
MR_GEMINI_DB_PREV=GeminiDBPrev
MR_FINAL_GEMINI_DB=FinalGeminiDB

GEMINI_USERNAME=gemini-db-build
GEMINI_QUOTA=1000
GEMINI_MR_QUOTA=100
KIWI_USERNAME=gemini_relev_urls
KIWI_QUOTA=50

FROM_MAIL="gemini@yandex-team.ru"
TO_MAIL="robot-gemini-reports@yandex-team.ru"
SUBJECT="Test Gemini DB"

MR_ARISTOTLE=aristotle.yt.yandex.net

MR_SERVER=$MR_ARISTOTLE
MR_HOME=robot/gemini_test
MR_AGGREGATED=$MR_HOME/aggregated/
MR_AGGREGATED_BACKUP=$MR_HOME/aggregated_backup/
MR_EXPORT_PATH=$MR_HOME/from_kiwi/
MR_DB_PATH=$MR_HOME/db/
MR_INDEX_PATH=$MR_HOME/index/

MR_NO_CONTENT=NoContentHTTPCode
MR_REDIRECTS=Redirects
MR_REL_CANONICAL=RelCanonical
MR_SIMHASH=Simhash
MR_NO_CONTENT_REL_CANONICAL=NoContentRelCanonical
MR_MIRRORS=Mirrors
MR_RANKING_DATA=RankingData
MR_CLEAN_PARAMS=CleanParams
MR_DEL=Del
MR_SUPERDUPS_DB=robot/deprecated/gemini/sd_mr/sd_db

FILTER_RFL_MEMORY_LIMIT=5368709120

MR_SEMIPUDS_INPUT=$MR_DB_PATH"semidups_input"
MR_SEMIPUDS_OUTPUT=$MR_DB_PATH"semidups_output"

MR_KIWI_EXPORT_RATE=4500
MR_KIWI_EXPORT_LOG=$MR_HOME/kiwi_upload_log/

MR_LOG_LEVEL=1
MR_HOST_FACTORS=$MR_DB_PATH"host_factors"



export MR_RUNTIME=YT
export YT_PREFIX=//home/
export MR_TMP=$MR_HOME/tmp/
export YT_POOL=robot
export YT_TOKEN=aff329fb80ec0a39c1f3cb45fe10569a #gemini_robot fake user
export YT_PROXY=aristotle.yt.yandex.net

# Alhena base

function target_ALHENA_create_index_mr {
    /Berkanavt/gemini/gemini_db/bin/create_index_mr \
        -s $MR_PLATO \
        -i $MR_DB_PATH$MR_FINAL_GEMINI_DB \
        -o $MR_INDEX_PATH"alhena.index" \
        -g /Berkanavt/gemini/config/gemini.cfg \
        -f /Berkanavt/gemini/data/filter.rfl \
        -r /Berkanavt/gemini/data/filter.robots.rfl \
        -m alhena
}

function target_ALHENA_touch_prepared {
    touch /Berkanavt/gemini/BASE/ALHENA.tag
}

# Alhena service

function target_ALHENA_get_index {
    while [ ! -f /Berkanavt/gemini/BASE/ALHENA.tag ]; do
        sleep 300
    done

    rm -rf /Berkanavt/gemini/BASE/ALHENA/*

    cd /Berkanavt/gemini/BASE/ALHENA

    mapreduce-yt \
        -subkey \
        -server $MR_PLATO \
        -read robot/deprecated/gemini/index/alhena.index \
        -lowerkey $(hostname) \
        -upperkey $(hostname) | awk '{print $2"\t"$3"\t"$4"\t"$5}' > alhena.index.txt
}

function target_ALHENA_index_base {
    cd /Berkanavt/gemini/BASE/ALHENA
    cat alhena.index.txt | gemini_alhena_indexer
}

function target_ALHENA_remove_tag {
    rm /Berkanavt/gemini/BASE/ALHENA.tag
}

#------------------------------------------------------------------------------------------------

function write_statistics_record {
    graph=$1
    line=$2
    dt=$3
    value=$4

    wget -O - "http://robotmon-ii/robot/exm_upload.py?graph=$graph&line=$line&dt=$dt&value=$value"
}

function write_statistics {
    stats_filename=$1
    graph=$2
    dt=$3

    cat $stats_filename | \
    while read line; do
        value=`echo $line | sed -n '1p' | awk '{print $1}'`
        line_name=`echo $line | sed -n '1p' | awk '{print $2}'`
        write_statistics_record $graph $line_name $dt $value

        #wget -O - "http://robotmon-ii/robot/exm_upload.py?graph=$graph&line=$line_name&delete=yes"
    done
}

function write_statistics_fake {
    stats_filename=$1
    graph=$2
    dt=$3

    cat $stats_filename | \
    while read line; do
        value=`echo $line | sed -n '1p' | awk '{print $1}'`
        line_name=`echo $line | sed -n '1p' | awk '{print $2}'`
        echo $graph $line_name $dt $value

        #wget -O - "http://robotmon-ii/robot/exm_upload.py?graph=$graph&line=$line_name&delete=yes"
    done
}

function format_file_content {
    file=$1
    result=$2

    cat $file | sort -rnk1 |\
        awk 'BEGIN {printf("<table border=1>");}
        {
            printf("<tr>");
            tokensNumber = split($0, tokens, "\t");
            for (i = 1; i <= tokensNumber; i++) {
                printf("<td>%s", tokens[i]);
            }
            printf("</tr>");
        }
        END {printf("</table>");}'\
        > $result
}

function target_gemini_db_start {
    db_generation_start=$(date +%s)
    echo $db_generation_start > $DB_GENERATION_TIME
}

function target_gemini_db_update_configs {
    SVN_SSH=/Berkanavt/bin/scripts/svn_ssh svn export --force svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/robot/deprecated/gemini/db/testenv/configs $CONFIGS
}

function target_gemini_db_update_data {
    SVN_SSH=/Berkanavt/bin/scripts/svn_ssh svn export --force svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/yweb/common/roboconf/semidups.rfl $DATA

    if [ ! -d "$RFL" ]; then
        mkdir $RFL
    fi

    repeatrsync -t $(fbhost ya)::berkanavt/paramstats/paramstats.rfl.all $RFL/paramstats.rfl
    SVN_SSH=/Berkanavt/bin/scripts/svn_ssh svn export --force svn+ssh://arcadia.yandex.ru/arc/trunk/data/robot/filter/rfl $RFL

    find $RFL -maxdepth 1 -name '*.rfl' |
        while read fileName; do
            cat $fileName
            echo
        done |
        python $SCRIPTS/merge_rfl.py > $FILTER_RFL
}

function target_gemini_db_backup_aggregated {
    mapreduce-yt -copy -src $MR_AGGREGATED$MR_NO_CONTENT -dst $MR_AGGREGATED_BACKUP$MR_NO_CONTENT
    mapreduce-yt -copy -src $MR_AGGREGATED$MR_REDIRECTS -dst $MR_AGGREGATED_BACKUP$MR_REDIRECTS
    mapreduce-yt -copy -src $MR_AGGREGATED$MR_REL_CANONICAL -dst $MR_AGGREGATED_BACKUP$MR_REL_CANONICAL
    mapreduce-yt -copy -src $MR_AGGREGATED$MR_SIMHASH -dst $MR_AGGREGATED_BACKUP$MR_SIMHASH
    mapreduce-yt -copy -src $MR_AGGREGATED$MR_NO_CONTENT_REL_CANONICAL -dst $MR_AGGREGATED_BACKUP$MR_NO_CONTENT_REL_CANONICAL
    mapreduce-yt -copy -src $MR_AGGREGATED$MR_RANKING_DATA -dst $MR_AGGREGATED_BACKUP$MR_RANKING_DATA
    mapreduce-yt -copy -src $MR_AGGREGATED$MR_CLEAN_PARAMS -dst $MR_AGGREGATED_BACKUP$MR_CLEAN_PARAMS
}

function target_gemini_db_actualize_ranking_data {
    main_deltas_prefix=$MR_EXPORT_PATH$MR_RANKING_DATA"/final/"
    del_deltas_prefix=$MR_EXPORT_PATH$MR_DEL"/final/"
    del_field_name_with_timestamp="0"

    actualize_kiwi_export \
        -s $MR_SERVER \
        --deltas-prefix $main_deltas_prefix \
        --aggregated $MR_AGGREGATED$MR_RANKING_DATA \
        --format protobin \
        --erase-deltas \
        --del-deltas-prefix $del_deltas_prefix \
        --del-aggregated $MR_AGGREGATED$MR_DEL \
        --del-format plaintext \
        --del-field-name $del_field_name_with_timestamp \
        -e $MR_LOG_LEVEL
}

function target_gemini_db_actualize_clean_params {
    deltas_prefix=$MR_EXPORT_PATH"CleanParams/final/"
    field_name_with_timestamp="RobotsLastAccess"
    record_separator=$'\r\n'

    actualize_kiwi_export \
        -s $MR_SERVER \
        --deltas-prefix $deltas_prefix \
        --aggregated $MR_AGGREGATED$MR_CLEAN_PARAMS \
        --field-name $field_name_with_timestamp \
        --record-separator "$record_separator" \
        --erase-deltas \
        --format plaintext \
        --lower-keys \
        -e $MR_LOG_LEVEL
}

function target_gemini_db_build_rfl {
    record_separator=$'\r\n'

    build_rfl \
        -s $MR_SERVER \
        -i $MR_AGGREGATED$MR_CLEAN_PARAMS \
        -o $MR_DB_PATH"clean_params" \
        --record-separator "$record_separator" \
        -e $MR_LOG_LEVEL

    mapreduce-yt -read $MR_DB_PATH"clean_params" | \
        awk 'BEGIN {FS = "\t";}
        {
            printf("host:%s\n", $1);
            tokensNumber = split($0, tokens, "\t");
            for (i = 2; i <= tokensNumber; i++) {
                printf("clean-param: %s\n", tokens[i]);
            }
            printf("\n");
        }'\
        > $ROBOTS_FILTER_RFL_NEW
}

function target_gemini_db_compress_rfl {
    cp $ROBOTS_FILTER_RFL_NEW $ROBOTS_FILTER_RFL_NEW"_uncompressed"
    rfl_compressor $ROBOTS_FILTER_RFL_NEW $ROBOTS_FILTER_RFL_NEW"2"
    mv $ROBOTS_FILTER_RFL_NEW"2" $ROBOTS_FILTER_RFL_NEW
}

function target_gemini_db_actualize {
    mr_gemini_merge_kiwi_delta \
        -s $MR_SERVER \
        --data-path $MR_EXPORT_PATH \
        --aggregated $MR_AGGREGATED \
        --no-content $MR_NO_CONTENT \
        --redirects $MR_REDIRECTS \
        --relcanonical $MR_REL_CANONICAL \
        --simhash $MR_SIMHASH \
        --no-content-relcanonical $MR_NO_CONTENT_REL_CANONICAL \
        --del $MR_DEL \
        --deltas-size $DELTAS_SIZE \
        --aggregated-size $AGGREGATED_SIZE \
        --docs-count-by-lang $DOCS_COUNT_BY_LANG \
        -e $MR_LOG_LEVEL
}

function target_gemini_db_append_rel_canonical {
    mr_gemini_append_rel_canonical \
        -s $MR_SERVER \
        --db-path $MR_DB_PATH \
        --aggregated $MR_AGGREGATED \
        --relcanonical $MR_REL_CANONICAL \
        --no-content-relcanonical $MR_NO_CONTENT_REL_CANONICAL \
        --simhash $MR_SIMHASH \
        -e $MR_LOG_LEVEL
}

function target_gemini_db_redirs_compressor {
    mr_gemini_redirs_compressor \
        -s $MR_SERVER \
        --db-path $MR_DB_PATH \
        --aggregated $MR_AGGREGATED \
        --redirects $MR_REDIRECTS \
        --redirects-count $REDIRECTS_COUNT \
        -e $MR_LOG_LEVEL
}

function target_gemini_db_reduct2mirrors {
    mr_gemini_reduction2mirrors \
        -s $MR_SERVER \
        --db-path $MR_DB_PATH \
        --aggregated $MR_AGGREGATED \
        --simhash $MR_SIMHASH \
        --mirrors $MR_MIRRORS \
        -e $MR_LOG_LEVEL

    mapreduce-yt -drop $MR_DB_PATH"simhash_host"
}

function target_gemini_db_filter_rfl {
    mr_gemini_filter_rfl \
        -s $MR_SERVER \
        --db-path $MR_DB_PATH \
        --filter-rfl $FILTER_RFL \
        --robots-filter-rfl $ROBOTS_FILTER_RFL_NEW \
        --memory-limit $FILTER_RFL_MEMORY_LIMIT \
        -e $MR_LOG_LEVEL

    mapreduce-yt -drop $MR_DB_PATH"from_main_mirrors"
}

function target_gemini_db_filter_regexps {
    mr_gemini_filter_regexps \
        -s $MR_SERVER \
        --db-path $MR_DB_PATH \
        --filter-regexps $FILTER_REGEXPS \
        -e $MR_LOG_LEVEL

    mapreduce-yt -drop $MR_DB_PATH"mains_after_rfl"
}

function target_gemini_db_cut_superdups {
    mr_gemini_cut_superdups \
        -s $MR_SERVER \
        --db-path $MR_DB_PATH \
        --superdups-db $MR_SUPERDUPS_DB \
        -e $MR_LOG_LEVEL

    mapreduce-yt -drop $MR_DB_PATH"regexps_not_filtered"
}

function target_gemini_db_apply_social_info {
    mr_gemini_apply_social_info \
        -s $MR_SERVER \
        --db-path $MR_DB_PATH \
        -e $MR_LOG_LEVEL

    mapreduce-yt -drop $MR_DB_PATH"mains_after_superdups"
}

function target_gemini_db_urls2semidupsmr {
    mr_gemini_urls2semidupsmr \
        -s $MR_SERVER \
        --db-path $MR_DB_PATH \
        --big-hosts-file $BIG_HOSTS \
        -e $MR_LOG_LEVEL

    #mapreduce-yt -drop $MR_DB_PATH"mains_after_social"
}

function target_gemini_db_semidupsmr {
    mr_gemini_semidupsmr cls \
        --server $MR_SERVER \
        --memcfg 1G \
        --input-table $MR_SEMIPUDS_INPUT \
        --output-table $MR_SEMIPUDS_OUTPUT \
        --memory-limit 4000

    mapreduce-yt -drop $MR_DB_PATH"semidups_input"
}

function target_gemini_db_process_big_groups {
    mr_gemini_semidupsmr2urls \
        -s $MR_SERVER \
        --db-path $MR_DB_PATH \
        --semidups-output semidups_output.big_output \
        --simhash-groups simhash_groups.big_output \
        --first-step \
        -e $MR_LOG_LEVEL
}

function target_gemini_db_semidupsmr2urls {
    mr_gemini_semidupsmr2urls \
        -s $MR_SERVER \
        --db-path $MR_DB_PATH \
        -e $MR_LOG_LEVEL
}

function target_gemini_db_backup_gemini_db {
    mapreduce-yt -copy -src $MR_DB_PATH$MR_GEMINI_DB -dst $MR_DB_PATH$MR_GEMINI_DB_PREV
}

function target_gemini_db_stick_parts {
    mr_gemini_stick_parts \
        -s $MR_SERVER \
        --db-path $MR_DB_PATH \
        --not-mains-count $NOT_MAINS_COUNT \
        --db $MR_GEMINI_DB \
        -e $MR_LOG_LEVEL
}

function target_gemini_db_info_incut {
    fictive_percents_count=$(mr_grep-dev -s $MR_SERVER -k "%2525252525" -c $MR_DB_PATH$MR_GEMINI_DB)
    echo -e "$fictive_percents_count\t5_times" > $FICTIVE_PERCENTS

    generation_id=`cat $DB_GENERATION | sed -n '1p' | awk '{print $1}'`
    echo $generation_id

    mr_gemini_db_info_incut \
        -s $MR_SERVER \
        --db-path $MR_DB_PATH \
        --aggregated $MR_AGGREGATED \
        --generation-id $generation_id \
        --groups-count $GROUPS_COUNT \
        --groups-urls-count $GROUPS_URLS_COUNT \
        --groups-size-config $GROUPS_SIZE_CONFIG \
        --db $MR_GEMINI_DB \
        --mirrors $MR_MIRRORS \
        --ranking-data $MR_RANKING_DATA \
        --final-db $MR_FINAL_GEMINI_DB \
        --db-size $DB_SIZE \
        -e $MR_LOG_LEVEL

    mapreduce-yt -reduce "cat | awk -v OFS='\t' '
        {
            prev_not_main = cur_not_main;
            prev_main = cur_main;
            cur_not_main = \$1;
            cur_main = \$2;
            if (cur_not_main == prev_not_main) {
                all++;
                if (cur_main != prev_main) {
                    diff++;
                }
            }
        }
        END {print diff, all;}'"\
        -src $MR_DB_PATH$MR_GEMINI_DB -src $MR_DB_PATH$MR_GEMINI_DB_PREV -dst $MR_DB_PATH$MR_GEMINI_DB"_diff"

    mapreduce-yt -sort -src $MR_DB_PATH$MR_GEMINI_DB"_diff" -dst $MR_DB_PATH$MR_GEMINI_DB"_diff"
    mapreduce-yt -map "cat | awk -v OFS='\t' '{ diff += \$1; all += \$2;} END {print diff, all;}'"\
        -src $MR_DB_PATH$MR_GEMINI_DB"_diff" -dst $MR_DB_PATH$MR_GEMINI_DB"_diff_agr"
    mapreduce-yt -read $MR_DB_PATH$MR_GEMINI_DB"_diff_agr" | awk 'BEGIN {OFS = "\t";} {print $1, "changed_mains"}' > $CHANGED_MAINS

    mapreduce-yt -inputformat "<enable_table_index=true>yamr" -reducews "cat | awk -v OFS='\t' '
        BEGIN {ind = 0; not_main_to_main = 0; main_to_not_main = 0;}
        NF == 1 {ind = \$0;}
        NF == 2 {
            prev_not_main = cur_not_main;
            cur_not_main = \$1;
            main[ind] = \$2;
            if (cur_not_main == prev_not_main) {
                if (main[0] != cur_not_main && main[1] == cur_not_main) {
                    not_main_to_main++;
                }
                if (main[0] == cur_not_main && main[1] != cur_not_main) {
                    main_to_not_main++;
                }
            }
        }
        END {print not_main_to_main, main_to_not_main;}'"\
        -src $MR_DB_PATH$MR_GEMINI_DB_PREV -src $MR_DB_PATH$MR_GEMINI_DB -dst $MR_DB_PATH"not_mains_stats"

    mapreduce-yt -sort -src $MR_DB_PATH"not_mains_stats" -dst $MR_DB_PATH"not_mains_stats"
    mapreduce-yt -map "cat | awk -v OFS='\t' '
        {first += \$1; second += \$2;}
        END {print first, second}'"\
        -src $MR_DB_PATH"not_mains_stats" -dst $MR_DB_PATH"not_mains_stats_agr"
    mapreduce-yt -read $MR_DB_PATH"not_mains_stats_agr" | awk 'BEGIN {OFS = "\t";} {print $1, "not_main_to_main"; print $2, "main_to_not_main"}' >> $CHANGED_MAINS

    new_generation_id=$(echo "$generation_id+1" | bc)
    echo $new_generation_id > $DB_GENERATION

    db_generation_end=`date +%s`
    echo $db_generation_end >> $DB_GENERATION_TIME
}

function target_gemini_db_clear_intermediate_tables {
    mapreduce-yt -drop $MR_DB_PATH"regexps_not_filtered"
    mapreduce-yt -drop $MR_DB_PATH"mains_after_rfl"
    mapreduce-yt -drop $MR_DB_PATH"from_main_mirrors"
    mapreduce-yt -drop $MR_DB_PATH"simhash_host"
}

function target_gemini_db_create_index {
    create_index_mr \
        -s $MR_SERVER \
        -e 2 \
        -o $MR_INDEX_PATH \
        -i $MR_DB_PATH$MR_FINAL_GEMINI_DB \
        -f "/Berkanavt/gemini/data/filter.rfl" \
        -r "/Berkanavt/gemini/data/filter.robots.rfl"
}

function target_gemini_db_update_statistics {
    dt=$(date +%Y-%m-%d+%R)

    #deltas size
    write_statistics_fake $DELTAS_SIZE "gemini_db_deltas_size" $dt

    #aggregated size
    write_statistics_fake $AGGREGATED_SIZE "gemini_db_aggregated_size" $dt

    #redirects count
    write_statistics_fake $REDIRECTS_COUNT "gemini_db_redirects" $dt

    #not mains count
    write_statistics_fake $NOT_MAINS_COUNT "gemini_db_not_mains" $dt

    #groups count
    write_statistics_fake $GROUPS_COUNT "gemini_db_groups_size" $dt

    #groups urls count
    write_statistics_fake $GROUPS_URLS_COUNT "gemini_db_groups_urls_count" $dt

    #changed mains
    write_statistics_fake $CHANGED_MAINS "gemini_db_changed_mains" $dt

    #fictive percents count
    write_statistics_fake $FICTIVE_PERCENTS "gemini_db_fictive_percents_count" $dt

    #relev urls stats
    write_statistics_fake $RELEV_URLS_STATS "gemini_db_relev_urls_stats" $dt

    #relev urls diff stats
    write_statistics_fake $RELEV_URLS_DIFF_STATS "gemini_db_relev_urls_diff_stats" $dt

    #docs count by lang
    write_statistics_fake $DOCS_COUNT_BY_LANG "gemini_db_docs_count_by_lang" $dt
}

function target_gemini_db_calc_sample_stats {
    sample_size=10000
    sample_table=$MR_GEMINI_DB"_sample"
    mr_sample-dev \
        -s $MR_SERVER \
        -sub \
        -f \
        -n $sample_size $MR_DB_PATH$MR_GEMINI_DB $MR_DB_PATH$sample_table

    cd $DATA

    mapreduce-yt -subkey -read $MR_DB_PATH$sample_table | awk 'BEGIN {OFS = "\t"; FS = "\t";} {print $1, $3, $2;}' > sample
    sample_size=$(wc -l sample | awk '{print $1}')
    cat sample | awk '{print $1;}' > sample_urls

    geminicl \
        -f sample_urls \
        --format text \
        -u $GEMINI_USERNAME \
        --quota $GEMINI_QUOTA \
        --reveal-url-not-found &> sample_urls_canonized

    >unf_urls
    >not_unf_urls
    cat sample_urls_canonized | awk 'BEGIN {OFS = "\t";} NF != 3 {print $1 > "unf_urls";} NF == 3 {print $1 > "not_unf_urls";}'
    rm -f sample_urls

    cat sample | sort -t $'\t' > sample_sorted
    cat unf_urls | sort -t $'\t' >  unf_urls_sorted
    cat not_unf_urls | sort -t $'\t' > not_unf_urls_sorted
    rm -f sample unf_urls not_unf_urls sample_urls_canonized

    join sample_sorted unf_urls_sorted -t $'\t' > unf_sample
    join sample_sorted not_unf_urls_sorted -t $'\t' > not_unf_sample
    rm -f sample_sorted unf_urls_sorted not_unf_urls_sorted

    >not_unf_source
    >not_unf_new
    cat not_unf_sample | awk 'BEGIN {OFS = "\t"; FS = "\t";} {print $1, NR > "not_unf_source"; print $2, NR > "not_unf_new";}'

    mapreduce-yt -write $MR_DB_PATH"not_unf_source" < not_unf_source

    mr_geminicl \
        -s $MR_SERVER \
        -i $MR_DB_PATH"not_unf_source" \
        -o $MR_DB_PATH"not_unf_source_canonized" \
        -u $GEMINI_USERNAME \
        -q $GEMINI_MR_QUOTA \
        --join-tables

    mapreduce-yt -read $MR_DB_PATH"not_unf_source_canonized" > not_unf_source_canonized
    cat not_unf_source_canonized | awk 'BEGIN {OFS = "\t";} {print $2, $1;}' | sort -t $'\t' > not_unf_source_canonized_sorted
    mapreduce-yt -drop $MR_DB_PATH"not_unf_source"
    mapreduce-yt -drop $MR_DB_PATH"not_unf_source_canonized"
    rm -f not_unf_source not_unf_source_canonized

    mapreduce-yt -write $MR_DB_PATH"not_unf_new" < not_unf_new

    mr_geminicl \
        -s $MR_SERVER \
        -i $MR_DB_PATH"not_unf_new" \
        -o $MR_DB_PATH"not_unf_new_canonized" \
        -u $GEMINI_USERNAME \
        -q $GEMINI_MR_QUOTA \
        --join-tables

    mapreduce-yt -read $MR_DB_PATH"not_unf_new_canonized" > not_unf_new_canonized
    cat not_unf_new_canonized | awk 'BEGIN {OFS = "\t";} {print $2, $1;}' | sort -t $'\t' > not_unf_new_canonized_sorted
    mapreduce-yt -drop $MR_DB_PATH"not_unf_new"
    mapreduce-yt -drop $MR_DB_PATH"not_unf_new_canonized"
    rm -f not_unf_new not_unf_new_canonized

    join not_unf_source_canonized_sorted not_unf_new_canonized_sorted -t $'\t' | awk 'BEGIN {OFS = "\t";} $2 != $3 {print $2;}' | sort -t $'\t' > different_groups_source_urls
    join different_groups_source_urls not_unf_sample -t $'\t' > different_groups_not_unf_sample
    rm -f not_unf_source_canonized_sorted not_unf_new_canonized_sorted different_groups_source_urls not_unf_sample

    mapreduce-yt -subkey -write $MR_DB_PATH"different_groups_not_unf_sample" < different_groups_not_unf_sample

    mr_geminicl \
        -s $MR_SERVER \
        -i $MR_DB_PATH"different_groups_not_unf_sample" \
        -o $MR_DB_PATH"different_groups_not_unf_sample_canonized" \
        -u $GEMINI_USERNAME \
        -q $GEMINI_MR_QUOTA \
        --join-tables \
        --save-source-url \
        --save-subkey

    mapreduce-yt -subkey -read $MR_DB_PATH"different_groups_not_unf_sample_canonized" > different_groups_not_unf_sample_canonized
    mapreduce-yt -drop $MR_DB_PATH"different_groups_not_unf_sample"
    mapreduce-yt -drop $MR_DB_PATH"different_groups_not_unf_sample_canonized"

    rm -f different_groups_not_unf_sample

    cat different_groups_not_unf_sample_canonized | awk '{OFS = "\t"; FS = "\t";} {print $2, $1, $3, $4;}' | awk '{OFS = "\t"; FS = "\t";} $2 != $3 {print $0;}' > final_diff
    rm -f different_groups_not_unf_sample_canonized

    mv -f unf_sample $SAMPLE_UNF
    mv -f final_diff $SAMPLE_DIFF

    unf_urls_count=$(wc -l $SAMPLE_UNF | awk '{print $1}')
    diff_size=$(wc -l $SAMPLE_DIFF | awk '{print $1}')

    unf_part=$(echo "scale=4; 100.0*$unf_urls_count/$sample_size;" | bc)
    diff_part=$(echo "scale=4; 100.0*$diff_size/$sample_size;" | bc)

    echo "Sample size: $sample_size urls<br>" > $SAMPLE_STATS
    echo "URL_NOT_FOUND: $unf_urls_count urls ($unf_part%) - $host:$SAMPLE_UNF<br>" >> $SAMPLE_STATS
    echo "Diff: $diff_size urls ($diff_part%) - $host:$SAMPLE_DIFF<br>" >> $SAMPLE_STATS

    cat $SAMPLE_STATS
}

function target_gemini_db_calc_relev_urls_sample_stats {
    cd $DATA
    wget http://dump.scrimmage.yandex.ru/web/ru/judgements/web-ru-all-dump.tsd

    cat web-ru-all-dump.tsd |
        awk '
        $2 == "RELEVANT_PLUS" || $2 == "VITAL" || $2 == "USEFUL" {
            if (rand() < 0.000003) {
                print $1;
            }
        }
        ' > vital_urls_sample

    cat vital_urls_sample |
        kwworm -u $KIWI_USERNAME --maxrps $KIWI_QUOTA read --mode MERGE -d 9999 -k 50 -f text -q '
            GeminiBeautyUrl = GetGeminiBeautyUrl(?GeminiDataTimestamp, ?GeminiMainUrl, ?GeminiDupReason, ?GeminiBeautyUrl);
            SearchBaseMainUrl = (if (!IsNull(?SearchBaseMainUrl)) then $SearchBaseMainUrl else "ERROR");
            return GeminiBeautyUrl, SearchBaseMainUrl;' |
            awk '
            BEGIN {
                OFS = "\t";
            }
            NF == 0 {
                url = "";
                gemini_beauty_url = "";
                search_base_main_url = "";
            }
            NF != 0 {
                if (url == "") {
                    url = $1;
                }
                else if (gemini_beauty_url == "") {
                    gemini_beauty_url = $1;
                }
                else {
                    search_base_main_url = $1;
                    print url, gemini_beauty_url, search_base_main_url
                }
            }
            ' > gemini_vs_robot_diff

    cat gemini_vs_robot_diff |
        awk '
        {
            all++;
            gemini_beauty_url = $2;
            search_base_main_url = $3;
            if (gemini_beauty_url != search_base_main_url && search_base_main_url != "ERROR") {
                different++;
            }
            else {
                same++;
            }
        }
        END {
            if (all > 0) {
                printf "%f\tsame\n", 100 * same / all;
                printf "%f\tdifferent\n", 100 * different / all;
            }
        }
        ' > $RELEV_URLS_STATS

    cat gemini_vs_robot_diff |
        awk '
        NF == 3 {
            all++;
            if (tolower($2) == tolower($3)) {
                case_count++
            }
            else if ($2 == "ERROR") {
                error_count++;
            }
            else if (length($2) < length($3)) {
                better_count++;
            }
            else if (length($2) == length($3)) {
                same_length++;
            }
            else if ($1 ~ "wikipedia.org/wiki") {
                wiki_count++;
            }
            else {
                if (match($2, "[^:]+://[^/]+")) {
                    gemini_host = substr($2, RSTART, RLENGTH);
                    if (match($3, "[^:]+://[^/]+")) {
                        walrus_host = substr($3, RSTART, RLENGTH);
                    }
                }
                if (gemini_host != walrus_host) {
                    different_hosts_count++;
                }
                else {
                    worse_count++;
                }
            }
        }
        END {
            if (all > 0) {
                printf "%f\tcase_count\n", 100 * case_count / all;
                printf "%f\terror_count\n", 100 * error_count / all;
                printf "%f\tbetter_count\n", 100 * better_count / all;
                printf "%f\tsame_length\n", 100 * same_length / all;
                printf "%f\twiki_count\n", 100 * wiki_count / all;
                printf "%f\tdifferent_hosts_count\n", 100 * different_hosts_count / all;
                printf "%f\tworse_count\n", 100 * worse_count / all;
            }
        }
        ' > $RELEV_URLS_DIFF_STATS

    rm web-ru-all-dump.tsd*

    cat $RELEV_URLS_STATS
    cat $RELEV_URLS_DIFF_STATS
}

function target_gemini_db_send_mail {
    generation_id=`cat $DB_GENERATION | sed -n '1p' | awk '{print $1}'`
    old_generation_id=`echo "$generation_id-1" | bc`

    db_generation_start=`cat $DB_GENERATION_TIME | sed -n '1p' | awk '{print $1}'`
    db_generation_end=`cat $DB_GENERATION_TIME | sed -n '2p' | awk '{print $1}'`
    db_generation_time_diff=`echo "$db_generation_end-$db_generation_start" | bc`

    tmp_file=$DATA/tmp_file
    >$tmp_file

    mail_source=$DATA/mail_source
    >$mail_source
    echo "From: $FROM_MAIL" >> $mail_source
    echo "To: $TO_MAIL" >> $mail_source
    echo "Subject: $SUBJECT" >> $mail_source
    echo "MIME-Version: 1.0" >> $mail_source
    echo "Content-Type: text/html" >> $mail_source
    echo "" >> $mail_source
    echo "New <a href='http://yt.yandex.net/aristotle/#page=navigation&path=//home/$MR_DB_PATH$MR_GEMINI_DB'>Test Gemini DB</a> was successfully generated.<br>" >> $mail_source
    echo "<br>" >> $mail_source
    echo "Gemini DB <i>generation</i> number: $old_generation_id.<br>" >> $mail_source
    echo "<a href='http://sas-dev-gemini00.search.yandex.net:4140/targets'>DB building process</a><br>" >> $mail_source
    echo "<br>" >> $mail_source
    echo "Statistics:<br>" >> $mail_source
    echo "<br>" >> $mail_source

    format_file_content $DELTAS_SIZE $tmp_file
    cat $tmp_file >> $mail_source
    echo "<br>" >> $mail_source

    format_file_content $AGGREGATED_SIZE $tmp_file
    cat $tmp_file >> $mail_source
    echo "<br>" >> $mail_source

    format_file_content $REDIRECTS_COUNT $tmp_file
    cat $tmp_file >> $mail_source
    echo "<br>" >> $mail_source

    format_file_content $NOT_MAINS_COUNT $tmp_file
    cat $tmp_file >> $mail_source
    echo "<br>" >> $mail_source

    format_file_content $GROUPS_COUNT $tmp_file
    cat $tmp_file >> $mail_source
    echo "<br>" >> $mail_source

    format_file_content $GROUPS_URLS_COUNT $tmp_file
    cat $tmp_file >> $mail_source
    echo "<br>" >> $mail_source

    format_file_content $CHANGED_MAINS $tmp_file
    cat $tmp_file >> $mail_source
    echo "<br>" >> $mail_source

    format_file_content $RELEV_URLS_STATS $tmp_file
    cat $tmp_file >> $mail_source
    echo "<br>" >> $mail_source

    format_file_content $RELEV_URLS_DIFF_STATS $tmp_file
    cat $tmp_file >> $mail_source
    echo "<br>" >> $mail_source

    cat $SAMPLE_STATS >> $mail_source

    cat $mail_source | sendmail -t
}

function target_oxygen_calc_host_factors {
    mr_gemini_host_erf calc \
        --mr-server $MR_SERVER \
        --input $MR_AGGREGATED$MR_SIMHASH \
        --input $MR_AGGREGATED$MR_REL_CANONICAL \
        --output $MR_HOST_FACTORS \
        --mirrors $MR_AGGREGATED$MR_MIRRORS
}

function target_gemini_db_finish {
    true
}

function target_gemini_db_restart {
    # restart_subgraph is a bash function from cm-common.sh
    restart_subgraph "gemini_db_finish"
}



function target_gemini_db_kiwi_sasovo_export_start {
    true
}

function target_gemini_db_kiwi_sasovo_export {
    part=$1

    generation_id=`cat $DB_GENERATION | sed -n '1p' | awk '{print $1}'`
    old_generation_id=`echo "$generation_id-1" | bc`
    date=$(date +%Y%m%d)

    db_size=`cat $DB_SIZE | sed -n '1p' | awk '{print $1}'`
    db_part_size=`echo "$db_size/$DB_EXPORT_PARTS_COUNT" | bc`
    db_part_begin=`echo "($part-1)*$db_part_size" | bc`
    db_part_end=`echo "$db_part_begin+$db_part_size-1" | bc`

    if [ "$part" = "$DB_EXPORT_PARTS_COUNT" ]; then
        db_part_end=`echo "$db_size-1" | bc`
    fi

    echo "$db_part_begin $db_part_end"
    mr_gemini_kiwi_export \
        -s $MR_SERVER \
        -r 2000 \
        -G $old_generation_id \
        -i $MR_DB_PATH$MR_FINAL_GEMINI_DB \
        -o $MR_KIWI_EXPORT_LOG$date"_sasovo_"$part \
        -b $db_part_begin \
        -e $db_part_end \
        -k "apteryx.yandex.net"
}

function target_gemini_db_kiwi_sasovo_export_finish {
    true
}

function target_gemini_db_kiwi_sasovo_export_restart {
    # restart_subgraph is a bash function from cm-common.sh
    restart_subgraph "gemini_db_kiwi_sasovo_export_finish"
}



function target_gemini_db_prepare_aggregated {
    MR_HOME_PRODUCTION=robot/gemini
    MR_AGGREGATED_PRODUCTION=$MR_HOME_PRODUCTION/aggregated/
    MR_DB_PATH_PRODUCTION=$MR_HOME_PRODUCTION/db/
    MR_PEOPLESEARCH_IDS=peoplesearch_ids
    MR_TEST_PART=100

    for table in $MR_NO_CONTENT $MR_REDIRECTS $MR_REL_CANONICAL $MR_SIMHASH $MR_NO_CONTENT_REL_CANONICAL $MR_RANKING_DATA
    do
        records_count=$(mr_wc-dev -s aristotle.yt.yandex.net -w $MR_AGGREGATED_PRODUCTION$table | awk '{print $1;}')
        records_count=$(echo "$records_count/$MR_TEST_PART" | bc)
        mr_sample-dev -s aristotle.yt.yandex.net -sub -k -n $records_count -f $MR_AGGREGATED_PRODUCTION$table $MR_AGGREGATED$table
        mapreduce-yt -sort -src $MR_AGGREGATED$table -dst $MR_AGGREGATED$table
    done


    mapreduce-yt -copy -src $MR_AGGREGATED_PRODUCTION$MR_CLEAN_PARAMS -dst $MR_AGGREGATED$MR_CLEAN_PARAMS
    mapreduce-yt -copy -src $MR_AGGREGATED_PRODUCTION$MR_MIRRORS -dst $MR_AGGREGATED$MR_MIRRORS
    mapreduce-yt -copy -src $MR_DB_PATH_PRODUCTION$MR_PEOPLESEARCH_IDS -dst $MR_DB_PATH$MR_PEOPLESEARCH_IDS
}




TARGET=${1:-none}
pwd
umask
date '+%Y%m%dT%H%M%S'

lockfile="$LOCKS/$TARGET.${2:-}.lock"
(
    flock 300
    target_$TARGET ${2:-}
) 300>"$lockfile"
rm -f "$lockfile"
date '+%Y%m%dT%H%M%S'

