import pytest

from antifraud import utils


def _get_urls_by_type(with_slash=False):
    base_url = 'v1/events/protocol/'
    events = [
        'paymentmethods',
        'expecteddestinations',
        'couponlist',
        'nearestzone',
        'zoneinfo',
        'suggesteddestinations',
        'suggestedpositions',
        'geofences',
        'orderdraft',
        'ordercommit',
        'order',
        'launch',
        'routestats',
        'personalstate',
    ]
    formats = ['{}{}', '{}{}/']
    fmt = formats[1] if with_slash else formats[0]
    return {event: fmt.format(base_url, event) for event in events}


@pytest.mark.parametrize('user_id', ['user_id1'])
@pytest.mark.config(AFS_STORE_PROTOCOL_EVENTS=True)
@pytest.mark.parametrize('with_slash', [True, False])
@pytest.mark.now('2018-10-01T09:00:00+0000')
def test_events_protocol_base(
        taxi_antifraud, redis_store, testpoint, user_id, with_slash,
):
    @testpoint('after_store_events_to_db')
    def after_store_to_db(_):
        pass

    urls_by_type = _get_urls_by_type(with_slash)

    for url in urls_by_type.values():
        response = taxi_antifraud.post(url, {'user_id': user_id})
        assert 200 == response.status_code
        assert {} == response.json()

    for _ in range(len(urls_by_type)):
        after_store_to_db.wait_call()

    key = 'v1:events:protocol:base:{}'.format(user_id)

    assert 1200 == redis_store.ttl(key)

    created_by_type = {
        record.decode().split(':')[-1]: record.decode().split(':')[-2]
        for record in redis_store.lrange(key, 0, -1)
    }

    assert len(urls_by_type) == len(created_by_type)

    for url_type in urls_by_type.keys():
        created = created_by_type[url_type]
        assert 1538384400000 == int(created)


def _check_raws(db, user_id, phone_id, device_id, types, events_num=1):
    rec = db.antifraud_users_aggregates.find_one(
        {
            'user_id': user_id,
            'user_phone_id': phone_id,
            'device_id': device_id,
        },
    )
    if rec is None:
        return False
    res = True
    res = res and rec.get('user_phone_id') == phone_id
    res = res and rec.get('device_id') == device_id

    events = rec.get('events', {})

    def _base_alright():
        for event in types:
            if events.get(event) != events_num:
                return False

        return True

    res = res and _base_alright()
    return res


@utils.wait_for_correct(retries=100)
def _check_for_correct_raws(
        db, user_id, phone_id, device_id, types, events_num=1,
):
    return _check_raws(db, user_id, phone_id, device_id, types, events_num)


@pytest.mark.config(
    AFS_PERIODIC_STORE_PROTOCOL_AGGREGATES=True,
    AFS_PROTOCOL_AGGREGATES_SEND_PERIOD=50,
    AFS_PROTOCOL_AGGREGATES_ADD_FULL_LOGGING=True,
)
@pytest.mark.parametrize('is_fast_store', [True, False])
@pytest.mark.parametrize(
    'user_id,phone_id,device_id',
    [('user_id1', 'phone_id1', None), ('user_id2', 'phone_id2', 'device_id2')],
)
def test_aggregates_protocol_base(
        taxi_antifraud,
        db,
        config,
        user_id,
        phone_id,
        device_id,
        is_fast_store,
        mockserver,
):
    @mockserver.json_handler('/user-api/users/search')
    def _mock_user_api_search(request):
        assert request.json == {'ids': ['user_id1']}
        return {'items': [{'id': 'user_id1', 'phone_id': 'phone_id1'}]}

    config.set_values(
        dict(AFS_PROTOCOL_AGGREGATES_FAST_STORE_TO_DB=is_fast_store),
    )
    urls_by_type = _get_urls_by_type()

    for url in urls_by_type.values():
        response = taxi_antifraud.post(
            url,
            {'user_id': user_id, 'phone_id': phone_id, 'device_id': device_id},
        )
        assert 200 == response.status_code
        assert {} == response.json()

    res = _check_for_correct_raws(
        db, user_id, phone_id, device_id, urls_by_type.keys(),
    )
    assert res, 'not every events'


