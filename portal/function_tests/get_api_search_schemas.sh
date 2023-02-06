#!/usr/bin/env bash
cwd=$(pwd)
schema_dir="$cwd/schema"
tmp_dir="$schema_dir/tmp"
tmp_dir_div="$schema_dir/tmp_div"

echo "Clean schema dir"
rm -rf ${schema_dir}

git clone https://bitbucket.browser.yandex-team.ru/scm/ml/morda-schema.git ${tmp_dir}
git clone https://bitbucket.browser.yandex-team.ru/scm/ml/div-schema.git ${tmp_dir_div}

cd ${tmp_dir}
echo "Checkout master bitbucket: morda-schema"
git checkout master
echo "Store some base schemas in ${schema_dir}"
for schema in "cleanvars" "geohelper" "config_pp" "widgetsapi" "widgetsapi_searchlib" "samsungbixby" "api/widgets/ios" "api/search/2" "vps" "ntp";
    do echo "Store schema ${schema}";
    mkdir -p ${schema_dir}/${schema} && cp -RfL ${schema} ${schema_dir}/${schema}/..;
done

cd ${tmp_dir_div}
echo "Checkout master bitbucket: div-schema"
git checkout master
echo "Store some base schemas in ${schema_dir}"
schema="div";
echo "Store schema ${schema}";
mkdir -p ${schema_dir}/${schema} && cp -RfL ${schema} ${schema_dir}/${schema}/..;

cd ${tmp_dir}
echo "Processing bitbucket: morda-schema"
git branch -a | grep 'release' --color=never | while read -r branch ; do
    echo "Checkout branch $branch"
    branch=${branch#remotes/origin/}
    regexp="\/([0-9]+)\.([0-9]+)(\.([0-9]+))?$"
    path="$schema_dir/${branch#release/}"
    if [[ ! $path =~ $regexp ]]; then echo "Skip branch $branch"; continue; fi
    dir=$path
    git checkout ${branch}
    echo "Store schema in $dir"
    mkdir -p "$dir"
    cp -RfL api ${dir}


    [[ $dir =~ \/([0-9]+)\.([0-9]+) ]]
    major_version=${BASH_REMATCH[1]}
    minor_version=${BASH_REMATCH[2]}

    # В версиях < 22.13 берем папку div/2 из morda-schema, div/1 всегда берем из morda-schema
    if [[ $dir =~ "android" && ( $major_version < 22 || ( $major_version == 22 && $minor_version < 13 ) ) ]]
    then
        if [ -d "${tmp_dir}/div" ]; then cp -RfL div ${dir}; fi
    # В версиях < 96.00 берем папку div/2 из morda-schema, div/1 всегда берем из morda-schema
    elif [[ $dir =~ "search_app_ios" && $major_version < 96 ]]
    then
        if [ -d "${tmp_dir}/div" ]; then cp -RfL div ${dir}; fi
    else
        if [ -d "${tmp_dir}/div/1" ]; then
            mkdir -p ${dir}/div/
            cp -RfL div/1 ${dir}/div/; 
        fi
    fi
done

cd ${tmp_dir_div}
echo "Processing bitbucket: div-schema"
git branch -a | grep 'release' --color=never | while read -r branch ; do
    echo "Checkout branch $branch"
    branch=${branch#remotes/origin/}
    regexp="\/([0-9]+)\.([0-9]+)(\.([0-9]+))?$"
    path="$schema_dir/${branch#release/}"
    if [[ ! $path =~ $regexp ]]; then echo "Skip branch $branch"; continue; fi
    dir=$path
    git checkout ${branch}
    echo "Store schema in $dir"
    mkdir -p "$dir"
    cp -RfL api ${dir}

    [[ $dir =~ \/([0-9]+)\.([0-9]+) ]]
    major_version=${BASH_REMATCH[1]}
    minor_version=${BASH_REMATCH[2]}

    # В версиях >= 22.13 берем папку div/2 из div-schema, div/1 всегда берем из morda-schema
    # В версиях >= 96.00 берем папку div/2 из div-schema, div/1 всегда берем из morda-schema
    if [[ ($dir =~ "android" && ( $major_version > 22 || ( $major_version == 22 && $minor_version -ge 13 ) )) ||
          ($dir =~ "search_app_ios" && $major_version -ge 96)]]
    then
        if [ -d "${tmp_dir_div}/div/2" ]; then
            mkdir -p ${dir}/div/2
            cp -RfL ${tmp_dir_div}/div/2/. ${dir}/div/2; 
        elif [ -d "${tmp_dir_div}" ]; then
            mkdir -p ${dir}/div/2
            cp -RfL ${tmp_dir_div}/. ${dir}/div/2; 
        fi
    fi
done

cd ${cwd}
rm -rf ${tmp_dir}
rm -rf ${tmp_dir_div}
