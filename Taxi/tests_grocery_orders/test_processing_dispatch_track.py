# pylint: disable=too-many-lines

import dataclasses
import datetime
from typing import Optional
import uuid

import pytest

from . import consts
from . import helpers
from . import models
from . import processing_noncrit

TRACK_SELFCALL = 200
NOW_TIME = '2020-05-25T17:43:00+00:00'
PREV_TIME = '2020-05-25T17:40:45+00:00'

PICKUPED_TIME_OK_CANCEL = '2020-05-25T17:48:45+00:00'
PICKUPED_TIME_NO_CANCEL_1 = '2020-05-25T17:47:45+00:00'
PICKUPED_TIME_NO_CANCEL_2 = '2020-05-25T17:46:45+00:00'
PICKUPED_TIME_NO_CANCEL_3 = '2020-05-25T17:42:45+00:00'

DISPATCH_RETRIES_CONFIG = pytest.mark.experiments3(
    name='grocery_processing_events_policy',
    consumers=[
        'grocery-orders/processing-policy',
        'grocery-processing/policy',
    ],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        *(processing_noncrit.NOTIFICATION_CLAUSES_LIST),
        {
            'title': 'Track',
            'predicate': {
                'init': {
                    'set': ['dispatch-track'],
                    'arg_name': 'name',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {'retry_interval': {'hours': 24}},
        },
    ],
    is_config=True,
)


def _check_notification_pipeline_payload(result, expected, now):
    assert result['order_id'] == expected['order_id']
    assert result['code'] == expected['code']
    assert result['reason'] == expected['reason']
    assert result['payload'] == expected['payload']

    minutes = processing_noncrit.STOP_RETRY_AFTER_MINUTES
    stop_retry_after = now + datetime.timedelta(minutes=minutes)
    assert result['event_policy'] == {
        'retry_count': 1,
        'stop_retry_after': stop_retry_after.isoformat(),
    }


def get_new_uuid():
    return str(uuid.uuid4())


def _tristero_new_status(previous_cargo_status, new_cargo_status):
    courier_assigned = [
        'performer_found',
        'pickup_arrived',
        'ready_for_pickup_confirmation',
    ]
    delivering = [
        'pickuped',
        'delivery_arrived',
        'ready_for_delivery_confirmation',
    ]

    if (
            new_cargo_status in courier_assigned
            and previous_cargo_status not in courier_assigned
    ):
        return 'courier_assigned'
    if (
            new_cargo_status in delivering
            and previous_cargo_status not in delivering
    ):
        return 'delivering'
    return None


LAVKA_PLACE_ID = (
    'ymapsbm1://geo?ll=37.601%2C55.585&spn=0.001%2C0.001&text='
    '%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2C%20%D0%9C%D0%BE%D1'
    '%81%D0%BA%D0%B2%D0%B0%2C%20%D0%92%D0%B0%D1%80%D1%88%D0%B0'
    '%D0%B2%D1%81%D0%BA%D0%BE%D0%B5%20%D1%88%D0%BE%D1%81%D1%81'
    '%D0%B5%2C%20141%D0%90%D0%BA1%2C%20%D0%BF%D0%BE%D0%B4%D1%8'
    'A%D0%B5%D0%B7%D0%B4%201%20%7B3457696635%7D'
)


@dataclasses.dataclass
class ParametrizeData:
    # изначальный статус(наш) в базе данных g-orders
    init_dispatch_status: str = 'delivering'
    # изначальный статус(каргошный) в базе данных g-orders
    init_dispatch_cargo_status: str = 'pickuped'
    # статус в респонсе ручки /internal/dispatch/v1/status
    response_dispatch_status: str = 'delivering'
    # итоговый ожидаемый статус после /dispatch/track
    result_dispatch_status: str = 'delivering'
    # итоговый ожидаемый карго статус после /dispatch/track
    result_dispatch_cargo_status: str = 'pickuped'
    # изначальный статус заказа в бд
    order_status: str = 'delivering'

    dispatch_id = str(uuid.uuid4())

    # заполняется на стороне grocery_dispatch
    failure_reason_type: str = 'failed'

    # ожидаемое число вызовов info из карго
    cargo_info_called: int = 0
    # ожидаемое число вызовов info из g-dispatch
    dispatch_info_called: int = 1

    # TODO: когда выпилим cargo- спилить
    dispatch_flow = 'grocery_dispatch'

    status_code: Optional[int] = 200

    # данные о курьере
    performer_id: Optional[str] = None
    eat_courier_id: Optional[str] = None
    # ВНИМАТЕЛЬНО! dispatch так замокан, что без
    # performer_name вернет пустой performer_info
    performer_name: Optional[str] = None
    first_performer_name: Optional[str] = None

    init_performer_name: Optional[str] = None
    init_first_performer_name: Optional[str] = None

    transport_type: Optional[str] = None
    delivery_type: str = 'courier'

    # в ручке /track сюда присвоится performer_id
    init_driver_id: Optional[str] = None

    external_performer_cargo_called: int = 0
    external_performer_dispatch_called: int = 0


def close_payload(order):
    return {
        'order_id': order.order_id,
        'reason': 'close',
        'flow_version': 'grocery_flow_v1',
        'is_canceled': False,
        'idempotency_token': '{}-close'.format(order.idempotency_token),
    }


def cancel_payload(order, data):
    expected_message = ''
    if data.failure_reason_type:
        expected_message = data.failure_reason_type

    assert order.desired_status == 'canceled'
    return {
        'order_id': order.order_id,
        'reason': 'cancel',
        'flow_version': 'grocery_flow_v1',
        'cancel_reason_type': 'dispatch_failure',
        'payload': {
            'event_created': '2020-05-25T17:40:45+00:00',
            'initial_event_created': '2020-05-25T17:40:45+00:00',
        },
        'cancel_reason_message': expected_message,
        'times_called': 0,
    }


def delivering_notification(order, now):
    minutes = processing_noncrit.STOP_RETRY_AFTER_MINUTES
    stop_retry_after = now + datetime.timedelta(minutes=minutes)
    return {
        'order_id': order.order_id,
        'reason': 'order_notification',
        'code': 'delivering',
        'order_info': {
            'app_info': order.app_info,
            'yandex_uid': order.yandex_uid,
            'country_iso3': 'RUS',
            'currency_code': order.currency,
            'depot_id': order.depot_id,
            'eats_user_id': order.eats_user_id,
            'leave_at_door': order.left_at_door,
            'locale': order.locale,
            'order_id': order.order_id,
            'personal_phone_id': order.personal_phone_id,
            'region_id': order.region_id,
            'short_order_id': order.short_order_id,
            'taxi_user_id': order.taxi_user_id,
        },
        'payload': {'delivery_type': 'courier'},
        'event_policy': {
            'retry_count': 1,
            'stop_retry_after': stop_retry_after.isoformat(),
        },
    }


def rover_arrived_notification(order):
    return {
        'order_id': order.order_id,
        'reason': 'order_notification',
        'code': 'ready_for_delivery_confirmation',
        'order_info': {
            'app_info': order.app_info,
            'yandex_uid': order.yandex_uid,
            'country_iso3': 'RUS',
            'currency_code': order.currency,
            'depot_id': order.depot_id,
            'eats_user_id': order.eats_user_id,
            'leave_at_door': order.left_at_door,
            'locale': order.locale,
            'order_id': order.order_id,
            'personal_phone_id': order.personal_phone_id,
            'region_id': order.region_id,
            'short_order_id': order.short_order_id,
            'taxi_user_id': order.taxi_user_id,
        },
        'payload': {},
    }


def status_changed_delivery_payload(order, now=consts.NOW_DT):
    return {
        'order_id': order.order_id,
        'reason': 'status_change',
        'status_change': 'delivering',
        'order_log_info': {
            'order_state': 'delivering',
            'order_type': 'grocery',
            'order_pickuped_date': now.isoformat(),
            'depot_id': order.depot_id,
        },
        'atlas_order_info': {
            'order_id': order.order_id,
            'status': 'delivering',
        },
    }


def send_parcel_status_payload(order, tristero_status):
    return {
        'order_id': order.order_id,
        'parcels_body': {
            'parcel_wms_ids': ['parcel_item_id:st-pa'],
            'state': tristero_status,
            'state_meta': {'order_id': order.order_id},
        },
        'reason': 'tristero_setstate',
    }


def new_performer_payload(order, data):
    return {
        'dispatch_track_version': (
            order.dispatch_status_info.dispatch_track_version
        ),
        'driver_id': data.performer_id if data.performer_id else 'null',
        'flow_version': 'grocery_flow_v1',
        'order_id': order.order_id,
        'reason': 'dispatch_new_performer',
    }


def new_performer_status_changed(order):
    return {
        'order_id': order.order_id,
        'order_log_info': {
            'depot_id': order.depot_id,
            'order_state': 'performer_found',
            'order_type': 'grocery',
        },
        'reason': 'status_change',
        'status_change': 'delivering',
    }


def restart_track_payload(order):
    return {
        'event_policy': {'retry_count': 1, 'retry_interval': 86400},
        'flow_version': 'grocery_flow_v1',
        'order_id': order.order_id,
        'reason': 'dispatch_track',
        'times_called': 1,
    }


def processing_payloads_for_state(initial_order, order_updated, data):
    if data.result_dispatch_status == 'closed':
        return [close_payload(order_updated)]
    if data.result_dispatch_status in ('revoked', 'failed'):
        return [cancel_payload(order_updated, data)]
    if (
            initial_order.dispatch_status_info.dispatch_driver_id
            != data.performer_id
    ):
        return [
            new_performer_payload(order_updated, data),
            restart_track_payload(order_updated),
        ]
    return [restart_track_payload(order_updated)]


def tristero_new_status(previous_cargo_status, new_cargo_status):
    courier_assigned = [
        'performer_found',
        'pickup_arrived',
        'ready_for_pickup_confirmation',
    ]
    delivering = [
        'pickuped',
        'delivery_arrived',
        'ready_for_delivery_confirmation',
    ]

    if (
            new_cargo_status in courier_assigned
            and previous_cargo_status not in courier_assigned
    ):
        # похоже что этот кейс не воспроизводится с g-dispatch
        return 'courier_assigned'
    if (
            new_cargo_status in delivering
            and previous_cargo_status not in delivering
    ):
        return 'delivering'
    return None


def noncrit_payloads_for_state(
        initial_order, order_updated, data, now, with_tristero,
):
    payloads = []
    if data.result_dispatch_status == 'delivering' and (
            data.init_dispatch_status == 'accepted'
            or data.init_dispatch_status == 'created'
    ):
        payloads.append(delivering_notification(order_updated, now))

    if (
            data.result_dispatch_cargo_status
            == 'ready_for_delivery_confirmation'
            and data.init_dispatch_cargo_status
            != 'ready_for_delivery_confirmation'
            and data.delivery_type == 'rover'
    ):
        payloads.append(rover_arrived_notification(order_updated))

    if (
            data.response_dispatch_status == 'delivering'
            and data.init_dispatch_cargo_status != 'pickuped'
    ):
        payloads.append(status_changed_delivery_payload(order_updated, now))
    # проверяем data.performer_name потому что если он пустой, то замоканный
    # диспач вернет null-performer и мы не дойдем до этого пайплайна,
    # а переключимся в HandleEmptyPerformer
    if (
            data.performer_name
            and initial_order.dispatch_status_info.dispatch_driver_id
            != data.performer_id
    ):
        payloads.append(new_performer_status_changed(order_updated))

    if with_tristero:
        tristero_status = tristero_new_status(
            data.init_dispatch_cargo_status, data.result_dispatch_cargo_status,
        )
        if tristero_status:
            payloads.append(
                send_parcel_status_payload(order_updated, tristero_status),
            )
    return payloads


def check_delivery_started_payload(event, event_to_comp):
    assert event['order_id'] == event_to_comp['order_id']
    assert event['reason'] == event_to_comp['reason']
    assert event['status_change'] == event_to_comp['status_change']
    assert (
        event['order_log_info']['order_state']
        == event_to_comp['order_log_info']['order_state']
    )
    assert (
        event['order_log_info']['order_type']
        == event_to_comp['order_log_info']['order_type']
    )
    assert (
        event['order_log_info']['order_pickuped_date']
        == event_to_comp['order_log_info']['order_pickuped_date']
    )
    assert (
        event['order_log_info']['depot_id']
        == event_to_comp['order_log_info']['depot_id']
    )
    assert (
        event['atlas_order_info']['order_id']
        == event_to_comp['atlas_order_info']['order_id']
    )
    assert (
        event['atlas_order_info']['status']
        == event_to_comp['atlas_order_info']['status']
    )


def check_noncrit_payloads(
        initial_order, order_updated, data, events, events_to_compare,
):
    assert len(events) == len(events_to_compare)
    for event, to_comp in zip(events, events_to_compare):
        if 'atlas_order_info' in event:
            # потому что сверять по всем полям AtlasOrderInfo это боль
            check_delivery_started_payload(event, to_comp)
        else:
            assert event == to_comp


def should_call_wms_set_courier(order, data):
    return order.dispatch_status_info and (
        order.dispatch_status_info.dispatch_driver_id != data.performer_id
    )


def extract_payloads(events):
    return list(map(lambda ev: ev.payload, events))


@pytest.mark.now(PREV_TIME)
@pytest.mark.parametrize(
    'data',
    [
        ParametrizeData(
            init_dispatch_status='delivering',
            init_dispatch_cargo_status='pickuped',
            response_dispatch_status='finished',
            result_dispatch_status='closed',
            result_dispatch_cargo_status='delivered_finish',
        ),
        ParametrizeData(
            init_dispatch_status='delivering',
            init_dispatch_cargo_status='pickuped',
            response_dispatch_status='delivered',
            result_dispatch_status='closed',
            result_dispatch_cargo_status='delivered',
        ),
        ParametrizeData(
            init_dispatch_status='delivering',
            init_dispatch_cargo_status='pickuped',
            response_dispatch_status='canceling',
            result_dispatch_status='revoked',
            result_dispatch_cargo_status='cancelled',
        ),
        ParametrizeData(
            init_dispatch_status='delivering',
            init_dispatch_cargo_status='pickuped',
            response_dispatch_status='canceled',
            result_dispatch_status='revoked',
            result_dispatch_cargo_status='cancelled',
        ),
        ParametrizeData(
            init_dispatch_status='delivering',
            init_dispatch_cargo_status='pickuped',
            response_dispatch_status='revoked',
            result_dispatch_status='failed',
            result_dispatch_cargo_status='failed',
        ),
        ParametrizeData(
            init_dispatch_status='delivering',
            init_dispatch_cargo_status='pickuped',
            response_dispatch_status='delivering',
            result_dispatch_status='delivering',
            result_dispatch_cargo_status='pickuped',
        ),
        ParametrizeData(
            init_dispatch_status='delivering',
            init_dispatch_cargo_status='pickuped',
            response_dispatch_status='delivering',
            result_dispatch_status='delivering',
            result_dispatch_cargo_status='pickuped',
            init_driver_id='init_id',
        ),
        ParametrizeData(
            init_dispatch_status='delivering',
            init_dispatch_cargo_status='pickuped',
            response_dispatch_status='delivering',
            result_dispatch_status='delivering',
            result_dispatch_cargo_status='pickuped',
            performer_name='dog',
            init_performer_name='dog',
            performer_id='new_id',
            init_driver_id='init_id',
        ),
        ParametrizeData(
            init_dispatch_status='delivering',
            init_dispatch_cargo_status='pickuped',
            response_dispatch_status='delivering',
            result_dispatch_status='delivering',
            result_dispatch_cargo_status='pickuped',
            performer_name='dog',
            init_performer_name='dog',
            performer_id='init_id',
            init_driver_id='init_id',
        ),
        ParametrizeData(
            init_dispatch_status='accepted',
            init_dispatch_cargo_status='performer_found',
            response_dispatch_status='delivering',
            result_dispatch_status='delivering',
            result_dispatch_cargo_status='pickuped',
        ),
        ParametrizeData(
            init_dispatch_status='accepted',
            init_dispatch_cargo_status='performer_found',
            response_dispatch_status='matched',
            result_dispatch_status='accepted',
            result_dispatch_cargo_status='performer_found',
        ),
        ParametrizeData(
            init_dispatch_status='accepted',
            init_dispatch_cargo_status='performer_found',
            response_dispatch_status='delivery_arrived',
            result_dispatch_status='delivering',
            result_dispatch_cargo_status='delivery_arrived',
        ),
        ParametrizeData(
            init_dispatch_status='created',
            init_dispatch_cargo_status='new',
            response_dispatch_status='scheduled',
            result_dispatch_status='created',
            result_dispatch_cargo_status='accepted',
        ),
        ParametrizeData(
            init_dispatch_status='created',
            init_dispatch_cargo_status='new',
            response_dispatch_status='idle',
            result_dispatch_status='created',
            result_dispatch_cargo_status='new',
        ),
        ParametrizeData(
            init_dispatch_status='created',
            init_dispatch_cargo_status='new',
            response_dispatch_status='delivering',
            result_dispatch_status='delivering',
            result_dispatch_cargo_status='pickuped',
        ),
        ParametrizeData(
            init_dispatch_status='delivering',
            init_dispatch_cargo_status='pickuped',
            response_dispatch_status='ready_for_delivery_confirmation',
            result_dispatch_status='delivering',
            result_dispatch_cargo_status='ready_for_delivery_confirmation',
            delivery_type='rover',
            init_performer_name='Bender',
            performer_name='Bender',
            init_driver_id='kiss_my_shiny_metal_ass',
            performer_id='kiss_my_shiny_metal_ass',
        ),
    ],
)
@pytest.mark.parametrize('with_tristero_parcels', [True, False])
@DISPATCH_RETRIES_CONFIG
@pytest.mark.config(GROCERY_ORDERS_SEND_ATLAS_EVENTS=True)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        data,
        processing,
        grocery_depots,
        with_tristero_parcels,
        experiments3,
        grocery_supply,
        grocery_dispatch,
        grocery_wms_gateway,
):
    order = models.Order(
        pgsql=pgsql,
        status=data.order_status,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=data.dispatch_id,
            dispatch_status=data.init_dispatch_status,
            dispatch_cargo_status=data.init_dispatch_cargo_status,
            dispatch_delivered_eta_ts=PREV_TIME,
            dispatch_courier_name=data.init_performer_name,
            dispatch_transport_type=data.delivery_type,
        ),
        order_version=0,
        dispatch_flow=data.dispatch_flow,
    )
    order.update()
    initial_order = order.clone()

    dispatch_driver_id = (
        data.performer_id
        if data.performer_id is not None
        else data.init_driver_id
    )

    grocery_dispatch.set_data(
        order_id=order.order_id,
        items=grocery_cart.get_items(),
        status=data.response_dispatch_status,
        dispatch_id=data.dispatch_id,
        failure_reason_type=data.failure_reason_type,
        performer_name=data.performer_name,
        performer_id=data.performer_id,
        eats_profile_id='1010',
        driver_id=dispatch_driver_id,
        transport_type=data.delivery_type,
        eta=2 * 60 + 15,
    )

    if with_tristero_parcels:
        grocery_cart.set_items(
            [models.GroceryCartItem('parcel_item_id:st-pa')],
        )

    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, region_id=order.region_id,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type(data.delivery_type)

    grocery_wms_gateway.set_driver_uuid(dispatch_driver_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/track',
        json={'order_id': order.order_id, 'payload': {}},
    )

    assert response.status_code == data.status_code
    assert (
        grocery_dispatch.times_performer_info_called()
        == data.external_performer_dispatch_called
    )
    assert grocery_dispatch.times_info_called() == data.dispatch_info_called

    assert (
        grocery_wms_gateway.times_set_courier_called()
        == should_call_wms_set_courier(order, data)
    )

    order.update()

    assert (
        order.dispatch_status_info.dispatch_status
        == data.result_dispatch_status
    )
    assert (
        order.dispatch_status_info.dispatch_cargo_status
        == data.result_dispatch_cargo_status
    )

    events = list(processing.events(scope='grocery', queue='processing'))
    assert extract_payloads(events) == processing_payloads_for_state(
        initial_order, order, data,
    )

    non_crit_events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    non_crit_to_compare = noncrit_payloads_for_state(
        initial_order,
        order,
        data,
        datetime.datetime.fromisoformat(PREV_TIME),
        with_tristero_parcels,
    )

    check_noncrit_payloads(
        initial_order,
        order,
        data,
        extract_payloads(non_crit_events),
        non_crit_to_compare,
    )


