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
    configDB: taxi_test_dbarchive_config_shard3/dbarchive-mrs-shard3-sas-01.taxi.tst.yandex.net,dbarchive-mrs-shard3-vla-01.taxi.tst.yandex.net,dbarchive-mrs-shard3-myt-01.taxi.tst.yandex.net
  replication:
    localPingThresholdMs: 5
