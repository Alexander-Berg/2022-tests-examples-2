mongos-taxi-billing-buffer-proxy:
    config_path: /etc/mongos/mongos-taxi-billing-buffer-proxy.conf
    net:
        bindIp: ::1,127.0.0.1
        port: 3037
    security:
        keyFile: /etc/mongos/key-billing-buffer-proxy
    sharding:
        configDB: taxi_test_billing_buffer_proxy_config/billing-buffer-proxy-mrs-myt-01.taxi.tst.yandex.net,billing-buffer-proxy-mrs-sas-01.taxi.tst.yandex.net,billing-buffer-proxy-mrs-vla-01.taxi.tst.yandex.net
    systemLog:
        path: /var/log/mongodb/mongos-taxi-billing-buffer-proxy.log

yav:
    templates:
        /etc/mongos/key-billing-buffer-proxy:
            mode: '0600'
            owner: 'mongodb:root'
            secrets: 'sec-01d45pv7xa5qcpjj063tzwhxep->MONGO'
            template: 'mongo-secret-key.tpl'
