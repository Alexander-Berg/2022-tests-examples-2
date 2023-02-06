import copy
import datetime
import uuid

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from . import consts
from . import headers
from . import models


def _metric(name):
    return f'grocery_orders_{name}'


FINISH_METRIC = _metric('order_is_finished')
FINISH_METRIC_BY_COUNTRY = _metric('order_is_finished_by_country')
ORDER_SUBMIT_BAD_REQUEST_METRIC = _metric('order_submit_bad_request')
FINISH_METRIC_BY_SHELF_TYPE = _metric('finish_status_by_shelf_type')
FINISH_METRIC_BY_DELIVERY_TYPE = _metric('finish_status_by_delivery_type')
CANCEL_REASONS = _metric('cancel_reasons')
CANCEL_REASONS_WITHOUT_MESSAGE = _metric('cancel_reasons_by_type')
ORDER_CANCEL_USER_ADMIN = _metric('order_cancel_user_admin')
ORDER_CANCEL_ORDER_CYCLE = _metric('order_cancel_order_cycle')
ORDER_CANCEL_PAYMENT_FAIL = _metric('order_cancel_payment_fail')
CTE_PERCENTILE = _metric('cte_percentile')
ORDER_INFLIGHT = _metric('order_inflight')
ORDER_CREATED = _metric('order_created')
ORDER_DELIVERED = _metric('order_delivered')

YANGO_PRETTY_NAME = 'Yango (android)'

CART_ID = '00000000-0000-0000-0000-d98013100500'
OFFER_ID = 'offer-id'
CART_VERSION = 4
LOCATION_IN_RUSSIA = [37.62, 55.75]
PLACE_ID = 'yamaps://12345'
FLOOR = '13'
FLAT = '666'
DOORCODE = '42'
DOORCODE_EXTRA = 'doorcode_extra'
BUILDING_NAME = 'building_name'
DOORBELL_NAME = 'doorbell_name'
LEFT_AT_DOOR = False
COMMENT = 'comment'
DEPOT_ID = '2809'
ENTRANCE = '3333'

PROCESSING_FLOW_VERSION = 'grocery_flow_v1'

SUBMIT_BODY = {
    'cart_id': CART_ID,
    'cart_version': CART_VERSION,
    'offer_id': OFFER_ID,
    'position': {
        'location': LOCATION_IN_RUSSIA,
        'place_id': PLACE_ID,
        'floor': FLOOR,
        'flat': FLAT,
        'doorcode': DOORCODE,
        'doorcode_extra': DOORCODE_EXTRA,
        'building_name': BUILDING_NAME,
        'doorbell_name': DOORBELL_NAME,
        'left_at_door': LEFT_AT_DOOR,
        'comment': COMMENT,
        'entrance': ENTRANCE,
    },
    'flow_version': PROCESSING_FLOW_VERSION,
    'payment_method_type': 'card',
    'payment_method_id': 'card-x123',
}


@pytest.fixture(name='create_order')
def _create_order(pgsql, grocery_depots, grocery_cart):
    async def _do(
            status='closed',
            country: models.Country = models.Country.Russia,
            region_id=213,
            delivery_type='courier',
            cancel_reason_message=None,
            cancel_reason_type=None,
            created=models.DEFAULT_CREATED,
    ):
        orderstate = models.OrderState()
        orderstate.close_money_status = 'success'
        order = models.Order(
            pgsql=pgsql,
            status=status,
            cancel_reason_message=cancel_reason_message,
            cancel_reason_type=cancel_reason_type,
            state=orderstate,
            app_info=headers.APP_INFO,
            created=created,
        )
        grocery_depots.add_depot(
            legacy_depot_id=order.depot_id,
            country_iso3=country.country_iso3,
            region_id=region_id,
        )
        grocery_cart.set_cart_data(cart_id=order.cart_id)
        grocery_cart.set_delivery_type(delivery_type)

        return order

    return _do


@pytest.fixture(name='run_finish')
def _run_finish(taxi_grocery_orders):
    async def _run(order_id: str):
        await taxi_grocery_orders.post(
            '/processing/v1/finish',
            json={'order_id': order_id, 'payload': {}},
        )

    return _run


@pytest.fixture(name='run_submit')
def _run_submit(taxi_grocery_orders):
    async def _run():
        response = await taxi_grocery_orders.post(
            '/lavka/v1/orders/v2/submit',
            json=SUBMIT_BODY,
            headers=headers.DEFAULT_HEADERS,
        )
        body = response.json()

        return body['order_id'] if 'order_id' in body else None

    return _run


@pytest.fixture(name='run_submit_v1')
def _run_submit_v1(taxi_grocery_orders, eats_core_eater):
    async def _run():
        eats_core_eater.set_personal_email_id('email')

        body = copy.deepcopy(SUBMIT_BODY)
        body['flow_version'] = 'eats_payments'

        response = await taxi_grocery_orders.post(
            '/lavka/v1/orders/v1/submit',
            json=body,
            headers=headers.DEFAULT_HEADERS,
        )
        assert response.status_code == 200

    return _run


def get_new_uuid():
    return str(uuid.uuid4())


@pytest.mark.parametrize('status', ['closed', 'canceled'])
@pytest.mark.parametrize(
    'country, region_id, city_name',
    [
        (models.Country.Russia, 213, 'Moscow'),
        (models.Country.Israel, 131, 'Tel Aviv'),
    ],
)
async def test_order_is_finished_metric(
        run_finish,
        create_order,
        taxi_grocery_orders_monitor,
        status,
        country,
        region_id,
        city_name,
):
    order = await create_order(
        status=status, country=country, region_id=region_id,
    )

    metric_status = _get_status(status)

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_orders_monitor,
            sensor=FINISH_METRIC,
            labels={'country': country.name, 'status': metric_status},
    ) as collector:
        await run_finish(order.order_id)

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'country': country.name,
        'region_id': str(region_id),
        'app_name': YANGO_PRETTY_NAME,
        'sensor': FINISH_METRIC,
        'status': metric_status,
        'city_name': city_name,
    }


@pytest.mark.parametrize('status', ['closed', 'canceled'])
@pytest.mark.parametrize(
    'country', [models.Country.Russia, models.Country.Israel],
)
async def test_order_is_finished_metric_by_country(
        run_finish, create_order, taxi_grocery_orders_monitor, status, country,
):
    order = await create_order(status=status, country=country)

    metric_status = _get_status(status)

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_orders_monitor,
            sensor=FINISH_METRIC_BY_COUNTRY,
            labels={'country': country.name, 'status': metric_status},
    ) as collector:
        await run_finish(order.order_id)

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'country': country.name,
        'sensor': FINISH_METRIC_BY_COUNTRY,
        'status': metric_status,
    }


@pytest.mark.parametrize(
    'country', [models.Country.Russia, models.Country.Israel],
)
async def test_order_created(
        grocery_cart,
        grocery_depots,
        taxi_grocery_orders_monitor,
        run_submit,
        country,
):
    city_name = 'Moscow'
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_depots.add_depot(
        legacy_depot_id=DEPOT_ID, country_iso3=country.country_iso3,
    )
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_orders_monitor,
            sensor=ORDER_CREATED,
            labels={'country': country.name},
    ) as collector:
        await run_submit()

    metric = collector.get_single_collected_metric()

    assert metric.value == 1
    assert metric.labels == {
        'country': country.name,
        'app_name': YANGO_PRETTY_NAME,
        'sensor': ORDER_CREATED,
        'order_cycle': 'grocery',
        'city_name': city_name,
    }


async def test_order_created_eats_cycle(
        grocery_cart,
        grocery_depots,
        taxi_grocery_orders_monitor,
        run_submit_v1,
):
    city_name = 'Moscow'
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_depots.add_depot(legacy_depot_id=DEPOT_ID)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_orders_monitor,
            sensor=ORDER_CREATED,
            labels={'country': models.Country.Russia.name},
    ) as collector:
        await run_submit_v1()

    metric = collector.get_single_collected_metric()

    assert metric.value == 1
    assert metric.labels == {
        'country': models.Country.Russia.name,
        'app_name': YANGO_PRETTY_NAME,
        'sensor': ORDER_CREATED,
        'order_cycle': 'eats',
        'city_name': city_name,
    }


@pytest.mark.parametrize(
    'country', [models.Country.Russia, models.Country.Israel],
)
async def test_order_inflight(
        grocery_cart,
        grocery_depots,
        run_finish,
        taxi_grocery_orders_monitor,
        run_submit,
        country,
):
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_depots.add_depot(
        legacy_depot_id=DEPOT_ID, country_iso3=country.country_iso3,
    )
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_orders_monitor,
            sensor=ORDER_INFLIGHT,
            labels={'country': country.name},
    ) as collector:
        order_id = await run_submit()

    metric = collector.get_single_collected_metric()

    assert metric.value == 1
    assert metric.labels == {
        'country': country.name,
        'app_name': YANGO_PRETTY_NAME,
        'sensor': ORDER_INFLIGHT,
    }

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_orders_monitor,
            sensor=ORDER_INFLIGHT,
            labels={'country': country.name},
    ) as collector:
        await run_finish(order_id)

    metric = collector.get_single_collected_metric()

    assert not metric


