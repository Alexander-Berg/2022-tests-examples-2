sentinel monitor test_master${index} 127.0.0.1 ${port} 2
sentinel down-after-milliseconds test_master${index} ${down_after_milliseconds}
sentinel failover-timeout test_master${index} ${failover_timeout}
sentinel parallel-syncs test_master${index} ${parallel_syncs}