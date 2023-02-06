from metrika.pylib.yc.postgresql import ManagedPostgreSQL


def test_init():
    ManagedPostgreSQL(token='')
