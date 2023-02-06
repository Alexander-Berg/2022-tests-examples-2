#!/usr/bin/env bash
if [[ "$(uname)" == "Darwin" ]]; then
    realpath() {
        [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
    }
    export realpath
fi
SHORT_OPTS="hs:v"
LONG_OPTS="service:,billing-docker:,billing-py3:,billing-test-data:,output:"
CONFIG_LONG_OPTS="help,no-restart,no-stop-vms,cleanup"
CWD=$"$(dirname $"$(realpath $"$0")")"
source "${CWD}/_shared.sh"

do_cleanup=0
no_restart=0
no_stop_vms=0
verbose=0

services=()
args=()
dirs_to_test=()

FAILED=0

function dump_config() {
    echo "Services to test: ${services[*]}"
    echo "Tests: ${dirs_to_test[*]}"
    echo "Do not restart: ${no_restart}"
    echo "Do not stop vms after tests: ${no_stop_vms}"
}

function usage() {
    echo -e "Usage:\n"
    echo "$(basename ${0}) [-v] [--no-restart] [--no-stop-vms] [--make] [--s|service=service_name]"
    echo -e "\t[--billing-py3=billing-py3-path]"
    echo -e "\t[--billing-docker=billing-docker-path]"
    echo -e "\t[--billing-test-data=billing-test-data-path]"
    echo -e "\t[--output=output-path]"
    echo -e "\tpath_or_subset_name [path_or_subset_name ...]"
    echo
    printf "\t%-40s%s\n" \
        "-v" "Verbose mode" \
        "--no-restart" "Do not restart vm's for tests (for different set execution)" \
        "--no-stop-vms" "Do not stop vm's after complete (for watching database state)" \
        "--cleanup" "perform reset permissions on the generated files and exit" \
        "-s name|service=name" "Test service named 'name' (Default only billing-accounts)" \
        "--billing-py3=path" "Custom path to billing-py3" \
        "--billing-docker=path" "Custom path to billing-docker" \
        "--billing-test-data=path" "Custom path to billing-test-data" \
        "--ouput=path" "path for output artifacts" \
        "path_or_subset_name" "Subset name for services (from billing-test-data) or path to custom tests"
}

function setdefaults() {
    if [[ ${#services[*]} -eq 0 ]]; then
        services[${#services[*]}]='billing-accounts'
    fi
    if [[ ${#args[*]} -eq 0 ]]; then
        args[${#args[*]}]='0min'
    fi
}

function generate_test_dirs() {
    for r in `seq 0 $((${#args[*]}-1))`; do
        test_dir=${args[$r]}
        if [[ -d ${args[$r]} ]]; then
            dirs_to_test[${#dirs_to_test[*]}]=$test_dir
        else
            for s in `seq 0 $((${#services[*]}-1))`; do
                service=${services[$s]}
                tmp_dir="${GIT_TAXI_TEST_PATH}/${service}-${test_dir}"
                if [[ ! -d "${tmp_dir}" ]]; then
                    (>&2 echo "tests for ${service} and ${test_dir} not found")
                else
                    dirs_to_test[${#dirs_to_test[*]}]=$tmp_dir
                fi
            done
        fi
    done
}

function run_sibilla() {
    local ARGS="${@:3}"
    local target=$2
    export TEST_PATH="$(realpath ${1})"
    export SOURCE
    # build
    make -C "$GIT_TAXI_BILLING_DOCKER_PATH" $target || return 1
    # and execute tests
    docker-compose -f "$GIT_TAXI_BILLING_DOCKER_PATH/docker-compose.yml" \
        -f "$CWD/docker-compose.yml" \
        run --rm billing-testing-light /taxi/sibilla/bin/run.sh "$([[ $verbose == 1 ]] && echo '--verbose')" ${ARGS}
    return $?
}

function run_test() {
    run_sibilla $1 init-db --warmup-db
    run_sibilla $1 stq-services --warmup-stq
    run_sibilla $1 billing --tests
    return $?
}

function execute_tests() {
    for idx in `seq 0 $((${#dirs_to_test[*]}-1))`; do
        test_path=${dirs_to_test[$idx]}
        echo "Run tests from ${test_path}"
        if ! run_test $test_path ; then
             FAILED=$[ $FAILED + 1 ]
        fi
        echo "apply package versions to the output..."
        cp -f "$test_path/generated"/versions-*.txt "$OUTPUT_PATH" || true
    done
}

function tears_up() {
    if [[ $no_restart -eq 0 ]]; then
        echo "Tears up: clean up old data"
        make -C $GIT_TAXI_BILLING_DOCKER_PATH down
        make -C $GIT_TAXI_BILLING_DOCKER_PATH clean-logs
    fi
    if [[ ! -d $GIT_TAXI_BACKEND_PATH/generated ]]; then
        echo "Tears up: generate py3 data"
        make -C $GIT_TAXI_BACKEND_PATH gen-lib-billing
    fi
}

function reset_dirs() {
    reset_dir $GIT_TAXI_BACKEND_PATH
    reset_dir $GIT_TAXI_BILLING_DOCKER_PATH
    reset_dir $GIT_TAXI_TEST_PATH
    reset_dir $GIT_TAXI_BILLING_TESTING_PATH
    reset_dir $OUTPUT_PATH
}

function tears_down() {
    if [[ $no_restart -eq 0 ]] && [[ $no_stop_vms -eq 0 ]]; then
        make -C $GIT_TAXI_BILLING_DOCKER_PATH clean
        reset_dirs
    fi
}


options=$(get_options "$@") || {
    usage
    exit 1
}

BASE_PATH=$(realpath "${CWD}/..")
GIT_TAXI_BILLING_TESTING_PATH=$CWD
: ${GIT_TAXI_BACKEND_PATH:="$BASE_PATH/backend-py3"}
: ${GIT_TAXI_BILLING_DOCKER_PATH:="$BASE_PATH/billing-docker"}
: ${GIT_TAXI_TEST_PATH:="$BASE_PATH/billing-test-data"}
: ${OUTPUT_PATH:="$BASE_PATH/output"}
: ${SOURCE:="rtc"}

eval set -- "$options"
while true; do
    case "$1" in
        -v)
            verbose=1
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        --cleanup)
            do_cleanup=1
            ;;
        --service|-s)
            shift
            services[${#services[*]}]=$1
            ;;
        --billing-docker)
            shift
            GIT_TAXI_BILLING_DOCKER_PATH=$1
            ;;
        --billing-py3)
            shift
            GIT_TAXI_BACKEND_PATH=$1
            ;;
        --billing-test-data)
            shift
            GIT_TAXI_TEST_PATH=$1
            ;;
        --output)
            shift
            OUTPUT_PATH="$1"
            ;;
        --no-restart)
            no_restart=1
            ;;
        --no-stop-vms)
            no_stop_vms=1
            ;;
        --) # found argument section
            shift
            break
            ;;
        *) # skip not used options
            ;;
    esac
    shift
done

while [[ $# != 0 ]]; do
    args[${#args[*]}]=$1
    shift
done


checkdirs "$GIT_TAXI_BACKEND_PATH" \
          "$GIT_TAXI_BILLING_DOCKER_PATH" \
          "$GIT_TAXI_TEST_PATH"

export GIT_TAXI_BACKEND_PATH
export GIT_TAXI_BILLING_DOCKER_PATH
export GIT_TAXI_TEST_PATH
export GIT_TAXI_BILLING_TESTING_PATH
export OUTPUT_PATH

if [[ $do_cleanup -eq 1 ]]; then
  reset_dirs
  exit 0
fi

setdefaults
generate_test_dirs

[[ $verbose -eq 1 ]] && dump_config

if [[ ${#dirs_to_test[*]} -gt 0 ]]; then
    tears_up
    execute_tests
    tears_down
else
    (>&2 echo "No tests for execution")
fi

if [[ $FAILED -eq 0 ]]; then
  echo "test passed"
  exit 0
else
  echo "test failed"
  exit 1
fi
