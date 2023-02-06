#!/bin/bash -E
set -aeo pipefail # x

script_dir="$(dirname $(readlink -f $0))"
. ${script_dir}/geodata6-common.sh

borders_datafile_src_url="https://proxy.sandbox.yandex-team.ru/last/REVERSE_BORDERS_WORLD/${borders_file}"

build
