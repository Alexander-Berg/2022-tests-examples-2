# pylint: disable=unused-variable

import pytest


@pytest.mark.parametrize(
    ['expected_body', 'called_region', 'exp_channel', 'exp_enabled'],
    [
        [
            {
                'meta': {'count': 1},
                'payload': {
                    'channels': [
                        {
                            'id': 1,
                            'channel': '+7906',
                            'type': 'phone',
                            'text': 'Текст',
                        },
                    ],
                },
            },
            '1',
            '+7906',
            True,
        ],
        [
            {
                'meta': {'count': 1},
                'payload': {
                    'channels': [
                        {
                            'id': 1,
                            'channel': '+7495',
                            'type': 'phone',
                            'text': 'Текст',
                        },
                    ],
                },
            },
            '1',
            '',
            True,
        ],
        [
            {
                'meta': {'count': 1},
                'payload': {
                    'channels': [
                        {
                            'id': 1,
                            'channel': '8800',
                            'type': 'phone',
                            'text': 'Текст',
                        },
                    ],
                },
            },
            '2',
            '',
            True,
        ],
        [
            {
                'meta': {'count': 1},
                'payload': {
                    'channels': [
                        {
                            'id': 1,
                            'channel': '88006001210',
                            'type': 'phone',
                            'text': 'Позвонить',
                        },
                    ],
                },
            },
            '2',
            '',
            False,
        ],
    ],
    ids=[
        'Phone from exp',
        'Phone override via the region config',
        'Phone by region doesn\'t exist',
        'Fallen back to a default phone if the exp is turned off',
    ],
)
@pytest.mark.config(
    EATS_FEEDBACK_PHONE_NUMBERS={
        '__default__': {'phone_number': '8800', 'id': 2},
        '1': {'phone_number': '+7495', 'id': 1},
    },
)
async def test_eats_messenger_phone(
        taxi_eats_messenger,
        mockserver,
        experiments3,
        expected_body,
        called_region,
        exp_channel,
        exp_enabled,
):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_eda_eats_ordershistory_(request):
        return mockserver.make_response(json={'orders': []}, status=200)

    experiments3.add_config(
        name='eats_messenger_feedback_channels',
        consumers=['eats-messenger/feedback-channels'],
        match={'predicate': {'type': 'true'}, 'enabled': exp_enabled},
        clauses=[],
        default_value={
            'enabled': True,
            'one_chat': True,
            'channels': [
                {
                    'id': 1,
                    'type': 'phone',
                    'text': 'text',
                    'text_key': 'feedback_channels.text_key',
                    'channel': exp_channel,
                },
            ],
        },
    )

    response = await taxi_eats_messenger.get(
        '/eats/v1/eats-messenger/v1/feedback-channels?regionId='
        + called_region,
    )

    assert response.json() == expected_body


