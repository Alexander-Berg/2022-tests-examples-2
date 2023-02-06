#!/bin/bash -E
set -aeo pipefail # x

script_dir="$(dirname $(readlink -f $0))"
. ${script_dir}/common.sh

get_generator_deb() {
    case $db_kind in
        psql)  echo "geobase6-generator=6.0-35"
               return
               ;;
    esac

    echo "$FUNCNAME >>> unknown db_kind ${db_kind}"
    exit 1
}

geodata_format="4.1.6"
required_debs_list="curl yandex-internal-root-ca $(get_generator_deb) geobase5-checker=5.3-14 geobase5-utils=5.3-14 libgeobase5-python=5.3-14 libgeobase6-python=6.0-35 python-ipaddr awscli"
geogen_tool="/opt/yandex/geobase/geobase6-generator"

geobin_datafile="${data_path}/geodata4.bin"
geobin_datafile_targz="${data_path}/geodata4.bin.tar.gz"

borders_datafile_src_url="https://proxy.sandbox.yandex-team.ru/554584447"
borders_file="yandex_country_borders.bin"
borders_datafile="${data_path}/${borders_file}"

prepare_assets() {
    echo "assets download [${asdata_src}]..."
    get_assets \
    | tr '-' ' ' \
    | awk '{ print $1, $2, $3 }' \
    > $assets_datafile

    wc -l $assets_datafile
}

check_resources() {
    echo $FUNCNAME
    check_basic_resources
    check_file ${borders_datafile}
}

build() {
    debug_info
    view_remote_content
    install_required_debs ${required_debs_list}
    check_awscli

    prepare_assets
    download_ipregs
    download_tor
    download_borders_section
    check_resources

    generate_geodata4_bin "--country-borders=${borders_datafile}"
    check_geodata_bin
    test_geodata_bin

    generate_targz
    move_result_file_if_required
    upload_s3mds
}

build
