import datetime
import uuid

import dateutil

SELECT_ALL_TAGS = """
SELECT
    *
FROM
    user_profiles.tags;
"""


async def test_ban_unban_idem(taxi_grocery_user_profiles, pgsql, mocked_time):
    yandex_uid = 'yandex_uid0'
    pkey = None

    cursor = pgsql['grocery_user_profiles'].cursor()

    async def _check(
            *,
            now,
            action,
            request,
            idempotency_token,
            yandex_login,
            reason,
            tag_info_len,
    ):
        headers = {
            'X-Idempotency-Token': idempotency_token,
            'X-Yandex-Login': yandex_login,
        }

        response = await taxi_grocery_user_profiles.post(
            f'/user-profiles/v1/admin/v1/user-{action}',
            headers=headers,
            json=request,
        )
        assert response.status_code == 200

        response = response.json()

        if action == 'ban':
            assert 'id' in response
            nonlocal pkey
            if pkey is None:
                pkey = response['id']
                try:
                    uuid.UUID(pkey)
                except ValueError:
                    assert False
            else:
                assert response['id'] == pkey
        elif action == 'unban':
            assert response == {}
        else:
            assert False

        cursor.execute(SELECT_ALL_TAGS)
        rows = list(cursor.fetchall())
        assert len(rows) == 1
        row = {
            description[0]: value
            for description, value in zip(cursor.description, rows[0])
        }
        tag_info = row.pop('tag_info')
        assert len(tag_info) == tag_info_len
        assert dateutil.parser.parse(tag_info[-1].pop('imposed_at')) == now
        assert tag_info[-1] == {
            'action': action,
            'reason': reason,
            'yandex_login': yandex_login,
            'idempotency_token': idempotency_token,
        }
        del row['created_at']  # can't handle properly
        del row['updated_at']  # can't handle properly
        assert row == {
            'id': pkey,
            'is_disabled': action == 'unban',
            'tag_name': 'ban',
            'yandex_uid': yandex_uid,
            'personal_phone_id': None,
            'appmetrica_device_id': None,
            'bound_session': None,
        }

    now = mocked_time.now().replace(tzinfo=datetime.timezone.utc)
    reason = 'a reason0'
    ban_request = {
        'personal_ids': {'yandex_uid': yandex_uid},
        'reason': reason,
    }

    for _ in range(2):  # check idempotency
        await _check(
            now=now,
            action='ban',
            request=ban_request,
            idempotency_token='idempotency_token0',
            yandex_login='yandex_login0',
            reason=reason,
            tag_info_len=1,
        )
        mocked_time.sleep(1)

    now = mocked_time.now().replace(tzinfo=datetime.timezone.utc)
    reason = 'a reason1'
    unban_request = {'id': pkey, 'reason': reason}

    for _ in range(2):  # check idempotency
        await _check(
            now=now,
            action='unban',
            request=unban_request,
            idempotency_token='idempotency_token1',
            yandex_login='yandex_login1',
            reason=reason,
            tag_info_len=2,
        )
        mocked_time.sleep(1)


