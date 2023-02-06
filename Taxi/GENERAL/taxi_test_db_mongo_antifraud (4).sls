mongos-taxi-antifraud:
    config_path: /etc/mongos/mongos-taxi-antifraud.conf
    net:
        bindIp: ::1,127.0.0.1
        port: 3044
    security:
        keyFile: /etc/mongos/key-antifraud
    sharding:
        configDB: taxi_test_antifraud_config/antifraud-mrs-sas-01.taxi.tst.yandex.net,antifraud-mrs-vla-01.taxi.tst.yandex.net,antifraud-mrs-myt-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-antifraud.log

yav:
    templates:
        /etc/mongos/key-antifraud:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01dd1vxgvh327v7yadkgmhzm7y->MONGO'
            template: 'mongo-secret-key.tpl'
