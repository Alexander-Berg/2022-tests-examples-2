csync2:
  conf:
    nossl:
      - '* *'
    groups:
      teamcity:
        key: '/etc/csync2.teamcity.key'
        backup-directory: '/var/backups/csync2'
        hosts:
          - teamcity-sas-01.taxi.tst.yandex.net
          - teamcity-vla-01.taxi.tst.yandex.net
        includes:
          - '/usr/local/teamcity
          - '/var/lib/teamcity/BuildServer
