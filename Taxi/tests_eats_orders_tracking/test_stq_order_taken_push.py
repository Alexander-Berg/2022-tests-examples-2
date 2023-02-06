# pylint: disable=too-many-lines

import pytest

PERSONAL_PHONE_ID = '123456789'

ORDER_TAKEN_ENABLED = pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='eats_orders_tracking_order_taken_push',
    consumers=['eats-orders-tracking/order-taken-push'],
    clauses=[],
    default_value=dict({'enabled': True}),
)


def make_config_stq_retry(
        max_exec_tries, max_reschedule_counter, reschedule_seconds,
):
    return {
        'stq_order_taken_push': {
            'max_exec_tries': max_exec_tries,
            'max_reschedule_counter': max_reschedule_counter,
            'reschedule_seconds': reschedule_seconds,
        },
        'stq_couriers': {
            'max_exec_tries': 10,
            'max_reschedule_counter': 10,
            'reschedule_seconds': 10,
        },
        'stq_orders_eta': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
        'stq_orders': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
        'stq_cargo_waybill_changes': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
        'stq_picker_orders': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
        'stq_order_to_another_eater_sms': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
    }


def get_stq_orders_kwargs(
        order_nr,
        place_id,
        eater_id,
        event_time=16107965710948,
        updated_at='2020-10-28T18:26:43.51+00:00',
        raw_status='1',
        cancel_reason='duplicate',
):
    date = '2020-10-20T12:00:00+00:00'

    kwargs = {
        'event_time': event_time,
        'order': {
            'order_nr': order_nr,
            'place_id': place_id,
            'eater_id': eater_id,
            'status': raw_status,
            'status_detail': {'id': 1, 'date': date},
            'promise': date,
            'location': {'latitude': 30.12, 'longitude': 30.34},
            'is_asap': False,
            'type': 'retail',
            'delivery_type': 'native',
            'shipping_type': 'delivery',
            'created_at': date,
            'updated_at': updated_at,
            'service': 'grocery',
            'client_app': 'native',
            'status_history': {},
            'changes_state': {'applicable_until': date},
            'region': {
                'name': 'Москва',
                'code': 'moscow',
                'timezone': 'Europe/Moscow',
                'country_code': 'RU',
            },
            'pre_order_date': date,
            'cancel_reason': cancel_reason,
            'payment_method': 'taxi',
            'is_second_batch_delivery': True,
            'short_order_nr': '000000-111-6543',
            'personal_phone_id': PERSONAL_PHONE_ID,
            'delivery_class': 'regular',
        },
    }

    return kwargs


def make_order_json_in_db(kwargs):
    order = kwargs['order'].copy()
    del order['order_nr']
    del order['eater_id']

    order['raw_type'] = kwargs['order']['type']
    order['raw_delivery_type'] = kwargs['order']['delivery_type']
    order['raw_shipping_type'] = kwargs['order']['shipping_type']
    order['raw_cancel_reason'] = kwargs['order']['cancel_reason']
    order['cancel_reason'] = kwargs['order']['cancel_reason']
    order['raw_payment_method'] = kwargs['order']['payment_method']
    order['payment_method'] = 'taxi'
    order['is_second_batch_delivery'] = True

    raw_status = kwargs['order']['status']
    order['raw_status'] = raw_status
    if raw_status == '1':
        order['status'] = 'call_center_confirmed'
    elif raw_status == '4':
        order['status'] = 'delivered'
    elif raw_status == '5':
        order['status'] = 'cancelled'
    elif raw_status == '9':
        order['status'] = 'order_taken'
    else:
        assert False

    return order


@pytest.fixture(name='mock_eats_eta_orders_estimate')
def _mock_eats_eta_orders_estimate(mockserver, load_json):
    @mockserver.json_handler('/eats-eta/v1/eta/orders/estimate')
    def _handler(request):
        mock_response = {
            'orders': [
                {
                    'order_nr': '000000-000000',
                    'estimations': [
                        {
                            'name': 'courier_arrival_at',
                            'calculated_at': '2020-10-28T18:12:00.00+00:00',
                            'status': 'in_progress',
                        },
                        {
                            'name': 'delivery_at',
                            'calculated_at': '2020-10-28T18:12:00.00+00:00',
                            'expected_at': '2020-10-28T18:32:00.00+00:00',
                        },
                    ],
                },
            ],
            'not_found_orders': ['000000-000002'],
        }
        return mockserver.make_response(json=mock_response, status=200)

    return _handler


@pytest.fixture(name='mock_eats_notifications')
def _mock_eats_notifications(mockserver, load_json):
    @mockserver.json_handler('/eats-notifications/v1/notification')
    def _mock_eda_eats_notifications_(request):
        return mockserver.make_response(status=204)

    return _mock_eda_eats_notifications_