DEPOT_LOCATION = [13.0, 37.0]
CART_ID = '00000000-0000-0000-0000-d98013100500'
CART_ID_PREFIX = '00000000-0000-0000-0000-d980131005'


@pytest.mark.parametrize(
    'cargo_dispatch',
    [
        {'dispatch_delivery_type': 'yandex_taxi'},
        {'dispatch_in_batch': True, 'batch_order_num': 1},
        {'dispatch_in_batch': True},
        None,
    ],
)
async def test_dispatch_batch(
        taxi_grocery_orders,
        pgsql,
        grocery_dispatch,
        cargo_dispatch,
        grocery_cart,
        grocery_depots,
        grocery_wms_gateway,
):
    dispatch_id = get_new_uuid()

    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status='delivering',
            dispatch_cargo_status='pickuped',
            dispatch_start_delivery_ts=NOW_TIME,
        ),
        dispatch_flow='grocery_dispatch',
    )

    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, location=DEPOT_LOCATION,
    )

    grocery_dispatch.set_data(
        dispatch_id=dispatch_id,
        order_id=order.order_id,
        status='delivering',
        eta=3 * 60,
    )

    dispatch_in_batch = (
        cargo_dispatch['dispatch_in_batch']
        if cargo_dispatch is not None
        and 'dispatch_in_batch' in cargo_dispatch.keys()
        else None
    )

    batch_order_num = (
        cargo_dispatch['batch_order_num']
        if cargo_dispatch is not None
        and 'batch_order_num' in cargo_dispatch.keys()
        else None
    )

    dispatch_delivery_type = (
        cargo_dispatch['dispatch_delivery_type']
        if cargo_dispatch is not None
        and 'dispatch_delivery_type' in cargo_dispatch.keys()
        else None
    )

    if dispatch_delivery_type is not None:
        grocery_wms_gateway.set_dispatch_delivery_type(dispatch_delivery_type)

    grocery_dispatch.set_cargo_dispatch_info(
        dispatch_in_batch=dispatch_in_batch,
        batch_order_num=batch_order_num,
        dispatch_delivery_type=dispatch_delivery_type,
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type('eats_dispatch')

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/track',
        json={'order_id': order.order_id, 'payload': {}},
    )

    assert response.status_code == 200

    order.update()

    if (
            order.dispatch_status_info.dispatch_status_meta is not None
            and 'cargo_dispatch'
            in order.dispatch_status_info.dispatch_status_meta.keys()
    ):
        assert (
            order.dispatch_status_info.dispatch_status_meta['cargo_dispatch']
            == cargo_dispatch
        )
    else:
        assert cargo_dispatch is None


