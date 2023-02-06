import pytest


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_admin_telegram_list.sql',),
)
@pytest.mark.config(EATS_RESTAPP_COMMUNICATIONS_TELEGRAM_LOGINS_LIMIT=100)
async def test_admin_telegram_list(
        taxi_eats_restapp_communications, mockserver,
):
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

    response = await taxi_eats_restapp_communications.post(
        '/admin/communications/v1/telegram/list',
        json={'place_ids': [1, 2, 3, 4]},
    )

    assert response.status_code == 200
    body = response.json()
    payload = [
        {'logins': sorted(item['logins']), 'place_id': item['place_id']}
        for item in body['payload']
    ]
    assert sorted(payload, key=lambda x: x['place_id']) == [
        {'logins': ['tg_login_1', 'tg_login_4'], 'place_id': 1},
        {'logins': ['tg_login_1', 'tg_login_2'], 'place_id': 2},
        {'logins': ['tg_login_2', 'tg_login_3', 'tg_login_4'], 'place_id': 3},
        {'logins': [], 'place_id': 4},
    ]
    assert body['meta'] == {'logins_limit': 100}
