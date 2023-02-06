mongos-taxi-stq-order1:
    config_path: /etc/mongos/mongos-taxi-stq-order1.conf
    net:
        bindIp: ::1,127.0.0.1
        port: 3039
    security:
        keyFile: /etc/mongos/key-stq-order1
    sharding:
        configDB: taxi_test_stq_order1_config/stq-order1-mrs-sas-01.taxi.tst.yandex.net,stq-order1-mrs-vla-01.taxi.tst.yandex.net,stq-order1-mrs-iva-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-stq-order1.log

yav:
    templates:
        /etc/mongos/key-stq-order1:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01d4tjtvxn564rgwbhhspbvjry->MONGO'
            template: 'mongo-secret-key.tpl'
