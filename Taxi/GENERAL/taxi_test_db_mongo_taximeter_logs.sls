mongodb3:
  storage:
    engine: wiredTiger
    wiredTiger:
      engineConfig:
        journalCompressor: zlib
        cacheSizeGB: 5
      collectionConfig:
        blockCompressor: zlib
  replication:
    replSetName: taxi_test_taximeter_logs
  net:
    compression:
      compressors: snappy
    bindIp: ::,0.0.0.0
