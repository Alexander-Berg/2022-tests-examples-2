#!/bin/bash -E
set -aeo pipefail # x

script_dir="$(dirname $(readlink -f $0))"
. ${script_dir}/common.sh

required_debs_list="curl python-ipaddr libipreg1-python yandex-yt-python"

build() {
    debug_info
    install_required_debs ${required_debs_list}

    /usr/bin/python2.7 ${script_dir}/build_layout.py --layout-json ${result_fname_path}
    move_result_file_if_required
}

build
