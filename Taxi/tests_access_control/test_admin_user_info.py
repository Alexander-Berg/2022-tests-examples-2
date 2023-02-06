import pytest


@pytest.mark.parametrize(
    [
        'provider_header',
        'provider_user_id_header',
        'expected_status_code',
        'expected_response_json',
    ],
    [
        pytest.param(
            'yandex',
            'user1',
            200,
            {
                'permissions': [],
                'evaluated_permissions': [],
                'restrictions': [],
            },
            id='empty',
        ),
        pytest.param(
            'yandex',
            'user1',
            200,
            {
                'permissions': ['permission1'],
                'evaluated_permissions': [
                    {'rule_name': 'org_body_rule', 'rule_value': 'taxi'},
                ],
                'restrictions': [
                    {
                        'handler': {'method': 'POST', 'path': '/foo/bar'},
                        'predicate': {},
                    },
                ],
            },
            id='nonempty',
            marks=pytest.mark.pgsql(
                'access_control', files=['simple_test_data.sql'],
            ),
        ),
        pytest.param(
            'yandex',
            'user1',
            200,
            {
                'permissions': ['permission1', 'permission2'],
                'evaluated_permissions': [],
                'restrictions': [],
            },
            id='user1_permissions',
            marks=pytest.mark.pgsql(
                'access_control', files=['tree_test_data.sql'],
            ),
        ),
        pytest.param(
            'yandex',
            'user2',
            200,
            {
                'permissions': ['permission1', 'permission3'],
                'evaluated_permissions': [],
                'restrictions': [],
            },
            id='user2_permissions',
            marks=pytest.mark.pgsql(
                'access_control', files=['tree_test_data.sql'],
            ),
        ),
    ],
)
async def test_admin_user_info(
        taxi_access_control,
        provider_header,
        provider_user_id_header,
        expected_status_code,
        expected_response_json,
):
    response = await taxi_access_control.get(
        '/cc/v1/access-control/v1/admin/user-info/',
        headers={
            'X-YaTaxi-Provider': provider_header,
            'X-YaTaxi-ProviderUserId': provider_user_id_header,
        },
    )
    response_json = response.json()

    assert response.status_code == expected_status_code, (
        response.status_code,
        expected_status_code,
        response_json,
    )
    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )
