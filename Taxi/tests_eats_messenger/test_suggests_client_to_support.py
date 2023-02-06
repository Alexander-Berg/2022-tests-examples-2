import pytest


class Anything:
    def __eq__(self, other):
        return True


ORDER_NR = '111111-100000'

EATS_EATERS_FIND_BY_PASSPORT_UID = {
    'eater': {
        'personal_phone_id': 'phone_id',
        'id': '123456',
        'uuid': 'eater-uuid-1',
        'created_at': '2021-06-01T00:00:00+00:00',
        'updated_at': '2021-06-01T00:00:00+00:00',
    },
}

EATS_ORDERSHISTORY_V2_GET_ORDERS_RESPONSE = {
    'orders': [
        {
            'order_id': ORDER_NR,
            'place_id': 1337,
            'status': 'taken',
            'source': 'eda',
            'delivery_location': {'lat': 0, 'lon': 0},
            'total_amount': '123',
            'is_asap': False,
            'created_at': '2020-04-28T09:00:00+0000',
        },
    ],
}

EATS_CATALOG_STORAGE_PLACES_RETRIEVE_BY_IDS = {
    'places': [
        {
            'id': 1337,
            'revision_id': 1,
            'updated_at': '2020-04-28T12:00:00+03:00',
            'name': 'kfc',
            'business': 'restaurant',
            'region': {
                'geobase_ids': [213, 216],
                'id': 1,
                'name': 'region_name',
                'time_zone': 'Europe/Moscow',
            },
        },
    ],
    'not_found_place_ids': [],
}

EATS_SUPPORT_MISC_ORDER_SUPPORT_META = {
    'metadata': {
        'eater_id': 'some_id',
        'eater_decency': 'good',
        'eater_passport_uid': '1234',
        'is_first_order': True,
        'is_blocked_user': False,
        'order_status': 'order_taken',
        'order_type': 'native',
        'delivery_type': 'native',
        'is_fast_food': False,
        'app_type': 'eats',
        'country_code': 'RU',
        'country_label': 'Russia',
        'city_label': 'Moscow',
        'order_created_at': '2020-04-28T01:00:00+03:00',
        'order_promised_at': '2020-04-28T13:00:00+03:00',
        'is_surge': False,
        'is_promocode_used': False,
        'persons_count': 1,
        'payment_method': 'card',
        'order_total_amount': 150.15,
        'place_id': '10',
        'place_name': 'some_place_name',
        'is_sent_to_restapp': False,
        'is_sent_to_integration': True,
        'integration_type': 'native',
        'place_eta': '2020-04-28T12:20:00.100000+03:00',
        'eater_eta': '2020-04-28T12:30:00.100000+03:00',
        'courier_type': 'car',
        'readable_order_created_at': '01.01.2021 02:00',
        'readable_order_promised_at': '01.01.2021 02:00',
        'readable_place_eta': '13:20',
        'readable_eater_eta': '13:30',
        'has_receipts': True,
        'receipt_urls': ['ofd_receipt_url', 'another_ofd_url'],
        'courier_arrived_to_customer_planned_time': (
            '2020-04-28T00:16:30+03:00'
        ),
        'readable_courier_arrived_to_customer_planned_time': '01:16',
        'courier_arrived_to_customer_from': 10,
        'courier_arrived_to_customer_to': 15,
        'local_time': '01:10',
        'local_date': '28.04.2020',
    },
}

GROCERY_EATS_GATEWAY_LATEST_ORDERS = [
    {
        'created_at': '2020-04-28T12:20:00.100000+03:00',
        'delivery_address': {
            'city': '',
            'house': '10',
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'short': 'some street, 10',
            'street': 'some street',
        },
        'final_cost_for_customer': '0',
        'order_nr': '111111-111111',
        'short_order_id': 'short_order_2',
        'status_for_customer': 3,
    },
    {
        'created_at': '2010-04-28T12:21:00.100000+03:00',
        'delivery_address': {
            'city': '',
            'house': '10',
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'short': 'some street, 10',
            'street': 'some street',
        },
        'final_cost_for_customer': '0',
        'order_nr': '222222-222222',
        'short_order_id': 'short_order_3',
        'status_for_customer': 4,
    },
]


