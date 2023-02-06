# pylint: disable=too-many-lines
import copy
import datetime

import pytest

from testsuite.utils import matching


@pytest.fixture(name='mock_c2c_save', autouse=True)
def _mock_c2c(mockserver, get_default_order_id):
    @mockserver.json_handler('/cargo-c2c/v1/clients-orders')
    def _get_orders(request):
        assert request.json['order_id'] == get_default_order_id()
        if (
                context.empty_orders_on_first_call
                and _get_orders.times_called == 0
        ):
            return mockserver.make_response(
                json={
                    'orders': [
                        {
                            'id': {
                                'order_id': get_default_order_id(),
                                'order_provider_id': 'cargo-c2c',
                                'phone_pd_id': '+71111111113_id',
                            },
                            'roles': ['initiator'],
                            'sharing_key': 'sharing_key_3',
                            'sharing_url': 'http://host/sharing_key_3',
                        },
                    ],
                },
            )

        return mockserver.make_response(
            json={
                'orders': [
                    {
                        'id': {
                            'order_id': get_default_order_id(),
                            'order_provider_id': 'cargo-c2c',
                            'phone_pd_id': '+71111111111_id',
                        },
                        'roles': ['sender', 'recipient'],
                        'sharing_key': 'sharing_key_1',
                        'sharing_url': 'http://host/sharing_key_1',
                    },
                    {
                        'id': {
                            'order_id': get_default_order_id(),
                            'order_provider_id': 'cargo-c2c',
                            'phone_pd_id': '+71111111112_id',
                        },
                        'roles': ['recipient'],
                        'sharing_key': 'sharing_key_2',
                        'sharing_url': 'http://host/sharing_key_2',
                    },
                    {
                        'id': {
                            'order_id': get_default_order_id(),
                            'order_provider_id': 'cargo-c2c',
                            'phone_pd_id': '+71111111113_id',
                        },
                        'roles': ['initiator'],
                        'sharing_key': 'sharing_key_3',
                        'sharing_url': 'http://host/sharing_key_3',
                    },
                ],
            },
        )

    class Context:
        def __init__(self):
            self.empty_orders_on_first_call = False

    context = Context()
    return context


def append_country(kwargs):
    kwargs['country_id'] = 'rus'
    return kwargs


def append_country_and_sender(kwargs):
    kwargs['country_id'] = 'rus'
    kwargs['sender'] = 'go'
    return kwargs


def build_notify_stq_kwards(
        phone_pd_id,
        order_id,
        role,
        status,
        notification_id,
        key_title,
        key_body,
):
    return {
        'id': {
            'phone_pd_id': phone_pd_id,
            'order_id': order_id,
            'order_provider_id': 'cargo-c2c',
        },
        'notification_id': notification_id,
        'push_payload': {
            'logistics': {
                'type': 'delivery-state-changed',
                'delivery_id': f'cargo-c2c/{order_id}',
                'notification_group': f'cargo-c2c/{order_id}',
                'meta': {
                    'tariff_class': 'courier',
                    'order_provider_id': 'cargo-c2c',
                    'roles': [role],
                    'order_status': status,
                },
            },
        },
        'push_content': {
            'title': {
                'keyset': 'cargo',
                'key': f'{key_title}.title',
                'locale': 'ru',
            },
            'body': {
                'keyset': 'cargo',
                'key': f'{key_body}.body',
                'locale': 'ru',
            },
        },
        'log_extra': {'_link': matching.AnyString()},
        'country_id': 'rus',
        'role': role,
        'initiator_phone_pd_id': '+71111111113_id',
    }


