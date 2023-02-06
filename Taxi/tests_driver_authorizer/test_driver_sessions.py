import json

import pytest

from testsuite.utils import ordered_object


@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pzxcvb:Sasdfg',
        {'client_id': 'taximeter', 'driver_profile_id': '1234'},
    ],
)
@pytest.mark.redis_store(
    ['zadd', 'DriverSessionsTtl{a}', {'DriverSession:Pzxcvb:Sasdfg': 1e15}],
)
@pytest.mark.redis_store(['hset', 'Driver:Pzxcvb:U1234', 'Session', 'asdfg'])
async def test_auth_ok(taxi_driver_authorizer):
    headers = {'X-Driver-Session': 'asdfg'}

    data = {'client_id': 'taximeter', 'park_id': 'zxcvb', 'ttl': 4444}

    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {
        'client_id': 'taximeter',
        'uuid': '1234',
        'driver_app_profile_id': '1234',
        'ttl': 4444,
    }

    # wrong client_id
    data['client_id'] = 'uberdriver'
    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 401
    assert response.json() == {
        'code': '401',
        'message': 'authorization failed',
    }


@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pzxcvb:Sasdfg',
        {
            'client_id': 'taximeter',
            'driver_profile_id': '1234',
            'yandex_uid': '111',
        },
    ],
)
@pytest.mark.redis_store(
    ['zadd', 'DriverSessionsTtl{a}', {'DriverSession:Pzxcvb:Sasdfg': 1e15}],
)
@pytest.mark.redis_store(['hset', 'Driver:Pzxcvb:U1234', 'Session', 'asdfg'])
async def test_auth_ok_passport(taxi_driver_authorizer, redis_store):
    headers = {'X-Driver-Session': 'asdfg'}

    data = {'client_id': 'taximeter', 'park_id': 'zxcvb', 'ttl': 4444}

    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {
        'client_id': 'taximeter',
        'uuid': '1234',
        'driver_app_profile_id': '1234',
        'ttl': 4444,
        'yandex_uid': '111',
    }

    assert redis_store.type('DriverSession:Pzxcvb:Sasdfg') == b'hash'
    assert (
        redis_store.hget('DriverSession:Pzxcvb:Sasdfg', 'client_id')
        == b'taximeter'
    )
    assert (
        redis_store.hget('DriverSession:Pzxcvb:Sasdfg', 'driver_profile_id')
        == b'1234'
    )
    assert (
        redis_store.hget('DriverSession:Pzxcvb:Sasdfg', 'yandex_uid') == b'111'
    )

    delete_params = {
        'client_id': 'taximeter',
        'park_id': 'zxcvb',
        'uuid': '1234',
        'driver_app_profile_id': '1234',
    }
    response = await taxi_driver_authorizer.delete(
        'driver/sessions', params=delete_params,
    )
    assert response.status_code == 200

    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 401

    assert redis_store.type('DriverSession:Pzxcvb:Sasdfg') == b'none'


async def _make_driver_sessions_check_request(
        taxi_driver_authorizer, client_id, park_id, session,
):
    headers = {'X-Driver-Session': session}

    data = {'client_id': client_id, 'park_id': park_id, 'ttl': 4444}

    return await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data),
    )


async def test_auth_bad(taxi_driver_authorizer):
    headers = {'X-Driver-Session': '1'}

    data = {'client_id': 'taximeter', 'park_id': '1'}

    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 401
    assert response.json()['message'] == 'authorization failed'


@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pzxcvb:Sasdfg',
        {'client_id': 'taximeter', 'driver_profile_id': '1234'},
    ],
)
@pytest.mark.redis_store(
    ['zadd', 'DriverSessionsTtl{a}', {'DriverSession:Pzxcvb:Sasdfg': 1e15}],
)
@pytest.mark.redis_store(['hset', 'Driver:Pzxcvb:U1234', 'Session', 'asdfg'])
async def test_auth_bad_session(taxi_driver_authorizer):
    headers = {'X-Driver-Session': 'asdxx'}

    data = {'client_id': 'taximeter', 'park_id': 'zxcvb', 'ttl': 4444}

    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 401
    assert response.json()['message'] == 'authorization failed'


