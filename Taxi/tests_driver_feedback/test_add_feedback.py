import urllib.parse

import pytest

ENDPOINT = '/driver/v1/driver-feedback/v1/feedback'
PARK_ID = 'ParkId'
DRIVER_ID = 'DriverId'

PARAMS = {'park_id': PARK_ID}
HEADERS = {
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.07 (1234)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'User-Agent': 'Taximeter 9.07 (1234)',
}


def data_builder(order_id, rating, comment=None, feed_type=None, choices=None):
    data = {'order': order_id, 'rating': rating}
    if comment:
        data['msg'] = comment
    if feed_type:
        data['feed_type'] = feed_type
    if choices:
        data['choices'] = choices
    return urllib.parse.urlencode(data)


# check order correspondence via mock driver_orders like in test_repeater
@pytest.mark.now('2020-04-01T12:34:56+03:00')
@pytest.mark.parametrize(
    'data, expected_kwargs',
    [
        pytest.param(
            ('OrderId', '4', 'Passenger smoked'),
            {
                'park_id': 'ParkId',
                'driver_id': 'DriverId',
                'order_id': 'OrderId',
                'feedback_id': '15f269e400ed11552632d00ade9a7dac',
                'date': {'$date': '2020-04-01T09:34:56.000Z'},
                'score': 4,
                'status': 0,
                'feed_type': 1,
                'description': 'Passenger smoked',
            },
            id='without type',
        ),
        pytest.param(
            ('OrderId', '5', 'Passenger was cool', ''),
            {
                'park_id': 'ParkId',
                'driver_id': 'DriverId',
                'order_id': 'OrderId',
                'feedback_id': '15f269e400ed11552632d00ade9a7dac',
                'date': {'$date': '2020-04-01T09:34:56.000Z'},
                'score': 5,
                'status': 0,
                'feed_type': 1,
                'description': 'Passenger was cool',
            },
            id='no type -> passenger',
        ),
        pytest.param(
            ('OrderId', '4', 'Passenger smiled', 'passenger'),
            {
                'park_id': 'ParkId',
                'driver_id': 'DriverId',
                'order_id': 'OrderId',
                'feedback_id': '15f269e400ed11552632d00ade9a7dac',
                'date': {'$date': '2020-04-01T09:34:56.000Z'},
                'score': 4,
                'status': 0,
                'feed_type': 1,
                'description': 'Passenger smiled',
            },
            id='passenger type',
        ),
        pytest.param(
            ('OrderId', '3', 'Passenger died', 'sender'),
            {
                'park_id': 'ParkId',
                'driver_id': 'DriverId',
                'order_id': 'OrderId',
                'feedback_id': 'f37253b863563f3cb798a8cdeb963fc5',
                'date': {'$date': '2020-04-01T09:34:56.000Z'},
                'score': 3,
                'status': 0,
                'feed_type': 2,
                'description': 'Passenger died',
            },
            id='sender type',
        ),
        pytest.param(
            ('OrderId', '5', 'It is alive!', 'recipient'),
            {
                'park_id': 'ParkId',
                'driver_id': 'DriverId',
                'order_id': 'OrderId',
                'feedback_id': 'e454af8f45f514dfaba17d8e4b210638',
                'date': {'$date': '2020-04-01T09:34:56.000Z'},
                'score': 5,
                'status': 0,
                'feed_type': 3,
                'description': 'It is alive!',
            },
            id='recipient type',
        ),
        pytest.param(
            ('OrderId', '4', 'Wait too long', 'eater'),
            {
                'park_id': 'ParkId',
                'driver_id': 'DriverId',
                'order_id': 'OrderId',
                'feedback_id': '4615defc46d5f398244564e288bcdccb',
                'date': {'$date': '2020-04-01T09:34:56.000Z'},
                'score': 4,
                'status': 0,
                'feed_type': 4,
                'description': 'Wait too long',
            },
            id='eater type',
        ),
        pytest.param(
            ('OrderId', '5', 'Tasty', 'restaurant'),
            {
                'park_id': 'ParkId',
                'driver_id': 'DriverId',
                'order_id': 'OrderId',
                'feedback_id': 'd20786334f44b3686faf15db5d9041ac',
                'date': {'$date': '2020-04-01T09:34:56.000Z'},
                'score': 5,
                'status': 0,
                'feed_type': 5,
                'description': 'Tasty',
            },
            id='restaurant type',
        ),
        pytest.param(
            ('OrderId', '5', 'Wonderful', 'grocery'),
            {
                'park_id': 'ParkId',
                'driver_id': 'DriverId',
                'order_id': 'OrderId',
                'feedback_id': '27481ac446f9f2e66fcfda189cb1fc49',
                'date': {'$date': '2020-04-01T09:34:56.000Z'},
                'score': 5,
                'status': 0,
                'feed_type': 6,
                'description': 'Wonderful',
            },
            id='grocery type',
        ),
        pytest.param(
            ('OrderId', '2', 'What should I rate?', 'misc'),
            {
                'park_id': 'ParkId',
                'driver_id': 'DriverId',
                'order_id': 'OrderId',
                'feedback_id': '7126b996e2405351e57486fbce015556',
                'date': {'$date': '2020-04-01T09:34:56.000Z'},
                'score': 2,
                'status': 0,
                'feed_type': 7,
                'description': 'What should I rate?',
            },
            id='misc type',
        ),
        pytest.param(
            ('OrderId', '1', None, 'recipient', 'reason_1;reason_2'),
            {
                'park_id': 'ParkId',
                'driver_id': 'DriverId',
                'order_id': 'OrderId',
                'feedback_id': 'e454af8f45f514dfaba17d8e4b210638',
                'date': {'$date': '2020-04-01T09:34:56.000Z'},
                'score': 1,
                'status': 0,
                'feed_type': 3,
                'choices': 'reason_1;reason_2',
            },
            id='with choices',
        ),
        pytest.param(
            ('OrderId', '3', None, 'passenger', 'reason_2'),
            {
                'park_id': 'ParkId',
                'driver_id': 'DriverId',
                'order_id': 'OrderId',
                'feedback_id': '15f269e400ed11552632d00ade9a7dac',
                'date': {'$date': '2020-04-01T09:34:56.000Z'},
                'score': 3,
                'status': 0,
                'feed_type': 1,
                'choices': 'reason_2',
            },
            id='with choice',
        ),
    ],
)
async def test_driver_feeds_add_via_stq(
        taxi_driver_feedback, driver_orders, stq, data, expected_kwargs,
):
    driver_orders.set_order_params('order_id_1', {'ended_at': None})
    response = await taxi_driver_feedback.post(
        ENDPOINT, params=PARAMS, headers=HEADERS, data=data_builder(*data),
    )
    assert response.status_code == 200
    assert stq.driver_feedback_repeat.times_called == 1

    kwargs = stq.driver_feedback_repeat.next_call()['kwargs']
    del kwargs['log_extra']
    assert kwargs == expected_kwargs
