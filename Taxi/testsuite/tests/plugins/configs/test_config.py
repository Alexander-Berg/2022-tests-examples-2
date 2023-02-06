import pytest

from taxi_tests.plugins import config


def test_config_read(taxi_config):
    assert taxi_config.get('TEST_FALSE') is False
    assert taxi_config.get('TEST_TRUE') is True
    assert taxi_config.get('TEST_VALUE') == 42
    assert taxi_config.get('TEST_NOT_EXISTS', 'def') == 'def'
    with pytest.raises(config.ConfigNotFoundError) as exc_info:
        taxi_config.get('TEST_NOT_EXISTS')
    expected_err = 'param "TEST_NOT_EXISTS" is not found in config'
    assert str(exc_info.value) == expected_err


@pytest.mark.parametrize('use_set', [True, False])
def test_config_write(taxi_config, use_set):
    values = {
        'TEST_NEW_1': 1,
        'TEST_NEW_TRUE': True,
        'TEST_NEW_FALSE': False,
        'TEST_NEW_STR': 'str',
    }

    if use_set:
        taxi_config.set(**values)
    else:
        taxi_config.set_values(values)

    assert taxi_config.get('TEST_NEW_1') == 1
    assert taxi_config.get('TEST_NEW_TRUE') is True
    assert taxi_config.get('TEST_NEW_FALSE') is False
    assert taxi_config.get('TEST_NEW_STR') == 'str'
