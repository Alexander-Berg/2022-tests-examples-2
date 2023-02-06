mongos3-original:
  processManagement:
    fork: 'false'
  net:
    bindIp: ::,0.0.0.0
    port: 27017
    ipv6: 'true'
    compression:
      compressors: snappy
  systemLog:
    destination: file
    path: "/var/log/mongodb/mongos.log"
    logAppend: 'true'
  security:
    keyFile: /etc/mongo-secret-key.conf
  sharding:
    configDB: taxi_test_stq_order0_config/stq-order0-mrs-sas-01.taxi.tst.yandex.net,stq-order0-mrs-vla-01.taxi.tst.yandex.net,stq-order0-mrs-iva-01.taxi.tst.yandex.net
  replication:
    localPingThresholdMs: 5