@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pzxcvb:Sasdfg',
        {'client_id': 'taximeter', 'driver_profile_id': '1234'},
    ],
)
@pytest.mark.redis_store(
    ['zadd', 'DriverSessionsTtl{a}', {'DriverSession:Pzxcvb:Sasdfg': 1e15}],
)
@pytest.mark.redis_store(['hset', 'Driver:Pzxcvb:U1234', 'Session', 'asdfg'])
async def test_auth_bad_db(taxi_driver_authorizer):
    headers = {'X-Driver-Session': 'asdfg'}

    data = {'client_id': 'taximeter', 'park_id': 'zxcxx', 'ttl': 4444}

    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 401
    assert response.json()['message'] == 'authorization failed'


async def delete_session(
        taxi_driver_authorizer,
        client_id,
        park_id,
        uuid,
        driver_app_profile_id,
):
    params = {'client_id': client_id, 'park_id': park_id, 'uuid': uuid}
    if driver_app_profile_id is not None:
        params.update({'driver_app_profile_id': driver_app_profile_id})

    return await taxi_driver_authorizer.delete(
        'driver/sessions', params=params,
    )


async def test_driver_sessions_put(taxi_driver_authorizer, put_session):
    response = await put_session(
        client_id='taximeter',
        park_id='zxcvb123',
        uuid='iouylkjh456',
        driver_app_profile_id=None,
        ttl=5555,
    )
    assert response.status_code == 200
    assert response.json() == {'ttl': 5555}

    session = response.headers.get('X-Driver-Session')
    assert session is not None


async def test_driver_sessions_put_passport(
        taxi_driver_authorizer, put_session,
):
    park_id = 'zxcvb123'
    response = await put_session(
        client_id='taximeter',
        park_id=park_id,
        uuid='iouylkjh456',
        driver_app_profile_id=None,
        ttl=5555,
        yandex_uid='111',
    )
    assert response.status_code == 200
    assert response.json() == {'ttl': 5555}

    session = response.headers.get('X-Driver-Session')
    assert session is not None

    headers = {'X-Driver-Session': session}
    data = {'client_id': 'taximeter', 'park_id': park_id}
    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json()['yandex_uid'] == '111'


async def test_driver_sessions_put_non_taximeter(
        taxi_driver_authorizer, put_session,
):
    response = await put_session(
        client_id='non_taximeter',
        park_id='zxcvb123',
        uuid='iouylkjh456',
        driver_app_profile_id=None,
        ttl=5555,
    )
    assert response.status_code == 400


async def test_auth_put_check(taxi_driver_authorizer, put_session):
    response = await put_session(
        client_id='taximeter',
        park_id='zxcvb123',
        uuid='iouylkjh456',
        driver_app_profile_id=None,
        ttl=5555,
    )
    session = response.headers.get('X-Driver-Session')
    assert response.status_code == 200
    assert response.json() == {'ttl': 5555}
    assert session is not None

    headers = {'X-Driver-Session': session}

    data = {'client_id': 'taximeter', 'park_id': 'zxcvb123', 'ttl': 4444}

    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {
        'client_id': 'taximeter',
        'uuid': 'iouylkjh456',
        'driver_app_profile_id': 'iouylkjh456',
        'ttl': 4444,
    }


async def test_auth_put_check_driver_app_profile_id(
        taxi_driver_authorizer, put_session,
):
    response = await put_session(
        client_id='taximeter',
        park_id='zxcvb123',
        uuid='iouylkjh456',
        driver_app_profile_id='kjhgfd',
        ttl=5555,
    )
    session = response.headers.get('X-Driver-Session')
    assert response.status_code == 200
    assert response.json() == {'ttl': 5555}
    assert session is not None

    headers = {'X-Driver-Session': session}

    data = {'client_id': 'taximeter', 'park_id': 'zxcvb123', 'ttl': 4444}

    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {
        'client_id': 'taximeter',
        'uuid': 'iouylkjh456',
        'driver_app_profile_id': 'kjhgfd',
        'ttl': 4444,
    }


