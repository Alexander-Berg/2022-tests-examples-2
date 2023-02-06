# pylint: disable=too-many-lines
import copy
import datetime

import pytest

from tests_grocery_dispatch import configs
from tests_grocery_dispatch import constants as const
from tests_grocery_dispatch import models

DEPOT_ID_CACHE = '1'
LOGISTIC_GROUP = '28'
LOGISTIC_GROUP_CACHE = '1'

CREATE_REQUEST_DATA_CACHE = {
    'order_id': const.ORDER_ID,
    'short_order_id': const.SHORT_ORDER_ID,
    'depot_id': DEPOT_ID_CACHE,
    'location': {'lon': 39.60258, 'lat': 52.569089},
    'zone_type': 'pedestrian',
    'created_at': '2020-10-05T16:28:00.000Z',
    'max_eta': 900,
    'items': [
        {
            'item_id': 'item_id_1',
            'title': 'some product',
            'price': '12.99',
            'currency': 'RUB',
            'quantity': '1',
        },
        {
            'item_id': 'item_id_2',
            'title': 'some product_2',
            'price': '13.88',
            'currency': 'RUB',
            'quantity': '1',
        },
    ],
    'user_locale': 'ru',
    'personal_phone_id': const.PERSONAL_PHONE_ID,
    'comment': 'user comment',
    'door_code': 'doorcode',
    'door_code_extra': 'door_code_extra',
    'doorbell_name': 'doorbell_name',
    'building_name': 'building_name',
    'floor': 'floor',
    'flat': 'flat',
    'city': 'city',
    'street': 'street',
}

PARK_ID = '123432'
DRIVER_ID = '23423'


def _make_first_point():
    first_point = copy.deepcopy(models.FIRST_POINT)
    first_point.comment = None
    return first_point


FIRST_POINT = _make_first_point()


