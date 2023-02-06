redis:
  master:
{% for port in range(6379,6387) %}
    redis_{{ port }}:
      port: {{ port }}
      maxmemory: 4g
      repl-backlog-size: 128mb
      repl-backlog-ttl: 0
      maxmemory-policy: volatile-random
      maxclients: 10000
      save:
        900: 1
        300: 10
        60: 10000
{% endfor %}
  sentinel:
{% for port in range(6379,6387) %}
    redis_{{ port }}:
      host: db-redis-user-tracks-sas-01.taxi.tst.yandex.net
      port: {{ port }}
      vote: 1
      down-after-milliseconds: 15000
      failover-timeout: 30000
      parallel-syncs: 1
{% endfor %}