@pytest.mark.config(
    EATS_MESSENGER_TIMEOUTS_FOR_CANCELLED_ORDERS_SHOW={
        '__default__': {'cancelled_period': {'__default__': 86400}},
    },
)
@pytest.mark.now('2020-04-28T12:21:00.100000+03:00')
@pytest.mark.parametrize(
    [
        'callback_data',
        'eats_eaters_response',
        'eats_ordershistory_response',
        'eats_catalog_storage_response',
        'eats_support_misc_response',
        'grocery_eats_gateway_response',
        'expected_response_code',
        'expected_response_json',
    ],
    [
        pytest.param(
            {},
            EATS_EATERS_FIND_BY_PASSPORT_UID,
            {
                'orders': [
                    {
                        'order_id': '111111-100000',
                        'place_id': 1337,
                        'status': 'taken',
                        'source': 'eda',
                        'delivery_location': {'lat': 0, 'lon': 0},
                        'total_amount': '123',
                        'is_asap': False,
                        'created_at': '2020-04-28T02:00:00+0000',
                    },
                    {
                        'order_id': '111111-200000',
                        'place_id': 1337,
                        'status': 'finished',
                        'source': 'eda',
                        'delivery_location': {'lat': 0, 'lon': 0},
                        'total_amount': '123',
                        'is_asap': False,
                        'created_at': '2020-04-28T01:00:00+0000',
                        'delivered_at': '2020-04-28T02:00:00+0000',
                    },
                    {
                        'order_id': '111111-300000',
                        'place_id': 1337,
                        'status': 'taken',
                        'source': 'eda',
                        'delivery_location': {'lat': 0, 'lon': 0},
                        'total_amount': '123',
                        'is_asap': False,
                        'created_at': '2020-04-28T03:00:00+0000',
                    },
                    {
                        'order_id': '111111-400000',
                        'place_id': 1337,
                        'status': 'cancelled',
                        'source': 'eda',
                        'delivery_location': {'lat': 0, 'lon': 0},
                        'total_amount': '123',
                        'is_asap': False,
                        'created_at': '2020-04-28T01:59:59+0000',
                        'cancelled_at': '2020-04-28T02:00:00+0000',
                    },
                    {
                        'order_id': '111111-600000',
                        'place_id': 1337,
                        'status': 'cancelled',
                        'source': 'eda',
                        'delivery_location': {'lat': 0, 'lon': 0},
                        'total_amount': '123',
                        'is_asap': False,
                        'created_at': '2020-04-27T01:59:59+0000',
                        'cancelled_at': '2020-04-27T09:21:00+0000',
                    },
                ],
            },
            EATS_CATALOG_STORAGE_PLACES_RETRIEVE_BY_IDS,
            EATS_SUPPORT_MISC_ORDER_SUPPORT_META,
            GROCERY_EATS_GATEWAY_LATEST_ORDERS,
            200,
            {
                'suggest_buttons': [
                    {
                        'payload': {
                            'suggest_id': 'chose_eater_order',
                            'order_nr': '111111-111111',
                            'question_about_grocery_order': True,
                        },
                        'text': 'Вопрос по заказу из Лавки',
                    },
                    {
                        'payload': {
                            'suggest_id': 'chose_eater_order',
                            'order_nr': '111111-300000',
                        },
                        'text': 'Заказ такой-то',
                    },
                    {
                        'payload': {
                            'suggest_id': 'chose_eater_order',
                            'order_nr': '111111-100000',
                        },
                        'text': 'Заказ такой-то',
                    },
                    {
                        'payload': {
                            'suggest_id': 'chose_eater_order',
                            'order_nr': '111111-400000',
                        },
                        'text': 'Заказ такой-то',
                    },
                    {
                        'payload': {
                            'suggest_id': 'chose_eater_order',
                            'order_nr': '111111-200000',
                        },
                        'text': 'Заказ такой-то',
                    },
                    {
                        'payload': {
                            'suggest_id': 'chose_eater_order',
                            'order_nr': '222222-222222',
                            'question_about_grocery_order': True,
                        },
                        'text': 'Вопрос по заказу из Лавки',
                    },
                    {
                        'payload': {'suggest_id': 'chose_eater_order'},
                        'text': 'Вопрос не по заказу',
                    },
                ],
                'tag': Anything(),
                'terminal': False,
                'text': 'Здравствуйте! Выберите, пожалуйста, заказ.',
            },
            id='root, chose order, right order',
        ),
        pytest.param(
            {'suggest_id': 'chose_eater_order', 'order_nr': ORDER_NR},
            EATS_EATERS_FIND_BY_PASSPORT_UID,
            EATS_ORDERSHISTORY_V2_GET_ORDERS_RESPONSE,
            EATS_CATALOG_STORAGE_PLACES_RETRIEVE_BY_IDS,
            EATS_SUPPORT_MISC_ORDER_SUPPORT_META,
            GROCERY_EATS_GATEWAY_LATEST_ORDERS,
            200,
            {
                'suggest_buttons': [
                    {
                        'payload': {
                            'suggest_id': 'payment_problem',
                            'order_nr': ORDER_NR,
                        },
                        'text': 'Проблема с оплатой',
                    },
                    {
                        'payload': {'suggest_id': 'root'},
                        'text': 'Выбрать другой заказ',
                    },
                ],
                'tag': Anything(),
                'terminal': False,
                'text': 'Вы выбрали заказ такой-то. Чем можем помочь?',
            },
            id='chosen specified order',
        ),
        pytest.param(
            {'suggest_id': 'payment_problem', 'order_nr': ORDER_NR},
            EATS_EATERS_FIND_BY_PASSPORT_UID,
            EATS_ORDERSHISTORY_V2_GET_ORDERS_RESPONSE,
            EATS_CATALOG_STORAGE_PLACES_RETRIEVE_BY_IDS,
            EATS_SUPPORT_MISC_ORDER_SUPPORT_META,
            GROCERY_EATS_GATEWAY_LATEST_ORDERS,
            200,
            {
                'suggest_buttons': [
                    {
                        'payload': {
                            'suggest_id': 'payment_problem__yes',
                            'order_nr': ORDER_NR,
                        },
                        'text': 'Да, закрыть чат',
                    },
                    {
                        'payload': {
                            'suggest_id': 'payment_problem__no',
                            'order_nr': ORDER_NR,
                        },
                        'text': 'Нет, позвать оператора',
                    },
                    {
                        'payload': {
                            'suggest_id': 'chose_eater_order',
                            'order_nr': ORDER_NR,
                        },
                        'text': 'Назад',
                    },
                ],
                'tag': Anything(),
                'terminal': False,
                'text': (
                    'Попробуйте переключить способ оплаты при создании'
                    ' заказа. Это помогло?'
                ),
            },
            id='chosen specified order : next level suggest',
        ),
        pytest.param(
            {'suggest_id': 'payment_problem__yes', 'order_nr': ORDER_NR},
            EATS_EATERS_FIND_BY_PASSPORT_UID,
            EATS_ORDERSHISTORY_V2_GET_ORDERS_RESPONSE,
            EATS_CATALOG_STORAGE_PLACES_RETRIEVE_BY_IDS,
            EATS_SUPPORT_MISC_ORDER_SUPPORT_META,
            GROCERY_EATS_GATEWAY_LATEST_ORDERS,
            200,
            {
                'tag': Anything(),
                'terminal': True,
                'text': 'Чат был закрыт. До свидания!',
            },
            id='terminate chat',
        ),
        pytest.param(
            {'suggest_id': 'payment_problem__no', 'order_nr': ORDER_NR},
            EATS_EATERS_FIND_BY_PASSPORT_UID,
            EATS_ORDERSHISTORY_V2_GET_ORDERS_RESPONSE,
            EATS_CATALOG_STORAGE_PLACES_RETRIEVE_BY_IDS,
            EATS_SUPPORT_MISC_ORDER_SUPPORT_META,
            GROCERY_EATS_GATEWAY_LATEST_ORDERS,
            422,
            {'chatterbox.meta': {'order_id': '111111-100000'}},
            id='switch to chatterbox chat',
        ),
        pytest.param(
            {'suggest_id': 'chose_eater_order'},
            EATS_EATERS_FIND_BY_PASSPORT_UID,
            EATS_ORDERSHISTORY_V2_GET_ORDERS_RESPONSE,
            EATS_CATALOG_STORAGE_PLACES_RETRIEVE_BY_IDS,
            EATS_SUPPORT_MISC_ORDER_SUPPORT_META,
            GROCERY_EATS_GATEWAY_LATEST_ORDERS,
            200,
            {
                'suggest_buttons': [
                    {
                        'payload': {'suggest_id': 'how_to_create_order'},
                        'text': 'Как сделать заказ',
                    },
                    {
                        'payload': {'suggest_id': 'root'},
                        'text': 'Выбрать другой заказ',
                    },
                ],
                'tag': Anything(),
                'terminal': False,
                'text': 'Чем мы можем вам помочь не по конкретному заказу?',
            },
            id='chosen question not about order',
        ),
        pytest.param(
            {
                'suggest_id': 'chose_eater_order',
                'order_nr': '111111-111111',
                'question_about_grocery_order': True,
            },
            EATS_EATERS_FIND_BY_PASSPORT_UID,
            EATS_ORDERSHISTORY_V2_GET_ORDERS_RESPONSE,
            EATS_CATALOG_STORAGE_PLACES_RETRIEVE_BY_IDS,
            EATS_SUPPORT_MISC_ORDER_SUPPORT_META,
            GROCERY_EATS_GATEWAY_LATEST_ORDERS,
            422,
            {
                'chatterbox.meta': {
                    'order_id': '111111-111111',
                    'eater_name': 'Olya',
                },
            },
            id='chosen question about grocery order',
        ),
        pytest.param(
            {'suggest_id': 'root'},
            EATS_EATERS_FIND_BY_PASSPORT_UID,
            {'orders': []},
            EATS_CATALOG_STORAGE_PLACES_RETRIEVE_BY_IDS,
            EATS_SUPPORT_MISC_ORDER_SUPPORT_META,
            [],
            200,
            {
                'suggest_buttons': [
                    {
                        'payload': {'suggest_id': 'how_to_create_order'},
                        'text': 'Как сделать заказ',
                    },
                ],
                'tag': Anything(),
                'terminal': False,
                'text': 'Чем мы можем вам помочь не по конкретному заказу?',
            },
            id='root, user has not orders',
        ),
    ],
)
@pytest.mark.experiments3(
    filename='eats_messenger_eater_to_support_suggest_trees.json',
)
async def test_green_flow(
        taxi_eats_messenger,
        mockserver,
        callback_data,
        eats_eaters_response,
        eats_ordershistory_response,
        eats_catalog_storage_response,
        eats_support_misc_response,
        grocery_eats_gateway_response,
        expected_response_code,
        expected_response_json,
):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uid')
    def _mock_eats_eaters_(request):  # pylint: disable=unused-variable
        return mockserver.make_response(json=eats_eaters_response, status=200)

    @mockserver.json_handler(
        '/grocery-eats-gateway/grocery-eats-gateway/v1/latest',
    )
    def _mock_grocery_eats_gateway_(
            request,
    ):  # pylint: disable=unused-variable
        return mockserver.make_response(
            json=grocery_eats_gateway_response, status=200,
        )

    @mockserver.json_handler('/eats-ordershistory/v2/get-orders')
    def _mock_eats_ordershistory_(request):  # pylint: disable=unused-variable
        return mockserver.make_response(
            json=eats_ordershistory_response, status=200,
        )

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def _mock_eats_catalog_storage_(
            request,
    ):  # pylint: disable=unused-variable
        return mockserver.make_response(
            json=eats_catalog_storage_response, status=200,
        )

    @mockserver.json_handler('/eats-support-misc/v1/get-support-meta')
    def _mock_eats_support_misc_(request):  # pylint: disable=unused-variable
        return mockserver.make_response(
            json=eats_support_misc_response, status=200,
        )

    response = await taxi_eats_messenger.post(
        '/internal-api/v1/eats-messenger/v1/suggests/client-to-support',
        {'puid': 1234, 'context': {}, 'callback_data': callback_data},
    )

    assert response.status_code == expected_response_code
    assert response.json() == expected_response_json


