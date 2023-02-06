import copy

import pytest

from testsuite.utils import matching


CARGO_C2C_LP_SETTINGS = {
    'orders_to_process': [
        {
            'employer': 'beru',
            'last_mile_operator_id': 'taxi-external',
            'last_mile_transfer_policy': 'AFAP',
        },
        {
            'employer': 'beru',
            'last_mile_operator_id': 'taxi-external',
            'last_mile_transfer_policy': 'interval_strict',
        },
        {
            'employer': 'beru',
            'last_mile_operator_id': 'lavka',
            'start_processing_statuses_overrides': [
                'DELIVERY_ARRIVED_PICKUP_POINT',
            ],
            'terminal_statuses_overrides': {
                'failed': ['TODO'],
                'succeed': ['ORDERED'],
            },
        },
        {
            'employer': 'testAPI',
            'last_mile_operator_id': 'self_pickup',
            'last_mile_transfer_policy': 'self_pickup',
        },
    ],
    'terminal_statuses': {
        'failed': [
            'VALIDATING_ERROR',
            'ORDER_CANCELLED',
            'DELIVERY_CAN_NOT_BE_COMPLETED',
            'CANCELLED_BY_RECIPIENT',
            'DELIVERY_REJECTED',
            'RETURNED_FINISH',
            'CANCELLED',
            'CANCEL_WITH_PAYMENT',
            'LOST',
            'CANCELLED_USER',
        ],
        'succeed': [
            'DELIVERY_DELIVERED',
            'PARTIALLY_DELIVERED',
            'DELIVERED_FINISH',
        ],
    },
}


@pytest.fixture(autouse=True, name='mock_c2c_save')
def _mock_c2c(mockserver, get_default_order_id):
    @mockserver.json_handler('/cargo-c2c/v1/clients-orders')
    def _get_orders(request):
        if not context.expected_order_id:
            assert request.json['order_id'] == get_default_order_id()
        else:
            assert request.json['order_id'] == context.expected_order_id

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
                            'order_provider_id': 'logistic-platform',
                            'phone_pd_id': '+71111111111_id',
                        },
                        'roles': ['recipient'],
                        'sharing_key': 'sharing_key_1',
                        'sharing_url': 'http://host/sharing_key_1',
                    },
                ],
            },
        )

    class Context:
        def __init__(self):
            self.expected_order_id = None
            self.empty_orders_on_first_call = False

    context = Context()
    return context