async def test_auth_put_check_eats_courier_id(
        taxi_driver_authorizer, put_session,
):
    response = await put_session(
        client_id='taximeter',
        park_id='zxcvb123',
        uuid='iouylkjh456',
        driver_app_profile_id=None,
        eats_courier_id='1122',
        ttl=5555,
    )
    session = response.headers.get('X-Driver-Session')
    assert response.status_code == 200
    assert response.json() == {'ttl': 5555}
    assert session is not None

    headers = {'X-Driver-Session': session}

    data = {'client_id': 'taximeter', 'park_id': 'zxcvb123', 'ttl': 4444}

    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {
        'client_id': 'taximeter',
        'uuid': 'iouylkjh456',
        'driver_app_profile_id': 'iouylkjh456',
        'eats_courier_id': '1122',
        'ttl': 4444,
    }


@pytest.mark.config(DRIVER_SESSIONS_PROLONG_HALF_EXPIRED=True)
async def test_auth_put_check_half_expired(
        taxi_driver_authorizer, put_session,
):
    response = await put_session(
        client_id='taximeter',
        park_id='zxcvb123',
        uuid='iouylkjh456',
        driver_app_profile_id=None,
        ttl=1000,
    )
    session = response.headers.get('X-Driver-Session')
    assert response.status_code == 200
    assert response.json() == {'ttl': 1000}
    assert session is not None

    headers = {'X-Driver-Session': session}

    data1 = {'client_id': 'taximeter', 'park_id': 'zxcvb123', 'ttl': 1777}

    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data1),
    )
    assert response.status_code == 200
    assert response.json()['uuid'] == 'iouylkjh456'
    assert response.json()['ttl'] <= 1000
    assert response.json()['client_id'] == 'taximeter'

    data2 = {'client_id': 'taximeter', 'park_id': 'zxcvb123', 'ttl': 1789}

    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data2),
    )
    assert response.status_code == 200
    assert response.json()['uuid'] == 'iouylkjh456'
    assert response.json()['ttl'] <= 1000
    assert response.json()['client_id'] == 'taximeter'

    data3 = {'client_id': 'taximeter', 'park_id': 'zxcvb123', 'ttl': 2200}

    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data3),
    )
    assert response.status_code == 200
    assert response.json() == {
        'client_id': 'taximeter',
        'uuid': 'iouylkjh456',
        'driver_app_profile_id': 'iouylkjh456',
        'ttl': 2200,
    }


async def test_auth_put2(taxi_driver_authorizer, put_session):
    response = await put_session(
        client_id='taximeter',
        park_id='zxcvb123',
        uuid='iouylkjh456',
        driver_app_profile_id=None,
        ttl=5555,
    )
    session = response.headers.get('X-Driver-Session')
    assert response.status_code == 200
    assert response.json() == {'ttl': 5555}
    assert session is not None

    response2 = await put_session(
        client_id='taximeter',
        park_id='zxcvb123',
        uuid='iouylkjh456',
        driver_app_profile_id=None,
        ttl=5555,
    )
    session2 = response2.headers.get('X-Driver-Session')
    assert response2.status_code == 200
    assert response2.json() == {'ttl': 5555}
    assert session2 == session


