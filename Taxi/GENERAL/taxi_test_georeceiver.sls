pushclient:
  ident: taxi
  tvm_service_name: georeceiver
  proto: pq
  files:
    - name: /var/cache/yandex/taxi-georeceiver-stats/positions
      log_type: tracker-positions-testing-log
    - name: /var/cache/yandex/taxi-georeceiver-stats/statuses
      log_type: tracker-statuses-testing-log
