# pylint: disable=C0302
import pytest

from testsuite.utils import matching


def get_proc(order_id, status, taxi_status):
    return {
        '_id': order_id,
        'order': {
            'status': status,
            'taxi_status': taxi_status,
            'request': {
                'class': ['courier'],
                'source': {
                    'uris': ['some uri'],
                    'geopoint': [37.642859, 55.735316],
                    'fullname': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'description': 'Москва, Россия',
                    'porchnumber': '10',
                    'extra_data': {
                        'floor': '1',
                        'apartment': '2',
                        'doorphone_number': '3',
                        'comment': '4',
                    },
                },
                'destinations': [
                    {
                        'uris': ['some uri'],
                        'geopoint': [38.642859, 56.735316],
                        'fullname': 'Россия, Москва, Садовническая улица 82',
                        'short_text': 'БЦ Аврора',
                        'description': 'Москва, Россия',
                        'porchnumber': '5',
                        'extra_data': {
                            'floor': '6',
                            'apartment': '7',
                            'doorphone_number': '8',
                            'comment': '9',
                        },
                    },
                ],
            },
            'nz': 'moscow',
        },
        'candidates': [
            {
                'first_name': 'Иван',
                'name': 'Petr',
                'phone_personal_id': '+7123_id',
                'driver_id': 'clid_driverid1',
                'db_id': 'parkid1',
                'car_model': 'BMW',
                'car_number': 'A001AA77',
                'car_color_code': 'some_code',
            },
        ],
        'performer': {'candidate_index': 0},
    }


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
                            'order_provider_id': 'taxi',
                            'phone_pd_id': '200000000000000000000000',
                        },
                        'roles': ['sender'],
                        'sharing_key': 'sharing_key_1',
                        'sharing_url': 'http://host/sharing_key_1',
                    },
                    {
                        'id': {
                            'order_id': get_default_order_id(),
                            'order_provider_id': 'taxi',
                            'phone_pd_id': '400000000000000000000000',
                        },
                        'roles': ['recipient'],
                        'sharing_key': 'sharing_key_2',
                        'sharing_url': 'http://host/sharing_key_2',
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
        phone_pd_id, order_id, role, status, notification_id, key,
):
    return {
        'id': {
            'phone_pd_id': phone_pd_id,
            'order_id': order_id,
            'order_provider_id': 'taxi',
        },
        'notification_id': notification_id,
        'push_payload': {
            'logistics': {
                'type': 'delivery-state-changed',
                'delivery_id': f'taxi/{order_id}',
                'notification_group': f'taxi/{order_id}',
                'meta': {
                    'tariff_class': 'courier',
                    'order_provider_id': 'taxi',
                    'roles': [role],
                    'order_status': status,
                },
            },
        },
        'push_content': {
            'title': {
                'keyset': 'cargo',
                'key': f'{key}.title',
                'locale': 'ru',
            },
            'body': {'keyset': 'cargo', 'key': f'{key}.body', 'locale': 'ru'},
        },
        'log_extra': {'_link': matching.AnyString()},
        'initiator_phone_pd_id': '100000000000000000000000',
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_empty_orders(
        stq_runner, save_client_order, taxi_processing, get_default_order_id,
):
    await taxi_processing(
        get_default_order_id(),
        'create',
        'pending',
        {'$oid': '500000000000000000000000'},
        'courier',
        'ru',
        {
            'extra_data': {
                'contact_phone_id': {'$oid': '500000000000000000000000'},
            },
        },
        [
            {
                'extra_data': {
                    'contact_phone_id': {'$oid': '500000000000000000000000'},
                },
            },
        ],
        False,
        '4.4.4',
        'moscow',
        '123',
    )

    assert save_client_order.times_called == 0


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_C2C_NEW_DELIVERY_SMS_SETTINGS=[
        {
            'settings': {
                'role': 'recipient',
                'tariff_class': 'courier',
                'door_to_door': True,
            },
            'tanker_key': 'courier.sms.to_reciever.door_to_door',
            'keyset': 'notify',
        },
        {
            'settings': {
                'role': 'sender',
                'tariff_class': 'courier',
                'door_to_door': True,
            },
            'tanker_key': 'express.sms.to_sender.door_to_door',
            'keyset': 'notify',
        },
    ],
    ROUTE_SHARING_URL_TEMPLATES={
        'yandex': 'https://abc/{key}?lang={lang}',
        'yauber': 'https://abc/{key}?lang={lang}',
    },
)
async def test_create(
        stq_runner,
        save_client_order,
        stq,
        build_ucommunications_body,
        order_processing_order_create_requested,
        mockserver,
        mock_c2c_save,
        taxi_processing,
        order_archive_mock,
        get_default_order_id,
):
    mock_c2c_save.empty_orders_on_first_call = True

    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'pending', None),
    )

    await taxi_processing(
        get_default_order_id(),
        'handle_assigning',
        'assigned',
        {'$oid': '100000000000000000000000'},
        'courier',
        'ru',
        {
            'extra_data': {
                'contact_phone_id': {'$oid': '200000000000000000000000'},
            },
        },
        [
            {
                'extra_data': {
                    'contact_phone_id': {'$oid': '400000000000000000000000'},
                },
            },
        ],
        True,
        '4.4.4',
        'moscow',
        '123',
    )

    assert save_client_order.next_call() == {
        'arg': {
            'orders': [
                {
                    'id': {
                        'order_id': get_default_order_id(),
                        'order_provider_id': 'taxi',
                        'phone_pd_id': '200000000000000000000000',
                    },
                    'roles': ['sender'],
                },
                {
                    'id': {
                        'order_id': get_default_order_id(),
                        'order_provider_id': 'taxi',
                        'phone_pd_id': '400000000000000000000000',
                    },
                    'roles': ['recipient'],
                },
            ],
        },
    }

    expected_notify_kwargs = build_notify_stq_kwards(
        '200000000000000000000000',
        get_default_order_id(),
        'sender',
        'assigned',
        'cargo_c2c_sender_new_order',
        'c2c.push.sender.new_order',
    )
    expected_notify_kwargs['sms_content'] = {
        'text': {
            'args': {'sharing_url': 'https://abc/123?lang=ru'},
            'key': 'express.sms.to_sender.door_to_door',
            'keyset': 'notify',
            'locale': 'ru',
        },
    }
    assert stq['cargo_c2c_send_notification'].next_call()[
        'kwargs'
    ] == append_country_and_sender(expected_notify_kwargs)

    expected_notify_kwargs = build_notify_stq_kwards(
        '400000000000000000000000',
        get_default_order_id(),
        'recipient',
        'assigned',
        'cargo_c2c_recipient_new_order',
        'c2c.push.recipient.new_order',
    )
    expected_notify_kwargs['sms_content'] = {
        'text': {
            'args': {'sharing_url': 'https://abc/123?lang=ru'},
            'key': 'courier.sms.to_reciever.door_to_door',
            'keyset': 'notify',
            'locale': 'ru',
        },
    }
    assert stq['cargo_c2c_send_notification'].next_call()[
        'kwargs'
    ] == append_country_and_sender(expected_notify_kwargs)

    assert order_processing_order_create_requested.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'taxi',
                'phone_pd_id': '200000000000000000000000',
                'roles': ['sender'],
            },
            'kind': 'order-create-requested',
            'trait': 'is-create',
        },
    }
    assert order_processing_order_create_requested.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'taxi',
                'phone_pd_id': '400000000000000000000000',
                'roles': ['recipient'],
            },
            'kind': 'order-create-requested',
            'trait': 'is-create',
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_C2C_NEW_DELIVERY_SMS_SETTINGS=[
        {
            'settings': {
                'role': 'recipient',
                'tariff_class': 'courier',
                'door_to_door': True,
            },
            'tanker_key': 'courier.sms.to_reciever.door_to_door',
            'keyset': 'notify',
        },
        {
            'settings': {
                'role': 'sender',
                'tariff_class': 'courier',
                'door_to_door': True,
            },
            'tanker_key': 'express.sms.to_sender.door_to_door',
            'keyset': 'notify',
        },
    ],
    ROUTE_SHARING_URL_TEMPLATES={
        'yandex': 'https://abc/{key}?lang={lang}',
        'yauber': 'https://abc/{key}?lang={lang}',
    },
    CARGO_C2C_ENABLE_SHORT_URL_IN_SMS=True,
)
async def test_sms_short_url(
        stq_runner,
        save_client_order,
        stq,
        build_ucommunications_body,
        order_processing_order_create_requested,
        mockserver,
        taxi_processing,
        order_archive_mock,
        get_default_order_id,
        mock_c2c_save,
):
    mock_c2c_save.empty_orders_on_first_call = True

    @mockserver.json_handler('/clck/--')
    def _mock_clck(request):
        return ['short_url']

    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'pending', None),
    )

    await taxi_processing(
        get_default_order_id(),
        'handle_assigning',
        'assigned',
        {'$oid': '100000000000000000000000'},
        'courier',
        'ru',
        {
            'extra_data': {
                'contact_phone_id': {'$oid': '200000000000000000000000'},
            },
        },
        [
            {
                'extra_data': {
                    'contact_phone_id': {'$oid': '400000000000000000000000'},
                },
            },
        ],
        True,
        '4.4.4',
        'moscow',
        '123',
    )

    result = stq['cargo_c2c_send_notification'].next_call()['kwargs']
    assert result['sms_content']['text']['args']['sharing_url'] == 'short_url'


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
        },
    },
)
async def test_create_corp(
        stq_runner,
        save_client_order,
        stq,
        build_ucommunications_body,
        order_processing_order_create_requested,
        mockserver,
        taxi_processing,
        get_default_order_id,
        mock_c2c_save,
        order_archive_mock,
):
    mock_c2c_save.empty_orders_on_first_call = True

    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'pending', None),
    )

    await taxi_processing(
        get_default_order_id(),
        'handle_assigning',
        'assigned',
        {'$oid': '100000000000000000000000'},
        'courier',
        'ru',
        {
            'extra_data': {
                'contact_phone_id': {'$oid': '200000000000000000000000'},
            },
        },
        [
            {
                'extra_data': {
                    'contact_phone_id': {'$oid': '400000000000000000000000'},
                },
            },
        ],
        True,
        '4.4.4',
        'moscow',
        '123',
        None,
        {
            'phone_personal_id': '+70000_id',
            'forwarding': {'phone': '+70000', 'ext': '123'},
        },
        '5e36732e2bc54e088b1466e08e31c486',
    )

    assert save_client_order.next_call() == {
        'arg': {
            'orders': [
                {
                    'id': {
                        'order_id': get_default_order_id(),
                        'order_provider_id': 'taxi',
                        'phone_pd_id': '400000000000000000000000',
                    },
                    'roles': ['recipient'],
                },
            ],
        },
    }

    expected_notify_kwargs = build_notify_stq_kwards(
        '400000000000000000000000',
        get_default_order_id(),
        'recipient',
        'assigned',
        'cargo_c2c_recipient_new_order',
        'b2c.push.recipient.new_order',
    )
    expected_notify_kwargs['push_content']['body']['args'] = {
        'corp_client_name': 'Рога и Копыта',
    }
    assert stq['cargo_c2c_send_notification'].next_call()[
        'kwargs'
    ] == append_country_and_sender(expected_notify_kwargs)


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_c2c_control_client_orders_creation',
    consumers=['cargo-c2c/control_orders_creation'],
    clauses=[],
    default_value={'enabled': True, 'allowed_roles': ['recipient']},
    is_config=True,
)
async def test_crate_client_orders_experiment(
        stq_runner,
        save_client_order,
        mockserver,
        taxi_processing,
        get_default_order_id,
        mock_c2c_save,
        order_archive_mock,
):
    mock_c2c_save.empty_orders_on_first_call = True

    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'pending', None),
    )

    await taxi_processing(
        get_default_order_id(),
        'handle_assigning',
        'assigned',
        {'$oid': '100000000000000000000000'},
        'courier',
        'ru',
        {
            'extra_data': {
                'contact_phone_id': {'$oid': '200000000000000000000000'},
            },
        },
        [
            {
                'extra_data': {
                    'contact_phone_id': {'$oid': '400000000000000000000000'},
                },
            },
        ],
        True,
        '4.4.4',
        'moscow',
        '123',
    )

    assert save_client_order.next_call() == {
        'arg': {
            'orders': [
                {
                    'id': {
                        'order_id': get_default_order_id(),
                        'order_provider_id': 'taxi',
                        'phone_pd_id': '400000000000000000000000',
                    },
                    'roles': ['recipient'],
                },
            ],
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_autoreorder(
        stq_runner,
        stq,
        build_ucommunications_body,
        save_client_order,
        order_processing_order_create_requested,
        taxi_processing,
        get_default_order_id,
        mock_c2c_save,
        order_archive_mock,
):
    mock_c2c_save.empty_orders_on_first_call = True

    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'pending', None),
    )

    await taxi_processing(
        get_default_order_id(),
        'handle_assigning',
        'assigned',
        {'$oid': '100000000000000000000000'},
        'courier',
        'ru',
        {
            'extra_data': {
                'contact_phone_id': {'$oid': '200000000000000000000000'},
            },
        },
        [
            {
                'extra_data': {
                    'contact_phone_id': {'$oid': '400000000000000000000000'},
                },
            },
        ],
        True,
        '4.4.4',
        'moscow',
        '123',
    )

    assert save_client_order.times_called == 1
    assert order_processing_order_create_requested.times_called == 2

    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '200000000000000000000000',
                get_default_order_id(),
                'sender',
                'assigned',
                'cargo_c2c_sender_new_order',
                'c2c.push.sender.new_order',
            ),
        )
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '400000000000000000000000',
                get_default_order_id(),
                'recipient',
                'assigned',
                'cargo_c2c_recipient_new_order',
                'c2c.push.recipient.new_order',
            ),
        )
    )


