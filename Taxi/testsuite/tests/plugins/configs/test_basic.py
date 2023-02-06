from taxi_tests.plugins import config


def test_memory_config():
    obj = config.TaxiConfig()
    obj.set(foo=1, bar=2)
    assert obj.get('foo') == 1
    assert obj.get('bar') == 2
    assert obj.get_values() == {'foo': 1, 'bar': 2}