@pytest.mark.parametrize(
    'status, description_key',
    [
        ('failed', 'delivery_failed'),
        ('cancelled', 'delivery_cancelled'),
        ('cancelled_with_payment', 'delivery_cancelled'),
        ('cancelled_by_taxi', 'delivery_cancelled_by_service'),
        ('cancelled_with_items_on_hands', 'delivery_cancelled_by_service'),
        ('performer_not_found', 'performer_not_found'),
        ('returning', 'delivery_returning'),
    ],
)
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_SMS_SENDER_BY_COUNTRY={'rus': 'go'},
    CARGO_C2C_SENDER_BY_BRAND={'yataxi': 'go'},
)
async def test_order_fails(
        stq_runner,
        order_processing_order_terminated,
        mock_claims_full,
        get_default_order_id,
        stq,
        status,
        description_key,
        taxi_cargo_c2c,
):
    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-c2c/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': status,
            'current_point_id': 661932,
        },
    )
    assert response.status_code == 200

    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '+71111111111_id',
                get_default_order_id(),
                'sender',
                status,
                'cargo_c2c_sender_' + description_key,
                'c2c.push.sender.' + 'delivery_failed',
                'c2c.push.sender.' + description_key,
            ),
        )
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '+71111111112_id',
                get_default_order_id(),
                'recipient',
                status,
                'cargo_c2c_recipient_' + description_key,
                'c2c.push.recipient.' + 'delivery_failed',
                'c2c.push.recipient.' + description_key,
            ),
        )
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_SMS_SENDER_BY_COUNTRY={'rus': 'go'},
    CARGO_C2C_SENDER_BY_BRAND={'yataxi': 'go'},
)
async def test_delivery_returned(
        stq_runner,
        order_processing_order_terminated,
        mock_claims_full,
        get_default_order_id,
        stq,
        taxi_cargo_c2c,
):
    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-c2c/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'returned_finish',
            'current_point_id': 661932,
        },
    )
    assert response.status_code == 200

    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '+71111111111_id',
                get_default_order_id(),
                'sender',
                'returned_finish',
                'cargo_c2c_sender_delivery_returned',
                'c2c.push.sender.delivery_failed',
                'c2c.push.sender.delivery_returned',
            ),
        )
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_SMS_SENDER_BY_COUNTRY={'rus': 'go'},
    CARGO_C2C_SENDER_BY_BRAND={'yataxi': 'go'},
)
async def test_mark_terminated(
        stq_runner,
        order_processing_order_terminated,
        build_ucommunications_body,
        stq,
        get_default_order_id,
        mock_claims_full,
        taxi_cargo_c2c,
):
    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-c2c/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'delivered_finish',
            'current_point_id': 661932,
            'resolution': 'success',
        },
    )
    assert response.status_code == 200

    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '+71111111111_id',
                get_default_order_id(),
                'sender',
                'delivered_finish',
                'cargo_c2c_sender_delivery_finished',
                'c2c.push.sender.delivery_finished',
                'c2c.push.sender.delivery_finished',
            ),
        )
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '+71111111112_id',
                get_default_order_id(),
                'recipient',
                'delivered_finish',
                'cargo_c2c_recipient_delivery_finished',
                'c2c.push.recipient.delivery_finished',
                'c2c.push.recipient.delivery_finished',
            ),
        )
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '+71111111113_id',
                get_default_order_id(),
                'initiator',
                'delivered_finish',
                'cargo_c2c_initiator_delivery_finished',
                'c2c.push.initiator.delivery_finished',
                'c2c.push.initiator.delivery_finished',
            ),
        )
    )
    assert order_processing_order_terminated.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': '+71111111111_id',
                'resolution': 'succeed',
            },
            'kind': 'order-terminated',
        },
    }
    assert order_processing_order_terminated.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': '+71111111112_id',
                'resolution': 'succeed',
            },
            'kind': 'order-terminated',
        },
    }
    assert order_processing_order_terminated.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': '+71111111113_id',
                'resolution': 'succeed',
            },
            'kind': 'order-terminated',
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_SMS_SENDER_BY_COUNTRY={'rus': 'go'},
    CARGO_C2C_SENDER_BY_BRAND={'yataxi': 'go'},
)
async def test_mark_terminated_recipients_orders_on_pickuped(
        stq_runner,
        stq,
        build_ucommunications_body,
        mock_claims_full,
        get_default_order_id,
        taxi_cargo_c2c,
):
    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-c2c/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'pickuped',
            'current_point_id': 661933,
        },
    )
    assert response.status_code == 200

    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '+71111111112_id',
                get_default_order_id(),
                'recipient',
                'pickuped',
                'cargo_c2c_recipient_delivery_finished',
                'c2c.push.recipient.delivery_finished',
                'c2c.push.recipient.delivery_finished',
            ),
        )
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '+71111111113_id',
                get_default_order_id(),
                'initiator',
                'pickuped',
                'cargo_c2c_initiator_performer_on_the_way_to_destination',
                'c2c.push.initiator.destination.performer_on_the_way',
                'c2c.push.initiator.destination.performer_on_the_way',
            ),
        )
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_SMS_SENDER_BY_COUNTRY={'rus': 'go'},
    CARGO_C2C_SENDER_BY_BRAND={'yataxi': 'go'},
    CARGO_C2C_NEW_DELIVERY_SMS_SETTINGS=[
        {
            'settings': {
                'role': 'recipient',
                'tariff_class': 'courier',
                'door_to_door': False,
            },
            'tanker_key': 'courier.sms.to_reciever',
            'keyset': 'notify',
        },
        {
            'settings': {
                'role': 'sender',
                'tariff_class': 'courier',
                'door_to_door': False,
            },
            'tanker_key': 'courier.sms.to_sender',
            'keyset': 'notify',
        },
    ],
)
async def test_performer_found(
        stq_runner,
        stq,
        save_client_order,
        mockserver,
        load_json,
        mock_claims_full,
        get_default_order_id,
        order_processing_order_create_requested,
        mock_c2c_save,
        taxi_cargo_c2c,
):
    mock_c2c_save.empty_orders_on_first_call = True

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-c2c/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'performer_found',
            'current_point_id': 661931,
        },
    )
    assert response.status_code == 200

    assert order_processing_order_create_requested.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': '+71111111111_id',
                'roles': ['sender', 'recipient'],
            },
            'kind': 'order-create-requested',
            'trait': 'is-create',
        },
    }
    assert order_processing_order_create_requested.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': '+71111111112_id',
                'roles': ['recipient'],
            },
            'kind': 'order-create-requested',
            'trait': 'is-create',
        },
    }

    assert save_client_order.next_call() == {
        'arg': {
            'orders': [
                {
                    'id': {
                        'order_id': get_default_order_id(),
                        'order_provider_id': 'cargo-c2c',
                        'phone_pd_id': '+71111111111_id',
                    },
                    'roles': ['sender', 'recipient'],
                },
                {
                    'id': {
                        'order_id': get_default_order_id(),
                        'order_provider_id': 'cargo-c2c',
                        'phone_pd_id': '+71111111112_id',
                    },
                    'roles': ['recipient'],
                },
            ],
        },
    }

    expected_notify_kwargs = build_notify_stq_kwards(
        '+71111111111_id',
        get_default_order_id(),
        'sender',
        'performer_found',
        'cargo_c2c_sender_new_order',
        'c2c.push.sender.new_order',
        'c2c.push.sender.new_order',
    )
    expected_notify_kwargs['sms_content'] = {
        'text': {
            'args': {
                'sharing_url': 'http://host/some_sharing_key',
                'recipient_address': 'Красный строитель',
                'recipient_name': 'string',
            },
            'key': 'courier.sms.to_sender',
            'keyset': 'notify',
            'locale': 'ru',
        },
    }
    assert stq['cargo_c2c_send_notification'].next_call()[
        'kwargs'
    ] == append_country_and_sender(expected_notify_kwargs)

    expected_notify_kwargs = build_notify_stq_kwards(
        '+71111111112_id',
        get_default_order_id(),
        'recipient',
        'performer_found',
        'cargo_c2c_recipient_new_order',
        'c2c.push.recipient.new_order',
        'c2c.push.recipient.new_order',
    )
    expected_notify_kwargs['sms_content'] = {
        'text': {
            'args': {
                'sharing_url': 'http://host/some_sharing_key',
                'recipient_address': 'Ураина',
                'recipient_name': 'string',
            },
            'key': 'courier.sms.to_reciever',
            'keyset': 'notify',
            'locale': 'ru',
        },
    }
    assert stq['cargo_c2c_send_notification'].next_call()[
        'kwargs'
    ] == append_country_and_sender(expected_notify_kwargs)

    expected_notify_kwargs = build_notify_stq_kwards(
        '+71111111113_id',
        get_default_order_id(),
        'initiator',
        'performer_found',
        'cargo_c2c_initiator_performer_on_the_way_to_source',
        'c2c.push.initiator.source.performer_on_the_way',
        'c2c.push.initiator.source.performer_on_the_way',
    )
    assert stq['cargo_c2c_send_notification'].next_call()[
        'kwargs'
    ] == append_country_and_sender(expected_notify_kwargs)


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_SMS_SENDER_BY_COUNTRY={'rus': 'go'},
    CARGO_C2C_SENDER_BY_BRAND={'yataxi': 'go'},
)
async def test_courier_on_the_way_recipient(
        stq_runner,
        stq,
        build_ucommunications_body,
        mock_claims_full,
        get_default_order_id,
        mockserver,
        load_json,
        taxi_cargo_c2c,
):
    mock_claims_full.current_point = {
        'claim_point_id': 661932,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-c2c/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'pickuped',
            'current_point_id': 661932,
        },
    )
    assert response.status_code == 200

    assert stq['cargo_c2c_send_notification'].times_called == 2
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '+71111111112_id',
                get_default_order_id(),
                'recipient',
                'pickuped',
                'cargo_c2c_recipient_performer_on_the_way_to_destination',
                'c2c.push.recipient.destination.performer_on_the_way',
                'c2c.push.recipient.destination.performer_on_the_way',
            ),
        )
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '+71111111113_id',
                get_default_order_id(),
                'initiator',
                'pickuped',
                'cargo_c2c_initiator_performer_on_the_way_to_destination',
                'c2c.push.initiator.destination.performer_on_the_way',
                'c2c.push.initiator.destination.performer_on_the_way',
            ),
        )
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_SMS_SENDER_BY_COUNTRY={'rus': 'go'},
    CARGO_C2C_SENDER_BY_BRAND={'yataxi': 'go'},
)
async def test_pickuped_status_from_processing(
        stq_runner,
        stq,
        build_ucommunications_body,
        mock_claims_full,
        get_default_order_id,
        mockserver,
        load_json,
        taxi_cargo_c2c,
):
    mock_claims_full.current_point = {
        'claim_point_id': 661933,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-c2c/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'pickuped',
            'current_point_id': 661932,
            'called_from': 'processing',
        },
    )
    assert response.status_code == 200

    assert stq['cargo_c2c_send_notification'].times_called == 2
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '+71111111112_id',
                get_default_order_id(),
                'recipient',
                'pickuped',
                'cargo_c2c_recipient_performer_on_the_way_to_destination',
                'c2c.push.recipient.destination.performer_on_the_way',
                'c2c.push.recipient.destination.performer_on_the_way',
            ),
        )
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '+71111111113_id',
                get_default_order_id(),
                'initiator',
                'pickuped',
                'cargo_c2c_initiator_performer_on_the_way_to_destination',
                'c2c.push.initiator.destination.performer_on_the_way',
                'c2c.push.initiator.destination.performer_on_the_way',
            ),
        )
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_SMS_SENDER_BY_COUNTRY={'rus': 'go'},
    CARGO_C2C_SENDER_BY_BRAND={'yataxi': 'go'},
)
async def test_pickup_arrived(
        stq_runner,
        stq,
        build_ucommunications_body,
        get_default_order_id,
        build_notify_stq_kwargs,
        mockserver,
        load_json,
        taxi_cargo_c2c,
):
    current_point_id = 1

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        resp = load_json('claim_full_response_waiting.json')
        for point in resp['route_points']:
            if point['id'] == current_point_id:
                point['visit_status'] = 'arrived'
                break
            point['visit_status'] = 'visited'

        resp['on_the_way_state'] = {
            'current_point': {
                'claim_point_id': current_point_id,
                'last_status_change_ts': '2020-06-17T22:39:50+0300',
                'visit_status': 'arrived',
            },
        }

        return mockserver.make_response(json=resp)

    @mockserver.json_handler('/cargo-claims/v2/claims/points-eta')
    def _claims_points_eta(request):
        full = load_json('claim_full_response.json')
        points_eta = {
            'id': full['id'],
            'route_points': [],
            'performer_position': [52.569089, 39.60258],
        }

        stop_visit = False
        for point in full['route_points']:
            point.pop('contact', None)
            point.pop('skip_confirmation', None)
            if point['id'] == current_point_id:
                point['visit_status'] = 'arrived'
                stop_visit = True
            if not stop_visit:
                point['visit_status'] = 'visited'

            points_eta['route_points'].append(point)

        return mockserver.make_response(json=points_eta)

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-c2c/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'pickup_arrived',
            'current_point_id': current_point_id,
        },
    )
    assert response.status_code == 200

    source_waiting_args = {'free_waiting_time': '5', 'waiting_price': '5\xa0₽'}

    assert stq['cargo_c2c_send_notification'].times_called == 3
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwargs(
                '+71111111111_id',
                get_default_order_id(),
                'cargo-c2c',
                'sender',
                'pickup_arrived',
                'cargo_c2c_initiator_payer.source.'
                + 'paid_waiting.not_d2d.sender.id',
                'c2c.push.initiator_payer.source.paid_waiting.not_d2d.sender',
                'c2c.push.initiator_payer.source.paid_waiting.not_d2d.sender',
                5,
                source_waiting_args,
                source_waiting_args,
            ),
        )
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwargs(
                '+71111111112_id',
                get_default_order_id(),
                'cargo-c2c',
                'recipient',
                'pickup_arrived',
                (
                    'cargo_c2c_initiator_payer.source.paid_waiting.'
                    'not_d2d.recipient.id'
                ),
                (
                    'c2c.push.initiator_payer.source.paid_waiting.'
                    'not_d2d.recipient'
                ),
                (
                    'c2c.push.initiator_payer.source.paid_waiting.'
                    'not_d2d.recipient'
                ),
                5,
                source_waiting_args,
                source_waiting_args,
            ),
        )
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwargs(
                '+71111111113_id',
                get_default_order_id(),
                'cargo-c2c',
                'initiator',
                'pickup_arrived',
                (
                    'cargo_c2c_initiator_payer.source.paid_waiting.'
                    'not_d2d.initiator.id'
                ),
                (
                    'c2c.push.initiator_payer.source.paid_waiting.'
                    'not_d2d.initiator'
                ),
                (
                    'c2c.push.initiator_payer.source.paid_waiting.'
                    'not_d2d.initiator'
                ),
                5,
                source_waiting_args,
                source_waiting_args,
            ),
        )
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_SMS_SENDER_BY_COUNTRY={'rus': 'go'},
    CARGO_C2C_SENDER_BY_BRAND={'yataxi': 'go'},
)
async def test_delivery_arrived(
        stq_runner,
        stq,
        build_ucommunications_body,
        get_default_order_id,
        build_notify_stq_kwargs,
        mockserver,
        load_json,
        taxi_cargo_c2c,
):
    current_point_id = 2

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        resp = load_json('claim_full_response_waiting.json')
        for point in resp['route_points']:
            if point['id'] == current_point_id:
                point['visit_status'] = 'arrived'
                break
            point['visit_status'] = 'visited'

        resp['on_the_way_state'] = {
            'current_point': {
                'claim_point_id': current_point_id,
                'last_status_change_ts': '2020-06-17T22:39:50+0300',
                'visit_status': 'arrived',
            },
        }

        return mockserver.make_response(json=resp)

    @mockserver.json_handler('/cargo-claims/v2/claims/points-eta')
    def _claims_points_eta(request):
        full = load_json('claim_full_response.json')
        points_eta = {
            'id': full['id'],
            'route_points': [],
            'performer_position': [52.569089, 39.60258],
        }

        stop_visit = False
        for point in full['route_points']:
            point.pop('contact', None)
            point.pop('skip_confirmation', None)
            if point['id'] == current_point_id:
                point['visit_status'] = 'arrived'
                stop_visit = True
            if not stop_visit:
                point['visit_status'] = 'visited'

            points_eta['route_points'].append(point)

        return mockserver.make_response(json=points_eta)

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-c2c/process-event',
        json={
            'claim_id': '4b8d1af142664fde824626a7c19e2bd9',
            'status': 'delivery_arrived',
            'current_point_id': current_point_id,
        },
    )
    assert response.status_code == 200

    destination_waiting_args = {
        'free_waiting_time': '10',
        'waiting_price': '10\xa0₽',
    }

    assert stq['cargo_c2c_send_notification'].times_called == 3
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwargs(
                '+71111111111_id',
                get_default_order_id(),
                'cargo-c2c',
                'sender',
                'delivery_arrived',
                (
                    'cargo_c2c_initiator_payer.destination.paid_waiting.'
                    'not_d2d.sender.id'
                ),
                (
                    'c2c.push.initiator_payer.destination.paid_waiting.'
                    'not_d2d.sender'
                ),
                (
                    'c2c.push.initiator_payer.destination.paid_waiting.'
                    'not_d2d.sender'
                ),
                10,
                destination_waiting_args,
                destination_waiting_args,
            ),
        )
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwargs(
                '+71111111112_id',
                get_default_order_id(),
                'cargo-c2c',
                'recipient',
                'delivery_arrived',
                (
                    'cargo_c2c_initiator_payer.destination.paid_waiting.'
                    'not_d2d.recipient.id'
                ),
                (
                    'c2c.push.initiator_payer.destination.paid_waiting.'
                    'not_d2d.recipient'
                ),
                (
                    'c2c.push.initiator_payer.destination.paid_waiting.'
                    'not_d2d.recipient'
                ),
                10,
                destination_waiting_args,
                destination_waiting_args,
            ),
        )
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwargs(
                '+71111111113_id',
                get_default_order_id(),
                'cargo-c2c',
                'initiator',
                'delivery_arrived',
                (
                    'cargo_c2c_initiator_payer.destination.paid_waiting.'
                    'not_d2d.initiator.id'
                ),
                (
                    'c2c.push.initiator_payer.destination.paid_waiting.'
                    'not_d2d.initiator'
                ),
                (
                    'c2c.push.initiator_payer.destination.paid_waiting.'
                    'not_d2d.initiator'
                ),
                10,
                destination_waiting_args,
                destination_waiting_args,
            ),
        )
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_SMS_SENDER_BY_COUNTRY={'rus': 'go'},
    CARGO_C2C_SENDER_BY_BRAND={'yataxi': 'go'},
)
async def test_delivery_arrived_multipoint(
        stq_runner,
        stq,
        build_ucommunications_body,
        get_default_order_id,
        mockserver,
        build_notify_stq_kwargs,
        load_json,
        taxi_cargo_c2c,
):
    current_point_id = 3

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        resp = load_json('claim_full_response_waiting.json')
        for point in resp['route_points']:
            if point['id'] == current_point_id:
                point['visit_status'] = 'arrived'
                break
            point['visit_status'] = 'visited'

        resp['on_the_way_state'] = {
            'current_point': {
                'claim_point_id': current_point_id,
                'last_status_change_ts': '2020-06-17T22:39:50+0300',
                'visit_status': 'arrived',
            },
        }

        return mockserver.make_response(json=resp)

    @mockserver.json_handler('/cargo-claims/v2/claims/points-eta')
    def _claims_points_eta(request):
        full = load_json('claim_full_response.json')
        points_eta = {
            'id': full['id'],
            'route_points': [],
            'performer_position': [52.569089, 39.60258],
        }

        stop_visit = False
        for point in full['route_points']:
            point.pop('contact', None)
            point.pop('skip_confirmation', None)
            if point['id'] == current_point_id:
                point['visit_status'] = 'arrived'
                stop_visit = True
            if not stop_visit:
                point['visit_status'] = 'visited'

            points_eta['route_points'].append(point)

        return mockserver.make_response(json=points_eta)

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-c2c/process-event',
        json={
            'claim_id': '4b8d1af142664fde824626a7c19e2bd9',
            'status': 'delivery_arrived',
            'current_point_id': current_point_id,
        },
    )
    assert response.status_code == 200

    destination_waiting_args = {
        'free_waiting_time': '10',
        'waiting_price': '10\xa0₽',
    }

    assert stq['cargo_c2c_send_notification'].times_called == 3
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwargs(
                '+71111111111_id',
                get_default_order_id(),
                'cargo-c2c',
                'sender',
                'delivery_arrived',
                (
                    'cargo_c2c_initiator_payer.destination.paid_waiting.'
                    'not_d2d.sender.id'
                ),
                (
                    'c2c.push.initiator_payer.destination.paid_waiting.'
                    'not_d2d.sender'
                ),
                (
                    'c2c.push.initiator_payer.destination.paid_waiting.'
                    'not_d2d.sender'
                ),
                10,
                destination_waiting_args,
                destination_waiting_args,
            ),
        )
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwargs(
                '+71111111112_id',
                get_default_order_id(),
                'cargo-c2c',
                'recipient',
                'delivery_arrived',
                (
                    'cargo_c2c_initiator_payer.destination.paid_waiting.'
                    'not_d2d.recipient.id'
                ),
                (
                    'c2c.push.initiator_payer.destination.paid_waiting.'
                    'not_d2d.recipient'
                ),
                (
                    'c2c.push.initiator_payer.destination.paid_waiting.'
                    'not_d2d.recipient'
                ),
                10,
                destination_waiting_args,
                destination_waiting_args,
            ),
        )
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwargs(
                '+71111111113_id',
                get_default_order_id(),
                'cargo-c2c',
                'initiator',
                'delivery_arrived',
                (
                    'cargo_c2c_initiator_payer.destination.paid_waiting.'
                    'not_d2d.initiator.id'
                ),
                (
                    'c2c.push.initiator_payer.destination.paid_waiting.'
                    'not_d2d.initiator'
                ),
                (
                    'c2c.push.initiator_payer.destination.paid_waiting.'
                    'not_d2d.initiator'
                ),
                10,
                destination_waiting_args,
                destination_waiting_args,
            ),
        )
    )