@pytest.mark.now(NOW_TIME)
@pytest.mark.parametrize(
    'init_dispatch_status,response_dispatch_status,'
    'init_start_delivery_ts,result_start_delivery_ts',
    [
        ('accepted', 'matching', None, None),
        ('accepted', 'delivering', None, NOW_TIME),
        ('delivering', 'delivering', PREV_TIME, PREV_TIME),
    ],
)
@pytest.mark.parametrize('enable_pull_dispatch', [True, False])
async def test_start_delivery_ts(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_dispatch,
        grocery_depots,
        init_dispatch_status,
        response_dispatch_status,
        init_start_delivery_ts,
        result_start_delivery_ts,
        experiments3,
        enable_pull_dispatch,
):
    dispatch_id = get_new_uuid()

    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id,
            init_dispatch_status,
            'accepted',
            100,
            init_start_delivery_ts,
        ),
        dispatch_flow='grocery_dispatch',
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type('courier')

    grocery_dispatch.set_data(
        order_id=order.order_id,
        items=grocery_cart.get_items(),
        status=response_dispatch_status,
        dispatch_id=dispatch_id,
        performer_id='123',
        eats_profile_id='1010',
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/track',
        json={'order_id': order.order_id, 'payload': {}},
    )
    assert response.status_code == TRACK_SELFCALL

    order.update()

    if result_start_delivery_ts is not None:
        assert (
            order.dispatch_status_info.dispatch_start_delivery_ts
            == datetime.datetime.fromisoformat(result_start_delivery_ts)
        )


