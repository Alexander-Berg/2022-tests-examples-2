import copy
import datetime

import pytest

from tests_grocery_marketing import common
from tests_grocery_marketing import configs
from tests_grocery_marketing import models

DEPOT_ID = '194293'
ITEM_ID = f'de-{DEPOT_ID}'
UTC_TZ = datetime.timezone.utc
NOW_DT = datetime.datetime(2020, 3, 13, 7, 19, 00, tzinfo=UTC_TZ)

NOW_TIME = '2020-01-01T11:00:00+0300'
RESTART_NOW_TIME = '2020-01-01T08:10:00+00:00'
POSTPONE_NOW_TIME = '2020-01-01T09:00:00+00:00'

PREV_LAST_SEEN_CREATED_TIME = '2020-03-13T07:20:00+00:00'
LAST_SEEN_CREATED_TIME = '2020-03-13T07:22:00+00:00'

GROCERY_MARKETING_PG_TIMEOUTS = {
    '__default__': {'execute_timeout_ms': 500, 'statement_timeout_ms': 250},
    'get_depot_subscriptions': {
        'execute_timeout_ms': 4000,
        'statement_timeout_ms': 2000,
    },
}

GET_DEPOT_SUBSCRIPTIONS_TIMEOUTS = 'get_depot_subscriptions_timeouts'


def _add_depot(grocery_depots):
    depot = grocery_depots.add_depot(
        depot_test_id=1, legacy_depot_id=DEPOT_ID, auto_add_zone=False,
    )
    depot.add_zone(
        geozone={
            'type': 'MultiPolygon',
            'coordinates': [
                [
                    [
                        {'lat': 4.0, 'lon': 3.0},
                        {'lat': 5.0, 'lon': 5.0},
                        {'lat': 2.0, 'lon': 7.0},
                        {'lat': 10.0, 'lon': 8.0},
                        {'lat': 9.0, 'lon': 1.0},
                        {'lat': 4.0, 'lon': 3.0},
                    ],
                ],
                [
                    [
                        {'lat': 1.0, 'lon': 2.0},
                        {'lat': 1.0, 'lon': 3.0},
                        {'lat': 2.0, 'lon': 3.0},
                        {'lat': 2.0, 'lon': 2.0},
                        {'lat': 1.0, 'lon': 2.0},
                    ],
                ],
            ],
        },
    )


async def _add_subscription(
        taxi_grocery_marketing,
        *,
        location,
        subscribe,
        taxi_user_id,
        phone=None,
):
    headers = copy.deepcopy(common.DEFAULT_USER_HEADERS)
    headers['X-YaTaxi-UserId'] = taxi_user_id
    headers['X-YaTaxi-Session'] = f'taxi:{taxi_user_id}'

    response = await taxi_grocery_marketing.post(
        '/lavka/v1/marketing/v1/coming-soon/subscribe',
        json={
            'position': {'location': location, 'depot_id': DEPOT_ID},
            'subscribe': subscribe,
            'phone_number': phone,
        },
        headers=headers,
    )

    assert response.status_code == 200


async def _add_subscription_without_taxi_user_id(
        taxi_grocery_marketing, *, location, subscribe,
):
    headers = copy.deepcopy(common.DEFAULT_USER_HEADERS)
    del headers['X-YaTaxi-UserId']
    headers['X-YaTaxi-Session'] = f'eats:some_eats_id'

    response = await taxi_grocery_marketing.post(
        '/lavka/v1/marketing/v1/coming-soon/subscribe',
        json={
            'position': {'location': location, 'depot_id': DEPOT_ID},
            'subscribe': subscribe,
        },
        headers=headers,
    )

    assert response.status_code == 200


