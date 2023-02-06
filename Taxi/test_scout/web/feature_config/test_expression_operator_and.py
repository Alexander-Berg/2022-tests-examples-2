import pytest

from scout import feature_config


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {
            'and': [
                {'check': 'env', 'in': ['testing']},
                {'check': 'zone', 'in': ['sas']},
            ],
        },
    },
)
async def test_env_zone_match(get_sample_value):
    value = get_sample_value()
    assert value is True


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {
            'and': [
                {'check': 'env', 'in': ['stable']},
                {'check': 'zone', 'in': ['sas']},
            ],
        },
    },
)
async def test_env_zone_mismatch_env(get_sample_value):
    value = get_sample_value()
    assert value is False


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {
            'and': [
                {'check': 'env', 'in': ['testing']},
                {'check': 'zone', 'in': ['man']},
            ],
        },
    },
)
async def test_env_zone_mismatch_zone(get_sample_value):
    value = get_sample_value()
    assert value is False


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {
            'and': [
                {'check': 'env', 'in': ['stable']},
                {'check': 'zone', 'in': ['man']},
            ],
        },
    },
)
async def test_env_zone_mismatch_all(get_sample_value):
    value = get_sample_value()
    assert value is False


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {
            'and': [
                {'check': 'env', 'in': ['testing']},
                {'check': 'zone', 'in': ['sas']},
            ],
        },
    },
)
async def test_env_zone_badcluster(get_sample_value):
    value = get_sample_value(cluster='bad cluster')
    assert value is False


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'expression',
        'expression': {
            'and': [
                {'check': 'env', 'in': ['testing']},
                {'check': 'zone', 'in': ['sas']},
            ],
        },
    },
)
async def test_env_zone_badcluster_raising(get_sample_value_raising):
    try:
        get_sample_value_raising(cluster='bad cluster')
        assert False, 'Assert should never happen'
    except feature_config.HandleError:
        pass