@pytest.mark.parametrize(
    [
        'expected_body',
        'expected_phone_id',
        'one_chat',
        'query_order_nr',
        'expected_history_calls',
        'expected_history_request',
        'history',
        'taxi_user',
    ],
    [
        [
            {
                'meta': {'count': 1},
                'payload': {
                    'channels': [
                        {
                            'id': 2,
                            'channel': 'link',
                            'type': 'chat',
                            'text': 'Текст',
                        },
                    ],
                },
            },
            '',
            False,
            None,
            0,
            {},
            [],
            '',
        ],
        [
            {
                'meta': {'count': 1},
                'payload': {
                    'channels': [
                        {
                            'id': 1,
                            'channel': 'link?order_nr=123123-123123',
                            'type': 'chat',
                            'text': 'Текст',
                        },
                    ],
                },
            },
            '',
            False,
            '123123-123123',
            0,
            {},
            [],
            '',
        ],
        [
            {
                'meta': {'count': 1},
                'payload': {
                    'channels': [
                        {
                            'id': 1,
                            'channel': 'link?order_nr=123123-123123',
                            'type': 'chat',
                            'text': 'Текст',
                        },
                    ],
                },
            },
            'g9348hj',
            False,
            '123123-123123',
            1,
            {
                'eats_user_id': 42,
                'orders': 1,
                'cart': False,
                'delivery_address': False,
                'offset': 0,
            },
            {
                'orders': [
                    {
                        'order_id': '321321-321321',
                        'status': 'delivered',
                        'created_at': '2019-12-31T23:58:59+00:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'total_amount': '123.45',
                        'is_asap': True,
                        'place_id': 40000,
                    },
                ],
            },
            'personal_phone_id=g9348hj, user_id=42',
        ],
        [
            {
                'meta': {'count': 2},
                'payload': {
                    'channels': [
                        {
                            'id': 1,
                            'channel': 'link?order_nr=321321-321321',
                            'type': 'chat',
                            'text': 'Текст',
                        },
                        {
                            'id': 2,
                            'channel': 'link',
                            'type': 'chat',
                            'text': 'Текст',
                        },
                    ],
                },
            },
            'g9348hj',
            False,
            None,
            1,
            {
                'eats_user_id': 42,
                'orders': 1,
                'cart': False,
                'delivery_address': False,
                'offset': 0,
            },
            {
                'orders': [
                    {
                        'order_id': '321321-321321',
                        'status': 'delivered',
                        'created_at': '2019-12-31T23:58:59+00:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'total_amount': '123.45',
                        'is_asap': True,
                        'place_id': 40000,
                    },
                ],
            },
            'personal_phone_id=g9348hj, user_id=42',
        ],
        [
            {
                'meta': {'count': 1},
                'payload': {
                    'channels': [
                        {
                            'id': 2,
                            'channel': 'link',
                            'type': 'chat',
                            'text': 'Текст',
                        },
                    ],
                },
            },
            '',
            True,
            None,
            0,
            {},
            [],
            '',
        ],
        [
            {
                'meta': {'count': 1},
                'payload': {
                    'channels': [
                        {
                            'id': 1,
                            'channel': 'link?order_nr=123123-123123',
                            'type': 'chat',
                            'text': 'Текст',
                        },
                    ],
                },
            },
            'g9348hj',
            True,
            '123123-123123',
            1,
            {
                'eats_user_id': 42,
                'orders': 1,
                'cart': False,
                'delivery_address': False,
                'offset': 0,
            },
            {
                'orders': [
                    {
                        'order_id': '321321-321321',
                        'status': 'delivered',
                        'created_at': '2019-12-31T23:58:59+00:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'total_amount': '123.45',
                        'is_asap': True,
                        'place_id': 40000,
                    },
                ],
            },
            'personal_phone_id=g9348hj, user_id=42',
        ],
        [
            {
                'meta': {'count': 1},
                'payload': {
                    'channels': [
                        {
                            'id': 1,
                            'channel': 'link?order_nr=321321-321321',
                            'type': 'chat',
                            'text': 'Текст',
                        },
                    ],
                },
            },
            'g9348hj',
            True,
            None,
            1,
            {
                'eats_user_id': 42,
                'orders': 1,
                'cart': False,
                'delivery_address': False,
                'offset': 0,
            },
            {
                'orders': [
                    {
                        'order_id': '321321-321321',
                        'status': 'delivered',
                        'created_at': '2019-12-31T23:58:59+00:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'total_amount': '123.45',
                        'is_asap': True,
                        'place_id': 40000,
                    },
                ],
            },
            'personal_phone_id=g9348hj, user_id=42',
        ],
    ],
    ids=[
        'No auth, one_chat=false -> general chat only',
        'No auth, one_chat=false, order nr provided via query '
        '-> order chat only',
        'Auth, has order, one_chat=false, order nr provided via query '
        '-> order chat only, nr from query',
        'Auth, has order, one_chat=false, order nr from history -> both chats',
        'No auth, one_chat=true -> general chat only',
        'Auth, one_chat=true, order nr provided via query '
        '-> order chat only, nr from query',
        'Auth, one_chat=true, order nr from history -> order chat only',
    ],
)
@pytest.mark.config(
    EATS_FEEDBACK_PHONE_NUMBERS={
        '1': {'phone_number': '8800', 'id': 1},
        '__default__': {'phone_number': '72185', 'id': 2},
    },
)
async def test_eats_messenger_chat(
        taxi_eats_messenger,
        mockserver,
        experiments3,
        expected_body,
        expected_phone_id,
        one_chat,
        query_order_nr,
        expected_history_calls,
        expected_history_request,
        history,
        taxi_user,
):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_eda_eats_ordershistory_(request):
        return mockserver.make_response(json=history, status=200)

    experiments3.add_config(
        name='eats_messenger_feedback_channels',
        consumers=['eats-messenger/feedback-channels'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'enabled': True,
            'one_chat': one_chat,
            'channels': [
                {
                    'id': 1,
                    'type': 'chat',
                    'text': 'text',
                    'text_key': 'feedback_channels.text_key',
                    'channel': 'link?order_nr=',
                },
                {
                    'id': 2,
                    'type': 'chat_no_order',
                    'text': 'text',
                    'text_key': 'feedback_channels.text_key',
                    'channel': 'link',
                },
            ],
        },
    )

    if query_order_nr is None:
        response = await taxi_eats_messenger.get(
            '/eats/v1/eats-messenger/v1/feedback-channels',
            headers={'X-Eats-User': taxi_user},
        )
    else:
        response = await taxi_eats_messenger.get(
            '/eats/v1/eats-messenger/v1/feedback-channels?orderNr='
            + query_order_nr,
            headers={'X-Eats-User': taxi_user},
        )

    assert _mock_eda_eats_ordershistory_.times_called == expected_history_calls
    assert response.json() == expected_body


