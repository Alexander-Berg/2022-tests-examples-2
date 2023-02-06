mongos-taxi-phone:
    config_path: /etc/mongos/mongos-taxi-phone.conf
    net:
        bindIp: ::,127.0.0.1
        port: 3030
    security:
        keyFile: /etc/mongos/key-phone
    sharding:
        configDB: taxi_test_phone_config/phone-mrs-sas-01.taxi.tst.yandex.net,phone-mrs-vla-01.taxi.tst.yandex.net,phone-mrs-myt-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-phone.log
    setParameter:
        ShardingTaskExecutorPoolMaxConnecting: 8
        ShardingTaskExecutorPoolMaxSize: 8
        taskExecutorPoolSize: 8
        connPoolMaxShardedConnsPerHost: 64
        diagnosticDataCollectionEnabled: 'false'


yav:
    templates:
        /etc/mongos/key-phone:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01cs2j3gdwsef5qgy7h20v27bm->MONGO'
            template: 'mongo-secret-key.tpl'
