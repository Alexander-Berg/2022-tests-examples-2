#!/usr/bin/env bash
if [[ "$(uname)" == "Darwin" ]]; then
  realpath() {
    [[ $1 == /* ]] && echo "$1" || echo "$PWD/${1#./}"
  }
  export realpath
fi
CWD=$(dirname $(realpath $0))
SHORT_OPTS="h"
LONG_OPTS="billing-docker:,billing-py3:,billing-test-data:,output:"
CONFIG_LONG_OPTS="help"
source "${CWD}/_shared.sh"

function usage() {
  echo -e "Usage:\n"
  echo "$(basename ${0}) [options...]"
  printf "\t%-40s%s\n" \
    "--billing-py3=path" "Custom path to billing-py3" \
    "--billing-docker=path" "Custom path to billing-docker" \
    "--ouput=path" "path for output artifacts"
}

options=$(get_options "$@") || {
  usage
  exit 1
}

eval set -- "$options"
while true; do
  case "$1" in
  --help | -h)
    usage
    exit 0
    ;;
  --billing-docker)
    shift
    GIT_TAXI_BILLING_DOCKER_PATH="$1"
    ;;
  --billing-py3)
    shift
    GIT_TAXI_BACKEND_PATH="$1"
    ;;
  --output)
    shift
    OUTPUT_PATH="$1"
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

TEST_PATH="/tmp"

export GIT_TAXI_BACKEND_PATH
export GIT_TAXI_BILLING_DOCKER_PATH
export GIT_TAXI_BILLING_TESTING_PATH
export OUTPUT_PATH
export TEST_PATH

checkdirs "$GIT_TAXI_BACKEND_PATH" \
          "$GIT_TAXI_BILLING_DOCKER_PATH" \
          "$GIT_TAXI_BILLING_TESTING_PATH" \
          "$TEST_PATH" \
          "$OUTPUT_PATH"

docker-compose -f "$GIT_TAXI_BILLING_DOCKER_PATH/docker-compose.yml" \
  -f "$CWD/docker-compose.yml" \
  run --rm billing-testing-light \
  /taxi/sibilla/bin/genreport.sh

docker run --rm \
  -v "$OUTPUT_PATH:/dir_to_reset:rw" \
  $BASE_IMAGE bash -c "chown -R $(id -u):$(id -g) /dir_to_reset"
