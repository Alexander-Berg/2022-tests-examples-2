import datetime

import pytest

from . import utils


KWARGS = {
    'notification_type': 'first_retail_order_changes',
    'idempotency_token': 'idempotency_token_0',
    'time': '2021-09-30T20:00:00+00:00',
    'level': 'INFO',
    'order_nr': utils.ORDER_ID,
    'retail_order_changes': {
        'add': [
            {'id': '0', 'name': 'Креветки'},
            {'id': '1', 'name': 'Черная икра'},
        ],
        'remove': [
            {'id': '2', 'name': 'Шоколадная медаль'},
            {'id': '3', 'name': 'Колбаса'},
        ],
        'update_count': [
            {'id': '4', 'name': 'Фугу', 'old_count': 1, 'new_count': 2},
        ],
        'update_weight': [
            {
                'id': '5',
                'name': 'Мармелад',
                'old_weight': {
                    'value': 100,
                    'measure_unit': {'code': 'GRM', 'sign': 'г'},
                },
                'new_weight': {
                    'value': 200,
                    'measure_unit': {'code': 'GRM', 'sign': 'г'},
                },
            },
        ],
    },
    'total_cost_for_customer': {'currency_sign': 'RUB', 'value': '42.64'},
}

EATS_NOTIFICATIONS_APPLICATIONS_CONFIG = {
    'eda_native': {
        'aliases': ['eda_native'],
        'settings': {'route': 'eda', 'service': 'eda-client'},
        'type': 'xiva',
        'user_identity_name': 'eater_id',
    },
    'go': {
        'aliases': ['go', 'go_alias'],
        'settings': {'route': 'eda', 'service': 'eda-client'},
        'type': 'xiva',
        'user_identity_name': 'taxi_user_id',
    },
}

NOTIFICATION_TYPE_TRANSFORMATION = {
    'total_cost_for_customer': 'order_in_delivery',
}


@utils.notifications_config3()
@pytest.mark.now('2021-09-30T20:00:00+00:00')
@pytest.mark.parametrize(
    'notification_type, config_key',
    [
        ('first_retail_order_changes', 'retail_order_changes'),
        ('order_in_delivery', 'total_cost_for_customer'),
        ('total_cost_for_customer', 'total_cost_for_customer'),
    ],
)
@pytest.mark.parametrize('is_notification_exist', [False, True])
async def test_stq_notify_customer(
        stq_runner,
        create_order,
        create_customer_notification,
        environment,
        get_order,
        get_notification,
        notification_type,
        config_key,
        is_notification_exist,
):
    environment.set_default()
    notification_type_transformed = NOTIFICATION_TYPE_TRANSFORMATION.get(
        notification_type, notification_type,
    )
    order_id = create_order(
        status_for_customer='in_delivery',
        picking_status='complete',
        application='eda_native',
        place_id=utils.PLACE_ID,
        brand_id=utils.BRAND_ID,
        customer_id=utils.CUSTOMER_ID,
        yandex_uid=utils.YANDEX_UID,
        personal_phone_id=utils.PERSONAL_PHONE_ID,
    )
    kwargs = dict(KWARGS, notification_type=notification_type)
    if is_notification_exist:
        create_customer_notification(
            notification_type_v2=notification_type_transformed,
            idempotency_token=kwargs['idempotency_token'],
        )
    config = utils.NOTIFICATIONS_CONFIG_ALL_ENABLED[
        notification_type_transformed
    ]

    await stq_runner.eats_retail_order_history_notify_customer.call(
        task_id='uuid', kwargs=kwargs,
    )

    order = get_order(order_id)

    assert environment.mock_eats_notification_notify.times_called == (
        not is_notification_exist
    )

    if is_notification_exist:
        return

    args = environment.mock_eats_notification_notify.next_call()[
        'request'
    ].json
    assert args['project'] == config['project']
    assert args['notification_key'] == config['notification_key']
    assert args['application'] == order['application']
    assert args['user_id'] == order['customer_id']
    assert args['locale'] == 'ru'
    assert args['user_type'] == 'eater_id'

    notification = get_notification(kwargs['idempotency_token'])
    if config_key == 'first_retail_order_changes':
        assert args['options_values'] == {'order.orderNr': utils.ORDER_ID}
        assert (
            notification['events'] == '{add,remove,update_count,update_weight}'
        )
    elif config_key == 'total_cost_for_customer':
        assert args['options_values'] == {
            'order.orderNr': utils.ORDER_ID,
            'currencySymbol': kwargs[config_key]['currency_sign'],
            'price': kwargs[config_key]['value'],
        }
        assert notification['events'] is None

    assert notification['order_nr'] == kwargs['order_nr']
    assert kwargs['notification_type'] == notification_type
    assert notification['notification_type'] is None
    assert (
        notification['notification_type_v2'] == notification_type_transformed
    )
    assert notification['idempotency_token'] == kwargs['idempotency_token']
    assert notification['status_for_customer'] == order['status_for_customer']
    assert notification['picking_status'] == order['picking_status']
    assert notification['customer_id'] == order['customer_id']
    assert notification['notification_key'] == config['notification_key']
    assert notification['project'] == config['project']
    assert notification['application'] == order['application']
    assert notification['token'] == 'notification_token_0'


