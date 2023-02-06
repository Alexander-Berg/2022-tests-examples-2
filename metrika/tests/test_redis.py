from metrika.pylib.yc.redis import ManagedRedis


def test_init():
    ManagedRedis(token='')
