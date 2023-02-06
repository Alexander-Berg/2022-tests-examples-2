import pytest

MOCK_PHONE_ID = 'xxxxx'


@pytest.mark.parametrize(
    ['client_id', 'url_args', 'expected_result'],
    [
        (
            'client1',
            {'phone': '+79263452214'},
            {
                'history': [
                    {
                        'performer': 'somebody',
                        'updated': '2019-10-21T17:12:42.128000+00:00',
                        'action': 'PUT',
                        'ip': '2a02:6b8:0:421:19fc:9534:6bc8:ef0d',
                        'doc': {
                            'department_id': (
                                '3d7be98faf1544479ef3c586a7fcac5e'
                            ),
                            'email_id': '',
                            'fullname': 'Антон',
                            'is_deleted': False,
                            'is_active': True,
                            'phone_id': 'xxxxx',
                            'role': {
                                'role_id': 'e035dd56774b43faa6ffc6fe57434ec4',
                            },
                            'limits': [
                                {
                                    'limit_id': (
                                        'bf2bab11ba9042438fec23ec5aa0fc22'
                                    ),
                                    'service': 'taxi',
                                },
                                {
                                    'limit_id': (
                                        '5cba9a2321684c0c931b33f71358b070'
                                    ),
                                    'service': 'eats2',
                                },
                            ],
                            'services': {
                                'eats': {
                                    'is_active': False,
                                    'send_activation_sms': True,
                                },
                                'taxi': {'send_activation_sms': False},
                            },
                            'cost_center': '',
                            'cost_centers': {
                                'required': False,
                                'format': 'text',
                                'values': [],
                            },
                            'nickname': '',
                        },
                    },
                    {
                        'performer': 'login',
                        'updated': '2019-10-21T17:12:42.128000+00:00',
                        'action': 'PUT',
                        'ip': None,
                        'doc': {
                            'department_id': (
                                '3d7be98faf1544479ef3c586a7fcac5e'
                            ),
                            'email_id': '',
                            'fullname': 'Антон',
                            'is_deleted': False,
                            'is_active': True,
                            'phone_id': 'xxxxx',
                            'role': {
                                'role_id': 'e035dd56774b43faa6ffc6fe57434ec4',
                            },
                            'limits': [
                                {
                                    'limit_id': (
                                        'bf2bab11ba9042438fec23ec5aa0fc22'
                                    ),
                                    'service': 'taxi',
                                },
                                {
                                    'limit_id': (
                                        '5cba9a2321684c0c931b33f71358b070'
                                    ),
                                    'service': 'eats2',
                                },
                            ],
                            'services': {
                                'eats': {
                                    'is_active': False,
                                    'send_activation_sms': True,
                                },
                                'taxi': {'send_activation_sms': False},
                            },
                            'cost_center': '',
                            'cost_centers': {
                                'required': False,
                                'format': 'text',
                                'values': [],
                            },
                            'nickname': '',
                        },
                    },
                ],
            },
        ),
    ],
)
async def test_get_history_handler(
        taxi_corp_admin_client, client_id, url_args, expected_result, patch,
):
    from test_taxi_corp_admin.static.test_history import yt_response

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': MOCK_PHONE_ID}

    @patch('yt.wrapper.YtClient.select_rows')
    def _select_yt_rows(*args, **kwargs):
        return yt_response.YT_HISTORY_ROWS

    @patch('taxi.clients.passport.PassportClient.get_info_by_uid')
    async def _get_uid(*args, **kwargs):
        return {'uid': '4014756266', 'login': 'somebody'}

    response = await taxi_corp_admin_client.get(
        f'/v1/clients/{client_id}/history', params=url_args,
    )

    assert response.status == 200
    assert await response.json() == expected_result
