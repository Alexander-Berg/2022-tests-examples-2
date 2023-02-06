#!/usr/bin/env bash
#
# perform prepare reference dataset for test[s]
# examples:
# ./bootstrap.sh

if [[ "$(uname)" == "Darwin" ]]; then
  realpath() {
    [[ $1 == /* ]] && echo "$1" || echo "$PWD/${1#./}"
  }
  export realpath
fi
SHORT_OPTS="hnqv"
LONG_OPTS="source:,billing-docker:,billing-py3:,billing-test-data:,output:"
CONFIG_LONG_OPTS="help,no-rebuild,no-stop-vms,dry-run"
CWD=$(dirname $(realpath $0))
source "${CWD}/_shared.sh"

base=$"$(realpath $"${CWD}/..")"
: ${GIT_TAXI_BILLING_TESTING_PATH:="$CWD"}
: ${GIT_TAXI_BACKEND_PATH:="$base/backend-py3"}
: ${GIT_TAXI_BILLING_DOCKER_PATH:="$base/billing-docker"}
: ${GIT_TAXI_TEST_PATH:="$base/billing-test-data"}
: ${OUTPUT_PATH:="$base/output/bootstrap"}

no_rebuild=0
no_stop_vms=0
verbose=0
dry_run=0

dirs_to_bootstrap=()

FAILED=0

source "$CWD/_timer.sh"
timer_start main

function fatal() {
  local msg="$*"
  echo "FATAL: $msg" 1>&2
  echo "Execution terminated" 1>&2
  exit 1
}

function error() {
  local msg="$*"
  echo "ERROR: $msg" 1>&2
}

function dump_config() {
  echo "Do not rebuild vms before bootstraps: ${no_rebuild}"
  echo "Do not stop vms after bootstraps    : ${no_stop_vms}"
  echo "dirs to bootstrap: ${dirs_to_bootstrap[*]}"
}

function collect_versions() {
  echo "Collect installed packages"
  if [[ $dry_run == 1 ]]; then
    return 0
  fi
  git rev-parse HEAD $GIT_TAXI_BACKEND_PATH > $TEST_PATH/generated/versions-backend-py3.txt || true
}

function usage() {
  echo -e "Usage:\n"
  echo "$(basename ${0}) [-v|--verbose] [-q|--no-rebuild] [-n|--no-stop-vms]"
  echo -e "\t[--billing-py3=billing-py3-path]"
  echo -e "\t[--billing-docker=billing-docker-path]"
  echo -e "\t[--billing-test-data=billing-test-data-path]"
  echo -e "\t[--source=rtc|src]"
  echo -e "\t[--output=output-path]"
  echo -e "\tsubpath [subpath ...]"
  echo
  printf "\t%-40s%s\n" \
    "-v|--verbose" "Verbose mode" \
    "-q|--no-rebuild" "Do not rebuild (use it only for local development!)" \
    "-n|--no-stop-vms" "Do not stop vm's at end (for watching database state)" \
    "--billing-py3=path" "specify path to billing-py3" \
    "--billing-docker=path" "specify path to billing-docker" \
    "--billing-test-data=path" "specify path to billing-test-data" \
    "--ouput=path" "specify path for output artifacts" \
    "subpath" "path relative of GIT_TAXI_TEST_PATH"
  echo "By default source=src used"
}

function initialize() {
  timer_start init
  if [[ $dry_run == 1 ]]; then
    echo "Dry run initialize"
    return 0
  fi
  echo "--- start initialization with next environment settings: ---"
  echo "GIT_TAXI_BACKEND_PATH=$GIT_TAXI_BACKEND_PATH"
  echo "GIT_TAXI_BILLING_DOCKER_PATH=$GIT_TAXI_BILLING_DOCKER_PATH"
  echo "GIT_TAXI_TEST_PATH=$GIT_TAXI_TEST_PATH"
  echo "GIT_TAXI_BILLING_TESTING_PATH=$GIT_TAXI_BILLING_TESTING_PATH"
  echo "OUTPUT_PATH=$OUTPUT_PATH"
  echo "SOURCE=$SOURCE"
  echo "GENERATE=$GENERATE"
  echo "VERBOSE=$VERBOSE"

  make -C $GIT_TAXI_BILLING_DOCKER_PATH clean

  timer_finish init
  echo "initialized in $(timer_show init)."
}

function finalize() {
  timer_start fin
  if [[ $dry_run == 1 ]]; then
    echo "Dry run finalize"
    return 0
  fi
  for dir in $GIT_TAXI_BACKEND_PATH \
    $GIT_TAXI_BILLING_DOCKER_PATH \
    $GIT_TAXI_TEST_PATH \
    $GIT_TAXI_BILLING_TESTING_PATH \
    $OUTPUT_PATH; do
    reset_dir "$dir" || true
  done

  if [[ $no_stop_vms -eq 0 ]]; then
    docker-compose \
      -f $GIT_TAXI_BILLING_DOCKER_PATH/docker-compose.yml \
      -f $CWD/docker-compose.yml \
      down
    make -C $GIT_TAXI_BILLING_DOCKER_PATH clean
  fi
  timer_finish fin
  echo "finalized in $(timer_show fin)."
}

function run_sibilla() {
    if [[ $dry_run == 1 ]]; then
      echo "Dry run ${2} with ${@:3}"
      return 0
    fi
    local ARGS="${@:3}"
    local target=$2
    # build
    make -C "$GIT_TAXI_BILLING_DOCKER_PATH" $target || return 1
    # and execute tests
    docker-compose -f "$GIT_TAXI_BILLING_DOCKER_PATH/docker-compose.yml" \
        -f "$CWD/docker-compose.yml" \
        run --rm billing-testing-light /taxi/sibilla/bin/run.sh "$([[ $verbose == 1 ]] && echo '--verbose')" ${ARGS}
    return $?
}

function bootstrap_test() {
    run_sibilla $1 init-db --warmup-db
    run_sibilla $1 stq-services --warmup-stq
    run_sibilla $1 billing --bootstrap --tests
    return $?
}

function bootstrap() {
  export TEST_PATH="$(realpath ${1})"
  echo "perform bootstrap for ${TEST_PATH} ..."
  timer_start bt
  bootstrap_test $TEST_PATH
  RC="$?"
  reset_dir "$TEST_PATH/generated"
  echo "store versions of installed packages..."
  collect_versions
  timer_finish bt
  echo "bootstrap for $TEST_PATH finished in $(timer_show bt) with RC=$RC"
  return $RC
}

function get_getopt_executable() {
  local OS="$(uname)"
  if [[ $OS == "Darwin" ]]; then
    which brew >/dev/null || fatal "brew missing"
    [ -d "$(brew --prefix gnu-getopt)/bin" ] || fatal "gnu-getopt missing"
    echo "$(brew --prefix gnu-getopt)/bin/getopt"
  else
    which getopt >/dev/null || fatal "getopt missing"
    echo "getopt"
  fi
}

### main ###

# process command line options through getopt
options=$(get_options "$@") || {
  usage
  exit 1
}

# replace command line options to output from getopt
eval set -- "$options"
while true; do
  case "$1" in
  -v | --verbose)
    verbose=1
    ;;
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
  --billing-test-data)
    shift
    GIT_TAXI_TEST_PATH="$1"
    ;;
  --source)
    shift
    if [[ "$1" == 'src' ]] || [[ "${1}" == 'rtc' ]]; then
      SOURCE="$1"
    fi
    ;;
  --output)
    shift
    OUTPUT_PATH="$1"
    ;;
  -q | --no-rebuild)
    no_rebuild=1
    ;;
  -n | --no-stop-vms)
    no_stop_vms=1
    ;;
  --dry-run)
    dry_run=1
    ;;
  --) # argument section found: break option processing
    shift
    break
    ;;
  *) # unexpected option (usually unreachable)
    error "unexpected option: '$1'"
    usage
    exit 1
    ;;
  esac
  shift # throw it out
done

# pre-create output directory
if ! mkdir -p "$OUTPUT_PATH"; then
  fatal "output not created: $OUTPUT_PATH."
fi

# now all of directories wich we'll used must be exists. check them.
checkdirs "$GIT_TAXI_BACKEND_PATH" \
  "$GIT_TAXI_BILLING_DOCKER_PATH" \
  "$GIT_TAXI_TEST_PATH" \
  "$OUTPUT_PATH"

# export all collected or predefined envvars to subprocesses
export GIT_TAXI_BACKEND_PATH
export GIT_TAXI_BILLING_DOCKER_PATH
export GIT_TAXI_TEST_PATH
export GIT_TAXI_BILLING_TESTING_PATH
export OUTPUT_PATH

# instruct the sub-process to perform bootstrapping from deb-packages
: ${SOURCE:='src'}
export SOURCE
export GENERATE=1
export VERBOSE=$verbose

# the rest of options is a source for bootstrapping
for name in "$@"; do
  case "$name" in
  /*)
    # this is an absolute name. store as is
    dname="$name"
    ;;
  *)
    # looks loke a relative name. add test bas path as a prefix
    dname="$GIT_TAXI_TEST_PATH/$name"
    ;;
  esac
  [ -d "$dname" ] || fatal "does not exists or not a directory: '$dname'"
  dirs_to_bootstrap[${#dirs_to_bootstrap[*]}]="$dname"
done

[ $verbose -eq 1 ] && dump_config

# check we have some directories to bootstrap
[ ${#dirs_to_bootstrap[*]} -ne 0 ] || fatal "No tests for bootstrapping"

# make sure we have the freshest environment
initialize

# perform bootstrapping for every collected testdir
for idx in $(seq 0 $((${#dirs_to_bootstrap[*]} - 1))); do
  test_path=${dirs_to_bootstrap[$idx]}
  if ! bootstrap $test_path; then
    FAILED=$(($FAILED + 1))
  fi
done

# shut down and clean up after out activity
finalize

timer_finish main
if [[ $FAILED -eq 0 ]]; then
  echo "bootstrap finished in $(timer_show main) with no errors"
  exit 0
else
  echo "bootstrap finished in $(timer_show main) with $FAILED error[s]"
  exit 1
fi
