mongodb3:
  storage:
    engine: wiredTiger
    directoryPerDB: 'true'
    wiredTiger:
      engineConfig:
        journalCompressor: none
        cacheSizeGB: 5
      collectionConfig:
        blockCompressor: none
  replication:
    replSetName: taxi_test_tracker
  net:
    compression:
      compressors: snappy
    bindIp: ::,0.0.0.0
