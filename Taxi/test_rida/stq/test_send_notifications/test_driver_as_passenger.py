import pytest

from rida import consts
from rida.stq import send_notifications


@pytest.mark.now('2020-02-26T13:50:00.000')
@pytest.mark.mongodb_collections('rida_drivers')
@pytest.mark.filldb()
async def test_driver_riding_as_passenger(
        stq3_context, validate_stq3_sent_notifications,
):
    """
    If a driver is currently riding as a passenger,
    no new_offer notifications should be created
    """

    await send_notifications.task(
        stq3_context,
        intent='new_offer',
        offer_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5J',
        start_point=[23.45, 45.23],
        point_a='point_a',
        point_b='point_b',
        initial_price=500.4,
    )
    validate_stq3_sent_notifications(
        expected_notifications=[], expected_times_called=0,
    )


@pytest.mark.translations(
    rida={
        'notifications.driver.new_offer.title': {'en': 'new_offer'},
        'notifications.driver.new_offer.body': {'en': 'new_offer_body'},
    },
)
@pytest.mark.now('2020-02-26T13:50:00.000')
@pytest.mark.mongodb_collections('rida_drivers')
@pytest.mark.filldb()
async def test_driver_riding_as_passenger_offer_completed(
        stq3_context, mongodb, validate_stq3_sent_notifications,
):
    """
    If a driver was riding as a passenger, but the ride has finished,
    new_offer notifications should be created normally.
    """
    mongodb.rida_offers.update_one(
        {'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'},
        {'$set': {'offer_status': consts.OfferStatus.COMPLETE.value}},
    )

    await send_notifications.task(
        stq3_context,
        intent='new_offer',
        offer_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5J',
        start_point=[23.45, 45.23],
        point_a='point_a',
        point_b='point_b',
        initial_price=500.4,
    )
    validate_stq3_sent_notifications(
        expected_notifications=[
            {
                'id': '00000000000000000000000000000000',
                'firebase_token': 'firebase_token0',
                'title': 'new_offer',
                'body': 'new_offer_body',
                'data': {
                    'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
                    'push_type': 1,
                },
                'sound': {'apns': 'new_order.caf'},
                'notification_channel': {'android': 'tada_new_order_chanel'},
            },
        ],
    )
