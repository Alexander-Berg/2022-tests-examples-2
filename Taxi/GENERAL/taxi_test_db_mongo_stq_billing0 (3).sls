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
    configDB: taxi_test_stq_billing0_config/stq-billing0-mrs-sas-01.taxi.tst.yandex.net,stq-billing0-mrs-iva-01.taxi.tst.yandex.net,stq-billing0-mrs-man-01.taxi.tst.yandex.net
  replication:
    localPingThresholdMs: 5
