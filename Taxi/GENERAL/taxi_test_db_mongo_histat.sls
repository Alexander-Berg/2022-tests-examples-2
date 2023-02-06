mongodbcfg3:
  storage:
    engine: wiredTiger
    wiredTiger:
      engineConfig:
        cacheSizeGB: 2
  replication:
    replSetName: taxi_test_histat_config
  net:
    bindIp: ::,0.0.0.0
