mongos-taximeter-logs:
    config_path: /etc/mongos/mongos-taximeter-logs.conf
    net:
        bindIp: ::1,127.0.0.1
        port: 3028
    security:
        keyFile: /etc/mongos/key-taximeter-logs
    sharding:
        configDB: taxi_test_config_taximeter/taximeter-logs-mrs-sas-01.taxi.tst.yandex.net,taximeter-logs-mrs-vla-01.taxi.tst.yandex.net,taximeter-logs-mrs-iva-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taximeter-logs.log

yav:
    templates:
        /etc/mongos/key-taximeter-logs:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01cs2jxdz83sk2tsp160dtkzvh->MONGO'
            template: 'mongo-secret-key.tpl'
