# pylint: disable=redefined-outer-name
import pytest


BASE_SPENDING_RESPONSE = {
    'items': {
        'test_user_1': {
            'limit3_2_eats2': {'spent': '200'},
            'limit3_2_tanker': {'spent': '200'},
            'limit3_2_with_users': {'spent': '200'},
            'drive_limit': {'spent': '182.00'},
        },
        'test_user_3': {'limit3_2_with_users': {'spent': '0'}},
    },
}


@pytest.mark.parametrize(
    [
        'passport_mock',
        'corp_users_response',
        'expected_code',
        'expected_response',
    ],
    [
        pytest.param(
            'client1',
            BASE_SPENDING_RESPONSE,
            200,
            BASE_SPENDING_RESPONSE,
            id='success-path',
        ),
        pytest.param(
            'client1',
            {
                'message': 'Not found',
                'code': 'NOT_FOUND',
                'reason': 'User not found',
            },
            404,
            {
                'message': 'Not found',
                'code': 'NOT_FOUND',
                'reason': 'User not found',
            },
            id='one-user-not-found',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_get_user_spending_proxy(
        taxi_corp_real_auth_client,
        mock_corp_users,
        passport_mock,
        corp_users_response,
        expected_code,
        expected_response,
):
    mock_corp_users.data.get_users_spending_response = corp_users_response
    mock_corp_users.data.get_users_spending_code = expected_code

    response = await taxi_corp_real_auth_client.post(
        '/2.0/users-spending',
        json={'user_ids': ['test_user_1', 'test_user_3']},
    )
    assert response.status == expected_code
    response_data = await response.json()
    assert response_data == expected_response
