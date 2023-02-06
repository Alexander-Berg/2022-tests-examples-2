import pytest


CONFIGS_VALUES_URL = 'configs/values'


def _patch_config(config, config_vars):
    config['components_manager']['components']['configs-defaults-cache'][
        'disable-load-from-schemas'
    ] = True


@pytest.mark.parametrize(
    'name, value, disable_defaults',
    [
        ('SECOND_CONFIG', 200, False),
        ('GITCONFIG', 10, False),
        pytest.param(
            'GITCONFIG',
            None,
            True,
            marks=pytest.mark.uservice_oneshot(config_hooks=[_patch_config]),
            id='disable_default_cache_and_non_existed_config',
        ),
        pytest.param(
            'SECOND_CONFIG',
            200,
            True,
            marks=pytest.mark.uservice_oneshot(config_hooks=[_patch_config]),
            id='disable_default_cache_and_existed_config',
        ),
    ],
)
async def test_configs_value(
        taxi_uconfigs, config_schemas, name, value, disable_defaults,
):
    if disable_defaults:
        config_schemas.defaults.answer = None
    else:
        config_schemas.defaults.answer = {
            'commit': 'hash_new',
            'defaults': {'GITCONFIG': 10},
        }

    for specify_ids in (True, False):
        await taxi_uconfigs.invalidate_caches()
        request = {}
        if specify_ids:
            request['ids'] = [name]
        response = await taxi_uconfigs.post(CONFIGS_VALUES_URL, json=request)
        assert response.status_code == 200
        data = response.json()
        assert str(data['configs'].get(name)) == str(value)
        if disable_defaults:
            assert not config_schemas.defaults_times_called
        else:
            assert config_schemas.defaults_times_called