async def test_banlist(taxi_grocery_user_profiles, mocked_time):
    yandex_login = 'yandex_login0'

    async def _ban(
            *,
            idempotency_token,
            reason,
            yandex_uid,
            personal_phone_id,
            appmetrica_device_id,
            bound_session,
    ):
        headers = {
            'X-Idempotency-Token': idempotency_token,
            'X-Yandex-Login': yandex_login,
        }

        personal_ids = {
            'yandex_uid': yandex_uid,
            'personal_phone_id': personal_phone_id,
            'appmetrica_device_id': appmetrica_device_id,
            'bound_session': bound_session,
        }
        ban_request = {'personal_ids': personal_ids, 'reason': reason}

        response = await taxi_grocery_user_profiles.post(
            '/user-profiles/v1/admin/v1/user-ban',
            headers=headers,
            json=ban_request,
        )
        assert response.status_code == 200

        return response.json()['id']

    pkeys = []
    personal_ids = [
        ('yandex_uid0', None, None, None),
        ('yandex_uid1', None, None, None),
        (None, 'personal_phone_id0', None, None),
        (None, 'personal_phone_id1', None, None),
        (None, None, 'appmetricadeviceid0', None),
        (None, None, 'appmetricadeviceid1', None),
        (None, None, None, 'bound_session0'),
        (None, None, None, 'bound_session1'),
    ]
    for (
            i,
            (
                yandex_uid,
                personal_phone_id,
                appmetrica_device_id,
                bound_session,
            ),
    ) in enumerate(personal_ids):
        reason = f'a reason{i}'
        pkey = await _ban(
            idempotency_token=f'idempotency_token{i}',
            reason=reason,
            yandex_uid=yandex_uid,
            personal_phone_id=personal_phone_id,
            appmetrica_device_id=appmetrica_device_id,
            bound_session=bound_session,
        )
        pkeys.append(pkey)

    imposed_at = mocked_time.now().replace(tzinfo=datetime.timezone.utc)

    async def _check(banlist_request, beg, end):
        idempotency_token = 'banlist_idem0'
        headers = {
            'X-Idempotency-Token': idempotency_token,
            'X-Yandex-Login': yandex_login,
        }

        response = await taxi_grocery_user_profiles.post(
            '/user-profiles/v1/admin/v1/user-banlist',
            headers=headers,
            json=banlist_request,
        )
        assert response.status_code == 200

        banlist = list(reversed(response.json()['banlist']))
        assert len(banlist) == end - beg
        for (
                i,
                user_ban_info,
                pkey,
                (
                    yandex_uid,
                    personal_phone_id,
                    appmetrica_device_id,
                    bound_session,
                ),
        ) in (
                zip(
                    range(beg, end),
                    banlist,
                    pkeys[beg:end],
                    personal_ids[beg:end],
                )
        ):
            assert user_ban_info['id'] == pkey
            assert user_ban_info['ban_history'][-1]['reason'] == f'a reason{i}'
            assert user_ban_info.get('is_disabled') == banlist_request.get(
                'is_disabled', False,
            )
            # created_at cannot be handled
            nonlocal imposed_at
            assert (
                dateutil.parser.parse(
                    user_ban_info['ban_history'][-1]['imposed_at'],
                )
                == imposed_at
            )
            pids = user_ban_info['personal_ids']
            assert pids.get('yandex_uid') == yandex_uid
            assert pids.get('personal_phone_id') == personal_phone_id
            assert pids.get('appmetrica_device_id') == appmetrica_device_id
            assert pids.get('bound_session') == bound_session

    personal_ids_filter = [
        'yandex_uid',
        'personal_phone_id',
        'appmetrica_device_id',
        'bound_session',
    ]
    banlist_request = {
        'cursor': {
            'count': 101325,
            'older_than': (
                imposed_at + datetime.timedelta(hours=24)
            ).isoformat(),
        },
        'personal_ids': {},
        'personal_ids_filter': personal_ids_filter,
    }
    await _check(banlist_request, 0, 8)

    for i, personal_id_kind in enumerate(personal_ids_filter):
        banlist_request['personal_ids_filter'] = [personal_id_kind]
        await _check(banlist_request, i * 2, (i + 1) * 2)

    del banlist_request['personal_ids_filter'][:]
    for (
            i,
            (
                yandex_uid,
                personal_phone_id,
                appmetrica_device_id,
                bound_session,
            ),
    ) in enumerate(personal_ids):
        banlist_request['personal_ids'] = {
            'yandex_uid': yandex_uid,
            'personal_phone_id': personal_phone_id,
            'appmetrica_device_id': appmetrica_device_id,
            'bound_session': bound_session,
        }
        await _check(banlist_request, i, i + 1)

    for i in range(4):
        idempotency_token = f'idem_unban{i}'
        headers = {
            'X-Idempotency-Token': idempotency_token,
            'X-Yandex-Login': yandex_login,
        }
        unban_request = {'id': pkeys[i], 'reason': f'a reason{i}'}
        response = await taxi_grocery_user_profiles.post(
            '/user-profiles/v1/admin/v1/user-unban',
            headers=headers,
            json=unban_request,
        )
        assert response.status_code == 200

    banlist_request['personal_ids'] = {}

    banlist_request['is_disabled'] = True
    await _check(banlist_request, 0, 4)
    banlist_request['is_disabled'] = False
    await _check(banlist_request, 4, 8)


async def test_ban_400(taxi_grocery_user_profiles):
    idempotency_token = 'idempotency_token0'
    yandex_login = 'yandex_login0'
    headers = {
        'X-Idempotency-Token': idempotency_token,
        'X-Yandex-Login': yandex_login,
    }

    yandex_uid = 'yandex_uid0'
    personal_phone_id = 'personal_phone_id0'
    appmetrica_device_id = 'appmetricadeviceid0'
    bound_session = 'bound_session0'

    reason = 'a reason0'

    personal_ids = {}
    ban_request = {'personal_ids': personal_ids, 'reason': reason}

    response = await taxi_grocery_user_profiles.post(
        '/user-profiles/v1/admin/v1/user-ban',
        headers=headers,
        json=ban_request,
    )
    assert response.status_code == 400

    personal_ids = {
        'yandex_uid': yandex_uid,
        'personal_phone_id': personal_phone_id,
        'appmetrica_device_id': appmetrica_device_id,
        'bound_session': bound_session,
    }
    response = await taxi_grocery_user_profiles.post(
        '/user-profiles/v1/admin/v1/user-ban',
        headers=headers,
        json=ban_request,
    )
    assert response.status_code == 400