@pytest.mark.config(
    AFS_PERIODIC_STORE_PROTOCOL_AGGREGATES=False,
    AFS_PROTOCOL_AGGREGATES_FAST_STORE_TO_DB=False,
    AFS_PROTOCOL_AGGREGATES_SEND_PERIOD=50,
    AFS_PROTOCOL_AGGREGATES_ADD_FULL_LOGGING=True,
)
def test_config_off(taxi_antifraud, db):
    urls_by_type = _get_urls_by_type()

    for url in urls_by_type.values():
        response = taxi_antifraud.post(
            url,
            {
                'user_id': 'user',
                'phone_id': 'phone_id',
                'device_id': 'device_id',
            },
        )
        assert 200 == response.status_code
        assert {} == response.json()

    @utils.wait_for_correct(2)
    def check_collection_empty():
        raw_in_db = db.antifraud_users_aggregates.find_one()
        return raw_in_db is None

    assert (
        check_collection_empty()
    ), 'protocol aggregates collection must be empty with disabled config'


@pytest.mark.config(
    AFS_PERIODIC_STORE_PROTOCOL_AGGREGATES=True,
    AFS_PROTOCOL_AGGREGATES_SEND_PERIOD=50,
    AFS_PROTOCOL_AGGREGATES_ADD_FULL_LOGGING=True,
)
@pytest.mark.parametrize('is_fast_store', [True, False])
def test_aggregates_multi_events(taxi_antifraud, db, is_fast_store, config):
    config.set_values(
        dict(AFS_PROTOCOL_AGGREGATES_FAST_STORE_TO_DB=is_fast_store),
    )
    urls_by_type = _get_urls_by_type()
    _NUM_OF_EVENTS = 3

    for _ in range(_NUM_OF_EVENTS):
        for url in urls_by_type.values():
            response = taxi_antifraud.post(
                url,
                {
                    'user_id': 'user_id',
                    'phone_id': 'phone_id',
                    'device_id': 'device_id',
                },
            )
            assert 200 == response.status_code
            assert {} == response.json()

    assert _check_for_correct_raws(
        db,
        'user_id',
        'phone_id',
        'device_id',
        urls_by_type.keys(),
        _NUM_OF_EVENTS,
    ), 'wrong db content after multi events for one user'


@pytest.mark.config(
    AFS_PERIODIC_STORE_PROTOCOL_AGGREGATES=True,
    AFS_PROTOCOL_AGGREGATES_SEND_PERIOD=50,
    AFS_PROTOCOL_AGGREGATES_ADD_FULL_LOGGING=True,
)
def test_aggregates_multi_users(taxi_antifraud, db):
    urls = _get_urls_by_type()
    event_type = list(urls.keys())[0]
    url = urls[event_type]
    _NUM_OF_USERS = 5
    _NUM_OF_RETRIES = 2

    users = [
        {'user_id': str(i), 'phone_id': str(i), 'device_id': str(i)}
        for i in range(_NUM_OF_USERS)
    ]

    for _ in range(_NUM_OF_RETRIES):
        for user in users:
            response = taxi_antifraud.post(url, user)
            assert 200 == response.status_code
            assert {} == response.json()

    @utils.wait_for_correct()
    def _check_multiuser():
        for user in users:
            if not _check_raws(
                    db,
                    user['user_id'],
                    user['phone_id'],
                    user['device_id'],
                    [event_type],
                    _NUM_OF_RETRIES,
            ):
                return False
        return True

    assert _check_multiuser(), 'wrong db content for multi user aggregates'


