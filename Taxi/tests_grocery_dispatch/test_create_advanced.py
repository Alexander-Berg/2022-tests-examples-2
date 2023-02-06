import copy

import pytest

from tests_grocery_dispatch import configs
from tests_grocery_dispatch import constants as const
from tests_grocery_dispatch import models

# flake8: noqa F401, IS001
# pylint: disable=C5521
from tests_grocery_dispatch.plugins.models import OrderInfo


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_PULL_DISPATCH
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_COMMENT_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG_SYNC
@configs.MODELER_DECISION_CONFIG_DISABLED
@configs.DISPATCH_DEPOT_ADDRESS_CONFIG
async def test_create_depot_location(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
        grocery_depots,
):
    grocery_depots.clear_depots()

    depot_coordinates = [37, 57]
    grocery_depots.add_depot(
        depot_test_id=int(const.DEPOT_ID),
        location=depot_coordinates,
        auto_add_zone=False,
    )

    first_point = copy.deepcopy(models.FIRST_POINT)
    first_point.comment = None
    first_point.coordinates = depot_coordinates

    second_point = copy.deepcopy(models.CLIENT_POINT)

    return_point = copy.deepcopy(models.RETURN_POINT)
    return_point.coordinates = depot_coordinates

    cargo.check_request(
        route_points=[first_point, second_point, return_point],
        items=cargo.convert_items(models.CREATE_REQUEST_DATA['items'])
        + [models.FAKE_ITEM],
        taxi_class='lavka',
    )
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)

    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response1.status_code == 200
    assert cargo.times_create_accepted_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG
