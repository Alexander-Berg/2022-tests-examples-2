import pytest

from rida.stq import send_notifications


def _check_bid_status_log(mongodb, bid_guid: str, expected_log_id: str):
    bid = mongodb.rida_bids.find_one({'bid_guid': bid_guid})
    bid_status_log = bid.get('bid_status_log')
    assert bid_status_log is not None
    assert len(bid_status_log) > 0  # pylint: disable=len-as-condition
    last_log = bid_status_log[-1]
    assert last_log['log_id'] == expected_log_id


@pytest.mark.mongodb_collections('rida_drivers')
@pytest.mark.filldb()
@pytest.mark.translations(
    rida={
        'notifications.driver.bid_auction.price_matched.title': {
            'en': 'Your bid is matched',
        },
        'notifications.driver.bid_auction.price_matched.body': {
            'en': 'Consider making a better bid to secure order',
        },
    },
)
async def test_bid_auction_price_matched(
        stq3_context, mongodb, validate_stq3_sent_notifications,
):
    await send_notifications.task(
        stq3_context,
        intent='bid_auction_price_matched',
        offer_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5F',
        driver_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
        price_sequence=1,
        proposed_price=250.0,
    )
    await send_notifications.task(
        stq3_context,
        intent='bid_auction_price_matched',
        offer_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5F',
        driver_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
        price_sequence=1,
        proposed_price=250.0,
    )
    _check_bid_status_log(mongodb, 'other_bid_250_1', 'bid_auction.matched')
    validate_stq3_sent_notifications(
        expected_times_called=1,
        expected_notifications=[
            {
                'id': '00000000000000000000000000000000',
                'firebase_token': 'firebase_token0',
                'title': 'Your bid is matched',
                'body': 'Consider making a better bid to secure order',
            },
        ],
    )


@pytest.mark.mongodb_collections('rida_drivers')
@pytest.mark.filldb()
@pytest.mark.translations(
    rida={
        'notifications.driver.bid_auction.price_outbidden.title': {
            'en': 'Your bid is bested',
        },
        'notifications.driver.bid_auction.price_outbidden.body': {
            'en': 'Consider making a better bid to secure order',
        },
    },
)
async def test_bid_auction_price_outbidden(
        stq3_context, mongodb, validate_stq3_sent_notifications,
):
    await send_notifications.task(
        stq3_context,
        intent='bid_auction_price_outbidden',
        offer_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5F',
        driver_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
        price_sequence=1,
        proposed_price=250.0,
    )
    await send_notifications.task(
        stq3_context,
        intent='bid_auction_price_outbidden',
        offer_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5F',
        driver_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
        price_sequence=1,
        proposed_price=250.0,
    )
    _check_bid_status_log(mongodb, 'other_bid_300_1', 'bid_auction.outbidden')
    _check_bid_status_log(mongodb, 'other_bid_400', 'bid_auction.outbidden')
    validate_stq3_sent_notifications(
        expected_times_called=1,
        expected_notifications=[
            {
                'id': '00000000000000000000000000000000',
                'firebase_token': 'firebase_token0',
                'title': 'Your bid is bested',
                'body': 'Consider making a better bid to secure order',
            },
            {
                'id': '00000000000000000000000000000001',
                'firebase_token': 'firebase_token1',
                'title': 'Your bid is bested',
                'body': 'Consider making a better bid to secure order',
            },
        ],
    )
