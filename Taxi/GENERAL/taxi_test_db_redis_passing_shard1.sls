redis:
  master:
{% for port in range(6379,6383) %}
    redis_{{ port }}:
      port: {{ port }}
      maxmemory: 64g
      repl-backlog-size: 128mb
      repl-backlog-ttl: 0
      maxmemory-policy: volatile-random
      maxclients: 20000
      timeout: 1200
{% endfor %}
  sentinel:
{% for port in range(6379,6387) %}
    redis_{{ port }}:
      host: redis-passing-myt-01.taxi.tst.yandex.net
      port: {{ port }}
      vote: 2
      down-after-milliseconds: 60000
      failover-timeout: 180000
      parallel-syncs: 1
{% endfor %}

