import datetime

import pytest


@pytest.mark.now('2021-03-05T12:00:00.00Z')
@pytest.mark.config(
    CALLCENTER_OPERATORS_CALLCENTER_MAP_DOMAIN={'__default__': 'unit.test'},
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=[
        {'domain': 'unit.test', 'token_alias': 'UNITTESTS_CONNECT_OAUTH'},
    ],
)
@pytest.mark.parametrize(
    [
        'request_json',
        'response_status',
        'expected_response',
        'expected_stq_times_called',
    ],
    (
        pytest.param(
            {
                'logins': [
                    'login1@unit.test',
                    'login2@unit.test',
                    'login3@unit.test',
                    'login4@unit.test',
                ],
            },
            200,
            {'notFoundLogins': ['login2@unit.test', 'login4@unit.test']},
            2,
            id='ok request',
        ),
        pytest.param(
            {'logins': ['bad_login']},
            404,
            {
                'code': 'no_operators_found',
                'message': 'Ни один оператор из списка не найден',
            },
            0,
            id='ok request, not existing login',
        ),
        pytest.param(
            {'bad': 'request'},
            400,
            {'code': 'invalid_request', 'message': 'Неверный запрос'},
            0,
            id='bad request',
        ),
    ),
)
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
async def test_admin_bulk_delete(
        taxi_callcenter_operators_web,
        request_json,
        response_status,
        expected_response,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_passport,
        mock_telephony_api_full,
        mock_save_status,
        stq,
        expected_stq_times_called,
        mock_set_status_cc_queues,
):
    response = await taxi_callcenter_operators_web.post(
        '/v2/admin/operators/delete_bulk/', json=request_json,
    )
    assert response.status == response_status
    assert (
        stq.callcenter_operators_sync_roles.times_called
        == expected_stq_times_called
    )
    for _ in range(expected_stq_times_called):
        call = stq.callcenter_operators_sync_roles.next_call()
        assert call['eta'] == datetime.datetime(2021, 3, 5, 12, 0, 1)
    if response_status != 200:
        text_content = await response.text()
        assert text_content
    else:
        content = await response.json()

        assert set(content['notFoundLogins']) == set(
            expected_response['notFoundLogins'],
        )


@pytest.mark.now('2021-03-05T12:00:00.00Z')
@pytest.mark.config(
    CALLCENTER_OPERATORS_CALLCENTER_MAP_DOMAIN={'__default__': 'unit.test'},
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=[
        {'domain': 'unit.test', 'token_alias': 'UNITTESTS_CONNECT_OAUTH'},
    ],
)
@pytest.mark.parametrize(
    [
        'request_json',
        'response_status',
        'expected_response',
        'expected_stq_times_called',
    ],
    (
        pytest.param(
            {'logins': ['login1@unit.test', 'login3@unit.test']},
            200,
            {},
            1,
            id='ok request',
        ),
    ),
)
@pytest.mark.pgsql(
    'callcenter_auth',
    files=['callcenter_auth_existing_operators_with_idm_roles.sql'],
)
async def test_cannot_bulk_delete_for_operator_with_idm_roles(
        taxi_callcenter_operators_web,
        request_json,
        response_status,
        expected_response,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_passport,
        mock_telephony_api_full,
        mock_save_status,
        stq,
        expected_stq_times_called,
        mock_set_status_cc_queues,
):
    response = await taxi_callcenter_operators_web.post(
        '/v2/admin/operators/delete_bulk/', json=request_json,
    )
    assert response.status == response_status
    assert (
        stq.callcenter_operators_sync_roles.times_called
        == expected_stq_times_called
    )
    for _ in range(expected_stq_times_called):
        call = stq.callcenter_operators_sync_roles.next_call()
        assert call['eta'] == datetime.datetime(2021, 3, 5, 12, 0, 1)

    content = await response.json()

    assert content == {'hasIdmRoles': ['login1'], 'notFoundLogins': []}