async def test_cte_sum(
        taxi_grocery_orders,
        taxi_grocery_orders_monitor,
        pgsql,
        grocery_cart,
        grocery_dispatch,
        processing,
        grocery_depots,
        mocked_time,
):
    grocery_cart.set_delivery_type('courier')
    grocery_depots.add_depot(legacy_depot_id=models.DEFAULT_DEPOT_ID)
    grocery_dispatch.set_data(
        items=grocery_cart.get_items(),
        status='delivered',
        dispatch_id=get_new_uuid(),
        performer_id='123',
        eats_profile_id='101',
        transport_type='rover',
    )
    mocked_time.set(consts.NOW_DT)

    await taxi_grocery_orders.tests_control(reset_metrics=True)

    def _get_new_order_id(delta_minutes):
        created = consts.NOW_DT - datetime.timedelta(minutes=delta_minutes)
        order = models.Order(
            pgsql=pgsql,
            status='closed',
            created=created.isoformat(),
            app_info=headers.APP_INFO,
            dispatch_status_info=models.DispatchStatusInfo(
                dispatch_id=grocery_dispatch.dispatch_id,
                dispatch_status='delivering',
                dispatch_cargo_status='accepted',
            ),
            dispatch_flow='grocery_dispatch',
        )

        grocery_cart.set_cart_data(cart_id=order.cart_id)
        return order.order_id

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_orders_monitor,
            sensor=_metric('cte_sum'),
            labels={'country': models.Country.Russia.name},
    ) as collector:
        iter_count = 10
        for delta_minutes in range(iter_count):
            order_id = _get_new_order_id(delta_minutes)
            grocery_dispatch.set_data(order_id=order_id)

            response = await taxi_grocery_orders.post(
                '/processing/v1/dispatch/track',
                json={'order_id': order_id, 'payload': {}},
            )
            assert response.status_code == 200

    metric = collector.get_single_collected_metric()

    assert metric.labels['sensor'] == _metric('cte_sum')
    assert metric.labels['country'] == models.Country.Russia.name
    assert metric.labels['app_name'] == YANGO_PRETTY_NAME

    assert metric.value == 45


async def test_order_delivered(
        taxi_grocery_orders,
        taxi_grocery_orders_monitor,
        pgsql,
        grocery_cart,
        grocery_dispatch,
        processing,
        grocery_depots,
        mocked_time,
):
    grocery_cart.set_delivery_type('courier')
    grocery_depots.add_depot(legacy_depot_id=models.DEFAULT_DEPOT_ID)
    dispatch_id = get_new_uuid()

    mocked_time.set(consts.NOW_DT)

    await taxi_grocery_orders.tests_control(reset_metrics=True)

    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        app_info=headers.APP_INFO,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status='delivering',
            dispatch_cargo_status='accepted',
        ),
        dispatch_flow='grocery_dispatch',
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_dispatch.set_data(
        order_id=order.order_id,
        items=grocery_cart.get_items(),
        status='delivered',
        dispatch_id=dispatch_id,
        performer_id='123',
        eats_profile_id='101',
        transport_type='rover',
    )

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_orders_monitor,
            sensor=ORDER_DELIVERED,
            labels={'country': models.Country.Russia.name},
    ) as collector:
        response = await taxi_grocery_orders.post(
            '/processing/v1/dispatch/track',
            json={'order_id': order.order_id, 'payload': {}},
        )
        assert response.status_code == 200

    metric = collector.get_single_collected_metric()

    assert metric.value == 1
    assert metric.labels == {
        'country': models.Country.Russia.name,
        'app_name': YANGO_PRETTY_NAME,
        'sensor': ORDER_DELIVERED,
    }