async def test_stq_notify_customer_no_config(stq_runner, environment):
    environment.set_default()
    await stq_runner.eats_retail_order_history_notify_customer.call(
        task_id='uuid', kwargs=KWARGS,
    )
    assert not environment.mock_eats_notification_notify.has_calls


@pytest.mark.config(
    EATS_NOTIFICATIONS_APPLICATIONS_V2=EATS_NOTIFICATIONS_APPLICATIONS_CONFIG,
)
@pytest.mark.now('2021-09-30T20:00:00+00:00')
@utils.notifications_config3()
@pytest.mark.parametrize(
    'application, has_calls_by_app',
    [('go', True), ('eda_native', True), ('web', False)],
)
@pytest.mark.parametrize(
    'place_id, has_calls_by_place_id',
    [(utils.PLACE_ID, True), ('unknown_place_id', False), (None, False)],
)
@pytest.mark.parametrize(
    'brand_id, has_calls_by_brand_id',
    [(int(utils.BRAND_ID), True), (666, False), (None, False)],
)
@pytest.mark.parametrize(
    'eater_id, has_calls_by_eater_id',
    [(utils.CUSTOMER_ID, True), ('unknown_customer_id', False)],
)
@pytest.mark.parametrize(
    'eater_passport_id, has_calls_by_eater_passport_id',
    [(utils.YANDEX_UID, True), ('unknown_yandex_uid', False)],
)
@pytest.mark.parametrize(
    'eater_personal_phone_id, has_calls_by_eater_personal_phone_id',
    [
        (utils.PERSONAL_PHONE_ID, True),
        ('unknown_personal_phone_id', False),
        (None, False),
    ],
)
async def test_stq_notify_customer_config_kwargs(
        stq_runner,
        environment,
        create_order,
        now,
        application,
        has_calls_by_app,
        place_id,
        has_calls_by_place_id,
        brand_id,
        has_calls_by_brand_id,
        eater_id,
        has_calls_by_eater_id,
        eater_passport_id,
        has_calls_by_eater_passport_id,
        eater_personal_phone_id,
        has_calls_by_eater_personal_phone_id,
):
    now = now.replace(tzinfo=datetime.timezone.utc)
    environment.set_default()
    create_order(
        status_for_customer='in_delivery',
        picking_status='complete',
        application=application,
        place_id=place_id,
        brand_id=brand_id,
        customer_id=eater_id,
        yandex_uid=eater_passport_id,
        personal_phone_id=eater_personal_phone_id,
    )
    await stq_runner.eats_retail_order_history_notify_customer.call(
        task_id='uuid', kwargs=KWARGS,
    )
    assert environment.mock_eats_notification_notify.has_calls == (
        has_calls_by_app
        and has_calls_by_place_id
        and has_calls_by_brand_id
        and has_calls_by_eater_id
        and has_calls_by_eater_passport_id
        and has_calls_by_eater_personal_phone_id
    )