@configs.DISPATCH_GENERAL_CONFIG_LEAVE_UNDER_DOOR
@configs.DISPATCH_COMMENT_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
@pytest.mark.experiments3(
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='grocery_dispatch_priority',
    default_value={'dispatches': ['cargo_taxi']},
    is_config=True,
)
async def test_send_leave_under_door(
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
        features=[{'id': 'lavka_leave_at_the_door'}],
    )
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['leave_under_door'] = True

    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response1.status_code == 200
    assert cargo.times_create_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_PULL_DISPATCH
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_COMMENT_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG_SYNC
@configs.MODELER_DECISION_CONFIG_DISABLED
@configs.DISPATCH_BATCHING_CONFIG
async def test_has_fragile_tag_batching_disabled(
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
    return_point = copy.deepcopy(models.RETURN_POINT)
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['items'][0]['item_tags'] = ['fragile']

    custom_context = {
        'brand_name': 'brand_name_lavka',
        'delivery_flags': {
            'is_forbidden_to_be_in_batch': True,
            'assign_rover': False,
        },
        'depot_id': const.DEPOT_ID,
        'dispatch_type': 'pull-dispatch',
        'external_feature_prices': {'external_order_created_ts': 1601915280},
        'lavka_has_market_parcel': False,
        'order_id': request_data['order_id'],
        'dispatch_wave': 0,
        'created': request_data['created_at'],
        'weight': 0.0,
        'dispatch_id': 'placeholder',
        'region_id': 213,
        'personal_phone_id': const.PERSONAL_PHONE_ID,
    }

    cargo.check_request(
        route_points=[first_point, second_point, return_point],
        items=cargo.convert_items(models.CREATE_REQUEST_DATA['items'])
        + [models.FAKE_ITEM],
        custom_context=custom_context,
        taxi_class='lavka',
    )

    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response1.status_code == 200
    assert cargo.times_create_accepted_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_PULL_DISPATCH
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_COMMENT_CONFIG
@configs.DISPATCH_PENDING_RESCHEDULE_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG_FULL
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_create_pending(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
        stq,
        stq_runner,
):
    first_point = copy.deepcopy(models.FIRST_POINT)
    first_point.comment = None

    second_point = copy.deepcopy(models.CLIENT_POINT)

    return_point = copy.deepcopy(models.RETURN_POINT)
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['items'][0]['item_tags'] = ['hot']

    cargo.check_request(
        route_points=[first_point, second_point, return_point],
        items=cargo.convert_items(request_data['items']) + [models.FAKE_ITEM],
        taxi_class='lavka',
    )

    exp3_recorder = experiments3.record_match_tries(
        'grocery_dispatch_pending_reschedule',
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response.status_code == 200
    assert cargo.times_create_accepted_called() == 0

    dispatch_id = response.json()['dispatch_id']
    request = {'dispatch_id': dispatch_id}
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/order_ready', json=request,
    )

    assert response.status_code == 200
    assert cargo.times_create_accepted_called() == 0

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    match_tries[0].ensure_matched_with_clause('default')

    call_data = stq.grocery_dispatch_reschedule_executor.next_call()

    await stq_runner.grocery_dispatch_reschedule_executor.call(
        task_id=call_data['id'], kwargs=call_data['kwargs'],
    )

    assert cargo.times_create_accepted_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_PULL_DISPATCH
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_COMMENT_CONFIG
@configs.DISPATCH_PENDING_RESCHEDULE_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG_FULL
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_cancel_pending(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
        stq,
        stq_runner,
):
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['items'][0]['item_tags'] = ['hot']

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response.status_code == 200
    assert cargo.times_create_accepted_called() == 0

    dispatch_id = response.json()['dispatch_id']

    json = {'dispatch_id': dispatch_id, 'cancel_type': 'free'}
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/cancel', json,
    )

    assert response.status_code == 200

    request = {'dispatch_id': dispatch_id}
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/order_ready', json=request,
    )

    assert response.status_code == 409
    assert cargo.times_create_accepted_called() == 0

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', {'dispatch_id': dispatch_id},
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'canceled'


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_PULL_DISPATCH
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_COMMENT_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG_SYNC
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_create_postal_code(
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
    second_point.postal_code = 'postal_code'

    return_point = copy.deepcopy(models.RETURN_POINT)

    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)

    request_data['postal_code'] = 'postal_code'

    cargo.set_data(number_of_user_address_parts=4)

    cargo.check_request(
        route_points=[first_point, second_point, return_point],
        taxi_class='lavka',
    )

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
@pytest.mark.parametrize(
    ['item1_qty', 'item2_qty', 'response_code', 'cargo_resp_code'],
    [('1', '1', 400, 400)],
)
async def test_basic_create_cargo_failure(
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
        cargo_resp_code,
        logistic_dispatcher,
):
    cargo.set_data(cargo_create_error_code=cargo_resp_code)
    grocery_supply.add_log_group(const.DEPOT_ID, 'ya_eats_group')

    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)

    request_data['items'][0]['quantity'] = item1_qty
    request_data['items'][1]['quantity'] = item2_qty

    request_items = []
    if int(item1_qty) > 0:
        request_items.append(request_data['items'][0])
    if int(item2_qty) > 0:
        request_items.append(request_data['items'][1])

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response.status_code == response_code

    cursor = pgsql['grocery_dispatch'].cursor()
    cursor.execute('SELECT status, wave, eta FROM dispatch.dispatches')
    result = cursor.fetchall()
    assert len(result) == 1
    assert result[0] == ('revoked', 0, 0)


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG
@configs.DISPATCH_GENERAL_CONFIG
@configs.MODELER_ORDERS_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG_TAXI
@configs.MODELER_DECISION_CONFIG
@configs.ETA_THRESHOLD_CONFIG
async def test_create_not_read_from_db(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
        logistic_dispatcher,
        grocery_shifts,
        grocery_depots,
):
    grocery_shifts.set_couriers_shifts_response(
        {'depot_ids': [const.DEPOT_ID_2]},
    )

    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)

    # will be checked at cargo mock
    cargo.short_order_id = const.SHORT_ORDER_ID
    cargo.custom_context = {
        'delivery_flags': {'is_forbidden_to_be_in_batch': False},
        'external_feature_prices': {'external_order_created_ts': const.NOW_TS},
        'depot_id': const.DEPOT_ID,
        'lavka_has_market_parcel': False,
        'order_id': request_data['order_id'],
        'dispatch_wave': 0,
        'created': request_data['created_at'],
        'weight': 0.0,
        'dispatch_id': 'placeholder',
        'region_id': 213,
        'personal_phone_id': const.PERSONAL_PHONE_ID,
    }

    grocery_supply.add_log_group(const.DEPOT_ID, 'ya_eats_group')

    request_data['items'][0]['quantity'] = '1'
    request_data['items'][1]['quantity'] = '1'

    request_items = []
    request_items.append(request_data['items'][0])
    request_items.append(request_data['items'][1])

    cargo.check_request(
        route_points=[models.FIRST_POINT, models.CLIENT_POINT],
        items=cargo.convert_items(request_items),
    )

    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response1.status_code == 200
    assert cargo.times_create_called() == 1

    grocery_depots.add_depot(
        depot_test_id=int(const.DEPOT_ID_2), auto_add_zone=False,
    )
    await taxi_grocery_dispatch.invalidate_caches()

    request_data['order_id'] = const.ORDER_ID_2
    request_data['depot_id'] = const.DEPOT_ID_2

    cargo.custom_context = {
        'delivery_flags': {'is_forbidden_to_be_in_batch': False},
        'external_feature_prices': {'external_order_created_ts': const.NOW_TS},
        'depot_id': const.DEPOT_ID_2,
        'lavka_has_market_parcel': False,
        'order_id': request_data['order_id'],
        'dispatch_wave': 0,
        'created': request_data['created_at'],
        'weight': 0.0,
        'dispatch_id': 'placeholder',
        'region_id': 213,
        'personal_phone_id': const.PERSONAL_PHONE_ID,
    }

    grocery_supply.add_log_group(const.DEPOT_ID_2, 'ya_eats_group')

    cargo.check_request(
        route_points=[models.FIRST_POINT, models.CLIENT_POINT],
        items=cargo.convert_items(request_items),
    )

    response2 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response2.status_code == 200
    assert cargo.times_create_called() == 2