@pytest.mark.parametrize('status', ['closed', 'canceled'])
@pytest.mark.parametrize(
    'country', [models.Country.Russia, models.Country.Israel],
)
@pytest.mark.parametrize('shelf_type', ['markdown', 'store', 'parcel'])
async def test_finish_status_by_shelf_type_metric(
        grocery_cart,
        run_finish,
        create_order,
        taxi_grocery_orders_monitor,
        status,
        country,
        shelf_type,
):
    city_name = 'Moscow'

    order = await create_order(status=status, country=country)

    _prepare_cart_for_shelf_type(shelf_type, grocery_cart)

    metric_status = _get_status(status)

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_orders_monitor,
            sensor=FINISH_METRIC_BY_SHELF_TYPE,
            labels={
                'country': country.name,
                'status': metric_status,
                'shelf_type': shelf_type,
            },
    ) as collector:
        await run_finish(order.order_id)

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'country': country.name,
        'app_name': YANGO_PRETTY_NAME,
        'shelf_type': shelf_type,
        'sensor': FINISH_METRIC_BY_SHELF_TYPE,
        'status': metric_status,
        'city_name': city_name,
    }


@pytest.mark.parametrize('status', ['closed', 'canceled'])
@pytest.mark.parametrize(
    'country', [models.Country.Russia, models.Country.Israel],
)
@pytest.mark.parametrize('delivery_type', ['courier', 'pickup', 'rover'])
async def test_finish_status_by_delivery_type_metric(
        run_finish,
        create_order,
        taxi_grocery_orders_monitor,
        status,
        country,
        delivery_type,
):
    city_name = 'Moscow'
    order = await create_order(
        status=status, country=country, delivery_type=delivery_type,
    )

    metric_status = _get_status(status)

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_orders_monitor,
            sensor=FINISH_METRIC_BY_DELIVERY_TYPE,
            labels={
                'country': country.name,
                'status': metric_status,
                'delivery_type': delivery_type,
            },
    ) as collector:
        await run_finish(order.order_id)

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'country': country.name,
        'app_name': YANGO_PRETTY_NAME,
        'delivery_type': delivery_type,
        'sensor': FINISH_METRIC_BY_DELIVERY_TYPE,
        'status': metric_status,
        'city_name': city_name,
    }


@pytest.mark.parametrize(
    'country', [models.Country.Russia, models.Country.Israel],
)
async def test_cancel_reason(
        create_order, run_finish, taxi_grocery_orders_monitor, country,
):
    city_name = 'Moscow'
    cancel_reason_message = 'some-reason'
    cancel_reason_type = 'failure'

    order = await create_order(
        status='canceled',
        cancel_reason_message=cancel_reason_message,
        cancel_reason_type=cancel_reason_type,
        country=country,
    )

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_orders_monitor,
            sensor=CANCEL_REASONS,
            labels={
                'country': country.name,
                'cancel_reason_message': cancel_reason_message,
                'cancel_reason_type': cancel_reason_type,
            },
    ) as collector:
        await run_finish(order.order_id)

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'cancel_reason_message': cancel_reason_message,
        'cancel_reason_type': cancel_reason_type,
        'country': country.name,
        'sensor': CANCEL_REASONS,
        'app_name': YANGO_PRETTY_NAME,
        'city_name': city_name,
    }


@pytest.mark.parametrize(
    'country', [models.Country.Russia, models.Country.Israel],
)
async def test_cancel_reason_without_message(
        create_order, run_finish, taxi_grocery_orders_monitor, country,
):
    city_name = 'Moscow'
    cancel_reason_type = 'failure'

    order = await create_order(
        status='canceled',
        cancel_reason_type=cancel_reason_type,
        country=country,
    )

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_orders_monitor,
            sensor=CANCEL_REASONS_WITHOUT_MESSAGE,
            labels={
                'country': country.name,
                'cancel_reason_type': cancel_reason_type,
            },
    ) as collector:
        await run_finish(order.order_id)

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'cancel_reason_type': cancel_reason_type,
        'country': country.name,
        'sensor': CANCEL_REASONS_WITHOUT_MESSAGE,
        'app_name': YANGO_PRETTY_NAME,
        'city_name': city_name,
    }