@pytest.mark.parametrize(
    'order_revision,response_cargo_revision,got_status',
    [
        (2, 1, 'ready_for_approval'),
        (2, 1, 'performer_found'),
        (1, 1, 'ready_for_approval'),
        (1, 1, 'performer_found'),
        (1, 2, 'ready_for_approval'),
        (1, 2, 'performer_found'),
        (1, 2, 'ready_for_delivery_confirmation'),
    ],
)
async def test_dispatch_info_update(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_dispatch,
        grocery_depots,
        order_revision,
        response_cargo_revision,
        got_status,
):
    dispatch_id = get_new_uuid()
    eats_courier_id = '101010'
    init_order_version = 1

    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status='delivering',
            dispatch_cargo_status='pickuped',
            dispatch_cargo_revision=order_revision,
        ),
        dispatch_flow='grocery_dispatch',
        order_version=init_order_version,
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type('rover')

    grocery_dispatch.set_data(
        items=grocery_cart.get_items(),
        status=got_status,
        dispatch_id=dispatch_id,
        performer_id='123',
        eats_profile_id=eats_courier_id,
        transport_type='rover',
        cargo_revision=response_cargo_revision,
    )
    await taxi_grocery_orders.post(
        '/processing/v1/dispatch/track',
        json={'order_id': order.order_id, 'payload': {}},
    )
    order.update()

    assert order.order_version == init_order_version


