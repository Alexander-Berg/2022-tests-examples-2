import pytest

from scout import feature_config


@pytest.fixture(name='complex_config')
async def _complex_config(load_json, taxi_config, web_context):
    taxi_config.set(
        SCOUT_FEATURE_CONFIG_SAMPLE=load_json('complex_config.json'),
    )
    await web_context.refresh_caches()


async def test_default(complex_config, get_sample_value):
    value = get_sample_value()
    assert value is False


async def test_default_raising(complex_config, get_sample_value_raising):
    value = get_sample_value_raising()
    assert value is False


async def test_badcluster(complex_config, get_sample_value):
    value = get_sample_value(cluster='bad cluster')
    assert value is False


async def test_badcluster_raising(complex_config, get_sample_value_raising):
    try:
        get_sample_value_raising(cluster='bad cluster')
        assert False, 'Assert should never happen'
    except feature_config.HandleError:
        pass


async def test_env_zone_true(complex_config, get_sample_value_raising):
    value = get_sample_value_raising(zone='vla')
    assert value is True


async def test_tvm_name_true(complex_config, get_sample_value_raising):
    value = get_sample_value_raising(
        cluster='taxi_tst_envoy-exp-bravo_testing',
    )
    assert value is True


async def test_zone_host_true(complex_config, get_sample_value_raising):
    value = get_sample_value_raising(
        zone='vla',
        host='"taxi-envoy-exp-alpha-testing-3.vla.yp-c.yandex.net"',
    )
    assert value is True
