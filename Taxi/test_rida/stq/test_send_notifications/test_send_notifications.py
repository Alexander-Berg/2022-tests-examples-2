from typing import Optional

import pytest

from rida.stq import send_notifications


async def test_missing_translations(
        stq3_context, validate_stq3_sent_notifications,
):
    # raises no errors
    await send_notifications.task(
        stq3_context,
        intent='add_bid',
        user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        price=1234,
    )
    validate_stq3_sent_notifications(expected_notifications=[])


@pytest.mark.translations(
    rida={
        'notifications.user.add_bid.title': {'en': 'Added bid'},
        'notifications.user.add_bid.body': {
            'en': 'Suggested price: {price} {currency}',
        },
    },
)
async def test_add_bid(stq3_context, validate_stq3_sent_notifications):
    await send_notifications.task(
        stq3_context,
        intent='add_bid',
        user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        price=1000.3,
        currency='RUB',
    )
    validate_stq3_sent_notifications(
        expected_notifications=[
            {
                'id': '00000000000000000000000000000000',
                'firebase_token': 'firebase_token0',
                'title': 'Added bid',
                'body': 'Suggested price: 1000 RUB',
            },
        ],
    )


@pytest.mark.translations(
    rida={
        'notifications.user.waiting_ride.title': {
            'en': 'Driver is waiting for you',
        },
    },
)
async def test_waiting_ride(stq3_context, validate_stq3_sent_notifications):
    await send_notifications.task(
        stq3_context,
        intent='waiting_ride',
        user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
    )
    validate_stq3_sent_notifications(
        expected_notifications=[
            {
                'id': '00000000000000000000000000000000',
                'firebase_token': 'firebase_token0',
                'title': 'Driver is waiting for you',
            },
        ],
    )


@pytest.mark.translations(
    rida={
        'notifications.user.driver_cancelled_waiting_ride.title': {
            'en': 'cancel_in_waiting',
        },
        'notifications.user.driver_cancelled_driving_ride.title': {
            'en': 'cancel_in_driving',
        },
    },
)
@pytest.mark.parametrize(
    ['offer_status', 'expected_times_called', 'expected_title'],
    [
        pytest.param('WAITING', 1, 'cancel_in_waiting'),
        pytest.param('DRIVING', 1, 'cancel_in_driving'),
        pytest.param('TRANSPORTING', 0, None),
    ],
)
async def test_driver_cancelled_ride(
        stq3_context,
        validate_stq3_sent_notifications,
        offer_status: str,
        expected_times_called: int,
        expected_title: Optional[str],
):
    await send_notifications.task(
        stq3_context,
        intent='driver_cancelled_ride',
        user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        offer_status=offer_status,
    )
    expected_notifications = None
    if expected_title is not None:
        expected_notifications = [
            {
                'id': '00000000000000000000000000000000',
                'firebase_token': 'firebase_token0',
                'title': expected_title,
            },
        ]
    else:
        expected_notifications = []
    validate_stq3_sent_notifications(
        expected_notifications=expected_notifications,
        expected_times_called=0 if not expected_notifications else 1,
    )


@pytest.mark.mongodb_collections('rida_drivers')
@pytest.mark.filldb()
@pytest.mark.translations(
    rida={
        'notifications.driver.passenger_accept_bid.title': {
            'en': 'Bid accepted',
        },
        'notifications.driver.passenger_accept_bid.body': {
            'en': 'Pick up the passenger',
        },
    },
)
async def test_passenger_accept_bid(
        stq3_context, validate_stq3_sent_notifications,
):
    await send_notifications.task(
        stq3_context,
        intent='passenger_accept_bid',
        driver_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
    )
    validate_stq3_sent_notifications(
        expected_notifications=[
            {
                'id': '00000000000000000000000000000000',
                'firebase_token': 'firebase_token0',
                'title': 'Bid accepted',
                'body': 'Pick up the passenger',
            },
        ],
    )


