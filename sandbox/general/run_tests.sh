#!/usr/bin/env bash
set -e

# Download resource from Sandbox, if not already downloaded
function download() {
    if [ -r "$2" ] ; then
        # already downloaded
        return 0
    fi
    wget --no-check-certificate "https://proxy.sandbox.yandex-team.ru/$1" -O "$2"
}

function download_by_skynet() {
    if [ -r "$2" ] ; then
        # already downloaded
        return 0
    fi
    sky get -wu "$1"
    echo "$2 was downloaded"
}

function remove() {
    if [ -e "$1" ] ; then
        rm -r "$1"
    fi
}

my_path=$(dirname $(readlink -f $0))
cd $my_path

wd=$(pwd)
mkdir tmp_dir_0 # in order not to have errors in the next line
rm -r tmp_dir_*

# run from sandbox-tasks
cd ../../../../
sandbox_tasks=$(pwd)
cd ../../../
arcadia_root=$(pwd)

cd $sandbox_tasks
PYTHONPATH=.:$arcadia_root/contrib/libs/protobuf/python  python projects/common/differ/ut/ut.py $wd

