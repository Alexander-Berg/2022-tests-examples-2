import json


async def test_auth_put_get_bulk(taxi_driver_authorizer, put_session):
    park_id1 = 'zxcvb123'
    uuid1 = 'iouylkjh456'
    park_id2 = 'asdfg654'
    uuid2 = 'qwopieru789'
    driver_app_profile_id2 = 'sdhgsdbs89'

    response_put1 = await put_session(
        client_id='taximeter',
        park_id=park_id1,
        uuid=uuid1,
        driver_app_profile_id=None,
        ttl=5555,
    )
    assert response_put1.status_code == 200
    assert response_put1.json() == {'ttl': 5555}
    session_put1 = response_put1.headers.get('X-Driver-Session')
    assert session_put1 is not None

    response_put2 = await put_session(
        client_id='taximeter',
        park_id=park_id2,
        uuid=uuid2,
        driver_app_profile_id=driver_app_profile_id2,
        ttl=4455,
    )
    assert response_put2.status_code == 200
    assert response_put2.json() == {'ttl': 4455}
    session_put2 = response_put2.headers.get('X-Driver-Session')
    assert session_put2 is not None

    data = {
        'drivers': [
            {'client_id': 'taximeter', 'park_id': park_id1, 'uuid': uuid1},
            {
                'client_id': 'taximeter',
                'park_id': park_id1,
                'uuid': uuid2,
                'driver_app_profile_id': driver_app_profile_id2,
            },
            {'client_id': 'taximeter', 'park_id': park_id2, 'uuid': uuid1},
            {
                'client_id': 'taximeter',
                'park_id': park_id2,
                'uuid': uuid2,
                'driver_app_profile_id': driver_app_profile_id2,
            },
            {'client_id': 'taximeter', 'park_id': park_id2, 'uuid': uuid2},
        ],
    }

    response_bulk_get = await taxi_driver_authorizer.post(
        'driver/sessions/bulk_retrieve', data=json.dumps(data),
    )
    assert response_bulk_get.status_code == 200
    sessions = response_bulk_get.json()['sessions']
    assert sessions[0]['ttl'] > 5500 and sessions[0]['ttl'] <= 5555
    assert sessions[3]['ttl'] > 4400 and sessions[3]['ttl'] <= 4455
    sessions[0]['ttl'] = 'already_checked'
    sessions[3]['ttl'] = 'already_checked'
    assert sessions == [
        {
            'client_id': 'taximeter',
            'park_id': park_id1,
            'uuid': uuid1,
            'driver_app_profile_id': uuid1,
            'status': 'ok',
            'session': session_put1,
            'ttl': 'already_checked',
        },
        {
            'client_id': 'taximeter',
            'park_id': park_id1,
            'uuid': uuid2,
            'driver_app_profile_id': driver_app_profile_id2,
            'status': 'not_found',
        },
        {
            'client_id': 'taximeter',
            'park_id': park_id2,
            'uuid': uuid1,
            'driver_app_profile_id': uuid1,
            'status': 'not_found',
        },
        {
            'client_id': 'taximeter',
            'park_id': park_id2,
            'uuid': uuid2,
            'driver_app_profile_id': driver_app_profile_id2,
            'status': 'ok',
            'session': session_put2,
            'ttl': 'already_checked',
        },
        {
            'client_id': 'taximeter',
            'park_id': park_id2,
            'uuid': uuid2,
            'driver_app_profile_id': uuid2,
            'status': 'not_found',
        },
    ]


async def test_auth_put_get_bulk_no_park_id(
        taxi_driver_authorizer, put_session,
):
    uuid1 = 'iouylkjh456'
    uuid2 = 'qwopieru789'
    driver_app_profile_id2 = 'oiutra89'

    response_put1 = await put_session(
        client_id='taximeter',
        park_id=None,
        uuid=uuid1,
        driver_app_profile_id=None,
        ttl=5555,
    )
    assert response_put1.status_code == 200
    assert response_put1.json() == {'ttl': 5555}
    session_put1 = response_put1.headers.get('X-Driver-Session')
    assert session_put1 is not None

    response_put2 = await put_session(
        client_id='taximeter',
        park_id=None,
        uuid=uuid2,
        driver_app_profile_id=driver_app_profile_id2,
        ttl=4455,
    )
    assert response_put2.status_code == 200
    assert response_put2.json() == {'ttl': 4455}
    session_put2 = response_put2.headers.get('X-Driver-Session')
    assert session_put2 is not None

    data = {
        'drivers': [
            {'client_id': 'taximeter', 'uuid': uuid1},
            {
                'client_id': 'taximeter',
                'uuid': uuid2,
                'driver_app_profile_id': driver_app_profile_id2,
            },
            {'client_id': 'taximeter', 'uuid': uuid2},
        ],
    }

    response_bulk_get = await taxi_driver_authorizer.post(
        'driver/sessions/bulk_retrieve', data=json.dumps(data),
    )
    assert response_bulk_get.status_code == 200
    sessions = response_bulk_get.json()['sessions']
    assert sessions[0]['ttl'] > 5500 and sessions[0]['ttl'] <= 5555
    assert sessions[1]['ttl'] > 4400 and sessions[1]['ttl'] <= 4455
    sessions[0]['ttl'] = 'already_checked'
    sessions[1]['ttl'] = 'already_checked'
    assert sessions == [
        {
            'client_id': 'taximeter',
            'uuid': uuid1,
            'driver_app_profile_id': uuid1,
            'status': 'ok',
            'session': session_put1,
            'ttl': 'already_checked',
        },
        {
            'client_id': 'taximeter',
            'uuid': uuid2,
            'driver_app_profile_id': driver_app_profile_id2,
            'status': 'ok',
            'session': session_put2,
            'ttl': 'already_checked',
        },
        {
            'client_id': 'taximeter',
            'uuid': uuid2,
            'driver_app_profile_id': uuid2,
            'status': 'not_found',
        },
    ]


async def test_auth_get_bulk_too_large(taxi_driver_authorizer):
    data = {
        'drivers': [
            {
                'client_id': 'taximeter',
                'park_id': 'zxcvb123',
                'uuid': 'iouylkjh456',
            },
        ] * 31,
    }

    response_bulk_get = await taxi_driver_authorizer.post(
        'driver/sessions/bulk_retrieve', data=json.dumps(data),
    )
    assert response_bulk_get.status_code == 400
    assert response_bulk_get.json()['code'] == '400'
