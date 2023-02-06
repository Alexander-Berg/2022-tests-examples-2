mongodb3:
  storage:
    engine: wiredTiger
    wiredTiger:
      engineConfig:
        cacheSizeGB: 5
  replication:
    replSetName: taxi_test_companion
  net:
    compression:
      compressors: snappy
    bindIp: ::,0.0.0.0