@pytest.mark.now(NOW_TIME)
@pytest.mark.config(
    GROCERY_MARKETING_PG_TIMEOUTS=GROCERY_MARKETING_PG_TIMEOUTS,
)
async def test_basic(
        taxi_grocery_marketing,
        grocery_depots,
        processing,
        pgsql,
        mocked_time,
        personal,
        testpoint,
):
    _add_depot(grocery_depots)

    ok_locations = [
        ([5.0, 5.0], True, '0'),
        ([5.0, 7.0], True, '1'),
        ([2.0, 8.0], True, '2'),
        ([2.5, 1.5], True, '3'),
        ([3.0, 8.0], False, '4'),
    ]

    bad_locations = [
        ([2.0, 5.0], True, '5'),
        ([5.0, 3.0], True, '6'),
        ([5.0, 1.0], True, '7'),
        ([5.0, 10.0], True, '8'),
    ]

    phone = '+78005553535'
    personal_phone_id = 'some_personal_phone_id'
    personal.check_request(phone=phone, personal_phone_id=personal_phone_id)

    for location, subscribe, taxi_user_id in ok_locations:
        await _add_subscription(
            taxi_grocery_marketing,
            location=location,
            subscribe=subscribe,
            taxi_user_id=taxi_user_id,
            phone=phone,
        )

    for location, subscribe, taxi_user_id in bad_locations:
        await _add_subscription(
            taxi_grocery_marketing,
            location=location,
            subscribe=subscribe,
            taxi_user_id=taxi_user_id,
        )

    @testpoint(GET_DEPOT_SUBSCRIPTIONS_TIMEOUTS)
    def get_timeouts(data):
        return data

    response = await taxi_grocery_marketing.post(
        '/processing/v1/marketing/v1/event/depot/opened',
        json={'depot_id': DEPOT_ID, 'item_id': ITEM_ID},
    )

    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 2

    notification_event = events[0]
    restart_event = events[1]

    assert notification_event.payload['reason'] == 'opened_depot_notification'
    assert notification_event.payload['item_id'] == ITEM_ID
    assert notification_event.payload['depot_id'] == DEPOT_ID
    assert notification_event.payload['batch_number'] == 1

    notification_event.payload['users'].sort(
        key=lambda user: user['taxi_user_id'],
    )
    assert notification_event.payload['users'] == [
        {
            'taxi_user_id': taxi_user_id,
            'personal_phone_id': personal_phone_id,
            'locale': 'en',
            'application': 'android',
        }
        for location, subscribe, taxi_user_id in ok_locations
        if subscribe
    ]

    assert restart_event.payload['reason'] == 'opened_depot'
    assert restart_event.payload['item_id'] == ITEM_ID
    assert restart_event.payload['depot_id'] == DEPOT_ID
    assert restart_event.payload['iteration_id'] == 2

    for location, subscribe, taxi_user_id in ok_locations:
        subscription = models.ComingSoonSubscription.fetch(
            pgsql,
            lat=location[1],
            lon=location[0],
            session=f'taxi:{taxi_user_id}',
        )
        if subscribe:
            assert subscription.notified is True
            assert subscription.processed is True
            assert subscription.subscribe is True
            assert subscription.processed_depot_id == DEPOT_ID
            assert subscription.processed_item_id == ITEM_ID
        else:
            assert subscription.notified is False
            assert subscription.processed is None
            assert subscription.subscribe is False
            assert subscription.processed_depot_id is None
            assert subscription.processed_item_id is None

    for location, subscribe, taxi_user_id in bad_locations:
        subscription = models.ComingSoonSubscription.fetch(
            pgsql,
            lat=location[1],
            lon=location[0],
            session=f'taxi:{taxi_user_id}',
        )
        assert subscription.notified is False
        assert subscription.processed is None
        assert subscription.subscribe == subscribe

    timeouts = (await get_timeouts.wait_call())['data']
    assert (
        timeouts['execute']
        == GROCERY_MARKETING_PG_TIMEOUTS['get_depot_subscriptions'][
            'execute_timeout_ms'
        ]
    )
    assert (
        timeouts['statement']
        == GROCERY_MARKETING_PG_TIMEOUTS['get_depot_subscriptions'][
            'statement_timeout_ms'
        ]
    )


@pytest.mark.now(NOW_TIME)
async def test_several_subscriptions(
        taxi_grocery_marketing, grocery_depots, processing, pgsql, mocked_time,
):
    taxi_user_id = 'some_user_id'
    not_last_subscribe_location = [5.0, 7.0]
    last_subscribe_location = [5.0, 5.0]
    last_not_subscribe_location = [2.0, 8.0]

    _add_depot(grocery_depots)

    # Not last subscription with subscribe
    mocked_time.set(NOW_DT)
    await _add_subscription(
        taxi_grocery_marketing,
        location=not_last_subscribe_location,
        subscribe=True,
        taxi_user_id=taxi_user_id,
    )

    # Last subscription with subscribe
    mocked_time.set(NOW_DT + datetime.timedelta(minutes=1))
    await _add_subscription(
        taxi_grocery_marketing,
        location=last_subscribe_location,
        subscribe=True,
        taxi_user_id=taxi_user_id,
    )

    # Last subscription without subscribe
    mocked_time.set(NOW_DT + datetime.timedelta(minutes=2))
    await _add_subscription(
        taxi_grocery_marketing,
        location=last_not_subscribe_location,
        subscribe=False,
        taxi_user_id=taxi_user_id,
    )

    response = await taxi_grocery_marketing.post(
        '/processing/v1/marketing/v1/event/depot/opened',
        json={'depot_id': DEPOT_ID, 'item_id': ITEM_ID},
    )
    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 2

    notification_event = events[0]

    assert notification_event.payload['users'] == [
        {
            'taxi_user_id': taxi_user_id,
            'locale': 'en',
            'application': 'android',
        },
    ]

    subscription = models.ComingSoonSubscription.fetch(
        pgsql,
        lat=last_subscribe_location[1],
        lon=last_subscribe_location[0],
        session=f'taxi:{taxi_user_id}',
    )
    assert subscription.notified is True
    assert subscription.processed is True

    subscription = models.ComingSoonSubscription.fetch(
        pgsql,
        lat=not_last_subscribe_location[1],
        lon=not_last_subscribe_location[0],
        session=f'taxi:{taxi_user_id}',
    )
    assert subscription.notified is False
    assert subscription.processed is True

    subscription = models.ComingSoonSubscription.fetch(
        pgsql,
        lat=last_not_subscribe_location[1],
        lon=last_not_subscribe_location[0],
        session=f'taxi:{taxi_user_id}',
    )
    assert subscription.notified is False
    assert subscription.processed is True