async def test_send_delivery_time_metric(
        taxi_grocery_orders,
        taxi_grocery_orders_monitor,
        pgsql,
        grocery_cart,
        grocery_dispatch,
        processing,
        grocery_depots,
        mocked_time,
):
    grocery_cart.set_delivery_type('courier')

    grocery_dispatch.set_data(
        items=grocery_cart.get_items(),
        status='delivered',
        dispatch_id=get_new_uuid(),
        performer_id='123',
        eats_profile_id='101',
        transport_type='rover',
    )
    grocery_depots.add_depot(legacy_depot_id=models.DEFAULT_DEPOT_ID)

    mocked_time.set(consts.NOW_DT)

    def _get_new_order_id(delta_minutes):
        start = consts.NOW_DT - datetime.timedelta(minutes=delta_minutes)
        order = models.Order(
            pgsql=pgsql,
            status='delivering',
            app_info=headers.APP_INFO,
            dispatch_status_info=models.DispatchStatusInfo(
                dispatch_id=grocery_dispatch.dispatch_id,
                dispatch_status='delivering',
                dispatch_cargo_status='accepted',
                dispatch_start_delivery_ts=start.isoformat(),
            ),
            dispatch_flow='grocery_dispatch',
        )

        grocery_cart.set_cart_data(cart_id=order.cart_id)
        return order.order_id

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_orders_monitor,
            sensor=_metric('delivery_time_percentile'),
            labels={'country': models.Country.Russia.name},
    ) as collector:
        iter_count = 10
        for delta_minutes in range(iter_count):
            if delta_minutes == iter_count - 1:
                mocked_time.set(consts.NOW_DT + datetime.timedelta(seconds=10))

            order_id = _get_new_order_id(delta_minutes)
            grocery_dispatch.set_data(order_id=order_id)

            response = await taxi_grocery_orders.post(
                '/processing/v1/dispatch/track',
                json={'order_id': order_id, 'payload': {}},
            )
            assert response.status_code == 200

    metrics = collector.collected_metrics
    percentile_to_value = {}
    for metric in metrics:
        assert metric.labels['sensor'] == _metric('delivery_time_percentile')
        assert metric.labels['country'] == models.Country.Russia.name
        assert metric.labels['app_name'] == YANGO_PRETTY_NAME

        percentile_to_value[metric.labels['percentile']] = metric.value

    assert percentile_to_value == {'p50': 4, 'p80': 7, 'p95': 8, 'p98': 8}


DELAY_HOURS = 6
# If order's lifetime is less than `CRIT_LEVEL_2` and more than `DELAY_HOURS`,
# it means current crit level is: 1.
CRIT_LEVEL_2 = 12
CRIT_LEVEL_3 = 36


@pytest.mark.parametrize(
    'country', [models.Country.Russia, models.Country.Israel],
)
@pytest.mark.experiments3(
    name='grocery_alert_not_finished_orders_settings',
    consumers=['grocery-orders/metrics'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'delay_hours': DELAY_HOURS,
                'bounds_hours': [CRIT_LEVEL_2, CRIT_LEVEL_3],
            },
        },
    ],
    is_config=True,
)
@pytest.mark.parametrize(
    'order_lifetime_hours, time_boundary',
    [
        (DELAY_HOURS - 1, None),
        (CRIT_LEVEL_2 - 1, DELAY_HOURS),
        (CRIT_LEVEL_2 + 1, CRIT_LEVEL_2),
        (CRIT_LEVEL_3 - 1, CRIT_LEVEL_2),
        (CRIT_LEVEL_3 + 1, CRIT_LEVEL_3),
    ],
)
async def test_not_closed_orders_lifetimes(
        taxi_grocery_orders,
        taxi_grocery_orders_monitor,
        create_order,
        country,
        order_lifetime_hours,
        time_boundary,
):
    old_created = datetime.datetime.now() - datetime.timedelta(
        hours=order_lifetime_hours,
    )
    time_boundary_str = f'{time_boundary}h'
    await create_order(
        status='delivering', created=old_created, country=country,
    )

    await taxi_grocery_orders.run_periodic_task('orders-metrics-checker')

    metrics = await taxi_grocery_orders_monitor.get_metric('metrics')
    value = metrics[_metric('not_finished_orders_alert_by_country')]

    if time_boundary is None:
        assert value == {'$meta': {'solomon_children_labels': 'country'}}
    else:
        assert value == {
            '$meta': {'solomon_children_labels': 'country'},
            country.name: {
                '$meta': {'solomon_children_labels': 'time_boundary'},
                time_boundary_str: 1,
            },
        }


