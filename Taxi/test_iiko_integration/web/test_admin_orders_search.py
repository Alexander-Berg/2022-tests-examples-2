import pytest

from test_iiko_integration import stubs

RESTAURANT_INFO = {
    'country_code': 'RU',
    'eda_client_id': 1,
    'geopoint': {'lat': 55.751244, 'lon': 37.618423},
    'name': 'Ресторан Максимум',
    'address': 'address_ru',
    'region_id': 1,
}

EXPECTED_ORDERS = [
    {
        'amount': '100.00',
        'created_at': '2020-06-04T09:15:00+03:00',
        'currency': 'RUB',
        'discount': '0.00',
        'order_id': '02',
        'restaurant_info': RESTAURANT_INFO,
        'user_id': 'user',
        'restaurant_order_id': 'iiko_02',
        'status': {
            'restaurant_status': 'CANCELED',
            'invoice_status': 'HOLD_FAILED',
            'updated_at': '2020-06-04T06:00:00+00:00',
        },
    },
    {
        'amount': '100.00',
        'created_at': '2020-06-02T09:00:00+03:00',
        'currency': 'RUB',
        'discount': '0.00',
        'order_id': '01',
        'restaurant_info': RESTAURANT_INFO,
        'user_id': 'user',
        'restaurant_order_id': 'iiko_01',
        'status': {
            'restaurant_status': 'PAYMENT_CONFIRMED',
            'invoice_status': 'CLEARED',
            'updated_at': '2020-06-02T06:00:00+00:00',
        },
    },
]


@pytest.mark.config(
    IIKO_INTEGRATION_ORDER_STATUS_POLLING_DELAY=3,
    **stubs.RESTAURANT_INFO_CONFIGS,
)
@pytest.mark.translations(
    qr_payment={'maximum.kek': {'ru': 'Ресторан Максимум'}},
)
@pytest.mark.parametrize(
    [
        'phone',
        'card_number',
        'expected_code',
        'expected_response',
        'limit',
        'offset',
    ],
    [
        pytest.param(
            'no_personal_phone_id',
            None,
            404,
            {'code': 'user_not_found', 'message': 'Empty personal_phone_id'},
            100,
            0,
            id='bad_phone_1',
        ),
        pytest.param(
            'no_phone_ids',
            None,
            404,
            {'code': 'user_not_found', 'message': 'Empty user_phones'},
            100,
            0,
            id='bad_phone_2',
        ),
        pytest.param(
            'no_user_ids',
            None,
            404,
            {'code': 'user_not_found', 'message': 'Empty user_ids'},
            100,
            0,
            id='bad_phone_3',
        ),
        pytest.param(
            'empty_orders',
            None,
            200,
            {'orders': []},
            100,
            0,
            id='empty_orders',
        ),
        pytest.param(
            'orders',
            None,
            200,
            {'orders': EXPECTED_ORDERS},
            None,
            None,
            id='orders',
        ),
        pytest.param(
            'orders',
            None,
            200,
            {'orders': EXPECTED_ORDERS},
            100,
            0,
            id='orders',
        ),
        pytest.param(
            'orders',
            None,
            200,
            {'orders': EXPECTED_ORDERS[1:]},
            1,
            1,
            id='orders',
        ),
        pytest.param(
            'orders',
            None,
            200,
            {'orders': []},
            100,
            100,
            id='orders_with_offset',
        ),
        pytest.param(
            None, None, 200, {'orders': []}, 100, 0, id='empty_params',
        ),
        pytest.param(
            None,
            'card-02',
            200,
            {'orders': [EXPECTED_ORDERS[0]]},
            100,
            0,
            id='only_card',
        ),
        pytest.param(
            'orders',
            'card-01',
            200,
            {'orders': [EXPECTED_ORDERS[1]]},
            100,
            0,
            id='phone_and_card_ok',
        ),
        pytest.param(
            None,
            'invalid_card_number',
            404,
            {
                'code': 'card_not_found',
                'message': 'No cards with number invalid_card_number',
            },
            100,
            0,
            id='invalid_card_number',
        ),
        pytest.param(
            'orders',
            'card-03',
            200,
            {'orders': []},
            100,
            0,
            id='phone_and_card_empty',
        ),
    ],
)
@pytest.mark.config(
    TVM_RULES=[
        {'src': 'iiko-integration', 'dst': 'personal'},
        {'src': 'iiko-integration', 'dst': 'user-api'},
    ],
)
async def test_orders_search(
        web_app_client,
        mockserver,
        load_json,
        phone,
        card_number,
        expected_code,
        expected_response,
        limit,
        offset,
):
    @mockserver.json_handler('/cardstorage/v1/cards')
    def _cardstorage_mock(req):
        assert req.json == {'number': card_number, 'service_type': 'card'}
        if card_number == 'invalid_card_number':
            return {'cards': []}

        response = load_json('cardstorage_response.json')
        response['cards'][0]['card_id'] = card_number
        return response

    @mockserver.json_handler('/personal/v1/phones/store')
    def _personal_mock(req):
        response = {'value': req.json['value']}
        if req.json['value'] == 'no_personal_phone_id':
            response['id'] = ''
        else:
            response['id'] = req.json['value']
        return response

    @mockserver.json_handler(
        '/user_api-api/user_phones/by_personal/retrieve_bulk',
    )
    def _user_api_retrieve_phones_mock(req):
        phone_id = req.json['items'][0]['personal_phone_id']
        # we always have one element in current tests

        response = None
        if phone_id == 'no_phone_ids':
            response = []
        else:
            response = [{'id': phone_id}]
        return {'items': response}

    @mockserver.json_handler('/user_api-api/users/search')
    def _user_api_users_search_mock(req):
        phone_id = req.json['phone_ids'][0]
        # we always have one element in current tests

        response = None
        if phone_id == 'no_user_ids':
            response = []
        elif phone_id == 'empty_orders':
            response = [{'id': 'bad_user_id1'}]
        else:
            response = [{'id': 'user'}, {'id': 'bad_user_id2'}]
        return {'items': response}

    if limit and offset:
        params = {'limit': limit, 'offset': offset}
    else:
        params = None
    response = await web_app_client.post(
        '/admin/qr-pay/v1/orders-search',
        params=params,
        json={'phone': phone, 'card_number': card_number},
    )
    assert response.status == expected_code
    content = await response.json()
    assert content == expected_response