@pytest.mark.experiments3(filename='experiment.json')
async def test_waiting(
        stq_runner,
        save_client_order,
        stq,
        build_ucommunications_body,
        order_processing_order_create_requested,
        mockserver,
        mock_c2c_save,
        taxi_processing,
        order_archive_mock,
        get_default_order_id,
):
    mock_c2c_save.empty_orders_on_first_call = False

    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'assigned', None),
    )

    await taxi_processing(
        get_default_order_id(),
        'handle_waiting',
        'assigned',
        {'$oid': '100000000000000000000000'},
        'courier',
        'ru',
        {
            'extra_data': {
                'contact_phone_id': {'$oid': '200000000000000000000000'},
            },
        },
        [
            {
                'extra_data': {
                    'contact_phone_id': {'$oid': '400000000000000000000000'},
                },
            },
        ],
        True,
        '4.4.4',
        'moscow',
        '123',
    )

    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '200000000000000000000000',
                get_default_order_id(),
                'sender',
                'assigned',
                'cargo_c2c_sender_performer_arrived_to_source',
                'c2c.push.sender.source.performer_arrived',
            ),
        )
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
        },
    },
)
async def test_waiting_corp(
        stq_runner,
        stq,
        build_ucommunications_body,
        taxi_processing,
        mock_c2c_save,
        order_archive_mock,
        get_default_order_id,
):
    mock_c2c_save.empty_orders_on_first_call = False

    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'assigned', None),
    )

    await taxi_processing(
        get_default_order_id(),
        'handle_waiting',
        'assigned',
        {'$oid': '100000000000000000000000'},
        'courier',
        'ru',
        {
            'extra_data': {
                'contact_phone_id': {'$oid': '200000000000000000000000'},
            },
        },
        [
            {
                'extra_data': {
                    'contact_phone_id': {'$oid': '400000000000000000000000'},
                },
            },
        ],
        True,
        '4.4.4',
        'moscow',
        '123',
        'waiting',
        None,
        '5e36732e2bc54e088b1466e08e31c486',
    )

    expected_kwargs = build_notify_stq_kwards(
        '200000000000000000000000',
        get_default_order_id(),
        'sender',
        'assigned',
        'cargo_c2c_sender_performer_arrived_to_source',
        'b2c.push.sender.source.performer_arrived',
    )
    expected_kwargs['push_content']['body']['args'] = {
        'corp_client_name': 'Рога и Копыта',
    }
    assert stq['cargo_c2c_send_notification'].next_call()[
        'kwargs'
    ] == append_country_and_sender(expected_kwargs)


