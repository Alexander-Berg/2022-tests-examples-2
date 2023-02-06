import os
import typing

import taxi_approvals
from taxi_approvals.components.services_schemes import schemes_checker
from taxi_approvals.internal import types as ts


EXPECTED_BAD_SCHEMAS = {
    'test_all_default': (
        'there is more than one default approval '
        'group in file test_all_default.yaml'
    ),
    'bad_no_permissions': (
        'permissions are required for approvement'
        ' group managers in all_envs'
    ),
    'test_audit_and_default': (
        'audit groups are considered as default groups. '
        'Additional default groups should not be '
        'specified test_audit_and_default.yaml'
    ),
    'test_audit_disable': (
        'audit group cannot be disabled test_audit_disable.yaml'
    ),
    'test_error': 'there is duplicate group name in file test_error.yaml',
    'test_audit_default': (
        'audit group cannot be marked as '
        'default group test_audit_default.yaml'
    ),
    'test_no_default': (
        'all approval groups can be disabled, '
        'but there is no default approval '
        'group in file test_no_default.yaml'
    ),
    'test_service_audit_error': (
        'When the flag "is_audit_group" is set, '
        '"common_self_approve" setting can not be used. '
        'Use "audit_self_approve" instead.test_service_audit_error.yaml'
    ),
    'test_service_no_group_name': (
        'all environments must have group name in '
        'file test_service_no_group_name.yaml'
    ),
    'test_perm': '$skip',
}


EXPECTED_BAD_PLATFORM = {
    'bad_permissions': (
        'clowny_roles are required for '
        'approvement group test_name in all_envs'
    ),
}


class SchemeError(Exception):
    """Scheme error for this module"""


def _check_for_errors(schemes):
    for service, scheme in schemes.items():
        if not scheme['is_valid']:
            error = scheme['errors'][0]
            raise SchemeError(f'Service {service} error: {error}')


def test_real_schemas(taxi_approvals_client):
    real_services_schemes_path = os.path.join(
        os.path.dirname(taxi_approvals.__file__), 'services_schemes',
    )
    real_platform_schemes_path = os.path.join(
        real_services_schemes_path, 'platform',
    )
    real_bank_schemes_path = os.path.join(real_services_schemes_path, 'bank')
    real_wfm_effrat_schemes_path = os.path.join(
        real_services_schemes_path, 'wfm_effrat',
    )
    context = typing.cast(ts.WebContext, taxi_approvals_client.app.ctx)
    services_info = schemes_checker.check_all_schemes(
        real_services_schemes_path,
        real_platform_schemes_path,
        real_bank_schemes_path,
        real_wfm_effrat_schemes_path,
        context.services_schemes.json_validators,
    )
    _check_for_errors(services_info['schemes_info'])
    _check_for_errors(services_info['platform_schemes_info'])
    _check_for_errors(services_info['bank_schemes_info'])
    _check_for_errors(services_info['wfm_effrat_schemes_info'])


def _check_bad_schemas(schemes_info, expected):
    not_checked_bad_services = set(expected.keys())
    for service, scheme in schemes_info.items():
        if not scheme['is_valid']:
            assert len(scheme['errors']) == 1
            error = scheme['errors'][0]
            not_checked_bad_services.remove(service)
            if expected[service] == '$skip':
                assert error
            else:
                assert expected[service] == error
    assert not not_checked_bad_services


def test_bad_schemas(taxi_approvals_client):
    context = typing.cast(ts.WebContext, taxi_approvals_client.app.ctx)
    services_info = context.services_schemes.services_info
    assert services_info.keys() == {
        'schemes_info',
        'platform_schemes_info',
        'wfm_effrat_schemes_info',
        'bank_schemes_info',
    }
    schemes_info = services_info['schemes_info']
    platform_schemes_info = services_info['platform_schemes_info']
    _check_bad_schemas(schemes_info, EXPECTED_BAD_SCHEMAS)
    _check_bad_schemas(platform_schemes_info, EXPECTED_BAD_PLATFORM)
