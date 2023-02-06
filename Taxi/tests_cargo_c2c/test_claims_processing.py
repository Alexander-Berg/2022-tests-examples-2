# pylint: disable=import-error, too-many-lines
import pytest

from testsuite.utils import matching

SETTINGS = {'enabled': True, 'period-ms': 5}


@pytest.fixture(name='mock_c2c_save', autouse=True)
def _mock_c2c(mockserver, load_json, get_default_order_id):
    @mockserver.json_handler('/cargo-c2c/v1/clients-orders')
    def _get_orders(request):
        if (
                context.empty_orders_on_first_call
                and _get_orders.times_called == 0
        ):
            return mockserver.make_response(json={'orders': []})

        return mockserver.make_response(
            json={
                'orders': [
                    {
                        'id': {
                            'order_id': get_default_order_id(),
                            'order_provider_id': 'cargo-claims',
                            'phone_pd_id': '+71111111111_id',
                        },
                        'roles': ['sender', 'recipient'],
                        'source': 'pickup_point',
                        'sharing_key': 'some_sharing_key',
                        'sharing_url': 'http://host/some_sharing_key',
                    },
                    {
                        'id': {
                            'order_id': get_default_order_id(),
                            'order_provider_id': 'cargo-claims',
                            'phone_pd_id': '+71111111112_id',
                        },
                        'roles': ['recipient'],
                        'source': 'pickup_point',
                        'sharing_key': 'some_sharing_key',
                        'sharing_url': 'http://host/some_sharing_key',
                    },
                ],
            },
        )

    class Context:
        def __init__(self):
            self.empty_orders_on_first_call = False

    context = Context()
    return context


