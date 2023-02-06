import os
import typing

import pytest
import yaml

from taxi.util.aiohttp_kit import api as api_kit

import taxi_api_admin
from taxi_api_admin.components.services_schemes import exceptions
from taxi_api_admin.components.services_schemes import models
from taxi_api_admin.components.services_schemes import scheme_checker
from taxi_api_admin.internal import types as ts


class SchemeError(Exception):
    """Scheme error for this module"""


@pytest.mark.parametrize(
    'is_platform, error_schemes',
    [
        pytest.param(
            False,
            {
                'error_service': {
                    'These action ids are already exist, '
                    'please fix the scheme: {\'test_action_id\'}',
                    'These categories ids were not found in admin '
                    'and api admin services: {\'test_perm_cat\'}',
                    'Config NOT_DECLARED_CONFIG not declared '
                    'in service.yaml:config',
                },
                'service_with_empty_permission': {
                    'These permissions are empty, please '
                    'fix the scheme: empty_action/?',
                },
            },
            id='admin_schemes',
        ),
        pytest.param(
            True,
            {
                'error_service': {
                    '{\'tvm_auth\': ["True is not of type \'object\'"], '
                    '\'api.0.methods.0\': '
                    '["\'clowny_roles\' is a required property"]}',
                },
                'error_bad_field_type': {
                    '{\'api.0.methods.0.clowny_roles.any_of.0.all_of.'
                    '0.check_field.type\': '
                    '["\'bad_field_type\' is not one of '
                    '[\'branch_id\', \'service_id\', \'project_id\', '
                    '\'project_name\', \'tplatform_namespace\', '
                    '\'abc_slug\', \'no_scope_check\']"]}',
                },
                'missing_no_scope_reason': {
                    'x-no-scope-role-check-reason field is required '
                    'in case of type==no_scope_check',
                },
                'missing_retrieve_settings': {
                    'retrieve_settings field is required '
                    'in case of type==service_id',
                },
            },
            id='platform_schemes',
        ),
    ],
)
@pytest.mark.norerun
def test_all_schemes(
        taxi_api_admin_client, taxi_api_admin_app, error_schemes, is_platform,
):
    ctx = typing.cast(ts.WebContext, taxi_api_admin_app.ctx)
    services_schemes = ctx.services_schemes
    if is_platform:
        schemes_info = services_schemes.services_info.platform_schemes_info
    else:
        schemes_info = services_schemes.services_info.schemes_info
    bad_schemes = dict()
    for key, value in schemes_info.items():
        if not value.is_valid:
            bad_schemes[key] = value
    for bad_key, bad_value in bad_schemes.items():
        assert error_schemes.get(bad_key), bad_key
        for error in bad_value.errors:
            assert error in error_schemes[bad_key], f'{error!r}'
        assert len(bad_value.errors) == len(error_schemes[bad_key])
    assert len(bad_schemes.keys()) == len(error_schemes.keys())


@pytest.mark.norerun
def test_platform_real_schemes(taxi_api_admin_client):
    real_services_schemes_path = os.path.join(
        os.path.dirname(taxi_api_admin.__file__),
        'services_schemes',
        'platform',
    )
    verify_schemes_path = os.path.join(
        os.path.dirname(taxi_api_admin.__file__), 'docs', 'api',
    )
    json_validators = api_kit.JsonValidatorStore(verify_schemes_path)
    schemes_info: models.PlatformSchemesInfo = models.PlatformSchemesInfo(
        real_services_schemes_path,
        models.PlatformServiceSchemeParser,
        json_validators,
    )
    assert list(schemes_info.schemes_files)
    for scheme_file in schemes_info.schemes_files:
        if not scheme_file.endswith('yaml'):
            continue
        scheme_info = schemes_info.init_scheme_info(scheme_file)
        scheme_checker.check_qos_configs(
            taxi_api_admin_client.app.ctx, scheme_info.scheme,
        )
        scheme_checker.check_platform_methods(scheme_info.scheme)
        if scheme_info.errors:
            raise SchemeError(scheme_info.errors[0])


@pytest.mark.norerun
def test_permission(taxi_api_admin_client):
    real_services_schemes_path = os.path.join(
        os.path.dirname(taxi_api_admin.__file__), 'services_schemes',
    )
    actions_path = os.path.join(
        os.path.dirname(taxi_api_admin.__file__),
        'services_schemes',
        'permissions',
        'actions.yaml',
    )
    sections_path = os.path.join(
        os.path.dirname(taxi_api_admin.__file__),
        'services_schemes',
        'permissions',
        'sections.yaml',
    )
    verify_schemes_path = os.path.join(
        os.path.dirname(taxi_api_admin.__file__), 'docs', 'api',
    )
    json_validators = api_kit.JsonValidatorStore(verify_schemes_path)
    all_actions = scheme_checker.get_actions(json_validators, actions_path)
    all_sections = scheme_checker.get_sections(json_validators, sections_path)
    all_py3_permission_ids = []
    schemes_info: models.AdminSchemesInfo = models.AdminSchemesInfo(
        real_services_schemes_path,
        models.AdminServiceSchemeParser,
        json_validators,
    )
    assert list(schemes_info.schemes_files)
    for scheme_file in schemes_info.schemes_files:
        if not scheme_file.endswith('yaml'):
            continue
        try:
            scheme_info = schemes_info.init_scheme_info(scheme_file)
            if scheme_info.errors:
                raise SchemeError(scheme_info.errors[0])
            service_scheme = scheme_info.scheme
            service_admin_permissions = service_scheme.admin_permissions
            if service_admin_permissions:
                scheme_checker.check_permissions_actions(
                    service_admin_permissions, all_actions,
                )
                scheme_checker.check_permissions_sections(
                    service_admin_permissions, all_sections,
                )
                all_py3_permission_ids.extend(
                    [
                        permission.permission_id
                        for permission in service_admin_permissions
                    ],
                )
            api = service_scheme.api
            for path in api:
                for method in path['methods']:
                    if not method.get('permissions'):
                        raise SchemeError(
                            f'{path["path"]} has empty '
                            f'permission field in {scheme_file}',
                        )
        except (yaml.YAMLError, exceptions.PermissionsError) as error:
            raise SchemeError(str(error))
    unique_permission_ids = set(all_py3_permission_ids)
    if len(unique_permission_ids) != len(all_py3_permission_ids):
        for unique_permission_id in unique_permission_ids:
            all_py3_permission_ids.remove(unique_permission_id)
        assert all_py3_permission_ids == []
