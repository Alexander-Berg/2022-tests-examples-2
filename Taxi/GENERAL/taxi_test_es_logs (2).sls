elasticsearch-7x:
  repos:
    elastic-7: 'deb https://artifacts.elastic.co/packages/7.x/apt stable main'
    curator-5: 'deb [arch=amd64] https://packages.elastic.co/curator/5/debian stable main'
  packages:
    kibana: 7.16.2
    elasticsearch: 7.16.2
    elasticsearch-curator: 5.8.1
    cerebro: 0.9.2+taxi1
    config-nginx-elastic-logs: latest
    config-nginx-elastic-logs-kibana: latest
    config-nginx-elastic-logs-cerebro: latest
    yandex-taxi-elasticsearch-curator: latest
    yandex-taxi-elasticsearch-graphite: latest
  etcdefault:
    es_heap_size: 31g
  systemd:
    limit_nofile: 200000
  config:
    node_master: "true"
    node_data: "true"
    masters:
    - "elastic-logs-sas-04.taxi.tst.yandex.net"
    - "elastic-logs-sas-05.taxi.tst.yandex.net"
    - "elastic-logs-sas-06.taxi.tst.yandex.net"
    - "elastic-logs-vla-04.taxi.tst.yandex.net"
    - "elastic-logs-vla-05.taxi.tst.yandex.net"
    - "elastic-logs-vla-06.taxi.tst.yandex.net"
    - "elastic-logs-myt-01.taxi.tst.yandex.net"
    cluster:
      cluster_name: "yandex-taxi-logs"
      custom_settings:
      - "indices.fielddata.cache.size: 30%"
      - "indices.query.bool.max_clause_count: 8192"
    nodes:
      elastic-logs-myt-01.taxi.tst.yandex.net:
        node_data: "false"
        etcdefault:
          es_heap_size: 8g
  kibana:
    config:
      server_port: "5602"
      server_max_payload_bytes: "4194304"
      xpack_reporting_enabled: "true"
      xpack_uptime_enabled: "false"
      xpack_siem_enabled: "false"
      elasticsearch_request_timeout: 60000
      elasticsearch_shard_timeout: 60000
