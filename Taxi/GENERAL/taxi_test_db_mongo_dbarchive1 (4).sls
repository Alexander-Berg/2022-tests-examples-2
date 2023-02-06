mongos-taxi-dbarchive1:
    config_path: /etc/mongos/mongos-taxi-dbarchive1.conf
    net:
        bindIp: ::1,127.0.0.1
        port: 3041
    security:
        keyFile: /etc/mongos/key-dbarchive1
    sharding:
        configDB: taxi_test_dbarhive_config_shard1/dbarchive-mrs-shard1-myt-01.taxi.tst.yandex.net,dbarchive-mrs-shard1-sas-01.taxi.tst.yandex.net,dbarchive-mrs-shard1-vla-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-dbarchive1.log

yav:
    templates:
        /etc/mongos/key-dbarchive1:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01d7pjwvyen8abz9h5zvtp4qj7->MONGO'
            template: 'mongo-secret-key.tpl'