@pytest.mark.now(NOW_TIME)
async def test_stop_when_no_more(
        taxi_grocery_marketing, grocery_depots, processing, pgsql, mocked_time,
):
    taxi_user_id = 'some_user_id'
    not_last_location = [5.0, 7.0]
    last_location = [5.0, 5.0]

    _add_depot(grocery_depots)

    mocked_time.set(NOW_DT)
    await _add_subscription(
        taxi_grocery_marketing,
        location=not_last_location,
        subscribe=True,
        taxi_user_id=taxi_user_id,
    )

    mocked_time.set(NOW_DT + datetime.timedelta(minutes=1))
    await _add_subscription(
        taxi_grocery_marketing,
        location=last_location,
        subscribe=True,
        taxi_user_id=taxi_user_id,
    )

    response = await taxi_grocery_marketing.post(
        '/processing/v1/marketing/v1/event/depot/opened',
        json={'depot_id': DEPOT_ID, 'item_id': ITEM_ID},
    )
    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 2

    notification_event = events[0]

    assert notification_event.payload['users'] == [
        {
            'taxi_user_id': taxi_user_id,
            'locale': 'en',
            'application': 'android',
        },
    ]

    subscription = models.ComingSoonSubscription.fetch(
        pgsql,
        lat=last_location[1],
        lon=last_location[0],
        session=f'taxi:{taxi_user_id}',
    )
    assert subscription.notified is True
    assert subscription.processed is True

    subscription = models.ComingSoonSubscription.fetch(
        pgsql,
        lat=not_last_location[1],
        lon=not_last_location[0],
        session=f'taxi:{taxi_user_id}',
    )
    assert subscription.notified is False
    assert subscription.processed is True

    response = await taxi_grocery_marketing.post(
        '/processing/v1/marketing/v1/event/depot/opened',
        json={'depot_id': DEPOT_ID, 'item_id': ITEM_ID, 'iteration_id': 2},
    )
    assert response.status_code == 200

    events = list(
        processing.events(scope='grocery', queue='processing_tasks'),
    )[2:]

    assert not events


@pytest.mark.now(NOW_TIME)
@configs.GROCERY_MARKETING_OPENED_DEPOT_PROCESSING
async def test_batch_num(
        taxi_grocery_marketing, grocery_depots, processing, pgsql,
):
    _add_depot(grocery_depots)

    locations = [([5.0, 5.0], '0'), ([5.0, 7.0], '1'), ([2.0, 8.0], '2')]

    for location, taxi_user_id in locations:
        await _add_subscription(
            taxi_grocery_marketing,
            location=location,
            subscribe=True,
            taxi_user_id=taxi_user_id,
        )

    response = await taxi_grocery_marketing.post(
        '/processing/v1/marketing/v1/event/depot/opened',
        json={'depot_id': DEPOT_ID, 'item_id': ITEM_ID},
    )

    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 2

    notification_event = events[0]
    restart_event = events[1]

    assert notification_event.payload['reason'] == 'opened_depot_notification'
    assert notification_event.payload['item_id'] == ITEM_ID
    assert notification_event.payload['depot_id'] == DEPOT_ID
    assert notification_event.payload['batch_number'] == 1

    notification_event.payload['users'].sort(
        key=lambda user: user['taxi_user_id'],
    )
    assert notification_event.payload['users'] == [
        {
            'taxi_user_id': taxi_user_id,
            'locale': 'en',
            'application': 'android',
        }
        for location, taxi_user_id in locations[:2]
    ]

    assert restart_event.payload['reason'] == 'opened_depot'
    assert restart_event.payload['item_id'] == ITEM_ID
    assert restart_event.payload['depot_id'] == DEPOT_ID
    assert restart_event.payload['iteration_id'] == 2

    for location, taxi_user_id in locations[:2]:
        subscription = models.ComingSoonSubscription.fetch(
            pgsql,
            lat=location[1],
            lon=location[0],
            session=f'taxi:{taxi_user_id}',
        )

        assert subscription.notified is True
        assert subscription.processed is True

    for location, taxi_user_id in locations[2:]:
        subscription = models.ComingSoonSubscription.fetch(
            pgsql,
            lat=location[1],
            lon=location[0],
            session=f'taxi:{taxi_user_id}',
        )
        assert subscription.notified is False
        assert subscription.processed is None


