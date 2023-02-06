import uuid

import pytest

BASE_REQUEST = {
    'client_id': 'client_id_1',
    'route_type': 'ONE_A_MANY_B',
    'route_task_id': 'route_task_1',
    'common_point': {
        'country': 'Россия',
        'fullname': (
            'Россия, Москва, Люблинско-Дмитровская линия, метро Трубная'
        ),
        'short_text': 'метро Трубная',
        'short_text_from': 'метро Трубная',
        'short_text_to': 'метро Трубная',
        'geopoint': [37.62188427341478, 55.7679393937369],
        'locality': 'Москва',
        'thoroughfare': 'метро Трубная',
        'type': 'address',
        'object_type': 'другое',
    },
    'class': 'business',
    'orders': [
        {
            'phone': '+79992268443',
            'personal_phone_id': 'owner_personal_id',
            'comment': '',
            'user_points': [
                {
                    'user_personal_phone_id': 'per1',
                    'point': {
                        'country': 'Россия',
                        'fullname': (
                            'Россия, Москва, Люблинско-Дмитровская линия, '
                            'метро Достоевская'
                        ),
                        'short_text': 'метро Трубная',
                        'short_text_from': 'метро Трубная',
                        'short_text_to': 'метро Трубная',
                        'geopoint': [37.62188427341478, 55.7679393937369],
                        'locality': 'Москва',
                        'thoroughfare': 'метро Трубная',
                        'type': 'address',
                        'object_type': 'другое',
                    },
                },
                {
                    'user_personal_phone_id': 'per2',
                    'point': {
                        'country': 'Россия',
                        'fullname': (
                            'Россия, Москва, Таганско-Краснопресненская '
                            'линия, метро Пушкинская'
                        ),
                        'short_text': 'метро Пушкинская',
                        'short_text_from': 'метро Пушкинская',
                        'short_text_to': 'метро Пушкинская',
                        'geopoint': [37.6039000014267, 55.7657515910581],
                        'locality': 'Москва',
                        'thoroughfare': 'метро Пушкинская',
                        'type': 'address',
                        'object_type': 'другое',
                    },
                },
            ],
            'offer': '7a25c5c92796469198fff21aed18456f',
        },
    ],
}

RESPONSE_ORDER_IDS = [
    'a8ca021ff95fd95bb7b308df2ea5a4b6',
    'a1cc6a61171e4a409d923e1bbcc4fbf8',
]


BASE_COMMIT_RESPONSE_BODY = {
    '_id': uuid.uuid4().hex,
    'status': {
        'simple': 'active',
        'full': 'search',
        'description': 'Такси приедет через 10 мин.',
    },
}

SUCCESS_ORDER_CREATION = {
    'id': RESPONSE_ORDER_IDS[0],
    'code': 'ORDER_CREATED',
    'status': {
        'description': 'active',
        'full': 'search',
        'simple': 'Такси приедет через 10 мин.',
    },
}

PAYMENT_METHODS_FAILED = {
    'message': 'Персональный лимит на корпоративные поездки закончился',
    'code': 'PAYMENT_METHODS_FAILED',
}

PRICE_CHANGED = {
    'message': 'Цена поездки устарела или изменилась',
    'code': 'PRICE_CHANGED',
}

FATAL_ERROR = {'code': 'FATAL_ERROR', 'message': 'Order creation fatal error'}


