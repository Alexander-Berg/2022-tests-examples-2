redis:
  master:
{% for port in range(6379,6395) %}
    redis_{{ port }}:
      port: {{ port }}
      maxmemory: 4g
      repl-backlog-size: 128mb
      repl-backlog-ttl: 0
      maxmemory-policy: volatile-random
      maxclients: 10000
{% endfor %}
  sentinel:
{% for port in range(6379,6395) %}
    redis_{{ port }}:
      host: taximeter-temp-redis-myt-01.taxi.tst.yandex.net
      port: {{ port }}
      vote: 2
      down-after-milliseconds: 15000
      failover-timeout: 60000
      parallel-syncs: 1
{% endfor %}