@pytest.mark.now(NOW_TIME)
@configs.GROCERY_MARKETING_OPENED_DEPOT_PROCESSING
async def test_restart_with_due(
        taxi_grocery_marketing, grocery_depots, processing, pgsql,
):
    _add_depot(grocery_depots)

    locations = [([5.0, 5.0], '0'), ([5.0, 7.0], '1'), ([2.0, 8.0], '2')]

    for location, taxi_user_id in locations:
        await _add_subscription(
            taxi_grocery_marketing,
            location=location,
            subscribe=True,
            taxi_user_id=taxi_user_id,
        )

    response = await taxi_grocery_marketing.post(
        '/processing/v1/marketing/v1/event/depot/opened',
        json={'depot_id': DEPOT_ID, 'item_id': ITEM_ID},
    )

    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 2

    restart_event = events[1]

    assert restart_event.payload['reason'] == 'opened_depot'
    assert restart_event.payload['item_id'] == ITEM_ID
    assert restart_event.payload['depot_id'] == DEPOT_ID
    assert restart_event.payload['iteration_id'] == 2

    assert restart_event.due == RESTART_NOW_TIME


@pytest.mark.now(NOW_TIME)
@configs.GROCERY_MARKETING_OPENED_DEPOT_PROCESSING
async def test_postpone(
        taxi_grocery_marketing, grocery_depots, processing, pgsql,
):
    _add_depot(grocery_depots)

    locations = [([5.0, 5.0], '0'), ([5.0, 7.0], '1'), ([2.0, 8.0], '2')]

    time_limit = {'start': 7, 'end': 9}

    for location, taxi_user_id in locations:
        await _add_subscription(
            taxi_grocery_marketing,
            location=location,
            subscribe=True,
            taxi_user_id=taxi_user_id,
        )

    response = await taxi_grocery_marketing.post(
        '/processing/v1/marketing/v1/event/depot/opened',
        json={
            'depot_id': DEPOT_ID,
            'item_id': ITEM_ID,
            'time_limit': time_limit,
        },
    )

    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 1

    restart_event = events[0]

    assert restart_event.payload['reason'] == 'opened_depot'
    assert restart_event.payload['item_id'] == ITEM_ID
    assert restart_event.payload['depot_id'] == DEPOT_ID
    assert restart_event.payload['iteration_id'] == 2
    assert restart_event.payload['time_limit'] == time_limit

    assert restart_event.due == POSTPONE_NOW_TIME


@pytest.mark.now(NOW_TIME)
async def test_last_seen_created(
        taxi_grocery_marketing, grocery_depots, processing, pgsql, mocked_time,
):
    _add_depot(grocery_depots)

    locations = [([5.0, 5.0], '0'), ([5.0, 7.0], '1'), ([2.0, 8.0], '2')]

    time_delta = 0
    for location, taxi_user_id in locations:
        await _add_subscription(
            taxi_grocery_marketing,
            location=location,
            subscribe=True,
            taxi_user_id=taxi_user_id,
        )

        subscription = models.ComingSoonSubscription.fetch(
            pgsql,
            lat=location[1],
            lon=location[0],
            session=f'taxi:{taxi_user_id}',
        )
        subscription.upsert(created=f'2020-03-13T07:2{time_delta}:00+00:00')

        time_delta += 1

    response = await taxi_grocery_marketing.post(
        '/processing/v1/marketing/v1/event/depot/opened',
        json={
            'depot_id': DEPOT_ID,
            'item_id': ITEM_ID,
            'last_seen_created': PREV_LAST_SEEN_CREATED_TIME,
        },
    )

    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 2

    notification_event = events[0]
    assert len(notification_event.payload['users']) == 2
    taxi_user_ids = [
        notification_event.payload['users'][0]['taxi_user_id'],
        notification_event.payload['users'][1]['taxi_user_id'],
    ]
    taxi_user_ids.sort()
    assert taxi_user_ids == ['1', '2']

    restart_event = events[1]
    assert restart_event.payload['last_seen_created'] == LAST_SEEN_CREATED_TIME


