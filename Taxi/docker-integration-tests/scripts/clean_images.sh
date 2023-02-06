#!/bin/sh

rm_all_images() {
    # Discovers and removes all the docker images
    # specified with the string in $1
    images=`docker image ls | grep -F $1 | awk '{print $3}'`
    echo "Clearing images $1:"
    echo "$images"
    if [ -n "$images" ]; then
        docker rmi -f $images
    fi
}

echo "Clearing images"
# docker image prune
rm_all_images registry.yandex.net/taxi/
rm_all_images registry.yandex.net/eda/
