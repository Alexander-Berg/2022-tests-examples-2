postgresql:
  version: 9.4
  cluster: main
  max_connections: 200
  shared_buffers: 1000MB
  additional_maps_packages: 'off'
  rsync_test_connection: 'maps@pgsql-backup.taxi.yandex.net/taxi-pgsql'
