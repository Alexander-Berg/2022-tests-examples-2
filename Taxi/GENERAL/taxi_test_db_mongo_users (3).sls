mongos-taxi-users:
    config_path: /etc/mongos/mongos-taxi-users.conf
    net:
        bindIp: ::1,127.0.0.1
        port: 3027
    security:
        keyFile: /etc/mongos/key-users
    sharding:
        configDB: taxi_test_users_config/users-mrs-shard0-man-01.taxi.tst.yandex.net,users-mrs-shard0-sas-01.taxi.tst.yandex.net,users-mrs-shard0-vla-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-users.log
{% if 'taxi_test_user_api' in salt['grains.get']('conductor:groups') %}
    setParameter:
        ShardingTaskExecutorPoolMaxSize: 12
        connPoolMaxShardedConnsPerHost: 96
        taskExecutorPoolSize: 12
        ShardingTaskExecutorPoolMaxConnecting: 12
{% endif %}

yav:
    templates:
        /etc/mongos/key-users:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01dkyaaqxws1thx9jfdnad0ttt->MONGO'
            template: 'mongo-secret-key.tpl'
