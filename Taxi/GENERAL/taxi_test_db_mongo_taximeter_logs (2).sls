mongodbcfg3:
  storage:
    engine: wiredTiger
    wiredTiger:
      engineConfig:
        cacheSizeGB: 1
  replication:
    replSetName: taxi_test_config_taximeter
  net:
    bindIp: ::,0.0.0.0
