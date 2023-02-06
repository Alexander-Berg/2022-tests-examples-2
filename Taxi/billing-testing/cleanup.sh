#! /bin/bash
$(dirname $(readlink -f $0))/run.sh --clean
make -C ../billing-docker clean-images
