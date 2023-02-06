import pytest

from test_callcenter_operators import params


@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.parametrize(
    ['request_json', 'response_status', 'expected_response'],
    (
        pytest.param(
            {'login': f'{params.OPERATOR_1["login"]}@unit.test'},
            200,
            {'password': params.OPERATOR_1['password']},
            id='ok_request',
            marks=pytest.mark.pgsql(
                'callcenter_auth',
                files=['callcenter_auth_existing_operators.sql'],
            ),
        ),
        pytest.param(
            {'bad_request': 'very_bad'},
            400,
            {'code': 'invalid_request', 'message': 'Неверный запрос'},
            id='bag_request',
            marks=pytest.mark.pgsql(
                'callcenter_auth',
                files=['callcenter_auth_existing_operators.sql'],
            ),
        ),
        pytest.param(
            {'login': 'login100'},
            404,
            {
                'code': 'operator_not_found',
                'message': 'Оператор не найден или не имеет пароля',
            },
            id='operator_not_found',
            marks=pytest.mark.pgsql(
                'callcenter_auth',
                files=['callcenter_auth_existing_operators.sql'],
            ),
        ),
        pytest.param(
            {'login': f'{params.OPERATOR_1["login"]}@unit.test'},
            404,
            {
                'code': 'operator_not_found',
                'message': 'Оператор не найден или не имеет пароля',
            },
            id='old_record operator',
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_old_records.sql'],
            ),
        ),
    ),
)
async def test_admin_get_password(
        taxi_callcenter_operators_web,
        request_json,
        response_status,
        expected_response,
):
    response = await taxi_callcenter_operators_web.post(
        '/v2/admin/operators/password/', json=request_json,
    )

    assert response.status == response_status
    if response_status == 400:
        text_content = await response.text()
        assert text_content
    else:
        content = await response.json()
        assert content == expected_response