@pytest.mark.mongodb_collections('rida_drivers', 'rida_bids')
@pytest.mark.filldb()
@pytest.mark.translations(
    rida={
        'notifications.driver.passenger_accept_another_driver.title': {
            'en': 'Chose another driver',
        },
        'notifications.driver.passenger_accept_another_driver.body': {
            'en': 'Sorry, the passenger chose another driver',
        },
    },
)
async def test_passenger_accept_another_driver(
        stq3_context, validate_stq3_sent_notifications,
):
    await send_notifications.task(
        stq3_context,
        intent='passenger_accept_another_driver',
        bid={
            'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D',
            'price_sequence': 1,
        },
    )
    validate_stq3_sent_notifications(
        expected_notifications=[
            {
                'id': str(i).rjust(32, '0'),
                'firebase_token': f'firebase_token{i}',
                'title': 'Chose another driver',
                'body': 'Sorry, the passenger chose another driver',
            }
            for i in range(2)
        ],
    )


@pytest.mark.mongodb_collections('rida_drivers')
@pytest.mark.filldb()
@pytest.mark.translations(
    rida={
        'notifications.driver.passenger_declined_bid.title': {
            'en': 'Bid declined',
        },
        'notifications.driver.passenger_declined_bid.body': {
            'en': 'Sorry, passenger declined your offer',
        },
    },
)
async def test_passenger_declined_bid(
        stq3_context, validate_stq3_sent_notifications,
):
    await send_notifications.task(
        stq3_context,
        intent='passenger_declined_bid',
        driver_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
    )
    validate_stq3_sent_notifications(
        expected_notifications=[
            {
                'id': '00000000000000000000000000000000',
                'firebase_token': 'firebase_token0',
                'title': 'Bid declined',
                'body': 'Sorry, passenger declined your offer',
            },
        ],
    )


@pytest.mark.mongodb_collections('rida_drivers')
@pytest.mark.filldb()
@pytest.mark.translations(
    rida={
        'notifications.driver.passenger_offer_cancel.title': {
            'en': 'Offer cancelled',
        },
        'notifications.driver.passenger_offer_cancel.body': {
            'en': 'Sorry, the passenger cancelled the ride',
        },
    },
)
async def test_passenger_offer_cancel(
        stq3_context, validate_stq3_sent_notifications,
):
    await send_notifications.task(
        stq3_context,
        intent='passenger_offer_cancel',
        driver_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
    )
    validate_stq3_sent_notifications(
        expected_notifications=[
            {
                'id': '00000000000000000000000000000000',
                'firebase_token': 'firebase_token0',
                'title': 'Offer cancelled',
                'body': 'Sorry, the passenger cancelled the ride',
            },
        ],
    )


@pytest.mark.mongodb_collections('rida_drivers')
@pytest.mark.filldb()
@pytest.mark.translations(
    rida={
        'notifications.driver.offer_expired.title': {'en': 'Offer expired'},
        'notifications.driver.offer_expired.body': {
            'en': 'Oops, your offer expired.',
        },
    },
)
async def test_driver_offer_expired(
        stq3_context, validate_stq3_sent_notifications,
):
    await send_notifications.task(
        stq3_context,
        intent='offer_expired',
        driver_guids=['9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'],
    )
    validate_stq3_sent_notifications(
        expected_notifications=[
            {
                'id': '00000000000000000000000000000000',
                'firebase_token': 'firebase_token0',
                'title': 'Offer expired',
                'body': 'Oops, your offer expired.',
            },
        ],
    )


@pytest.mark.mongodb_collections('rida_drivers')
@pytest.mark.filldb()
@pytest.mark.translations(
    rida={
        'notifications.driver.passenger_offer_cancel.title': {
            'en': 'Offer cancelled',
        },
        'notifications.driver.passenger_offer_cancel.body': {
            'en': 'Sorry, the passenger cancelled the ride',
        },
    },
)
async def test_passenger_offer_cancel_bulk(
        stq3_context, validate_stq3_sent_notifications,
):
    await send_notifications.task(
        stq3_context,
        intent='passenger_offer_cancel_bulk',
        driver_guids=['9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'],
    )
    validate_stq3_sent_notifications(
        expected_notifications=[
            {
                'id': '00000000000000000000000000000000',
                'firebase_token': 'firebase_token0',
                'title': 'Offer cancelled',
                'body': 'Sorry, the passenger cancelled the ride',
            },
        ],
    )
