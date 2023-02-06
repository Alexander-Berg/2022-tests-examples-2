mongos-taxi-subs:
    config_path: /etc/mongos/mongos-taxi-subs.conf
    net:
        bindIp: ::1,127.0.0.1
        port: 3026
    security:
        keyFile: /etc/mongos/key-subs
    sharding:
        configDB: taxi_subs_config/subs-mrs-sas-01.taxi.tst.yandex.net,subs-mrs-myt-01.taxi.tst.yandex.net,subs-mrs-vla-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-subs.log

yav:
    templates:
        /etc/mongos/key-subs:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01cs2jqc1zcsmhhz5rxxdkfwvn->MONGO'
            template: 'mongo-secret-key.tpl'