def _add_suffix(shelf_store):
    if shelf_store == 'store':
        return ''
    if shelf_store == 'markdown':
        return ':st-md'
    if shelf_store == 'parcel':
        return ':st-pa'
    assert False
    return None


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
@pytest.mark.parametrize(
    ['item1_qty', 'item2_qty', 'response_code'],
    [('1', '1', 200), ('1', '0', 200), ('0', '1', 200), ('0', '0', 406)],
)
async def test_basic_create(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
        item1_qty,
        item2_qty,
        response_code,
        logistic_dispatcher,
):
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)

    # will be checked at cargo mock
    cargo.short_order_id = const.SHORT_ORDER_ID
    cargo.custom_context = {
        'delivery_flags': {
            'is_forbidden_to_be_in_batch': False,
            'assign_rover': False,
        },
        'external_feature_prices': {'external_order_created_ts': const.NOW_TS},
        'depot_id': const.DEPOT_ID,
        'lavka_has_market_parcel': False,
        'order_id': const.ORDER_ID,
        'dispatch_wave': 0,
        'created': request_data['created_at'],
        'weight': 0.0,
        'dispatch_id': 'placeholder',
        'brand_name': 'brand_name_lavka',
        'dispatch_type': 'pull-dispatch',
        'region_id': 213,
        'personal_phone_id': const.PERSONAL_PHONE_ID,
    }

    grocery_supply.add_log_group(const.DEPOT_ID, 'ya_eats_group')

    expected_cargo_called_times = 1 if response_code == 200 else 0

    request_data['items'][0]['quantity'] = item1_qty
    request_data['items'][1]['quantity'] = item2_qty

    request_items = []
    if int(item1_qty) > 0:
        request_items.append(request_data['items'][0])
    if int(item2_qty) > 0:
        request_items.append(request_data['items'][1])

    cargo.check_request(
        route_points=[FIRST_POINT, models.CLIENT_POINT, models.RETURN_POINT],
        items=cargo.convert_items(request_items) + [models.FAKE_ITEM],
    )

    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response1.status_code == response_code
    assert cargo.times_create_accepted_called() == expected_cargo_called_times

    response2 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response2.status_code == response_code
    if response_code == 200:
        assert response1.json() == response2.json()

    assert cargo.times_create_accepted_called() == expected_cargo_called_times


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_comment_create(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        cargo_pg,
        grocery_dispatch_pg,
        experiments3,
        grocery_supply,
):
    cargo.set_data(claim_id=const.CLAIM_ID)

    cargo.check_request(
        route_points=[FIRST_POINT, models.CLIENT_POINT, models.RETURN_POINT],
        items=cargo.convert_items(models.CREATE_REQUEST_DATA['items'])
        + [models.FAKE_ITEM],
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', models.CREATE_REQUEST_DATA,
    )
    assert response.status_code == 200
    assert cargo.times_create_accepted_called() == 1

    claim = cargo_pg.get_claim(claim_id=const.CLAIM_ID)
    dispatch = grocery_dispatch_pg.get_dispatch(
        dispatch_id=response.json()['dispatch_id'],
    )
    assert dispatch.wave == claim.wave


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG_FULL
@configs.DISPATCH_COMMENT_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_comment_create_leave_under_door_taxi(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
):
    client_point = copy.deepcopy(models.CLIENT_POINT_LEAVE_UNDER_DOOR)
    client_point.comment = 'leave_under_door_comment_taxi user comment'

    cargo.check_request(
        route_points=[models.FIRST_POINT, client_point],
        items=cargo.convert_items(models.CREATE_REQUEST_DATA['items']),
    )
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['leave_under_door'] = True
    request_data['zone_type'] = 'yandex_taxi'

    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response1.status_code == 200
    assert cargo.times_create_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_comment_create_meet_outside(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
):
    client_point = copy.deepcopy(models.CLIENT_POINT)
    client_point.meet_outside = True
    client_point.no_door_call = True

    cargo.check_request(
        route_points=[FIRST_POINT, client_point, models.RETURN_POINT],
        items=cargo.convert_items(models.CREATE_REQUEST_DATA['items'])
        + [models.FAKE_ITEM],
    )
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['meet_outside'] = True
    request_data['no_door_call'] = True

    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response1.status_code == 200
    assert cargo.times_create_accepted_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
@pytest.mark.experiments3(
    name='grocery_dispatch_comments',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={},
    is_config=True,
)
async def test_comment_create_leave_under_door_disable_by_config(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
):
    second_point = copy.deepcopy(models.CLIENT_POINT_LEAVE_UNDER_DOOR)
    second_point.comment = 'user comment'

    cargo.check_request(
        route_points=[FIRST_POINT, second_point, models.RETURN_POINT],
        items=cargo.convert_items(models.CREATE_REQUEST_DATA['items'])
        + [models.FAKE_ITEM],
    )
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['leave_under_door'] = True

    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response1.status_code == 200
    assert cargo.times_create_accepted_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_DEFAULT
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG
@configs.DISPATCH_COMMENT_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_comment_create_no_door_call_meet_outside(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
):
    first_point = copy.deepcopy(models.FIRST_POINT)
    first_point.comment = None

    second_point = copy.deepcopy(models.CLIENT_POINT)
    second_point.comment = (
        'meet_outside_comment no_door_call_comment user comment'
    )
    second_point.meet_outside = True
    second_point.no_door_call = True

    cargo.check_request(
        route_points=[first_point, second_point, models.RETURN_POINT],
        items=cargo.convert_items(models.CREATE_REQUEST_DATA['items'])
        + [models.FAKE_ITEM],
    )
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['meet_outside'] = True
    request_data['no_door_call'] = True

    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response1.status_code == 200
    assert cargo.times_create_accepted_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_DEFAULT
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG
@configs.DISPATCH_COMMENT_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
@pytest.mark.parametrize('leave_under_door', [True, False])
async def test_comment_create_pull_dispatch(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        leave_under_door,
        experiments3,
        grocery_supply,
):
    first_point = copy.deepcopy(models.FIRST_POINT)
    first_point.comment = None

    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    if leave_under_door:
        request_data['leave_under_door'] = True

    client_point = (
        models.CLIENT_POINT_LEAVE_UNDER_DOOR
        if leave_under_door
        else models.CLIENT_POINT
    )

    cargo.check_request(
        route_points=[first_point, client_point, models.RETURN_POINT],
        items=cargo.convert_items(models.CREATE_REQUEST_DATA['items'])
        + [models.FAKE_ITEM],
    )

    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response1.status_code == 200
    assert cargo.times_create_accepted_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_PULL_DISPATCH
