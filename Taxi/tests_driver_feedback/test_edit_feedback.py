import datetime
import urllib.parse

import pytest

from tests_driver_feedback import utils

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
GET_FEEDBACK_QUERY = """SELECT
            park_id,
            driver_id,
            order_id,
            id,
            date,
            score,
            feed_type,
            status,
            description,
            predefined_comments
            FROM feedbacks_0"""


def data_builder(order_id, score, comment, choices=None, feed_type=None):
    data = {'order': order_id, 'rating': score, 'msg': comment}
    if feed_type:
        data['feed_type'] = feed_type
    if choices:
        data['choices'] = choices

    return urllib.parse.urlencode(data, doseq=True)


def feedback_builder(
        order_id, score, choices=None, comment=None, feed_type='passenger',
):
    feed_type_code = utils.get_feed_type_code(feed_type)
    if choices is not None:
        choices = ';'.join(choices)
    return (
        PARK_ID,
        DRIVER_ID,
        order_id,
        utils.get_feedback_id(order_id, DRIVER_ID, feed_type_code),
        datetime.datetime(2020, 4, 1, 9, 34, 56),  # date
        int(score),
        feed_type_code,
        0,  # status
        comment,  # description
        choices,
    )


@pytest.mark.now('2020-04-01T12:34:56+03:00')
@pytest.mark.parametrize(
    'order_id, data',
    [
        pytest.param('OrderId', {'score': 1}, id='case 1'),
        pytest.param(
            'OrderId',
            {
                'score': 2,
                'choices': ['reason_1', 'reason_2'],
                'feed_type': 'passenger',
            },
            id='case 2',
        ),
        pytest.param(
            'OrderId',
            {
                'score': 3,
                'choices': ['reason_1'],
                'comment': 'Passenger smoke',
                'feed_type': 'sender',
            },
            id='case 3',
        ),
        pytest.param(
            'OrderId',
            {
                'score': 4,
                'choices': [],
                'comment': 'Passenger smile',
                'feed_type': 'recipient',
            },
            id='case 4',
        ),
        pytest.param(
            'OrderId',
            {'score': 5, 'choices': ['reason_1', 'reason_2', 'reason_3']},
            id='case 5',
        ),
    ],
)
async def test_driver_feeds_patch(
        taxi_driver_feedback, order_id, data, stq, pgsql,
):
    response = await taxi_driver_feedback.patch(
        ENDPOINT,
        params={**PARAMS, 'order': order_id},
        headers=HEADERS,
        json=data,
    )
    assert response.status_code == 200
    assert stq.driver_feedback_repeat.times_called == 0

    if response.status_code == 200:
        cursor = pgsql['taximeter_feedbacks@0'].cursor()
        cursor.execute(GET_FEEDBACK_QUERY)
        rows = cursor.fetchall()

        assert len(rows) == 1
        assert rows[0] == feedback_builder(order_id, **data)


@pytest.mark.now('2020-04-01T12:34:56+03:00')
async def test_driver_feeds_add_and_patch(taxi_driver_feedback, stq, pgsql):
    order_id = 'OrderId'
    data = {
        'score': 4,
        'choices': ['reason_1', 'reason_2'],
        'comment': 'Passenger smile',
        'feed_type': 'recipient',
    }
    response = await taxi_driver_feedback.patch(
        ENDPOINT,
        params={**PARAMS, 'order': order_id},
        headers=HEADERS,
        json=data,
    )
    assert response.status_code == 200

    cursor = pgsql['taximeter_feedbacks@0'].cursor()
    cursor.execute(GET_FEEDBACK_QUERY)
    rows = cursor.fetchall()

    assert len(rows) == 1
    assert rows[0] == feedback_builder(order_id, **data)

    response = await taxi_driver_feedback.patch(
        ENDPOINT,
        params={**PARAMS, 'order': order_id},
        headers=HEADERS,
        json={'score': 2, 'feed_type': 'recipient'},
    )
    assert response.status_code == 200

    cursor.execute(GET_FEEDBACK_QUERY)
    rows = cursor.fetchall()

    assert len(rows) == 1
    assert rows[0] == feedback_builder(order_id, **{**data, 'score': 2})

    response = await taxi_driver_feedback.patch(
        ENDPOINT,
        params={**PARAMS, 'order': order_id},
        headers=HEADERS,
        json={'score': 2, 'choices': ['reason_1'], 'feed_type': 'recipient'},
    )
    assert response.status_code == 200

    cursor.execute(GET_FEEDBACK_QUERY)
    rows = cursor.fetchall()

    assert len(rows) == 1
    assert rows[0] == feedback_builder(
        order_id, **{**data, 'score': 2, 'choices': ['reason_1']},
    )

    assert stq.driver_feedback_repeat.times_called == 0
