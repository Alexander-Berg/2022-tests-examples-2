import pytest

from tests_access_control.helpers import user_access_info


@pytest.mark.parametrize('provider', ['yandex', 'restapp'])
async def test_get_user_access_info_empty(taxi_access_control, provider):
    await user_access_info.get_user_access_info(
        taxi_access_control,
        provider,
        'user1',
        expected_status_code=200,
        expected_response_json={
            'permissions': [],
            'evaluated_permissions': [],
            'restrictions': [],
            'roles': [],
        },
    )


@pytest.mark.parametrize(
    ['provider', 'provider_user_id'],
    [('yandex', 'user1'), ('restapp', 'user2')],
)
@pytest.mark.pgsql('access_control', files=['simple_test_data.sql'])
async def test_get_user_access_info_nonempty(
        taxi_access_control, provider, provider_user_id,
):
    await user_access_info.get_user_access_info(
        taxi_access_control,
        provider,
        provider_user_id,
        expected_status_code=200,
        expected_response_json={
            'permissions': ['permission1'],
            'evaluated_permissions': [
                {
                    'rule_name': 'org_body_rule',
                    'rule_storage': 'body',
                    'rule_path': 'org',
                    'rule_value': 'taxi',
                },
            ],
            'restrictions': [],
            'roles': [
                {
                    'evaluated_permissions': [
                        {
                            'rule_name': 'org_body_rule',
                            'rule_path': 'org',
                            'rule_storage': 'body',
                            'rule_value': 'taxi',
                        },
                    ],
                    'permissions': ['permission1'],
                    'restrictions': [],
                    'role': 'role1',
                },
            ],
        },
    )


@pytest.mark.pgsql('access_control', files=['tree_test_data.sql'])
async def test_get_user_access_info_user1_permissions(taxi_access_control):
    await user_access_info.get_user_access_info(
        taxi_access_control,
        'yandex',
        'user1',
        expected_status_code=200,
        expected_response_json={
            'permissions': ['permission1', 'permission2'],
            'evaluated_permissions': [],
            'restrictions': [],
            'roles': [
                {
                    'evaluated_permissions': [],
                    'permissions': ['permission1'],
                    'restrictions': [],
                    'role': 'role1',
                },
                {
                    'evaluated_permissions': [],
                    'permissions': ['permission2'],
                    'restrictions': [],
                    'role': 'role2',
                },
            ],
        },
    )


@pytest.mark.pgsql('access_control', files=['tree_test_data.sql'])
async def test_get_user_access_info_user2_permissions(taxi_access_control):
    await user_access_info.get_user_access_info(
        taxi_access_control,
        'yandex',
        'user2',
        expected_status_code=200,
        expected_response_json={
            'permissions': ['permission1', 'permission3'],
            'evaluated_permissions': [],
            'restrictions': [],
            'roles': [
                {
                    'evaluated_permissions': [],
                    'permissions': ['permission1'],
                    'restrictions': [],
                    'role': 'role1',
                },
                {
                    'evaluated_permissions': [],
                    'permissions': ['permission3'],
                    'restrictions': [],
                    'role': 'role3',
                },
            ],
        },
    )


@pytest.mark.pgsql('access_control', files=['restrictions/simple.sql'])
async def test_get_user_restrictions(taxi_access_control):
    restrictions = [
        {
            'handler_path': '/example/handler1',
            'handler_method': 'POST',
            'restriction': {
                'init': {
                    'value': 3,
                    'arg_name': 'body:sample_int_value',
                    'arg_type': 'int',
                },
                'type': 'lte',
            },
        },
        {
            'handler_path': '/example/handler2',
            'handler_method': 'GET',
            'restriction': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'set': ['value1', 'value2'],
                                'arg_name': 'body:sample_field.subfield',
                                'set_elem_type': 'string',
                            },
                            'type': 'in_set',
                        },
                        {
                            'init': {
                                'value': 5.6,
                                'arg_name': 'query:sample_double_value',
                                'arg_type': 'double',
                            },
                            'type': 'lt',
                        },
                    ],
                },
                'type': 'all_of',
            },
        },
    ]
    await user_access_info.get_user_access_info(
        taxi_access_control,
        'yandex',
        'user1',
        expected_status_code=200,
        expected_response_json={
            'permissions': ['permission1'],
            'evaluated_permissions': [],
            'restrictions': restrictions,
            'roles': [
                {
                    'role': 'role1',
                    'permissions': ['permission1'],
                    'evaluated_permissions': [],
                    'restrictions': restrictions,
                },
            ],
        },
    )