async def test_ban_409(taxi_grocery_user_profiles):
    headers = {
        'X-Idempotency-Token': 'idempotency_token0',
        'X-Yandex-Login': 'yandex_login0',
    }
    ban_request = {
        'personal_ids': {'yandex_uid': 'yandex_uid0'},
        'reason': 'a reason0',
    }

    response = await taxi_grocery_user_profiles.post(
        '/user-profiles/v1/admin/v1/user-ban',
        headers=headers,
        json=ban_request,
    )
    assert response.status_code == 200

    headers['X-Idempotency-Token'] = 'idempotency_token1'
    response = await taxi_grocery_user_profiles.post(
        '/user-profiles/v1/admin/v1/user-ban',
        headers=headers,
        json=ban_request,
    )
    assert response.status_code == 409


async def test_ban_unban_series(taxi_grocery_user_profiles):
    for i in range(0, 4, 2):
        headers = {
            'X-Yandex-Login': f'yandex_login{i}',
            'X-Idempotency-Token': f'idempotency_token{i}',
        }
        ban_request = {
            'personal_ids': {'yandex_uid': f'yandex_uid{i}'},
            'reason': f'a ban reason{i}',
        }

        response = await taxi_grocery_user_profiles.post(
            '/user-profiles/v1/admin/v1/user-ban',
            headers=headers,
            json=ban_request,
        )
        assert response.status_code == 200

        headers = {
            'X-Yandex-Login': f'yandex_login{i + 1}',
            'X-Idempotency-Token': f'idempotency_token{i + 1}',
        }
        unban_request = {
            'id': response.json()['id'],
            'reason': f'an unban reason{i + 1}',
        }

        response = await taxi_grocery_user_profiles.post(
            '/user-profiles/v1/admin/v1/user-unban',
            headers=headers,
            json=unban_request,
        )
        assert response.status_code == 200


async def test_unban_40x(taxi_grocery_user_profiles):
    yandex_login = 'yandex_login0'

    idempotency_token = 'idempotency_token0'
    headers = {
        'X-Idempotency-Token': idempotency_token,
        'X-Yandex-Login': yandex_login,
    }

    yandex_uid = 'yandex_uid0'
    reason = 'a reason0'
    personal_ids = {'yandex_uid': yandex_uid}
    ban_request = {'personal_ids': personal_ids, 'reason': reason}

    response = await taxi_grocery_user_profiles.post(
        '/user-profiles/v1/admin/v1/user-ban',
        headers=headers,
        json=ban_request,
    )
    assert response.status_code == 200
    pkey = response.json()['id']

    unban_request = {'id': str(uuid.uuid4()), 'reason': 'a reason0'}

    headers['X-Idempotency-Token'] = 'idempotency_token1'
    response = await taxi_grocery_user_profiles.post(
        '/user-profiles/v1/admin/v1/user-unban',
        headers=headers,
        json=unban_request,
    )
    assert response.status_code == 404

    response = await taxi_grocery_user_profiles.post(
        '/user-profiles/v1/admin/v1/user-unban',
        headers={},
        json=unban_request,
    )
    assert response.status_code == 400

    headers['X-Idempotency-Token'] = 'idempotency_token2'
    unban_request['id'] = pkey
    response = await taxi_grocery_user_profiles.post(
        '/user-profiles/v1/admin/v1/user-unban',
        headers=headers,
        json=unban_request,
    )
    assert response.status_code == 200

    headers['X-Idempotency-Token'] = 'idempotency_token3'
    response = await taxi_grocery_user_profiles.post(
        '/user-profiles/v1/admin/v1/user-unban',
        headers=headers,
        json=unban_request,
    )
    assert response.status_code == 409


async def test_banlist_40x(taxi_grocery_user_profiles, now):
    yandex_login = 'yandex_login0'

    idempotency_token = 'idempotency_token0'
    headers = {
        'X-Idempotency-Token': idempotency_token,
        'X-Yandex-Login': yandex_login,
    }

    wrong_personal_id = 'wrong'
    banlist_request = {
        'cursor': {'count': 1, 'older_than': now.isoformat()},
        'personal_ids': {},
        'personal_ids_filter': [wrong_personal_id],
    }

    response = await taxi_grocery_user_profiles.post(
        '/user-profiles/v1/admin/v1/user-banlist',
        headers=headers,
        json=banlist_request,
    )
    assert response.status_code == 400
