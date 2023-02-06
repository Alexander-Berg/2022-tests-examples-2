import datetime

import pytest

NOW = datetime.datetime(2019, 4, 9, 12, 35, 55, tzinfo=datetime.timezone.utc)
ONE_DAY_AGO = NOW - datetime.timedelta(days=1)
ONE_YEAR_AGO = NOW - datetime.timedelta(days=365)


# pylint: disable=too-many-arguments
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    DRIVER_CARD_CLAIMS_THEMES=['theme_1', 'theme_2'], TVM_ENABLED=True,
)
@pytest.mark.parametrize(
    [
        'identification',
        'chatterbox_tickets',
        'expected_result',
        'chatterbox_called_params',
    ],
    [
        (
            'itsdriverlicence',
            [
                {
                    'id': '1',
                    'theme_name': 'theme_1',
                    'created': ONE_DAY_AGO.isoformat(),
                    'chat_type': 'driver',
                },
                {
                    'id': '2',
                    'theme_name': 'theme_2',
                    'created': ONE_YEAR_AGO.isoformat(),
                    'chat_type': 'driver',
                },
                {
                    'id': '3',
                    'theme_name': 'theme_3',
                    'created': ONE_DAY_AGO.isoformat(),
                    'chat_type': 'client',
                },
            ],
            {
                'claims': [
                    {
                        'chatterbox_id': '1',
                        'theme_name': 'theme_1',
                        'created': ONE_DAY_AGO.isoformat(),
                    },
                    {
                        'chatterbox_id': '2',
                        'theme_name': 'theme_2',
                        'created': ONE_YEAR_AGO.isoformat(),
                    },
                ],
                'appeals': {'total_count': 2, 'monthly_count': 1},
            },
            {
                'created_from': '2018-06-13',
                'driver_license': 'itsdriverlicence',
            },
        ),
        (
            'itsdriverlicence',
            [
                {
                    'id': '1',
                    'theme_name': 'theme_3',
                    'created': ONE_DAY_AGO.isoformat(),
                    'chat_type': 'client',
                },
                {
                    'id': '2',
                    'theme_name': 'theme_4',
                    'created': ONE_YEAR_AGO.isoformat(),
                    'chat_type': 'driver',
                },
            ],
            {'claims': [], 'appeals': {'total_count': 1, 'monthly_count': 0}},
            {
                'created_from': '2018-06-13',
                'driver_license': 'itsdriverlicence',
            },
        ),
    ],
)
async def test_tickets(
        mock_personal_single_response,
        support_info_client,
        identification,
        chatterbox_tickets,
        expected_result,
        chatterbox_called_params,
        mock_chatterbox_search,
        mock_zendesk_search,
        mock_tvm_get_service_name,
):

    mock_chatterbox_search.set_response({'tasks': chatterbox_tickets})
    mock_personal_single_response(identification)
    response = await support_info_client.get(
        '/v1/tickets/driver/{}'.format(identification),
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'X-Ya-Service-Ticket': 'TVM_key',
        },
    )
    assert response.status == 200
    assert await response.json() == expected_result

    chat_called = mock_chatterbox_search.call['kwargs']
    assert chat_called['data'] == chatterbox_called_params


@pytest.mark.config(TVM_ENABLED=True)
async def test_not_authorized(support_info_client):
    response = await support_info_client.get(
        '/v1/tickets/driver/vasya',
        headers={'Content-Type': 'application/json; charset=utf-8'},
    )
    assert response.status == 403
    # utils.reformat_response made it
    assert await response.json() == {
        'error': (
            '{"status": "error", "message": "TVM header missing", '
            '"code": "tvm-auth-error"}'
        ),
        'status': 'error',
    }
