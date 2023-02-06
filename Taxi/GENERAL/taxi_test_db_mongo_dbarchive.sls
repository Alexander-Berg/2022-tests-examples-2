mongos-taxi-dbarchive:
    config_path: /etc/mongos/mongos-taxi-dbarchive.conf
    net:
        bindIp: ::1,127.0.0.1
        port: 3021
    security:
        keyFile: /etc/mongos/key-dbarchive
    sharding:
        configDB: taxi_dbarhive/dbarchive-mrs-sas-01.taxi.tst.yandex.net,dbarchive-mrs-vla-01.taxi.tst.yandex.net,dbarchive-mrs-myt-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-dbarchive.log

yav:
    templates:
        /etc/mongos/key-dbarchive:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01cs2gv89fr0ptgy3byzkx0005->MONGO'
            template: 'mongo-secret-key.tpl'
