import pytest

from taxi_testsuite.plugins import config


def test_fixture_basic(taxi_config):
    assert taxi_config.get('foo') == 1
    assert taxi_config.get('bar') == 2
    with pytest.raises(config.ConfigNotFoundError):
        taxi_config.get('maurice')


@pytest.mark.config(foo=111, bar=222, maurice=333, xxx='yyy')
def test_fixture_override(taxi_config):
    assert taxi_config.get('foo') == 111
    assert taxi_config.get('bar') == 222
    assert taxi_config.get('maurice') == 333
    assert taxi_config.get('xxx') == 'yyy'