async def test_auth_put_check_put(taxi_driver_authorizer, put_session):
    response = await put_session(
        client_id='taximeter',
        park_id='zxcvb123',
        uuid='iouylkjh456',
        driver_app_profile_id=None,
        ttl=5555,
    )
    session = response.headers.get('X-Driver-Session')
    assert response.status_code == 200
    assert response.json() == {'ttl': 5555}
    assert session is not None

    headers = {'X-Driver-Session': session}
    data = {'client_id': 'taximeter', 'park_id': 'zxcvb123', 'ttl': 4444}
    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {
        'client_id': 'taximeter',
        'uuid': 'iouylkjh456',
        'driver_app_profile_id': 'iouylkjh456',
        'ttl': 4444,
    }

    response2 = await put_session(
        client_id='taximeter',
        park_id='zxcvb123',
        uuid='iouylkjh456',
        driver_app_profile_id=None,
        ttl=4444,
    )
    session2 = response2.headers.get('X-Driver-Session')
    assert response2.status_code == 200
    assert response2.json() == {'ttl': 4444}
    assert session2 == session


async def _test_auth_put_get_client_id(
        taxi_driver_authorizer, client_id, park_id, uuid,
):
    params = {'client_id': client_id, 'park_id': park_id, 'uuid': uuid}

    data = {'ttl': 5555}

    response_put = await taxi_driver_authorizer.put(
        'driver/sessions', params=params, data=json.dumps(data),
    )
    assert response_put.status_code == 200
    assert response_put.json() == {'ttl': 5555}
    session_put = response_put.headers.get('X-Driver-Session')
    assert session_put is not None

    response_get = await taxi_driver_authorizer.get(
        'driver/sessions', params=params,
    )
    assert response_get.status_code == 200
    session_get = response_get.headers.get('X-Driver-Session')
    assert session_get == session_put


async def test_auth_put_get(taxi_driver_authorizer):
    await _test_auth_put_get_client_id(
        taxi_driver_authorizer, 'taximeter', 'zxcvb123', 'iouylkjh456',
    )
    await _test_auth_put_get_client_id(
        taxi_driver_authorizer, 'uberdriver', 'zxcvb1234', 'iouylkjh4567',
    )
    await _test_auth_put_get_client_id(
        taxi_driver_authorizer, 'vezet', 'zxcvb1234', 'iouylkjh4569',
    )


async def test_auth_put_check_incorrect_session(
        taxi_driver_authorizer, put_session,
):
    response = await put_session(
        client_id='taximeter',
        park_id='zxcvb123',
        uuid='iouylkjh456',
        driver_app_profile_id=None,
        ttl=5555,
    )
    session = response.headers.get('X-Driver-Session')
    assert response.status_code == 200
    assert response.json() == {'ttl': 5555}
    assert session is not None

    headers = {'X-Driver-Session': session + 'x'}

    data = {'client_id': 'taximeter', 'park_id': 'zxcvb123', 'ttl': 4444}

    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 401
    assert response.json()['message'] == 'authorization failed'


