#! /bin/bash
# every script must be started with next preamble:
#
# if [[ "$(uname)" == "Darwin" ]]; then
#     realpath() {
#         [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
#     }
#     export realpath
# fi
# CWD=$(dirname $(realpath $0))
# SHORT_OPTS="..."
# LONG_OPTS="..."
# CONFIG_LONG_OPTS="..."
# source "${CWD}/_shared.sh"
#
[ $"$(basename $"$0")" == "_shared.sh" ] &&
  fatal 'This is a library. Do not run it directly.'

export BASE_IMAGE="registry.yandex.net/taxi/taxi-integration-xenial-base:latest"

fatal() {
  echo "$*" 1>&2
  echo "Execution aborted." 1>&2
  exit 1
}

error() {
  echo "$*" 1>&2
}

checkdirs() {
  local ok=0
  for dirname in $*; do
    [ -d "$dirname" ] || fatal "directory does not exists: '$dirname'"
  done
}

reset_dir() {
  local path="$(realpath ${1})"
  local ids="$(id -u):$(id -g)"
  echo "reset directory ownership to $ids for $path ..."
  if [[ $dry_run == 1 ]]; then
    return 0
  fi
  docker run --rm \
    -v $path:/dir_to_reset:rw \
    $BASE_IMAGE bash -c "chown -R $ids /dir_to_reset"
}

get_options() {
  # SHORT_OPTS, LONG_OPTS and CONFIG_LONG_OPTS must be defined before calling
  local OS
  [ -z "$SHORT_OPTS" ] && fatal "SHORT_OPTS undefined"
  [ -z "$LONG_OPTS" ] && fatal "LONG_OPTS undefined"
  [ -z "$CONFIG_LONG_OPTS" ] && fatal "CONFIG_LONG_OPTS undefined"
  OS="$(uname)"
  if [[ "$OS" == "Darwin" ]]; then
    brew="$(command -v brew)" || fatal "brew missing"
    [ -d "$($"$brew" --prefix gnu-getopt)/bin" ] || fatal "gnu-getopt missing"
    getopt="$($"$brew" --prefix gnu-getopt)/bin/getopt"
  else
    getopt="$(command -v getopt)" || fatal "getopt missing"
  fi
  "${getopt}" \
    -o "$SHORT_OPTS" \
    --long "$LONG_OPTS" \
    --long "$CONFIG_LONG_OPTS" \
    -- "$@"
}

base=$"$(realpath $"${CWD}/..")"
: ${GIT_TAXI_BILLING_TESTING_PATH:="$CWD"}
: ${GIT_TAXI_BACKEND_PATH:="$base/backend-py3"}
: ${GIT_TAXI_BILLING_DOCKER_PATH:="$base/billing-docker"}
: ${GIT_TAXI_TEST_PATH:="$base/billing-test-data"}
: ${OUTPUT_PATH:="$base/output"}
