elasticsearch-2x:
  repos:
    elastic-2x: 'deb https://packages.elastic.co/elasticsearch/2.x/debian stable main'
    kibana-45: 'deb http://packages.elastic.co/kibana/4.5/debian stable main'
    curator-4: 'deb http://packages.elastic.co/curator/4/debian stable main'
  packages:
    elasticsearch: 2.4.6
    kibana: 4.5.4
    python-elasticsearch-curator: 4.0.3
    yandex-jdk8: any
    yandex-taxi-elasticsearch-monrun: any
    yandex-taxi-elasticsearch-curator: any
    yandex-taxi-elasticsearch-graphite: any
  etcdefault:
    es_heap_size: 64g
    max_locked_memory: "unlimited"
  misc:
    old_logs_count: 1
  config:
    cluster:
      cluster_name: "yandex-taxi-logs"
      bootstrap_mlockall: "true"
      http_port: 9201
      dz_minimum_master_nodes: 3
      recover_after_nodes: 1
      index_number_of_replicas: 0
      index_number_of_shards: 1
      custom_settings:
      - "script.inline: true"
      - "script.indexed: true"
      - "script.update: false"
      - "script.mapping: false"
      - "indices.fielddata.cache.size: 30%"
      - "processors: 128"
      - "threadpool.bulk.size: 128"
      - "threadpool.index.size: 128"
    nodes:
      elastic-logs-myt-01.taxi.tst.yandex.net:
        node_name: "logs-myt-01"
        node_data: "false"
        node_master: "true"
        etcdefault:
          es_heap_size: 8g
        kibana:
          config:
            elasticsearch_url: "http://elastic-logs-slb.taxi.tst.yandex.net:9200"
      elastic-logs-vla-01.taxi.tst.yandex.net:
        node_name: "logs-vla-01"
        node_master: "true"
      elastic-logs-vla-02.taxi.tst.yandex.net:
        node_name: "logs-vla-02"
        node_master: "true"
      elastic-logs-sas-01.taxi.tst.yandex.net:
        node_name: "logs-sas-01"
        node_master: "true"
      elastic-logs-sas-02.taxi.tst.yandex.net:
        node_name: "logs-sas-02"
        node_master: "true"
  kibana:
    config:
      server_port: "5602"
      server_host: "127.0.0.1"
