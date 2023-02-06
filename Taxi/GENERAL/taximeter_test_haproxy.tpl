global
        log 127.0.0.1   local0
        log 127.0.0.1   local1 notice
        maxconn 4096
        user haproxy
        group haproxy
        stats socket /var/run/haproxy.stat level admin
        tune.ssl.default-dh-param 2048
        daemon
        nbproc 4

defaults
        log     global
        mode    tcp
        option  tcplog
        timeout client  5s
        timeout server  5s
        timeout connect 5s
        balance         leastconn

{% for port in range(6379,6395) %}
listen base-master-{{ port }}
    bind 127.0.0.1:{{ 13622 + port }}
    bind ::1:{{ 13622 + port }}
        
    option tcp-check
    tcp-check send AUTH\ {{ REDIS['masterauth'] }}\r\n
    tcp-check expect string +OK

    tcp-check send PING\r\n
    tcp-check expect string +PONG

    tcp-check send info\ replication\r\n
    tcp-check expect string role:master

    tcp-check send QUIT\r\n
    tcp-check expect string +OK

    server taximeter-base-redis-iva-01.taxi.tst.yandex.net taximeter-base-redis-iva-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-base-redis-myt-01.taxi.tst.yandex.net taximeter-base-redis-myt-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-base-redis-vla-01.taxi.tst.yandex.net taximeter-base-redis-vla-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-base-redis-iva-01.taxi.tst.yandex.net taximeter-base-redis-iva-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-base-redis-myt-01.taxi.tst.yandex.net taximeter-base-redis-myt-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-base-redis-vla-01.taxi.tst.yandex.net taximeter-base-redis-vla-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions

listen base-slaves-{{ port }}
    bind 127.0.0.1:{{ 14622 + port }}
    bind ::1:{{ 14622 + port }}

    option tcp-check

    tcp-check send AUTH\ {{ REDIS['masterauth'] }}\r\n
    tcp-check expect string +OK

    tcp-check send PING\r\n
    tcp-check expect string +PONG

    tcp-check send QUIT\r\n
    tcp-check expect string +OK

    server taximeter-base-redis-iva-01.taxi.tst.yandex.net taximeter-base-redis-iva-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-base-redis-myt-01.taxi.tst.yandex.net taximeter-base-redis-myt-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-base-redis-vla-01.taxi.tst.yandex.net taximeter-base-redis-vla-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-base-redis-iva-01.taxi.tst.yandex.net taximeter-base-redis-iva-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-base-redis-myt-01.taxi.tst.yandex.net taximeter-base-redis-myt-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-base-redis-vla-01.taxi.tst.yandex.net taximeter-base-redis-vla-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions

listen hour-master-{{ port }}
    bind 127.0.0.1:{{ 23622 + port }}
    bind ::1:{{ 23622 + port }}
        
    option tcp-check
    tcp-check send AUTH\ {{ REDIS['masterauth'] }}\r\n
    tcp-check expect string +OK

    tcp-check send PING\r\n
    tcp-check expect string +PONG

    tcp-check send info\ replication\r\n
    tcp-check expect string role:master

    tcp-check send QUIT\r\n
    tcp-check expect string +OK

    server taximeter-hour-redis-iva-01.taxi.tst.yandex.net taximeter-hour-redis-iva-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-hour-redis-myt-01.taxi.tst.yandex.net taximeter-hour-redis-myt-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-hour-redis-vla-01.taxi.tst.yandex.net taximeter-hour-redis-vla-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-hour-redis-iva-01.taxi.tst.yandex.net taximeter-hour-redis-iva-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-hour-redis-myt-01.taxi.tst.yandex.net taximeter-hour-redis-myt-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-hour-redis-vla-01.taxi.tst.yandex.net taximeter-hour-redis-vla-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions

listen hour-slaves-{{ port }}
    bind 127.0.0.1:{{ 24622 + port }}
    bind ::1:{{ 24622 + port }}

    option tcp-check

    tcp-check send AUTH\ {{ REDIS['masterauth'] }}\r\n
    tcp-check expect string +OK

    tcp-check send PING\r\n
    tcp-check expect string +PONG

    tcp-check send QUIT\r\n
    tcp-check expect string +OK

    server taximeter-hour-redis-iva-01.taxi.tst.yandex.net taximeter-hour-redis-iva-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-hour-redis-myt-01.taxi.tst.yandex.net taximeter-hour-redis-myt-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-hour-redis-vla-01.taxi.tst.yandex.net taximeter-hour-redis-vla-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-hour-redis-iva-01.taxi.tst.yandex.net taximeter-hour-redis-iva-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-hour-redis-myt-01.taxi.tst.yandex.net taximeter-hour-redis-myt-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-hour-redis-vla-01.taxi.tst.yandex.net taximeter-hour-redis-vla-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions

listen temp-master-{{ port }}
    bind 127.0.0.1:{{ 18622 + port }}
    bind ::1:{{ 18622 + port }}
        
    option tcp-check
    tcp-check send AUTH\ {{ REDIS['masterauth'] }}\r\n
    tcp-check expect string +OK

    tcp-check send PING\r\n
    tcp-check expect string +PONG

    tcp-check send info\ replication\r\n
    tcp-check expect string role:master

    tcp-check send QUIT\r\n
    tcp-check expect string +OK

    server taximeter-temp-redis-iva-01.taxi.tst.yandex.net taximeter-temp-redis-iva-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-temp-redis-myt-01.taxi.tst.yandex.net taximeter-temp-redis-myt-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-temp-redis-vla-01.taxi.tst.yandex.net taximeter-temp-redis-vla-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-temp-redis-iva-01.taxi.tst.yandex.net taximeter-temp-redis-iva-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-temp-redis-myt-01.taxi.tst.yandex.net taximeter-temp-redis-myt-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-temp-redis-vla-01.taxi.tst.yandex.net taximeter-temp-redis-vla-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions

listen temp-slaves-{{ port }}
    bind 127.0.0.1:{{ 19622 + port }}
    bind ::1:{{ 19622 + port }}

    option tcp-check

    tcp-check send AUTH\ {{ REDIS['masterauth'] }}\r\n
    tcp-check expect string +OK

    tcp-check send PING\r\n
    tcp-check expect string +PONG

    tcp-check send QUIT\r\n
    tcp-check expect string +OK

    server taximeter-temp-redis-iva-01.taxi.tst.yandex.net taximeter-temp-redis-iva-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-temp-redis-myt-01.taxi.tst.yandex.net taximeter-temp-redis-myt-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-temp-redis-vla-01.taxi.tst.yandex.net taximeter-temp-redis-vla-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-temp-redis-iva-01.taxi.tst.yandex.net taximeter-temp-redis-iva-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-temp-redis-myt-01.taxi.tst.yandex.net taximeter-temp-redis-myt-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions
    server taximeter-temp-redis-vla-01.taxi.tst.yandex.net taximeter-temp-redis-vla-01.taxi.tst.yandex.net:{{ port }} check inter 1s fall 3 rise 1 on-marked-down shutdown-sessions

{% endfor %}
