mongos-taxi-minor:
    config_path: /etc/mongos/mongos-taxi-minor.conf
    net:
        bindIp: ::1,127.0.0.1
        port: 3018
    security:
        keyFile: /etc/mongos/key-minor
    sharding:
        configDB: taxi_minor/minor-mrs-sas-01.taxi.tst.yandex.net,minor-mrs-iva-01.taxi.tst.yandex.net,minor-mrs-vla-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-minor.log

yav:
    templates:
        /etc/mongos/key-minor:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01cs2hj0s6w0bv7f9ctdc0bwbz->MONGO'
            template: 'mongo-secret-key.tpl'
