import hashlib

import pytest

PHONE = '+79161889004'
PASSPORT_UID = '3000062912'
APP_FAMILY = 'taximeter'
PARK_ID = 'park_id_0'
DRIVER_ID = 'driver_id'
TOKEN = 'ABVGDEIKA'
SESSION = 'test_session'
STATUS_OFFLINE = 'offline'
USER_ID_INFOS = {'phone': PHONE, 'passport_uid': PASSPORT_UID}
X_REMOTE_IP = '1.1.1.1'
AUTHORIZATION = 'Bearer abc123'

AUTH_PARAMS = [
    ({}, {'session': SESSION, 'park_id': PARK_ID}),
    ({'X-Driver-Session': SESSION}, {'park_id': PARK_ID}),
]

AUTH_PARAMS_BAD = [
    ({}, {'session': 'bad_session', 'park_id': PARK_ID}),
    ({'X-Driver-Session': 'bad_session'}, {'park_id': PARK_ID}),
]

# tvmknife unittest service --src 123 --dst 1024
MOCK_TVM_TICKET = (
    '3:serv:CBAQ__________9_IgUIexCACA:CsTZ_V5slb9lejg97g'
    'v8mSgKJSsNOdnXi12CtuhVIeTT1Zf8BsaBnF7D-xdK_8pud0jTzo'
    'DtEppc9rn9S3wS3nabV7J74WN9LUyOa-0INeBBs3XguD16ctYR1i'
    '5da5ENrGUBXpfspgc6C_vk0wDJH1E8YXWnbNg4OtiXi64-sb0'
)

HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Taximeter 8.90 (228)',
}

MATCH_DRIVER = {
    'predicate': {
        'type': 'all_of',
        'init': {
            'predicates': [
                {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'park_id',
                        'arg_type': 'string',
                        'value': PARK_ID,
                    },
                },
                {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'driver_profile_id',
                        'arg_type': 'string',
                        'value': DRIVER_ID,
                    },
                },
            ],
        },
    },
    'enabled': True,
}


def workdate_key(park_id):
    return f'Driver:WorkDateTimeStart:{park_id}'


def requestorder_key(park_id, driver_id):
    return f'RequestOrder:MD5{park_id}:{driver_id}'


def token_key(user_id_info, app_family='taximeter'):
    key = (
        user_id_info['phone']
        if 'phone' in user_id_info
        else ('y' + user_id_info['passport_uid'])
    )
    key_arg = key + ('' if app_family == 'taximeter' else app_family)
    return f'Driver:AuthToken:{my_hash(key_arg)}'


def my_hash(key):
    return hashlib.sha256(
        (key + 'DRIVER_LOGIN_SECRET').encode('utf-8'),
    ).hexdigest()


def set_redis_for_driver(
        redis_store, app_family, park_id, driver_id, user_id_info,
):
    redis_store.hset(
        workdate_key(park_id), driver_id, b'"2018-04-01T00:00:00.000000Z"',
    )
    redis_store.set(requestorder_key(park_id, driver_id), 'driver')
    redis_store.set(token_key(user_id_info, app_family), my_hash(TOKEN))


def is_redis_set_for_driver(
        redis_store, app_family, park_id, driver_id,
) -> bool:
    return (
        redis_store.hget(workdate_key(park_id), driver_id) is not None
        and redis_store.get(requestorder_key(park_id, driver_id)) is not None
    )


def set_redis(redis_store, user_id_info):
    set_redis_for_driver(
        redis_store, APP_FAMILY, PARK_ID, DRIVER_ID, user_id_info,
    )


def is_redis_set(redis_store):
    return is_redis_set_for_driver(redis_store, APP_FAMILY, PARK_ID, DRIVER_ID)


def set_session(driver_authorizer):
    driver_authorizer.set_client_session(
        client_id=APP_FAMILY,
        park_id=PARK_ID,
        session=SESSION,
        driver_id=DRIVER_ID,
    )


def user_id_info_by_type(user_id_type):
    return {user_id_type: USER_ID_INFOS[user_id_type]}


def opt_headers_by_user_id_type(user_id_type):
    return (
        {'X-Remote-IP': X_REMOTE_IP, 'Authorization': AUTHORIZATION}
        if user_id_type == 'passport_uid'
        else {}
    )