@pytest.mark.config(
    AFS_PERIODIC_STORE_PROTOCOL_AGGREGATES=True,
    AFS_PROTOCOL_AGGREGATES_SEND_PERIOD=50,
    AFS_PROTOCOL_AGGREGATES_ADD_FULL_LOGGING=True,
)
@pytest.mark.filldb(antifraud_users_aggregates='multidays')
def test_aggregates_multi_days(taxi_antifraud, db):
    urls = _get_urls_by_type()
    all_raws = [raw for raw in db.antifraud_users_aggregates.find()]
    assert len(all_raws) == 1
    basic_raw = all_raws[0]

    for url in urls.values():
        response = taxi_antifraud.post(
            url, {'user_id': '0', 'phone_id': '0', 'device_id': '0'},
        )
        assert 200 == response.status_code
        assert {} == response.json()

    @utils.wait_for_correct()
    def _check():
        raws = [raw for raw in db.antifraud_users_aggregates.find()]

        if len(raws) != 2:
            return False

        for field in ['hash', 'user_id', 'user_phone_id', 'device_id']:
            if raws[0][field] != raws[1][field]:
                return False
        first = raws[1] if raws[1].get('first') is not None else raws[0]

        return first == basic_raw

    assert (
        _check()
    ), 'aggregates from different days should not overwrite each other'


@pytest.mark.config(
    AFS_PERIODIC_STORE_PROTOCOL_AGGREGATES=True,
    AFS_USE_USER_API_IN_PROTOCOL_AGGREGATES_COLLECTOR=True,
    AFS_PROTOCOL_AGGREGATES_SEND_PERIOD=50,
    AFS_PROTOCOL_AGGREGATES_ADD_FULL_LOGGING=True,
)
@pytest.mark.parametrize(
    'user_id,phone_id,device_id', [('user_id1', 'phone_id1', None)],
)
def test_aggregates_protocol_with_user_api(
        taxi_antifraud, db, user_id, phone_id, device_id, mockserver,
):
    @mockserver.json_handler('/user-api/users/search')
    def _mock_user_api_search(request):
        assert request.json == {
            'ids': ['user_id1'],
            'primary_replica': False,
            'fields': ['phone_id', 'device_id'],
        }
        return {
            'items': [
                {
                    'id': 'user_id1',
                    'phone_id': 'phone_id1',
                    'device_id': 'device_id1',
                },
            ],
        }

    urls_by_type = _get_urls_by_type()

    for url in urls_by_type.values():
        response = taxi_antifraud.post(
            url,
            {'user_id': user_id, 'phone_id': phone_id, 'device_id': device_id},
        )
        assert 200 == response.status_code
        assert {} == response.json()

    res = _check_for_correct_raws(
        db, user_id, phone_id, 'device_id1', urls_by_type.keys(),
    )
    assert res, 'not every events'


@pytest.mark.config(
    AFS_PERIODIC_STORE_PROTOCOL_AGGREGATES=True,
    AFS_USE_USER_API_IN_PROTOCOL_AGGREGATES_COLLECTOR=True,
    AFS_PROTOCOL_AGGREGATES_SEND_PERIOD=50,
    AFS_PROTOCOL_AGGREGATES_ADD_FULL_LOGGING=True,
)
@pytest.mark.parametrize(
    'user_id,phone_id,device_id', [('user_id1', None, None)],
)
def test_aggregates_protocol_with_user_api_without_any_ids(
        taxi_antifraud, db, user_id, phone_id, device_id, mockserver,
):
    @mockserver.json_handler('/user-api/users/search')
    def _mock_user_api_search(request):
        assert request.json == {
            'ids': ['user_id1'],
            'primary_replica': False,
            'fields': ['phone_id', 'device_id'],
        }
        return {
            'items': [
                {
                    'id': 'user_id1',
                    'phone_id': 'phone_id1',
                    'device_id': 'device_id1',
                },
            ],
        }

    urls_by_type = _get_urls_by_type()

    for url in urls_by_type.values():
        response = taxi_antifraud.post(
            url,
            {'user_id': user_id, 'phone_id': phone_id, 'device_id': device_id},
        )
        assert 200 == response.status_code
        assert {} == response.json()

    res = _check_for_correct_raws(
        db, user_id, 'phone_id1', 'device_id1', urls_by_type.keys(),
    )
    assert res, 'not every events'


