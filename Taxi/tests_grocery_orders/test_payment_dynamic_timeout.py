import copy
import datetime

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from . import consts
from . import experiments
from . import models

PAYMENT_TYPE = 'card'
COUNTRY_ISO3 = 'RUS'
ERRORS_PERCENT = 10
SHORT_FALLBACK_NAME = f'payment_timeout_{ERRORS_PERCENT}'
FALLBACK_NAME = f'{PAYMENT_TYPE}_{COUNTRY_ISO3.lower()}_{SHORT_FALLBACK_NAME}'
PAYMENTS_TIMEOUT_FALLBACK_TIMEOUT_SECONDS = 600

PAYMENTS_TIMEOUT_FALLBACKS = pytest.mark.experiments3(
    name='grocery_payments_timeout_fallbacks',
    consumers=['grocery-payments/timeout_fallbacks'],
    is_config=True,
    default_value={
        'fallbacks': [
            {
                'errors_percent': ERRORS_PERCENT,
                'timeout_seconds': PAYMENTS_TIMEOUT_FALLBACK_TIMEOUT_SECONDS,
            },
        ],
    },
)

PAYMENTS_TIMEOUT_POSTPONE_SECONDS = 120

PAYMENTS_TIMEOUT_POSTPONE = pytest.mark.experiments3(
    name='grocery_payments_timeout_postpone',
    consumers=['grocery-payments/timeout_fallbacks'],
    is_config=True,
    default_value={'postpone_seconds': PAYMENTS_TIMEOUT_POSTPONE_SECONDS},
)

TIMEOUT_CANCEL_ACTION_CANCEL = pytest.mark.experiments3(
    name='lavka_timeout_cancel_action',
    consumers=['grocery-orders/cancel'],
    is_config=True,
    default_value={'type': 'cancel'},
)


def _time_seconds_ago(seconds):
    return (consts.NOW_DT - datetime.timedelta(seconds=seconds)).isoformat()


def _time_in_seconds_in_future(seconds, now=consts.NOW_DT):
    return (now + datetime.timedelta(seconds=seconds)).isoformat()


ITEM_ID = 'some_id'
SUBITEM = models.GroceryCartSubItem(
    ITEM_ID + '_0',
    price='1',
    full_price='1',
    quantity='1',
    paid_with_cashback='1',
)

ITEM_V2 = models.GroceryCartItemV2(ITEM_ID, sub_items=[SUBITEM], title='title')

CANCEL_REASON_TYPE = 'payment_timeout'
CANCEL_REASON_MESSAGE = 'Payment timed out'


async def _processing_cancel(
        taxi_grocery_orders,
        order: models.Order,
        event_created_time,
        initial_event_created_time=None,
):
    return await taxi_grocery_orders.post(
        '/processing/v1/cancel',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'cancel_reason_message': CANCEL_REASON_MESSAGE,
            'cancel_reason_type': CANCEL_REASON_TYPE,
            'times_called': 0,
            'payload': {
                'event_created': event_created_time,
                'initial_event_created': (
                    initial_event_created_time
                    if initial_event_created_time is not None
                    else event_created_time
                ),
            },
        },
    )


@pytest.fixture(name='_environment')
def _environment(grocery_depots, grocery_cart, pgsql):
    class Context:
        order: models.Order

        def init(self):
            self.order = models.Order(
                pgsql=pgsql, status='checked_out', country=COUNTRY_ISO3,
            )
            grocery_depots.add_depot(legacy_depot_id=self.order.depot_id)
            grocery_cart.set_cart_data(cart_id=self.order.cart_id)
            grocery_cart.set_payment_method(
                {'type': PAYMENT_TYPE, 'id': 'test_payment_method_id'},
            )
            grocery_cart.set_items_v2([ITEM_V2])

            return self.order

    context = Context()

    return context