@pytest.mark.parametrize(
    ['puid', 'callback_data', 'endpoints_times_called'],
    [
        (0, {}, [0, 0, 0, 0]),
        (1234, {}, [1, 1, 1, 0]),
        (1234, {'order_nr': '111111-100000'}, [1, 1, 1, 1]),
    ],
    ids=[
        'No endpoints, cause not authorized',
        'Authorized, get eater_id -> eater_orders -> places_info '
        'by place_ids in eater_orders',
        'Authorized, get eater_id -> eater_orders -> places_info '
        'by place_ids in eater_orders, '
        'callback_data has order_nr -> get order support meta',
    ],
)
@pytest.mark.experiments3(
    filename='eats_messenger_eater_to_support_suggest_trees.json',
)
async def test_chat_event_processor_data_filling_endpoints(
        taxi_eats_messenger,
        mockserver,
        puid,
        callback_data,
        endpoints_times_called,
):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uid')
    def _mock_eats_eaters_(request):
        return mockserver.make_response(
            json=EATS_EATERS_FIND_BY_PASSPORT_UID, status=200,
        )

    @mockserver.json_handler('/eats-ordershistory/v2/get-orders')
    def _mock_eats_ordershistory_(request):
        return mockserver.make_response(
            json=EATS_ORDERSHISTORY_V2_GET_ORDERS_RESPONSE, status=200,
        )

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def _mock_eats_catalog_storage_(request):
        return mockserver.make_response(
            json=EATS_CATALOG_STORAGE_PLACES_RETRIEVE_BY_IDS, status=200,
        )

    @mockserver.json_handler(
        '/grocery-eats-gateway/grocery-eats-gateway/v1/latest',
    )
    def _mock_grocery_eats_gateway_(
            request,
    ):  # pylint: disable=unused-variable
        return mockserver.make_response(
            json=GROCERY_EATS_GATEWAY_LATEST_ORDERS, status=200,
        )

    @mockserver.json_handler('/eats-support-misc/v1/get-support-meta')
    def _mock_eats_support_misc_(request):
        return mockserver.make_response(
            json=EATS_SUPPORT_MISC_ORDER_SUPPORT_META, status=200,
        )

    response = await taxi_eats_messenger.post(
        '/internal-api/v1/eats-messenger/v1/suggests/client-to-support',
        {'puid': puid, 'context': {}, 'callback_data': callback_data},
    )

    assert response.status_code == 200
    assert [
        _mock_eats_eaters_.times_called,
        _mock_eats_ordershistory_.times_called,
        _mock_eats_catalog_storage_.times_called,
        _mock_eats_support_misc_.times_called,
    ] == endpoints_times_called