@pytest.mark.experiments3(filename='experiment.json')
async def test_transporting(
        stq_runner,
        stq,
        build_ucommunications_body,
        taxi_processing,
        mock_c2c_save,
        order_archive_mock,
        get_default_order_id,
):
    mock_c2c_save.empty_orders_on_first_call = False

    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'pending', None),
    )

    await taxi_processing(
        get_default_order_id(),
        'handle_transporting',
        'assigned',
        {'$oid': '100000000000000000000000'},
        'courier',
        'ru',
        {
            'extra_data': {
                'contact_phone_id': {'$oid': '200000000000000000000000'},
            },
        },
        [
            {
                'extra_data': {
                    'contact_phone_id': {'$oid': '400000000000000000000000'},
                },
            },
        ],
        True,
        '4.4.4',
        'moscow',
        '123',
        'transporting',
    )

    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '200000000000000000000000',
                get_default_order_id(),
                'sender',
                'assigned',
                'cargo_c2c_sender_performer_on_the_way_to_destination',
                'c2c.push.sender.destination.performer_on_the_way',
            ),
        )
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '400000000000000000000000',
                get_default_order_id(),
                'recipient',
                'assigned',
                'cargo_c2c_recipient_performer_on_the_way_to_destination',
                'c2c.push.recipient.destination.performer_on_the_way',
            ),
        )
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
        },
    },
)
async def test_transporting_corp(
        stq_runner,
        stq,
        build_ucommunications_body,
        mockserver,
        taxi_processing,
        mock_c2c_save,
        order_archive_mock,
        get_default_order_id,
):
    mock_c2c_save.empty_orders_on_first_call = True

    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'pending', None),
    )

    @mockserver.json_handler('/cargo-c2c/v1/clients-orders')
    def _get_orders(request):
        return mockserver.make_response(
            json={
                'orders': [
                    {
                        'id': {
                            'order_id': get_default_order_id(),
                            'order_provider_id': 'taxi',
                            'phone_pd_id': '400000000000000000000000',
                        },
                        'roles': ['recipient'],
                        'sharing_key': 'sharing_key_1',
                        'sharing_url': 'http://host/sharing_key_1',
                    },
                ],
            },
        )

    await taxi_processing(
        get_default_order_id(),
        'handle_transporting',
        'assigned',
        {'$oid': '100000000000000000000000'},
        'courier',
        'ru',
        {
            'extra_data': {
                'contact_phone_id': {'$oid': '200000000000000000000000'},
            },
        },
        [
            {
                'extra_data': {
                    'contact_phone_id': {'$oid': '400000000000000000000000'},
                },
            },
        ],
        True,
        '4.4.4',
        'moscow',
        '123',
        'transporting',
        None,
        '5e36732e2bc54e088b1466e08e31c486',
    )
    expected_kwargs = build_notify_stq_kwards(
        '400000000000000000000000',
        get_default_order_id(),
        'recipient',
        'assigned',
        'cargo_c2c_recipient_performer_on_the_way_to_destination',
        'b2c.push.recipient.destination.performer_on_the_way',
    )
    expected_kwargs['push_content']['body']['args'] = {
        'corp_client_name': 'Рога и Копыта',
    }
    assert stq['cargo_c2c_send_notification'].next_call()[
        'kwargs'
    ] == append_country_and_sender(expected_kwargs)


