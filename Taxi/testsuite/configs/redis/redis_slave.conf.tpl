daemonize yes
port ${port}
tcp-backlog 511
bind 127.0.0.1 ::1
timeout 0
tcp-keepalive 0
loglevel notice
databases 16
save ""

slaveof 127.0.0.1 ${master_port}
