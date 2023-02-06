import json

import pytest

USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'

PA_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-Pass-Flags': 'phonish',
    'X-Yandex-UID': '4003514353',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=yango_android',
    'X-Ya-User-Ticket': 'user_ticket',
}


async def test_syncpos_bad_request(taxi_geosharing):
    response = await taxi_geosharing.post(
        '4.0/geosharing/v1/syncpos',
        {'key': 'request_body_malformed'},
        headers=PA_HEADERS,
    )
    assert response.status_code == 400


async def test_syncpos_noexp_nostore(load_json, taxi_geosharing):
    response = await taxi_geosharing.post(
        '4.0/geosharing/v1/syncpos',
        load_json('syncpos_request.json'),
        headers=PA_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'sharing': 'unavailable'}


@pytest.mark.config(
    GEOSHARING_SYNC_USER_TRACKER=True,
    GEOSHARING_USER_TRACKER_ALWAYS_STORE=True,
    FTS_USAGE={
        'send-positions': {'use-gateway': 100, 'use-grpc': 0},
        'position': {'use-gateway': 0, 'use-grpc': 0},
        'bulk-positions': {'use-gateway': 0, 'use-grpc': 0},
        'shorttrack': {'use-gateway': 0, 'use-grpc': 0},
        'bulk-shorttracks': {'use-gateway': 0, 'use-grpc': 0},
    },
)
async def test_syncpos_noexp(
        load_json, taxi_geosharing, user_tracker, mockserver,
):
    user_tracker.expect(
        {
            'accuracy': 2,
            'point': [37.5367, 55.7494],
            'time': '2019-12-13T11:29:33+0000',
            'user_id': USER_ID,
        },
    )
    response = await taxi_geosharing.post(
        '4.0/geosharing/v1/syncpos',
        load_json('syncpos_request.json'),
        headers=PA_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'sharing': 'unavailable'}


@pytest.mark.parametrize(
    'sharing_mode,accuracy,order_pos,ut_fail',
    [
        ('too_far', 1, [37.4321, 55.1234], False),
        ('allowed', 1, [37.5367, 55.7494], False),
        ('bad_accuracy', 1000, [37.5367, 55.7494], False),
        ('allowed', 1, [37.5367, 55.7494], True),
    ],
)
@pytest.mark.config(
    GEOSHARING_SYNC_USER_TRACKER=True,
    FTS_USAGE={
        'send-positions': {'use-gateway': 100, 'use-grpc': 0},
        'position': {'use-gateway': 0, 'use-grpc': 0},
        'bulk-positions': {'use-gateway': 0, 'use-grpc': 0},
        'shorttrack': {'use-gateway': 0, 'use-grpc': 0},
        'bulk-shorttracks': {'use-gateway': 0, 'use-grpc': 0},
    },
)
@pytest.mark.experiments3(filename='exp3_geosharing_policy.json')
async def test_syncpos(
        load_json,
        taxi_geosharing,
        user_tracker,
        sharing_mode,
        accuracy,
        order_pos,
        ut_fail,
        mockserver,
):
    user_tracker.expect(
        {
            'accuracy': accuracy,
            'point': [37.5367, 55.7494],
            'time': '2019-12-13T11:29:33+0000',
            'user_id': USER_ID,
        },
    )
    user_tracker.set_fail(ut_fail)
    request = load_json('syncpos_request.json')
    request['location']['accuracy'] = accuracy
    request['state']['order_source_pos'] = order_pos
    response = await taxi_geosharing.post(
        '4.0/geosharing/v1/syncpos', request, headers=PA_HEADERS,
    )
    expected = load_json('syncpos_response.json')
    expected['sharing'] = sharing_mode
    if sharing_mode != 'allowed':
        del expected['banner']
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.now('2019-12-13T12:00:01+0000')
@pytest.mark.config(
    GEOSHARING_SYNC_USER_TRACKER=True,
    FTS_USAGE={
        'send-positions': {'use-gateway': 100, 'use-grpc': 0},
        'position': {'use-gateway': 0, 'use-grpc': 0},
        'bulk-positions': {'use-gateway': 0, 'use-grpc': 0},
        'shorttrack': {'use-gateway': 0, 'use-grpc': 0},
        'bulk-shorttracks': {'use-gateway': 0, 'use-grpc': 0},
    },
)
@pytest.mark.experiments3(filename='exp3_geosharing_policy.json')
@pytest.mark.redis_store(
    [
        'set',
        'geosharing:seen:' + USER_ID,
        json.dumps(
            {
                'seen_at': '2019-12-13T11:58:01+0000',
                'status': 'ok',
                'position': {
                    'position': [1.2, 3.4],
                    'accuracy': 2.0,
                    'retrieved_at': '2016-12-13T12:00:01+0000',
                },
            },
        ),
    ],
)
async def test_syncpos_lastpos(
        load_json, taxi_geosharing, user_tracker, mockserver,
):
    user_tracker.expect(
        {
            'accuracy': 2,
            'point': [37.5367, 55.7494],
            'time': '2019-12-13T11:29:33+0000',
            'user_id': USER_ID,
        },
    )
    request = load_json('syncpos_request_last_seen.json')
    response = await taxi_geosharing.post(
        '4.0/geosharing/v1/syncpos', request, headers=PA_HEADERS,
    )
    expected = load_json('syncpos_response_last_seen.json')
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.config(
    GEOSHARING_SYNC_USER_TRACKER=True,
    FTS_USAGE={
        'send-positions': {'use-gateway': 100, 'use-grpc': 0},
        'position': {'use-gateway': 0, 'use-grpc': 0},
        'bulk-positions': {'use-gateway': 0, 'use-grpc': 0},
        'shorttrack': {'use-gateway': 0, 'use-grpc': 0},
        'bulk-shorttracks': {'use-gateway': 0, 'use-grpc': 0},
    },
)
@pytest.mark.experiments3(filename='exp3_geosharing_policy.json')
@pytest.mark.redis_store(
    ['set', 'geosharing:seen:' + USER_ID, '{some invalid json}'],
)
async def test_syncpos_lastpos_fail(
        load_json, taxi_geosharing, user_tracker, mockserver,
):
    user_tracker.expect(
        {
            'accuracy': 2,
            'point': [37.5367, 55.7494],
            'time': '2019-12-13T11:29:33+0000',
            'user_id': USER_ID,
        },
    )
    request = load_json('syncpos_request_last_seen.json')
    response = await taxi_geosharing.post(
        '4.0/geosharing/v1/syncpos', request, headers=PA_HEADERS,
    )
    expected = load_json('syncpos_response_last_seen.json')
    del expected['last_seen']
    assert response.status_code == 200
    assert response.json() == expected