async def test_stq_order_taken_from_stq_orders(
        stq_runner, stq, mock_storage_search_places,
):
    kwargs_value = get_stq_orders_kwargs(
        order_nr='000000-000001', place_id='40', eater_id='1', raw_status='9',
    )
    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )

    assert stq.eats_orders_tracking_order_taken_push.times_called == 1


@pytest.mark.pgsql('eats_orders_tracking', files=['fill_order_payload.sql'])
async def test_stq_order_taken_push_finished_order(
        stq_runner,
        stq,
        mock_eats_eta_orders_estimate,
        mock_eats_notifications,
        load_json,
):
    await stq_runner.eats_orders_tracking_order_taken_push.call(
        task_id='sample_task',
        kwargs={'order_nr': '000000-000001'},
        expect_fail=False,
    )

    assert mock_eats_eta_orders_estimate.times_called == 0
    assert mock_eats_notifications.times_called == 0


async def test_stq_order_taken_push_no_courier(
        stq_runner,
        stq,
        mock_eats_eta_orders_estimate,
        mock_eats_notifications,
        load_json,
):
    await stq_runner.eats_orders_tracking_order_taken_push.call(
        task_id='sample_task',
        kwargs={'order_nr': '000000-000002'},
        expect_fail=False,
    )

    assert mock_eats_eta_orders_estimate.times_called == 0
    assert mock_eats_notifications.times_called == 0


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': False,
        'is_endpoint_claims_performer_position_enabled': False,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'use_to_show',
    },
)
@ORDER_TAKEN_ENABLED
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_order_payload.sql'])
async def test_stq_order_taken_push_need_configurate_push(
        stq_runner, stq, mock_eats_eta_orders_estimate, load_json, mockserver,
):
    @mockserver.json_handler('/eats-notifications/v1/notification')
    def _mock_eats_notifications(request):
        assert (
            request.headers['X-Idempotency-Token']
            == 'eats_orders_tracking.order_taken_push_notification'
            '.000000-000000'
        )
        return mockserver.make_response(status=204)

    await stq_runner.eats_orders_tracking_order_taken_push.call(
        task_id='sample_task',
        kwargs={'order_nr': '000000-000000'},
        expect_fail=False,
    )

    assert mock_eats_eta_orders_estimate.times_called == 1
    assert _mock_eats_notifications.times_called == 1


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': False,
        'is_endpoint_claims_performer_position_enabled': False,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'use_to_show',
    },
)
@ORDER_TAKEN_ENABLED
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_order_payload.sql'])
@pytest.mark.config(
    EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry(
        max_exec_tries=10, max_reschedule_counter=10, reschedule_seconds=0,
    ),
)
async def test_stq_order_taken_push_notifications_failed(
        stq_runner, stq, mock_eats_eta_orders_estimate, mockserver,
):
    @mockserver.json_handler('/eats-notifications/v1/notification')
    def _mock_eats_notifications(request):
        assert (
            request.headers['X-Idempotency-Token']
            == 'eats_orders_tracking.order_taken_push_notification'
            '.000000-000000'
        )
        return mockserver.make_response(
            status=400,
            json={
                'code': 'INVALID_OPERATION',
                'message': 'Something happening',
            },
        )

    await stq_runner.eats_orders_tracking_order_taken_push.call(
        task_id='sample_task',
        kwargs={'order_nr': '000000-000000'},
        expect_fail=True,
    )

    assert mock_eats_eta_orders_estimate.times_called == 1
    assert _mock_eats_notifications.times_called == 1


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': False,
        'is_endpoint_claims_performer_position_enabled': False,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'use_to_show',
    },
)
@ORDER_TAKEN_ENABLED
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_order_payload.sql'])
async def test_stq_order_taken_not_mobile_application(
        stq_runner,
        stq,
        mock_eats_eta_orders_estimate,
        mock_eats_notifications,
):

    await stq_runner.eats_orders_tracking_order_taken_push.call(
        task_id='sample_task',
        kwargs={'order_nr': '000000-000003'},
        expect_fail=False,
    )

    assert mock_eats_eta_orders_estimate.times_called == 0
    assert mock_eats_notifications.times_called == 0


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': False,
        'is_endpoint_claims_performer_position_enabled': False,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'use_to_show',
    },
)
@ORDER_TAKEN_ENABLED
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_order_payload.sql'])
async def test_stq_order_taken_go_application_greenflow(
        stq_runner, stq, mock_eats_eta_orders_estimate, mockserver,
):
    @mockserver.json_handler('/eats-notifications/v1/notification')
    def _mock_eats_notifications(request):
        assert (
            request.headers['X-Idempotency-Token']
            == 'eats_orders_tracking.order_taken_push_notification'
            '.000000-000004'
        )
        assert request.json['options_values']['order_nr'] == '000000-000004'
        return mockserver.make_response(
            status=200, json={'token': 'some_token'},
        )

    await stq_runner.eats_orders_tracking_order_taken_push.call(
        task_id='sample_task',
        kwargs={'order_nr': '000000-000004'},
        expect_fail=False,
    )

    assert mock_eats_eta_orders_estimate.times_called == 1
    assert _mock_eats_notifications.times_called == 1


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': False,
        'is_endpoint_claims_performer_position_enabled': False,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'use_to_show',
    },
)
@ORDER_TAKEN_ENABLED
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_order_payload.sql'])
async def test_stq_order_taken_lavka_webview_application_greenflow(
        stq_runner, stq, mock_eats_eta_orders_estimate, mockserver,
):
    @mockserver.json_handler('/eats-notifications/v1/notification')
    def _mock_eats_notifications(request):
        assert (
            request.headers['X-Idempotency-Token']
            == 'eats_orders_tracking.order_taken_push_notification'
            '.000000-000005'
        )
        assert request.json['options_values']['order_nr'] == '000000-000005'
        # device_id is have to be null
        assert 'device_id' not in request.json['options_values']
        return mockserver.make_response(
            status=200, json={'token': 'some_token'},
        )

    await stq_runner.eats_orders_tracking_order_taken_push.call(
        task_id='sample_task',
        kwargs={'order_nr': '000000-000005'},
        expect_fail=False,
    )

    assert mock_eats_eta_orders_estimate.times_called == 1
    assert _mock_eats_notifications.times_called == 1


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': False,
        'is_endpoint_claims_performer_position_enabled': False,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'use_to_show',
    },
)
@ORDER_TAKEN_ENABLED
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_order_payload.sql'])
async def test_stq_order_taken_greenflow(
        stq_runner, stq, mock_eats_eta_orders_estimate, mockserver,
):
    @mockserver.json_handler('/eats-notifications/v1/notification')
    def _mock_eats_notifications(request):
        assert (
            request.headers['X-Idempotency-Token']
            == 'eats_orders_tracking.order_taken_push_notification'
            '.000000-000000'
        )
        assert request.json['options_values']['order_nr'] == '000000-000000'
        return mockserver.make_response(
            status=200, json={'token': 'some_token'},
        )

    await stq_runner.eats_orders_tracking_order_taken_push.call(
        task_id='sample_task',
        kwargs={'order_nr': '000000-000000'},
        expect_fail=False,
    )

    assert mock_eats_eta_orders_estimate.times_called == 1
    assert _mock_eats_notifications.times_called == 1


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': False,
        'is_endpoint_claims_performer_position_enabled': False,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'use_to_show',
    },
)
@ORDER_TAKEN_ENABLED
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_order_payload.sql'])
async def test_stq_order_taken_empty_car_info(
        stq_runner, stq, mock_eats_eta_orders_estimate, mockserver,
):
    @mockserver.json_handler('/eats-notifications/v1/notification')
    def _mock_eats_notifications(request):
        assert (
            request.headers['X-Idempotency-Token']
            == 'eats_orders_tracking.order_taken_push_notification'
            '.000000-000006'
        )
        assert request.json['options_values']['order_nr'] == '000000-000006'
        assert not request.json['options_values']['is_car_courier']
        return mockserver.make_response(
            status=200, json={'token': 'some_token'},
        )

    await stq_runner.eats_orders_tracking_order_taken_push.call(
        task_id='sample_task',
        # empty car info = no vehicle courier
        kwargs={'order_nr': '000000-000006'},
        expect_fail=False,
    )

    assert mock_eats_eta_orders_estimate.times_called == 1
    assert _mock_eats_notifications.times_called == 1


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': False,
        'is_endpoint_claims_performer_position_enabled': False,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'use_to_show',
    },
)
@ORDER_TAKEN_ENABLED
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_order_payload.sql'])
@pytest.mark.pgsql(
    'eats_orders_tracking',
    queries=[
        'insert into eats_orders_tracking.idempotency_keys (idempotency_key)'
        'values ('
        '\'eats_orders_tracking.order_taken_push_notification.000000-000006\''
        ')',
    ],
)
async def test_stq_order_taken_idempotency_key_duplicated(
        stq_runner,
        stq,
        mock_eats_eta_orders_estimate,
        mock_eats_notifications,
):

    await stq_runner.eats_orders_tracking_order_taken_push.call(
        task_id='sample_task',
        kwargs={'order_nr': '000000-000006'},
        expect_fail=False,
    )

    assert stq.eats_orders_tracking_order_taken_push.times_called == 0
    assert mock_eats_notifications.times_called == 0
