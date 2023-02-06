# flake8: noqa
# pylint: disable=import-error,wildcard-import
import datetime
import json
import psycopg2
import pytest

CREATED = 'created'
PAYED = 'payed'
CONFIRMED = 'confirmed'
TAKEN = 'taken'
FINISHED = 'finished'
CANCELLED = 'cancelled'
PROMISE_CHANGED = 'promise_changed'

LOGBROKER_CONSUMER_SETTINGS = {
    'order_client_events_consumer': {
        'enabled': True,
        'chunk_size': 2,
        'queue_timeout_ms': 50,
        'config_poll_period_ms': 1000,
    },
}


def _get_payload(
        order_nr, order_event, delivery_type='marketplace', place_id='123123',
):
    payload = {'order_nr': order_nr, 'order_event': order_event}

    payload['created_at'] = '2020-09-04T15:26:43+00:00'
    payload['order_type'] = 'order_type'
    payload['delivery_type'] = delivery_type
    payload['shipping_type'] = 'shipping_type'
    payload['eater_id'] = place_id
    payload['eater_personal_phone_id'] = place_id
    payload['eater_passport_uid'] = place_id
    payload['promised_at'] = '2020-09-04T16:26:43+00:00'
    payload['application'] = 'web'
    payload['place_id'] = place_id
    payload['payment_method'] = 'payment-method'
    if order_event == CREATED:
        return payload

    payload['payed_at'] = '2020-09-04T15:26:48+00:00'
    if order_event == PAYED:
        return payload

    payload['payed_at'] = '2020-09-04T15:26:51+00:00'
    if order_event == CONFIRMED:
        return payload

    payload['taken_at'] = '2020-09-04T15:56:51+00:00'
    if order_event == TAKEN:
        return payload

    payload['finished_at'] = '2020-09-04T15:59:51+00:00'
    if order_event == FINISHED:
        return payload

    payload['cancelled_at'] = '2020-09-04T16:59:51+00:00'
    payload['cancellation_reason'] = 'client_no_show'
    payload['cancelled_by'] = 'operator'
    if order_event == CANCELLED:
        return payload

    payload['promised_at'] = '2020-09-04T17:59:51+00:00'
    if order_event == PROMISE_CHANGED:
        return payload

    raise Exception('unknown order_event {}'.format(order_event))


async def _push_lb_order(taxi_eats_restapp_communications, lb_order):
    message = str(json.dumps(lb_order))
    response = await taxi_eats_restapp_communications.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-client-events-consumer',
                'data': message,
                'topic': '/eda/processing/testing/order-client-events',
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200


