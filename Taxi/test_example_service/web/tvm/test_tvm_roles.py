import pytest


@pytest.mark.config(
    TVM_ENABLED=True,
    SERVICE_ROLES_ENABLED=True,
    SERVICE_ROLES={
        'example_service': {
            'tvm_check_role': ['service_name_1', 'service_name_2'],
            'multi_role-allowed-complicated-q3_q2': [
                'service_name_2',
                'service_name_3',
            ],
        },
    },
)
@pytest.mark.parametrize(
    'request_path, headers, params, '
    'src_service_name, expected_status, expected_content',
    [
        (
            '/tvm/check_role',
            {'X-Ya-Service-Ticket': 'bad_key'},
            None,
            'service_name_1',
            401,
            {'code': 'tvm-auth-error', 'message': 'TVM authentication error'},
        ),
        (
            '/tvm/check_role',
            {'X-Ya-Service-Ticket': 'good'},
            None,
            'service_name_1',
            200,
            'ok',
        ),
        (
            '/tvm/check_role',
            {'X-Ya-Service-Ticket': 'good'},
            None,
            'service_name_2',
            200,
            'ok',
        ),
        (
            '/tvm/check_role',
            {'X-Ya-Service-Ticket': 'good'},
            None,
            'bad_service_name',
            403,
            {
                'code': 'tvm-auth-error',
                'message': 'Service is not allowed by role',
                'details': {
                    'reason': (
                        'Service bad_service_name is not allowed by role '
                        'tvm_check_role'
                    ),
                },
            },
        ),
        (
            '/tvm/multi_roles/bad_role',
            {'X-Ya-Service-Ticket': 'good'},
            {'sub_role2': 'bad', 'sub_role3': 'bad'},
            'service_name_3',
            403,
            {
                'code': 'tvm-auth-error',
                'message': 'Service is not allowed by role',
                'details': {
                    'reason': (
                        'Service service_name_3 is not allowed by role '
                        'multi_role-bad_role-complicated-bad_bad'
                    ),
                },
            },
        ),
        (
            '/tvm/multi_roles/allowed',
            {'X-Ya-Service-Ticket': 'good'},
            {'sub_role2': 'q2', 'sub_role3': 'q3'},
            'service_name_3',
            200,
            'ok for allowed',
        ),
        (
            '/tvm/multi_roles/allowed',
            {'X-Ya-Service-Ticket': 'bad'},
            {'sub_role2': 'q2', 'sub_role3': 'q3'},
            'service_name_3',
            401,
            {'code': 'tvm-auth-error', 'message': 'TVM authentication error'},
        ),
    ],
)
async def test_role(
        web_app_client,
        patcher_tvm_ticket_check,
        request_path,
        headers,
        params,
        src_service_name,
        expected_status,
        expected_content,
):
    patcher_tvm_ticket_check(src_service_name)
    response = await web_app_client.get(
        request_path, params=params, headers=headers,
    )
    if expected_status != 200:
        content = await response.json()
    else:
        content = await response.text()
    assert response.status == expected_status, content
    assert content == expected_content
