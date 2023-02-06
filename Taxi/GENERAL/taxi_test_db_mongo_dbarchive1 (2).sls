mongodbcfg3:
  storage:
    engine: wiredTiger
    wiredTiger:
      engineConfig:
        cacheSizeGB: 1
  replication:
    replSetName: taxi_test_dbarhive_config_shard1
  net:
    bindIp: ::,0.0.0.0