@pytest.mark.config(
    AFS_PERIODIC_STORE_PROTOCOL_AGGREGATES=True,
    AFS_USE_USER_API_IN_PROTOCOL_AGGREGATES_COLLECTOR=True,
    AFS_PROTOCOL_AGGREGATES_SEND_PERIOD=50,
    AFS_PROTOCOL_AGGREGATES_ADD_FULL_LOGGING=True,
)
@pytest.mark.parametrize(
    'user_id,phone_id,device_id',
    [
        ('user_id1', None, None),
        ('user_id2', None, 'device_id2'),
        ('user_id3', 'phone_id3', None),
        ('user_id4', 'phone_id4', 'device_id4'),
    ],
)
def test_aggregates_protocol_with_user_api_without_full_data(
        taxi_antifraud, db, user_id, phone_id, device_id, mockserver,
):
    @mockserver.json_handler('/user-api/users/search')
    def _mock_user_api_search(request):
        _id = request.json['ids'][0]
        result_map = {
            'user_id1': {'items': [{'id': 'user_id1'}]},
            'user_id2': {
                'items': [{'id': 'user_id2', 'device_id': 'device_id2'}],
            },
            'user_id3': {
                'items': [{'id': 'user_id3', 'phone_id': 'phone_id3'}],
            },
        }

        assert _id in result_map
        return result_map[_id]

    urls_by_type = _get_urls_by_type()

    for url in urls_by_type.values():
        response = taxi_antifraud.post(
            url,
            {'user_id': user_id, 'phone_id': phone_id, 'device_id': device_id},
        )
        assert 200 == response.status_code
        assert {} == response.json()

    res = _check_for_correct_raws(
        db, user_id, phone_id, device_id, urls_by_type.keys(),
    )
    assert res, 'not every events'


@pytest.mark.config(
    AFS_PERIODIC_STORE_PROTOCOL_AGGREGATES=True,
    AFS_USE_USER_API_IN_PROTOCOL_AGGREGATES_COLLECTOR=True,
    AFS_PROTOCOL_AGGREGATES_SEND_PERIOD=50,
    AFS_PROTOCOL_AGGREGATES_ADD_FULL_LOGGING=True,
)
@pytest.mark.parametrize(
    'user_id,phone_id,device_id', [('user_id1', None, None)],
)
def test_aggregates_protocol_with_user_api_cursor(
        taxi_antifraud, db, user_id, phone_id, device_id, mockserver,
):
    @mockserver.json_handler('/user-api/users/search')
    def _mock_user_api_search(request):
        request = request.json
        _ids = request['ids']
        cursor = request.get('cursor')
        assert _ids == ['user_id1']

        if cursor is None:
            return {'cursor': 'some_cursor', 'items': [{'id': 'user_id'}]}
        assert cursor == 'some_cursor'
        return {
            'items': [
                {
                    'id': 'user_id1',
                    'phone_id': 'phone_id1',
                    'device_id': 'device_id1',
                },
            ],
        }

    urls_by_type = _get_urls_by_type()

    for url in urls_by_type.values():
        response = taxi_antifraud.post(
            url,
            {'user_id': user_id, 'phone_id': phone_id, 'device_id': device_id},
        )
        assert 200 == response.status_code
        assert {} == response.json()

    res = _check_for_correct_raws(
        db, user_id, 'phone_id1', 'device_id1', urls_by_type.keys(),
    )
    assert res, 'not every events'
