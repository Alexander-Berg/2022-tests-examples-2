#! /bin/bash
t_start=$(date '+%s')

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
: ${docker_dir:=$base/billing-docker}
: ${data_dir:=$base/billing-test-data}
: ${output_dir:=$base/output}
: ${strict:=1}
: ${rebuild:=1}

if [[ $strict = 1 ]]; then
  add_args=""
else
  add_args="--no-restart --no-stop-vms"
fi

mkdir -p $output_dir
rm -rf $output_dir/* || true
cd $app_dir

FAILED=0
TEST_NO=0

function do_run() {
  TEST_NO=$[ $TEST_NO + 1 ]
  ${app_dir}/run.sh \
  	--billing-py3="${backend_dir}" \
        --billing-docker="${docker_dir}" \
        --output="${output_dir}" \
        ${make_args} ${add_args} -v \
        "${data_dir}/${1}"
  if [[ $? != 0 ]]; then
    FAILED=$[ $FAILED + 1 ]
    return 1
  fi
  return 0
}

if [[ ! -d "${backend_dir}/generated" ]]; then
    GIT_TAXI_BACKEND_PATH=${backend_dir} make -C $docker_dir gen-requirements
fi

while IFS='' read -r <&3 suite; do
    if [[ $suite != \#* ]] && [[ ! -z "${suite}" ]] ; then
        do_run $suite
        if [[ $? != 0 ]]; then
            echo "${suite} failed. check logs"
            break
        fi
    fi
    echo "done with ${suite}"
done 3< "${app_dir}/check_for_release.list"

"${app_dir}/genreport.sh" \
  --billing-docker="${docker_dir}" \
  --billing-py3="${backend_dir}" \
  --output="${output_dir}"

t_finish=$(date '+%s')

echo "seconds spent: $[ $t_finish - $t_start ]"
echo "tests total  : $TEST_NO"
echo "tests failed : $FAILED"
if [[ $FAILED -eq 0 ]]; then
  exit 0
else
  exit 1
fi