@pytest.mark.experiments3(filename='experiment.json')
async def test_finish(
        stq_runner,
        stq,
        build_ucommunications_body,
        order_processing_order_terminated,
        taxi_processing,
        mock_c2c_save,
        order_archive_mock,
        get_default_order_id,
):
    mock_c2c_save.empty_orders_on_first_call = False

    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'pending', None),
    )

    await taxi_processing(
        get_default_order_id(),
        'handle_finish',
        'finish',
        {'$oid': '100000000000000000000000'},
        'courier',
        'ru',
        {
            'extra_data': {
                'contact_phone_id': {'$oid': '200000000000000000000000'},
            },
        },
        [
            {
                'extra_data': {
                    'contact_phone_id': {'$oid': '400000000000000000000000'},
                },
            },
        ],
        True,
        '4.4.4',
        'moscow',
        '123',
        'complete',
    )

    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '200000000000000000000000',
                get_default_order_id(),
                'sender',
                'finish',
                'cargo_c2c_sender_delivery_finished',
                'c2c.push.sender.delivery_finished',
            ),
        )
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == append_country_and_sender(
            build_notify_stq_kwards(
                '400000000000000000000000',
                get_default_order_id(),
                'recipient',
                'finish',
                'cargo_c2c_recipient_delivery_finished',
                'c2c.push.recipient.delivery_finished',
            ),
        )
    )
    assert order_processing_order_terminated.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'taxi',
                'phone_pd_id': '200000000000000000000000',
                'resolution': 'succeed',
            },
            'kind': 'order-terminated',
        },
    }
    assert order_processing_order_terminated.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'taxi',
                'phone_pd_id': '400000000000000000000000',
                'resolution': 'succeed',
            },
            'kind': 'order-terminated',
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_cancel(
        stq_runner,
        stq,
        build_ucommunications_body,
        order_processing_order_terminated,
        taxi_processing,
        mock_c2c_save,
        order_archive_mock,
        get_default_order_id,
        mockserver,
):
    mock_c2c_save.empty_orders_on_first_call = False

    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'pending', None),
    )

    await taxi_processing(
        get_default_order_id(),
        'handle_finish',
        'finish',
        {'$oid': '100000000000000000000000'},
        'courier',
        'ru',
        {
            'extra_data': {
                'contact_phone_id': {'$oid': '200000000000000000000000'},
            },
        },
        [
            {
                'extra_data': {
                    'contact_phone_id': {'$oid': '400000000000000000000000'},
                },
            },
        ],
        True,
        '4.4.4',
        'moscow',
        '123',
        'canceled',
    )

    assert stq['cargo_c2c_send_notification'].times_called == 0
    assert order_processing_order_terminated.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'taxi',
                'phone_pd_id': '200000000000000000000000',
                'resolution': 'failed',
            },
            'kind': 'order-terminated',
        },
    }
    assert order_processing_order_terminated.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'taxi',
                'phone_pd_id': '400000000000000000000000',
                'resolution': 'failed',
            },
            'kind': 'order-terminated',
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_create_twice(
        stq_runner,
        save_client_order,
        stq,
        build_ucommunications_body,
        order_processing_order_create_requested,
        mockserver,
        mock_c2c_save,
        taxi_processing,
        order_archive_mock,
        get_default_order_id,
):
    mock_c2c_save.empty_orders_on_first_call = True

    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'pending', None),
    )

    args = [
        get_default_order_id(),
        'handle_assigning',
        'assigned',
        {'$oid': '100000000000000000000000'},
        'courier',
        'ru',
        {
            'extra_data': {
                'contact_phone_id': {'$oid': '200000000000000000000000'},
            },
        },
        [
            {
                'extra_data': {
                    'contact_phone_id': {'$oid': '400000000000000000000000'},
                },
            },
        ],
        True,
        '4.4.4',
        'moscow',
        '123',
        None,
        {
            'phone_personal_id': '+70000_id',
            'forwarding': {'phone': '+70000', 'ext': '123'},
        },
        None,
    ]
    mock_c2c_save.empty_orders_on_first_call = True

    await taxi_processing(*args)
    assert save_client_order.times_called == 1
    assert stq['cargo_c2c_send_notification'].times_called == 2
    assert order_processing_order_create_requested.times_called == 2

    await taxi_processing(*args)
    assert save_client_order.times_called == 1
    assert stq['cargo_c2c_send_notification'].times_called == 4
    assert order_processing_order_create_requested.times_called == 2