@pytest.mark.parametrize(
    [
        'request_body',
        'expected_status',
        'expected_response',
        'corp_cabinet_response_status',
        'corp_cabinet_response_body',
        'cabinet_commit_response_status',
        'cabinet_commit_response_body',
    ],
    [
        pytest.param(
            {**BASE_REQUEST, **{'route_type': 'invalid'}},
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 52, path \'route_type\': '
                    'Value \'invalid\' is not '
                    'parseable into handlers::RouteType, the '
                    'latest token was : '
                    '"invalid"'
                ),
            },
            200,
            {'_id': RESPONSE_ORDER_IDS[0]},
            200,
            BASE_COMMIT_RESPONSE_BODY,
            id='schema validation fail',
        ),
        pytest.param(
            {**BASE_REQUEST, **{'route_task_id': 'some_task_id'}},
            400,
            {
                'code': '400',
                'message': 'route_task with id some_task_id does not exist',
            },
            200,
            {'_id': RESPONSE_ORDER_IDS[0]},
            200,
            BASE_COMMIT_RESPONSE_BODY,
            id='bad route_task_id reference',
        ),
        pytest.param(
            BASE_REQUEST,
            200,
            {'orders': [PAYMENT_METHODS_FAILED]},
            406,
            {
                'errors': [
                    {
                        'text': (
                            'Персональный лимит на '
                            'корпоративные поездки закончился'
                        ),
                        'code': 'GENERAL',
                    },
                ],
                'message': (
                    'Персональный лимит на корпоративные поездки закончился'
                ),
                'code': 'GENERAL',
            },
            200,
            BASE_COMMIT_RESPONSE_BODY,
            id='corp_pm failed',
        ),
        pytest.param(
            BASE_REQUEST,
            200,
            {'orders': [PRICE_CHANGED]},
            200,
            {'_id': RESPONSE_ORDER_IDS[0]},
            406,
            {
                'errors': [
                    {
                        'text': 'Цена поездки устарела или изменилась',
                        'code': 'PRICE_CHANGED',
                    },
                ],
                'message': 'Цена поездки устарела или изменилась',
                'code': 'PRICE_CHANGED',
            },
            id='price changed',
        ),
        pytest.param(
            BASE_REQUEST,
            200,
            {'orders': [FATAL_ERROR]},
            500,
            {},
            200,
            BASE_COMMIT_RESPONSE_BODY,
            id='fatal error',
        ),
    ],
)
@pytest.mark.pgsql('corp_combo_orders', files=['insert_route_tasks.sql'])
async def test_creation_fail(
        taxi_corp_combo_orders,
        mock_corp_cabinet,
        request_body,
        expected_status,
        expected_response,
        corp_cabinet_response_status,
        corp_cabinet_response_body,
        cabinet_commit_response_status,
        cabinet_commit_response_body,
):
    mock_corp_cabinet.data.cabinet_response_body = (
        b for b in [corp_cabinet_response_body]
    )
    mock_corp_cabinet.data.cabinet_response_status = (
        s for s in [corp_cabinet_response_status]
    )
    mock_corp_cabinet.data.commit_response_body = cabinet_commit_response_body
    mock_corp_cabinet.data.commit_response_status = (
        cabinet_commit_response_status
    )

    response = await taxi_corp_combo_orders.post(
        '/v1/orders/create', json=request_body,
    )

    assert response.status == expected_status
    assert response.json() == expected_response


@pytest.mark.pgsql('corp_combo_orders', files=['insert_route_tasks.sql'])
async def test_single_creation(
        taxi_corp_combo_orders, mock_corp_cabinet, pgsql, load_json,
):
    mock_corp_cabinet.data.cabinet_response_body = (
        b for b in [{'_id': RESPONSE_ORDER_IDS[0]}]
    )
    mock_corp_cabinet.data.cabinet_response_status = (s for s in [200])
    mock_corp_cabinet.data.commit_response_body = BASE_COMMIT_RESPONSE_BODY
    mock_corp_cabinet.data.commit_response_status = 200

    response = await taxi_corp_combo_orders.post(
        '/v1/orders/create',
        json=BASE_REQUEST,
        headers={'X-Application-Version': '0.0.100'},
    )

    assert response.status == 200
    assert response.json() == {'orders': [SUCCESS_ORDER_CREATION]}

    cursor = pgsql['corp_combo_orders'].cursor()
    cursor.execute(
        'SELECT id, client_id, route_task_id, '
        'route_type, common_point '
        'FROM corp_combo_orders.deliveries ORDER BY id;',
    )
    delivery = list(cursor)[0]
    delivery_id = delivery[0]
    assert delivery == (
        delivery_id,
        'client_id_1',
        'route_task_1',
        'ONE_A_MANY_B',
        {
            'geopoint': [37.62188427341478, 55.7679393937369],
            'fullname': (
                'Россия, Москва, Люблинско-Дмитровская линия, ' 'метро Трубная'
            ),
        },
    )

    order_request = mock_corp_cabinet.data.cabinet_request
    expected_request = load_json('corp_cabinet_request.json')
    expected_request['combo_order']['delivery_id'] = delivery_id
    assert order_request.json == expected_request
    assert order_request.headers['X-Application-Version'] == '0.0.100'

    cursor.execute(
        'SELECT id, delivery_id, source, destination, '
        'interim_destinations, status, taxi_status '
        'FROM corp_combo_orders.orders ORDER BY id;',
    )
    assert list(cursor) == [
        (
            'a8ca021ff95fd95bb7b308df2ea5a4b6',
            delivery_id,
            {
                'fullname': (
                    'Россия, Москва, Люблинско-Дмитровская линия, '
                    'метро Трубная'
                ),
                'geopoint': [37.62188427341478, 55.7679393937369],
            },
            {
                'fullname': (
                    'Россия, Москва, Таганско-Краснопресненская линия, '
                    'метро Пушкинская'
                ),
                'geopoint': [37.6039000014267, 55.7657515910581],
            },
            [
                {
                    'fullname': (
                        'Россия, Москва, Люблинско-Дмитровская линия, '
                        'метро Достоевская'
                    ),
                    'geopoint': [37.62188427341478, 55.7679393937369],
                },
            ],
            'pending',
            '',
        ),
    ]

    cursor.execute(
        'SELECT id, order_id, user_personal_phone_id, point '
        'FROM corp_combo_orders.order_points ORDER BY id;',
    )
    assert list(cursor) == [
        (
            1,
            'a8ca021ff95fd95bb7b308df2ea5a4b6',
            'per1',
            {
                'geopoint': [37.62188427341478, 55.7679393937369],
                'fullname': (
                    'Россия, Москва, Люблинско-Дмитровская линия, '
                    'метро Достоевская'
                ),
            },
        ),
        (
            2,
            'a8ca021ff95fd95bb7b308df2ea5a4b6',
            'per2',
            {
                'geopoint': [37.6039000014267, 55.7657515910581],
                'fullname': (
                    'Россия, Москва, Таганско-Краснопресненская линия, '
                    'метро Пушкинская'
                ),
            },
        ),
    ]


