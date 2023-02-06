from metrika.pylib.yc.clickhouse import ManagedClickhouse


def test_init():
    ManagedClickhouse(token='')
