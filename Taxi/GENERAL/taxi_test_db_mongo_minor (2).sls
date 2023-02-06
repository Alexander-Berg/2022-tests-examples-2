mongodbcfg3:
  storage:
    engine: wiredTiger
    wiredTiger:
      engineConfig:
        cacheSizeGB: 1
  replication:
    replSetName: taxi_minor
  net:
    bindIp: ::,0.0.0.0