@pytest.mark.now('2022-01-16T17:34:02+0000')
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_SMS_SENDER_BY_COUNTRY={'rus': 'go'},
    CARGO_C2C_SENDER_BY_BRAND={'yataxi': 'go'},
)
async def test_cargo_c2c_paid_waiting_processing_eta(
        stq_runner, stq, mockserver, load_json, mocked_time, taxi_cargo_c2c,
):
    current_point_id = 1

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        resp = load_json('claim_full_response_waiting.json')
        for point in resp['route_points']:
            if point['id'] == current_point_id:
                point['visit_status'] = 'arrived'
                break
            point['visit_status'] = 'visited'

        resp['on_the_way_state'] = {
            'current_point': {
                'claim_point_id': current_point_id,
                'last_status_change_ts': '2022-01-16T17:34:00+0000',
                'visit_status': 'arrived',
            },
        }

        return mockserver.make_response(json=resp)

    @mockserver.json_handler('/cargo-claims/v2/claims/points-eta')
    def _claims_points_eta(request):
        full = load_json('claim_full_response.json')
        points_eta = {
            'id': full['id'],
            'route_points': [],
            'performer_position': [52.569089, 39.60258],
        }

        stop_visit = False
        for point in full['route_points']:
            point.pop('contact', None)
            point.pop('skip_confirmation', None)
            if point['id'] == current_point_id:
                point['visit_status'] = 'arrived'
                stop_visit = True
            if not stop_visit:
                point['visit_status'] = 'visited'

            points_eta['route_points'].append(point)

        return mockserver.make_response(json=points_eta)

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-c2c/process-event',
        json={
            'claim_id': '4b8d1af142664fde824626a7c19e2bd9',
            'status': 'pickup_arrived',
            'current_point_id': current_point_id,
        },
    )
    assert response.status_code == 200

    already_waited = mocked_time.now() - datetime.datetime.strptime(
        '2022-01-16T17:34:00+0000', '%Y-%m-%dT%H:%M:%S+%f',
    )
    eta = mocked_time.now() + datetime.timedelta(minutes=5) - already_waited

    assert stq['cargo_c2c_paid_waiting_processing'].next_call()['eta'] == eta


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_SMS_SENDER_BY_COUNTRY={'rus': 'go'},
    CARGO_C2C_SENDER_BY_BRAND={'yataxi': 'go'},
)
async def test_cargo_c2c_paid_waiting_processing(
        stq,
        stq_runner,
        get_default_order_id,
        mockserver,
        load_json,
        build_notify_stq_kwargs,
):
    current_point_id = 1

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        resp = load_json('claim_full_response_waiting.json')
        for point in resp['route_points']:
            if point['id'] == current_point_id:
                point['visit_status'] = 'arrived'
                break
            point['visit_status'] = 'visited'
        resp['status'] = 'pickup_arrived'

        resp['on_the_way_state'] = {
            'current_point': {
                'claim_point_id': current_point_id,
                'last_status_change_ts': '2022-01-16T17:34:00+0000',
                'visit_status': 'arrived',
            },
        }

        return mockserver.make_response(json=resp)

    @mockserver.json_handler('/cargo-claims/v2/claims/points-eta')
    def _claims_points_eta(request):
        full = load_json('claim_full_response.json')
        points_eta = {
            'id': full['id'],
            'route_points': [],
            'performer_position': [52.569089, 39.60258],
        }

        stop_visit = False
        for point in full['route_points']:
            point.pop('contact', None)
            point.pop('skip_confirmation', None)
            if point['id'] == current_point_id:
                point['visit_status'] = 'arrived'
                stop_visit = True
            if not stop_visit:
                point['visit_status'] = 'visited'

            points_eta['route_points'].append(point)

        return mockserver.make_response(json=points_eta)

    await stq_runner.cargo_c2c_paid_waiting_processing.call(
        task_id='1',
        args=[
            '4b8d1af142664fde824626a7c19e2bd9',
            get_default_order_id(),
            '+71111111111_id',
            'cargo-c2c',
            'pickup_arrived',
            current_point_id,
        ],
    )

    source_waiting_args = {'free_waiting_time': '5', 'waiting_price': '5\xa0₽'}

    assert stq['cargo_c2c_send_notification'].times_called == 1
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == build_notify_stq_kwargs(
            '+71111111111_id',
            get_default_order_id(),
            'cargo-c2c',
            'sender',
            'pickup_arrived',
            (
                'cargo_c2c_initiator_payer.source.paid_waiting.'
                'not_d2d.sender.id'
            ),
            ('c2c.push.initiator_payer.source.paid_waiting.' 'not_d2d.sender'),
            ('c2c.push.initiator_payer.source.paid_waiting.' 'not_d2d.sender'),
            5,
            source_waiting_args,
            source_waiting_args,
        )
    )


