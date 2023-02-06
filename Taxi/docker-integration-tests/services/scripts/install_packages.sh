#!/usr/bin/env bash
set -e

rm -f /bin/systemctl
ln -s /bin/true /bin/systemctl

project_dir=/taxi/services/$project
if [ -d $project_dir/deb ]; then
    cd $project_dir/deb
        dpkg-scanpackages . /dev/null > Packages
    cd -
    # must be first line for highest priority
    sed -i "1ideb [trusted=yes] file:$project_dir/deb ./" /etc/apt/sources.list
fi

apt-get update
apt-get install -y --allow-unauthenticated --allow-downgrades --no-install-recommends $packages

apt-get clean all
