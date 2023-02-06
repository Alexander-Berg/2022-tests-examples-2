#!/usr/bin/env bash
#
# examples:
# ./sync_prod.sh

if [ "$(uname)" == "Darwin" ]; then
  app_dir=$(dirname $(stat -f $0))
else
  app_dir=$(dirname $(readlink -f $0))
fi

if [[ $(basename $app_dir) = "billing-testing" ]]; then
  base=$(dirname $app_dir)
else
  base="$app_dir"
  app_dir="$base/billing-testing"
fi
backend_dir=$GIT_TAXI_BACKEND_PATH
: ${backend_dir:=$base/backend-py3}
uservices_dir=$base/uservices
test_dir=$base/billing-test-data/billing-common-test

SHORT_OPTS="h"
LONG_OPTS="test-path:,billing-py3:,uservices:"
CONFIG_LONG_OPTS="help"
CWD=$(dirname $(realpath $0))
source "${CWD}/_shared.sh"
source "$CWD/_timer.sh"
timer_start main

function usage() {
  echo -e "Usage:\n"
  echo "$(basename ${0})"
  echo -e "\t[--test-path=test-path]"
  echo -e "\t[--billing-py3=billing-py3-path]"
  echo -e "\t[--uservices=uservices-path]"
  echo
  printf "\t%-40s%s\n" \
    "--test-path=path" "Specify path to test. Default ../billing-test-data/billing-common-test"\
    "--billing-py3=path" "Specify path to billing-py3. Default ../backend-py3"\
    "--uservices=path" "Specify path to uservices. Default ../uservices"
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
    --help | -h)
      usage
      exit 0
      ;;
    --test-path)
      shift
      test_dir="$1"
      ;;
    --billing-py3)
      shift
      backend_dir="$1"
      ;;
    --uservices)
      shift
      uservices_dir="$1"
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

echo "backend_dir: $backend_dir"
echo "uservices_dir: $uservices_dir"
echo "test_dir: $test_dir"

if [[ ! -d "${test_dir}" ]]; then
  echo "test_dir doesn't exist: test_dir"
  exit 1
fi
if [[ ! -d "${backend_dir}" ]]; then
  echo "backend_dir doesn't exist: $backend_dir"
  exit 1
fi
if [[ ! -d "${uservices_dir}" ]]; then
  echo "uservices_dir doesn't exist: $backend_dir"
  exit 1
fi

# check_token
devtools_token_path="$HOME/.taxi-devtools"
if [[ -f $devtools_token_path ]]; then
  echo "devtools token ok"
else
  pushd `pwd`
  cd $HOME
  echo "get token here https://oauth.yandex-team.ru/authorize?response_type=token&client_id=ed682c8c3e9c489cb0734062fc675a3d"
  echo "or visit https://wiki.yandex-team.ru/taxi/backend/Adminka-bez-koda/#oauth"
  echo "token: "
  read token
  echo -e "[default]\ntariff-editor-token = $token" > $devtools_token_path
  echo "tariff-editor-token saved: $devtools_token_path"
  popd
fi

export PYTHONPATH=$backend_dir
echo "/usr/lib/yandex/taxi-py3-2/bin/python ./sync_prod/sync_prod.py $test_dir $backend_dir $uservices_dir"
/usr/lib/yandex/taxi-py3-2/bin/python ./sync_prod/sync_prod.py  $test_dir $backend_dir $uservices_dir

timer_finish main
echo "finished in $(timer_show main)"
exit $?