@configs.DISPATCH_GENERAL_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
@pytest.mark.experiments3(
    name='grocery_dispatch_priority',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Big weight',
            'predicate': {
                'init': {
                    'value': 10000,
                    'arg_name': 'order_weight',
                    'arg_type': 'double',
                },
                'type': 'gt',
            },
            'value': {'dispatches': ['cargo_taxi']},
        },
        {
            'title': 'cargo',
            'predicate': {'type': 'true'},
            'value': {'dispatches': ['cargo_sync']},
        },
    ],
    is_config=True,
)
async def test_create_weight_fallback(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
):
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['items'][0]['quantity'] = '5'
    request_data['items'][0]['weight'] = 1500
    request_data['items'][0]['height'] = 1700
    request_data['items'][0]['width'] = 1600
    request_data['items'][0]['depth'] = 500
    request_data['items'][1]['quantity'] = '3'
    request_data['items'][1]['weight'] = 1200
    request_data['items'][1]['height'] = 2500
    request_data['items'][1]['width'] = 300
    request_data['items'][1]['depth'] = 100

    cargo.check_request(
        route_points=[models.FIRST_POINT, models.CLIENT_POINT],
        items=cargo.convert_items(request_data['items']),
        taxi_class='express',
        claim_kind='delivery_service',
        taxi_classes=['courier'],
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response.status_code == 200
    assert cargo.times_create_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_PULL_DISPATCH
@configs.DISPATCH_GENERAL_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
@pytest.mark.experiments3(
    name='grocery_dispatch_priority',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Has parcel',
            'predicate': {
                'init': {
                    'value': 1,
                    'arg_name': 'has_parcel',
                    'arg_type': 'int',
                },
                'type': 'eq',
            },
            'value': {'dispatches': ['cargo_taxi']},
        },
        {
            'title': 'cargo',
            'predicate': {'type': 'true'},
            'value': {'dispatches': ['cargo_sync']},
        },
    ],
    is_config=True,
)
async def test_create_parcel_fallback(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
):
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['items'][0]['item_id'] = request_data['items'][0][
        'item_id'
    ] + _add_suffix('parcel')

    cargo.check_request(
        route_points=[models.FIRST_POINT, models.CLIENT_POINT],
        items=cargo.convert_items(request_data['items']),
        taxi_class='express',
        claim_kind='delivery_service',
        taxi_classes=['courier'],
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response.status_code == 200
    assert cargo.times_create_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_PULL_DISPATCH
@configs.DISPATCH_GENERAL_CONFIG
@configs.MODELER_DECISION_CONFIG
@configs.ETA_THRESHOLD_CONFIG
@configs.MODELER_ORDERS_CONFIG
@pytest.mark.experiments3(
    name='grocery_dispatch_priority',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Modeler fallback',
            'predicate': {
                'init': {'arg_name': 'modeler_decision'},
                'type': 'bool',
            },
            'value': {'dispatches': ['cargo_taxi']},
        },
        {
            'title': 'cargo',
            'predicate': {'type': 'true'},
            'value': {'dispatches': ['cargo_sync']},
        },
    ],
    is_config=True,
)
@pytest.mark.parametrize('estimate_time', [1, 24 * 60])
async def test_create_time_fallback(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
        logistic_dispatcher,
        estimate_time,
):
    grocery_supply.add_log_group(const.DEPOT_ID, '28')

    delivery_finished = int(
        (
            datetime.datetime.fromisoformat(const.NOW)
            + datetime.timedelta(minutes=estimate_time)
        ).timestamp(),
    )

    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    logistic_dispatcher.set_response(delivery_finished_at=delivery_finished)

    if estimate_time < 60:
        first_point = copy.deepcopy(models.FIRST_POINT)
        first_point.comment = None

        cargo.check_request(
            route_points=[
                first_point,
                models.CLIENT_POINT,
                models.RETURN_POINT,
            ],
            items=cargo.convert_items(models.CREATE_REQUEST_DATA['items'])
            + [models.FAKE_ITEM],
            taxi_class='lavka',
            claim_kind='platform_usage',
            taxi_classes=['lavka'],
        )
    else:
        cargo.check_request(
            route_points=[models.FIRST_POINT, models.CLIENT_POINT],
            items=cargo.convert_items(request_data['items']),
            taxi_class='express',
            claim_kind='delivery_service',
            taxi_classes=['courier'],
        )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response.status_code == 200
    if estimate_time < 60:
        assert cargo.times_create_called() == 0
        assert cargo.times_create_accepted_called() == 1
    else:
        assert cargo.times_create_called() == 1
        assert cargo.times_create_accepted_called() == 0


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_DEFAULT
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
@pytest.mark.parametrize(
    ['depot_id', 'order_info', 'logistic_group'],
    [
        (const.DEPOT_ID, models.CREATE_REQUEST_DATA, LOGISTIC_GROUP),
        (DEPOT_ID_CACHE, CREATE_REQUEST_DATA_CACHE, LOGISTIC_GROUP_CACHE),
    ],
)
async def test_create_check_logistic_group(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_depots,
        grocery_supply,
        logistic_dispatcher,
        depot_id,
        order_info,
        logistic_group,
):
    estimate_time = 1

    grocery_depots.clear_depots()
    grocery_depots.add_depot(depot_test_id=int(depot_id), auto_add_zone=False)
    await taxi_grocery_dispatch.invalidate_caches()

    grocery_supply.add_log_group(depot_id, '28')

    delivery_finished = int(
        (
            datetime.datetime.fromisoformat(const.NOW)
            + datetime.timedelta(minutes=estimate_time)
        ).timestamp(),
    )

    request_data = copy.deepcopy(order_info)
    logistic_dispatcher.set_response(
        delivery_finished_at=delivery_finished, logistic_group=logistic_group,
    )

    first_point = copy.deepcopy(models.FIRST_POINT)
    first_point.comment = None

    cargo.check_requirements_flag = True
    cargo.requirement_logistic_group = logistic_group
    cargo.requirement_shift_type = (
        'eats' if (logistic_group == '28') else 'grocery'
    )

    cargo.check_request(
        route_points=[first_point, models.CLIENT_POINT, models.RETURN_POINT],
        items=cargo.convert_items(order_info['items']) + [models.FAKE_ITEM],
        taxi_class='express',
        claim_kind='platform_usage',
        taxi_classes=['lavka'],
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response.status_code == 200
    assert cargo.times_create_accepted_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_PULL_DISPATCH
@configs.DISPATCH_GENERAL_CONFIG
@configs.MODELER_DECISION_CONFIG
@configs.ETA_THRESHOLD_CONFIG
@configs.MODELER_ORDERS_CONFIG
@pytest.mark.experiments3(
    name='grocery_dispatch_priority',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Modeler fallback',
            'predicate': {
                'init': {'arg_name': 'modeler_decision'},
                'type': 'bool',
            },
            'value': {'dispatches': ['cargo_taxi']},
        },
        {
            'title': 'cargo',
            'predicate': {'type': 'true'},
            'value': {'dispatches': ['cargo_sync']},
        },
    ],
    is_config=True,
)
@pytest.mark.parametrize('estimate_time', [1, 24 * 60])
async def test_create_time_fallback_enabled(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
        logistic_dispatcher,
        estimate_time,
        grocery_shifts_queue_info,
        queue_info,
):
    grocery_supply.add_log_group(const.DEPOT_ID, '28')

    delivery_finished = int(
        (
            datetime.datetime.fromisoformat(const.NOW)
            + datetime.timedelta(minutes=estimate_time)
        ).timestamp(),
    )

    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    logistic_dispatcher.set_response(delivery_finished_at=delivery_finished)

    if estimate_time < 60:
        first_point = copy.deepcopy(models.FIRST_POINT)
        first_point.comment = None

        cargo.check_request(
            route_points=[
                first_point,
                models.CLIENT_POINT,
                models.RETURN_POINT,
            ],
            items=cargo.convert_items(models.CREATE_REQUEST_DATA['items'])
            + [models.FAKE_ITEM],
            taxi_class='lavka',
            claim_kind='platform_usage',
            taxi_classes=['lavka'],
        )
    else:
        cargo.check_request(
            route_points=[models.FIRST_POINT, models.CLIENT_POINT],
            items=cargo.convert_items(request_data['items']),
            taxi_class='express',
            claim_kind='delivery_service',
            taxi_classes=['courier'],
        )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response.status_code == 200
    if estimate_time < 60:
        assert cargo.times_create_called() == 0
        assert cargo.times_create_accepted_called() == 1
    else:
        assert cargo.times_create_called() == 1
        assert cargo.times_create_accepted_called() == 0


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_DEFAULT
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_COMMENT_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
@pytest.mark.experiments3(
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='grocery_dispatch_priority',
    default_value={'dispatches': ['cargo_sync']},
    is_config=True,
)
async def test_create_sync(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
):
    first_point = copy.deepcopy(models.FIRST_POINT)
    first_point.comment = None

    second_point = copy.deepcopy(models.CLIENT_POINT)

    cargo.check_request(
        route_points=[first_point, second_point, models.RETURN_POINT],
        items=cargo.convert_items(models.CREATE_REQUEST_DATA['items'])
        + [models.FAKE_ITEM],
        taxi_class='express',
    )
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)

    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response1.status_code == 200
    assert cargo.times_create_called() == 0
    assert cargo.times_create_accepted_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_DEFAULT
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_COMMENT_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG_UNITED_DISPATCH
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_create_united_dispatch_controller(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
):
    first_point = copy.deepcopy(models.FIRST_POINT)
    first_point.comment = None

    second_point = copy.deepcopy(models.CLIENT_POINT)
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)

    cargo.custom_context = {
        'delivery_flags': {
            'is_forbidden_to_be_in_batch': False,
            'assign_rover': False,
        },
        'external_feature_prices': {'external_order_created_ts': const.NOW_TS},
        'depot_id': const.DEPOT_ID,
        'lavka_has_market_parcel': False,
        'order_id': const.ORDER_ID,
        'dispatch_wave': 0,
        'created': request_data['created_at'],
        'weight': 0.0,
        'dispatch_id': 'placeholder',
        'router_intent': 'united-dispatch',
        'brand_name': 'brand_name_lavka',
        'dispatch_type': 'pull-dispatch',
        'region_id': 213,
        'personal_phone_id': const.PERSONAL_PHONE_ID,
    }

    cargo.check_request(
        route_points=[first_point, second_point, models.RETURN_POINT],
        items=cargo.convert_items(request_data['items']) + [models.FAKE_ITEM],
        taxi_class='express',
    )

    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response1.status_code == 200
    assert cargo.times_create_called() == 0
    assert cargo.times_create_accepted_called() == 1


