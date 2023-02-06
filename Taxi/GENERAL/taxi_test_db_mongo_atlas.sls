mongos-taxi-atlas:
    config_path: /etc/mongos/mongos-taxi-atlas.conf
    net:
        bindIp: ::,127.0.0.1
        port: 3047
    security:
        keyFile: /etc/mongos/key-main
    sharding:
        configDB: taxi_mrs_config/taxi-mrs-vla-01.taxi.tst.yandex.net,taxi-mrs-myt-01.taxi.tst.yandex.net,taxi-mrs-sas-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-atlas.log
    setParameter:
        ShardingTaskExecutorPoolMaxConnecting: 8
        ShardingTaskExecutorPoolMaxSize: 8
        taskExecutorPoolSize: 8
        connPoolMaxShardedConnsPerHost: 64
        diagnosticDataCollectionEnabled: 'false'


yav:
    templates:
        /etc/mongos/key-main:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01cs2jefs30p13yvh6rmkxz2vp->MONGO'
            template: 'mongo-secret-key.tpl'
