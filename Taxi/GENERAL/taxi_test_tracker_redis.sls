redis:
  syslog:
    template: '$ISODATE $MSGONLY\n'
  master:
{% for port in range(6379,6387) %}
    redis_{{ port }}:
      port: {{ port }}
      maxmemory: 2g
      repl-backlog-size: 128mb
      repl-backlog-ttl: 0
      maxmemory-policy: volatile-random
      maxclients: 10000
{% endfor %}
  sentinel:
{% for port in range(6379,6387) %}
    redis_{{ port }}:
      host: taxi-tracker-redis01i.taxi.tst.yandex.net
      port: {{ port }}
      vote: 2
      down-after-milliseconds: 60000
      failover-timeout: 180000
      parallel-syncs: 1
{% endfor %}
