mongos-taxi-stq-order2:
    config_path: /etc/mongos/mongos-taxi-stq-order2.conf
    net:
        bindIp: ::,127.0.0.1
        port: 3045
    security:
        keyFile: /etc/mongos/key-stq-order2
    sharding:
        configDB: taxi_test_stq_order2_config/stq-order2-mrs-sas-01.taxi.tst.yandex.net,stq-order2-mrs-vla-01.taxi.tst.yandex.net,stq-order2-mrs-myt-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-stq-order2.log
    setParameter:
        ShardingTaskExecutorPoolMaxConnecting: 8
        ShardingTaskExecutorPoolMaxSize: 8
        taskExecutorPoolSize: 8
        connPoolMaxShardedConnsPerHost: 64
        diagnosticDataCollectionEnabled: 'false'


yav:
    templates:
        /etc/mongos/key-stq-order2:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01dzkwc6fp4mfxwxyajfmw738j->MONGO'
            template: 'mongo-secret-key.tpl'
