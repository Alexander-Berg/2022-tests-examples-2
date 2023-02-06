mongos-taxi-tracker:
    config_path: /etc/mongos/mongos-taxi-tracker.conf
    net:
        bindIp: ::1,127.0.0.1
        port: 3020
    security:
        keyFile: /etc/mongos/key-tracker
    sharding:
        configDB: taxi_tracker_config/tracker-mrs-vla-01.taxi.tst.yandex.net,tracker-mrs-sas-01.taxi.tst.yandex.net,tracker-mrs-myt-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-tracker.log

yav:
    templates:
        /etc/mongos/key-tracker:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01cs2k108sh3mmh5a1k2f8kfks->MONGO'
            template: 'mongo-secret-key.tpl'
