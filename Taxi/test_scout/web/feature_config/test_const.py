import pytest


async def test_default(get_sample_value):
    value = get_sample_value()
    assert value is False


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={'type': 'const', 'value': False},
)
async def test_false(get_sample_value):
    value = get_sample_value()
    assert value is False


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={'type': 'const', 'value': False},
)
async def test_false_badcluster(get_sample_value):
    value = get_sample_value(cluster='bad cluster')
    assert value is False


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'const',
        'value': False,
        'error_politic': 'soft',
    },
)
async def test_false_badcluster_raising(get_sample_value_raising):
    value = get_sample_value_raising(cluster='bad cluster')
    assert value is False


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={'type': 'const', 'value': True},
)
async def test_true(get_sample_value):
    value = get_sample_value()
    assert value is True


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={'type': 'const', 'value': True},
)
async def test_true_badcluster(get_sample_value):
    value = get_sample_value(cluster='bad cluster')
    assert value is True


@pytest.mark.config(
    SCOUT_FEATURE_CONFIG_SAMPLE={
        'type': 'const',
        'value': True,
        'error_politic': 'soft',
    },
)
async def test_true_badcluster_raising(get_sample_value_raising):
    value = get_sample_value_raising(cluster='bad cluster')
    assert value is True