def build_notify_stq_kwargs(
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
            'order_provider_id': 'logistic-platform',
        },
        'notification_id': notification_id,
        'push_payload': {
            'logistics': {
                'type': 'delivery-state-changed',
                'delivery_id': f'logistic-platform/{order_id}',
                'notification_group': f'logistic-platform/{order_id}',
                'meta': {
                    'tariff_class': '',
                    'order_provider_id': 'logistic-platform',
                    'roles': [role],
                    'order_status': status,
                },
            },
        },
        'push_content': {
            'title': {
                'keyset': 'cargo_notify',
                'key': f'{key_title}.title',
                'locale': 'ru',
            },
            'body': {
                'keyset': 'cargo_notify',
                'key': f'{key_body}.body',
                'locale': 'ru',
            },
        },
        'log_extra': {'_link': matching.AnyString()},
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(CARGO_C2C_LP_SETTINGS=CARGO_C2C_LP_SETTINGS)
async def test_order_created(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        mock_logistic_platform,
        mock_order_statuses_history,
        stq_runner,
        mockserver,
        order_processing_order_create_requested,
        save_client_order,
        stq,
        mock_c2c_save,
):
    mock_c2c_save.empty_orders_on_first_call = True

    mock_logistic_platform.file_name = 'order_created.json'
    mock_order_statuses_history.file_name = 'order_created.json'
    await taxi_cargo_c2c.post(
        '/v1/processing/logistic-platform/process-event',
        json={'request_id': get_default_order_id(), 'status': ''},
    )

    assert order_processing_order_create_requested.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'logistic-platform',
                'phone_pd_id': '+71111111111_id',
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
                        'order_provider_id': 'logistic-platform',
                        'phone_pd_id': '+71111111111_id',
                    },
                    'roles': ['recipient'],
                },
            ],
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(CARGO_C2C_LP_SETTINGS=CARGO_C2C_LP_SETTINGS)
async def test_order_created_self_pickup(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        mock_logistic_platform,
        mock_order_statuses_history,
        stq_runner,
        mockserver,
        order_processing_order_create_requested,
        save_client_order,
        stq,
        mock_c2c_save,
):
    mock_c2c_save.empty_orders_on_first_call = True

    mock_logistic_platform.file_name = 'self_pickup_order_created.json'
    mock_order_statuses_history.file_name = 'order_created.json'
    await taxi_cargo_c2c.post(
        '/v1/processing/logistic-platform/process-event',
        json={'request_id': get_default_order_id(), 'status': ''},
    )

    assert order_processing_order_create_requested.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'logistic-platform',
                'phone_pd_id': '+71111111111_id',
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
                        'order_provider_id': 'logistic-platform',
                        'phone_pd_id': '+71111111111_id',
                    },
                    'roles': ['recipient'],
                },
            ],
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(CARGO_C2C_LP_SETTINGS=CARGO_C2C_LP_SETTINGS)
@pytest.mark.now('2022-02-16T14:00:00+03:00')
async def test_shipment_created(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        mock_logistic_platform,
        mock_order_statuses_history,
        stq_runner,
        mockserver,
        order_processing_order_create_requested,
        save_client_order,
        stq,
        mock_c2c_save,
):
    mock_c2c_save.empty_orders_on_first_call = True

    mock_logistic_platform.file_name = 'shipment.json'
    mock_order_statuses_history.file_name = 'shipment_order_created.json'
    await taxi_cargo_c2c.post(
        '/v1/processing/logistic-platform/process-event',
        json={'request_id': get_default_order_id(), 'status': ''},
    )

    assert order_processing_order_create_requested.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'logistic-platform',
                'phone_pd_id': '+71111111111_id',
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
                        'order_provider_id': 'logistic-platform',
                        'phone_pd_id': '+71111111111_id',
                    },
                    'roles': ['recipient'],
                },
            ],
        },
    }

    assert stq['cargo_c2c_send_notification'].times_called == 1
    push = stq['cargo_c2c_send_notification'].next_call()['kwargs']
    assert push['push_payload'] == {
        'deeplink': 'yandextaxi://shipment?id=%s' % get_default_order_id(),
    }
    assert push['push_content'] == {
        'body': {
            'key': 'market_by_click.on_demand.new_order.body',
            'keyset': 'cargo_notify',
            'locale': 'ru',
            'args': {
                'corp_client_name': 'Рога и Копыта',
                'sharing_url': 'http://host/sharing_key_1',
                'corp_client_name_ru_genitive': 'Рога и Копыта',
                'external_order_id': '100',
                'last_station_end_work': '23:59',
                'last_station_start_work': '0:00',
                'delivery_interval_date_lowwer': '28 Ноября',
                'delivery_interval_date_upper': '28 Ноября',
                'delivery_interval_numeric_date_lowwer': '28.11',
                'delivery_interval_numeric_date_upper': '28.11',
                'delivery_interval_time_from': '14:00',
                'delivery_interval_time_to': '19:33',
                'delivery_interval_date_to': '28 Ноября',
                'delivery_interval_numeric_date_to_lower': '28.11',
                'delivery_interval_numeric_date_to_upper': '28.11',
                'delivery_interval_date_to_lower': '28 Ноября',
                'delivery_interval_date_to_upper': '28 Ноября',
                'stored_until_date': '6 Декабря',
                'stored_until_time': '02:57',
            },
        },
        'title': {
            'key': 'market_by_click.interval_strict.new_order.title',
            'keyset': 'cargo_notify',
            'locale': 'ru',
            'args': {
                'corp_client_name': 'Рога и Копыта',
                'sharing_url': 'http://host/sharing_key_1',
                'corp_client_name_ru_genitive': 'Рога и Копыта',
                'external_order_id': '100',
                'last_station_end_work': '23:59',
                'last_station_start_work': '0:00',
                'delivery_interval_date_lowwer': '28 Ноября',
                'delivery_interval_date_upper': '28 Ноября',
                'delivery_interval_numeric_date_lowwer': '28.11',
                'delivery_interval_numeric_date_upper': '28.11',
                'delivery_interval_time_from': '14:00',
                'delivery_interval_time_to': '19:33',
                'delivery_interval_date_to': '28 Ноября',
                'delivery_interval_numeric_date_to_lower': '28.11',
                'delivery_interval_numeric_date_to_upper': '28.11',
                'delivery_interval_date_to_lower': '28 Ноября',
                'delivery_interval_date_to_upper': '28 Ноября',
                'stored_until_date': '6 Декабря',
                'stored_until_time': '02:57',
            },
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_do_not_show_in_go(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        mock_logistic_platform,
        mock_order_statuses_history,
        stq_runner,
        mockserver,
        order_processing_order_create_requested,
        save_client_order,
        stq,
        mock_c2c_save,
        taxi_config,
):
    settings = copy.deepcopy(CARGO_C2C_LP_SETTINGS)
    settings['orders_to_process'][0]['creation_context'] = {
        'do_not_show_in_go': True,
    }
    settings['orders_to_process'][1]['creation_context'] = {
        'do_not_show_in_go': True,
    }
    taxi_config.set(CARGO_C2C_LP_SETTINGS=settings)

    mock_c2c_save.empty_orders_on_first_call = True

    mock_logistic_platform.file_name = 'order_created.json'
    mock_order_statuses_history.file_name = 'order_created.json'
    await taxi_cargo_c2c.post(
        '/v1/processing/logistic-platform/process-event',
        json={'request_id': get_default_order_id(), 'status': ''},
    )

    assert save_client_order.next_call() == {
        'arg': {
            'orders': [
                {
                    'id': {
                        'order_id': get_default_order_id(),
                        'order_provider_id': 'logistic-platform',
                        'phone_pd_id': '+71111111111_id',
                    },
                    'roles': ['recipient'],
                    'do_not_show_in_go': True,
                },
            ],
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(CARGO_C2C_LP_SETTINGS=CARGO_C2C_LP_SETTINGS)
async def test_delivered(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        order_processing_order_terminated,
        get_default_order_id,
        mock_logistic_platform,
        mock_order_statuses_history,
        stq_runner,
        stq,
):
    mock_logistic_platform.file_name = 'delivered.json'
    mock_order_statuses_history.file_name = 'delivered.json'

    await taxi_cargo_c2c.post(
        '/v1/processing/logistic-platform/process-event',
        json={'request_id': get_default_order_id(), 'status': ''},
    )
    assert order_processing_order_terminated.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'logistic-platform',
                'phone_pd_id': '+71111111111_id',
                'resolution': 'succeed',
            },
            'kind': 'order-terminated',
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(CARGO_C2C_LP_SETTINGS=CARGO_C2C_LP_SETTINGS)
async def test_shipment_ordered(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        order_processing_order_terminated,
        get_default_order_id,
        mock_logistic_platform,
        mock_order_statuses_history,
        stq_runner,
        stq,
):
    mock_logistic_platform.file_name = 'shipment.json'
    mock_order_statuses_history.file_name = 'shipment_ordered.json'

    await taxi_cargo_c2c.post(
        '/v1/processing/logistic-platform/process-event',
        json={'request_id': get_default_order_id(), 'status': ''},
    )
    assert order_processing_order_terminated.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'logistic-platform',
                'phone_pd_id': '+71111111111_id',
                'resolution': 'succeed',
            },
            'kind': 'order-terminated',
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(CARGO_C2C_LP_SETTINGS=CARGO_C2C_LP_SETTINGS)
async def test_cancelled(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        order_processing_order_terminated,
        get_default_order_id,
        mock_logistic_platform,
        mock_order_statuses_history,
        stq_runner,
        stq,
):
    mock_logistic_platform.file_name = 'cancelled.json'
    mock_order_statuses_history.file_name = 'cancelled.json'
    await taxi_cargo_c2c.post(
        '/v1/processing/logistic-platform/process-event',
        json={'request_id': get_default_order_id(), 'status': ''},
    )
    assert order_processing_order_terminated.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'logistic-platform',
                'phone_pd_id': '+71111111111_id',
                'resolution': 'failed',
            },
            'kind': 'order-terminated',
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(CARGO_C2C_LP_SETTINGS=CARGO_C2C_LP_SETTINGS)
async def test_returning(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        order_processing_order_terminated,
        get_default_order_id,
        mock_logistic_platform,
        mock_order_statuses_history,
        stq_runner,
        stq,
):
    mock_logistic_platform.file_name = 'returning.json'
    mock_order_statuses_history.file_name = 'returning.json'

    await taxi_cargo_c2c.post(
        '/v1/processing/logistic-platform/process-event',
        json={'request_id': get_default_order_id(), 'status': ''},
    )
    assert order_processing_order_terminated.next_call() == {
        'arg': {
            'data': {
                'order_id': get_default_order_id(),
                'order_provider_id': 'logistic-platform',
                'phone_pd_id': '+71111111111_id',
                'resolution': 'failed',
            },
            'kind': 'order-terminated',
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(CARGO_C2C_LP_SETTINGS=CARGO_C2C_LP_SETTINGS)
async def test_order_created_twice(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        mock_logistic_platform,
        mock_order_statuses_history,
        stq_runner,
        mockserver,
        order_processing_order_create_requested,
        save_client_order,
        stq,
        mock_c2c_save,
):
    mock_c2c_save.empty_orders_on_first_call = True
    mock_logistic_platform.file_name = 'order_created.json'
    mock_order_statuses_history.file_name = 'order_created.json'

    await taxi_cargo_c2c.post(
        '/v1/processing/logistic-platform/process-event',
        json={'request_id': get_default_order_id(), 'status': ''},
    )
    assert order_processing_order_create_requested.times_called == 1
    assert save_client_order.times_called == 1

    await taxi_cargo_c2c.post(
        '/v1/processing/logistic-platform/process-event',
        json={'request_id': get_default_order_id(), 'status': ''},
    )
    assert order_processing_order_create_requested.times_called == 1
    assert save_client_order.times_called == 1


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(CARGO_C2C_LP_SETTINGS=CARGO_C2C_LP_SETTINGS)
async def test_logistic_platform_pushes_processing(
        create_logistic_platform_orders,
        get_default_order_id,
        mock_logistic_platform,
        mock_order_statuses_history,
        stq,
        stq_runner,
        taxi_cargo_c2c,
):
    mock_logistic_platform.file_name = 'order_created.json'
    mock_order_statuses_history.file_name = 'order_created.json'

    await taxi_cargo_c2c.post(
        '/v1/processing/logistic-platform/process-event',
        json={'request_id': get_default_order_id(), 'status': ''},
    )
    assert stq['cargo_c2c_send_notification'].times_called == 1

    mock_logistic_platform.file_name = 'delivered.json'
    mock_order_statuses_history.file_name = 'delivered.json'

    await taxi_cargo_c2c.post(
        '/v1/processing/logistic-platform/process-event',
        json={'request_id': get_default_order_id(), 'status': ''},
    )
    assert stq['cargo_c2c_send_notification'].times_called == 3

    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs'][
            'push_content'
        ]
        == {
            'body': {
                'key': 'market_express.new_order.body',
                'keyset': 'cargo_notify',
                'locale': 'ru',
                'args': {
                    'corp_client_name': 'Рога и Копыта',
                    'sharing_url': 'http://host/sharing_key_1',
                    'corp_client_name_ru_genitive': 'Рога и Копыта',
                    'external_order_id': '32779352',
                    'last_station_end_work': '23:59',
                    'last_station_start_work': '0:00',
                },
            },
            'title': {
                'key': 'market_express.new_order.title',
                'keyset': 'cargo_notify',
                'locale': 'ru',
                'args': {
                    'corp_client_name': 'Рога и Копыта',
                    'sharing_url': 'http://host/sharing_key_1',
                    'corp_client_name_ru_genitive': 'Рога и Копыта',
                    'external_order_id': '32779352',
                    'last_station_end_work': '23:59',
                    'last_station_start_work': '0:00',
                },
            },
        }
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs'][
            'push_content'
        ]
        == {
            'body': {
                'key': 'market_express.delivery_on_the_way.body',
                'keyset': 'cargo_notify',
                'locale': 'ru',
                'args': {
                    'corp_client_name': 'Рога и Копыта',
                    'sharing_url': 'http://host/sharing_key_1',
                    'corp_client_name_ru_genitive': 'Рога и Копыта',
                    'external_order_id': '32779352',
                    'last_station_end_work': '23:59',
                    'last_station_start_work': '0:00',
                },
            },
            'title': {
                'key': 'market_express.delivery_on_the_way.title',
                'keyset': 'cargo_notify',
                'locale': 'ru',
                'args': {
                    'corp_client_name': 'Рога и Копыта',
                    'sharing_url': 'http://host/sharing_key_1',
                    'corp_client_name_ru_genitive': 'Рога и Копыта',
                    'external_order_id': '32779352',
                    'last_station_end_work': '23:59',
                    'last_station_start_work': '0:00',
                },
            },
        }
    )
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs'][
            'push_content'
        ]
        == {
            'body': {
                'key': 'market_express.delivery_finished.body',
                'keyset': 'cargo_notify',
                'locale': 'ru',
                'args': {
                    'corp_client_name': 'Рога и Копыта',
                    'sharing_url': 'http://host/sharing_key_1',
                    'corp_client_name_ru_genitive': 'Рога и Копыта',
                    'external_order_id': '32779352',
                    'last_station_end_work': '23:59',
                    'last_station_start_work': '0:00',
                },
            },
            'title': {
                'key': 'market_express.delivery_finished.title',
                'keyset': 'cargo_notify',
                'locale': 'ru',
                'args': {
                    'corp_client_name': 'Рога и Копыта',
                    'sharing_url': 'http://host/sharing_key_1',
                    'corp_client_name_ru_genitive': 'Рога и Копыта',
                    'external_order_id': '32779352',
                    'last_station_end_work': '23:59',
                    'last_station_start_work': '0:00',
                },
            },
        }
    )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_c2c_lp_order_notify_tanker_keys',
    consumers=['cargo-c2c/lp_order'],
    clauses=[],
    default_value={
        'tanker_keys_by_args': [
            {
                'required_args': ['corp_client_name'],
                'intent': 'market_express_new_order',
                'sms_tanker_keys': {
                    'text': {
                        'key': 'market_express.new_order.sms',
                        'keyset': 'cargo_notify',
                    },
                },
            },
        ],
    },
    is_config=True,
)
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_C2C_LP_SETTINGS=CARGO_C2C_LP_SETTINGS,
    CARGO_SMS_SENDER_BY_COUNTRY={'rus': 'go'},
)
async def test_logistic_platform_sms(
        create_logistic_platform_orders,
        get_default_order_id,
        mock_logistic_platform,
        mock_order_statuses_history,
        stq,
        stq_runner,
        taxi_cargo_c2c,
):
    mock_logistic_platform.file_name = 'order_created.json'
    mock_order_statuses_history.file_name = 'order_created.json'

    await taxi_cargo_c2c.post(
        '/v1/processing/logistic-platform/process-event',
        json={'request_id': get_default_order_id(), 'status': ''},
    )

    result = stq['cargo_c2c_send_notification'].next_call()['kwargs']
    assert result['sms_content'] == {
        'text': {
            'key': 'market_express.new_order.sms',
            'keyset': 'cargo_notify',
            'locale': 'ru',
            'args': {
                'corp_client_name': 'Рога и Копыта',
                'sharing_url': 'http://host/sharing_key_1',
                'corp_client_name_ru_genitive': 'Рога и Копыта',
                'external_order_id': '32779352',
                'last_station_end_work': '23:59',
                'last_station_start_work': '0:00',
            },
        },
    }

    assert result['sender'] == 'go'


