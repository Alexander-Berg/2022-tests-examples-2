import pytest


PARTNER_ID = 42


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_get_telegram_logins.sql',),
)
async def test_get_telegram_logins_with_authorizer_error(
        taxi_eats_restapp_communications, mockserver,
):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    async def _handler(_):
        return mockserver.make_response(status=403)

    response = await taxi_eats_restapp_communications.post(
        '/4.0/restapp-front/communications/v1/telegram/list',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json={'place_ids': [1, 2, 3]},
    )

    assert response.status_code == 403


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_get_telegram_logins.sql',),
)
@pytest.mark.config(EATS_RESTAPP_COMMUNICATIONS_TELEGRAM_LOGINS_LIMIT=100)
@pytest.mark.parametrize(
    'resolved_logins',
    [
        pytest.param(
            True,
            marks=(
                pytest.mark.config(EATS_RESTAPP_TG_BOT_ENABLE_PERSONAL=False)
            ),
            id='send logins resolved in personal',
        ),
        pytest.param(
            False,
            marks=(
                pytest.mark.config(EATS_RESTAPP_TG_BOT_ENABLE_PERSONAL=True)
            ),
            id='send login ids',
        ),
    ],
)
async def test_get_telegram_logins(
        taxi_eats_restapp_communications, mockserver, resolved_logins,
):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    async def _handler(_):
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/personal/v1/telegram_logins/bulk_retrieve')
    async def _personal_handler(request):
        assert sorted(request.json['items'], key=lambda x: x['id']) == [
            {'id': 'login_id_1'},
            {'id': 'login_id_2'},
            {'id': 'login_id_3'},
            {'id': 'login_id_4'},
        ]
        return {
            'items': [
                {'id': 'login_id_1', 'value': '@tg_login_1'},
                {'id': 'login_id_2', 'value': '@tg_login_2'},
                {'id': 'login_id_3', 'value': '@tg_login_3'},
                {'id': 'login_id_4', 'value': '@tg_login_4'},
            ],
        }

    @mockserver.json_handler('/eats-restapp-tg-bot/v1/get-available-logins')
    async def _bot_handler(request):
        if resolved_logins:
            assert sorted(request.json['logins']) == [
                'tg_login_1',
                'tg_login_2',
                'tg_login_3',
                'tg_login_4',
            ]
            return {
                'logins': [
                    {'available': True, 'login': 'tg_login_1'},
                    {'available': True, 'login': 'tg_login_2'},
                    {'available': False, 'login': 'tg_login_4'},
                ],
            }
        else:
            assert sorted(request.json['logins']) == [
                'login_id_1',
                'login_id_2',
                'login_id_3',
                'login_id_4',
            ]
            return {
                'logins': [
                    {'available': True, 'login': 'login_id_1'},
                    {'available': True, 'login': 'login_id_2'},
                    {'available': False, 'login': 'login_id_4'},
                ],
            }

    response = await taxi_eats_restapp_communications.post(
        '/4.0/restapp-front/communications/v1/telegram/list',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json={'place_ids': [1, 2, 3, 4]},
    )

    assert response.status_code == 200
    body = response.json()
    payload = [
        {
            'logins': sorted(item['logins'], key=lambda x: x['login']),
            'place_id': item['place_id'],
        }
        for item in body['payload']
    ]
    assert sorted(payload, key=lambda x: x['place_id']) == [
        {
            'logins': [
                {'is_bot_active': True, 'login': 'tg_login_1'},
                {'is_bot_active': False, 'login': 'tg_login_4'},
            ],
            'place_id': 1,
        },
        {
            'logins': [
                {'is_bot_active': True, 'login': 'tg_login_1'},
                {'is_bot_active': True, 'login': 'tg_login_2'},
            ],
            'place_id': 2,
        },
        {
            'logins': [
                {'is_bot_active': True, 'login': 'tg_login_2'},
                {'is_bot_active': False, 'login': 'tg_login_3'},
                {'is_bot_active': False, 'login': 'tg_login_4'},
            ],
            'place_id': 3,
        },
        {'logins': [], 'place_id': 4},
    ]
    assert body['meta'] == {'logins_limit': 100}
