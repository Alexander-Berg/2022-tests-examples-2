import pytest


@pytest.mark.parametrize(
    'audit_action_ids, permissions, expected',
    [
        (
            ['test_apply_audit_action_id'],
            [
                'test_permission',
                'test_dev_permission',
                'test_man_permission',
                'unknown_permission',
            ],
            {
                'valid_schemas': [
                    {'service_name': 'test_service', 'schema_type': 'admin'},
                    {'service_name': 'test_service2', 'schema_type': 'admin'},
                    {'service_name': 'test_service20', 'schema_type': 'admin'},
                    {'service_name': 'test_perm', 'schema_type': 'admin'},
                    {
                        'schema_type': 'platform',
                        'service_name': 'good_service',
                    },
                    {
                        'schema_type': 'platform',
                        'service_name': 'test_service',
                    },
                    {'schema_type': 'bank', 'service_name': 'bank_service'},
                    {
                        'schema_type': 'bank',
                        'service_name': 'bank_service_configs',
                    },
                ],
                'invalid_schemas': [
                    {'service_name': 'test_perm', 'schema_type': 'admin'},
                    {'service_name': 'test_error', 'schema_type': 'admin'},
                    {
                        'service_name': 'test_no_default',
                        'schema_type': 'admin',
                    },
                    {
                        'service_name': 'test_all_default',
                        'schema_type': 'admin',
                    },
                    {
                        'service_name': 'test_audit_and_default',
                        'schema_type': 'admin',
                    },
                    {
                        'service_name': 'test_audit_default',
                        'schema_type': 'admin',
                    },
                    {
                        'service_name': 'test_audit_disable',
                        'schema_type': 'admin',
                    },
                    {
                        'service_name': 'test_service_audit_error',
                        'schema_type': 'admin',
                    },
                    {
                        'service_name': 'test_service_no_group_name',
                        'schema_type': 'admin',
                    },
                    {
                        'service_name': 'bad_no_permissions',
                        'schema_type': 'admin',
                    },
                    {
                        'schema_type': 'platform',
                        'service_name': 'bad_permissions',
                    },
                ],
            },
        ),
        (
            ['draft_apply'],
            ['test_permission'],
            {
                'valid_schemas': [
                    {'service_name': 'test_service2', 'schema_type': 'admin'},
                    {'service_name': 'test_service20', 'schema_type': 'admin'},
                    {
                        'schema_type': 'platform',
                        'service_name': 'good_service',
                    },
                    {
                        'schema_type': 'platform',
                        'service_name': 'test_service',
                    },
                    {'schema_type': 'bank', 'service_name': 'bank_service'},
                    {
                        'schema_type': 'bank',
                        'service_name': 'bank_service_configs',
                    },
                ],
                'invalid_schemas': [
                    {'service_name': 'test_perm', 'schema_type': 'admin'},
                    {
                        'service_name': 'test_service',
                        'schema_type': 'admin',
                        'details': {
                            'unregistered_audit_actions': [
                                'test_apply_audit_action_id',
                            ],
                            'unregistered_permissions': [
                                'test_dev_permission',
                                'test_man_permission',
                            ],
                        },
                    },
                    {'service_name': 'test_error', 'schema_type': 'admin'},
                    {
                        'service_name': 'test_no_default',
                        'schema_type': 'admin',
                    },
                    {
                        'service_name': 'test_all_default',
                        'schema_type': 'admin',
                    },
                    {
                        'service_name': 'test_audit_and_default',
                        'schema_type': 'admin',
                    },
                    {
                        'service_name': 'test_audit_default',
                        'schema_type': 'admin',
                    },
                    {
                        'service_name': 'test_audit_disable',
                        'schema_type': 'admin',
                    },
                    {
                        'service_name': 'test_service_audit_error',
                        'schema_type': 'admin',
                    },
                    {
                        'service_name': 'test_service_no_group_name',
                        'schema_type': 'admin',
                    },
                    {
                        'service_name': 'bad_no_permissions',
                        'schema_type': 'admin',
                    },
                    {
                        'schema_type': 'platform',
                        'service_name': 'bad_permissions',
                    },
                ],
            },
        ),
    ],
)
async def test_get_apply_action_ids(
        taxi_approvals_client, audit_action_ids, permissions, expected,
):
    response = await taxi_approvals_client.post(
        '/technological/validate_schemas/',
        json={
            'audit_action_ids': audit_action_ids,
            'permissions': permissions,
        },
    )
    content = await response.json()
    assert response.status == 200
    valid_schemas = content.pop('valid_schemas')
    invalid_schemas = content.pop('invalid_schemas')
    assert check_schemas(valid_schemas, expected['valid_schemas'])
    assert check_schemas(invalid_schemas, expected['invalid_schemas'])
    assert content == {}


def check_schemas(schemas, expected_schemas):
    for schema in schemas:
        assert schema in expected_schemas
    return True