@pytest.mark.now(PREV_TIME)
async def test_driver_cancelled_by_admin(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_dispatch,
        grocery_depots,
        grocery_wms_gateway,
):
    first_driver_id = '123'
    first_driver_name = 'zaurbek'
    second_driver_id = '456'
    second_driver_name = 'ne_zaurbek'
    dispatch_id = get_new_uuid()
    grocery_dispatch.set_data(dispatch_id=dispatch_id)
    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status='accepted',
            dispatch_cargo_status='performer_found',
            dispatch_delivered_eta_ts=PREV_TIME,
        ),
        order_version=0,
        dispatch_flow='grocery_dispatch',
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type('eats_dispatch')

    grocery_dispatch.set_data(
        order_id=order.order_id,
        status='delivering',
        eta=3 * 60,
        driver_id=first_driver_id,
        performer_name=first_driver_id,
        performer_first_name=first_driver_name,
        performer_id=first_driver_id,
        eats_profile_id=first_driver_id,
    )

    grocery_wms_gateway.set_driver_uuid(first_driver_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/track',
        json={'order_id': order.order_id, 'payload': {}},
    )

    assert response.status_code == 200

    order.update()

    assert order.dispatch_status_info.dispatch_driver_id == first_driver_id
    assert (
        order.dispatch_status_info.dispatch_courier_first_name
        == first_driver_name
    )

    grocery_dispatch.reset_performer()
    grocery_wms_gateway.set_driver_uuid(None)

    response2 = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/track',
        json={'order_id': order.order_id, 'payload': {}},
    )

    assert response2.status_code == 200

    order.update()
    assert order.dispatch_status_info.dispatch_driver_id == 'null'
    assert (
        order.dispatch_status_info.dispatch_courier_first_name
        == first_driver_name
    )

    grocery_dispatch.set_data(
        driver_id=second_driver_id,
        performer_name=second_driver_id,
        performer_first_name=second_driver_name,
        performer_id=second_driver_id,
        eats_profile_id=second_driver_id,
    )
    grocery_wms_gateway.set_driver_uuid(second_driver_id)

    response3 = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/track',
        json={'order_id': order.order_id, 'payload': {}},
    )

    assert response3.status_code == 200

    order.update()
    assert order.dispatch_status_info.dispatch_driver_id == second_driver_id
    assert (
        order.dispatch_status_info.dispatch_courier_first_name
        == second_driver_name
    )


