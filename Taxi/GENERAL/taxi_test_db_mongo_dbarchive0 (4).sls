mongos3-original:
  net:
    bindIp: ::,0.0.0.0
    compression:
      compressors: snappy
    ipv6: 'true'
    port: 27017
  processManagement:
    fork: 'false'
  replication:
    localPingThresholdMs: 5
  security:
    keyFile: /etc/mongo-secret-key.conf
  sharding:
    configDB: taxi_dbarhive/dbarchive-mrs-sas-01.taxi.tst.yandex.net,dbarchive-mrs-vla-01.taxi.tst.yandex.net,dbarchive-mrs-myt-01.taxi.tst.yandex.net
  systemLog:
    destination: file
    logAppend: 'true'
    path: /var/log/mongodb/mongos.log
