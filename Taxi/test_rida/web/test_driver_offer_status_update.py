import datetime
from typing import Any
from typing import Dict
from typing import List

import pytest

from test_rida import helpers


_NOW = datetime.datetime(2020, 2, 26, 13, 50)


async def test_driver_offer_status_update(
        web_app, web_app_client, get_stats_by_label_values,
):
    headers = helpers.get_auth_headers(user_id=1234)
    response = await web_app_client.post(
        '/v3/driver/offer/status/update',
        headers=headers,
        json={
            'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F',
            'status': 'WAITING',
            'position': [56.45, 45.56],
            'cancel_reason_id': 1,
        },
    )
    assert response.status == 200
    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'offers.status_change'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {'sensor': 'offers.status_change', 'status': 'WAITING'},
            'value': 1,
            'timestamp': None,
        },
    ]


@pytest.mark.parametrize(
    ['offer_guid', 'expected_status'],
    [
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F', 200, id='mongo_offer',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G',
            200,
            id='pg_canceled_offer',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5X',
            400,
            id='not_suitable_status',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFB0001',
            400,
            id='driver_does_not_have_access_to_offer',
        ),
    ],
)
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_pg_offer.sql'])
async def test_driver_cancel(web_app_client, offer_guid, expected_status):
    headers = helpers.get_auth_headers(user_id=1234)
    response = await web_app_client.post(
        '/v3/driver/offer/status/update',
        headers=headers,
        json={
            'offer_guid': offer_guid,
            'status': 'DRIVER_CANCELLED',
            'position': [56.45, 45.56],
            'cancel_reason_id': 1,
        },
    )
    assert response.status == expected_status


async def _get_user_trips(web_app, user_guid: str) -> int:
    async with web_app['context'].pg.ro_pool.acquire() as connection:
        record = await connection.fetchrow(
            f'SELECT * FROM users WHERE guid=\'{user_guid}\'',
        )
        return record['number_of_trips']


async def _set_user_trips(
        web_app, user_guid: str, user_trips_count: int,
) -> None:
    query = f"""
    UPDATE users
    SET number_of_trips = {user_trips_count}
    WHERE guid='{user_guid}'
    """
    async with web_app['context'].pg.rw_pool.acquire() as connection:
        await connection.execute(query)


async def _get_driver_trips(web_app, driver_guid: str) -> int:
    async with web_app['context'].pg.ro_pool.acquire() as connection:
        record = await connection.fetchrow(
            f'SELECT * FROM drivers WHERE guid=\'{driver_guid}\'',
        )
        return record['number_of_trips']


def _add_offer_bids(
        mongodb, offer_guid: str, bids_count: int,
) -> List[Dict[str, Any]]:
    bids = []
    for bid_num in range(bids_count):
        bid = {
            'bid_guid': f'{bid_num}'.rjust(36, '0'),
            'offer_guid': offer_guid,
            'user_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
            'driver_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
            'proposed_price': 100,
            'accepted_bid': '0',
            'bid_status': 'PENDING',
            'created_at': datetime.datetime(2022, 4, 29, 10, 12, 14),
            'updated_at': datetime.datetime(2022, 4, 29, 10, 12, 14),
            'expired_at': datetime.datetime(2022, 4, 29, 10, 12, 14),
            'price_sequence': 1,
            'is_shown': False,
        }
        mongodb.rida_bids.insert_one(bid)
        bids.append(bid)
    return bids


async def _check_bid_exported(web_app, bid: Dict[str, Any]) -> None:
    async with web_app['context'].pg.ro_pool.acquire() as connection:
        bid_guid = bid['bid_guid']
        record = await connection.fetchrow(
            f'SELECT * from bids WHERE bid_guid=\'{bid_guid}\'',
        )
    pg_bid = {k: v for k, v in record.items()}

    # Fix fields that differ from mongo to postgres
    bid.pop('updated_at', None)
    pg_bid.pop('updated_at', None)  # set in postgres query
    bid.pop('expired_at', None)
    bid.pop('_id', None)
    pg_bid.pop('id', None)
    pg_bid['proposed_price'] = float(pg_bid['proposed_price'])

    assert pg_bid == bid


async def _check_bids_exported(web_app, bids: List[Dict[str, Any]]) -> None:
    for bid in bids:
        await _check_bid_exported(web_app, bid)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    RIDA_ADJUST_SETTINGS=dict(
        rida_android=dict(
            app_token='rida_android_token',
            event_tokens=dict(
                rider_first_order_completed='rider_first_order_done',
                rider_order_completed='rider_order_done',
                driver_first_order_completed='driver_first_order_done',
                driver_order_completed='driver_order_done',
            ),
        ),
    ),
)
@pytest.mark.parametrize(
    'bids_count',
    [
        pytest.param(0, id='no_bids'),
        pytest.param(1, id='one_bid'),
        pytest.param(3, id='multiple_bids'),
    ],
)
async def test_offer_complete(
        web_app,
        web_app_client,
        mongodb,
        get_stats_by_label_values,
        stq,
        bids_count: int,
):

    offer_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5X'
    passenger_user_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5E'
    driver_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'
    driver_user_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B'
    bids = _add_offer_bids(mongodb, offer_guid, bids_count)
    await _set_user_trips(web_app, passenger_user_guid, 3)
    old_user_trips = await _get_user_trips(web_app, passenger_user_guid)
    old_driver_trips = await _get_driver_trips(web_app, driver_guid)

    response = await web_app_client.post(
        '/v3/driver/offer/status/update',
        headers=helpers.get_auth_headers(user_id=1234),
        json={
            'offer_guid': offer_guid,
            'status': 'COMPLETE',
            'position': [56.45, 45.56],
        },
    )
    assert response.status == 200

    new_user_trips = await _get_user_trips(web_app, passenger_user_guid)
    new_driver_trips = await _get_driver_trips(web_app, driver_guid)

    assert new_user_trips == old_user_trips + 1
    assert new_driver_trips == old_driver_trips + 1
    await _check_bids_exported(web_app, bids)

    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'offers.status_change'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {'sensor': 'offers.status_change', 'status': 'COMPLETE'},
            'value': 1,
            'timestamp': None,
        },
    ]

    adjust_queue = stq.rida_adjust_events
    assert adjust_queue.times_called == 4
    stq_calls_kwargs = [adjust_queue.next_call()['kwargs'] for _ in range(4)]
    stq_calls_kwargs.sort(key=lambda kwargs: kwargs['event_token'])
    assert stq_calls_kwargs[0] == {
        'application': 'rida_android',
        'app_token': 'rida_android_token',
        'user_guid': driver_user_guid,
        'event_token': 'driver_first_order_done',
        'created_at': {'$date': 1582725000000},
        'offer_guid': offer_guid,
    }
    assert stq_calls_kwargs[1] == {
        'application': 'rida_android',
        'app_token': 'rida_android_token',
        'user_guid': driver_user_guid,
        'event_token': 'driver_order_done',
        'created_at': {'$date': 1582725000000},
        'offer_guid': offer_guid,
    }
    assert stq_calls_kwargs[2] == {
        'application': 'rida_android',
        'app_token': 'rida_android_token',
        'user_guid': passenger_user_guid,
        'event_token': 'rider_first_order_done',
        'created_at': {'$date': 1582725000000},
        'offer_guid': offer_guid,
    }
    assert stq_calls_kwargs[3] == {
        'application': 'rida_android',
        'app_token': 'rida_android_token',
        'user_guid': passenger_user_guid,
        'event_token': 'rider_order_done',
        'created_at': {'$date': 1582725000000},
        'offer_guid': offer_guid,
    }
