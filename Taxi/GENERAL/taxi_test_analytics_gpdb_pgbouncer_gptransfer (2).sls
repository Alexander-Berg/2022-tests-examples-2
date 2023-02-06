pgbouncer:
  database:
    '*' : host=gpdb-master.taxi.tst.yandex.net port=5432
  pgbouncer:
    listen_addr: "*"
    listen_port: 5432
    pool_mode: transaction
    auth_type: pam
    admin_users: robot-taxi-tst-gpadm
    logfile: /var/log/pgbouncer/pgbouncer.log
    pidfile: /var/run/pgbouncer/pgbouncer.pid
    unix_socket_dir: /var/run/pgbouncer
    max_client_conn: 4096
    default_pool_size: 100
    client_tls_sslmode: allow
    client_tls_protocols: all
    ignore_startup_parameters: extra_float_digits
