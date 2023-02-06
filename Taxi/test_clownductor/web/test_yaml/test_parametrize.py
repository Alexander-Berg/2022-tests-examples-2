import pytest

from clownductor.internal import parameters
from clownductor.internal import service_parameters
from clownductor.internal.service_yaml import manager as yaml_manager


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'disk_profiles': True})
@pytest.mark.features_on(
    'enable_io_limits_params_remote', 'enable_io_limits_params_yaml',
)
async def test_parametrize_common(
        patch_github_single_file,
        web_context,
        load_json,
        repo_yaml_url,
        service_yaml_path,
):
    patch_github_single_file(
        service_yaml_path('common-service'), 'common.yaml',
    )
    clown_alias = await yaml_manager.get_clown_alias_by_name(
        web_context,
        repo_yaml_url('some-another-repo', 'common-service', 'master'),
        'common-service-critical',
    )
    result = await parameters.parametrize_clown_alias(web_context, clown_alias)
    serialized = service_parameters.service_config_serialize(result)
    expected = load_json(f'CommonServiceCritical.json')
    assert serialized == expected


@pytest.mark.config(
    CLOWNDUCTOR_AVAILABLE_DATACENTERS={
        'projects': [{'datacenters': ['vla', 'sas'], 'name': '__default__'}],
    },
)
@pytest.mark.features_on(
    'disk_profiles',
    'enable_io_limits_params_remote',
    'enable_io_limits_params_yaml',
)
async def test_py3_simple(
        patch_github_single_file,
        web_context,
        load_json,
        backend_py3_yaml_url,
        service_yaml_path,
):
    file_name = 'Py3NewPreset.json'
    alias_name = 'clownductor'
    patch_github_single_file(
        service_yaml_path(alias_name), 'service_py3_new_preset.yaml',
    )
    clown_alias = await yaml_manager.get_clown_alias_by_name(
        web_context, backend_py3_yaml_url(alias_name), alias_name,
    )
    result = await parameters.parametrize_clown_alias(web_context, clown_alias)
    serialized = service_parameters.service_config_serialize(result)
    expected = load_json(file_name)
    assert serialized == expected


@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={'disk_profiles': True},
    CLOWNDUCTOR_PROFILE_DEFAULT={'__default__': 'default'},
)
@pytest.mark.features_on(
    'enable_io_limits_params_remote', 'enable_io_limits_params_yaml',
)
@pytest.mark.parametrize(
    'file_name, alias_name',
    [
        ('TransactionsEdaStq.json', 'transactions-eda-stq'),
        ('TransactionsPersey.json', 'transactions-persey'),
    ],
)
async def test_py3_multi(
        patch_github_single_file,
        web_context,
        load_json,
        backend_py3_yaml_url,
        service_yaml_path,
        file_name,
        alias_name,
):
    patch_github_single_file(
        service_yaml_path('transactions'), 'py3_multi.yaml',
    )
    clown_alias = await yaml_manager.get_clown_alias_by_name(
        web_context, backend_py3_yaml_url('transactions'), alias_name,
    )
    result = await parameters.parametrize_clown_alias(web_context, clown_alias)
    serialized = service_parameters.service_config_serialize(result)
    expected = load_json(file_name)
    assert serialized == expected


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'disk_profiles': True})
@pytest.mark.features_on(
    'enable_io_limits_params_remote', 'enable_io_limits_params_yaml',
)
async def test_uservices_simple(
        patch_github_single_file,
        web_context,
        load_json,
        uservices_yaml_url,
        service_yaml_path,
):
    file_name = 'UservicesNewPreset.json'
    alias_name = 'eats-couriers-equipment'
    patch_github_single_file(
        service_yaml_path(alias_name), 'uservices_new_preset.yaml',
    )
    clown_alias = await yaml_manager.get_clown_alias_by_name(
        web_context, uservices_yaml_url(alias_name), alias_name,
    )
    result = await parameters.parametrize_clown_alias(web_context, clown_alias)
    serialized = service_parameters.service_config_serialize(result)
    expected = load_json(file_name)
    assert serialized == expected
