import pytest

from scout import feature_config


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {'check': 'env', 'in': ['testing']},
    },
)
async def test_env_match(get_sample_value):
    value = get_sample_value()
    assert value is True


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {'check': 'env', 'in': ['stable']},
    },
)
async def test_env_mismatch(get_sample_value):
    value = get_sample_value()
    assert value is False


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {'check': 'env', 'in': ['testing']},
    },
)
async def test_env_badcluster(get_sample_value):
    value = get_sample_value(cluster='bad cluster')
    assert value is False


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {'check': 'env', 'in': ['testing']},
    },
)
async def test_env_badcluster_raising(get_sample_value_raising):
    try:
        get_sample_value_raising(cluster='bad cluster')
        assert False, 'Assert should never happen'
    except feature_config.HandleError:
        pass


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {'check': 'zone', 'in': ['sas']},
    },
)
async def test_zone_match(get_sample_value):
    value = get_sample_value()
    assert value is True


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {'check': 'zone', 'in': ['sas']},
    },
)
async def test_zone_match_badcluster(get_sample_value):
    value = get_sample_value(cluster='bad cluster')
    assert value is True


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {'check': 'zone', 'in': ['sas']},
    },
)
async def test_zone_match_badcluster_raising(get_sample_value_raising):
    value = get_sample_value_raising(cluster='bad cluster')
    assert value is True


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {'check': 'zone', 'in': ['man']},
    },
)
async def test_zone_mismatch(get_sample_value):
    value = get_sample_value()
    assert value is False


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {'check': 'tvm_name', 'in': ['envoy-exp-alpha']},
    },
)
async def test_tvm_name_match(get_sample_value):
    value = get_sample_value()
    assert value is True


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {'check': 'tvm_name', 'in': ['envoy-exp-bravo']},
    },
)
async def test_tvm_name_mismatch(get_sample_value):
    value = get_sample_value()
    assert value is False


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {'check': 'tvm_name', 'in': ['envoy-exp-alpha']},
    },
)
async def test_tvm_name_badcluster(get_sample_value):
    value = get_sample_value(cluster='bad cluster')
    assert value is False


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {
            'check': 'host',
            'in': ['taxi-envoy-exp-alpha-testing-3.man.yp-c.yandex.net'],
        },
    },
)
async def test_host_match(get_sample_value):
    value = get_sample_value()
    assert value is True


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {
            'check': 'host',
            'in': ['taxi-envoy-exp-alpha-testing-4.man.yp-c.yandex.net'],
        },
    },
)
async def test_host_mismatch(get_sample_value):
    value = get_sample_value()
    assert value is False