@pytest.mark.parametrize(
    'has_lock, testpoint_times_called', [(True, 0), (False, 1)],
)
@pytest.mark.config(CARGO_C2C_LP_SETTINGS=CARGO_C2C_LP_SETTINGS)
async def test_logistic_platform_pushes_processing_lock(
        create_logistic_platform_orders,
        get_default_order_id,
        mock_logistic_platform,
        mock_order_statuses_history,
        stq_runner,
        pgsql,
        testpoint,
        has_lock,
        testpoint_times_called,
        taxi_cargo_c2c,
):
    @testpoint('got_lp_status_history_db_lock')
    def got_lp_status_history_db_lock(data):
        pass

    mock_logistic_platform.file_name = 'order_created.json'
    mock_order_statuses_history.file_name = 'order_created.json'

    connection = pgsql['cargo_c2c'].conn
    connection.autocommit = False

    # lock on order
    locked_order_id = (
        get_default_order_id() if has_lock else 'unknown_order_id'
    )
    connection.cursor().execute(
        f"""
        INSERT INTO cargo_c2c.lp_status_history(
            order_id,
            last_status_id
        )
        VALUES (
            '{locked_order_id}',
            1
        )
        ON CONFLICT (order_id)
        DO UPDATE SET last_status_id = 1
        RETURNING (
            SELECT last_status_id
            FROM cargo_c2c.lp_status_history
            WHERE order_id = '{locked_order_id}') AS old_last_status_id;
        """,
    )

    await taxi_cargo_c2c.post(
        '/v1/processing/logistic-platform/process-event',
        json={'request_id': get_default_order_id(), 'status': ''},
    )
    assert got_lp_status_history_db_lock.times_called == testpoint_times_called

    connection.rollback()
    connection.close()


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_c2c_control_logistic_platform_orders_creation',
    consumers=['cargo-c2c/logistic_platform_processing'],
    clauses=[],
    default_value={
        'enabled': True,
        'allowed_roles': ['initiator', 'sender', 'recipient'],
    },
    is_config=True,
)
@pytest.mark.config(
    CARGO_C2C_LP_SETTINGS={
        **CARGO_C2C_LP_SETTINGS,
        **{'c2c_settings': {'employer': 'beru'}},
    },
)
async def test_c2c_order_created(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        mock_logistic_platform,
        mock_order_statuses_history,
        stq_runner,
        mockserver,
        order_processing_order_create_requested,
        save_client_order,
        stq,
        mock_c2c_save,
):
    expected_order_id = '32779352'

    mock_c2c_save.empty_orders_on_first_call = True
    mock_c2c_save.expected_order_id = expected_order_id

    mock_logistic_platform.file_name = 'order_created.json'
    mock_order_statuses_history.file_name = 'order_created.json'
    await taxi_cargo_c2c.post(
        '/v1/processing/logistic-platform/process-event',
        json={'request_id': get_default_order_id(), 'status': ''},
    )

    assert order_processing_order_create_requested.next_call() == {
        'arg': {
            'data': {
                'order_id': expected_order_id,
                'order_provider_id': 'logistic-platform-c2c',
                'phone_pd_id': '+70000000002_id',
                'roles': ['sender'],
            },
            'kind': 'order-create-requested',
            'trait': 'is-create',
        },
    }
    assert order_processing_order_create_requested.next_call() == {
        'arg': {
            'data': {
                'order_id': expected_order_id,
                'order_provider_id': 'logistic-platform-c2c',
                'phone_pd_id': '+71111111111_id',
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
                        'order_id': expected_order_id,
                        'order_provider_id': 'logistic-platform-c2c',
                        'phone_pd_id': '+70000000002_id',
                    },
                    'roles': ['sender'],
                },
                {
                    'id': {
                        'order_id': expected_order_id,
                        'order_provider_id': 'logistic-platform-c2c',
                        'phone_pd_id': '+71111111111_id',
                    },
                    'roles': ['recipient'],
                },
            ],
        },
    }
