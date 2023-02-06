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
    configDB: taxi_dbarhive/taxi-dbarchive-mrs01h.tst.mobile.yandex.net,taxi-dbarchive-mrs02h.tst.mobile.yandex.net,taxi-dbarchive-mrs03h.tst.mobile.yandex.net
  systemLog:
    destination: file
    logAppend: 'true'
    path: /var/log/mongodb/mongos.log