@pytest.mark.config(
    STATISTICS_FALLBACK_OVERRIDES=[
        {
            'enabled': True,
            'fallbacks': [FALLBACK_NAME],
            'service': 'grocery-payments',
        },
    ],
)
@pytest.mark.now(consts.NOW)
@PAYMENTS_TIMEOUT_FALLBACKS
@PAYMENTS_TIMEOUT_POSTPONE
@TIMEOUT_CANCEL_ACTION_CANCEL
@experiments.PAYMENT_TIMEOUT
@experiments.WMS_RESERVE_TIMEOUT
@pytest.mark.parametrize(
    'event_created_time, expected_postpone_due, expected_status',
    [
        (
            _time_seconds_ago(PAYMENTS_TIMEOUT_FALLBACK_TIMEOUT_SECONDS - 1),
            _time_in_seconds_in_future(PAYMENTS_TIMEOUT_POSTPONE_SECONDS),
            'checked_out',
        ),
        (
            _time_seconds_ago(PAYMENTS_TIMEOUT_FALLBACK_TIMEOUT_SECONDS + 1),
            None,
            'pending_cancel',
        ),
    ],
)
async def test_dynamic_payment_timeout(
        statistics,
        grocery_depots,
        grocery_cart,
        taxi_grocery_orders,
        processing,
        event_created_time,
        expected_postpone_due,
        expected_status,
        _environment,
):
    order = _environment.init()

    await taxi_grocery_orders.invalidate_caches()

    response = await _processing_cancel(
        taxi_grocery_orders, order, event_created_time,
    )

    order.update()

    assert response.status_code == 200

    assert order.status == expected_status

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 1

    if expected_postpone_due:
        assert events[0].payload == {
            'order_id': order.order_id,
            'reason': 'cancel',
            'cancel_reason_type': CANCEL_REASON_TYPE,
            'payload': {
                'event_created': consts.NOW,
                'initial_event_created': event_created_time,
            },
            'cancel_reason_message': CANCEL_REASON_MESSAGE,
            'times_called': 1,
            'flow_version': 'grocery_flow_v1',
        }

        assert events[0].due == expected_postpone_due
    else:
        assert events[0].payload == {
            'order_id': order.order_id,
            'reason': 'close',
            'is_canceled': True,
            'flow_version': 'grocery_flow_v1',
            'idempotency_token': '{}-close'.format(order.idempotency_token),
        }


@pytest.mark.config(
    STATISTICS_FALLBACK_OVERRIDES=[
        {
            'enabled': True,
            'fallbacks': [FALLBACK_NAME],
            'service': 'grocery-payments',
        },
    ],
)
@pytest.mark.now(consts.NOW)
@PAYMENTS_TIMEOUT_FALLBACKS
@PAYMENTS_TIMEOUT_POSTPONE
@TIMEOUT_CANCEL_ACTION_CANCEL
@experiments.PAYMENT_TIMEOUT
@experiments.WMS_RESERVE_TIMEOUT
@pytest.mark.parametrize('timeout_exceeded', [True, False])
@pytest.mark.parametrize('hold', [True, False])
async def test_hold(
        statistics,
        grocery_depots,
        grocery_cart,
        taxi_grocery_orders,
        processing,
        _environment,
        hold,
        timeout_exceeded,
):
    order = _environment.init()

    await taxi_grocery_orders.invalidate_caches()

    order_state = copy.deepcopy(order.state)
    order_state.hold_money_status = 'success' if hold else None
    order.upsert(state=order_state)

    event_created_time = _time_seconds_ago(
        PAYMENTS_TIMEOUT_FALLBACK_TIMEOUT_SECONDS
        - (0 if timeout_exceeded else 1),
    )
    expected_postpone_due = _time_in_seconds_in_future(
        PAYMENTS_TIMEOUT_POSTPONE_SECONDS,
    )

    response = await _processing_cancel(
        taxi_grocery_orders, order, event_created_time,
    )

    assert response.status_code == 200

    order.update()

    events = list(processing.events(scope='grocery', queue='processing'))

    if hold:
        assert order.status == 'checked_out'
        assert not events
        return

    if timeout_exceeded:
        assert order.status == 'pending_cancel'

        assert len(events) == 1

        assert events[0].payload == {
            'order_id': order.order_id,
            'reason': 'close',
            'is_canceled': True,
            'flow_version': 'grocery_flow_v1',
            'idempotency_token': '{}-close'.format(order.idempotency_token),
        }
    else:
        assert len(events) == 1

        assert events[0].payload == {
            'order_id': order.order_id,
            'reason': 'cancel',
            'cancel_reason_type': CANCEL_REASON_TYPE,
            'payload': {
                'event_created': consts.NOW,
                'initial_event_created': event_created_time,
            },
            'cancel_reason_message': CANCEL_REASON_MESSAGE,
            'times_called': 1,
            'flow_version': 'grocery_flow_v1',
        }

        assert events[0].due == expected_postpone_due

        assert order.status == 'checked_out'