@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'lb_orders,cost',
    [
        pytest.param(
            [
                _get_payload('111111-100000', CREATED),
                _get_payload('111111-100001', FINISHED),
                _get_payload('111111-100000', CANCELLED),
                _get_payload('111111-100001', FINISHED),
                _get_payload('111111-100010', FINISHED),
                _get_payload('111111-100010', FINISHED),
            ],
            '2229.50₽',
            id='multiple orders in lb',
        ),
        pytest.param(
            [_get_payload('111111-100000', CANCELLED, 'marketplace')],
            '2229.50₽',
            id='marketplace order includes delivery cost',
        ),
        pytest.param(
            [_get_payload('111111-100000', CANCELLED, 'native')],
            '1770₽',
            id='native order excludes delivery cost',
        ),
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='eats_restapp_communications_cancelled_send',
    consumers=['eats_restapp_communications/cancelled_event'],
    clauses=[],
    default_value={'enabled': True},
)
async def test_order_save_db(
        taxi_eats_restapp_communications,
        lb_orders,
        cost,
        stq,
        mockserver,
        pgsql,
):
    @mockserver.json_handler(
        '/eats-place-subscriptions/internal/'
        'eats-place-subscriptions/v1/feature/enabled-for-places',
    )
    def _mock_subscriptions(request):
        req = request.json
        assert req['feature'] == 'boss_bot'
        assert sorted(req['place_ids']) == [123123]
        resp = {
            'feature': 'boss_bot',
            'places': {
                'with_enabled_feature': [123123],
                'with_disabled_feature': [],
            },
        }
        return mockserver.make_response(status=200, json=resp)

    @mockserver.json_handler(
        '/eats-order-revision/v1/revision/latest/customer-services',
    )
    async def _order_revision_mock(request):
        assert request.json == {'order_id': '111111-100000'}
        return mockserver.make_response(
            status=200,
            json={
                'origin_revision_id': '260975499',
                'created_at': '2022-04-21T17:09:24.723443+00:00',
                'customer_services': [
                    {
                        'details': {
                            'discriminator_type': (
                                'composition_products_details'
                            ),
                            'composition_products': [],
                        },
                        'discounts': [
                            {'discount_index': 0, 'discount_amount': '30.00'},
                        ],
                        'id': 'composition-products',
                        'name': 'Продукты заказа',
                        'cost_for_customer': '1770',
                        'currency': 'RUB',
                        'type': 'composition_products',
                        'trust_product_id': 'eda_107819207_ride',
                        'place_id': '71699',
                    },
                    {
                        'discounts': [],
                        'id': 'delivery-1',
                        'name': 'Доставка',
                        'cost_for_customer': '459.5',
                        'currency': 'RUB',
                        'type': 'delivery',
                        'vat': 'nds_none',
                        'trust_product_id': 'eda_107819207_ride',
                        'place_id': '71699',
                        'personal_tin_id': 'dcca712623af454f8f23428e7c3ce8fc',
                        'balance_client_id': '68465487',
                    },
                    {
                        'discounts': [],
                        'id': 'service_fee-1',
                        'name': 'Сервисный сбор',
                        'cost_for_customer': '9',
                        'currency': 'RUB',
                        'type': 'service_fee',
                        'vat': 'nds_20',
                        'trust_product_id': 'eda_107819207_ride',
                        'place_id': '71699',
                        'personal_tin_id': '84f06fa86b14459094568d88f9637f56',
                    },
                ],
            },
        )

    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_restapp_communications, lb_order)

    # wait for lb messages to be read
    await taxi_eats_restapp_communications.run_task(
        'order-client-events-consumer-lb_consumer',
    )
    assert stq.eats_restapp_communications_event_sender.times_called == 1
    event = 'cancelled-tg-alert'
    place_ids = [123123]
    arg = stq.eats_restapp_communications_event_sender.next_call()
    assert arg['queue'] == 'eats_restapp_communications_event_sender'
    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        """
        SELECT event_type, event_mode, recipients, data
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        (arg['id'],),
    )
    res = cursor.fetchall()
    assert len(res) == 1
    assert res[0][0] == event
    assert res[0][1] == 'asap'
    assert res[0][2]['recipients'] == {'place_ids': place_ids}
    assert res[0][3] == {
        'cancelled_at': '2020-09-04T16:59:51+00:00',
        'order_nr': '111111-100000',
        'place_id': '123123',
        'reason': 'Невозможно связаться с клиентом',
        'cost': '{}'.format(cost),
    }


@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'enabled_places,disabled_places,stq_calls,data',
    [
        pytest.param(
            [1, 2],
            [],
            2,
            {
                1: {
                    'cancelled_at': '2020-09-04T16:59:51+00:00',
                    'order_nr': '111111-100000',
                    'place_id': '1',
                    'reason': 'Невозможно связаться с клиентом',
                    'cost': '246₽',
                },
                2: {
                    'cancelled_at': '2020-09-04T16:59:51+00:00',
                    'order_nr': '111111-100001',
                    'place_id': '2',
                    'reason': 'Невозможно связаться с клиентом',
                    'cost': '246₽',
                },
            },
            id='all places enabled',
        ),
        pytest.param(
            [1],
            [2],
            1,
            {
                1: {
                    'cancelled_at': '2020-09-04T16:59:51+00:00',
                    'order_nr': '111111-100000',
                    'place_id': '1',
                    'reason': 'Невозможно связаться с клиентом',
                    'cost': '246₽',
                },
            },
            id='some places disabled',
        ),
        pytest.param([], [1, 2], 0, None, id='all places disabled'),
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='eats_restapp_communications_cancelled_send',
    consumers=['eats_restapp_communications/cancelled_event'],
    clauses=[],
    default_value={'enabled': True},
)
async def test_order_check_place_enabled(
        taxi_eats_restapp_communications,
        enabled_places,
        disabled_places,
        stq_calls,
        data,
        stq,
        mockserver,
        pgsql,
):
    @mockserver.json_handler(
        '/eats-place-subscriptions/internal/'
        'eats-place-subscriptions/v1/feature/enabled-for-places',
    )
    def _mock_subscriptions(request):
        req = request.json
        assert req['feature'] == 'boss_bot'
        assert sorted(req['place_ids']) == [1, 2]
        resp = {
            'feature': 'boss_bot',
            'places': {
                'with_enabled_feature': enabled_places,
                'with_disabled_feature': disabled_places,
            },
        }
        return mockserver.make_response(status=200, json=resp)

    @mockserver.json_handler(
        '/eats-order-revision/v1/revision/latest/customer-services',
    )
    async def _order_revision_mock(request):
        return mockserver.make_response(
            status=200,
            json={
                'origin_revision_id': '260975499',
                'created_at': '2022-04-21T17:09:24.723443+00:00',
                'customer_services': [
                    {
                        'details': {
                            'discriminator_type': (
                                'composition_products_details'
                            ),
                            'composition_products': [],
                        },
                        'discounts': [
                            {'discount_index': 0, 'discount_amount': '30.00'},
                        ],
                        'id': 'composition-products',
                        'name': 'Продукты заказа',
                        'cost_for_customer': '123',
                        'currency': 'RUB',
                        'type': 'composition_products',
                        'trust_product_id': 'eda_107819207_ride',
                        'place_id': '71699',
                    },
                    {
                        'discounts': [],
                        'id': 'delivery-1',
                        'name': 'Доставка',
                        'cost_for_customer': '123',
                        'currency': 'RUB',
                        'type': 'delivery',
                        'vat': 'nds_none',
                        'trust_product_id': 'eda_107819207_ride',
                        'place_id': '71699',
                        'personal_tin_id': 'dcca712623af454f8f23428e7c3ce8fc',
                        'balance_client_id': '68465487',
                    },
                    {
                        'discounts': [],
                        'id': 'service_fee-1',
                        'name': 'Сервисный сбор',
                        'cost_for_customer': '123',
                        'currency': 'RUB',
                        'type': 'service_fee',
                        'vat': 'nds_20',
                        'trust_product_id': 'eda_107819207_ride',
                        'place_id': '71699',
                        'personal_tin_id': '84f06fa86b14459094568d88f9637f56',
                    },
                ],
            },
        )

    lb_orders = [
        _get_payload('111111-100000', CREATED, place_id='1'),
        _get_payload('111111-100001', CREATED, place_id='2'),
        _get_payload('111111-100000', CANCELLED, place_id='1'),
        _get_payload('111111-100001', CANCELLED, place_id='2'),
    ]
    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_restapp_communications, lb_order)

    # wait for lb messages to be read
    await taxi_eats_restapp_communications.run_task(
        'order-client-events-consumer-lb_consumer',
    )
    assert _mock_subscriptions.times_called == 1
    assert (
        stq.eats_restapp_communications_event_sender.times_called == stq_calls
    )
    if stq_calls == 0:
        return
    event = 'cancelled-tg-alert'
    cursor = pgsql['eats_restapp_communications'].cursor()
    for place_id in enabled_places:
        place_ids = place_id
        arg = stq.eats_restapp_communications_event_sender.next_call()
        assert arg['queue'] == 'eats_restapp_communications_event_sender'
        cursor.execute(
            """
            SELECT event_type, event_mode, recipients, data
            FROM eats_restapp_communications.send_event_data
            WHERE event_id = %s
            """,
            (arg['id'],),
        )
        res = cursor.fetchall()
        assert len(res) == 1
        assert res[0][0] == event
        assert res[0][1] == 'asap'
        assert res[0][2]['recipients'] == {'place_ids': [place_ids]}
        assert res[0][3] == data[place_id]
