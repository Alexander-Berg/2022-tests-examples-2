mongodb3:
  storage:
    engine: wiredTiger
    wiredTiger:
      engineConfig:
        cacheSizeGB: 5
  replication:
    replSetName: taxi_mrs
  net:
    compression:
      compressors: snappy
    bindIp: ::,0.0.0.0
