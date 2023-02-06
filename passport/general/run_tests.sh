#!/usr/bin/env bash

set -eu -o pipefail


ALLURE_HOST=${ALLURE_HOST:-"127.0.0.1"}
ALLURE_PORT=${ALLURE_PORT:-"0"}
USER=${USER:-"default"}
TVMAUTH_CACHE_DIR="/tmp/passport/autotests/$USER/tvm_cache/"


function print_usage
{
    echo "usage: ./run_tests.sh [h] [-e ENV] [-na] [YA_MAKE_ARGS]"
    echo "   "
    echo "  -h | --help           : Show help"
    echo "  -e | --env            : Environment where tests will be run"
    echo "  -na | --no-allure     : Skip allure report generation"
    echo "  --no-allure-server    : Skip launching allure server"
    echo "  YA_MAKE_ARGS          : Args passed to 'ya make' (see 'ya make -h' for details)"
}


function parse_args
{
    # default arg values
    env="testing"
    no_allure="0"
    no_allure_server="0"

    positional_args=""

    # iterate all the args
    while [ $# -ne 0 ]; do
        case "$1" in
            -h | --help )                 print_usage; exit         ;;
            -e | --env )                  env="$2"; shift           ;;
            -na | --no-allure )           no_allure="1";
                                          no_allure_server="1"      ;;
            --no-allure-server )          no_allure_server="1"      ;;
            * )                           positional_args+=" $1"    ;; # if no match, add it to the positional args
        esac
        shift # move to next arg
    done
}


function get_secrets
{
    # determine environment-specific settings
    if [[ "${env}" == "testing" || "${env}" == "development" ]]; then
        SECRET_ID="sec-01ewabcg6j4jyd129mt11t4r5d"
    elif [[ "${env}" == "production" || "${env}" == "rc" ]]; then
        SECRET_ID="sec-01ewaz478n30zjpnknv6dsay4f"
    elif [[ "${env}" == "intranet_testing" ]]; then
        SECRET_ID="sec-01ewaz5zsas0jbc2p5djtrc2sz"
    elif [[ "${env}" == "intranet_production" || "${env}" == "intranet_rc" ]]; then
        SECRET_ID="sec-01ewaz85aye7za71za8h9zyfdr"
    else
        echo "Unknown env: ${env}"
        exit 1
    fi
    ENV="${env}"
    export ENV

    # set env vars with secrets' values
    echo "Trying to read https://yav.yandex-team.ru/secret/${SECRET_ID} ..."
    EXPORTS="$(ya vault get version ${SECRET_ID} --only-value | `dirname $0`/_export_secrets_to_env.py)"
    eval "${EXPORTS}"
}


function run
{
    parse_args "$@"

    get_secrets

    # make dir for tvm cache
    mkdir -p "${TVMAUTH_CACHE_DIR}"

    # make dir for allure report
    DIRNAME="/tmp/passport/autotests/allure/$USER"
    mkdir -p ${DIRNAME}

    YA_MAKE_ARGS="-tA -k"
    if [[ "${no_allure}" -eq "1" ]]; then
        echo "Skipping allure report generation"
    else
        YA_MAKE_ARGS+=" --allure=${DIRNAME}"
    fi
    YA_MAKE_ARGS+=" ${positional_args}"

    # run tests
    ya make ${YA_MAKE_ARGS} || true

    # remove received TVM tickets
    rm -r "${TVMAUTH_CACHE_DIR}"

    if [[ "${no_allure_server}" -ne "1" ]]; then
        # open allure report in browser
        allure open -h ${ALLURE_HOST} -p ${ALLURE_PORT} ${DIRNAME}
    fi
}

run "$@"
