haproxy:
  client_timeout: 600s
  server_timeout: 600s
  connect_timeout: 5s
  maxconn: 8192
  nbproc: 4
  balance: roundrobin
  proxies:
{% for port in [ 8443, 9440 ] %}
    - name: atlas-test-{{ port }}
      bind:
        - "[::]"
      port: {{ port }}
      mode: tcp
      tcp_check: []
      check_opts: 'inter 5s fastinter 2s fall 3 rise 3'
      servers:
        - name: sas-q5verwia864qeg8r.db.yandex.net
          port: {{ port }}
        - name: vla-5o8vdnv9mu04kw65.db.yandex.net
          port: {{ port }}
        - name: sas-pdxj0b465nz7l8b5.db.yandex.net
          port: {{ port }}
        - name: vla-aqo9ss0cabao3qzm.db.yandex.net
          port: {{ port }}
        - name: sas-mo0g2pk23i6ztq8j.db.yandex.net
          port: {{ port }}
        - name: vla-vxnwruwqpa8ahygt.db.yandex.net
          port: {{ port }}
{% endfor %}