@pytest.mark.now('2020-04-28T12:21:00.100000+03:00')
@pytest.mark.parametrize(
    ['puid', 'callback_data', 'ordershistory_response', 'expected_response'],
    [
        (
            123,
            {'suggest_id': 'chose_eater_order'},
            EATS_ORDERSHISTORY_V2_GET_ORDERS_RESPONSE,
            {
                'suggest_buttons': [
                    {
                        'payload': {'suggest_id': 'how_to_create_order'},
                        'text': 'Как сделать заказ',
                    },
                    {
                        'payload': {'suggest_id': 'root'},
                        'text': 'Выбрать другой заказ',
                    },
                ],
                'tag': Anything(),
                'terminal': False,
                'text': 'Чем мы можем вам помочь не по конкретному заказу?',
            },
        ),
        (
            123,
            {'suggest_id': 'chose_eater_order'},
            {'orders': []},
            {
                'suggest_buttons': [
                    {
                        'payload': {'suggest_id': 'how_to_create_order'},
                        'text': 'Как сделать заказ',
                    },
                ],
                'tag': Anything(),
                'terminal': False,
                'text': 'Чем мы можем вам помочь не по конкретному заказу?',
            },
        ),
        (
            123,
            {'suggest_id': 'how_to_create_order'},
            {'orders': []},
            {
                'suggest_buttons': [
                    {
                        'text': 'Да, закрыть чат',
                        'payload': {'suggest_id': 'how_to_create_order__yes'},
                    },
                    {
                        'text': 'Нет, позвать оператора',
                        'payload': {'suggest_id': 'how_to_create_order__no'},
                    },
                    {'text': 'Назад', 'payload': {'suggest_id': 'root'}},
                ],
                'tag': Anything(),
                'terminal': False,
                'text': (
                    'Пройдите в каталог, выберите ресторан, добавьте '
                    'понравившиеся блюда и оплатите заказ. Это помогло?'
                ),
            },
        ),
    ],
    ids=[
        'chose_eater_order with orders',
        'chose_eater_order without orders',
        'suggest under chose_eater_order without orders',
    ],
)
@pytest.mark.experiments3(
    filename='eats_messenger_eater_to_support_suggest_trees.json',
)
async def test_chat_event_processor_back_button_chose_eater_order_corners_root(
        taxi_eats_messenger,
        mockserver,
        puid,
        callback_data,
        ordershistory_response,
        expected_response,
):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uid')
    def _mock_eats_eaters_(request):  # pylint: disable=unused-variable
        return mockserver.make_response(
            json=EATS_EATERS_FIND_BY_PASSPORT_UID, status=200,
        )

    @mockserver.json_handler('/eats-ordershistory/v2/get-orders')
    def _mock_eats_ordershistory_(request):  # pylint: disable=unused-variable
        return mockserver.make_response(
            json=ordershistory_response, status=200,
        )

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def _mock_eats_catalog_storage_(
            request,
    ):  # pylint: disable=unused-variable
        return mockserver.make_response(
            json=EATS_CATALOG_STORAGE_PLACES_RETRIEVE_BY_IDS, status=200,
        )

    @mockserver.json_handler(
        '/grocery-eats-gateway/grocery-eats-gateway/v1/latest',
    )
    def _mock_grocery_eats_gateway_(
            request,
    ):  # pylint: disable=unused-variable
        return mockserver.make_response(json=[], status=200)

    response = await taxi_eats_messenger.post(
        '/internal-api/v1/eats-messenger/v1/suggests/client-to-support',
        {'puid': puid, 'callback_data': callback_data},
    )

    assert response.status_code == 200
    assert (
        response.json()['suggest_buttons']
        == expected_response['suggest_buttons']
    )


