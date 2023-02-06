import json

import pytest


@pytest.mark.parametrize(
    'feedback_request, order_proc_response',
    [
        (
            {
                'type': 'order_feedback',
                'score': 3,
                'comment': 'comment',
                'reasons': [{'reason_id': 'a'}, {'reason_id': 'b'}],
            },
            {
                'order_provider_id': 'cargo-claims',
                'phone_pd_id': 'phone_pd_id_1',
                'type': 'order_feedback',
                'score': 3,
                'comment': 'comment',
                'reasons': [{'reason_id': 'a'}, {'reason_id': 'b'}],
                'tips': {'decimal_value': '0', 'type': 'flat'},
            },
        ),
        (
            {
                'type': 'cancel_feedback',
                'comment': 'cancel comment',
                'reasons': [{'reason_id': 'c'}, {'reason_id': 'd'}],
            },
            {
                'order_provider_id': 'cargo-claims',
                'phone_pd_id': 'phone_pd_id_1',
                'type': 'cancel_feedback',
                'comment': 'cancel comment',
                'reasons': [{'reason_id': 'c'}, {'reason_id': 'd'}],
            },
        ),
        (
            {
                'type': 'order_feedback',
                'tips': {
                    'decimal_value': '40.0',
                    'choice_id': 'some-random-id',
                },
            },
            {
                'order_provider_id': 'cargo-claims',
                'phone_pd_id': 'phone_pd_id_1',
                'type': 'order_feedback',
                'tips': {'decimal_value': '40.0', 'type': 'flat'},
            },
        ),
        (
            {
                'type': 'order_feedback',
                'tips': {
                    'type': 'flat',
                    'decimal_value': '40.0',
                    'choice_id': 'some-random-id',
                },
            },
            {
                'order_provider_id': 'cargo-claims',
                'phone_pd_id': 'phone_pd_id_1',
                'type': 'order_feedback',
                'tips': {'decimal_value': '40.0', 'type': 'flat'},
            },
        ),
        (
            {
                'type': 'order_feedback',
                'tips': {
                    'type': 'percent',
                    'decimal_value': '40.0',
                    'choice_id': 'some-random-id',
                },
            },
            {
                'order_provider_id': 'cargo-claims',
                'phone_pd_id': 'phone_pd_id_1',
                'type': 'order_feedback',
                'tips': {'decimal_value': '40.0', 'type': 'percent'},
            },
        ),
    ],
)
async def test_feedback_requested(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
        default_pa_headers,
        order_processing_feedback_requested,
        feedback_request,
        order_proc_response,
):
    headers = default_pa_headers('phone_pd_id_1').copy()
    headers['X-Idempotency-Token'] = '123'

    request_json = feedback_request
    request_json['delivery_id'] = 'cargo-claims/' + get_default_order_id()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/feedback',
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {'operation_id': '123'}

    order_proc_data = order_proc_response
    order_proc_data['order_id'] = get_default_order_id()
    assert order_processing_feedback_requested.next_call() == {
        'arg': {'data': order_proc_data, 'kind': 'feedback-requested'},
    }