@pytest.mark.parametrize('headers,params', AUTH_PARAMS)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
@pytest.mark.parametrize('user_id_type', ['phone', 'passport_uid'])
async def test_logout_full(
        taxi_driver_login,
        redis_store,
        driver_authorizer,
        driver_status,
        headers,
        params,
        user_id_type,
        parks,
        mock_client_notify,
        experiments3,
        blackbox,
):
    user_id_info = user_id_info_by_type(user_id_type)
    opt_headers = opt_headers_by_user_id_type(user_id_type)
    set_session(driver_authorizer)
    set_redis(redis_store, user_id_info)
    phone = user_id_info if user_id_type == 'phone' else {}

    response = await taxi_driver_login.post(
        'v1/logout',
        headers={**HEADERS, **headers, **opt_headers},
        params=params,
        data={**phone, 'token': TOKEN},
    )
    assert response.status_code == 200

    assert not is_redis_set(redis_store)
    assert redis_store.get(token_key(user_id_info)) is None
    assert mock_client_notify.times_called == 1

    ds_internal = await driver_status.mock_status_store.wait_call()
    request = ds_internal['request']
    assert request.json['park_id'] == PARK_ID
    assert request.json['driver_id'] == DRIVER_ID
    assert request.json['status'] == STATUS_OFFLINE


