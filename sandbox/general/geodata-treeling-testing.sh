#!/bin/bash -E
set -aeo pipefail # x

script_dir="$(dirname $(readlink -f $0))"
. ${script_dir}/common.sh

get_generator_deb() {
    case $db_kind in
        psql)  echo "geobase6-generator=6.0-38"
               return
               ;;
    esac

    echo "$FUNCNAME >>> unknown db_kind ${db_kind}"
    exit 1
}

get_generator_path() {
    case $db_kind in
        mysql) echo "/opt/yandex/geobase5/geobase5-generator"
               return
               ;;
        psql)  echo "/opt/yandex/geobase/geobase6-generator"
               return
               ;;
    esac

    echo "$FUNCNAME >>> unknown db_kind ${db_kind}"
    exit 1
}

geodata_format="4.1.7"
required_debs_list="curl jq yandex-internal-root-ca geobase5-checker=5.3-14 geobase5-utils=5.3-14 libgeobase5-python=5.3-14 libgeobase6-python=6.0-35 $(get_generator_deb) yandex-yt-python awscli"
geogen_tool="$(get_generator_path)"

geobin_datafile="${data_path}/geodata4-tree+ling.bin"
geobin_datafile_targz="${data_path}/geodata4-tree+ling.tar.gz"

borders_data_url="https://proxy.sandbox.yandex-team.ru/1214947072" # TODO(dieash@) last/REVERSE_BORDERS_WORLD
windows_datafile="${data_path}/borders-window.list"

prepare_windows_data() { # LIB-713
    echo $FUNCNAME

    local wnd_arch="window.tar.bz2"
    local data_url="${borders_data_url}/${wnd_arch}"

    echo "border-windows download from [${data_url}]..."

    echo "#@desc	min_lat@double	min_lon@double	max_lat@double	max_lon@double" > $windows_datafile
    curl -s --insecure ${data_url} \
    | tar xjv --to-stdout \
    | awk -v FS='\t' -v OFS='\t' '{ print $1, $2, $3, $4, $5 }' \
    | awk 'NF > 5 { print "#" NR ";" NF ":" $0; } { print }' \
    >> $windows_datafile

    local min_windows_amount=45000 # at least in RU
    local window_amount=$(cat $windows_datafile | wc -l)
    if [ $window_amount -lt $min_windows_amount ]; then
        echo ">>>STRANGE: not enough of regions' windows data - ${window_amount}"
        exit 1
    fi
}

spec_value_column_name="covid-19"
spec_values_fname="${data_path}/${spec_value_column_name}.list"

prepare_spec_values_data() {
    echo $FUNCNAME

    check_file ${yt_traits_datafile}
    . ${yt_traits_datafile}

    check_file ${data_path}/add_flags.config
    . ${data_path}/add_flags.config  # SPEC_VALUES_YT_TABLE_PATH

    if [ -z "${SPEC_VALUES_YT_TABLE_PATH}" ]; then
        echo "no spec-table // SKIP"
        return
    fi

    echo "spec-data download [${SPEC_VALUES_YT_TABLE_PATH}]..."
    echo "#@desc ${spec_value_column_name}@string" > ${spec_values_fname}
    YT_PROXY=${yt_proxy} YT_TOKEN=${yt_token} yt read ${SPEC_VALUES_YT_TABLE_PATH} --format "<columns=[reg_id;spec_value];missing_value_mode=print_sentinel;enable_escaping=false>schemaful_dsv" | tee --append ${spec_values_fname} | wc -l
}

check_spec_values_data() {
    check_new_columns ${spec_value_column_name} ${spec_values_fname}
}

windows_data_check() {
    echo $FUNCNAME

    check_fname="${data_path}/borders-window-errors.list"
    detected_bugs=$(${script_dir}/check-borders-windows.py ${geobin_datafile} $windows_datafile 2>&1 | tee ${check_fname} | wc -l)
    if [ 0 -lt $detected_bugs ]; then
        echo ">>> BUG: borders-windows problems were detected, ${detected_bugs} // ${geodata_tree_datafile}"
        cat ${check_fname}
	    exit 1
    fi
}

check_resources() {
    echo $FUNCNAME

    check_file $ipreg_datafile
    check_file $assets_datafile
    check_file $tor_datafile

    check_file ${db_traits_datafile} 5
    check_file $windows_datafile

    check_file ${eu_regions_fname} 7000
    check_file ${iso_alpha3_fname} 210

    if [ -s ${spec_values_fname} ]; then
        check_file ${spec_values_fname} 1
    fi
}

regs_json_fname="_all_regs.json"
tbl_scheme="_tbl.scheme"

prepare_yt_export() {
    echo $FUNCNAME

    check_file ${geobin_datafile}

    python ${script_dir}/export2yt.py --geodata=${geobin_datafile} --root-id=10000 --table-data=${regs_json_fname} --table-scheme=${tbl_scheme}
    cat ${regs_json_fname} | jq '.reg_id' > /dev/null
}

upload_yt_export() {
    echo $FUNCNAME

    check_file ${regs_json_fname}
    check_file ${tbl_scheme}

    check_file ${yt_traits_datafile}
    . ${yt_traits_datafile}

    local yt_table_path="//home/geotargeting/public/geobase/regions"

    # upload to tmp-table
    for yt_proxy_name in hahn arnold; do
        cat ${regs_json_fname} | YT_PROXY=${yt_proxy_name} YT_TOKEN=${yt_token} yt write "$(cat ${tbl_scheme})${yt_table_path}.tmp" --format="<encode_utf8=false>json"
        echo "... ${yt_proxy_name} (tmp)"
    done

    # tbl-replacement
    for yt_proxy_name in hahn arnold; do
        YT_PROXY=${yt_proxy_name} YT_TOKEN=${yt_token} yt move --force ${yt_table_path}.tmp ${yt_table_path}
    done
}

check_linguistics() {
    echo $FUNCNAME
    ${script_dir}/check-lings.py --geodata=${geobin_datafile}
}

build() {
    debug_info
    install_required_debs ${required_debs_list}
    check_awscli

    prepare_eu_list
    prepare_iso_alpha3_list
    prepare_spec_values_data
    prepare_faked_resource
    prepare_windows_data
    check_resources

    local additional_flags="--add-db-fields=okato,oktmo --new-fields-data=${eu_regions_fname},${windows_datafile},${iso_alpha3_fname}"
    if [ -s ${spec_values_fname} ]; then
        additional_flags="${additional_flags},${spec_values_fname}"
    fi

    generate_geodata4_bin "${additional_flags}"
    check_geodata_bin
    check_spec_values_data
    check_eu_list
    check_iso_alpha3_list
    windows_data_check
    check_linguistics

    generate_targz
    move_result_file_if_required
    upload_s3mds
}

build