@pytest.mark.experiments3(filename='experiment.json')
async def test_waiting_push(
        stq,
        stq_runner,
        get_default_order_id,
        create_cargo_c2c_orders,
        mock_claims_full,
        mockserver,
        load_json,
        default_calc_response_v2,
        build_notify_stq_kwargs,
):
    current_point_id = 1

    waiting_part = {
        'total_waiting': '400',
        'paid_waiting': '100',
        'was_limited': False,
        'paid_waiting_disabled': True,
    }

    @mockserver.json_handler('/cargo-pricing/v2/taxi/calc/retrieve')
    def _retrieve(request):
        resp = copy.deepcopy(default_calc_response_v2)
        resp['calculations'][0]['result']['details']['waypoints'][0][
            'waiting'
        ] = waiting_part
        resp['calculations'][0]['result']['details']['waypoints'][1][
            'waiting'
        ] = waiting_part
        return resp

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        resp = load_json('claim_full_response_waiting.json')
        for point in resp['route_points']:
            if point['id'] == current_point_id:
                point['visit_status'] = 'arrived'
                break
            point['visit_status'] = 'visited'
        resp['status'] = 'pickup_arrived'

        resp['on_the_way_state'] = {
            'current_point': {
                'claim_point_id': current_point_id,
                'last_status_change_ts': '2022-01-16T17:34:00+0000',
                'visit_status': 'arrived',
            },
        }

        return mockserver.make_response(json=resp)

    @mockserver.json_handler('/cargo-claims/v2/claims/points-eta')
    def _claims_points_eta(request):
        full = load_json('claim_full_response.json')
        points_eta = {
            'id': full['id'],
            'route_points': [],
            'performer_position': [52.569089, 39.60258],
        }

        stop_visit = False
        for point in full['route_points']:
            point.pop('contact', None)
            point.pop('skip_confirmation', None)
            if point['id'] == current_point_id:
                point['visit_status'] = 'arrived'
                stop_visit = True
            if not stop_visit:
                point['visit_status'] = 'visited'

            points_eta['route_points'].append(point)

        return mockserver.make_response(json=points_eta)

    await stq_runner.cargo_c2c_paid_waiting_processing.call(
        task_id='1',
        args=[
            '4b8d1af142664fde824626a7c19e2bd9',
            get_default_order_id(),
            '+71111111111_id',
            'cargo-c2c',
            'pickup_arrived',
            current_point_id,
        ],
    )

    assert stq['cargo_c2c_send_notification'].times_called == 1

    expected_notify_stq_kwargs = build_notify_stq_kwargs(
        '+71111111111_id',
        get_default_order_id(),
        'cargo-c2c',
        'sender',
        'pickup_arrived',
        'cargo_c2c_initiator_payer.source.waiting.not_d2d.sender.id',
        'c2c.push.initiator_payer.source.waiting.not_d2d.sender',
        'c2c.push.initiator_payer.source.waiting.not_d2d.sender',
        None,
        {},
        {},
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == expected_notify_stq_kwargs
    )


@pytest.mark.experiments3(filename='experiment.json')
async def test_processing_fail_if_no_claim(stq, taxi_cargo_c2c, mockserver):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        return mockserver.make_response(
            json={'code': 'claim_not_ready', 'message': 'some message'},
            status=404,
        )

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-c2c/process-event',
        json={
            'claim_id': '4b8d1af142664fde824626a7c19e2bd9',
            'status': 'pickup_arrived',
            'current_point_id': 1,
        },
    )

    assert stq['cargo_c2c_send_notification'].times_called == 0
    assert response.status_code == 500
