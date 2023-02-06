pilorama:
  packages:
    yandex-taxi-pilorama: latest
    config-monrun-taxi-pilorama: latest
  config:
    file:
      discover_interval: "60s"
    filter:
      put_message: false
      defaults:
        type: log
      removals:
        - timestamp
        - metadata
        - host
        - timezone
        - coro_id
        - task_id
        - thread_id
      time_formats:
      - "%Y-%m-%d %H:%M:%S,%E*f"
      - "%Y-%m-%dT%H:%M:%S.%E*f"
      - "%Y-%m-%d %H:%M:%S.%E*f"
    output:
      elastic_version: 7
      send_timeout: "120s"
      initial_retry_delay: "500ms"
      max_in_flight_requests: 5
      index: "taximeter-logs-%Y.%m.%d.%H"
      error_index: "errors-taximeter-logs-%Y.%m.%d"
      hosts:
        - "http://elastic-logs-vla-04.taxi.tst.yandex.net:9200/_bulk"
        - "http://elastic-logs-sas-04.taxi.tst.yandex.net:9200/_bulk"
        - "http://elastic-logs-vla-05.taxi.tst.yandex.net:9200/_bulk"
        - "http://elastic-logs-sas-05.taxi.tst.yandex.net:9200/_bulk"
        - "http://elastic-logs-vla-06.taxi.tst.yandex.net:9200/_bulk"
        - "http://elastic-logs-sas-06.taxi.tst.yandex.net:9200/_bulk"
        - "http://elastic-logs-vla-07.taxi.tst.yandex.net:9200/_bulk"
        - "http://elastic-logs-sas-07.taxi.tst.yandex.net:9200/_bulk"
