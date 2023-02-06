logstash-5x:
  repos:
    logstash-6x: 'deb https://artifacts.elastic.co/packages/6.x/apt stable main'
  packages:
    yandex-jdk8: any
    logstash: 1:6.8.15-1
    yandex-taxi-logstash-config-mongo: latest
    yandex-taxi-logstash-graphite: latest
  jvm_opts:
    heap_size_initial: 256m
    heap_size_maximum: 1g
  settings:
    pipeline_workers: 2
    pipeline_output_workers: 2
    pipeline_batch_size: 1024
    old_logs_count: 5