async def test_expired(taxi_driver_authorizer, put_session):
    for i in range(6):
        response = await put_session(
            client_id='uberdriver'
            if i == 1
            else 'vezet'
            if i == 2
            else 'taximeter',
            park_id='zxcvbzz' + str(i),
            uuid='iouylkjhii' + str(i),
            driver_app_profile_id=None if i != 1 else 'oiuas1',
            ttl=6000 + i * 100,
        )
        session = response.headers.get('X-Driver-Session')
        if i == 0:
            session0 = session
        assert response.status_code == 200
        assert response.json() == {'ttl': 6000 + i * 100}
        assert session is not None

    limit = 2

    data_expired_req = {
        'range': {
            'newer_than': '2000-01-01T01:01:01+0300',
            'older_than': '2222-01-01T01:01:01+0300',
            'limit': limit,
        },
    }

    response = await taxi_driver_authorizer.post(
        'driver/sessions/expired', data=json.dumps(data_expired_req),
    )
    assert response.status_code == 200
    expired_sessions = response.json()
    assert len(expired_sessions['expired_sessions']) == limit
    for i in range(limit):
        expired_sessions['expired_sessions'][i]['expired_at'] = '***'
    ordered_object.assert_eq(
        expired_sessions,
        {
            'expired_sessions': [
                {
                    'client_id': 'taximeter',
                    'expired_at': '***',
                    'park_id': 'zxcvbzz0',
                    'uuid': 'iouylkjhii0',
                    'driver_app_profile_id': 'iouylkjhii0',
                },
                {
                    'client_id': 'uberdriver',
                    'expired_at': '***',
                    'park_id': 'zxcvbzz1',
                    'uuid': 'iouylkjhii1',
                    'driver_app_profile_id': 'oiuas1',
                },
            ],
        },
        ['expired_sessions'],
    )

    headers = {'X-Driver-Session': session0}

    data = {'client_id': 'taximeter', 'park_id': 'zxcvbzz0', 'ttl': 4444}

    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {
        'client_id': 'taximeter',
        'uuid': 'iouylkjhii0',
        'driver_app_profile_id': 'iouylkjhii0',
        'ttl': 4444,
    }

    delete_response = await delete_session(
        taxi_driver_authorizer,
        client_id='taximeter',
        park_id='zxcvbzz0',
        uuid='iouylkjhii0',
        driver_app_profile_id=None,
    )
    assert delete_response.status_code == 200

    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 401

    response = await taxi_driver_authorizer.post(
        'driver/sessions/expired', data=json.dumps(data_expired_req),
    )
    assert response.status_code == 200
    expired_sessions = response.json()
    assert len(expired_sessions['expired_sessions']) == limit
    for i in range(limit):
        expired_sessions['expired_sessions'][i]['expired_at'] = '***'
    ordered_object.assert_eq(
        expired_sessions,
        {
            'expired_sessions': [
                {
                    'client_id': 'uberdriver',
                    'expired_at': '***',
                    'park_id': 'zxcvbzz1',
                    'uuid': 'iouylkjhii1',
                    'driver_app_profile_id': 'oiuas1',
                },
                {
                    'client_id': 'vezet',
                    'expired_at': '***',
                    'park_id': 'zxcvbzz2',
                    'uuid': 'iouylkjhii2',
                    'driver_app_profile_id': 'iouylkjhii2',
                },
            ],
        },
        ['expired_sessions'],
    )


