import datetime

import pytest

from test_callcenter_operators import params

ADD_BULK_URL = '/v3/admin/operators/neophonish/add_bulk/'


@pytest.mark.now('2021-03-05T12:00:00.00Z')
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=params.ORGANIZATIONS_TOKENS,
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
            params.NEOPHONISH_REQUEST,
            200,
            {'warnings': []},
            1,
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_admin_only.sql'],
            ),
            id='normal request',
        ),
        pytest.param(
            params.NEOPHONISH_REQUEST_WITH_NOT_PASSPORT_OPERATOR,
            200,
            {
                'warnings': [
                    {'login': 'uid4@unit.test', 'code': 'not_found_in_bb'},
                ],
            },
            1,
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_admin_only.sql'],
            ),
            id='not in passport',
        ),
    ),
)
async def test_admin_bulk_add(
        taxi_callcenter_operators_web,
        request_json,
        response_status,
        expected_response,
        expected_stq_times_called,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_passport,
        mock_access_control_users,
        mock_telephony_api_full,
        stq,
        mock_set_status_cc_queues,
        mock_save_status,
        mock_system_info,
):
    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL,
        json=request_json,
        headers={'X-Ya-User-Ticket': 'ticket'},
    )
    assert response.status == response_status
    assert (
        stq.callcenter_operators_sync_roles.times_called
        == expected_stq_times_called
    )
    if response_status == 400:
        text_content = await response.text()
        assert text_content
    elif response_status == 200:
        content = await response.json()
        warning_logins = [
            warn['login'].split('@')[0]
            for warn in expected_response['warnings']
        ]
        expected_sec = []
        for (i, operator) in enumerate(request_json['operators']):
            if operator['uid'] not in warning_logins:
                expected_sec.append(i + 1)
        assert len(expected_sec) == expected_stq_times_called
        stq_calls = []
        for _ in range(expected_stq_times_called):
            stq_calls.append(stq.callcenter_operators_sync_roles.next_call())
        assert set(call['eta'] for call in stq_calls) == {
            datetime.datetime(2021, 3, 5, 12, 0, sec) for sec in expected_sec
        }
        assert {tuple(warn.items()) for warn in content['warnings']} == {
            tuple(warn.items()) for warn in expected_response['warnings']
        }
    else:
        content = await response.json()
        assert content == expected_response