@pytest.mark.parametrize(
    [
        'expected_response',
        'corp_cabinet_response_statuses',
        'corp_cabinet_response_bodies',
    ],
    [
        pytest.param(
            {
                'orders': [
                    {
                        **SUCCESS_ORDER_CREATION,
                        **{'id': RESPONSE_ORDER_IDS[1]},
                    },
                    SUCCESS_ORDER_CREATION,
                ],
            },
            [200, 200],
            [{'_id': RESPONSE_ORDER_IDS[1]}, {'_id': RESPONSE_ORDER_IDS[0]}],
            id='same idempotency tokens',
        ),
        pytest.param(
            {'orders': [SUCCESS_ORDER_CREATION, PAYMENT_METHODS_FAILED]},
            [200, 406],
            [
                {'_id': RESPONSE_ORDER_IDS[0]},
                {
                    'errors': [
                        {
                            'text': (
                                'Персональный лимит на '
                                'корпоративные поездки закончился'
                            ),
                            'code': 'GENERAL',
                        },
                    ],
                    'message': (
                        'Персональный лимит на корпоративные '
                        'поездки закончился'
                    ),
                    'code': 'GENERAL',
                },
            ],
            id='different idempotency tokens',
        ),
    ],
)
@pytest.mark.pgsql('corp_combo_orders', files=['insert_route_tasks.sql'])
async def test_multiple_orders_create(
        taxi_corp_combo_orders,
        mock_corp_cabinet,
        pgsql,
        expected_response,
        corp_cabinet_response_statuses,
        corp_cabinet_response_bodies,
):
    mock_corp_cabinet.data.cabinet_response_body = (
        b for b in corp_cabinet_response_bodies
    )
    mock_corp_cabinet.data.cabinet_response_status = (
        s for s in corp_cabinet_response_statuses
    )

    mock_corp_cabinet.data.commit_response_body = BASE_COMMIT_RESPONSE_BODY
    mock_corp_cabinet.data.commit_response_status = 200
    response = await taxi_corp_combo_orders.post(
        '/v1/orders/create',
        json={
            **BASE_REQUEST,
            **{'orders': [BASE_REQUEST['orders'][0] for _ in range(2)]},
        },
    )

    assert (
        sorted(
            response.json()['orders'], key=lambda x: (x['code'], x.get('id')),
        )
        == expected_response['orders']
    )

    cursor = pgsql['corp_combo_orders'].cursor()
    cursor.execute('SELECT COUNT(*) FROM corp_combo_orders.deliveries;')
    assert list(cursor) == [(1,)]

    cursor.execute('SELECT COUNT(*) FROM corp_combo_orders.orders;')
    assert list(cursor) == [
        (len([s for s in corp_cabinet_response_statuses if s == 200]),),
    ]
