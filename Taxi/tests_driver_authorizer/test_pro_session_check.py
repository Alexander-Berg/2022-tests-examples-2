import json

import pytest

from testsuite.utils import ordered_object


URL = 'pro-platform/v1/info-by-session/v1'

# Generated via `tvmknife unittest service -s 434343 -d 434343`
DA_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IggIp8EaEKfBGg:IaNrMboaBGsNm0R1BRrHu164WSAg9OzXDy'
    '6pZ8am9OtgKSccNRJScc_vlNC2YcsWtigKzkNwkfWb_m9sTGHNXLnNc38af5FYH_IhfgTycJ'
    'mSJ3E2nSnDXrn15_dtc1vTILUk18rf3aaginpPdYP-6mHh9ubAhvrL4BysnEFZ5iE'
)

# Generated via `tvmknife unittest service -s 111 -d 434343`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxCnwRo:LufdsoCq1FyPAswE89e_8TxDF6J6Kxf9l6If9'
    'QDU9mgEVkhuiMqHzujXsAG7GkfWjuaDCWq7i-DX2MEpQ5sNXhfDqLs0q2tlVz4OK5mj7wmAE'
    'iC5bVJYIRRX-57b88SADpiCYiXhfjzuS7D2b9XahRfR10c0gfI4m_jPG4uDdiI'
)

# Generated via:
# tvmknife unittest user -d 42 --scopes 'pro-contractor:all'
USER_TICKET_1 = (
    '3:user:CA0Q__________9_GiIKAggqECoaEnByby1jb250cmFjdG9yOmFsbCDShdjMBCgB:'
    'D9wT3jgGrY9ybpR9sbdz9BnmfSeDIsLWOomdYTQHfrmlBruaWQYOJKMr_UhdvxaO2VBKOsrY'
    'MayfWQEgUp_SjHGGIDcMHg4aPOHMb19DAt-ICEKSayGRlSgGMEoJzkdcyoGBdZAvP6UceGy6'
    'It3J__ntDPl6wJNoOub3pHDROjY'
)

# Generated via:
# tvmknife unittest user -d 42
USER_TICKET_2 = (
    '3:user:CA0Q__________9_Gg4KAggqECog0oXYzAQoAQ:Kr9yDga1WgoyVetMTelX2rYBg'
    'xvNrB2hDr6Pkc8UN69Aj3XNiCGeg_M7RxXukwmsQQQdW0ooLJdSENry5IpfTSqD7qAnMfya'
    'uWjKOx4hMONOtPojGbxk1-E7sgRKxdkqNpoPaMtQFY60UlqWgr3-WP0-IQEgHnuIvgUlINg'
    'ctoo'
)

USER_AGENT = 'Taximeter 12.00 (9999) ios'


