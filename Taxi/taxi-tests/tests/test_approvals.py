import logging

import requests


logger = logging.getLogger(__file__)

APPROVALS_HOST = 'http://taxi-approvals.taxi.yandex.net'
ADMIN_PY2_HOST = 'https://ymsh-admin.mobile.yandex-team.ru'
API_ADMIN_HOST = 'http://taxi-api-admin.taxi.yandex.net'


class SchemaError(Exception):
    """Validate schema error"""


def test_ping():
    url = f'{APPROVALS_HOST}/ping'
    response = requests.get(url)
    response.raise_for_status()
    assert response.content == b''


def test_check_approvals_schemas():
    actions_by_admin = _get_audit_actions_by_admin()
    static_permissions = _get_permissions_by_admin()
    _validate_schemas(actions_by_admin, static_permissions)


def _get_audit_actions_by_admin():
    url = f'{ADMIN_PY2_HOST}/api/audit/actions/list/'
    headers = {
        'Content-Type': 'application/json',
        'X-YaTaxi-Api-Key': 'api_admin_robot_token',
    }
    data = {'from_api_admin': False}
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    audit_actions = response.json()
    logger.info(f'audit_actions response {audit_actions}')
    return list({action['action_id'] for action in audit_actions})


def _get_permissions_by_admin():
    url = f'{ADMIN_PY2_HOST}/api/permissions/v2/list/'
    response = requests.get(url, headers={'X-YaTaxi-Api-Key': 'admin_token'})
    response.raise_for_status()
    permissions_tree = response.json()

    permissions = set()
    for category in permissions_tree['categories']:
        for permission in category['permissions']:
            permissions.add(permission['id'])
    permissions.add('example_permission')
    return list(permissions)


def _validate_schemas(actions_by_admin, static_permissions):
    url = f'{APPROVALS_HOST}/technological/validate_schemas/'
    logger.info(f'actions_by_admin: {actions_by_admin}')
    response = requests.post(
        url,
        headers={'X-YaTaxi-Api-Key': 'approvals_token'},
        json={
            'audit_action_ids': actions_by_admin,
            'permissions': static_permissions,
        },
    )
    response.raise_for_status()
    content = response.json()
    invalid_schemas = content['invalid_schemas']
    if invalid_schemas:
        msg = f'Failed validate schemas: {invalid_schemas}'
        logger.error(msg)
        raise SchemaError(msg)
