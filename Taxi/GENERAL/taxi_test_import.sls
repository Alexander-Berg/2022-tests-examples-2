logstash-5x:
  repos:
    logstash-5x: 'deb https://artifacts.elastic.co/packages/5.x/apt stable main'
  packages:
    yandex-jdk8: any
    logstash: 1:5.6.3-1
    yandex-taxi-logstash-config-logs: any
    yandex-taxi-logstash-graphite: any
    yandex-taxi-logstash-monrun: any
  jvm_opts:
    heap_size_initial: 256m
    heap_size_maximum: 2g
  settings:
    pipeline_workers: 4
    pipeline_output_workers: 4
    pipeline_batch_size: 4096
    old_logs_count: 1
  startup_opts:
    custom_settings:
    - "ES_CUSTOM_IDX_01=yandex-taxi-import"
    - "ES_CUSTOM_IDX_TAXI_NAME=yandex-taxi-import"
    - "ES_CUSTOM_IDX_TAXI_TIME=+YYYY.MM.dd"