@pytest.mark.now(consts.NOW)
@PAYMENTS_TIMEOUT_POSTPONE
@TIMEOUT_CANCEL_ACTION_CANCEL
@experiments.PAYMENT_TIMEOUT
@experiments.WMS_RESERVE_TIMEOUT
@pytest.mark.parametrize(
    'fallback_name, add_exp_name',
    [(SHORT_FALLBACK_NAME, True), (FALLBACK_NAME, False), (None, False)],
)
async def test_fallback_name(
        statistics,
        grocery_depots,
        grocery_cart,
        taxi_grocery_orders,
        processing,
        _environment,
        fallback_name,
        add_exp_name,
        experiments3,
        taxi_config,
):
    order = _environment.init()

    if fallback_name is not None:
        exp_fallbacks = {
            'fallbacks': [
                {
                    'errors_percent': ERRORS_PERCENT,
                    'timeout_seconds': (
                        PAYMENTS_TIMEOUT_FALLBACK_TIMEOUT_SECONDS
                    ),
                },
            ],
        }

        if add_exp_name:
            exp_fallback = exp_fallbacks['fallbacks'][0]
            exp_fallback['name'] = fallback_name

        experiments3.add_config(
            name='grocery_payments_timeout_fallbacks',
            consumers=['grocery-payments/timeout_fallbacks'],
            default_value=exp_fallbacks,
        )

        taxi_config.set_values(
            {
                'STATISTICS_FALLBACK_OVERRIDES': [
                    {
                        'enabled': True,
                        'fallbacks': [fallback_name],
                        'service': 'grocery-payments',
                    },
                ],
            },
        )

    await taxi_grocery_orders.invalidate_caches()

    event_created_time = _time_seconds_ago(
        PAYMENTS_TIMEOUT_FALLBACK_TIMEOUT_SECONDS - 1,
    )

    response = await _processing_cancel(
        taxi_grocery_orders, order, event_created_time,
    )

    order.update()

    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 1

    if fallback_name:
        assert order.status == 'checked_out'

        assert events[0].payload == {
            'order_id': order.order_id,
            'reason': 'cancel',
            'cancel_reason_type': CANCEL_REASON_TYPE,
            'payload': {
                'event_created': consts.NOW,
                'initial_event_created': event_created_time,
            },
            'cancel_reason_message': CANCEL_REASON_MESSAGE,
            'times_called': 1,
            'flow_version': 'grocery_flow_v1',
        }

        postpone_due = _time_in_seconds_in_future(
            PAYMENTS_TIMEOUT_POSTPONE_SECONDS,
        )

        assert events[0].due == postpone_due
    else:
        assert order.status == 'pending_cancel'

        assert events[0].payload == {
            'order_id': order.order_id,
            'reason': 'close',
            'is_canceled': True,
            'flow_version': 'grocery_flow_v1',
            'idempotency_token': '{}-close'.format(order.idempotency_token),
        }


@pytest.mark.now(consts.NOW)
async def test_metric_rescued_payments(
        taxi_grocery_orders_monitor,
        grocery_depots,
        taxi_grocery_orders,
        _environment,
):
    order = _environment.init()

    await taxi_grocery_orders.invalidate_caches()

    order_state = copy.deepcopy(order.state)
    order_state.hold_money_status = 'success'
    order.upsert(state=order_state)

    initial_event_created_time = _time_seconds_ago(2)
    event_created_time = _time_seconds_ago(1)

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_orders_monitor,
            sensor='grocery_orders_rescued_payments',
    ) as collector:
        await _processing_cancel(
            taxi_grocery_orders=taxi_grocery_orders,
            order=order,
            event_created_time=event_created_time,
            initial_event_created_time=initial_event_created_time,
        )

    metrics = collector.collected_metrics

    assert _check_metric_is_one(
        {'payment_type': 'card', 'country': models.Country.Russia.name},
        metrics,
    )

    assert _check_metric_is_one(
        {
            'payment_type': 'personal_wallet',
            'country': models.Country.Russia.name,
        },
        metrics,
    )


def _check_metric_is_one(metric_to_check, collected_metrics):
    for collected_metric in collected_metrics:
        all_fields_equal = True
        for key, value in metric_to_check.items():
            all_fields_equal = all_fields_equal and (
                collected_metric.labels[key] == value
            )

        if all_fields_equal:
            assert collected_metric.value == 1
            return True

    return False