@pytest.mark.parametrize('status', ['closed', 'canceled'])
@pytest.mark.parametrize(
    'country, region_id, city_name',
    [
        (models.Country.Russia, 213, 'Moscow'),
        (models.Country.Israel, 131, 'Tel Aviv'),
    ],
)
async def test_finished_orders_per_day(
        taxi_grocery_orders,
        pgsql,
        taxi_grocery_orders_monitor,
        grocery_depots,
        status,
        country,
        region_id,
        city_name,
):
    old_order = models.Order(
        pgsql=pgsql,
        status=status,
        created=datetime.datetime.now() - datetime.timedelta(days=1, hours=1),
        region_id=2,
    )
    order = models.Order(
        pgsql=pgsql,
        status=status,
        created=datetime.datetime.now(),
        region_id=region_id,
        depot_id=old_order.depot_id,
    )
    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id,
        country_iso3=country.country_iso3,
        region_id=region_id,
    )

    await taxi_grocery_orders.run_periodic_task('orders-metrics-checker')

    metrics = await taxi_grocery_orders_monitor.get_metric('metrics')
    value = metrics[_metric('finished_orders_per_day')]
    assert value == {
        country.name: {
            _get_status(status): {
                city_name: {
                    YANGO_PRETTY_NAME: 1,
                    '$meta': {'solomon_children_labels': 'app_name'},
                },
                '$meta': {'solomon_children_labels': 'city_name'},
            },
            '$meta': {'solomon_children_labels': 'status'},
        },
        '$meta': {'solomon_children_labels': 'country'},
    }


async def test_cancel_reasons_per_day(
        taxi_grocery_orders,
        pgsql,
        taxi_grocery_orders_monitor,
        grocery_depots,
):
    country = models.Country.Russia
    region_id = 213
    order0 = models.Order(
        pgsql=pgsql,
        status='canceled',
        created=datetime.datetime.now(),
        region_id=region_id,
        cancel_reason_type='failure',
        cancel_reason_message='hold_money_failed',
    )
    order1 = models.Order(
        pgsql=pgsql,
        status='canceled',
        created=datetime.datetime.now(),
        region_id=region_id,
        depot_id=order0.depot_id,
        cancel_reason_type='admin_request',
        cancel_reason_message='cant_accept_order',
    )
    grocery_depots.add_depot(
        legacy_depot_id=order1.depot_id,
        country_iso3=country.country_iso3,
        region_id=region_id,
    )

    await taxi_grocery_orders.run_periodic_task('orders-metrics-checker')

    metrics = await taxi_grocery_orders_monitor.get_metric('metrics')
    value = metrics[_metric('cancel_reasons_per_day')]
    assert value == {
        'Russia': {
            'Moscow': {
                YANGO_PRETTY_NAME: {
                    'failure': {
                        'hold_money_failed': 1,
                        '$meta': {
                            'solomon_children_labels': 'cancel_reason_message',
                        },
                    },
                    'admin_request': {
                        'cant_accept_order': 1,
                        '$meta': {
                            'solomon_children_labels': 'cancel_reason_message',
                        },
                    },
                    '$meta': {'solomon_children_labels': 'cancel_reason_type'},
                },
                '$meta': {'solomon_children_labels': 'app_name'},
            },
            '$meta': {'solomon_children_labels': 'city_name'},
        },
        '$meta': {'solomon_children_labels': 'country'},
    }


async def test_order_submit_bad_request(
        taxi_grocery_orders,
        grocery_cart,
        personal,
        grocery_depots,
        taxi_grocery_orders_monitor,
        run_submit,
):
    city_name = 'Moscow'
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_depots.add_depot(
        legacy_depot_id=DEPOT_ID,
        country_iso3=models.Country.Russia.country_iso3,
    )

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_orders_monitor,
            sensor=ORDER_SUBMIT_BAD_REQUEST_METRIC,
            labels={'bad_request_code': 'bad_payment_method'},
    ) as collector:
        await run_submit()

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'bad_request_code': 'bad_payment_method',
        'sensor': ORDER_SUBMIT_BAD_REQUEST_METRIC,
        'app_name': YANGO_PRETTY_NAME,
        'country': models.Country.Russia.name,
        'city_name': city_name,
    }


def _prepare_cart_for_shelf_type(shelf_type, grocery_cart):
    if shelf_type == 'markdown':
        item_id = 'item-id:st-md'
    elif shelf_type == 'store':
        item_id = 'item-id'
    elif shelf_type == 'parcel':
        item_id = 'item-id:st-pa'
    else:
        assert False

    items = [models.GroceryCartItem(item_id=item_id)]
    grocery_cart.set_items(items)


def _get_status(order_status):
    if order_status == 'closed':
        return 'success'
    if order_status == 'canceled':
        return 'canceled'
    return None
