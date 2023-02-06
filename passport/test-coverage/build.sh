#!/bin/bash

# if [ -n "$1" ]
# then
#     BRANCH_TO_BUILD=$1
# else
#     echo 'Build branch should be specified'
#     exit 1
# fi

# # Source checkout directory. Should be synchronized with /debian/rules
# SOURCEDIR=src
# REPOSITORY=https://github.yandex-team.ru/passport-frontend/passport/

# rm -rf ${SOURCEDIR}
# git clone ${REPOSITORY} ${SOURCEDIR}


# pushd ${SOURCEDIR}
# echo "In ${SOURCEDIR}"

# echo "Checking out ${BRANCH_TO_BUILD} from ${REPOSITORY}"
# git checkout ${BRANCH_TO_BUILD}

# echo "Copying changelog from `pwd`/debian/changelog to ../debian"
# cp ./debian/changelog ../debian

# echo "Checking release isn't behind master"
# bash ../tools/checkReleaseNotBehindMaster.sh

# #make node_modules
# #git clone https://github.yandex-team.ru/passport-frontend/node_modules.git modules
# #ln -s modules/node_modules .
# #ls node_modules
# popd

cp build/test-coverage/debian/* debian/

_PWD=`pwd`
_DIR=`basename ${_PWD}`
_PWD=`dirname ${_PWD}`
echo "Building"
# build-package-pbuilder ${_DIR} --upload-to passport-precise --basetgz base-nodejs.cow --with-cowbuilder --ov-source-path ${_PWD} || exit 3
build-package-pbuilder ${_DIR} --dont-upload --basetgz base-nodejs.tgz --ov-source-path ${_PWD} || exit 3
