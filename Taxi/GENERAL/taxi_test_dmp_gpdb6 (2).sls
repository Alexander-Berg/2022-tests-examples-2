gpdb6:
  hosts:
    master:
      - gpdb-6-master-vla-01.taxi.tst.yandex.net
      - gpdb-6-master-vla-02.taxi.tst.yandex.net
    segment:
      - gpdb-6-segment-vla-01.taxi.tst.yandex.net
      - gpdb-6-segment-vla-02.taxi.tst.yandex.net
      - gpdb-6-segment-vla-03.taxi.tst.yandex.net
      - gpdb-6-segment-vla-04.taxi.tst.yandex.net
      - gpdb-6-segment-vla-05.taxi.tst.yandex.net
      - gpdb-6-segment-vla-06.taxi.tst.yandex.net
      - gpdb-6-segment-vla-07.taxi.tst.yandex.net
      - gpdb-6-segment-vla-08.taxi.tst.yandex.net
  config:
    gpdb_user: robot-taxi-tst-gpadm
    gpdb_group: dpt_virtual_robots
    gpdb_userdbname: butthead