@configs.DISPATCH_CLAIM_CONFIG_DEFAULT
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
@pytest.mark.parametrize('item_tags', [['hot'], ['unknown_tag']])
async def test_create_order_with_item_tags(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        cargo,
        experiments3,
        grocery_supply,
        item_tags,
):
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['items'][0]['item_tags'] = item_tags

    exp3_recorder = experiments3.record_match_tries(
        'grocery_dispatch_priority',
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    assert match_tries[0].kwargs['item_tags'] == item_tags
    assert match_tries[0].kwargs['wave'] == 0

    assert response.status_code == 200
    assert cargo.times_create_accepted_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_PULL_DISPATCH
@configs.MODELER_DECISION_CONFIG_DISABLED
@pytest.mark.experiments3(
    name='grocery_dispatch_lavka_dispatch_options',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'dispatch_option': 'taxi_dispatch',
                'enable_pull_dispatch': False,
            },
        },
    ],
    is_config=True,
)
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG_TAXI
async def test_create_cargo_taxi_controller(taxi_grocery_dispatch, cargo):
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    cargo.check_request(
        route_points=[models.FIRST_POINT, models.CLIENT_POINT],
        items=cargo.convert_items(request_data['items']),
        taxi_class='express',
        claim_kind='delivery_service',
        taxi_classes=['courier'],
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response.status_code == 200
    assert cargo.times_create_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG_FULL
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_basic_create_taxi_zone(taxi_grocery_dispatch, cargo):
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['zone_type'] = 'yandex_taxi'

    cargo.short_order_id = const.SHORT_ORDER_ID
    cargo.custom_context = {
        'delivery_flags': {'is_forbidden_to_be_in_batch': False},
        'external_feature_prices': {'external_order_created_ts': const.NOW_TS},
        'depot_id': const.DEPOT_ID,
        'lavka_has_market_parcel': False,
        'order_id': const.ORDER_ID,
        'dispatch_wave': 0,
        'created': request_data['created_at'],
        'weight': 0.0,
        'dispatch_id': 'placeholder',
        'region_id': 213,
        'personal_phone_id': const.PERSONAL_PHONE_ID,
    }
    cargo.check_request(claim_kind='delivery_service')

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )

    assert response.status_code == 200


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG
@configs.DISPATCH_COMMENT_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_create_with_market_slot(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
        grocery_dispatch_pg,
        stq,
):
    market_slot = {'interval_start': const.NOW, 'interval_end': const.NOW}

    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['market_slot'] = market_slot

    cargo.short_order_id = const.SHORT_ORDER_ID
    cargo.custom_context = {
        'delivery_flags': {
            'is_forbidden_to_be_in_batch': False,
            'assign_rover': False,
        },
        'external_feature_prices': {'external_order_created_ts': const.NOW_TS},
        'depot_id': const.DEPOT_ID,
        'lavka_has_market_parcel': False,
        'order_id': const.ORDER_ID,
        'dispatch_wave': 0,
        'created': request_data['created_at'],
        'weight': 0.0,
        'dispatch_id': 'placeholder',
        'grocery_market_slot': market_slot,
        'brand_name': 'brand_name_lavka',
        'dispatch_type': 'pull-dispatch',
        'region_id': 213,
        'personal_phone_id': const.PERSONAL_PHONE_ID,
    }
    cargo.check_request(
        route_points=[FIRST_POINT, models.CLIENT_POINT, models.RETURN_POINT],
        items=cargo.convert_items(models.CREATE_REQUEST_DATA['items'])
        + [models.FAKE_ITEM],
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response.status_code == 200
    assert cargo.times_create_accepted_called() == 1

    dispatch = grocery_dispatch_pg.get_dispatch(
        dispatch_id=response.json()['dispatch_id'],
    )

    assert (
        dispatch.order.market_slot.interval_start
        == datetime.datetime.fromisoformat(const.NOW)
    )
    assert (
        dispatch.order.market_slot.interval_end
        == datetime.datetime.fromisoformat(const.NOW)
    )

    assert stq.grocery_dispatch_continue_order.times_called == 0