@pytest.fixture(autouse=True)
def _mock_claims_cut_bulk(mockserver, load_json, get_default_order_id):
    @mockserver.json_handler('/cargo-claims/v1/claims/bulk-info/cut')
    def _cut_bulk(request):
        return {
            'claims': [
                {
                    'id': 'b1fe01ddc30247279f806e6c5e210a9f',
                    'status': 'new',
                    'version': 1,
                    'user_request_revision': '1',
                    'skip_client_notify': False,
                },
            ],
        }


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
            'order_provider_id': 'cargo-claims',
        },
        'notification_id': notification_id,
        'push_payload': {
            'logistics': {
                'type': 'delivery-state-changed',
                'delivery_id': f'cargo-claims/{order_id}',
                'notification_group': f'cargo-claims/{order_id}',
                'meta': {
                    'tariff_class': 'courier',
                    'order_provider_id': 'cargo-claims',
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
                'args': {
                    'corp_client_name': 'Рога и Копыта',
                    'corp_client_name_ru_genitive': 'Рогов и Копытов',
                },
            },
        },
        'sender': 'go',
        'log_extra': {'_link': matching.AnyString()},
        'role': role,
    }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_c2c_control_client_orders_creation',
    consumers=[
        'cargo-c2c/control_orders_creation',
        'cargo-c2c/claims_processing',
    ],
    clauses=[],
    default_value={'enabled': True, 'allowed_roles': ['recipient']},
    is_config=True,
)
@pytest.mark.config(
    CARGO_C2C_LOCALE_BY_CORP_CLIENT_ID={
        '5e36732e2bc54e088b1466e08e31c486': 'ru',
    },
)
@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
            'ru_genitive': 'Рогов и Копытов',
        },
    },
)
async def test_crate_client_orders_experiment(
        stq_runner,
        save_client_order,
        mock_claims_full,
        get_default_order_id,
        mock_c2c_save,
        taxi_cargo_c2c,
):
    mock_c2c_save.empty_orders_on_first_call = True

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-claims/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'performer_found',
            'current_point_id': 661932,
        },
    )
    assert response.status_code == 200

    assert save_client_order.next_call() == {
        'arg': {
            'orders': [
                {
                    'id': {
                        'order_id': get_default_order_id(),
                        'order_provider_id': 'cargo-claims',
                        'phone_pd_id': '+71111111111_id',
                    },
                    'roles': ['recipient'],
                },
                {
                    'id': {
                        'order_id': get_default_order_id(),
                        'order_provider_id': 'cargo-claims',
                        'phone_pd_id': '+71111111112_id',
                    },
                    'roles': ['recipient'],
                },
            ],
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_C2C_LOCALE_BY_CORP_CLIENT_ID={
        '5e36732e2bc54e088b1466e08e31c486': 'ru',
    },
)
@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
            'ru_genitive': 'Рогов и Копытов',
        },
    },
)
async def test_mark_terminated(
        stq_runner,
        order_processing_order_terminated,
        mock_claims_full,
        get_default_order_id,
        taxi_cargo_c2c,
):
    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-claims/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'delivered_finish',
            'current_point_id': 661932,
            'resolution': 'success',
        },
    )
    assert response.status_code == 200

    assert order_processing_order_terminated.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
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
                'order_provider_id': 'cargo-claims',
                'phone_pd_id': '+71111111112_id',
                'resolution': 'succeed',
            },
            'kind': 'order-terminated',
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_C2C_LOCALE_BY_CORP_CLIENT_ID={
        '5e36732e2bc54e088b1466e08e31c486': 'ru',
    },
)
@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
            'ru_genitive': 'Рогов и Копытов',
        },
    },
)
async def test_mark_terminated_recipients_orders_on_pickuped(
        stq_runner,
        get_default_order_id,
        stq,
        build_ucommunications_body,
        mock_claims_full,
        taxi_cargo_c2c,
):
    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-claims/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'pickuped',
            'current_point_id': 661933,
        },
    )
    assert response.status_code == 200

    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country(
            build_notify_stq_kwards(
                '+71111111112_id',
                get_default_order_id(),
                'recipient',
                'pickuped',
                'cargo_b2c_recipient_delivery_finished',
                'b2c.push.recipient.delivery_finished',
                'b2c.push.recipient.delivery_finished',
            ),
        )
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(CARGO_C2C_ENABLE_ADDRESS_LOCALIZE=True)
@pytest.mark.config(
    CARGO_C2C_LOCALE_BY_CORP_CLIENT_ID={
        '5e36732e2bc54e088b1466e08e31c486': 'ru',
    },
)
@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
            'ru_genitive': 'Рогов и Копытов',
        },
    },
)
async def test_performer_found(
        stq_runner,
        get_default_order_id,
        stq,
        order_processing_order_create_requested,
        mockserver,
        load_json,
        mock_claims_full,
        save_client_order,
        mock_c2c_save,
        taxi_cargo_c2c,
):
    mock_claims_full.current_point = {
        'claim_point_id': 661931,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    mock_c2c_save.empty_orders_on_first_call = True

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-claims/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'performer_found',
            'current_point_id': 661931,
        },
    )
    assert response.status_code == 200

    kwargs = append_country_and_sender(
        build_notify_stq_kwards(
            '+71111111111_id',
            get_default_order_id(),
            'sender',
            'performer_found',
            'delivery_default',
            'b2c.push.sender.new_order',
            'b2c.push.sender.new_order',
        ),
    )
    kwargs['sms_content'] = {
        'text': {
            'args': {
                'sharing_url': 'http://host/some_sharing_key',
                'recipient_address': 'Россия, Москва, Садовническая улица',
                'retailer_name': 'Рога и Копыта',
                'recipient_name': 'string',
            },
            'key': 'cargo_claims.sms.new_delivery',
            'keyset': 'cargo_notify',
            'locale': 'ru',
        },
    }
    assert stq['cargo_c2c_send_notification'].next_call()['kwargs'] == kwargs

    kwargs = append_country_and_sender(
        build_notify_stq_kwards(
            '+71111111112_id',
            get_default_order_id(),
            'recipient',
            'performer_found',
            'delivery_default',
            'b2c.push.recipient.new_order',
            'b2c.push.recipient.new_order',
        ),
    )
    kwargs['sms_content'] = {
        'text': {
            'args': {
                'sharing_url': 'http://host/some_sharing_key',
                'recipient_address': 'Россия, Москва, Садовническая улица',
                'retailer_name': 'Рога и Копыта',
                'recipient_name': 'string',
            },
            'key': 'cargo_claims.sms.new_delivery',
            'keyset': 'cargo_notify',
            'locale': 'ru',
        },
    }
    assert stq['cargo_c2c_send_notification'].next_call()['kwargs'] == kwargs


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(CARGO_C2C_ENABLE_ADDRESS_LOCALIZE=True)
@pytest.mark.config(
    CARGO_C2C_LOCALE_BY_CORP_CLIENT_ID={
        '5e36732e2bc54e088b1466e08e31c486': 'ru',
    },
)
@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
            'ru_genitive': 'Рогов и Копытов',
        },
    },
    CARGO_SMS_SENDER_BY_COUNTRY={'il': 'go'},
)
async def test_sms_israel(
        stq_runner,
        get_default_order_id,
        stq,
        order_processing_order_create_requested,
        mockserver,
        load_json,
        mock_claims_full,
        save_client_order,
        mock_c2c_save,
        taxi_cargo_c2c,
):
    mock_claims_full.current_point = {
        'claim_point_id': 661931,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _retireve(request):
        resp = load_json('claim_full_response.json')
        resp['route_points'][0]['address']['coordinates'] = [
            34.809198,
            32.086604,
        ]  # Israel
        return mockserver.make_response(json=resp)

    @mockserver.json_handler('/cargo-claims/v2/claims/points-eta')
    def _claims_points_eta(request):
        full = load_json('claim_full_response.json')
        points_eta = {
            'id': full['id'],
            'route_points': [],
            'performer_position': [52.569089, 39.60258],
        }

        for point in full['route_points']:
            point.pop('contact', None)
            point.pop('skip_confirmation', None)
            points_eta['route_points'].append(point)

        points_eta['route_points'][0]['address']['coordinates'] = [
            34.809198,
            32.086604,
        ]  # Israel

        return mockserver.make_response(json=points_eta)

    mock_c2c_save.empty_orders_on_first_call = True

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-claims/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'performer_found',
            'current_point_id': 661931,
        },
    )
    assert response.status_code == 200

    stq['cargo_c2c_send_notification'].next_call()
    result = append_country_and_sender(
        stq['cargo_c2c_send_notification'].next_call()['kwargs'],
    )
    assert result['sms_content']['text']['args'] == {
        'sharing_url': 'http://host-isr/some_sharing_key',
        'recipient_address': 'Россия, Москва, Садовническая улица',
        'retailer_name': 'Рога и Копыта',
        'recipient_name': 'string',
    }

    assert result['sender'] == 'go'


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(CARGO_C2C_ENABLE_ADDRESS_LOCALIZE=True)
@pytest.mark.config(
    CARGO_C2C_LOCALE_BY_CORP_CLIENT_ID={
        '5e36732e2bc54e088b1466e08e31c486': 'ru',
    },
)
@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
            'ru_genitive': 'Рогов и Копытов',
        },
    },
    CARGO_SMS_SENDER_BY_COUNTRY={'il': 'go'},
)
async def test_sdc_sharing_url(
        stq_runner,
        get_default_order_id,
        stq,
        order_processing_order_create_requested,
        mockserver,
        load_json,
        mock_claims_full,
        save_client_order,
        mock_c2c_save,
        taxi_cargo_c2c,
):
    mock_claims_full.current_point = {
        'claim_point_id': 661931,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _retireve(request):
        resp = load_json('claim_full_response.json')
        resp['cargo_order_id'] = 'd055a905-8f7f-0000-58cf-850200000022'
        resp['route_points'][0]['address']['coordinates'] = [
            34.809198,
            32.086604,
        ]  # Israel
        resp['performer_info'] = {
            'courier_name': 'Delivery Rover',
            'driver_id': 'driverid1',
            'legal_name': 'SDC Robot',
            'park_id': 'parkid1',
            'transport_type': 'rover',
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

        for point in full['route_points']:
            point.pop('contact', None)
            point.pop('skip_confirmation', None)
            points_eta['route_points'].append(point)

        points_eta['route_points'][0]['address']['coordinates'] = [
            34.809198,
            32.086604,
        ]  # Israel

        return mockserver.make_response(json=points_eta)

    mock_c2c_save.empty_orders_on_first_call = True

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-claims/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'performer_found',
            'current_point_id': 661931,
        },
    )
    assert response.status_code == 200

    stq['cargo_c2c_send_notification'].next_call()
    result = append_country_and_sender(
        stq['cargo_c2c_send_notification'].next_call()['kwargs'],
    )
    assert (
        result['sms_content']['text']['args']['sharing_url']
        == f'http://sdc-host/d055a905-8f7f-0000-58cf-850200000022'
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(ORDER_ROUTE_SHARING_SUPPORTED_CORPS={})
async def test_performer_found_without_corp_name(
        stq_runner,
        get_default_order_id,
        stq,
        order_processing_order_create_requested,
        mockserver,
        load_json,
        mock_claims_full,
        save_client_order,
        mock_c2c_save,
        taxi_cargo_c2c,
):
    mock_claims_full.current_point = {
        'claim_point_id': 661932,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    mock_c2c_save.empty_orders_on_first_call = True

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-claims/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'performer_found',
            'current_point_id': 661931,
        },
    )
    assert response.status_code == 200

    expected = append_country_and_sender(
        build_notify_stq_kwards(
            '+71111111111_id',
            get_default_order_id(),
            'sender',
            'performer_found',
            'delivery_default',
            'b2c.push.sender.new_order',
            'b2c.push.sender.without_corp_name.new_order',
        ),
    )
    expected['sms_content'] = {
        'text': {
            'args': {
                'sharing_url': 'http://host/some_sharing_key',
                'recipient_address': 'Красный строитель',
                'recipient_name': 'string',
            },
            'key': 'cargo_claims_send_on_the_way_sms_sharing_sender',
            'keyset': 'notify',
            'locale': 'ru',
        },
    }
    expected['push_content']['body'].pop('args')
    assert stq['cargo_c2c_send_notification'].next_call()['kwargs'] == expected

    expected = append_country_and_sender(
        build_notify_stq_kwards(
            '+71111111112_id',
            get_default_order_id(),
            'recipient',
            'performer_found',
            'delivery_default',
            'b2c.push.recipient.new_order',
            'b2c.push.recipient.without_corp_name.new_order',
        ),
    )
    expected['sms_content'] = {
        'text': {
            'args': {
                'sharing_url': 'http://host/some_sharing_key',
                'recipient_address': 'Ураина',
                'recipient_name': 'string',
            },
            'key': 'cargo_claims_send_on_the_way_sms_sharing_recipient',
            'keyset': 'notify',
            'locale': 'ru',
        },
    }
    expected['push_content']['body'].pop('args')
    assert stq['cargo_c2c_send_notification'].next_call()['kwargs'] == expected


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_C2C_LOCALE_BY_CORP_CLIENT_ID={
        '5e36732e2bc54e088b1466e08e31c486': 'ru',
    },
)
@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
            'ru_genitive': 'Рогов и Копытов',
        },
    },
)
async def test_courier_on_the_way_recipient(
        stq_runner,
        get_default_order_id,
        stq,
        build_ucommunications_body,
        mock_claims_full,
        taxi_cargo_c2c,
):
    mock_claims_full.current_point = {
        'claim_point_id': 661933,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-claims/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'pickuped',
            'current_point_id': 661932,
        },
    )
    assert response.status_code == 200

    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country(
            build_notify_stq_kwards(
                '+71111111112_id',
                get_default_order_id(),
                'recipient',
                'pickuped',
                'cargo_b2c_recipient_performer_on_the_way_to_destination',
                'b2c.push.recipient.destination.performer_on_the_way',
                'b2c.push.recipient.destination.performer_on_the_way',
            ),
        )
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_C2C_LOCALE_BY_CORP_CLIENT_ID={
        '5e36732e2bc54e088b1466e08e31c486': 'ru',
    },
)
@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
            'ru_genitive': 'Рогов и Копытов',
        },
    },
)
async def test_pickuped_status_from_processing(
        stq_runner,
        get_default_order_id,
        stq,
        build_ucommunications_body,
        mock_claims_full,
        taxi_cargo_c2c,
):
    mock_claims_full.current_point = {
        'claim_point_id': 661932,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-claims/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'pickuped',
            'current_point_id': 661932,
            'called_from': 'processing',
        },
    )
    assert response.status_code == 200

    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country(
            build_notify_stq_kwards(
                '+71111111112_id',
                get_default_order_id(),
                'recipient',
                'pickuped',
                'cargo_b2c_recipient_performer_on_the_way_to_destination',
                'b2c.push.recipient.destination.performer_on_the_way',
                'b2c.push.recipient.destination.performer_on_the_way',
            ),
        )
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(ORDER_ROUTE_SHARING_SUPPORTED_CORPS={})
async def test_courier_on_the_way_recipient_without_corp_name(
        stq_runner,
        get_default_order_id,
        stq,
        build_ucommunications_body,
        mock_claims_full,
        taxi_cargo_c2c,
):
    mock_claims_full.current_point = {
        'claim_point_id': 661933,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-claims/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'pickuped',
            'current_point_id': 661932,
        },
    )
    assert response.status_code == 200

    expected = build_notify_stq_kwards(
        '+71111111112_id',
        get_default_order_id(),
        'recipient',
        'pickuped',
        'cargo_b2c_recipient_performer_on_the_way_to_destination',
        'b2c.push.recipient.destination.performer_on_the_way',
        'b2c.push.recipient.without_corp_name.'
        'destination.performer_on_the_way',
    )
    expected['push_content']['body'].pop('args')
    assert stq['cargo_c2c_send_notification'].next_call()[
        'kwargs'
    ] == append_country(expected)


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_C2C_LOCALE_BY_CORP_CLIENT_ID={
        '5e36732e2bc54e088b1466e08e31c486': 'ru',
    },
)
@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
            'ru_genitive': 'Рогов и Копытов',
        },
    },
)
async def test_courier_arrived(
        stq_runner,
        get_default_order_id,
        stq,
        build_ucommunications_body,
        mock_claims_full,
        taxi_cargo_c2c,
):
    mock_claims_full.current_point = {
        'claim_point_id': 661933,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'arrived',
    }
    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-claims/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'delivery_arrived',
            'current_point_id': 661933,
        },
    )
    assert response.status_code == 200

    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country(
            build_notify_stq_kwards(
                '+71111111112_id',
                get_default_order_id(),
                'recipient',
                'delivery_arrived',
                'cargo_b2c_recipient_performer_arrived_to_destination',
                'b2c.push.recipient.destination.performer_arrived',
                'b2c.push.recipient.destination.performer_arrived',
            ),
        )
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_C2C_LOCALE_BY_CORP_CLIENT_ID={
        '5e36732e2bc54e088b1466e08e31c486': 'ru',
    },
)
@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
            'ru_genitive': 'Рогов и Копытов',
        },
    },
)
async def test_courier_arrived_recipient_only(
        stq_runner,
        get_default_order_id,
        stq,
        build_ucommunications_body,
        mock_claims_full,
        mockserver,
        taxi_cargo_c2c,
):
    @mockserver.json_handler('/cargo-c2c/v1/clients-orders')
    def _get_orders(request):
        return mockserver.make_response(
            json={
                'orders': [
                    {
                        'id': {
                            'order_id': get_default_order_id(),
                            'order_provider_id': 'cargo-claims',
                            'phone_pd_id': '+71111111111_id',
                        },
                        'roles': ['recipient'],
                        'source': 'pickup_point',
                        'sharing_key': 'some_sharing_key',
                    },
                ],
            },
        )

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-claims/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'pickup_arrived',
            'current_point_id': 661932,
        },
    )
    assert response.status_code == 200

    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country(
            build_notify_stq_kwards(
                '+71111111111_id',
                get_default_order_id(),
                'recipient',
                'pickup_arrived',
                'cargo_b2c_sender_performer_arrived_to_source',
                'b2c.push.sender.source.performer_arrived',
                'b2c.push.sender.source.performer_arrived',
            ),
        )
    )