@pytest.mark.now(consts.NOW)
async def test_retry_interval(processing, _run_with_500_from_dispatch):
    retry_count = 2
    event_policy = {
        'retry_count': retry_count,
        'retry_interval': consts.RETRY_INTERVAL_MINUTES * 60,
    }
    order = await _run_with_500_from_dispatch(
        expected_code=200, event_policy=event_policy,
    )

    events = list(processing.events(scope='grocery', queue='processing'))

    event_policy['retry_count'] += 1
    assert len(events) == 1
    assert events[0].payload == {
        'event_policy': event_policy,
        'flow_version': 'grocery_flow_v1',
        'order_id': order.order_id,
        'reason': 'dispatch_track',
        'times_called': 2,
    }

    assert events[0].due == helpers.skip_minutes(consts.RETRY_INTERVAL_MINUTES)


async def test_stop_after(
        _run_with_500_from_dispatch,
        _retry_after_500_dispatch,
        processing,
        mocked_time,
):
    mocked_time.set(consts.NOW_DT)

    # Without retry_interval and error_after we cannot return 429 error, we
    # should return 500 to see it in alert chat/grafana.
    order = await _run_with_500_from_dispatch(
        expected_code=500,
        event_policy={
            'stop_retry_after': {'minutes': consts.STOP_AFTER_MINUTES},
        },
    )

    # try again later, after "stop_after".
    await _retry_after_500_dispatch(
        order=order,
        after_minutes=consts.STOP_AFTER_MINUTES + 1,
        event_policy={
            'stop_retry_after': helpers.skip_minutes(
                consts.STOP_AFTER_MINUTES,
            ),
        },
        expected_code=200,
    )

    events = list(processing.events(scope='grocery', queue='processing'))
    assert not events


