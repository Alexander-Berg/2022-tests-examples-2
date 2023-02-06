mongodb3:
  storage:
    engine: wiredTiger
    directoryPerDB: 'true'
    wiredTiger:
      engineConfig:
        journalCompressor: none
        cacheSizeGB: 5
  replication:
    replSetName: taxi_test_histat_shard1
  net:
    compression:
      compressors: snappy
    bindIp: ::,0.0.0.0
