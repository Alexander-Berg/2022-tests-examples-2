#!/bin/bash -E
set -aeo pipefail # x

script_dir="$(dirname $(readlink -f $0))"
. ${script_dir}/common.sh

required_debs_list="--allow-unauthenticated postgresql-client yandex-internal-root-ca"

geobin_datafile="${data_path}/$(date +%Y%m%d.%H%M).geodb.psql.dump"
geobin_datafile_targz="${data_path}/geodb.tar.gz"

prepare_psql_deb_src() {
    echo "${FUNCNAME}"

    echo "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main" > pgdg.list
    sudo mv pgdg.list /etc/apt/sources.list.d/
}

last_db_backup_fname=""

get_last_db() {
    echo "${FUNCNAME}"

    local db_arch="geodb.tar.gz"
    curl -OJ http://proxy.sandbox.yandex-team.ru/last/GEOADMIN_DB_BACKUP
    test -e ${db_arch}
    tar xvf ${db_arch}
    last_db_backup_fname=$(tar tf ${db_arch} | head -1)
}

update_test_db() {
    echo "${FUNCNAME} // $*"

    local in_file=$1
    if [ ! -s ${in_file} ]; then
        echo "NO DATA in ${in_file}"
        exit 1
    fi

    . ${db_traits_datafile}
    local db_conn_str="postgresql://${db_user}:${db_pswd}@${db_host}:${db_port}/geodb_testing?sslmode=allow"
    local upd_log=$(pg_restore --dbname="${db_conn_str}" --clean --if-exists --verbose ${in_file} 2>&1 | tee ${in_file}.update_Log >&2)
}

main_cycle() {
    prepare_psql_deb_src
    install_required_debs ${required_debs_list}
    get_last_db
    update_test_db ${last_db_backup_fname}
}

main_cycle
