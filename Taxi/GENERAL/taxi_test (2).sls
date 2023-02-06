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
    output:
      elastic_version: 7
      send_timeout: "120s"
      initial_retry_delay: "500ms"
      max_in_flight_requests: 5
      index: "yandex-taxi-%Y.%m.%d.%H"
      error_index: "errors-yandex-taxi-%Y.%m.%d"
      hosts:
        - "http://elastic-logs-vla-04.taxi.tst.yandex.net:9200/_bulk"
        - "http://elastic-logs-sas-04.taxi.tst.yandex.net:9200/_bulk"
        - "http://elastic-logs-vla-05.taxi.tst.yandex.net:9200/_bulk"
        - "http://elastic-logs-sas-05.taxi.tst.yandex.net:9200/_bulk"
        - "http://elastic-logs-vla-06.taxi.tst.yandex.net:9200/_bulk"
        - "http://elastic-logs-sas-06.taxi.tst.yandex.net:9200/_bulk"
        - "http://elastic-logs-vla-07.taxi.tst.yandex.net:9200/_bulk"
        - "http://elastic-logs-sas-07.taxi.tst.yandex.net:9200/_bulk"
