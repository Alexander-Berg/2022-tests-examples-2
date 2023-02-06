import pytest


async def test_bind_limit_exceed(taxi_eats_restapp_communications):
    response = await taxi_eats_restapp_communications.post(
        '/admin/communications/v1/telegram/bind',
        json={
            'places': [
                {
                    'place_id': 1,
                    'logins': [
                        'some_login1',
                        'some_login2',
                        'some_login3',
                        'some_login4',
                        'some_login5',
                        'some_login6',
                        'some_login7',
                        'some_login8',
                        'some_login9',
                        'some_login10',
                        'some_login11',
                    ],
                },
            ],
        },
    )
    assert response.status_code == 400


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_admin_telegram_bind.sql',),
)
async def test_bind(taxi_eats_restapp_communications, mockserver, pgsql):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/'
        + 'eats-catalog-storage/v1/places/retrieve-by-ids',
    )
    async def _catalog_handler(request):
        return {
            'places': [
                {
                    'id': 1,
                    'region': {
                        'id': 1,
                        'geobase_ids': [],
                        'time_zone': 'Europe/Moscow',
                    },
                    'revision_id': 1,
                    'updated_at': '2022-04-22T11:44:47.385057+00:00',
                },
                {
                    'id': 2,
                    'region': {
                        'id': 2,
                        'geobase_ids': [],
                        'time_zone': 'Australia/Tasmania',
                    },
                    'revision_id': 1,
                    'updated_at': '2022-04-22T11:44:47.385057+00:00',
                },
                {
                    'id': 3,
                    'region': {
                        'id': 3,
                        'geobase_ids': [],
                        'time_zone': 'Asia/Dushanbe',
                    },
                    'revision_id': 1,
                    'updated_at': '2022-04-22T11:44:47.385057+00:00',
                },
            ],
            'not_found_place_ids': [],
        }

    @mockserver.json_handler('/personal/v1/telegram_logins/bulk_store')
    async def _personal_handler(request):
        return {
            'items': [
                {'id': 'some_login1', 'value': '@tg_login_1'},
                {'id': 'some_login2', 'value': '@tg_login_2'},
                {'id': 'some_login3', 'value': '@tg_login_3'},
                {'id': 'some_login4', 'value': '@tg_login_4'},
                {'id': 'some_login5', 'value': '@tg_login_5'},
                {'id': 'some_login6', 'value': '@tg_login_6'},
                {'id': 'some_login7', 'value': '@tg_login_7'},
                {'id': 'some_login8', 'value': '@tg_login_8'},
                {'id': 'some_login9', 'value': '@tg_login_9'},
                {'id': 'some_login10', 'value': '@tg_login_10'},
            ],
        }

    @mockserver.json_handler('/personal/v1/telegram_logins/bulk_retrieve')
    async def _retrieve_handler(request):
        assert sorted(request.json['items'], key=lambda x: x['id']) == [
            {'id': 'some_login1'},
            {'id': 'some_login10'},
            {'id': 'some_login2'},
            {'id': 'some_login3'},
            {'id': 'some_login4'},
            {'id': 'some_login5'},
            {'id': 'some_login6'},
            {'id': 'some_login7'},
            {'id': 'some_login8'},
            {'id': 'some_login9'},
        ]
        return {
            'items': [
                {'id': 'some_login1', 'value': '@tg_login_1'},
                {'id': 'some_login2', 'value': '@tg_login_2'},
                {'id': 'some_login3', 'value': '@tg_login_3'},
                {'id': 'some_login4', 'value': '@tg_login_4'},
                {'id': 'some_login5', 'value': '@tg_login_5'},
                {'id': 'some_login6', 'value': '@tg_login_6'},
                {'id': 'some_login7', 'value': '@tg_login_7'},
                {'id': 'some_login8', 'value': '@tg_login_8'},
                {'id': 'some_login9', 'value': '@tg_login_9'},
                {'id': 'some_login10', 'value': '@tg_login_10'},
            ],
        }

    response = await taxi_eats_restapp_communications.post(
        '/admin/communications/v1/telegram/bind',
        json={
            'places': [
                {
                    'place_id': 1,
                    'logins': [
                        '@TG_LOGIN_1',
                        '@Tg_Login_2',
                        '@tg_login_3',
                        '@tg_login_4',
                        '@tg_login_5',
                        '@tg_login_6',
                        '@tg_login_7',
                        '@tg_login_8',
                        '@tg_login_9',
                    ],
                },
                {'place_id': 2, 'logins': ['@tg_login_10']},
                {'place_id': 3, 'logins': []},
            ],
        },
    )
    assert response.status_code == 204

    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        f"""SELECT * FROM eats_restapp_communications.places_tg_logins
        WHERE place_id = 1 AND deleted_at IS NULL""",
    )
    res = cursor.fetchall()
    assert len(res) == 9

    cursor.execute(
        f"""SELECT * FROM eats_restapp_communications.places_tg_logins
        WHERE place_id = 2 AND deleted_at IS NULL""",
    )
    res = cursor.fetchall()
    assert len(res) == 1

    cursor.execute(
        f"""SELECT * FROM eats_restapp_communications.places_tg_logins
        WHERE place_id = 3 AND deleted_at IS NULL""",
    )
    res = cursor.fetchall()
    assert not res

    cursor.execute(
        f"""SELECT place_id, is_active, timezone, to_send_at, sent_at
        FROM eats_restapp_communications.place_digest_send_schedule
        WHERE place_id = 1""",
    )
    res = cursor.fetchone()
    assert res[0] == 1
    assert res[1]
    assert res[2] == 'Europe/Moscow'
    assert res[3] is None
    assert res[4] is None

    cursor.execute(
        f"""SELECT place_id, is_active, timezone, to_send_at, sent_at FROM
        eats_restapp_communications.place_digest_send_schedule
        WHERE place_id = 2""",
    )
    res = cursor.fetchone()
    assert res[0] == 2
    assert res[1]
    assert res[2] == 'Australia/Tasmania'
    assert res[3] is None
    assert res[4] is None

    cursor.execute(
        f"""SELECT place_id, is_active, timezone, to_send_at, sent_at
        FROM eats_restapp_communications.place_digest_send_schedule
        WHERE place_id = 3""",
    )
    res = cursor.fetchone()
    assert res[0] == 3
    assert not res[1]
    assert res[2] == 'Asia/Dushanbe'
    assert res[3] is None
    assert res[4] is None