async def test_error_after(
        _run_with_500_from_dispatch,
        processing,
        mocked_time,
        _retry_after_500_dispatch,
):
    mocked_time.set(consts.NOW_DT)

    event_policy = {
        'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
    }
    # With `error_after` we don't want to see messages in alert chat, we want
    # to ignore problems until `error_after` happened.
    order = await _run_with_500_from_dispatch(
        expected_code=429, event_policy=event_policy,
    )

    await _retry_after_500_dispatch(
        order=order,
        after_minutes=consts.ERROR_AFTER_MINUTES + 1,
        event_policy=event_policy,
        expected_code=500,
    )

    events = list(processing.events(scope='grocery', queue='processing'))
    assert not events


async def test_retry_after_error_behaviour(
        _run_with_500_from_dispatch,
        processing,
        mocked_time,
        _retry_after_500_dispatch,
):
    event_policy = {
        'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        'stop_retry_after': helpers.skip_minutes(consts.STOP_AFTER_MINUTES),
        'retry_interval': consts.RETRY_INTERVAL_MINUTES * 60,
        'retry_count': 10,
    }
    mocked_time.set(consts.NOW_DT)
    # With error after we don't want to see messages in alert chat, we want to
    # ignore problems until `error_after` happened.
    order = await _run_with_500_from_dispatch(
        expected_code=200, event_policy=event_policy,
    )

    events = list(processing.events(scope='grocery', queue='processing'))

    events_after_first_retry = 1

    assert len(events) == events_after_first_retry
    assert events[0].due == helpers.skip_minutes(consts.RETRY_INTERVAL_MINUTES)

    await _retry_after_500_dispatch(
        order=order,
        after_minutes=consts.ERROR_AFTER_MINUTES + 1,
        event_policy=event_policy,
        expected_code=500,
    )

    await _retry_after_500_dispatch(
        order=order,
        after_minutes=consts.STOP_AFTER_MINUTES + 1,
        event_policy=event_policy,
        expected_code=200,
    )

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == events_after_first_retry


@pytest.fixture
def _retry_after_500_dispatch(mocked_time, taxi_grocery_orders):
    return helpers.retry_processing(
        '/processing/v1/dispatch/track', mocked_time, taxi_grocery_orders,
    )


@pytest.fixture
def _run_with_500_from_dispatch(
        pgsql,
        grocery_depots,
        grocery_cart,
        grocery_dispatch,
        taxi_grocery_orders,
):
    async def _do(expected_code, event_policy, times_called=1):
        dispatch_id = get_new_uuid()

        order = models.Order(
            pgsql=pgsql,
            status='delivering',
            dispatch_status_info=models.DispatchStatusInfo(
                dispatch_id=dispatch_id,
                dispatch_status='delivering',
                dispatch_cargo_status='pickuped',
            ),
            dispatch_flow='grocery_dispatch',
        )
        grocery_depots.add_depot(legacy_depot_id=order.depot_id)

        grocery_cart.set_cart_data(cart_id=order.cart_id)
        grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})

        grocery_dispatch.set_data(info_error_code=500, dispatch_id=dispatch_id)

        response = await taxi_grocery_orders.post(
            '/processing/v1/dispatch/track',
            json={
                'order_id': order.order_id,
                'times_called': times_called,
                'event_policy': event_policy,
                'payload': {},
            },
        )

        assert response.status_code == expected_code

        return order

    return _do


# тест привязан к PREV_TIME, NOW_TIME
@pytest.mark.now(PREV_TIME)
@pytest.mark.config(GROCERY_ORDERS_MIN_DELTA_ETA_TO_UPDATE=120)
@pytest.mark.parametrize(
    'init_eta_mins, new_eta_secs, should_be_updated',
    [(3, 195, False), (3, 300, True), (3, 60, False), (3, 0, True)],
)
async def test_update_after_enough_time_passed(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_dispatch,
        grocery_depots,
        init_eta_mins,
        new_eta_secs,
        should_be_updated,
):
    dispatch_id = get_new_uuid()

    initial_dispatch_performer = models.DispatchPerformer(
        driver_id='1337',
        eats_courier_id='1337',
        courier_full_name='billy herrington',
    )

    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status='delivering',
            dispatch_cargo_status='pickuped',
            dispatch_delivered_eta_ts=NOW_TIME,
            dispatch_cargo_revision=1,
            dispatch_driver_id=initial_dispatch_performer.driver_id,
            dispatch_courier_name=initial_dispatch_performer.courier_full_name,
            dispatch_delivery_eta=init_eta_mins,
        ),
        dispatch_flow='grocery_dispatch',
        order_version=0,
    )

    order.place_id = LAVKA_PLACE_ID
    order.upsert()

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type('eats_dispatch')

    grocery_dispatch.set_data(
        dispatch_id=dispatch_id,
        items=grocery_cart.get_items(),
        order_id=order.order_id,
        status='delivering',
        performer_id=initial_dispatch_performer.driver_id,
        eats_profile_id=initial_dispatch_performer.eats_courier_id,
        performer_name=initial_dispatch_performer.courier_full_name,
        eta=new_eta_secs,
    )
    # Check that update won't happen after small time change
    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/track',
        json={'order_id': order.order_id, 'payload': {}},
    )
    assert response.status_code == 200
    order.update()

    if should_be_updated:
        assert (
            order.dispatch_status_info.dispatch_delivered_eta_ts
            == datetime.datetime.fromisoformat(PREV_TIME)
            + datetime.timedelta(seconds=new_eta_secs)
        )
    else:
        assert (
            order.dispatch_status_info.dispatch_delivered_eta_ts
            == datetime.datetime.fromisoformat(NOW_TIME)
        )