async def test_events(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
        default_pa_headers,
        mockserver,
        create_taxi_orders,
        get_default_estimate_request,
        get_default_draft_request,
):
    @mockserver.json_handler('/processing/v1/delivery/order/events')
    def _events(request):
        return {
            'events': [
                {
                    'event_id': '1',
                    'created': '2020-02-25T06:00:00+03:00',
                    'payload': {
                        'kind': 'order-create-requested',
                        'trait': 'is-create',
                    },
                    'handled': True,
                },
                {
                    'event_id': '2',
                    'created': '2020-02-25T06:00:00+03:00',
                    'payload': {'kind': 'feedback-requested'},
                    'handled': True,
                },
                {
                    'event_id': '3',
                    'created': '2020-02-25T06:00:00+03:00',
                    'payload': {
                        'kind': 'order-create-failed',
                        'data': {
                            'code': '400',
                            'message': 'Не удалось создать заказ',
                        },
                    },
                    'handled': True,
                },
                {
                    'event_id': '4',
                    'created': '2020-02-25T06:00:00+03:00',
                    'payload': {'kind': 'feedback-succeeded'},
                    'handled': True,
                },
            ],
        }

    def _sort_events(events):
        return sorted(events, key=lambda k: k['delivery_id'])

    def _sort_cursor(cursor):
        return sorted(cursor, key=lambda k: k['order_id'])

    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=get_default_estimate_request(),
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    request = get_default_draft_request()
    request['offer_id'] = response.json()['estimations'][0]['offer_id']
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/draft',
        json=request,
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    cargo_c2c_order_id = response.json()['delivery_id'].split('/')[1]

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries/events',
        json={},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.headers['X-Refresh-After'] == '20'
    assert response.status_code == 200

    expected = [
        {
            'type': 'order-create-requested',
            'delivery_id': f'cargo-c2c/{cargo_c2c_order_id}',
        },
        {
            'type': 'order-create-failed',
            'failure_description': 'Не удалось создать заказ',
            'delivery_id': f'cargo-c2c/{cargo_c2c_order_id}',
        },
        {
            'type': 'order-create-requested',
            'delivery_id': f'cargo-claims/{get_default_order_id()}',
        },
        {
            'type': 'order-create-failed',
            'failure_description': 'Не удалось создать заказ',
            'delivery_id': f'cargo-claims/{get_default_order_id()}',
        },
        {
            'type': 'order-create-requested',
            'delivery_id': f'taxi/{get_default_order_id()}',
        },
        {
            'type': 'order-create-failed',
            'failure_description': 'Не удалось создать заказ',
            'delivery_id': f'taxi/{get_default_order_id()}',
        },
    ]
    assert _sort_events(response.json()['events']) == _sort_events(expected)
    cursor = response.json()['revision']
    assert _sort_cursor(json.loads(cursor)) == _sort_cursor(
        [
            {
                'order_id': cargo_c2c_order_id,
                'order_provider_id': 'cargo-c2c',
                'revision': 4,
                'queue': 'order',
            },
            {
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
                'revision': 4,
                'queue': 'order',
            },
            {
                'order_id': get_default_order_id(),
                'order_provider_id': 'taxi',
                'revision': 4,
                'queue': 'order',
            },
        ],
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries/events',
        json={'revision': cursor},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json()['events'] == []


async def test_free_cancel_unavalable(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
        default_pa_headers,
        mockserver,
):
    @mockserver.json_handler('/processing/v1/delivery/order/events')
    def _events(request):
        return {
            'events': [
                {
                    'event_id': '1',
                    'created': '2020-02-25T06:00:00+03:00',
                    'payload': {
                        'kind': 'order-cancel-failed',
                        'data': {
                            'code': 'free_cancel_is_unavailable',
                            'message': 'some message',
                            'cancel_type': 'free',
                            'request_id': '123',
                        },
                        'trait': 'is-create',
                    },
                    'handled': True,
                },
                {
                    'event_id': '1',
                    'created': '2020-02-25T06:00:00+03:00',
                    'payload': {
                        'kind': 'order-cancel-failed',
                        'data': {
                            'code': 'bad_request',
                            'message': 'some message',
                            'cancel_type': 'paid',
                            'request_id': '123',
                        },
                    },
                    'handled': True,
                },
            ],
        }

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries/events',
        json={},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json()['events'] == [
        {
            'delivery_id': 'cargo-claims/' + get_default_order_id(),
            'request_id': '123',
            'message': {
                'title': 'Платная отмена',
                'body': (
                    'Курьер уже ждет посылку, '
                    'поэтому бесплатная отмена недоступна'
                ),
                'close_button': {'title': 'Закрыть'},
                'confirm_button': {
                    'cancel_type': 'paid',
                    'title': 'Отменить платно',
                },
            },
            'type': 'order-cancel-failed',
        },
        {
            'delivery_id': 'cargo-claims/' + get_default_order_id(),
            'request_id': '123',
            'message': {
                'title': 'Не удалось отменить',
                'body': 'Что-то пошло не так',
                'close_button': {'title': 'Закрыть'},
            },
            'type': 'order-cancel-failed',
        },
    ]


async def test_empty_events(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
        default_pa_headers,
        mockserver,
        create_taxi_orders,
):
    @mockserver.json_handler('/processing/v1/delivery/order/events')
    def _events(request):
        return {
            'events': [
                {
                    'event_id': '1',
                    'created': '2020-02-25T06:00:00+03:00',
                    'payload': {'kind': 'order-cancel-failed'},
                    'handled': True,
                },
            ],
        }

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries/events',
        json={},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json()['events'] == []
