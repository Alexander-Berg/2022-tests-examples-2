import pytest

from test_rida import helpers


@pytest.mark.parametrize(
    ['initial_price'],
    [
        pytest.param(1200, id='float_success'),
        pytest.param('1200', id='str_success'),
    ],
)
@pytest.mark.parametrize(
    ['request_body_as_query'],
    [
        pytest.param(True, id='request_body_as_query'),
        pytest.param(False, id='request_body_as_json'),
    ],
)
@pytest.mark.now('2020-04-29T10:12:00.000+0000')
async def test_happy_path(
        web_app_client,
        stq,
        mongodb,
        load_json,
        request_body_as_query,
        initial_price,
):
    offer_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'
    offer = mongodb.rida_offers.find_one({'offer_guid': offer_guid})
    assert offer['initial_price'] == 900
    assert offer['price_sequence'] == 1
    assert offer['status_changes'] == []

    request_params = {}

    request_body = {'offer_guid': offer_guid, 'initial_price': initial_price}
    headers = helpers.get_auth_headers(user_id=1234)

    request_body = {k: v for k, v in request_body.items() if v is not None}
    if request_body_as_query:
        request_params['data'] = request_body
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    else:
        request_params['json'] = request_body
        headers['Content-Type'] = 'application/json'

    request_params['headers'] = headers

    response = await web_app_client.post(
        '/v1/offer/priceChange', **request_params,
    )

    assert response.status == 200
    response_json = await response.json()
    response_data = response_json['data']
    assert response_data['offer'] == load_json('happy_path.json')

    offer = mongodb.rida_offers.find_one({'offer_guid': offer_guid})
    assert offer['initial_price'] == float(initial_price)
    assert offer['price_sequence'] == 2
    assert offer['status_changes'] == [
        {
            'created_at': '2020-04-29 10:12:00',
            'initial_price': 1200.0,
            'offer_status': 'PRICE_CHANGED',
            'price_sequence': 2,
        },
    ]

    queue = stq.rida_send_notifications
    task = queue.next_call()
    assert task['kwargs'] == {
        'intent': 'price_changed',
        'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D',
        'user_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        'start_point': [40.2108517, 44.5281845],
        'point_a': '2 Nikoghayos Adonts St, Yerevan 0014, Armenia',
        'point_b': 'Ohanov St, Yerevan, Armenia',
        'initial_price': 1200.0,
        'currency': 'NGN',
    }


@pytest.mark.parametrize(
    ['offer_guid', 'user_id', 'expected_status'],
    [
        pytest.param('not_found', 1234, 404, id='offer_not_found'),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
            1449,
            404,
            id='foreign_offer',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5E',
            1234,
            409,
            id='incorrect_offer_status',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
            1234,
            409,
            id='exist_active_bids',
        ),
    ],
)
@pytest.mark.now('2020-04-29T10:12:00.000+0000')
async def test_error_handling(
        web_app_client, offer_guid, user_id, expected_status,
):
    response = await web_app_client.post(
        '/v1/offer/priceChange',
        headers=helpers.get_auth_headers(user_id),
        json={'offer_guid': offer_guid, 'initial_price': 2},
    )
    assert response.status == expected_status


@pytest.mark.now('2020-04-29T10:12:00.000+0000')
async def test_same_price(
        web_app_client, mongodb, validate_stq3_sent_notifications,
):
    offer_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'
    offer = mongodb.rida_offers.find_one({'offer_guid': offer_guid})
    assert offer['price_sequence'] == 1

    response = await web_app_client.post(
        '/v1/offer/priceChange',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': offer_guid, 'initial_price': 1200},
    )
    assert response.status == 200
    offer = mongodb.rida_offers.find_one({'offer_guid': offer_guid})
    assert offer['price_sequence'] == 2

    response = await web_app_client.post(
        '/v1/offer/priceChange',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': offer_guid, 'initial_price': 1200},
    )
    assert response.status == 200
    offer = mongodb.rida_offers.find_one({'offer_guid': offer_guid})
    assert offer['price_sequence'] == 2


@pytest.mark.now('2020-04-29T10:13:00.000+0000')
@pytest.mark.parametrize(
    ['duration', 'call_count'],
    [
        pytest.param(3, 0, id='last_price_change_time'),
        pytest.param(31, 1, id='after_timeout'),
    ],
)
async def test_price_change_without_notification(
        taxi_rida_web, stq, mocked_time, duration, call_count,
):
    mocked_time.sleep(duration)
    await taxi_rida_web.invalidate_caches()

    response = await taxi_rida_web.post(
        '/v1/offer/priceChange',
        headers=helpers.get_auth_headers(1234),
        json={
            'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5X',
            'initial_price': 1400,
        },
    )
    assert response.status == 200
    queue = stq.rida_send_notifications
    assert queue.times_called == call_count
