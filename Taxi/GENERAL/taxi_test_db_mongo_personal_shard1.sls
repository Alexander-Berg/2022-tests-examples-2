mongodb3:
  storage:
    engine: wiredTiger
    wiredTiger:
      engineConfig:
        cacheSizeGB: 5
  replication:
    replSetName: taxi_test_personal_shard1
  net:
    compression:
      compressors: snappy
    bindIp: ::,0.0.0.0
