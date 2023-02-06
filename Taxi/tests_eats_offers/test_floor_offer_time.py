import datetime


import pytest


MATCH_REQUEST = {
    'session_id': 'session-id-floor',
    'parameters': {
        'location': [4, 4],
        'delivery_time': '2019-10-31T12:00:00Z',
    },
    'need_prolong': True,
}

SET_REQUEST_EXISTING = {
    'session_id': 'session-id-floor',
    'parameters': {
        'location': [4, 4],
        'delivery_time': '2019-10-31T12:00:00Z',
    },
    'payload': {'extra-data': 'value'},
}

SET_REQUEST_CREATE = {
    'session_id': 'floor_session_new',
    'parameters': {
        'location': [4, 4],
        'delivery_time': '2019-10-31T12:00:00Z',
    },
    'payload': {'extra-data': 'value'},
}


NOW_DATETIME = datetime.datetime(
    2019, 10, 31, 11, 30, 27, tzinfo=datetime.timezone.utc,
)


@pytest.mark.parametrize(
    'expected_request_time, floor',
    [
        pytest.param(
            datetime.datetime(
                2019, 10, 31, 11, 23, 0, tzinfo=datetime.timezone.utc,
            ),
            datetime.datetime(
                2019, 10, 31, 11, 23, 10, tzinfo=datetime.timezone.utc,
            ),
            id='floor',
        ),
        pytest.param(
            datetime.datetime(
                2019, 10, 31, 11, 23, 37, tzinfo=datetime.timezone.utc,
            ),
            datetime.datetime(
                2019, 10, 31, 11, 23, 40, tzinfo=datetime.timezone.utc,
            ),
            id='don\'t floor (too early)',
        ),
        pytest.param(
            datetime.datetime(
                2019, 10, 31, 11, 23, 37, tzinfo=datetime.timezone.utc,
            ),
            None,
            id='don\'t floor (time not set)',
        ),
    ],
)
@pytest.mark.now(NOW_DATETIME.strftime('%Y-%m-%dT%H:%M:%S%z'))
async def test_offer_not_floored(
        taxi_eats_offers, expected_request_time, floor, taxi_config,
):
    config = taxi_config.get('EATS_OFFERS_FEATURE_FLAGS')
    config['floor_offer_time_since'] = floor and floor.strftime(
        '%Y-%m-%dT%H:%M:%S%z',
    )
    taxi_config.set_values({'EATS_OFFERS_FEATURE_FLAGS': config})

    response = await taxi_eats_offers.post(
        '/v1/offer/match', json=MATCH_REQUEST,
    )
    assert response.status_code == 200

    response_request_time = datetime.datetime.strptime(
        response.json()['request_time'], '%Y-%m-%dT%H:%M:%S%z',
    )

    assert response_request_time == expected_request_time


@pytest.mark.parametrize(
    'request_json, expected_request_time, floor',
    [
        pytest.param(
            SET_REQUEST_EXISTING,
            datetime.datetime(
                2019, 10, 31, 11, 23, 0, tzinfo=datetime.timezone.utc,
            ),
            datetime.datetime(
                2019, 10, 31, 11, 23, 10, tzinfo=datetime.timezone.utc,
            ),
            id='floor (existing)',
        ),
        pytest.param(
            SET_REQUEST_EXISTING,
            datetime.datetime(
                2019, 10, 31, 11, 23, 37, tzinfo=datetime.timezone.utc,
            ),
            datetime.datetime(
                2019, 10, 31, 11, 23, 40, tzinfo=datetime.timezone.utc,
            ),
            id='don\'t floor (existing, too early)',
        ),
        pytest.param(
            SET_REQUEST_EXISTING,
            datetime.datetime(
                2019, 10, 31, 11, 23, 37, tzinfo=datetime.timezone.utc,
            ),
            None,
            id='don\'t floor (existing, time not set)',
        ),
        pytest.param(
            SET_REQUEST_CREATE,
            datetime.datetime(
                2019, 10, 31, 11, 30, 00, tzinfo=datetime.timezone.utc,
            ),
            datetime.datetime(
                2019, 10, 31, 11, 30, 10, tzinfo=datetime.timezone.utc,
            ),
            id='floor (create)',
        ),
        pytest.param(
            SET_REQUEST_CREATE,
            datetime.datetime(
                2019, 10, 31, 11, 30, 27, tzinfo=datetime.timezone.utc,
            ),
            # more that hour ahead
            datetime.datetime(
                2019, 10, 31, 12, 59, 59, tzinfo=datetime.timezone.utc,
            ),
            id='don\'t floor (create, too early)',
        ),
        pytest.param(
            SET_REQUEST_CREATE,
            datetime.datetime(
                2019, 10, 31, 11, 30, 27, tzinfo=datetime.timezone.utc,
            ),
            None,
            id='don\'t floor (create, time not set)',
        ),
    ],
)
@pytest.mark.now(NOW_DATETIME.strftime('%Y-%m-%dT%H:%M:%S%z'))
async def test_base_offer_set(
        taxi_eats_offers,
        request_json,
        expected_request_time,
        floor,
        taxi_config,
):
    config = taxi_config.get('EATS_OFFERS_FEATURE_FLAGS')
    config['floor_offer_time_since'] = floor and floor.strftime(
        '%Y-%m-%dT%H:%M:%S%z',
    )

    taxi_config.set_values({'EATS_OFFERS_FEATURE_FLAGS': config})

    response = await taxi_eats_offers.post('/v1/offer/set', json=request_json)
    assert response.status_code == 200

    response_request_time = datetime.datetime.strptime(
        response.json()['request_time'], '%Y-%m-%dT%H:%M:%S%z',
    )

    # Antiflap.
    # You should not check exact value if offer have been created.
    # It's because offer is created with current time
    # and exact time of creation is unknown.
    if response.json()['status'] == 'NEW_OFFER_CREATED':
        if floor and floor < NOW_DATETIME:
            assert response_request_time.second == 0
        else:
            assert (
                response_request_time.second != 0
                or response_request_time > expected_request_time
            )
    else:
        assert response_request_time == expected_request_time
