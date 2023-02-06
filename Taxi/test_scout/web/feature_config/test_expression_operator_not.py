import pytest

from scout import feature_config


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {'not': {'check': 'env', 'in': ['testing']}},
    },
)
async def test_env_match(get_sample_value):
    value = get_sample_value()
    assert value is False


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {'not': {'check': 'env', 'in': ['stable']}},
    },
)
async def test_env_mismatch(get_sample_value):
    value = get_sample_value()
    assert value is True


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {'not': {'check': 'env', 'in': ['stable']}},
    },
)
async def test_env_badcluster(get_sample_value):
    value = get_sample_value(cluster='bad cluster')
    assert value is False


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {'not': {'check': 'env', 'in': ['stable']}},
    },
)
async def test_env_badcluster_raising(get_sample_value_raising):
    try:
        get_sample_value_raising(cluster='bad cluster')
        assert False, 'Assert should never happen'
    except feature_config.HandleError:
        pass
