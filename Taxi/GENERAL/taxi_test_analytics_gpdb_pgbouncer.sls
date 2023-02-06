odyssey:
  packages:
    odyssey: 0.0.1+taxi1
  conf:
    service:
      workers: 16
      resolvers: 4
      coroutine_stack_size: 128
    listen:
      tls: require
      port: 6432
    storage:
      greenplum-test:
        host: "gpdb-master.taxi.tst.yandex.net"
        port: 5432
      local:
        type: local
    database:
      default:
        user:
          default:
            storage: greenplum-test
            authentication: clear_text
            auth_pam_service: pgbouncer
      console:
        user:
          default:
            storage: local
            authentication: none