@pytest.mark.now('2020-04-28T12:21:00.100000+03:00')
@pytest.mark.parametrize(
    ['puid', 'context', 'expected_code', 'expected_response'],
    [
        (
            123,
            {'order_id': ORDER_NR},
            200,
            {
                'suggest_buttons': [
                    {
                        'payload': {
                            'order_nr': '111111-100000',
                            'suggest_id': 'payment_problem',
                        },
                        'text': 'Проблема с оплатой',
                    },
                    {
                        'payload': {'suggest_id': 'root'},
                        'text': 'Выбрать другой заказ',
                    },
                ],
                'tag': Anything(),
                'terminal': False,
                'text': 'Вы выбрали заказ такой-то. Чем можем помочь?',
            },
        ),
        (
            123,
            {'order_id': '111111-111111'},
            422,
            {
                'chatterbox.meta': {
                    'order_id': '111111-111111',
                    'eater_name': 'Olya',
                },
            },
        ),
    ],
    ids=[
        'chose_eater_order with context order_nr eda',
        'chose_eater_order with context order_nr grocery',
    ],
)
@pytest.mark.experiments3(
    filename='eats_messenger_eater_to_support_suggest_trees.json',
)
async def test_chat_event_processor_context_order_nr(
        taxi_eats_messenger,
        mockserver,
        puid,
        context,
        expected_code,
        expected_response,
):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uid')
    def _mock_eats_eaters_(request):  # pylint: disable=unused-variable
        return mockserver.make_response(
            json=EATS_EATERS_FIND_BY_PASSPORT_UID, status=200,
        )

    @mockserver.json_handler('/eats-ordershistory/v2/get-orders')
    def _mock_eats_ordershistory_(request):  # pylint: disable=unused-variable
        return mockserver.make_response(
            json=EATS_ORDERSHISTORY_V2_GET_ORDERS_RESPONSE, status=200,
        )

    @mockserver.json_handler('/eats-support-misc/v1/get-support-meta')
    def _mock_eats_support_misc_(request):  # pylint: disable=unused-variable
        return mockserver.make_response(
            json=EATS_SUPPORT_MISC_ORDER_SUPPORT_META, status=200,
        )

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def _mock_eats_catalog_storage_(
            request,
    ):  # pylint: disable=unused-variable
        return mockserver.make_response(
            json=EATS_CATALOG_STORAGE_PLACES_RETRIEVE_BY_IDS, status=200,
        )

    @mockserver.json_handler(
        '/grocery-eats-gateway/grocery-eats-gateway/v1/latest',
    )
    def _mock_grocery_eats_gateway_(
            request,
    ):  # pylint: disable=unused-variable
        return mockserver.make_response(
            json=GROCERY_EATS_GATEWAY_LATEST_ORDERS, status=200,
        )

    response = await taxi_eats_messenger.post(
        '/internal-api/v1/eats-messenger/v1/suggests/client-to-support',
        {'puid': puid, 'context': context},
    )

    assert response.status_code == expected_code
    assert response.json() == expected_response


