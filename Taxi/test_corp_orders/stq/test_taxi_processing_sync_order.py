# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import copy
import datetime

import bson
import pytest

from corp_orders.stq.taxi_processing import corp_taxi_processing_sync_order

NOW = datetime.datetime.utcnow().replace(microsecond=0)

pytestmark = [pytest.mark.now(NOW.isoformat())]


def now_delta(seconds: int):
    return NOW + datetime.timedelta(seconds=seconds)


ORDER_ID = '1234567'
POINTS = [
    {
        'fullname': 'Россия, Москва, Садовническая, 82с2',
        'geopoint': [55.735525, 37.642474],
        'porchnumber': '1',
        'extra_data': {
            'comment': 'source comment',
            'contact_phone_id': bson.ObjectId('5f20681b3e182e8a2c6cd200'),
            'apartment': '1',
            'floor': '1',
        },
    },
    {
        'fullname': 'Россия, Москва, 1-й Красногвардейский проезд, 21с1',
        'geopoint': [55.750028, 37.534406],
    },
    {
        'fullname': 'Россия, Москва, Льва Толстого, 16',
        'geopoint': [55.733974, 37.587093],
        'porchnumber': '3',
        'extra_data': {
            'comment': 'interim comment',
            'contact_phone_id': bson.ObjectId('5f20681b3e182e8a2c6cd202'),
            'apartment': '3',
            'floor': '3',
        },
    },
]
COST_CENTER = 'Мопед'
COST_CENTERS = [{'id': 'cost_center', 'value': 'Лодки', 'title': 'Центр'}]

CORP_ORDER = {
    '_id': ORDER_ID,
    '_type': 'soon',
    'city': 'Москва',
    'comment': '2 минуты, Турецкий',
    'nearest_zone': 'moscow',
    'application': 'android',
    'class': 'econom',
    'client_id': 'client_id_1',
    'corp_user': {'user_id': 'user_id_1', 'department_id': 'department_id_1'},
    'extra_user_phone_id': bson.ObjectId('5f20681b3e182e8a2c6cd299'),
    'status': 'finished',
    'taxi_status': 'complete',
    'created_date': now_delta(-100),
    'order_updated': now_delta(-10),
    'due_date': now_delta(-50),
    'requirements': {'door_to_door': True},
    'source': POINTS[0],
    'destination': POINTS[-1],
    'interim_destinations': POINTS[1:-1],
    'cost_center': {'user': COST_CENTER},
    'cost_centers': {'user': COST_CENTERS},
    'combo_order': {'delivery_id': 'delivery_1'},
    'distance': 1000,
    'waiting': {
        'waiting_cost': 60.6,
        'waiting_in_depart_time': 10,
        'waiting_in_transit_time': 20,
        'waiting_time': 30,
    },
    'start_waiting_time': now_delta(-40),
    'performer': {
        'car': 'лада веста white О123ОО',
        'vehicle': {
            'color_code': '000000',
            'model': 'лада веста',
            'number': 'О123ОО',
        },
        'park_name': 'Село',
    },
    'started_date': now_delta(-30),
    'finished_date': now_delta(-10),
    'processing': {'version': 10},
}

# fmt: off
STATUS_UPDATE_ASSIGN = {
    'q': 'requestconfirm_assigned',
    's': 'assigned',
    'i': 0,
    'c': now_delta(-70).isoformat(),
}
STATUS_UPDATE_AUTOREORDER = {
    'q': 'autoreorder',
    's': 'pending',
    'c': now_delta(-60).isoformat(),
}
STATUS_UPDATE_ASSIGN_2 = {
    'q': 'requestconfirm_assigned',
    's': 'assigned',
    'i': 1,
    'c': now_delta(-50).isoformat(),
}
STATUS_UPDATE_WAITING = {
    'q': 'requestconfirm_waiting',
    't': 'waiting',
    'i': 1,
    'c': now_delta(-40).isoformat(),
}
STATUS_UPDATE_TRANSPORTING = {
    'q': 'requestconfirm_transporting',
    't': 'transporting',
    'i': 1,
    'c': now_delta(-30).isoformat(),
}
STATUS_UPDATE_DESTINATIONS_CHANGED = {
    'q': 'destinations_changed',
    'c': now_delta(-20).isoformat(),
}
STATUS_UPDATE_FINISHED_COMPLETE = {
    'q': 'requestconfirm_complete',
    's': 'finished',
    't': 'complete',
    'c': now_delta(-10).isoformat(),
}

