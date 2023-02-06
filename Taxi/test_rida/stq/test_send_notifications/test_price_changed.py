import pytest

from rida.stq import send_notifications


@pytest.mark.now('2020-02-26T13:50:00.000')
@pytest.mark.mongodb_collections('rida_drivers')
@pytest.mark.filldb()
@pytest.mark.translations(
    rida={
        'notifications.driver.price_change.title': {'en': 'Price changed'},
        'notifications.driver.price_change.body': {
            'en': (
                'New ride suggestion for {price} '
                '{currency} {point_a} - {point_b}'
            ),
        },
    },
)
async def test_price_changed(stq3_context, validate_stq3_sent_notifications):
    await send_notifications.task(
        stq3_context,
        intent='price_changed',
        offer_guid='some_offer_guid',
        user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        start_point=[23.45, 45.23],
        point_a='point_a',
        point_b='point_b',
        initial_price=500.4,
        currency='NGN',
    )
    validate_stq3_sent_notifications(
        expected_notifications=[
            {
                'id': '00000000000000000000000000000000',
                'firebase_token': 'firebase_token1',
                'title': 'Price changed',
                'body': 'New ride suggestion for 500 NGN point_a - point_b',
                'data': {'offer_guid': 'some_offer_guid', 'push_type': 1},
            },
        ],
    )