@pytest.mark.parametrize(
    ['puid', 'callback_data', 'ordershistory_response', 'expected_response'],
    [
        (
            123,
            {'suggest_id': 'chose_eater_order'},
            {'orders': []},
            {
                'suggest_buttons': [
                    {
                        'text': 'Как сделать заказ',
                        'payload': {'suggest_id': 'how_to_create_order'},
                    },
                    {
                        'text': 'Назад',
                        'payload': {
                            'suggest_id': 'parent_for_chose_eater_order',
                        },
                    },
                ],
                'tag': Anything(),
                'terminal': False,
                'text': (
                    'Пройдите в каталог, выберите ресторан, добавьте '
                    'понравившиеся блюда и оплатите заказ. Это помогло?'
                ),
            },
        ),
    ],
    ids=['chose_eater_order without orders'],
)
@pytest.mark.experiments3(
    filename='eats_messenger_eater_to_support_chose_eater_'
    'order_corner_tree.json',
)
async def test_chat_event_processor_back_button_chose_eater_order_corners(
        taxi_eats_messenger,
        mockserver,
        experiments3,
        puid,
        callback_data,
        ordershistory_response,
        expected_response,
):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uid')
    def _mock_eats_eaters_(request):  # pylint: disable=unused-variable
        return mockserver.make_response(
            json=EATS_EATERS_FIND_BY_PASSPORT_UID, status=200,
        )

    @mockserver.json_handler('/eats-ordershistory/v2/get-orders')
    def _mock_eats_ordershistory_(request):  # pylint: disable=unused-variable
        return mockserver.make_response(
            json=ordershistory_response, status=200,
        )

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def _mock_eats_catalog_storage_(
            request,
    ):  # pylint: disable=unused-variable
        return mockserver.make_response(
            json=EATS_CATALOG_STORAGE_PLACES_RETRIEVE_BY_IDS, status=200,
        )

    @mockserver.json_handler(
        '/grocery-eats-gateway/grocery-eats-gateway/v1/latest',
    )
    def _mock_grocery_eats_gateway_(
            request,
    ):  # pylint: disable=unused-variable
        return mockserver.make_response(json=[], status=200)

    response = await taxi_eats_messenger.post(
        '/internal-api/v1/eats-messenger/v1/suggests/client-to-support',
        {'puid': puid, 'callback_data': callback_data},
    )

    assert response.status_code == 200
    assert (
        response.json()['suggest_buttons']
        == expected_response['suggest_buttons']
    )
