mongodb3:
  storage:
    engine: wiredTiger
  replication:
    replSetName: taxi_test_pda
  net:
    compression:
      compressors: snappy
    bindIp: ::,0.0.0.0
