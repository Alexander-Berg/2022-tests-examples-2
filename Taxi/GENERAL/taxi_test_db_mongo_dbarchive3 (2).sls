mongodbcfg3:
  storage:
    engine: wiredTiger
    wiredTiger:
      engineConfig:
        cacheSizeGB: 1
  replication:
    replSetName: taxi_test_dbarchive_config_shard3
  net:
    bindIp: ::,0.0.0.0
