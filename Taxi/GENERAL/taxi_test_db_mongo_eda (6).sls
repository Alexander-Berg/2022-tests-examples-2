mongos-taxi-eda:
    config_path: /etc/mongos/mongos-taxi-eda.conf
    net:
        bindIp: ::,127.0.0.1
        port: 3043
    security:
        keyFile: /etc/mongos/key-eda
    sharding:
        configDB: taxi_test_eda_config/eda-mrs-iva-01.taxi.tst.yandex.net,eda-mrs-vla-01.taxi.tst.yandex.net,eda-mrs-sas-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-eda.log
    setParameter:
        ShardingTaskExecutorPoolMaxConnecting: 8
        ShardingTaskExecutorPoolMaxSize: 8
        taskExecutorPoolSize: 8
        connPoolMaxShardedConnsPerHost: 64
        diagnosticDataCollectionEnabled: 'false'


yav:
    templates:
        /etc/mongos/key-eda:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01dbfwwbvt8geb5y3gfghngpw6->MONGO'
            template: 'mongo-secret-key.tpl'
