mongodb3:
  storage:
    engine: wiredTiger
    directoryPerDB: 'true'
    wiredTiger:
      engineConfig:
        journalCompressor: none
        cacheSizeGB: 5
  replication:
    replSetName: taxi_test_billing_orders_shard2
  net:
    compression:
      compressors: snappy
    bindIp: ::,0.0.0.0
