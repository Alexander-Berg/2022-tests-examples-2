mongodbcfg3:
  storage:
    engine: wiredTiger
    wiredTiger:
      engineConfig:
        cacheSizeGB: 1
  replication:
    replSetName: taxi_test_billing_buffer_proxy_config
  net:
    bindIp: ::,0.0.0.0
