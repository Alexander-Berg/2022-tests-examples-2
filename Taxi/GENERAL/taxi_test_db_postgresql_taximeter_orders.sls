postgresql:
  version: 9.4
  cluster: main
  max_connections: 200
  shared_buffers: 1000MB
  additional_maps_packages: 'off'
  archive_mode: 'off'
  monrun:
    postgresql_ping:
      interval: 60
    postgresql_lag:
      interval: 60
      warn: 180
      crit: 300
    postgresql_pool:
      interval: 60
      warn: 60
      crit: 85
    postgresql_xlog_files:
      interval: 60
    postgresql_errors:
      interval: 60
