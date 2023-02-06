#!/usr/bin/env bash
set -e

MONGOS_PORT=27017
MONGO_CONFIG_PORT=27018
MONGO_SHARD0_PORT=27019

MONGO_LOG_DIR="/taxi/logs"
MONGOS_LOG_FILE="$MONGO_LOG_DIR/taxi-mongos.log"
MONGO_CONFIG_LOG_FILE="$MONGO_LOG_DIR/taxi-mongo-config.log"
MONGO_SHARD0_LOG_FILE="$MONGO_LOG_DIR/taxi-mongo-shard0.log"

MONGO_FLAGS="--ipv6 --fork"

if [ -n "$MONGO_RAMDISK" ]
then
    MONGOS_DIR="/mnt/ram/taxi-mongos"
    MONGO_CONFIG_DIR="/mnt/ram/taxi-mongo-cfg"
    MONGO_SHARD0_DIR="/mnt/ram/taxi-mongo-shrd0"
    MONGO_CONFIG_FLAGS="$MONGO_FLAGS --smallfiles --noprealloc"
    MONGO_SHARD0_FLAGS="$MONGO_FLAGS --smallfiles --noprealloc --nojournal"
else
    MONGOS_DIR="/data/db/taxi-mongos"
    MONGO_CONFIG_DIR="/data/db/taxi-mongo-cfg"
    MONGO_SHARD0_DIR="/data/db/taxi-mongo-shrd0"
    MONGO_CONFIG_FLAGS="$MONGO_FLAGS"
    MONGO_SHARD0_FLAGS="$MONGO_FLAGS"
fi

# Create db directories
mkdir -p $MONGOS_DIR
mkdir -p $MONGO_CONFIG_DIR
mkdir -p $MONGO_SHARD0_DIR

# Start config server
mongod --configsvr --replSet crs0 --port $MONGO_CONFIG_PORT --dbpath $MONGO_CONFIG_DIR \
    --logpath $MONGO_CONFIG_LOG_FILE $MONGO_CONFIG_FLAGS

# Init replica set
mongo --port $MONGO_CONFIG_PORT --eval \
    'rs.initiate({_id: "crs0", configsvr: true, members: [{_id: 0, host: "localhost:'$MONGO_CONFIG_PORT'"}]})'

# Start mongo shard0
mongod --shardsvr --port $MONGO_SHARD0_PORT --dbpath $MONGO_SHARD0_DIR \
    --logpath $MONGO_SHARD0_LOG_FILE $MONGO_SHARD0_FLAGS

# Start mongos
mongos --configdb crs0/localhost:$MONGO_CONFIG_PORT --port $MONGOS_PORT \
    --bind_ip_all --logpath $MONGOS_LOG_FILE $MONGO_FLAGS

# Add shard0 to mongos
mongo --port $MONGOS_PORT --eval 'sh.addShard("localhost:'$MONGO_SHARD0_PORT'")'

# Keep container running
sleep infinity
