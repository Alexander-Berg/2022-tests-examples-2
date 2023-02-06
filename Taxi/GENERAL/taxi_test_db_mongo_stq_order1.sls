mongodb3:
  storage:
    engine: wiredTiger
    wiredTiger:
      engineConfig:
        cacheSizeGB: 2
  replication:
    replSetName: taxi_test_stq_order1
  net:
    compression:
      compressors: snappy
    bindIp: ::,0.0.0.0