STATUS_UPDATE_PARK_CANCELLED = {
    'q': 'requestconfirm_cancelled',
    's': 'finished',
    't': 'cancelled',
    'c': now_delta(-10).isoformat(),
}
STATUS_UPDATE_USER_CANCELLED = {
    'q': 'cancel',
    't': 'cancelled',
    'c': now_delta(-10).isoformat(),
}
STATUS_UPDATE_FAILED = {
    'q': 'requestconfirm_failed',
    't': 'failed',
    'c': now_delta(-10).isoformat(),
}
STATUS_UPDATE_EXPIRE = {
    'q': 'expire',
    's': 'finished',
    't': 'expired',
    'c': now_delta(-10).isoformat(),
}
# fmt: on

STATUS_UPDATES_BASE = [
    STATUS_UPDATE_ASSIGN,
    STATUS_UPDATE_AUTOREORDER,
    STATUS_UPDATE_ASSIGN_2,
    STATUS_UPDATE_WAITING,
    STATUS_UPDATE_TRANSPORTING,
    STATUS_UPDATE_DESTINATIONS_CHANGED,
]

STATUS_UPDATES_FINISHED_COMPLETE = STATUS_UPDATES_BASE + [
    STATUS_UPDATE_FINISHED_COMPLETE,
]

ORDER_PROC = {
    '_id': ORDER_ID,
    'created': now_delta(-100).isoformat(),
    'updated': now_delta(-10).isoformat(),
    'order': {
        'application': 'android',
        'request': {
            'due': now_delta(-50).isoformat(),
            'payment': {'type': 'corp'},
            'class': ['econom'],
            'comment': '2 минуты, Турецкий',
            'extra_user_phone_id': bson.ObjectId('5f20681b3e182e8a2c6cd299'),
            'corp': {
                'client_comment': 'comment',
                'client_id': 'client_id_1',
                'cost_center': COST_CENTER,
                'cost_centers': COST_CENTERS,
                'user_id': 'user_id_1',
                'combo_order': {'delivery_id': 'delivery_1'},
            },
            'requirements': {'door_to_door': True},
            'source': POINTS[0],
            'destinations': POINTS[1:],
        },
        '_type': 'soon',
        'city': 'Москва',
        'nz': 'moscow',
        'taximeter_receipt': {
            'details': [
                {'meter_value': 10, 'service_type': 'waiting'},
                {'meter_value': 20, 'service_type': 'waiting_in_transit'},
            ],
            'dst_actual_point': {'lon': 37.64, 'lat': 55.73},
            'total_distance': 1000,
        },
        'calc_info': {'waiting_cost': 60.6, 'waiting_time': 30},
        'status': 'finished',
        'taxi_status': 'complete',
        'performer': {'clid': '643753730233'},
    },
    'candidates': [
        {
            'driver_id': '12345',
            'car': 'лада веста',
            'car_color': 'white',
            'car_color_code': '000000',
            'car_model': 'лада веста',
            'car_number': 'О123ОО',
        },
    ],
    'order_info': {
        'statistics': {'status_updates': STATUS_UPDATES_FINISHED_COMPLETE},
    },
    'processing': {'version': 10},
}

