import datetime

import pytest

from taxi.clients import integration_api


@pytest.mark.config(MAX_CORPCABINET_ORDERS=15)
@pytest.mark.now('2016-06-15T09:00:00')
@pytest.mark.translations(
    corp={
        'order.taxi_will_arrive_in_time': {
            'ru': 'Такси приедет через {minutes:d} мин.',
        },
        'error.order_commit_default_error': {'ru': 'Невозможно создать заказ'},
        'error.order_commit_max_limit_error': {
            'ru': (
                'На данный номер телефона уже сделано {} заказов. '
                'Лимит превышен'
            ),
        },
    },
)
@pytest.mark.parametrize(
    'client, prefix, passport_mock',
    [
        ('taxi_corp_real_auth_client', '/1.0/client/client1', 'client1'),
        ('taxi_corp_tvm_client', '/internal/1.0', None),
    ],
    indirect=['client', 'passport_mock'],
)
@pytest.mark.parametrize(
    'commit_responses_data, expected_status, expected_result, expected_db',
    [
        (
            [
                {
                    'status': 200,
                    'data': {'orderid': 'order_id_1', 'status': 'search'},
                    'headers': {},
                },
            ],
            200,
            {
                'status': {
                    'simple': 'active',
                    'full': 'search',
                    'description': 'Такси приедет через 10 мин.',
                },
                '_id': 'order_id_1',
            },
            {
                '_id': 'order_id_1',
                'client_id': 'client1',
                'city': 'Москва',
                'class': 'econom',
                'corp_user': {'user_id': 'user_id'},
                'created_by': {'login': 'lubsandodok-client-requests'},
                'status': 'pending',
                'taxi_user_id': 'taxi_user_id_1',
                'created_date': datetime.datetime(2016, 6, 15, 9, 0, 26),
                'due_date': datetime.datetime(2016, 6, 15, 9, 10, 26),
                'source': {
                    'fullname': 'Россия, Москва, улица Льва Толстого, 16',
                    'geopoint': [37.588144, 55.733842],
                },
            },
        ),
        (
            [
                {
                    'status': 202,
                    'headers': {'Retry-After': 0},
                    'data': {'error': {'text': 'Parallel commit'}},
                },
                {
                    'status': 200,
                    'data': {'orderid': 'order_id_202', 'status': 'search'},
                    'headers': {},
                },
            ],
            200,
            {
                'status': {
                    'simple': 'active',
                    'full': 'search',
                    'description': 'Такси приедет через 10 мин.',
                },
                '_id': 'order_id_202',
            },
            {
                '_id': 'order_id_202',
                'client_id': 'client1',
                'city': 'Москва',
                'class': 'econom',
                'corp_user': {'user_id': 'user_id'},
                'created_by': {'login': 'lubsandodok-client-requests'},
                'status': 'pending',
                'taxi_user_id': 'taxi_user_id_1',
                'created_date': datetime.datetime(2016, 6, 15, 9, 0, 26),
                'due_date': datetime.datetime(2016, 6, 15, 9, 10, 26),
                'source': {
                    'fullname': 'Россия, Москва, улица Льва Толстого, 16',
                    'geopoint': [37.588144, 55.733842],
                },
            },
        ),
        (
            [
                {
                    'status': 406,
                    'data': {
                        'code': 'TOO_MANY_UNFINISHED_ORDERS',
                        'text': 'text',
                    },
                    'headers': {},
                },
            ],
            406,
            {
                'errors': [
                    {'code': 'TOO_MANY_UNFINISHED_ORDERS', 'text': 'text'},
                ],
                'message': 'text',
                'code': 'TOO_MANY_UNFINISHED_ORDERS',
            },
            None,
        ),
        (
            [
                {
                    'status': 403,
                    'data': {'blocked': '2015', 'type': 'type'},
                    'headers': {},
                },
            ],
            406,
            {
                'errors': [
                    {'code': 'GENERAL', 'text': 'Невозможно создать заказ'},
                ],
                'message': 'Невозможно создать заказ',
                'code': 'GENERAL',
            },
            None,
        ),
        (
            [
                {
                    'status': 403,
                    'data': {'blocked': '2015', 'type': 'type'},
                    'headers': {},
                },
            ],
            406,
            {
                'errors': [
                    {'code': 'GENERAL', 'text': 'Невозможно создать заказ'},
                ],
                'message': 'Невозможно создать заказ',
                'code': 'GENERAL',
            },
            None,
        ),
        (
            [
                {
                    'status': 406,
                    'data': {'code': 'MISSING_UID', 'text': 'text'},
                    'headers': {},
                },
            ],
            403,
            {
                'errors': [{'code': 'GENERAL', 'text': 'auth error'}],
                'message': 'auth error',
                'code': 'GENERAL',
            },
            None,
        ),
        (
            [
                {
                    'status': 400,
                    'data': {'text': 'error parsing json'},
                    'headers': {},
                },
            ],
            400,
            {
                'errors': [{'code': 'GENERAL', 'text': 'error parsing json'}],
                'message': 'error parsing json',
                'code': 'GENERAL',
            },
            None,
        ),
        (
            [{'status': 400, 'data': {}, 'headers': {}}],
            400,
            {
                'errors': [
                    {'code': 'GENERAL', 'text': 'Невозможно создать заказ'},
                ],
                'message': 'Невозможно создать заказ',
                'code': 'GENERAL',
            },
            None,
        ),
        (
            [
                {
                    'status': 406,
                    'data': {'code': 'PRICE_CHANGED'},
                    'headers': {},
                },
            ],
            406,
            {
                'errors': [
                    {
                        'code': 'PRICE_CHANGED',
                        'text': 'Cannot commit order. Price has been changed',
                    },
                ],
                'message': 'Cannot commit order. Price has been changed',
                'code': 'PRICE_CHANGED',
            },
            None,
        ),
        (
            [{'status': 429, 'data': {}, 'headers': {}}],
            429,
            {
                'errors': [
                    {
                        'code': 'TOO_MANY_CONCURRENT_ORDERS',
                        'text': (
                            'На данный номер телефона уже сделано '
                            '15 заказов. Лимит превышен'
                        ),
                    },
                ],
                'message': (
                    'На данный номер телефона уже сделано 15 заказов. '
                    'Лимит превышен'
                ),
                'code': 'TOO_MANY_CONCURRENT_ORDERS',
            },
            None,
        ),
    ],
)
async def test_create_order_processing(
        db,
        patch,
        caplog,
        client,
        prefix,
        passport_mock,
        commit_responses_data,
        expected_status,
        expected_result,
        expected_db,
):
    order_commit_responses = (
        integration_api.APIResponse(**d) for d in commit_responses_data
    )

    @patch('taxi.clients.integration_api.IntegrationAPIClient.order_commit')
    async def _order_commit(*args, **kwargs):
        return next(order_commit_responses)

    @patch('taxi.clients.integration_api.IntegrationAPIClient.order_search')
    async def _order_search(*args, **kwargs):
        return integration_api.APIResponse(
            status=200,
            data={
                'orders': [
                    {
                        'created': '2016-06-15T09:00:26.000Z',
                        'request': {
                            'class': 'econom',
                            'route': [
                                {
                                    'city': 'Москва',
                                    'fullname': (
                                        'Россия, Москва, '
                                        'улица Льва Толстого, 16'
                                    ),
                                    'geopoint': [37.588144, 55.733842],
                                },
                            ],
                        },
                    },
                ],
            },
            headers={},
        )

    order_id = commit_responses_data[-1]['data'].get('orderid', 'order_id_1')
    response = await client.post(f'{prefix}/order/{order_id}/processing')

    assert response.status == expected_status
    assert await response.json() == expected_result

    if expected_db is not None:
        db_item = await db.corp_orders.find_one({'_id': order_id})
        assert expected_db == db_item
        if order_id == 'order_id_202':
            assert (
                f'Got 202 response from orders_commit - '
                f'waiting 0 seconds, order_id {order_id}'
                in [record.message for record in caplog.records]
            )


