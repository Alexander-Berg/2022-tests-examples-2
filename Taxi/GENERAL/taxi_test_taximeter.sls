logstash-5x:
  repos:
    logstash-5x: 'deb https://artifacts.elastic.co/packages/5.x/apt stable main'
  packages:
    yandex-jdk8: any
    logstash: 1:5.6.3-1
    yandex-taximeter-logstash-config-logs: any
    yandex-taxi-logstash-graphite: any
    yandex-taxi-logstash-monrun: any
  jvm_opts:
    heap_size_initial: 256m
    heap_size_maximum: 2g
  settings:
    pipeline_workers: 4
    pipeline_output_workers: 4
    pipeline_batch_size: 4096
