mongos-taxi-stq:
    config_path: /etc/mongos/mongos-taxi-stq.conf
    net:
        bindIp: ::1,127.0.0.1
        port: 3019
    security:
        keyFile: /etc/mongos/key-stq
    sharding:
        configDB: taxi_stq_config/stq-mrs-vla-01.taxi.tst.yandex.net,stq-mrs-sas-01.taxi.tst.yandex.net,stq-mrs-iva-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-stq.log
    setParameter:
        ShardingTaskExecutorPoolMaxConnecting: 8
        ShardingTaskExecutorPoolMaxSize: 8
        taskExecutorPoolSize: 8
        connPoolMaxShardedConnsPerHost: 64

yav:
    templates:
        /etc/mongos/key-stq:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01cs2jkw01aehhe4ht0r8j4dy0->MONGO'
            template: 'mongo-secret-key.tpl'