@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
@pytest.mark.parametrize(
    [
        'order_id',
        'order_search',
        'cancel_status',
        'expected_status',
        'expected_result',
    ],
    [
        (
            'order_id_1',
            {
                'cancel_disabled': False,
                'userid': 'user_id_1',
                'cancel_rules': {'state': 'free'},
            },
            200,
            200,
            {},
        ),
        (
            'order_id_1',
            {
                'cancel_disabled': False,
                'userid': 'user_id_1',
                'cancel_rules': {'state': 'free', 'message': 'message'},
            },
            409,
            406,
            {
                'errors': [
                    {
                        'code': 'TOO_CLOSE_TO_CANCEL',
                        'text': 'Too close to cancel',
                    },
                ],
                'message': 'Too close to cancel',
                'code': 'TOO_CLOSE_TO_CANCEL',
            },
        ),
        (
            'order_id_1',
            {
                'cancel_disabled': True,
                'userid': 'user_id_1',
                'cancel_rules': {'state': 'free'},
            },
            200,
            406,
            {
                'errors': [
                    {
                        'code': 'TOO_CLOSE_TO_CANCEL',
                        'text': 'Too close to cancel',
                    },
                ],
                'message': 'Too close to cancel',
                'code': 'TOO_CLOSE_TO_CANCEL',
            },
        ),
        (
            'order_id_not_found',
            {},
            200,
            404,
            {
                'errors': [{'code': 'GENERAL', 'text': 'Order not found'}],
                'message': 'Order not found',
                'code': 'GENERAL',
            },
        ),
    ],
)
@pytest.mark.translations(
    corp={'error.too_close_to_cancel': {'ru': 'Too close to cancel'}},
)
async def test_delete(
        taxi_corp_real_auth_client,
        patch,
        passport_mock,
        order_id,
        order_search,
        cancel_status,
        expected_status,
        expected_result,
):
    @patch('taxi.clients.integration_api.IntegrationAPIClient.order_cancel')
    async def _order_cancel(*args, **kwargs):
        return integration_api.APIResponse(
            status=cancel_status,
            data={'cancel_rules': {'message': 'message'}},
            headers={},
        )

    @patch('taxi.clients.integration_api.IntegrationAPIClient.order_search')
    async def _order_search(*args, **kwargs):
        return integration_api.APIResponse(
            status=200, data={'orders': [order_search]}, headers={},
        )

    response = await taxi_corp_real_auth_client.delete(
        '/1.0/client/{}/order/{}/processing'.format(passport_mock, order_id),
    )

    assert response.status == expected_status
    assert await response.json() == expected_result