# fmt: off
ORDER_PROC_FIELDS = [
    '_id',
    'order._type',
    'order.status',
    'order.taxi_status',
    'order.status_updated',  # TODO: deprecated
    'order.city',
    'order.nz',
    'order.application',
    'order.request.due',
    'order.request.comment',
    'order.request.corp.client_id',
    'order.request.corp.user_id',
    'order.request.corp.cost_center',
    'order.request.corp.cost_centers',
    'order.request.corp.combo_order',
    'order.request.payment.type',
    'order.request.source.fullname',
    'order.request.source.geopoint',
    'order.request.source.porchnumber',
    'order.request.source.extra_data.comment',
    'order.request.source.extra_data.apartment',
    'order.request.source.extra_data.floor',
    'order.request.source.extra_data.contact_phone_id',
    'order.request.destinations.fullname',
    'order.request.destinations.geopoint',
    'order.request.destinations.porchnumber',
    'order.request.destinations.extra_data.comment',
    'order.request.destinations.extra_data.apartment',
    'order.request.destinations.extra_data.floor',
    'order.request.destinations.extra_data.contact_phone_id',
    'order.request.requirements',
    'order.request.class',
    'order.request.extra_user_phone_id',
    'order.calc_info.waiting_cost',
    'order.calc_info.waiting_time',
    'order.taximeter_receipt.total_distance',
    'order.taximeter_receipt.dst_actual_point.lon',
    'order.taximeter_receipt.dst_actual_point.lat',
    'order.taximeter_receipt.details.meter_value',
    'order.taximeter_receipt.details.service_type',
    'order.performer.clid',
    'order_info.statistics.s',
    'order_info.statistics.status_updates.s',
    'order_info.statistics.status_updates.t',
    'order_info.statistics.status_updates.q',
    'order_info.statistics.status_updates.c',
    'candidates.driver_id',
    'candidates.name',
    'candidates.car_color',
    'candidates.car_color_code',
    'candidates.car_model',
    'candidates.car_number',
    'processing.version',
    'created',
    'updated',
]
# fmt:on


async def test_base(
        stq3_context,
        db,
        load_json,
        mock_order_core,
        mock_corp_users,
        mock_parks_replica,
):
    mock_order_core.data.order_procs = [ORDER_PROC]
    mock_order_core.data.order_proc_fields = ORDER_PROC_FIELDS

    await corp_taxi_processing_sync_order.task(stq3_context, ORDER_ID)

    assert mock_order_core.order_proc_get_fields.times_called == 1

    corp_order = await db.corp_orders.find_one({'_id': ORDER_ID})
    assert corp_order.pop('created')
    assert corp_order.pop('updated')
    assert corp_order == CORP_ORDER


@pytest.mark.parametrize(
    'status_updates, status, taxi_status',
    [
        pytest.param(
            STATUS_UPDATES_BASE + [STATUS_UPDATE_PARK_CANCELLED],
            'finished',
            'cancelled',
            id='park cancelled',
        ),
        pytest.param(
            STATUS_UPDATES_BASE + [STATUS_UPDATE_USER_CANCELLED],
            'transporting',
            'cancelled',
            id='user cancelled',
        ),
        pytest.param(
            STATUS_UPDATES_BASE + [STATUS_UPDATE_FAILED],
            'transporting',
            'failed',
            id='failed',
        ),
        pytest.param(
            [STATUS_UPDATE_EXPIRE], 'finished', 'expired', id='expire',
        ),
    ],
)
async def test_order_finished_not_completed(
        stq3_context,
        db,
        load_json,
        mock_order_core,
        mock_corp_users,
        mock_parks_replica,
        status_updates,
        status,
        taxi_status,
):
    order_proc = copy.deepcopy(ORDER_PROC)
    order_proc['order']['status'] = status
    order_proc['order']['taxi_status'] = taxi_status

    order_proc['order_info']['statistics']['status_updates'] = status_updates

    mock_order_core.data.order_procs = [order_proc]
    mock_order_core.data.order_proc_fields = ORDER_PROC_FIELDS

    await corp_taxi_processing_sync_order.task(stq3_context, ORDER_ID)

    assert mock_order_core.order_proc_get_fields.times_called == 1

    corp_order = await db.corp_orders.find_one({'_id': ORDER_ID})

    assert corp_order['finished_date'] == now_delta(-10)
    assert corp_order['status'] == status
    assert corp_order['taxi_status'] == taxi_status