@pytest.mark.parametrize('headers,params', AUTH_PARAMS)
@pytest.mark.parametrize(
    'phone,token',
    [
        pytest.param(None, TOKEN, id='phone_absent'),
        pytest.param('', TOKEN, id='phone_empty'),
        pytest.param('700012345678', TOKEN, id='phone_no_lead_plus'),
        pytest.param('+00012345678', TOKEN, id='phone_first_zero'),
        pytest.param('+7', TOKEN, id='phone_short'),
        pytest.param('+700012345678', TOKEN, id='phone_wrong'),
        pytest.param(PHONE, None, id='token_absent'),
        pytest.param(PHONE, '', id='token_empty'),
        pytest.param(PHONE, 'bad_token', id='token_wrong'),
    ],
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_logout_shallow_by_phone(
        taxi_driver_login,
        redis_store,
        driver_authorizer,
        headers,
        params,
        phone,
        token,
):
    user_id_info = {'phone': PHONE}
    set_session(driver_authorizer)
    set_redis(redis_store, user_id_info)

    await taxi_driver_login.invalidate_caches()

    response = await taxi_driver_login.post(
        'v1/logout',
        headers={**HEADERS, **headers},
        params=params,
        data={'phone': phone, 'token': token},
    )
    assert response.status_code == 200
    assert not is_redis_set(redis_store)
    assert redis_store.get(token_key(user_id_info)) is not None


@pytest.mark.parametrize('headers,params', AUTH_PARAMS)
@pytest.mark.parametrize(
    'authorization,x_remote_ip,token',
    [
        pytest.param(None, X_REMOTE_IP, TOKEN, id='Authorization_absent'),
        pytest.param('', X_REMOTE_IP, TOKEN, id='Authorization_empty'),
        pytest.param(
            'Bearer BadToken',
            X_REMOTE_IP,
            TOKEN,
            id='Authorization_bad_token',
        ),
        pytest.param(
            'Bearer BadScopes',
            X_REMOTE_IP,
            TOKEN,
            marks=pytest.mark.config(
                DRIVER_AUTHPROXY_PASSPORT_SCOPES=['anohter-taxi-driver:all'],
            ),
            id='Authorization_bad_scopes',
        ),
        pytest.param(
            'Bearer BlackboxError',
            X_REMOTE_IP,
            TOKEN,
            id='Authorization_blackbox_error',
        ),
        pytest.param(AUTHORIZATION, None, TOKEN, id='X-Remote-IP_absent'),
        pytest.param(AUTHORIZATION, X_REMOTE_IP, None, id='token_absent'),
        pytest.param(AUTHORIZATION, X_REMOTE_IP, '', id='token_empty'),
        pytest.param(
            AUTHORIZATION, X_REMOTE_IP, 'bad_token', id='token_wrong',
        ),
    ],
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_logout_shallow_by_passport(
        taxi_driver_login,
        redis_store,
        driver_authorizer,
        headers,
        params,
        authorization,
        x_remote_ip,
        token,
        blackbox,
):
    user_id_info = {'passport_uid': PASSPORT_UID}
    set_session(driver_authorizer)
    set_redis(redis_store, user_id_info)

    if authorization == 'Bearer BadToken':
        blackbox.set_response(
            {
                'error': 'account is disabled',
                'status': {'id': 4, 'value': 'DISABLED'},
            },
        )
    if authorization == 'Bearer BlackboxError':
        blackbox.set_response(
            {
                'exception': {'value': 'UNKNOWN', 'id': 1},
                'error': 'some internal error',
            },
        )

    await taxi_driver_login.invalidate_caches()

    opt_headers = dict()
    if authorization is not None:
        opt_headers['Authorization'] = authorization
    if x_remote_ip is not None:
        opt_headers['X-Remote-IP'] = x_remote_ip
    response = await taxi_driver_login.post(
        'v1/logout',
        headers={**HEADERS, **headers, **opt_headers},
        params=params,
        data={'token': token},
    )
    assert response.status_code == 200
    assert not is_redis_set(redis_store)
    assert redis_store.get(token_key(user_id_info)) is not None


@pytest.mark.parametrize('headers,params', AUTH_PARAMS_BAD)
@pytest.mark.parametrize('is_token_ok', [True, False])
@pytest.mark.parametrize('user_id_type', ['phone', 'passport_uid'])
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_logout_unauthorized(
        taxi_driver_login,
        redis_store,
        driver_authorizer,
        blackbox,
        headers,
        params,
        is_token_ok,
        user_id_type,
):
    user_id_info = user_id_info_by_type(user_id_type)
    set_session(driver_authorizer)
    set_redis(redis_store, user_id_info)
    phone = user_id_info if user_id_type == 'phone' else {}
    opt_headers = opt_headers_by_user_id_type(user_id_type)

    response = await taxi_driver_login.post(
        'v1/logout',
        headers={**HEADERS, **headers, **opt_headers},
        params=params,
        data={**phone, 'token': TOKEN if is_token_ok else 'bad_token'},
    )
    assert response.status_code == 200
    assert is_redis_set(redis_store)
    assert is_token_ok == (redis_store.get(token_key(user_id_info)) is None)


@pytest.mark.config(
    DRIVERS_LOGOUT_CONFIG={
        'distribution_percent': 5,
        'dry_run': False,
        'enable': True,
        'with_metric': True,
    },
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_logout_job(
        mockserver,
        taxi_driver_login,
        redis_store,
        driver_authorizer,
        driver_status,
        parks,
):
    is_expired_already_called = False

    @mockserver.json_handler('/driver-authorizer/driver/sessions/expired')
    def _mock_driver_sessions_expired(request):
        nonlocal is_expired_already_called

        response = {
            'expired_sessions': (
                []
                if is_expired_already_called
                else [
                    {
                        'client_id': 'taximeter',
                        'park_id': 'park_id_0',
                        'uuid': 'driver_id',
                        'driver_app_profile_id': '',
                        'expired_at': '2000-01-01T00:00:00+0000',
                    },
                ]
            ),
        }
        is_expired_already_called = True
        return response

    set_session(driver_authorizer)
    metrics_key = 'GRAPHITE:COUNTERS:20190418131000'  # floor to minutes
    redis_store.hset(metrics_key, 'cl.car_lock.release', 0)
    assert redis_store.exists(metrics_key)

    redis_store.set('CarDriverLock:Car:park_id_0:some_car_id', DRIVER_ID)
    redis_store.set('CarDriverLock:Driver:park_id_0:driver_id', 'some_car_id')
    assert not redis_store.get('LogoutJob.LastDataTime')

    await taxi_driver_login.run_periodic_task('periodic-logout')
    # guaranteed second iterantion of while (!deadline.IsReached()) cycle
    await taxi_driver_login.run_periodic_task('periodic-logout')

    parks_request = await parks.mock_driver_profiles_search.wait_call()
    assert parks_request['request'].json['query']['driver']['id'] == [
        DRIVER_ID,
    ]

    ds_internal = await driver_status.mock_internal_status_bulk.wait_call()
    ds_request = ds_internal['request']
    assert len(ds_request.json['items']) == 1
    request_item = ds_request.json['items'][0]
    assert request_item['park_id'] == PARK_ID
    assert request_item['driver_id'] == DRIVER_ID
    assert request_item['status'] == STATUS_OFFLINE

    assert int(redis_store.hget(metrics_key, 'cl.car_lock.release')) == 1
    assert (
        redis_store.get('LogoutJob.LastDataTime')
        == b'\"2019-04-18T13:10:00.786000Z\"'
    )


@pytest.mark.tvm2_ticket({123: MOCK_TVM_TICKET})
@pytest.mark.now('2019-04-18T13:10:00.786Z')
@pytest.mark.parametrize('is_full_logout', [True, False])
async def test_logout_bulk(
        taxi_driver_login,
        driver_authorizer,
        redis_store,
        parks,
        driver_status,
        mockserver,
        is_full_logout,
):
    @mockserver.json_handler('/client-notify/v1/unsubscribe')
    def _mock_client_notify_unsubscribe(request):
        assert is_full_logout
        assert request.json['service'] == 'taximeter'
        assert request.json['client']['client_id'] in [
            'park_1-driver_1',
            'park_2-driver_2',
            'park_3-driver_3',
        ]
        return {}

    set_redis_for_driver(
        redis_store, 'taximeter', 'park_1', 'driver_1', {'phone': '+7123'},
    )
    set_redis_for_driver(
        redis_store, 'uberdriver', 'park_2', 'driver_2', {'phone': '+7321'},
    )
    set_redis_for_driver(
        redis_store,
        'taximeter',
        'park_3',
        'driver_3',
        {'passport_uid': PASSPORT_UID},
    )
    parks.set_parks(
        {'driver_1': 'park_1', 'driver_2': 'park_2', 'driver_3': 'park_3'},
    )

    driver_authorizer.set_client_session(
        'taximeter', 'park_1', 'session_1', 'driver_1',
    )
    driver_authorizer.set_client_session(
        'uberdriver', 'park_2', 'session_2', 'driver_2',
    )
    driver_authorizer.set_client_session(
        'taximeter', 'park_3', 'session_3', 'driver_3',
    )

    response = await taxi_driver_login.post(
        '/driver-login/v1/bulk-logout',
        headers={'X-Ya-Service-Ticket': MOCK_TVM_TICKET},
        json={
            'comment': 'BULK_LOGOUT',
            'is_full_logout': is_full_logout,
            'drivers': [
                {'park_id': 'park_1', 'driver_profile_id': 'driver_1'},
                {'park_id': 'park_2', 'driver_profile_id': 'driver_2'},
                {'park_id': 'park_3', 'driver_profile_id': 'driver_3'},
            ],
        },
    )

    assert response.status_code == 200
    drivers = response.json()['drivers']
    assert len(drivers) == 3
    for driver in drivers:
        assert driver['is_logged_out']

    assert not is_redis_set_for_driver(
        redis_store, 'taximeter', 'park_1', 'driver_1',
    )
    assert not is_redis_set_for_driver(
        redis_store, 'uberdriver', 'park_2', 'driver_2',
    )
    assert not is_redis_set_for_driver(
        redis_store, 'taximeter', 'park_3', 'driver_3',
    )

    assert not driver_authorizer.get_session('park_1', 'driver_1')
    assert not driver_authorizer.get_session('park_2', 'driver_2')
    assert not driver_authorizer.get_session('park_3', 'driver_3')

    for _ in range(3):
        ds_internal = await driver_status.mock_status_store.wait_call()
        request_item = ds_internal['request'].json
        assert request_item['status'] == STATUS_OFFLINE
        if request_item['park_id'] == 'park_1':
            assert request_item['driver_id'] == 'driver_1'
        elif request_item['park_id'] == 'park_2':
            assert request_item['driver_id'] == 'driver_2'
        elif request_item['park_id'] == 'park_3':
            assert request_item['driver_id'] == 'driver_3'
        else:
            assert False, 'unexpected driver'


@pytest.mark.tvm2_ticket({123: MOCK_TVM_TICKET})
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_logout_bulk_partial(
        taxi_driver_login,
        driver_authorizer,
        redis_store,
        parks,
        driver_status,
        mockserver,
):
    @mockserver.json_handler('/driver-authorizer/driver/sessions')
    def _delete_sessions(request):
        if request.query['park_id'] == 'park_2':
            return mockserver.make_response(status=500)
        assert request.query['park_id'] in ['park_1', 'park_3']
        driver_authorizer.delete_session(
            request.query['park_id'],
            request.query.get('uuid'),
            request.query.get('driver_app_profile_id'),
        )
        return {}

    set_redis_for_driver(
        redis_store, 'taximeter', 'park_1', 'driver_1', {'phone': '+7123'},
    )
    set_redis_for_driver(
        redis_store, 'uberdriver', 'park_2', 'driver_2', {'phone': '+7321'},
    )
    set_redis_for_driver(
        redis_store,
        'taximeter',
        'park_3',
        'driver_3',
        {'passport_uid': PASSPORT_UID},
    )
    parks.set_parks(
        {'driver_1': 'park_1', 'driver_2': 'park_2', 'driver_3': 'park_3'},
    )

    driver_authorizer.set_client_session(
        'taximeter', 'park_1', 'session_1', 'driver_1',
    )
    driver_authorizer.set_client_session(
        'uberdriver', 'park_2', 'session_2', 'driver_2',
    )
    driver_authorizer.set_client_session(
        'taximeter', 'park_3', 'session_3', 'driver_3',
    )

    response = await taxi_driver_login.post(
        '/driver-login/v1/bulk-logout',
        headers={'X-Ya-Service-Ticket': MOCK_TVM_TICKET},
        json={
            'comment': 'BULK_LOGOUT',
            'is_full_logout': True,
            'drivers': [
                {'park_id': 'park_1', 'driver_profile_id': 'driver_1'},
                {'park_id': 'park_2', 'driver_profile_id': 'driver_2'},
                {'park_id': 'park_3', 'driver_profile_id': 'driver_3'},
            ],
        },
    )

    assert response.status_code == 200
    drivers = response.json()['drivers']
    assert len(drivers) == 3
    for driver in drivers:
        if driver['driver']['park_id'] == 'park_2':
            assert not driver['is_logged_out']
        else:
            assert driver['is_logged_out']

    assert not is_redis_set_for_driver(
        redis_store, 'taximeter', 'park_1', 'driver_1',
    )
    assert is_redis_set_for_driver(
        redis_store, 'uberdriver', 'park_2', 'driver_2',
    )
    assert not is_redis_set_for_driver(
        redis_store, 'taximeter', 'park_3', 'driver_3',
    )

    assert not driver_authorizer.get_session('park_1', 'driver_1')
    assert driver_authorizer.get_session('park_2', 'driver_2')
    assert not driver_authorizer.get_session('park_3', 'driver_3')

    for _ in range(3):
        ds_internal = await driver_status.mock_status_store.wait_call()
        request_item = ds_internal['request'].json
        assert request_item['status'] == STATUS_OFFLINE


@pytest.mark.parametrize('headers,params', AUTH_PARAMS)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
@pytest.mark.parametrize('user_id_type', ['phone', 'passport_uid'])
async def test_logout_full_client_notify(
        taxi_driver_login,
        redis_store,
        driver_authorizer,
        driver_status,
        headers,
        params,
        user_id_type,
        parks,
        mockserver,
        experiments3,
        blackbox,
):
    @mockserver.json_handler('/client-notify/v1/unsubscribe')
    def mock_client_notify_unsubscribe(request):
        assert request.json == {
            'client': {'client_id': 'park_id_0-driver_id'},
            'service': 'taximeter',
        }
        return {}

    user_id_info = user_id_info_by_type(user_id_type)
    set_session(driver_authorizer)
    set_redis(redis_store, user_id_info)
    phone = user_id_info if user_id_type == 'phone' else {}
    opt_headers = opt_headers_by_user_id_type(user_id_type)

    response = await taxi_driver_login.post(
        'v1/logout',
        headers={**HEADERS, **headers, **opt_headers},
        params=params,
        data={**phone, 'token': TOKEN},
    )
    assert response.status_code == 200

    assert not is_redis_set(redis_store)
    assert redis_store.get(token_key(user_id_info)) is None
    assert mock_client_notify_unsubscribe.times_called == 1

    ds_internal = await driver_status.mock_status_store.wait_call()
    request = ds_internal['request']
    assert request.json['park_id'] == PARK_ID
    assert request.json['driver_id'] == DRIVER_ID
    assert request.json['status'] == STATUS_OFFLINE
