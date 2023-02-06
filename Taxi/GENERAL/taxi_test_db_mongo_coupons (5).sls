mongos-taxi-coupons:
    config_path: /etc/mongos/mongos-taxi-coupons.conf
    net:
        bindIp: ::1,127.0.0.1
        port: 3048
    security:
        keyFile: /etc/mongos/key-coupons
    sharding:
        configDB: taxi_test_coupons_config/coupons-mrs-iva-01.taxi.tst.yandex.net,coupons-mrs-vla-01.taxi.tst.yandex.net,coupons-mrs-sas-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-coupons.log

yav:
    templates:
        /etc/mongos/key-coupons:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01d1v145vd63996jystbr39j3r->MONGO'
            template: 'mongo-secret-key.tpl'
