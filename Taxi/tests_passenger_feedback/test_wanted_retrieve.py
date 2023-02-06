import pytest

ORDER_1 = {
    'order_id': 'order_with_later_due',
    'completed': '2018-08-10T17:01:30+0000',
    'park_id': 'park_id',
    'due': '2018-08-10T17:01:00+0000',
    'created': '2018-08-10T17:00:30+0000',
}
ORDER_2 = {
    'order_id': 'order_id',
    'completed': '2018-08-10T17:00:30+0000',
    'park_id': 'park_id',
    'due': '2018-08-10T17:00:30+0000',
    'created': '2018-08-10T17:00:30+0000',
}
ASK_FEEDBACK_TIMEOUT = 86400
ASK_FEEDBACK_COLLAPSE_TIMEOUT = 10800


def get_ask_feedback(
        hide_interval=ASK_FEEDBACK_TIMEOUT,
        collapse_interval=ASK_FEEDBACK_COLLAPSE_TIMEOUT,
):
    return {
        'orderid': 'order_with_later_due',
        'parkid': 'park_id',
        'due': '2018-08-10T17:01:00+0000',
        'appearance_date': '2018-08-10T17:01:30+0000',
        'hide_interval': hide_interval,
        'collapse_interval': collapse_interval,
    }


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.parametrize(
    'expected_response',
    (
        pytest.param(
            {'ask_feedback': get_ask_feedback(), 'orders': [ORDER_1, ORDER_2]},
            id='two_orders',
        ),
        pytest.param(
            {
                'ask_feedback': get_ask_feedback(
                    hide_interval=3630, collapse_interval=300,
                ),
                'orders': [ORDER_1],
            },
            marks=[
                pytest.mark.config(
                    ASK_FEEDBACK_TIMEOUT=3630,
                    ASK_FEEDBACK_COLLAPSE_TIMEOUT=300,
                ),
            ],
            id='one_order',
        ),
        pytest.param(
            {'orders': []},
            marks=[pytest.mark.config(ASK_FEEDBACK_TIMEOUT=60)],
            id='no_orders',
        ),
    ),
)
async def test_wanted_retrieve(taxi_passenger_feedback, expected_response):
    request = {'id': 'user_id', 'phone_id': '123456789012345678901234'}
    response = await taxi_passenger_feedback.post(
        '/passenger-feedback/v1/wanted/retrieve', request,
    )
    assert response.status_code == 200
    assert response.json() == expected_response