def make_headers(user_ticket=None, user_agent=None):
    headers = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}
    if user_ticket:
        headers['X-Ya-User-Ticket'] = user_ticket
    if user_agent:
        headers['User-Agent'] = user_agent
    return headers


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'driver-authorizer'}],
    TVM_SERVICES={'driver-authorizer': 434343, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: DA_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pzxcvb:Sasdfg',
        {
            'client_id': 'taximeter',
            'driver_profile_id': '1234',
            'yandex_uid': '42',
        },
    ],
)
@pytest.mark.redis_store(
    ['zadd', 'DriverSessionsTtl{a}', {'DriverSession:Pzxcvb:Sasdfg': 1e15}],
)
@pytest.mark.redis_store(['hset', 'Driver:Pzxcvb:U1234', 'Session', 'asdfg'])
async def test_auth_ok(taxi_driver_authorizer, redis_store):
    headers = make_headers(user_ticket=USER_TICKET_1, user_agent=USER_AGENT)

    data = {'session': 'asdfg', 'park_id': 'zxcvb', 'ttl': 4444}

    response = await taxi_driver_authorizer.post(
        URL, headers=headers, json=data,
    )
    assert response.status_code == 200
    assert response.json() == {'uuid': '1234', 'app_family': 'taximeter'}

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
        redis_store.hget('DriverSession:Pzxcvb:Sasdfg', 'yandex_uid') == b'42'
    )

    delete_params = {
        'client_id': 'taximeter',
        'park_id': 'zxcvb',
        'uuid': '1234',
        'driver_app_profile_id': '1234',
    }
    response = await taxi_driver_authorizer.delete(
        'driver/sessions', params=delete_params, headers=make_headers(),
    )
    assert response.status_code == 200

    response = await taxi_driver_authorizer.post(
        URL, headers=headers, json=data,
    )
    assert response.status_code == 401
    response_json = response.json()
    assert response_json['code'] == '401'
    assert response_json['message'] == 'authorization failed'

    assert redis_store.type('DriverSession:Pzxcvb:Sasdfg') == b'none'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'driver-authorizer'}],
    TVM_SERVICES={'driver-authorizer': 434343, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: DA_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pzxcvb:Sasdfg',
        {
            'client_id': 'taximeter',
            'driver_profile_id': '1234',
            'yandex_uid': '42',
        },
    ],
)
@pytest.mark.redis_store(
    ['zadd', 'DriverSessionsTtl{a}', {'DriverSession:Pzxcvb:Sasdfg': 1e15}],
)
@pytest.mark.redis_store(['hset', 'Driver:Pzxcvb:U1234', 'Session', 'asdfg'])
async def test_auth_bad_session(taxi_driver_authorizer):
    headers = make_headers(user_ticket=USER_TICKET_1, user_agent=USER_AGENT)

    data = {'session': 'asdxx', 'park_id': 'zxcvb', 'ttl': 4444}

    response = await taxi_driver_authorizer.post(
        URL, headers=headers, json=data,
    )
    assert response.status_code == 401
    response_json = response.json()
    assert response_json['code'] == '401'
    assert response_json['message'] == 'authorization failed'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'driver-authorizer'}],
    TVM_SERVICES={'driver-authorizer': 434343, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: DA_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pzxcvb:Sasdfg',
        {
            'client_id': 'taximeter',
            'driver_profile_id': '1234',
            'yandex_uid': '42',
        },
    ],
)
@pytest.mark.redis_store(
    ['zadd', 'DriverSessionsTtl{a}', {'DriverSession:Pzxcvb:Sasdfg': 1e15}],
)
@pytest.mark.redis_store(['hset', 'Driver:Pzxcvb:U1234', 'Session', 'asdfg'])
async def test_auth_bad_park_id(taxi_driver_authorizer):
    headers = make_headers(user_ticket=USER_TICKET_1, user_agent=USER_AGENT)

    data = {'session': 'asdfg', 'park_id': 'zxcxx', 'ttl': 4444}

    response = await taxi_driver_authorizer.post(
        URL, headers=headers, json=data,
    )
    assert response.status_code == 401
    response_json = response.json()
    assert response_json['code'] == '401'
    assert response_json['message'] == 'authorization failed'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'driver-authorizer'}],
    TVM_SERVICES={'driver-authorizer': 434343, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: DA_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pzxcvb:Sasdfg',
        {
            'client_id': 'taximeter',
            'driver_profile_id': '1234',
            'yandex_uid': '43',
        },
    ],
)
@pytest.mark.redis_store(
    ['zadd', 'DriverSessionsTtl{a}', {'DriverSession:Pzxcvb:Sasdfg': 1e15}],
)
@pytest.mark.redis_store(['hset', 'Driver:Pzxcvb:U1234', 'Session', 'asdfg'])
async def test_auth_bad_uid(taxi_driver_authorizer):
    headers = make_headers(user_ticket=USER_TICKET_1, user_agent=USER_AGENT)

    data = {'session': 'asdfg', 'park_id': 'zxcvb', 'ttl': 4444}

    response = await taxi_driver_authorizer.post(
        URL, headers=headers, json=data,
    )
    assert response.status_code == 401
    response_json = response.json()
    assert response_json['code'] == '401'
    assert response_json['message'] == 'authorization failed'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'driver-authorizer'}],
    TVM_SERVICES={'driver-authorizer': 434343, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: DA_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pzxcvb:Sasdfg',
        {
            'client_id': 'uberdriver',
            'driver_profile_id': '1234',
            'yandex_uid': '42',
        },
    ],
)
@pytest.mark.redis_store(
    ['zadd', 'DriverSessionsTtl{a}', {'DriverSession:Pzxcvb:Sasdfg': 1e15}],
)
@pytest.mark.redis_store(['hset', 'Driver:Pzxcvb:U1234', 'Session', 'asdfg'])
async def test_auth_bad_client_id(taxi_driver_authorizer):
    headers = make_headers(user_ticket=USER_TICKET_1, user_agent=USER_AGENT)

    data = {'session': 'asdfg', 'park_id': 'zxcvb', 'ttl': 4444}

    response = await taxi_driver_authorizer.post(
        URL, headers=headers, json=data,
    )
    assert response.status_code == 401
    response_json = response.json()
    assert response_json['code'] == '401'
    assert response_json['message'] == 'authorization failed'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'driver-authorizer'}],
    TVM_SERVICES={'driver-authorizer': 434343, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: DA_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pzxcvb:Sasdfg',
        {
            'client_id': 'taximeter',
            'driver_profile_id': '1234',
            'yandex_uid': '42',
        },
    ],
)
@pytest.mark.redis_store(
    ['zadd', 'DriverSessionsTtl{a}', {'DriverSession:Pzxcvb:Sasdfg': 1e15}],
)
@pytest.mark.redis_store(['hset', 'Driver:Pzxcvb:U1234', 'Session', 'asdfg'])
async def test_auth_bad_ua(taxi_driver_authorizer):
    headers = make_headers(user_ticket=USER_TICKET_1, user_agent='ie5')

    data = {'session': 'asdfg', 'park_id': 'zxcvb', 'ttl': 4444}

    response = await taxi_driver_authorizer.post(
        URL, headers=headers, json=data,
    )
    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == '400'
    assert response_json['message'] == 'bad request'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'driver-authorizer'}],
    TVM_SERVICES={'driver-authorizer': 434343, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: DA_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
@pytest.mark.redis_store(
    [
        'hmset',
        'DriverSession:Pzxcvb:Sasdfg',
        {
            'client_id': 'taximeter',
            'driver_profile_id': '1234',
            'yandex_uid': '42',
        },
    ],
)
@pytest.mark.redis_store(
    ['zadd', 'DriverSessionsTtl{a}', {'DriverSession:Pzxcvb:Sasdfg': 1e15}],
)
@pytest.mark.redis_store(['hset', 'Driver:Pzxcvb:U1234', 'Session', 'asdfg'])
async def test_auth_no_scopes(taxi_driver_authorizer):
    headers = make_headers(user_ticket=USER_TICKET_2, user_agent=USER_AGENT)

    data = {'session': 'asdfg', 'park_id': 'zxcvb', 'ttl': 4444}

    response = await taxi_driver_authorizer.post(
        URL, headers=headers, json=data,
    )
    assert response.status_code == 403


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'driver-authorizer'}],
    TVM_SERVICES={'driver-authorizer': 434343, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: DA_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_auth_put_check_incorrect_session(
        taxi_driver_authorizer, put_session,
):
    response = await put_session(
        client_id='taximeter',
        park_id='zxcvb123',
        uuid='iouylkjh456',
        driver_app_profile_id=None,
        yandex_uid='42',
        ttl=5555,
        headers=make_headers(),
    )
    session = response.headers.get('X-Driver-Session')
    assert response.status_code == 200
    assert response.json() == {'ttl': 5555}
    assert session is not None

    headers = make_headers(user_ticket=USER_TICKET_1, user_agent=USER_AGENT)

    data = {'session': f'{session}x', 'park_id': 'zxcvb123', 'ttl': 4444}

    response = await taxi_driver_authorizer.post(
        URL, headers=headers, json=data,
    )
    assert response.status_code == 401
    response_json = response.json()
    assert response_json['code'] == '401'
    assert response_json['message'] == 'authorization failed'