@pytest.mark.experiments3(
    name='grocery_orders_send_to_eats_tracking_v2',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': ['lavka_android', 'eda_webview_iphone'],
                    'arg_name': 'application',
                    'set_elem_type': 'string',
                },
            },
            'value': {
                'send_to_eats_courier': True,
                'send_to_eats_order': True,
            },
        },
    ],
    default_value={'send_to_eats_courier': False, 'send_to_eats_order': False},
    is_config=True,
)
@pytest.mark.parametrize(
    'app_name', ['lavka_iphone', 'eda_webview_iphone', 'lavka_android'],
)
@pytest.mark.parametrize(
    'has_payment_method, has_cancel_reason', [(True, True)],
)
async def test_send_order_info_to_stq(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        grocery_dispatch,
        grocery_eats_gateway,
        grocery_wms_gateway,
        app_name,
        has_payment_method,
        has_cancel_reason,
        grocery_supply,
        mockserver,
):

    order_id = '123456-grocery'
    eats_courier_id = 'eats_courier_id_123'
    dispatch_id = get_new_uuid()
    claim_id_ok = 'claim_id_good'
    claim_id_not_ok = 'claim_id_bad'
    car_number = 'ао322у99'
    driver_id = 'driver_uuid'
    transport_type = 'bicycle'
    courier_full_name = 'Ivanov Ivan Ivanovich'

    @mockserver.json_handler(
        '/grocery-dispatch/internal/dispatch/v1/admin/info',
    )
    def claim_info(request):
        return {
            'dispatches': [
                {
                    'dispatch_id': dispatch_id,
                    'cargo_details': [
                        {
                            'claim_id': claim_id_ok,
                            'claim_status': 'new',
                            'is_current_claim': True,
                        },
                        {
                            'claim_id': claim_id_not_ok,
                            'claim_status': 'cancelled',
                        },
                    ],
                },
            ],
        }

    grocery_wms_gateway.set_driver_uuid(driver_id)
    grocery_dispatch.set_data(
        eats_profile_id=eats_courier_id,
        performer_name=courier_full_name,
        performer_first_name='Ivan',
        transport_type=transport_type,
        dispatch_id=dispatch_id,
        order_id=order_id,
        status='canceled',
        performer_id=driver_id,
        driver_id=driver_id,
    )

    grocery_eats_gateway.set_order_data(
        cancel_reason='payment_failed' if has_cancel_reason else None,
        dispatch_cargo_status='cancelled',
        status='closed',
        app_name=app_name,
    )
    grocery_eats_gateway.set_courier_data(
        claim_id=claim_id_ok,
        personal_phone_id='phone_id_123',
        car_number=car_number,
    )

    order = models.Order(
        pgsql=pgsql,
        order_id=order_id,
        short_order_id='000000-111-2222',
        eats_user_id='eats_user_id_0',
        status='closed',
        created=PREV_TIME,
        updated=NOW_TIME,
        status_updated=NOW_TIME,
        app_info=f'app_name={app_name}',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status='accepted',
            dispatch_cargo_status='accepted',
            dispatch_delivered_eta_ts=NOW_TIME,
            dispatch_courier_id='courier_id',
            dispatch_courier_name='Aleksandr',
            dispatch_courier_first_name='Ivan',
            dispatch_transport_type='car',
            dispatch_car_number=car_number,
        ),
        cancel_reason_type=grocery_eats_gateway.order_info.get(
            'cancel_reason',
        ),
        depot_id='12345',
        dispatch_flow='grocery_dispatch',
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id, region_id=213)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    if has_payment_method:
        grocery_cart.set_payment_method(
            {'type': 'card', 'id': 'test_payment_method_id'},
        )
    grocery_cart.set_delivery_type('courier')

    grocery_supply.check_courier_info(courier_id=eats_courier_id)
    grocery_supply.set_courier_response(
        response={
            'courier_id': eats_courier_id,
            'transport_type': transport_type,
            'full_name': courier_full_name,
            'personal_phone_id': 'phone_id_123',
        },
    )
    grocery_eats_gateway.set_order_data(suffix_stq_task_id='42')

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/track',
        json={'order_id': order.order_id, 'payload': {}, 'times_called': 42},
    )

    assert response.status_code == 200
    assert grocery_eats_gateway.times_stq_orders() == (
        1 if app_name != 'lavka_iphone' else 0
    )
    assert grocery_eats_gateway.times_stq_couriers() == (
        1 if app_name != 'lavka_iphone' else 0
    )
    assert claim_info.times_called == (1 if app_name != 'lavka_iphone' else 0)
