mongos-taxi-stq-order0:
    config_path: /etc/mongos/mongos-taxi-stq-order0.conf
    net:
        bindIp: ::,127.0.0.1
        port: 3038
    security:
        keyFile: /etc/mongos/key-stq-order0
    sharding:
        configDB: taxi_test_stq_order0_config/stq-order0-mrs-sas-01.taxi.tst.yandex.net,stq-order0-mrs-vla-01.taxi.tst.yandex.net,stq-order0-mrs-iva-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-stq-order0.log
    setParameter:
        ShardingTaskExecutorPoolMaxConnecting: 8
        ShardingTaskExecutorPoolMaxSize: 8
        taskExecutorPoolSize: 8
        connPoolMaxShardedConnsPerHost: 64
        diagnosticDataCollectionEnabled: 'false'


yav:
    templates:
        /etc/mongos/key-stq-order0:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01d4tjqad2xpyt8nqs8z7zt56n->MONGO'
            template: 'mongo-secret-key.tpl'