@pytest.mark.parametrize(
    [
        'expected_body',
        'expected_phone_id',
        'one_chat',
        'query_order_nr',
        'expected_history_calls',
        'history',
        'taxi_user',
    ],
    [
        [
            {
                'meta': {'count': 1},
                'payload': {
                    'channels': [
                        {
                            'bot_id': 'text',
                            'entrypoint': 'entrypoint',
                            'phone_number': '72185',
                            'type': 'yandex_messenger',
                        },
                    ],
                },
            },
            'g9348hj',
            True,
            None,
            1,
            {
                'orders': [
                    {
                        'order_id': '321321-321321',
                        'status': 'delivered',
                        'created_at': '2019-12-31T23:58:59+00:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'total_amount': '123.45',
                        'is_asap': True,
                        'place_id': 40000,
                    },
                ],
            },
            'personal_phone_id=g9348hj, user_id=42',
        ],
        [
            {
                'meta': {'count': 1},
                'payload': {
                    'channels': [
                        {
                            'bot_id': 'text',
                            'entrypoint': 'entrypoint',
                            'order_nr': '123123-123123',
                            'phone_number': '72185',
                            'type': 'yandex_messenger',
                        },
                    ],
                },
            },
            'g9348hj',
            True,
            '123123-123123',
            1,
            {'orders': []},
            'personal_phone_id=g9348hj, user_id=42',
        ],
    ],
    ids=[
        'Auth, one_chat=true, order nr from history, '
        'ignore enabled -> no order chat',
        'Auth, one_chat=true, order nr from query, '
        'ignore enabled -> query order_nr chat',
    ],
)
@pytest.mark.config(
    EATS_FEEDBACK_PHONE_NUMBERS={
        '1': {'phone_number': '8800', 'id': 1},
        '__default__': {'phone_number': '72185', 'id': 2},
    },
)
async def test_eats_messenger_chat_ignore_order_nr(
        taxi_eats_messenger,
        mockserver,
        experiments3,
        expected_body,
        expected_phone_id,
        one_chat,
        query_order_nr,
        expected_history_calls,
        history,
        taxi_user,
):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_eda_eats_ordershistory_(request):
        return mockserver.make_response(json=history, status=200)

    experiments3.add_config(
        name='eats_messenger_feedback_channels',
        consumers=['eats-messenger/feedback-channels'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'enabled': True,
            'one_chat': False,
            'channels': [
                {
                    'entrypoint': 'entrypoint',
                    'type': 'yandex_messenger',
                    'bot_id': 'text',
                    'ignore_order_nr': True,
                },
            ],
        },
    )

    if query_order_nr is None:
        response = await taxi_eats_messenger.get(
            '/eats/v1/eats-messenger/v1/feedback-channels',
            headers={'X-Eats-User': taxi_user},
        )
    else:
        response = await taxi_eats_messenger.get(
            '/eats/v1/eats-messenger/v1/feedback-channels?orderNr='
            + query_order_nr,
            headers={'X-Eats-User': taxi_user},
        )

    assert _mock_eda_eats_ordershistory_.times_called == expected_history_calls
    assert response.json() == expected_body


