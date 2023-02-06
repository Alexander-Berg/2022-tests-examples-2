mongos-taxi-histat:
    config_path: /etc/mongos/mongos-taxi-histat.conf
    net:
        bindIp: ::,127.0.0.1
        port: 3029
    security:
        keyFile: /etc/mongos/key-histat
    sharding:
        configDB: taxi_test_histat_config/histat-mrs-shard1-vla-01.taxi.tst.yandex.net,histat-mrs-shard1-iva-01.taxi.tst.yandex.net,histat-mrs-shard1-sas-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-histat.log
    setParameter:
        ShardingTaskExecutorPoolMaxConnecting: 8
        ShardingTaskExecutorPoolMaxSize: 8
        taskExecutorPoolSize: 8
        connPoolMaxShardedConnsPerHost: 64
        diagnosticDataCollectionEnabled: 'false'


yav:
    templates:
        /etc/mongos/key-histat:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01cs2h2v3xavny1h9vxfmjxm3d->MONGO'
            template: 'mongo-secret-key.tpl'