@pytest.mark.config(
    EATS_NOTIFICATIONS_APPLICATIONS_V2=EATS_NOTIFICATIONS_APPLICATIONS_CONFIG,
)
@pytest.mark.now('2021-09-30T20:00:00+00:00')
@utils.notifications_config3()
@pytest.mark.parametrize(
    'application, has_calls_by_app', [('go', True), ('go_alias', True)],
)
@pytest.mark.parametrize(
    'place_id, has_calls_by_place_id',
    [(utils.PLACE_ID, True), ('unknown_place_id', False), (None, False)],
)
@pytest.mark.parametrize(
    'brand_id, has_calls_by_brand_id',
    [(int(utils.BRAND_ID), True), (666, False), (None, False)],
)
@pytest.mark.parametrize(
    'eater_id, has_calls_by_eater_id',
    [(utils.CUSTOMER_ID, True), ('unknown_customer_id', False)],
)
@pytest.mark.parametrize(
    'eater_passport_id, has_calls_by_eater_passport_id',
    [(utils.YANDEX_UID, True), ('unknown_yandex_uid', False)],
)
@pytest.mark.parametrize(
    'taxi_user_id, has_calls_by_taxi_user',
    [(utils.TAXI_USER_ID, True), (None, False)],
)
@pytest.mark.parametrize(
    'eater_personal_phone_id, has_calls_by_eater_personal_phone_id',
    [
        (utils.PERSONAL_PHONE_ID, True),
        ('unknown_personal_phone_id', False),
        (None, False),
    ],
)
async def test_stq_notify_customer_kwargs_go(
        stq_runner,
        environment,
        create_order,
        now,
        application,
        has_calls_by_app,
        taxi_user_id,
        has_calls_by_taxi_user,
        place_id,
        has_calls_by_place_id,
        brand_id,
        has_calls_by_brand_id,
        eater_id,
        has_calls_by_eater_id,
        eater_passport_id,
        has_calls_by_eater_passport_id,
        eater_personal_phone_id,
        has_calls_by_eater_personal_phone_id,
):
    now = now.replace(tzinfo=datetime.timezone.utc)
    environment.set_default()
    create_order(
        status_for_customer='in_delivery',
        picking_status='complete',
        application=application,
        place_id=place_id,
        brand_id=brand_id,
        customer_id=eater_id,
        yandex_uid=eater_passport_id,
        taxi_user_id=taxi_user_id,
        personal_phone_id=eater_personal_phone_id,
    )
    await stq_runner.eats_retail_order_history_notify_customer.call(
        task_id='uuid', kwargs=KWARGS,
    )
    assert environment.mock_eats_notification_notify.has_calls == (
        has_calls_by_app
        and has_calls_by_place_id
        and has_calls_by_brand_id
        and has_calls_by_eater_id
        and has_calls_by_eater_passport_id
        and has_calls_by_taxi_user
        and has_calls_by_eater_personal_phone_id
    )


@utils.notifications_config3(**utils.NOTIFICATIONS_CONFIG_ALL_DISABLED)
@pytest.mark.now('2021-09-30T20:00:00+00:00')
async def test_stq_notify_customer_all_disabled(
        stq_runner, environment, create_order,
):
    environment.set_default()
    create_order()
    await stq_runner.eats_retail_order_history_notify_customer.call(
        task_id='uuid', kwargs=KWARGS,
    )
    assert not environment.mock_eats_notification_notify.has_calls


@pytest.mark.now('2021-09-30T20:00:00+00:00')
@utils.notifications_config3()
@pytest.mark.parametrize(
    'picking_status, time_offset, do_reschedule',
    [
        (None, 0, False),
        ('picking', 0, True),
        ('picked_up', 0, True),
        ('picking', 240, True),
        ('picking', 360, False),
        ('complete', 0, False),
    ],
)
async def test_stq_notify_customer_order_in_delivery_reschedule(
        mockserver,
        stq_runner,
        now,
        create_order,
        environment,
        picking_status,
        time_offset,
        do_reschedule,
):
    environment.set_default()
    now = now.replace(tzinfo=datetime.timezone.utc)
    create_order(
        status_for_customer='in_delivery',
        picking_status=picking_status,
        application='eda_native',
        place_id=utils.PLACE_ID,
        brand_id=utils.BRAND_ID,
        customer_id=utils.CUSTOMER_ID,
        yandex_uid=utils.YANDEX_UID,
        personal_phone_id=utils.PERSONAL_PHONE_ID,
        our_picking=(picking_status is not None),
    )
    notification_type = 'order_in_delivery'

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _mock_stq_reschedule(request):
        return {}

    kwargs = dict(
        KWARGS,
        notification_type=notification_type,
        time=(now - datetime.timedelta(seconds=time_offset)).isoformat(),
    )
    await stq_runner.eats_retail_order_history_notify_customer.call(
        task_id='uuid', kwargs=kwargs,
    )

    assert _mock_stq_reschedule.times_called == int(do_reschedule)
