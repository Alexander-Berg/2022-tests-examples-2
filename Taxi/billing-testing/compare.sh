#!/usr/bin/env bash
#
# examples:
# ./compare.sh

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
: ${backend_dir:=$base/../backend-py3}
: ${uservices_dir:=$base/../uservices}
: ${docker_dir:=$base/billing-docker}
: ${data_dir:=$base/billing-test-data}
: ${output_dir:=$base/output}

SHORT_OPTS="h"
LONG_OPTS="billing-py3:,date:,uservices:"
CONFIG_LONG_OPTS="help,skip-docker-pull,skip-syncing,skip-sampling,skip-bootstrap"
CWD=$(dirname $(realpath $0))
source "${CWD}/_shared.sh"
source "$CWD/_timer.sh"
timer_start main
skip_docker_pull=0
skip_syncing=0
skip_sampling=0
skip_bootstrap=0
test_name="billing-common-test"
date="last"

function usage() {
  echo -e "Usage:\n"
  echo "$(basename ${0}) [--skip-docker-pull]"
  echo -e "\t[--skip-syncing]"
  echo -e "\t[--skip-sampling]"
  echo -e "\t[--skip-bootstrap]"
  echo -e "\t[--date=yyyy-mm-dd]"
  echo -e "\t[--billing-py3=billing-py3-path]"
  echo
  printf "\t%-40s%s\n" \
    "--skip-docker-pull" "Do not pull docker images" \
    "--skip-syncing" "Do not run sync_prod" \
    "--skip-sampling" "Do not run sample_data" \
    "--skip-bootstrap" "Do not run bootstrap" \
    "--date=yyyy-mm-dd|last" "Specify date for sampling, default: last"\
    "--billing-py3=path" "Specify path to billing-py3"\
    "--uservices=path" "Specify path to uservices (for syncing only)"
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
    --skip-docker-pull)
      skip_docker_pull=1
      ;;
    --skip-syncing)
      skip_syncing=1
      ;;
    --skip-sampling)
      skip_sampling=1
      ;;
    --skip-bootstrap)
      skip_bootstrap=1
      ;;
    --help | -h)
      usage
      exit 0
      ;;
    --date)
      shift
      date="$1"
      echo "got date $date"
      ;;
    --billing-py3)
      shift
      backend_dir="$1"
      echo "got backend_path $backend_dir"
      ;;
    --uservices)
      shift
      uservices_dir="$1"
      echo "got uservices_path $uservices_dir"
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

echo "TEST: $test_name"
echo "DATE: $date"
echo "skip_syncing: $skip_syncing"
echo "skip_sampling: $skip_sampling"
echo "skip_docker_pull: $skip_docker_pull"
echo "skip_bootstrap: $skip_bootstrap"
echo "backend_dir: $backend_dir"
echo "uservices_dir: $uservices_dir"
echo "output_dir: $output_dir"
echo "docker_dir: $docker_dir"
echo "data_dir: $data_dir"
echo "test_dir: $data_dir/$test_name"

# export GIT_TAXI_BACKEND_PATH
if [[ -d $backend_dir ]]; then
  echo "export GIT_TAXI_BACKEND_PATH=$backend_dir"
  export GIT_TAXI_BACKEND_PATH=$backend_dir
else
  echo "backend_dir ($backend_dir) doesn't exist"
fi

mkdir -p $output_dir
rm -rf $output_dir/* || true
cd $app_dir

echo -e "\n"
timer_start syncing
if [[ $skip_syncing -eq 0 ]]; then
  echo "syncing..."
  echo "sync_prod.sh\
    --test-path $data_dir/$test_name \
    --billing-py3 $backend_dir \
    --uservices $uservices_dir"
  ${app_dir}/sync_prod.sh \
    --test-path $data_dir/$test_name \
    --billing-py3 $backend_dir \
    --uservices $uservices_dir
  if [[ $? != 0 ]]; then
    echo "syncing failed"
    exit 1
  fi
else
  echo "skip syncing"
fi
timer_finish syncing

echo -e "\n"
timer_start sampling
if [[ $skip_sampling -eq 0 ]]; then
  echo "sampling..."
  echo "sample_data.sh $data_dir/$test_name $date"
  ${app_dir}/sample_data.sh \
    $data_dir/$test_name \
    $date
  if [[ $? != 0 ]]; then
    echo "sampling failed"
    exit 1
  fi
else
  echo "skip sampling"
fi
timer_finish sampling

echo -e "\n"
timer_start docker
if [[ $skip_docker_pull -eq 0 ]]; then
  echo "pulling images..."
  echo "entering $docker_dir"
  cd $docker_dir
  docker-compose pull
  echo "entering $app_dir"
  cd $app_dir
else
  echo "skip pulling images"
fi
timer_finish docker

echo -e "\n"
timer_start bootstrap
if [[ $skip_bootstrap -eq 0 ]]; then
  echo "bootstraping..."
  echo ${app_dir}/bootstrap.sh \
        --billing-py3="${backend_dir}" \
        --billing-docker="${docker_dir}" \
        --output="${output_dir}" \
        --source="rtc" \
        -v \
        "${data_dir}/$test_name"
  ${app_dir}/bootstrap.sh \
        --billing-py3="${backend_dir}" \
        --billing-docker="${docker_dir}" \
        --output="${output_dir}" \
        --source="rtc" \
        -v \
        "${data_dir}/$test_name"
  if [[ $? != 0 ]]; then
    echo "bootstrap failed"
    exit 1
  fi
else
  echo "skip bootstrap"
fi
timer_finish bootstrap

echo -e "\n"
echo "comparing..."
timer_start compare
echo "export SOURCE=src"
export SOURCE="src"
echo "${app_dir}/run.sh \
    --billing-py3="${backend_dir}" \
    --billing-docker="${docker_dir}" \
    --output="${output_dir}" \
    -v \
    "${data_dir}/$test_name""

${app_dir}/run.sh \
    --billing-py3="${backend_dir}" \
    --billing-docker="${docker_dir}" \
    --output="${output_dir}" \
    -v \
    "${data_dir}/$test_name"
timer_finish compare

echo -e "\n"
echo "generating report..."
timer_start report
echo "${app_dir}/genreport.sh \
  --billing-docker="${docker_dir}" \
  --billing-py3="${backend_dir}" \
  --output="${output_dir}""
"${app_dir}/genreport.sh" \
  --billing-docker="${docker_dir}" \
  --billing-py3="${backend_dir}" \
  --output="${output_dir}"
timer_finish report

echo -e "\n"
timer_finish main
echo "finished in $(timer_show main)"
echo -e "\tsyncing: $(timer_show syncing)"
echo -e "\tsampling: $(timer_show sampling)"
echo -e "\tdocker: $(timer_show docker)"
echo -e "\tbootstrap: $(timer_show bootstrap)"
echo -e "\tcompare: $(timer_show compare)"
echo -e "\treport: $(timer_show report)"
exit $?