@configs.DISPATCH_CLAIM_CONFIG_DEFAULT
@pytest.mark.experiments3(
    name='grocery_dispatch_modeler_decision',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'primary_modeler_name': 'local'},
        },
    ],
    is_config=True,
)
@pytest.mark.experiments3(
    name='grocery_dispatch_modeler_orders_options',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={
        'included_statuses': ['idle', 'scheduled', 'rescheduling', 'matching'],
        'excluded_dispatch_types': ['cargo_taxi'],
    },
    is_config=True,
)
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG
@pytest.mark.parametrize(
    ['couriers_quantity', 'couriers_to_orders_ratio'],
    [
        (0, 0.0),
        # (1, 0.5)
    ],
)
async def test_create_order_check_couriers_to_orders_ratio(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        cargo,
        experiments3,
        grocery_supply,
        grocery_shifts,
        queue_info_v2,
        couriers_quantity,
        couriers_to_orders_ratio,
        grocery_dispatch_pg,
        grocery_depots,
        testpoint,
):
    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(const.DEPOT_ID_2), auto_add_zone=False,
    )

    # Добавляю в бд заказ заказ в другой лавке, чтобы проверить,
    # что правильно выполняется запрос get_count_of_orders_without_performers
    grocery_dispatch_pg.create_dispatch(
        dispatch_name='cargo_sync',
        status='idle',
        order=OrderInfo(depot_id=const.DEPOT_ID_2),
    )

    grocery_depots.add_depot(
        depot_test_id=int(const.DEPOT_ID), auto_add_zone=False,
    )
    # И в нужную лавку заказ в очереди и завершенный
    grocery_dispatch_pg.create_dispatch(
        dispatch_name='cargo_taxi',
        status='scheduled',
        order=OrderInfo(depot_id=const.DEPOT_ID),
    )
    grocery_dispatch_pg.create_dispatch(
        dispatch_name='cargo_sync',
        status='delivered',
        order=OrderInfo(depot_id=const.DEPOT_ID),
    )
    grocery_shifts.set_couriers_shifts_response(
        {'depot_ids': [const.DEPOT_ID]},
    )

    queue_info_v2.set_queue_info_response(
        {
            'couriers': [
                {
                    'courier_id': f'courier_{n}',
                    'checkin_timestamp': '2020-10-05T16:28:00.000Z',
                }
                for n in range(couriers_quantity)
            ],
        },
    )

    await taxi_grocery_dispatch.invalidate_caches()

    exp3_recorder = experiments3.record_match_tries(
        'grocery_dispatch_modeler_decision',
    )

    @testpoint('local_modeler')
    def test_modeler_data(data):
        assert data['performers_cnt'] == couriers_quantity
        assert data['orders_cnt'] == 0
        assert data['ratio'] == couriers_to_orders_ratio
        return data

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', models.CREATE_REQUEST_DATA,
    )

    await exp3_recorder.get_match_tries(ensure_ntries=1)
    assert test_modeler_data.times_called
    assert response.status_code == 200
    assert cargo.times_create_accepted_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_DEFAULT
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG
@configs.DISPATCH_COMMENT_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_comment_create_additional_phone_code(
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
    second_point.comment = 'Добавочный телефонный номер: 3822 user comment'
    second_point.additional_phone_code = '3822'

    cargo.check_request(
        route_points=[first_point, second_point, models.RETURN_POINT],
        items=cargo.convert_items(models.CREATE_REQUEST_DATA['items'])
        + [models.FAKE_ITEM],
    )
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['additional_phone_code'] = '3822'

    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response1.status_code == 200
    assert cargo.times_create_accepted_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG
@configs.DISPATCH_GENERAL_CONFIG_MODIFIER_AGE_CHECK
@configs.DISPATCH_PRIORITY_CONFIG
@configs.DISPATCH_COMMENT_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_send_modifier_age_check(
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
    client_point.modifier_age_check = True

    first_point = copy.deepcopy(models.FIRST_POINT)
    first_point.comment = None

    cargo.check_request(
        route_points=[first_point, client_point, models.RETURN_POINT],
        items=cargo.convert_items(models.CREATE_REQUEST_DATA['items'])
        + [models.FAKE_ITEM],
    )
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['modifier_age_check'] = True

    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response1.status_code == 200
    assert cargo.times_create_accepted_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_PULL_DISPATCH
@configs.MODELER_DECISION_CONFIG_DISABLED
@pytest.mark.experiments3(
    name='grocery_dispatch_priority',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Big volume',
            'predicate': {
                'init': {
                    'value': 28000,
                    'arg_name': 'order_volume',
                    'arg_type': 'double',
                },
                'type': 'gt',
            },
            'value': {'dispatches': ['cargo_taxi']},
        },
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'dispatches': ['cargo_sync']},
        },
    ],
    is_config=True,
)
@configs.DISPATCH_GENERAL_CONFIG
async def test_create_volume_fallback(
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
    request_data['items'][0]['quantity'] = '10'
    request_data['items'][0]['weight'] = 1500
    request_data['items'][0]['height'] = 240
    request_data['items'][0]['width'] = 150
    request_data['items'][0]['depth'] = 70
    request_data['items'][1]['quantity'] = '4'
    request_data['items'][1]['weight'] = 1200
    request_data['items'][1]['height'] = 110
    request_data['items'][1]['width'] = 100
    request_data['items'][1]['depth'] = 70

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

    # small volume
    request_data['order_id'] = const.ORDER_ID_2
    request_data['items'][1]['quantity'] = '3'
    first_point = copy.deepcopy(models.FIRST_POINT)
    first_point.comment = None

    second_point = copy.deepcopy(models.CLIENT_POINT)

    cargo.check_request(
        route_points=[first_point, second_point, models.RETURN_POINT],
        items=cargo.convert_items(request_data['items']) + [models.FAKE_ITEM],
        taxi_class='lavka',
        claim_kind='platform_usage',
        taxi_classes=['lavka'],
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response.status_code == 200
    assert cargo.times_create_accepted_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_delivery_common_comment_create(
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
    test_comment = (
        '$$${"target_contractor_id": '
        '"0253f79a86d14b7ab9ac1d5d3017be47_5076397fbf767b7172e791145eede44c"'
        '}$$$'
    )
    cargo.set_data(claim_id=const.CLAIM_ID)
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['delivery_common_comment'] = test_comment

    first_point = copy.deepcopy(models.FIRST_POINT)
    first_point.comment = None

    cargo.check_request(
        route_points=[first_point, models.CLIENT_POINT, models.RETURN_POINT],
        items=cargo.convert_items(request_data['items']) + [models.FAKE_ITEM],
        comment=test_comment,
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response.status_code == 200
    assert cargo.times_create_accepted_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG_FULL
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_disabled_modeler(
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

    exp3_recorder_priority = experiments3.record_match_tries(
        'grocery_dispatch_priority',
    )
    exp3_recorder_modeler = experiments3.record_match_tries(
        'grocery_dispatch_modeler_decision',
    )
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', models.CREATE_REQUEST_DATA,
    )

    match_tries_priority = await exp3_recorder_priority.get_match_tries(
        ensure_ntries=1,
    )
    assert not match_tries_priority[0].kwargs['modeler_decision']
    await exp3_recorder_modeler.get_match_tries(ensure_ntries=1)
    assert response.status_code == 200
    assert cargo.times_create_accepted_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_CARGO
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG_FULL
@configs.DISPATCH_COMMENT_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_create_check_requirements_with_loaders(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
):
    cargo.check_request(
        route_points=[models.FIRST_POINT, models.CLIENT_POINT],
        items=cargo.convert_items(models.CREATE_REQUEST_DATA['items']),
        taxi_class='cargo',
        taxi_classes=['cargo'],
        cargo_loaders=1,
    )
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['zone_type'] = 'yandex_taxi'

    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response1.status_code == 200
    assert cargo.times_create_called() == 1


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_PULL_DISPATCH
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_COMMENT_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG_SYNC
@configs.MODELER_DECISION_CONFIG_DISABLED
@configs.DISPATCH_BATCHING_CONFIG
async def test_has_hot_tag_first_in_batch(
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
    return_point = copy.deepcopy(models.RETURN_POINT)
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['items'][0]['item_tags'] = ['hot']

    custom_context = {
        'brand_name': 'brand_name_lavka',
        'delivery_flags': {
            'is_forbidden_to_be_in_batch': False,
            'place_first_in_batch': True,
            'assign_rover': False,
        },
        'depot_id': const.DEPOT_ID,
        'dispatch_type': 'pull-dispatch',
        'external_feature_prices': {'external_order_created_ts': 1601915280},
        'lavka_has_market_parcel': False,
        'order_id': request_data['order_id'],
        'dispatch_wave': 0,
        'created': request_data['created_at'],
        'weight': 0.0,
        'dispatch_id': 'placeholder',
        'region_id': 213,
        'personal_phone_id': const.PERSONAL_PHONE_ID,
    }

    cargo.check_request(
        route_points=[first_point, second_point, return_point],
        items=cargo.convert_items(models.CREATE_REQUEST_DATA['items'])
        + [models.FAKE_ITEM],
        custom_context=custom_context,
        taxi_class='lavka',
    )

    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response1.status_code == 200
    assert cargo.times_create_accepted_called() == 1
