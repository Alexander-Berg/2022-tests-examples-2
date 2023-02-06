mongodb3:
  storage:
    engine: wiredTiger
    wiredTiger:
      collectionConfig:
        blockCompressor: zlib
      engineConfig:
        cacheSizeGB: 5
  replication:
    replSetName: taxi_test_dbarchive_shard1
  setParameter:
    cursorTimeoutMillis: 30000
    logLevel: 0
  net:
    compression:
      compressors: snappy
    bindIp: ::,0.0.0.0
