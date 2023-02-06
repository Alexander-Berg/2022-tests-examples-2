mongos-taxi-pda:
    config_path: /etc/mongos/mongos-taxi-pda.conf
    net:
        bindIp: ::1,127.0.0.1
        port: 3024
    security:
        keyFile: /etc/mongos/key-pda
    sharding:
        configDB: taxi_pda_config/pda-mrs-sas-01.taxi.tst.yandex.net,pda-mrs-iva-01.taxi.tst.yandex.net,pda-mrs-vla-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-pda.log

yav:
    templates:
        /etc/mongos/key-pda:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01cs2hpzvjazhvstk4a0jjrtcm->MONGO'
            template: 'mongo-secret-key.tpl'
