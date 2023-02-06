redis:
  master:
{% for port in range(6387,6391) %}
    redis_{{ port }}:
      port: {{ port }}
      maxmemory: 64g
      repl-backlog-size: 128mb
      repl-backlog-ttl: 0
      maxmemory-policy: volatile-random
      maxclients: 20000
      timeout: 1200
{% endfor %}
