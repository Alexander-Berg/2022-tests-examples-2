mongos-taxi-personal:
    config_path: /etc/mongos/mongos-taxi-personal.conf
    net:
        bindIp: ::,127.0.0.1
        port: 3032
    security:
        keyFile: /etc/mongos/key-personal
    sharding:
        configDB: taxi_test_personal_config/personal-mrs-shard1-sas-01.taxi.tst.yandex.net,personal-mrs-shard1-vla-01.taxi.tst.yandex.net,personal-mrs-shard1-myt-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-personal.log
{% if 'taxi_test_personal' in salt['grains.get']('conductor:groups') %}
    setParameter:
        ShardingTaskExecutorPoolMaxSize: 12
        connPoolMaxShardedConnsPerHost: 96
        taskExecutorPoolSize: 12
        ShardingTaskExecutorPoolMaxConnecting: 12
{% endif %}

yav:
    templates:
        /etc/mongos/key-personal:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01cs2hyb0qdes87mscaw3srkg5->MONGO'
            template: 'mongo-secret-key.tpl'