MARKET_CORP_CLIENT_ID = 'market_corp_client_id____size_32'


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_C2C_LOCALE_BY_CORP_CLIENT_ID={
        '5e36732e2bc54e088b1466e08e31c486': 'ru',
    },
)
@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
            'ru_genitive': 'Рогов и Копытов',
        },
    },
)
async def test_performer_found_twice(
        stq_runner,
        get_default_order_id,
        stq,
        order_processing_order_create_requested,
        mockserver,
        load_json,
        mock_claims_full,
        save_client_order,
        mock_c2c_save,
        taxi_cargo_c2c,
):
    mock_claims_full.current_point = {
        'claim_point_id': 661931,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    mock_c2c_save.empty_orders_on_first_call = True

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-claims/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'performer_found',
            'current_point_id': 661931,
        },
    )
    assert response.status_code == 200

    assert save_client_order.times_called == 1
    assert stq['cargo_c2c_send_notification'].times_called == 2
    assert order_processing_order_create_requested.times_called == 2

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-c2c/process-event',
        json={
            'claim_id': get_default_order_id(),
            'status': 'performer_found',
            'current_point_id': 661931,
        },
    )
    assert response.status_code == 200
    assert save_client_order.times_called == 1
    assert stq['cargo_c2c_send_notification'].times_called == 2
    assert order_processing_order_create_requested.times_called == 2