@pytest.mark.parametrize(
    ['expected_body', 'query_order_nr', 'taxi_user', 'history'],
    [
        [
            {
                'meta': {'count': 1},
                'payload': {
                    'channels': [
                        {
                            'bot_id': 'text',
                            'entrypoint': 'entrypoint',
                            'phone_number': '72185',
                            'type': 'yandex_messenger',
                        },
                    ],
                },
            },
            None,
            '',
            {},
        ],
        [
            {
                'meta': {'count': 1},
                'payload': {
                    'channels': [
                        {
                            'bot_id': 'text',
                            'entrypoint': 'entrypoint',
                            'order_nr': '321321-321321',
                            'phone_number': '72185',
                            'type': 'yandex_messenger',
                        },
                    ],
                },
            },
            '321321-321321',
            '',
            {},
        ],
        [
            {
                'meta': {'count': 1},
                'payload': {
                    'channels': [
                        {
                            'bot_id': 'text',
                            'entrypoint': 'entrypoint',
                            'order_nr': '321321-321321',
                            'phone_number': '72185',
                            'type': 'yandex_messenger',
                        },
                    ],
                },
            },
            None,
            'personal_phone_id=g9348hj, user_id=42',
            {
                'orders': [
                    {
                        'order_id': '321321-321321',
                        'status': 'delivered',
                        'created_at': '2019-12-31T23:58:59+00:00',
                        'source': 'eda',
                        'delivery_location': {'lat': 1.0, 'lon': 1.0},
                        'total_amount': '123.45',
                        'is_asap': True,
                        'place_id': 40000,
                    },
                ],
            },
        ],
    ],
    ids=[
        'No order_nr in history or query -> no order_nr from service',
        'Order_nr from query -> order_nr from service',
        'Order_nr from history -> order_nr from service',
    ],
)
@pytest.mark.config(
    EATS_FEEDBACK_PHONE_NUMBERS={
        '__default__': {'phone_number': '72185', 'id': 1},
    },
)
async def test_eats_messenger_yandex_messenger(
        taxi_eats_messenger,
        mockserver,
        experiments3,
        expected_body,
        query_order_nr,
        taxi_user,
        history,
):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_eda_eats_ordershistory_(request):
        return mockserver.make_response(json=history, status=200)

    experiments3.add_config(
        name='eats_messenger_feedback_channels',
        consumers=['eats-messenger/feedback-channels'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'enabled': True,
            'one_chat': False,
            'channels': [
                {
                    'entrypoint': 'entrypoint',
                    'type': 'yandex_messenger',
                    'bot_id': 'text',
                    'ignore_order_nr': False,
                },
            ],
        },
    )

    if query_order_nr is None:
        response = await taxi_eats_messenger.get(
            '/eats/v1/eats-messenger/v1/feedback-channels',
            headers={'X-Eats-User': taxi_user},
        )
    else:
        response = await taxi_eats_messenger.get(
            '/eats/v1/eats-messenger/v1/feedback-channels?orderNr='
            + query_order_nr,
            headers={'X-Eats-User': taxi_user},
        )

    assert response.json() == expected_body


@pytest.mark.parametrize(
    ['expected_body'],
    [
        [
            {
                'meta': {'count': 1},
                'payload': {
                    'channels': [
                        {
                            'id': 1,
                            'channel': '+7906',
                            'type': 'phone',
                            'text': 'Текст',
                        },
                    ],
                },
            },
        ],
    ],
    ids=['Green Flow'],
)
@pytest.mark.config(
    EATS_FEEDBACK_PHONE_NUMBERS={
        '__default__': {'phone_number': '8800', 'id': 2},
        '1': {'phone_number': '+7495', 'id': 1},
    },
    EATS_MESSENGER_SUPPORT_MISC_FEATURE_FLAG={'is_allowed_support_misc': True},
)
async def test_eats_messenger_additional_kwargs(
        taxi_eats_messenger, mockserver, experiments3, expected_body,
):
    @mockserver.json_handler('/eats-support-misc/v1/get-support-meta')
    def _mock_eda_eats_support_misc_(request):
        return mockserver.make_response(
            json={
                'metadata': {
                    'place_id': '1234',
                    'delivery_type': 'native',
                    'order_type': 'native',
                    'brand_id': '1',
                    'is_fast_food': True,
                },
            },
            status=200,
        )

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_eda_eats_ordershistory_(request):
        return mockserver.make_response(json={'orders': []}, status=200)

    experiments3.add_config(
        name='eats_messenger_feedback_channels',
        consumers=['eats-messenger/feedback-channels'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'enabled': True,
            'one_chat': True,
            'channels': [
                {
                    'id': 1,
                    'type': 'phone',
                    'text': 'text',
                    'text_key': 'feedback_channels.text_key',
                    'channel': '+7906',
                },
            ],
        },
    )

    exp3_recorder = experiments3.record_match_tries(
        'eats_messenger_feedback_channels',
    )

    response = await taxi_eats_messenger.get(
        '/eats/v1/eats-messenger/v1/feedback-channels?orderNr=111111-100000'
        '&regionId=3',
    )

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    assert match_tries[0].kwargs['region_id'] == '3'
    assert match_tries[0].kwargs['brand_id'] == '1'
    assert match_tries[0].kwargs['delivery_type'] == 'native'
    assert match_tries[0].kwargs['order_type'] == 'native'
    assert match_tries[0].kwargs['place_id'] == '1234'
    assert match_tries[0].kwargs['is_fast_food']

    assert response.json() == expected_body
