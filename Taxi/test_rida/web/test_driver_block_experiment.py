import datetime
from typing import List

import pytest

from rida.stq import send_notifications
from test_rida import experiments_utils
from test_rida import helpers

_NOW = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
_OFFERS = [
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F',
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5E',
]
_USER_GUID = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5E'
_DRIVERS = [
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D',
]
_DRIVER_USER_GUIDS = [
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G',
]


@pytest.mark.now(_NOW.isoformat())
@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/nearest')
@experiments_utils.get_distance_info_config(
    'ruler', 'v3/driver/offer/nearest', user_guid=_DRIVER_USER_GUIDS[1],
)
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_offers.sql'])
@pytest.mark.parametrize(
    'disable_stakan',
    [
        pytest.param(False, id='stakan is enabled'),
        pytest.param(
            True,
            id='stakan is disabled',
            marks=[
                experiments_utils.get_sequential_offers_exp(user_guid)
                for user_guid in _DRIVER_USER_GUIDS
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'expected_offer_guids, driver_guid, driver_user_id',
    [
        pytest.param(
            _OFFERS,
            _DRIVERS[0],
            1234,
            marks=[experiments_utils.get_driver_block_exp(_USER_GUID, 0.7, 2)],
            id='driver is good - too few cancellations',
        ),
        pytest.param(
            _OFFERS,
            _DRIVERS[0],
            1234,
            marks=[experiments_utils.get_driver_block_exp(_USER_GUID, 0.3, 7)],
            id='driver is good - too few offers',
        ),
        pytest.param(
            _OFFERS,
            _DRIVERS[1],
            1449,
            marks=[experiments_utils.get_driver_block_exp(_USER_GUID, 0.3, 7)],
            id='driver has no offers',
        ),
        pytest.param(
            _OFFERS[1:],
            _DRIVERS[0],
            1234,
            marks=[experiments_utils.get_driver_block_exp(_USER_GUID, 0.3, 2)],
            id='driver is bad',
        ),
    ],
)
async def test_driver_offer_nearest_blocked(
        taxi_rida_web,
        driver_guid: str,
        driver_user_id: int,
        expected_offer_guids: List[str],
        disable_stakan: bool,
):
    response = await taxi_rida_web.post(
        '/v3/driver/offer/nearest',
        headers=helpers.get_auth_headers(user_id=driver_user_id),
        json={'driver_guid': driver_guid},
    )
    assert response.status == 200
    data = await response.json()
    offers = data['data']['offers']
    if disable_stakan:
        expected_offer_guids = expected_offer_guids[:1]
    assert [offer['offer_guid'] for offer in offers] == expected_offer_guids


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize('intent', ['new_offer', 'price_changed'])
@pytest.mark.parametrize(
    'is_driver_bad',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=[experiments_utils.get_driver_block_exp(_USER_GUID, 0.3, 2)],
        ),
    ],
)
@pytest.mark.mongodb_collections('rida_drivers', 'rida_offers')
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_offers.sql'])
@pytest.mark.translations(
    rida={
        'notifications.driver.new_offer.title': {'en': 'New ride'},
        'notifications.driver.new_offer.body': {
            'en': (
                'New ride suggestion for {price}'
                ' {currency} {point_a} - {point_b}'
            ),
        },
        'notifications.driver.price_change.title': {'en': 'New ride'},
        'notifications.driver.price_change.body': {
            'en': (
                'New ride suggestion for {price}'
                ' {currency} {point_a} - {point_b}'
            ),
        },
    },
)
async def test_push_new_offer(
        stq3_context,
        taxi_rida_web,
        validate_stq3_sent_notifications,
        is_driver_bad: bool,
        intent: str,
):
    await send_notifications.task(
        stq3_context,
        intent=intent,
        offer_guid='some_offer_guid',
        user_guid=_USER_GUID,
        start_point=[40.2108517, 44.5281845],
        point_a='point_a',
        point_b='point_b',
        initial_price=500.4,
    )

    def get_notification(index: int):
        result = {
            'id': f'0000000000000000000000000000000{index}',
            'firebase_token': 'firebase_token',
            'title': 'New ride',
            'body': 'New ride suggestion for 500  point_a - point_b',
            'data': {'offer_guid': 'some_offer_guid', 'push_type': 1},
        }
        if intent == 'new_offer':
            result['sound'] = {'apns': 'new_order.caf'}
            result['notification_channel'] = {
                'android': 'tada_new_order_chanel',
            }
        return result

    if is_driver_bad:
        validate_stq3_sent_notifications(
            expected_notifications=[get_notification(0)],
        )
    else:
        validate_stq3_sent_notifications(
            expected_notifications=[get_notification(0), get_notification(1)],
        )
