pilorama:
  config_jaeger:
    filter:
      transform_date: false
      put_message: false
      time_formats:
        - "%Y-%m-%d %H:%M:%S,%E*f"
      additions:
        - '"flags":1'
      renames:
        trace_id: traceID
        span_id: spanID
        start_time: startTime
        start_time_millis: startTimeMillis
        operation_name: operationName
    output:
      index: "jaeger-span-write"
      jaeger_service_index: "jaeger-service-write"
      hosts:
        - "http://elastic-logs-sas-04.taxi.tst.yandex.net:9200/_bulk"
        - "http://elastic-logs-sas-05.taxi.tst.yandex.net:9200/_bulk"
        - "http://elastic-logs-vla-04.taxi.tst.yandex.net:9200/_bulk"
        - "http://elastic-logs-vla-05.taxi.tst.yandex.net:9200/_bulk"
