import dataclasses
import datetime
from typing import Any
from typing import Dict
from typing import List

import pytest

from rida.stq import send_notifications
from test_rida import experiments_utils
from test_rida import helpers


_NOW = datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc)
LAST_UPDATED_DATE = datetime.datetime(
    2020, 2, 26, 13, 49, tzinfo=datetime.timezone.utc,
)


@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_offers.sql'])
@pytest.mark.mongodb_collections('rida_drivers', 'rida_offers')
@pytest.mark.filldb()
async def test_finished_offer_info(web_app_client, mongodb):
    response = await web_app_client.post(
        '/v3/driver/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G'},
    )
    assert response.status == 200


async def _verify_number_of_nearest_offers(
        web_app_client, user_id: int, driver_guid: str, expected: int,
):
    response = await web_app_client.post(
        '/v3/driver/offer/nearest',
        headers=helpers.get_auth_headers(user_id=user_id),
        json={'driver_guid': driver_guid},
    )
    assert response.status == 200
    offers = (await response.json())['data']['offers']
    assert len(offers) == expected


_OFFERS = [
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G',
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F',
]


@pytest.mark.now(LAST_UPDATED_DATE.isoformat())
@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/nearest')
@experiments_utils.get_distance_info_config(
    'ruler',
    'v3/driver/offer/nearest',
    user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5E',
)
@pytest.mark.mongodb_collections('rida_drivers', 'rida_offers')
@pytest.mark.filldb()
@pytest.mark.parametrize(
    'experiment_enabled',
    [
        pytest.param(
            True,
            marks=[
                experiments_utils.get_sequential_offers_exp(user_guid)
                for user_guid in [
                    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
                    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5E',
                ]
            ],
            id='enabled experiment',
        ),
        pytest.param(False, id='disabled experiment'),
    ],
)
async def test_offer_info_seen(web_app_client, experiment_enabled: bool):
    drivers = [
        (1234, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B-driver'),
        (5678, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5E-driver'),
        (1234, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B-driver'),
    ]
    for driver in drivers:
        await _verify_number_of_nearest_offers(
            web_app_client,
            driver[0],
            driver[1],
            1 if experiment_enabled else len(_OFFERS),
        )
    for i, offer_guid in enumerate(_OFFERS):
        for driver in drivers:
            response = await web_app_client.post(
                '/v3/driver/offer/info',
                headers=helpers.get_auth_headers(user_id=driver[0]),
                json={'offer_guid': offer_guid},
            )
            assert response.status == 200
            if not experiment_enabled:
                expected_offers_count = len(_OFFERS)
            else:
                # if all offers have been seen we should not see any offers
                if i == len(_OFFERS) - 1:
                    expected_offers_count = 0
                # otherwise we should see only one offer
                else:
                    expected_offers_count = 1
            await _verify_number_of_nearest_offers(
                web_app_client, driver[0], driver[1], expected_offers_count,
            )


@pytest.mark.now(LAST_UPDATED_DATE.isoformat())
@experiments_utils.get_sequential_offers_exp(
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
)
@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/nearest')
@pytest.mark.mongodb_collections('rida_drivers', 'rida_offers')
@pytest.mark.filldb()
async def test_price_change_seen(web_app_client):
    driver = (1234, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B-driver')
    for offer_guid in _OFFERS:
        response = await web_app_client.post(
            '/v3/driver/offer/info',
            headers=helpers.get_auth_headers(user_id=driver[0]),
            json={'offer_guid': offer_guid},
        )
        assert response.status == 200
    await _verify_number_of_nearest_offers(
        web_app_client, driver[0], driver[1], 0,
    )

    response = await web_app_client.post(
        '/v1/offer/priceChange',
        headers=helpers.get_auth_headers(1449),
        json={'offer_guid': _OFFERS[0], 'initial_price': 35900},
    )
    assert response.status == 200

    await _verify_number_of_nearest_offers(
        web_app_client, driver[0], driver[1], 1,
    )


@pytest.mark.now(LAST_UPDATED_DATE.isoformat())
@pytest.mark.parametrize(
    'nearest_offers_after_seen',
    [
        pytest.param(
            1,
            marks=[
                experiments_utils.get_sequential_offers_exp(
                    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
                    value={
                        'enabled': True,
                        'repeated_offers': {'enabled': True},
                    },
                ),
            ],
            id='always repeat orders',
        ),
        pytest.param(
            0,
            marks=[
                experiments_utils.get_sequential_offers_exp(
                    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
                    value={
                        'enabled': True,
                        'repeated_offers': {'enabled': True, 'lower_bound': 3},
                    },
                ),
            ],
            id='repeat orders only when there are at least 3 of them near',
        ),
    ],
)
@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/nearest')
@pytest.mark.mongodb_collections('rida_drivers', 'rida_offers')
@pytest.mark.filldb()
async def test_repeated_offers(web_app_client, nearest_offers_after_seen: int):
    driver = (1234, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B-driver')
    await _verify_number_of_nearest_offers(
        web_app_client, driver[0], driver[1], 1,
    )
    for offer_guid in _OFFERS:
        response = await web_app_client.post(
            '/v3/driver/offer/info',
            headers=helpers.get_auth_headers(user_id=driver[0]),
            json={'offer_guid': offer_guid},
        )
        assert response.status == 200
    await _verify_number_of_nearest_offers(
        web_app_client, driver[0], driver[1], nearest_offers_after_seen,
    )


@pytest.mark.now(LAST_UPDATED_DATE.isoformat())
@experiments_utils.get_sequential_offers_exp(
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
    value={'enabled': True, 'repeated_offers': {'enabled': True}},
)
@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/nearest')
@pytest.mark.mongodb_collections('rida_drivers', 'rida_offers')
@pytest.mark.filldb()
async def test_offers_repetion_several_times(web_app_client):
    driver = (1234, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B-driver')
    await _verify_number_of_nearest_offers(
        web_app_client, driver[0], driver[1], 1,
    )
    for _ in range(5):
        for offer_guid in reversed(_OFFERS):
            response = await web_app_client.post(
                '/v3/driver/offer/nearest',
                headers=helpers.get_auth_headers(user_id=driver[0]),
                json={'driver_guid': driver[1]},
            )
            assert response.status == 200
            assert (await response.json())['data']['offers'][0][
                'offer_guid'
            ] == offer_guid
            response = await web_app_client.post(
                '/v3/driver/offer/info',
                headers=helpers.get_auth_headers(user_id=driver[0]),
                json={'offer_guid': offer_guid},
            )
            assert response.status == 200


@dataclasses.dataclass
class _Offer:
    offer_guid: str
    position: List[float]
    user_id: int


_NEAR_OFFER = _Offer(
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5I', [40.2104517, 44.5288845], 3456,
)
_FAR_OFFER = _Offer(
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5O', [40.2104519, 44.5288845], 1450,
)


async def _create_offer(web_app_client, offer: _Offer):
    request_body = {
        'offer_guid': offer.offer_guid,
        'point_a': 'point_a',
        'point_b': 'point_b',
        'point_a_lat': offer.position[1],
        'point_a_long': offer.position[0],
        'point_b_lat': 34.432,
        'point_b_long': 56.322,
        'points_data': 'points_data',
        'entrance': '1',
        'comment': 'comment',
        'initial_price': 35.5,
        'payment_method_id': 1,
        'payment_method': 'cash',
        'zone_id': 34,
        'country_id': 87,
        'direction_map_url': 'direction_map_url',
    }
    response = await web_app_client.post(
        '/v3/user/offer/create',
        headers=helpers.get_auth_headers(user_id=offer.user_id),
        json=request_body,
    )
    assert response.status == 200


def _get_push_value(
        offer_guid: str, intent: str, push_id: str,
) -> Dict[str, Any]:
    push = {
        'id': push_id,
        'firebase_token': 'firebase_token',
        'title': 'New ride',
        'body': 'New ride suggestion for 500  point_a - point_b',
        'data': {'offer_guid': offer_guid, 'push_type': 1},
    }
    if intent == 'new_offer':
        push['sound'] = {'apns': 'new_order.caf'}
        push['notification_channel'] = {'android': 'tada_new_order_chanel'}
    return push


async def _start_stq_task(stq3_context, push_intent, offer):
    await send_notifications.task(
        stq3_context,
        intent=push_intent,
        offer_guid=offer.offer_guid,
        user_guid='some-user-guid',
        start_point=offer.position,
        point_a='point_a',
        point_b='point_b',
        initial_price=500.4,
    )


@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/nearest')
@experiments_utils.get_sequential_offers_exp(
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
)
@pytest.mark.config(
    RIDA_NOTIFICATION_OVERRIDES={
        'new_offer_push_expired': {
            'is_enabled': True,
            'android': {'min_build_number': 100111},
            'iphone': {'min_build_number': 100500},
        },
    },
)
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
        'notifications.driver.new_offer_push_expired.title': {
            'en': 'This offer has expired',
        },
    },
)
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_offers.sql'])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize('push_intent', ['new_offer', 'price_changed'])
@pytest.mark.parametrize(
    'offers_sequence, see_first_offer_before_creating, '
    'change_price_in_the_end',
    [
        pytest.param(
            [(_NEAR_OFFER, True), (_FAR_OFFER, False)],
            False,
            False,
            id='near then far',
        ),
        pytest.param(
            [(_FAR_OFFER, True), (_NEAR_OFFER, True)],
            False,
            False,
            id='far then near',
        ),
        pytest.param(
            [(_NEAR_OFFER, True), (_FAR_OFFER, True)],
            True,
            False,
            id='near then see offer then far',
        ),
        pytest.param(
            [(_FAR_OFFER, True), (_NEAR_OFFER, True)],
            False,
            True,
            id='far then near then price change',
        ),
    ],
)
async def test_push_sending_and_killing(
        web_app_client,
        stq3_context,
        offers_sequence,
        see_first_offer_before_creating: bool,
        push_intent: str,
        change_price_in_the_end: bool,
        validate_stq3_sent_notifications,
):
    offer = offers_sequence[0][0]
    await _create_offer(web_app_client, offer)
    await _start_stq_task(stq3_context, push_intent, offer)

    if see_first_offer_before_creating:
        await web_app_client.post(
            '/v3/driver/offer/info',
            headers=helpers.get_auth_headers(user_id=1234),
            json={'offer_guid': offer.offer_guid},
        )

    expected_notifications = []
    push_id = 0
    should_notify_first = offers_sequence[0][1]
    if should_notify_first:
        expected_notifications.append(
            _get_push_value(
                offer.offer_guid,
                push_intent,
                f'0000000000000000000000000000000{push_id}',
            ),
        )
        push_id += 1

    offer = offers_sequence[1][0]
    await _create_offer(web_app_client, offer)
    await _start_stq_task(stq3_context, push_intent, offer)
    should_notify_second = offers_sequence[1][1]
    if should_notify_second:
        if should_notify_first:
            expected_notifications.append(
                {
                    'id': f'0000000000000000000000000000000{push_id}',
                    'firebase_token': 'firebase_token',
                    'data': {
                        'push_type': 666,
                        'push_id': '00000000000000000000000000000000',
                    },
                },
            )
            push_id += 1
        expected_notifications.append(
            _get_push_value(
                offer.offer_guid,
                push_intent,
                f'0000000000000000000000000000000{push_id}',
            ),
        )
        push_id += 1

    if change_price_in_the_end:
        await _start_stq_task(stq3_context, 'price_changed', offer)
        expected_notifications.append(
            {
                'id': f'0000000000000000000000000000000{push_id}',
                'firebase_token': 'firebase_token',
                'data': {
                    'push_type': 666,
                    'push_id': f'0000000000000000000000000000000{push_id-1}',
                },
            },
        )
        push_id += 1
        expected_notifications.append(
            _get_push_value(
                offer.offer_guid,
                'price_changed',
                f'0000000000000000000000000000000{push_id}',
            ),
        )
        push_id += 1

    validate_stq3_sent_notifications(
        expected_times_called=len(expected_notifications),
        expected_notifications=expected_notifications,
    )
