#!/usr/bin/env bash

set -e

WORK_DIR=/docker-entrypoint-initdb.d/schemas
ARCADIA_PATH=/arcadia

default_migrations() {
    for schema_dir in ${WORK_DIR}/*/
    do
        alias=$(basename ${schema_dir})
        echo "Dropping database ${alias}"
        dropdb --username "$POSTGRES_USER" --if-exists $alias
        echo "Creating database ${alias} from directory ${schema_dir}"
        createdb --username "$POSTGRES_USER" $alias
        readarray -d '' scripts < <(printf '%s\0' ${schema_dir}*sql | sort -zV)
        for script in "${scripts[@]}"
        do
            echo "Run SQL script ${script}:"
            psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" ${alias} -f "${script}"
        done
    done
}

arcadia_migrations() {
    INTEGRATION_TESTS_PATH="$ARCADIA_PATH/taxi/docker-integration-tests"
    eats_services=$(python3 "$INTEGRATION_TESTS_PATH/scripts/get_services.py" "$INTEGRATION_TESTS_PATH/docker-compose.eats.yml" | grep eats)

    for service in ${eats_services}
    do
        search_dir1="$ARCADIA_PATH/taxi/uservices/services/$service"
        search_dir2="$ARCADIA_PATH/taxi/backend-py3/services/$service"
        alias="${service//-/_}"
        if [ -d "$search_dir1" ]; then
            search_dir=$search_dir1
        elif [ -d "$search_dir2" ]; then
            search_dir=$search_dir2
        else
            search_dir=
        fi
        if [ ! -z "$search_dir" ]; then
            readarray scripts < <(find "$search_dir" -name *.sql -regextype posix-egrep -regex ".*(migrations|schemas).*" | sort -zV)
            if [[ ! ${#scripts[@]} -eq 0 ]]; then
                schema_dir=$(dirname ${scripts[0]})
                echo "Creating database ${alias} from directory ${schema_dir}"
                createdb --username "$POSTGRES_USER" $alias
                for script in ${scripts[@]}
                do
                        echo "Run SQL script ${script}:"
                        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" ${alias} -f "${script}" || return 1
                done
            fi
        fi
    done
}

fill_integration_tests() {
    echo "Fill eats_catalog_storage db for integration tests"
    sql_file="${WORK_DIR}/eats_catalog_storage/fill_integration_tests.sql"
    [ -f "$sql_file"  ] && psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" eats_catalog_storage -f "$sql_file"
}

if [ -d "$ARCADIA_PATH" ] && [ "$(ls -A $ARCADIA_PATH)" ]; then
    arcadia_migrations && fill_integration_tests || default_migrations
else
    default_migrations
fi
