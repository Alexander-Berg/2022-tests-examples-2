import pytest


CONFIGS_VALUES_URL = 'configs/values'


@pytest.mark.parametrize('config', ['GITCONFIG'])
async def test_big_int_in_default_value(taxi_uconfigs, config_schemas, config):
    config_schemas.defaults.answer = {
        'commit': 'hash',
        'defaults': {'GITCONFIG': {'big_int': 2 ** 29}},
    }
    await taxi_uconfigs.invalidate_caches()

    response = await taxi_uconfigs.post(
        CONFIGS_VALUES_URL, json={'ids': [config]},
    )
    assert response.status_code == 200, response.text
    configs = response.json()['configs']
    assert config in configs, response.text
    for _name, value in configs[config].items():
        assert isinstance(value, int)
