mongos-taxi-dbarchive3:
    config_path: /etc/mongos/mongos-taxi-dbarchive3.conf
    net:
        bindIp: ::,127.0.0.1
        port: 3046
    security:
        keyFile: /etc/mongos/key-dbarchive3
    sharding:
        configDB: taxi_test_dbarchive_config_shard3/dbarchive-mrs-shard3-sas-01.taxi.tst.yandex.net,dbarchive-mrs-shard3-vla-01.taxi.tst.yandex.net,dbarchive-mrs-shard3-myt-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-dbarchive3.log
    setParameter:
        ShardingTaskExecutorPoolMaxConnecting: 8
        ShardingTaskExecutorPoolMaxSize: 8
        taskExecutorPoolSize: 8
        connPoolMaxShardedConnsPerHost: 64
        diagnosticDataCollectionEnabled: 'false'


yav:
    templates:
        /etc/mongos/key-dbarchive3:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01e0r0p85v5f4kqqxhs62ra8hh->MONGO'
            template: 'mongo-secret-key.tpl'
