mongos-taxi-stq-billing0:
    config_path: /etc/mongos/mongos-taxi-stq-billing0.conf
    net:
        bindIp: ::,127.0.0.1
        port: 3040
    security:
        keyFile: /etc/mongos/key-stq-billing0
    sharding:
        configDB: taxi_test_stq_billing0_config/stq-billing0-mrs-sas-01.taxi.tst.yandex.net,stq-billing0-mrs-iva-01.taxi.tst.yandex.net,stq-billing0-mrs-man-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-stq-billing0.log
    setParameter:
        ShardingTaskExecutorPoolMaxConnecting: 8
        ShardingTaskExecutorPoolMaxSize: 8
        taskExecutorPoolSize: 8
        connPoolMaxShardedConnsPerHost: 64
        diagnosticDataCollectionEnabled: 'false'


yav:
  templates:
    /etc/mongos/key-stq-billing0:
      template: 'mongo-secret-key.tpl'
      owner: 'mongodb:root'
      mode: '0600'
      secrets: 'sec-01d7fbjeqf745tz17k8eqdjaza->MONGO'