async def test_corpweb(
        stq3_context,
        db,
        load_json,
        mock_order_core,
        mock_corp_users,
        mock_parks_replica,
):
    CORPWEB = 'corpweb'

    order_proc = copy.deepcopy(ORDER_PROC)
    expected_corp_order = copy.deepcopy(CORP_ORDER)

    order_proc['order']['application'] = CORPWEB
    expected_corp_order['application'] = CORPWEB

    expected_corp_order['cost_center'] = {'cabinet': COST_CENTER}
    expected_corp_order['cost_centers'] = {'cabinet': COST_CENTERS}

    mock_order_core.data.order_procs = [order_proc]

    await corp_taxi_processing_sync_order.task(stq3_context, ORDER_ID)

    corp_order = await db.corp_orders.find_one({'_id': ORDER_ID})
    assert corp_order.pop('created')
    assert corp_order.pop('updated')
    assert corp_order == expected_corp_order


async def test_update_order(
        stq3_context,
        db,
        load_json,
        mock_order_core,
        mock_corp_users,
        mock_parks_replica,
):
    await db.corp_orders.insert_one(
        dict(
            CORP_ORDER,
            **{'created': NOW, 'updated': NOW, 'processing': {'version': 4}},
        ),
    )

    order_proc = copy.deepcopy(ORDER_PROC)
    expected = copy.deepcopy(CORP_ORDER)

    order_proc['order']['nz'] = 'spb'

    mock_order_core.data.order_procs = [order_proc]

    await corp_taxi_processing_sync_order.task(stq3_context, ORDER_ID)

    corp_order = await db.corp_orders.find_one({'_id': ORDER_ID})
    expected['nearest_zone'] = 'spb'

    assert corp_order.pop('created')
    assert corp_order.pop('updated')
    assert corp_order == expected


async def test_outdated_order(
        stq3_context,
        db,
        load_json,
        mock_order_core,
        mock_corp_users,
        mock_parks_replica,
):
    mock_order_core.data.order_procs = [ORDER_PROC]

    last_update = now_delta(-1)

    corp_order = copy.deepcopy(CORP_ORDER)
    corp_order['order_updated'] = last_update

    await db.corp_orders.insert_one(
        dict(
            corp_order,
            **{
                'created': NOW,
                'updated': last_update,
                'processing': {'version': 4},
            },
        ),
    )

    await corp_taxi_processing_sync_order.task(stq3_context, ORDER_ID)

    corp_order = await db.corp_orders.find_one({'_id': ORDER_ID})
    assert corp_order['updated'] == last_update


async def test_not_corp_order(
        stq3_context, db, mock_order_core, mock_corp_users,
):
    order_proc = copy.deepcopy(ORDER_PROC)
    order_proc['order']['request']['payment']['type'] = 'card'

    mock_order_core.data.order_procs = [order_proc]

    await corp_taxi_processing_sync_order.task(stq3_context, ORDER_ID)

    corp_order = await db.corp_orders.find_one({'_id': ORDER_ID})
    assert corp_order is None


async def test_user_not_exists(
        stq3_context,
        db,
        load_json,
        mock_order_core,
        mock_corp_users,
        mock_parks_replica,
):
    order_proc = copy.deepcopy(ORDER_PROC)
    expected = copy.deepcopy(CORP_ORDER)

    order_proc['order']['request']['corp']['user_id'] = 'unknown'
    expected['corp_user'] = {'user_id': 'unknown'}  # wo department_id

    mock_order_core.data.order_procs = [order_proc]

    await corp_taxi_processing_sync_order.task(stq3_context, ORDER_ID)

    corp_order = await db.corp_orders.find_one({'_id': ORDER_ID})

    assert corp_order.pop('created')
    assert corp_order.pop('updated')
    assert corp_order == expected