@pytest.mark.now(NOW_TIME)
async def test_no_taxi_user_id_subscription(
        taxi_grocery_marketing, grocery_depots, processing, pgsql,
):
    taxi_user_id = 'some_user_id'

    _add_depot(grocery_depots)

    await _add_subscription(
        taxi_grocery_marketing,
        location=[5.0, 5.0],
        subscribe=True,
        taxi_user_id=taxi_user_id,
    )

    await _add_subscription_without_taxi_user_id(
        taxi_grocery_marketing, location=[5.0, 7.0], subscribe=True,
    )

    response = await taxi_grocery_marketing.post(
        '/processing/v1/marketing/v1/event/depot/opened',
        json={'depot_id': DEPOT_ID, 'item_id': ITEM_ID},
    )
    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 2

    notification_event = events[0]

    assert notification_event.payload['users'] == [
        {
            'taxi_user_id': taxi_user_id,
            'locale': 'en',
            'application': 'android',
        },
    ]


@pytest.mark.now(NOW_TIME)
@configs.GROCERY_MARKETING_OPENED_DEPOT_PROCESSING
async def test_process_all(
        taxi_grocery_marketing, grocery_depots, processing, pgsql,
):
    _add_depot(grocery_depots)

    bad_locations = [([5.0, 4.0], True, '0'), ([8.0, 2.0], True, '1')]

    ok_locations = [([5.0, 5.0], True, '2'), ([5.0, 6.0], True, '3')]

    time_delta = 0

    for location, subscribe, taxi_user_id in bad_locations:
        await _add_subscription(
            taxi_grocery_marketing,
            location=location,
            subscribe=subscribe,
            taxi_user_id=taxi_user_id,
        )
        subscription = models.ComingSoonSubscription.fetch(
            pgsql,
            lat=location[1],
            lon=location[0],
            session=f'taxi:{taxi_user_id}',
        )
        subscription.upsert(created=f'2020-03-13T07:2{time_delta}:00+00:00')

    time_delta += 1

    for location, subscribe, taxi_user_id in ok_locations:
        await _add_subscription(
            taxi_grocery_marketing,
            location=location,
            subscribe=subscribe,
            taxi_user_id=taxi_user_id,
        )
        subscription = models.ComingSoonSubscription.fetch(
            pgsql,
            lat=location[1],
            lon=location[0],
            session=f'taxi:{taxi_user_id}',
        )
        subscription.upsert(created=f'2020-03-13T07:2{time_delta}:00+00:00')

    response = await taxi_grocery_marketing.post(
        '/processing/v1/marketing/v1/event/depot/opened',
        json={'depot_id': DEPOT_ID, 'item_id': ITEM_ID},
    )

    assert response.status_code == 200

    response = await taxi_grocery_marketing.post(
        '/processing/v1/marketing/v1/event/depot/opened',
        json={
            'depot_id': DEPOT_ID,
            'item_id': ITEM_ID,
            'last_seen_created': '2020-03-13T07:20:00+00:00',
        },
    )

    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 3

    first_restart_event = events[0]
    notification_event = events[1]
    second_restart_event = events[2]

    assert first_restart_event.payload['reason'] == 'opened_depot'

    assert notification_event.payload['reason'] == 'opened_depot_notification'
    assert notification_event.payload['batch_number'] == 1

    assert second_restart_event.payload['reason'] == 'opened_depot'

    notification_event.payload['users'].sort(
        key=lambda user: user['taxi_user_id'],
    )
    assert notification_event.payload['users'] == [
        {
            'taxi_user_id': taxi_user_id,
            'locale': 'en',
            'application': 'android',
        }
        for location, subscribe, taxi_user_id in ok_locations
    ]

    for location, subscribe, taxi_user_id in bad_locations:
        subscription = models.ComingSoonSubscription.fetch(
            pgsql,
            lat=location[1],
            lon=location[0],
            session=f'taxi:{taxi_user_id}',
        )
        assert subscription.notified is False
        assert subscription.processed is None
        assert subscription.subscribe is True

    for location, subscribe, taxi_user_id in ok_locations:
        subscription = models.ComingSoonSubscription.fetch(
            pgsql,
            lat=location[1],
            lon=location[0],
            session=f'taxi:{taxi_user_id}',
        )
        assert subscription.notified is True
        assert subscription.processed is True
        assert subscription.subscribe is True
