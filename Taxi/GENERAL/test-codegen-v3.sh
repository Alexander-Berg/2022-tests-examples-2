#!/bin/bash
set -ex -o pipefail

SERVICE=$1
export BUILD_DIR=${2:-build}
export GENERATOR_DISABLE_BUILD_DIR_CHECK=1

if ! [ -d services/$SERVICE ]; then
    echo "service $SERVICE not found"
    exit
fi

PYTHON3=/usr/lib/yandex/taxi-py3-2/bin/python3

make clean
rm -rf gen generate $BUILD_DIR
find -name 'CMakeLists.txt' -delete
find -name 'ya.make' -delete
find -name 'ya.make.ext' -delete
find -name 'local-files-dependencies.txt' -delete
find -name 'build-dependencies-debian.txt' -delete
echo '.*' > .arcignore

make gen-$SERVICE
arc add --all
arc commit -m 'generated' -n

make clean
rm -rf gen generate $BUILD_DIR
find -name 'CMakeLists.txt' -delete
find -name 'ya.make' -delete
find -name 'ya.make.ext' -delete
find -name 'local-files-dependencies.txt' -delete
find -name 'build-dependencies-debian.txt' -delete

$PYTHON3 generator3.py --log-level=INFO --build-dir=$BUILD_DIR --generate-debian --services-to-generate $SERVICE

arc status