# no DriverSession:Pparkbad0:Sasdfssbad0 key
# no session record in Driver:Pparkbad0:Uuuidbad0 hash
@pytest.mark.redis_store(
    [
        'zadd',
        'DriverSessionsTtl{a}',
        {'DriverSession:Pparkbad0:Sasdfssbad0': 1553855369},
    ],
)
# no DriverSession:Pparkbad1:Sasdfssbad1 key
@pytest.mark.redis_store(
    ['hset', 'Driver:Pparkbad1:Uuuidbad1', 'Session', 'asdfssbad1'],
)
@pytest.mark.redis_store(
    [
        'zadd',
        'DriverSessionsTtl{a}',
        {'DriverSession:Pparkbad1:Sasdfssbad1': 1553855429},
    ],
)
# no session record in Driver:Pparkbad2:Uuuidbad2 hash
@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pparkbad2:Sasdfssbad2',
        {'client_id': 'taximeter', 'driver_profile_id': 'uuidbad2'},
    ],
)
@pytest.mark.redis_store(
    [
        'zadd',
        'DriverSessionsTtl{a}',
        {'DriverSession:Pparkbad2:Sasdfssbad2': 1553855489},
    ],
)
# distinct session record in Driver:Pparkbad3:Uuuidbad3 hash
@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pparkbad3:Sasdfssbad3',
        {'client_id': 'taximeter', 'driver_profile_id': 'uuidbad3'},
    ],
)
@pytest.mark.redis_store(
    ['hset', 'Driver:Pparkbad3:Uuuidbad3', 'Session', 'asdfssactive3'],
)
@pytest.mark.redis_store(
    [
        'zadd',
        'DriverSessionsTtl{a}',
        {'DriverSession:Pparkbad3:Sasdfssbad3': 1553855549},
    ],
)
# ok parkok1 uuidok1 session1
@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pparkok1:Sasdfss1',
        {'client_id': 'taximeter', 'driver_profile_id': 'uuidok1'},
    ],
)
@pytest.mark.redis_store(
    ['hset', 'Driver:Pparkok1:Uuuidok1', 'Session', 'asdfss1'],
)
@pytest.mark.redis_store(
    [
        'zadd',
        'DriverSessionsTtl{a}',
        {'DriverSession:Pparkok1:Sasdfss1': 1553855609},
    ],
)
# invalid client_id
@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pparkbad41:Sasdfss4',
        {'client_id': 'badclientid', 'driver_profile_id': 'uuidbad4'},
    ],
)
@pytest.mark.redis_store(
    ['hset', 'Driver:Pparkbad4:Uuuidbad4', 'Session', 'asdfss4'],
)
@pytest.mark.redis_store(
    [
        'zadd',
        'DriverSessionsTtl{a}',
        {'DriverSession:Pparkbad4:Sasdfss4': 1553855669},
    ],
)
# ok parkok2 uuidok2 session2
@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pparkok2:Sasdfss2',
        {'client_id': 'taximeter', 'driver_profile_id': 'uuidok2'},
    ],
)
@pytest.mark.redis_store(
    ['hset', 'Driver:Pparkok2:Uuuidok2', 'Session', 'asdfss2'],
)
@pytest.mark.redis_store(
    [
        'zadd',
        'DriverSessionsTtl{a}',
        {'DriverSession:Pparkok2:Sasdfss2': 1553855729},
    ],
)
# active session for parkbad3 uuidbad3
@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pparkbad3:Sasdfssactive3',
        {'client_id': 'taximeter', 'driver_profile_id': 'uuidbad3'},
    ],
)
@pytest.mark.redis_store(
    [
        'zadd',
        'DriverSessionsTtl{a}',
        {'DriverSession:Pparkbad3:Sasdfssactive3': 2553855549},
    ],
)
async def test_expired_bad_redis_data(taxi_driver_authorizer):
    limit = 4

    data_expired_req = {
        'range': {
            'newer_than': '2019-03-29T10:35:29+0300',
            'older_than': '2019-03-29T13:35:29+0300',
            'limit': limit,
        },
    }
    all_expired_sessions = {
        'expired_sessions': [
            {
                'client_id': 'taximeter',
                'expired_at': '2019-03-29T13:33:29+0300',
                'park_id': 'parkok1',
                'uuid': 'uuidok1',
                'driver_app_profile_id': 'uuidok1',
            },
            {
                'client_id': 'taximeter',
                'expired_at': '2019-03-29T13:35:29+0300',
                'park_id': 'parkok2',
                'uuid': 'uuidok2',
                'driver_app_profile_id': 'uuidok2',
            },
        ],
    }

    response = await taxi_driver_authorizer.post(
        'driver/sessions/expired', data=json.dumps(data_expired_req),
    )
    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(), all_expired_sessions, ['expired_sessions'],
    )

    no_optional_range_fields_req = {'range': {}}

    response = await taxi_driver_authorizer.post(
        'driver/sessions/expired',
        data=json.dumps(no_optional_range_fields_req),
    )
    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(), all_expired_sessions, ['expired_sessions'],
    )

    response = await taxi_driver_authorizer.post('driver/sessions/expired')
    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(), all_expired_sessions, ['expired_sessions'],
    )

    delete_response1 = await delete_session(
        taxi_driver_authorizer,
        client_id='taximeter',
        park_id='parkok1',
        uuid='uuidok1',
        driver_app_profile_id=None,
    )
    assert delete_response1.status_code == 200

    delete_response2 = await delete_session(
        taxi_driver_authorizer,
        client_id='taximeter',
        park_id='parkok2',
        uuid='uuidok2',
        driver_app_profile_id=None,
    )
    assert delete_response2.status_code == 200

    response2 = await taxi_driver_authorizer.post(
        'driver/sessions/expired', data=json.dumps(data_expired_req),
    )
    assert response2.status_code == 200
    assert response2.json() == {'expired_sessions': []}
