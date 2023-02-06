#!/bin/sh

rm_all_containers() {
    # Discovers, stops and removes all the docker containers
    # specified with the string in $1
    containers=`docker ps -a | grep -F $1 | awk '{print $1}'`
    echo "Clearing containers $1:"
    echo "$containers"
    if [ -n "$containers" ]; then
        docker container stop $containers
        docker container rm -v $containers
    fi
}

clean_persistent_mongodb() {
    if [ -z "$PERSISTENT_MONGO" ]; then
      if arc root > /dev/null; then
        arc clean -xdq volumes/mongo/
      else
        git clean -fdxq volumes/mongo/
      fi
    fi
}

clean_persistent_cache() {
    echo "Clearing generated cache"
    if arc root > /dev/null; then
      arc clean -xdq volumes/cache_dumps/
    else
      git clean -fdxq volumes/cache_dumps/
    fi
}
echo "Clearing containers"

rm_all_containers "taxi-memcached"
rm_all_containers "taxi-mongo"
clean_persistent_mongodb
rm_all_containers "taxi-redis"
rm_all_containers "taxi-redis-sentinel"
clean_persistent_cache
