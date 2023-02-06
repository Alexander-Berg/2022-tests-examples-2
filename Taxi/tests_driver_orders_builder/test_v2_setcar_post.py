# pylint: disable=too-many-lines

import copy
import datetime
import json
import math

import pytest

from tests_driver_orders_builder import utils

PAY_TYPE_CASHLESS = 1
PAY_TYPE_CARD = 2

SETCAR_CREATE_URL = '/v2/setcar'
V2_SETCAR_PUSH_URL = '/v2/setcar_push'

PARAMS = {
    'driver': {
        'park_id': 'park1',
        'driver_profile_id': 'driver1',
        'alias_id': '4d605a2849d747079b5d8c7012830419',
    },
    'order_id': 'test_order_id',
}

CARRIER_WITH_ID = {
    'registration_number': '1',
    'name': 'Ivanov',
    'address': 'Msk',
    'work_hours': '11-13',
    'entity_id': '5b5984fdfefe3d7ba0ac1234',
    'type': 'carrier_permit_owner',
    'legal_type': 'legal',
}

CARRIER = {
    'registration_number': '1',
    'name': 'Ivanov',
    'address': 'Msk',
    'work_hours': '11-13',
    'type': 'carrier_permit_owner',
}

PARK_WITH_ID = {
    'registration_number': '1234-ab-45',
    'name': 'Organization',
    'address': 'Street',
    'work_hours': '9-18',
    'entity_id': 'ok',
    'type': 'park',
}

PARK = {
    'registration_number': '1234-ab-45',
    'name': 'Organization',
    'address': 'Street',
    'work_hours': '9-18',
    'type': 'park',
}

MATCH_ALWAYS = {'predicate': {'type': 'true'}, 'enabled': True}

MATCH_UBERDRIVER = {
    'predicate': {
        'type': 'all_of',
        'init': {
            'predicates': [
                {
                    'type': 'contains',
                    'init': {
                        'arg_name': 'driver_tags',
                        'set_elem_type': 'string',
                        'value': 'uberdriver',
                    },
                },
                {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'application',
                        'arg_type': 'string',
                        'value': 'uberdriver',
                    },
                },
            ],
        },
    },
    'enabled': True,
}

MOCK_TARIFFSV2 = {
    'driver': {
        'category_prices_id': 'c/168c3ba42916455ca95cbbdd96ea6678',
        'geoareas': ['g/2bab7eff1aa848b681370b2bd83cfbf9'],
    },
    'user': {
        'category_prices_id': 'c/168c3ba42916455ca95cbbdd96ea6678',
        'geoareas': ['g/2bab7eff1aa848b681370b2bd83cfbf9'],
    },
}

MOCKED_NOW = '2021-08-18T09:00:00+03:00'


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.parametrize(
    'booking_time_settings',
    [
        {
            'due': datetime.datetime(2021, 8, 18, 6, 10, 00),
            'expected_date_drive': utils.date_to_taximeter_str(
                '2021-08-18T09:10:00+03:00',
            ),
            'expected_date_last_change': utils.date_to_taximeter_str(
                MOCKED_NOW,
            ),
            'expected_kind': 1,
        },
    ],
)
@pytest.mark.now(MOCKED_NOW)
async def test_create_setcar_ok(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        setcar_create_params,
        mockserver,
        booking_time_settings,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response.json')

    setcar_json = load_json('setcar.json')
    setcar_push = load_json('setcar_push.json')

    # booking time builder settings
    aliases = order_proc.order_proc['fields']['aliases']

    aliases[0]['due'] = booking_time_settings['due']
    if 'order_type' in booking_time_settings:
        order = order_proc.order_proc['fields']['order']
        order['_type'] = booking_time_settings['order_type']
    utils.add_booking_time_settings(setcar_json, booking_time_settings)
    utils.add_booking_time_settings(setcar_push, booking_time_settings)

    response = await taxi_driver_orders_builder.post(**setcar_create_params)

    assert response.status_code == 200, response.text
    resp = response.json()
    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    utils.add_accents(setcar_json)
    assert redis_dict == setcar_json
    assert resp['setcar'] == setcar_json
    assert resp['setcar_push'] == setcar_push

    requestv2push = copy.deepcopy(PARAMS)
    responsev2 = await taxi_driver_orders_builder.post(
        V2_SETCAR_PUSH_URL, json=requestv2push,
    )
    assert responsev2.json()['setcar_push'] == setcar_push


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.now(MOCKED_NOW)
async def test_create_setcar_with_legal_entities(
        taxi_driver_orders_builder,
        redis_store,
        mockserver,
        load_json,
        setcar_create_params,
):
    @mockserver.json_handler('/parks/cars/legal-entities')
    def _legal_entities(request):
        return {'legal_entities': [CARRIER_WITH_ID, PARK_WITH_ID]}

    setcar_legal_entities = [CARRIER, PARK]
    setcar_json = load_json('setcar.json')
    setcar_push = load_json('setcar_push.json')
    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    utils.add_accents(setcar_json)
    setcar_json['legal_entities'] = setcar_legal_entities
    setcar_push['legal_entities'] = setcar_legal_entities
    assert response.status_code == 200, response.text
    assert response.json()['setcar_push'] == setcar_push
    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    assert redis_dict == setcar_json


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.now(MOCKED_NOW)
async def test_create_setcar_with_single_legal_entity(
        taxi_driver_orders_builder,
        redis_store,
        mockserver,
        load_json,
        setcar_create_params,
):
    @mockserver.json_handler('/parks/cars/legal-entities')
    def _legal_entities(request):
        return {'legal_entities': [PARK_WITH_ID]}

    setcar_legal_entities = [PARK, PARK.copy()]
    setcar_legal_entities[1]['type'] = 'carrier_permit_owner'

    setcar_json = load_json('setcar.json')
    setcar_push = load_json('setcar_push.json')
    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    utils.add_accents(setcar_json)
    setcar_json['legal_entities'] = setcar_legal_entities
    setcar_push['legal_entities'] = setcar_legal_entities
    assert response.status_code == 200, response.text
    assert response.json()['setcar_push'] == setcar_push
    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    assert redis_dict == setcar_json


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.now(MOCKED_NOW)
async def test_create_setcar_hiding_fields(
        taxi_driver_orders_builder, redis_store, load_json,
):
    def _update_acceptance_items(setcar):
        setcar['ui']['acceptance_items'] = setcar['ui']['acceptance_items'][
            :2
        ]  # double_section and adress_from

    setcar_json = load_json('setcar.json')
    setcar_json['show_address'] = False
    setcar_json['fixed_price']['show'] = False
    setcar_json['driver_fixed_price']['show'] = False
    _update_acceptance_items(setcar_json)

    setcar_push = load_json('setcar_push.json')
    setcar_push['show_address'] = False
    setcar_push.pop('address_to')
    setcar_push.pop('route_points')
    setcar_push.pop('fixed_price')
    setcar_push.pop('driver_fixed_price')
    _update_acceptance_items(setcar_push)

    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200, response.text
    assert response.json()['setcar_push'] == setcar_push
    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    utils.add_accents(setcar_json)
    assert redis_dict == setcar_json
    requestv2push = copy.deepcopy(PARAMS)
    responsev2 = await taxi_driver_orders_builder.post(
        V2_SETCAR_PUSH_URL, json=requestv2push,
    )
    assert responsev2.json()['setcar_push'] == setcar_push


@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'all_of',
            'init': {
                'predicates': [
                    {
                        'type': 'in_set',
                        'init': {
                            'set': ['driver1'],
                            'arg_name': 'driver_profile_id',
                            'set_elem_type': 'string',
                        },
                    },
                    {
                        'type': 'not',
                        'init': {
                            'predicate': {
                                'type': 'in_set',
                                'init': {
                                    'set': ['business'],
                                    'arg_name': 'category',
                                    'set_elem_type': 'string',
                                },
                            },
                        },
                    },
                ],
            },
        },
        'enabled': True,
    },
    name='passenger_ratings_for_drivers',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value=True,
)
@pytest.mark.parametrize(
    'fields, application, push_file',
    [
        (
            {'category': 1, 'category_v2': 'econom'},
            'android',
            'setcar_push_passenger_rating.json',
        ),
        ({'category': 1, 'category_v2': 'econom'}, 'uber', 'setcar_push.json'),
        (
            {'category': 2, 'category_v2': 'business'},
            'android',
            'setcar_push.json',
        ),
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.parametrize(
    'booking_time_settings',
    [
        {
            'expected_date_drive': utils.date_to_taximeter_str(MOCKED_NOW),
            'expected_date_last_change': utils.date_to_taximeter_str(
                MOCKED_NOW,
            ),
            'expected_kind': 1,
        },
    ],
)
@pytest.mark.now(MOCKED_NOW)
async def test_create_setcar_passenger_rating(
        taxi_driver_orders_builder,
        redis_store,
        mockserver,
        load_json,
        fields,
        application,
        push_file,
        booking_time_settings,
        order_proc,
):
    @mockserver.json_handler('/passenger-profile/passenger-profile/v1/profile')
    def _mock_passenger_profile(request):
        return {'first_name': 'Иосиф', 'rating': '4.8'}

    order_proc.set_file(load_json, 'order_core_response2.json')
    order_proc.order_proc['fields']['order']['application'] = application
    order_proc.order_proc['fields']['order']['user_uid'] = '123'
    category_v2 = fields.get('category_v2')
    if category_v2 is not None:
        order_proc.order_proc['fields']['candidates'][0][
            'tariff_class'
        ] = category_v2

    setcar_json = load_json('setcar.json')
    setcar_push = load_json(push_file)
    if not fields.get('category_v2'):
        setcar_push['category_v2'] = ''
        setcar_json['category_v2'] = ''

    setcar_json.update(fields)
    setcar_push.update(fields)

    utils.add_booking_time_settings(setcar_json, booking_time_settings)
    utils.add_booking_time_settings(setcar_push, booking_time_settings)

    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200, response.text
    assert response.json()['setcar_push'] == setcar_push
    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    setcar_json['ui'] = setcar_push['ui']
    assert redis_dict == setcar_json


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.now(MOCKED_NOW)
async def test_create_setcar_address_details_flag(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        mockserver,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response.json')
    order_proc.order_proc['fields']['candidates'][0]['tariff_class'] = 'cargo'

    setcar_json = load_json('setcar.json')
    setcar_push = load_json('setcar_push.json')
    setcar_json['category'] = 1 << 25
    setcar_push['category'] = 1 << 25
    setcar_push['category_v2'] = 'cargo'
    setcar_json['category_v2'] = 'cargo'
    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200, response.text
    setcar_json['taximeter_settings']['show_detailed_addresses'] = True
    setcar_push['taximeter_settings']['show_detailed_addresses'] = True
    assert response.json()['setcar_push'] == setcar_push
    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    utils.add_accents(setcar_json)
    assert redis_dict == setcar_json, redis_dict


@pytest.mark.config(
    UNLOADING_CONFIG_BY_ZONE_AND_CATEGORY={
        'moscow': {
            'cargocorp': {
                'free_time': 300.0,
                'max_distance_to_destination': 500.0,
            },
        },
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.now(MOCKED_NOW)
async def test_create_setcar_unloading_config(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        mockserver,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response.json')
    order_proc.order_proc['fields']['candidates'][0][
        'tariff_class'
    ] = 'cargocorp'

    unloading_config = {
        'free_time': 300.0,
        'max_distance_to_destination': 500.0,
    }
    setcar_json = load_json('setcar.json')
    setcar_push = load_json('setcar_push.json')
    setcar_push['taximeter_settings']['unloading_config'] = unloading_config
    setcar_json['taximeter_settings']['unloading_config'] = unloading_config
    setcar_push['taximeter_settings']['show_detailed_addresses'] = True
    setcar_json['taximeter_settings']['show_detailed_addresses'] = True
    setcar_push['category'] = 1 << 25
    setcar_json['category'] = 1 << 25
    setcar_push['category_v2'] = 'cargo'
    setcar_json['category_v2'] = 'cargo'
    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200, response.text
    assert response.json()['setcar_push'] == setcar_push
    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    utils.add_accents(setcar_json)
    assert redis_dict == setcar_json, redis_dict


@pytest.mark.experiments3(filename='toll_road_experiments.json')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.parametrize(
    'can_switch_road,use_toll_road,auto_payment,response_flag,country',
    [
        (True, True, True, True, 'rus'),
        (True, False, True, False, 'rus'),
        (False, True, True, True, 'rus'),
        (False, False, True, None, 'rus'),
        (True, True, True, None, 'isr'),
    ],
)
@pytest.mark.now(MOCKED_NOW)
async def test_toll_roads_flag(
        taxi_driver_orders_builder,
        load_json,
        toll_roads,
        mockserver,
        can_switch_road,
        use_toll_road,
        auto_payment,
        response_flag,
        country,
        parks,
        setcar_create_params,
        order_proc,
):
    parks.set_response(country)
    toll_roads.set_response(can_switch_road, use_toll_road, auto_payment)

    order_proc.set_file(load_json, 'order_core_response1.json')
    order_proc.order_proc['fields']['order']['request']['toll_roads'] = {
        'some_data': 'something',
    }

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text
    response = response.json()['setcar']
    if response_flag is not None:
        toll_roads_response = response['order_options']['toll_roads']
        assert toll_roads_response['use_toll_road'] == response_flag
        if response_flag:
            assert (
                toll_roads_response['entrance_notification'][
                    'notify_distance_meters'
                ]
                == 100
            )
    else:
        assert 'order_options' not in response


@pytest.mark.experiments3(filename='toll_road_experiments.json')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_toll_roads_price_format',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'as_double': True},
)
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'toll_road_payment': '9.51'}},
    },
)
@pytest.mark.parametrize('order_proc_toll_roads', [True, False])
@pytest.mark.experiments3()
@pytest.mark.now(MOCKED_NOW)
async def test_toll_roads_order_proc(
        taxi_driver_orders_builder,
        load_json,
        toll_roads,
        mockserver,
        order_proc_toll_roads,
        setcar_create_params,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response1.json')
    if order_proc_toll_roads:
        order_proc.order_proc['fields']['order']['request']['toll_roads'] = {
            'user_had_choice': True,
            'user_chose_toll_road': True,
            'auto_payment': True,
        }

    toll_roads.set_response(True, True, True)
    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text
    response = response.json()['setcar']
    if order_proc_toll_roads:
        assert 'order_options' in response
        assert 'toll_roads' in response['order_options']
        assert (
            response['description']
            == 'Какой-то комментарий\nПроезд по платной дороге'
        )
        assert 'requirement_list' in response
        assert (
            response['requirement_list'][0]['max_price']
            == utils.MAX_COST_TOLL_ROADS
        )
    else:
        assert 'order_options' not in response
        assert response['description'] == 'Какой-то комментарий'


ACTIVITY_BONUS_FIELDS = {
    'subtitle': '+5',
    'primary_text_color': '#00945e',
    'left_icon': {
        'icon_type': 'activity',
        'tint_color': '#00ca50',
        'icon_size': 'large',
    },
}


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_price_activity_rebuild': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.now(MOCKED_NOW)
async def test_activity_bonus(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        redis_store,
        setcar_create_params,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response2.json')

    setcar_json = load_json('setcar.json')
    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    utils.add_accents(setcar_json)
    activity = setcar_json['ui']['acceptance_items'][0]['left']
    activity.update(ACTIVITY_BONUS_FIELDS)
    assert response.status_code == 200
    setcar_push = load_json('setcar_push.json')
    setcar_push['ui'] = setcar_json['ui']
    assert response.json()['setcar_push'] == setcar_push
    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    utils.add_accents(setcar_json)
    assert redis_dict == setcar_json


SURGE_FIELDS = {
    'subtitle': '+10 ₽',
    'primary_text_color': '#820abe',
    'left_icon': {
        'icon_type': 'surge',
        'tint_color': '#c81efa',
        'icon_size': 'large',
    },
}


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='paid_supply_in_surge',
    consumers=['driver-orders-builder/setcar'],
    clauses=[
        {
            'title': 'drivers',
            'value': {'enabled': True},
            'predicate': {
                'init': {
                    'set': ['driver1'],
                    'arg_name': 'driver_profile_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        },
    ],
    default_value={'enabled': False},
)
@pytest.mark.parametrize(
    'pricing_data_driver_meta, surge_patch, paid_supply, driver_id',
    [
        (
            {'setcar.show_surcharge': 777.55, 'setcar.show_surge': 1.95},
            '+777.55 ₽',
            False,
            None,
        ),
        ({'setcar.show_surcharge': 990}, '+990 ₽', False, None),
        ({'setcar.show_surge': 1.95}, '×1.95', False, None),
        (
            {
                'setcar.show_paid_supply_surcharge': 400,
                'setcar.show_surcharge': 990,
            },
            '+400 ₽',
            True,
            None,
        ),
        (
            {
                'setcar.show_paid_supply_surcharge': 400,
                'setcar.show_surcharge': 990,
            },
            '+990 ₽',
            False,
            'clid_driver1',
        ),
        (
            {
                'setcar.show_paid_supply_surcharge': 400,
                'setcar.show_surcharge': 990,
            },
            '+990 ₽',
            False,
            None,
        ),
    ],
    ids=[
        'get_surge_new_pricing_surcharge_1',
        'get_surge_new_pricing_surcharge_2',
        'get_surge_new_pricing_surge',
        'get_surge_new_pricing_surge_with_paid_supply',
        'get_surge_new_pricing_surge_with_paid_supply_driver_not_in_exp',
        'get_surge_new_pricing_surge_with_paid_supply_ps_reset',
    ],
)
@pytest.mark.now(MOCKED_NOW)
async def test_surge(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        pricing_data_driver_meta,
        surge_patch,
        params_wo_original_setcar,
        paid_supply,
        driver_id,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response2.json')
    if pricing_data_driver_meta:
        order_proc.order_proc['fields']['order']['pricing_data']['driver'][
            'meta'
        ] = pricing_data_driver_meta
    order_proc.order_proc['fields']['candidates'][0][
        'paid_supply'
    ] = paid_supply

    if driver_id is not None:
        order_proc.order_proc['fields']['candidates'][0][
            'driver_id'
        ] = driver_id

    setcar_json = load_json('setcar.json')
    utils.add_accents(setcar_json)
    activity = setcar_json['ui']['acceptance_items'][0]['left']
    activity.update(ACTIVITY_BONUS_FIELDS)
    price = setcar_json['ui']['acceptance_items'][0]['right']
    price.update(SURGE_FIELDS)
    if surge_patch:
        price['subtitle'] = surge_patch
    setcar_push = load_json('setcar_push.json')
    setcar_push['ui'] = setcar_json['ui']

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )
    assert response.status_code == 200

    assert (
        response.json()['setcar_push']['ui']['acceptance_items'][0]
        == setcar_push['ui']['acceptance_items'][0]
    )
    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    utils.add_accents(setcar_json)
    assert (
        redis_dict['ui']['acceptance_items'][0]
        == setcar_json['ui']['acceptance_items'][0]
    )


@pytest.mark.now(MOCKED_NOW)
@pytest.mark.parametrize(
    'pricing_data_driver_meta',
    [({'setcar.show_surge': 1}), ({'setcar.show_surcharge': 0})],
    ids=['show_surge', 'show_surcharge'],
)
async def test_show_surge_surcharge_crutch(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        order_proc,
        params_wo_original_setcar,
        pricing_data_driver_meta,
):
    order_proc.set_file(load_json, 'order_core_response2.json')
    if pricing_data_driver_meta:
        order_proc.order_proc['fields']['order']['pricing_data']['driver'][
            'meta'
        ] = pricing_data_driver_meta
    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )
    assert response.status_code == 200
    data = response.json()
    assert 'surcharge_message_v2' not in data['setcar']
    assert 'surge_message_any_digits' not in data['setcar']
    data_right = data['setcar']['ui']['acceptance_items'][0]['right']
    assert data_right['subtitle'] == '× 1'
    assert data_right['left_icon']['tint_color'] == '#d8d8d8'
    assert data_right['primary_text_color'] == '#9e9b98'


@pytest.mark.config(TAXIMETER_SEND_ANTISURGE=True)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[
        {
            'title': 'driver_mode_experiment',
            'value': {
                'enable_driver_mode_request': True,
                'enable_driver_tags_request': True,
                'enable_price_activity_rebuild': True,
            },
            'predicate': {
                'init': {
                    'set': ['park1_driver1'],
                    'arg_name': 'park_driver_profile_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        },
    ],
    default_value={'enable_driver_mode_request': False},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_ui_parts_settings',
    consumers=['driver-orders-builder/ui-parts-settings-experiment'],
    merge_values_by=[
        {
            'tag': 'ui_experiments',
            'consumer': 'driver-orders-builder/ui-parts-settings-experiment',
            'merge_method': 'dicts_recursive_merge',
        },
    ],
    clauses=[
        {
            'title': 'driver_fix tag',
            'value': {
                'hide_ui_parts': {
                    'is_hiding_activity': True,
                    'is_hiding_price': True,
                    'is_hiding_surge': True,
                },
                'show_ui_parts': {},
            },
            'predicate': {
                'init': {
                    'arg_name': 'driver_tags',
                    'set_elem_type': 'string',
                    'value': 'driver_fix',
                },
                'type': 'contains',
            },
        },
    ],
    default_value={'hide_ui_parts': {}, 'show_ui_parts': {}},
)
@pytest.mark.config(
    TAXIMETER_COST_HIDE_BY_DRIVER_MODE={
        'driver_fix': {
            'driver_hide_cost_counter': True,
            'driver_hide_cost_widget': False,
            'driver_hide_cost_plate': True,
            'show_user_cost': False,
        },
    },
)
@pytest.mark.parametrize(
    'driver_tags_request, tags_retrieve',
    [(True, False), (True, True), (False, None)],
)
@pytest.mark.now(MOCKED_NOW)
async def test_antisurge_hide_title(
        taxi_driver_orders_builder,
        taxi_config,
        load_json,
        mockserver,
        driver_tags_request,
        tags_retrieve,
        driver_tags_mocks,
        order_proc,
        params_wo_original_setcar,
):
    order_proc.set_file(load_json, 'order_core_response5.json')
    if driver_tags_request:
        driver_tags_mocks.set_tags_info('park1', 'driver1', ['driver_fix'])
    else:
        order_proc.order_proc['fields']['candidates'][0]['tags'] = [
            'driver_fix',
        ]

    if tags_retrieve is not None:
        taxi_config.set_values(
            dict(DRIVER_ORDERS_BUILDER_USE_TAGS_RETRIEVE=tags_retrieve),
        )

    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_dup(request):
        return {
            'display_mode': 'driver_fix',
            'display_profile': 'driver_fix_profile',
        }

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )

    assert response.status_code == 200
    response_setcar = response.json()['setcar']
    assert (
        response_setcar['taximeter_settings']['driver_mode_type']
        == 'driver_fix'
    )
    modes_info = response_setcar['driver_mode_info']
    assert modes_info['display_mode'] == 'driver_fix'
    assert modes_info['display_profile'] == 'driver_fix_profile'

    assert 'subtitle' not in response_setcar['ui']['accept_toolbar_params']
    assert 'subtitle' not in response_setcar['ui']['acceptance_button_params']

    assert driver_tags_mocks.has_calls('/v1/drivers/match/profile') is (
        tags_retrieve is False
    )
    assert driver_tags_mocks.has_calls('/v1/drivers/retrieve/profile') is (
        tags_retrieve is True
    )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[
        {
            'title': 'driver_mode_experiment',
            'value': {
                'enable_driver_mode_request': True,
                'enable_driver_tags_request': True,
            },
            'predicate': {
                'init': {
                    'set': ['park1_driver1'],
                    'arg_name': 'park_driver_profile_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        },
    ],
    default_value={'enable_driver_mode_request': False},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_ui_parts_settings',
    merge_values_by=[
        {
            'tag': 'ui_experiments',
            'consumer': 'driver-orders-builder/ui-parts-settings-experiment',
            'merge_method': 'dicts_recursive_merge',
        },
    ],
    consumers=['driver-orders-builder/ui-parts-settings-experiment'],
    clauses=[
        {
            'title': 'driver_fix tag',
            'value': {
                'hide_ui_parts': {
                    'is_hiding_activity': True,
                    'is_hiding_price': True,
                    'is_hiding_surge': True,
                },
                'show_ui_parts': {},
            },
            'predicate': {
                'init': {
                    'arg_name': 'driver_tags',
                    'set_elem_type': 'string',
                    'value': 'driver_fix',
                },
                'type': 'contains',
            },
        },
    ],
    default_value={'hide_ui_parts': {}, 'show_ui_parts': {}},
)
@pytest.mark.config(
    TAXIMETER_COST_HIDE_BY_DRIVER_MODE={
        'driver_fix': {
            'driver_hide_cost_counter': True,
            'driver_hide_cost_widget': False,
            'driver_hide_cost_plate': True,
            'show_user_cost': False,
        },
    },
)
@pytest.mark.driver_tags_match(
    dbid='park1', uuid='driver1', tags=['driver_fix'],
)
@pytest.mark.now(MOCKED_NOW)
async def test_build_paid_supply(
        taxi_driver_orders_builder,
        mockserver,
        load_json,
        params_wo_original_setcar,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response4.json')

    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_dup(request):
        return {'display_mode': 'driver_fix', 'display_profile': 'driver_fix'}

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )
    assert response.status_code == 200
    response_setcar = response.json()['setcar']
    assert 'driver_fix' not in response_setcar['taximeter_settings']
    assert (
        response_setcar['taximeter_settings']['driver_mode_type']
        == 'driver_fix'
    )
    assert 'subtitle' not in response_setcar['ui']['accept_toolbar_params']
    assert 'subtitle' not in response_setcar['ui']['acceptance_button_params']


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[
        {
            'title': 'driver_mode_experiment',
            'value': {
                'enable_driver_mode_request': True,
                'enable_driver_tags_request': True,
            },
            'predicate': {
                'init': {
                    'set': ['park1_driver1'],
                    'arg_name': 'park_driver_profile_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        },
    ],
    default_value={'enable_driver_mode_request': False},
)
@pytest.mark.config(
    TAXIMETER_COST_HIDE_BY_DRIVER_MODE={
        'driver_fix': {
            'driver_hide_cost_counter': True,
            'driver_hide_cost_widget': False,
            'driver_hide_cost_plate': True,
            'show_user_cost': False,
        },
    },
)
@pytest.mark.now(MOCKED_NOW)
async def test_driver_mode(
        taxi_driver_orders_builder, mockserver, setcar_create_params,
):
    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_dup(request):
        return {'display_mode': 'driver_fix', 'display_profile': 'driver_fix'}

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200
    response_setcar = response.json()['setcar']
    assert 'driver_mode' not in response_setcar['taximeter_settings']
    assert (
        response_setcar['taximeter_settings']['driver_mode_type']
        == 'driver_fix'
    )
    assert response_setcar['taximeter_settings']['hide_cost_counter'] is True
    assert response_setcar['taximeter_settings']['hide_cost_widget'] is False
    assert response_setcar['taximeter_settings']['hide_cost_plate'] is True
    assert response_setcar['taximeter_settings']['show_user_cost'] is False


@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': ['driver1'],
                'arg_name': 'driver_profile_id',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='driver_modes',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value=True,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_driver_tags_request': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_ui_parts_settings',
    merge_values_by=[
        {
            'tag': 'ui_experiments',
            'consumer': 'driver-orders-builder/ui-parts-settings-experiment',
            'merge_method': 'dicts_recursive_merge',
        },
    ],
    consumers=['driver-orders-builder/ui-parts-settings-experiment'],
    clauses=[
        {
            'title': 'driver_fix tag',
            'value': {
                'hide_ui_parts': {
                    'is_hiding_activity': True,
                    'is_hiding_price': True,
                    'is_hiding_surge': True,
                },
                'show_ui_parts': {},
            },
            'predicate': {
                'init': {
                    'arg_name': 'driver_tags',
                    'set_elem_type': 'string',
                    'value': 'driver_fix',
                },
                'type': 'contains',
            },
        },
    ],
    default_value={'hide_ui_parts': {}, 'show_ui_parts': {}},
)
@pytest.mark.driver_tags_match(
    dbid='park1', uuid='driver1', tags=['driver_fix'],
)
@pytest.mark.now(MOCKED_NOW)
async def test_driver_mode_by_exp(
        taxi_driver_orders_builder, mockserver, load_json,
):
    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_dup(request):
        return {'display_mode': 'driver_fix', 'display_profile': 'driver_fix'}

    setcar_json = load_json('setcar.json')
    setcar_json['driver_points_info'] = {'some_val_1': 1.0, 'some_val_2': 2.0}
    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200
    setcar_response = response.json()['setcar']
    assert 'driver_points_info' not in setcar_response

    # no double section
    assert (
        setcar_response['ui']['acceptance_items'][0]['type']
        != 'double_section'
    )
    assert 'driver_mode' not in setcar_response['taximeter_settings']
    assert (
        setcar_response['taximeter_settings']['driver_mode_type']
        == 'driver_fix'
    )


@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': ['driver1'],
                'arg_name': 'driver_profile_id',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='driver_modes',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value=True,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_ui_parts_settings',
    merge_values_by=[
        {
            'tag': 'ui_experiments',
            'consumer': 'driver-orders-builder/ui-parts-settings-experiment',
            'merge_method': 'dicts_recursive_merge',
        },
    ],
    consumers=['driver-orders-builder/ui-parts-settings-experiment'],
    clauses=[],
    default_value={
        'hide_ui_parts': {
            'is_hiding_activity': True,
            'is_hiding_price': True,
            'is_hiding_surge': True,
        },
        'show_ui_parts': {},
    },
)
@pytest.mark.now(MOCKED_NOW)
async def test_driver_mode_fallback(
        taxi_driver_orders_builder, load_json, driver_ui_profile,
):
    driver_ui_profile.set_error()

    setcar_json = load_json('setcar.json')
    setcar_json['driver_points_info'] = {'some_val_1': 1.0, 'some_val_2': 2.0}
    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200
    setcar_response = response.json()['setcar']
    # assert 'driver_points_info' not in setcar_response

    # no double section
    assert (
        setcar_response['ui']['acceptance_items'][0]['type']
        != 'double_section'
    )


@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': ['driver1'],
                'arg_name': 'driver_profile_id',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='driver_modes',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value=True,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_ui_parts_settings',
    merge_values_by=[
        {
            'tag': 'ui_experiments',
            'consumer': 'driver-orders-builder/ui-parts-settings-experiment',
            'merge_method': 'dicts_recursive_merge',
        },
    ],
    consumers=['driver-orders-builder/ui-parts-settings-experiment'],
    clauses=[],
    default_value={
        'hide_ui_parts': {
            'is_hiding_activity': True,
            'is_hiding_price': True,
            'is_hiding_surge': True,
        },
        'show_ui_parts': {},
    },
)
@pytest.mark.now(MOCKED_NOW)
async def test_retry_with_setcar_changes(
        taxi_driver_orders_builder, load_json, driver_ui_profile,
):
    driver_ui_profile.set_error()
    setcar_json = load_json('setcar.json')
    setcar_json['driver_points_info'] = {'some_val_1': 1.0, 'some_val_2': 2.0}

    # не проверяем ответ
    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    await taxi_driver_orders_builder.post(SETCAR_CREATE_URL, json=request)
    # получаем уже записанный в редис сеткар
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200
    setcar_response = response.json()['setcar']
    assert 'driver_points_info' not in setcar_response
    # no double section
    assert (
        setcar_response['ui']['acceptance_items'][0]['type']
        != 'double_section'
    )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enable_requirements_rebuild': True,
        'enable_cargo_multipoints': True,
    },
)
@pytest.mark.experiments3()
@pytest.mark.now(MOCKED_NOW)
async def test_cargo_order(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        mock_cargo_setcar_data,
        order_proc,
):
    cargo_ref_id = 'cargo_claim_id_1'
    mock_cargo_setcar_data(
        comment='Заказ с подтверждением по СМС.\n'
        'Комментарий из сервиса cargo-dispatch',
        is_batch_order=True,
        expected_request_cargo_ref_id=cargo_ref_id,
        expected_request_tariff_class='econom',
        expected_request_order_id='fe8250a5c1324bceb162b71f64e40ad7',
        expected_request_performer_info={
            'park_id': 'park1',
            'driver_profile_id': 'driver1',
            'transport_type': 'car',
        },
        deeplink='/foo/bar',
    )

    order_proc.set_file(load_json, 'order_core_response3.json')
    proc_request = order_proc.order_proc['fields']['order']['request']
    proc_request['requirements'] = {'cargo_type': 'lcv_l'}
    proc_request['cargo_ref_id'] = cargo_ref_id
    proc_request['corp_comment'] = 'Корп комментарий'
    proc_request['comment'] = 'Негодный комментарий из сервиса cargo-dispatch'
    proc_request['corp'] = {'client_id': 'corp_client_id_12312312312312312'}

    setcar_json = load_json('setcar_requirements.json')
    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200, response.text
    resp = response.json()['setcar']
    assert (
        resp['description'] == 'Заказ с подтверждением по СМС.\n'
        'Комментарий из сервиса cargo-dispatch'
    )
    assert resp['ui']['acceptance_items'] == load_json(
        'acceptance_items_cargo.json',
    )
    assert resp['cargo'] == {
        'instruction': {'deeplink': '/foo/bar'},
        'is_batch_order': True,
        'corp_client_id': 'corp_client_id_12312312312312312',
    }


@pytest.mark.parametrize('is_price_hidden', [True, False])
@pytest.mark.config(
    DRIVER_ORDERS_BUILDER_IS_PRICE_HIDDEN_FROM_CARGO_ORDERS=False,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enable_requirements_rebuild': True,
        'enable_cargo_multipoints': True,
    },
)
@pytest.mark.experiments3()
@pytest.mark.now(MOCKED_NOW)
async def test_cargo_multipoints_order(
        taxi_driver_orders_builder,
        experiments3,
        is_price_hidden,
        __test_cargo_multipoints_order,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_orders_builder_cargo_driver_settings',
        consumers=['driver-orders-builder/setcar'],
        clauses=[],
        default_value={'is_hiding_price': is_price_hidden},
    )
    await taxi_driver_orders_builder.invalidate_caches()
    pricing = {
        'price': {'total': '100.30', 'surge': '10.50'},
        'currency': {'code': 'RUB'},
    }
    await __test_cargo_multipoints_order(pricing, is_price_hidden)


@pytest.mark.parametrize('is_price_hidden', [True, False])
@pytest.mark.config(
    DRIVER_ORDERS_BUILDER_IS_PRICE_HIDDEN_FROM_CARGO_ORDERS=True,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enable_requirements_rebuild': True,
        'enable_cargo_multipoints': True,
    },
)
@pytest.mark.experiments3()
@pytest.mark.now(MOCKED_NOW)
async def test_cargo_multipoints_order_from_cargo_orders(
        __test_cargo_multipoints_order, is_price_hidden,
):
    pricing = {
        'price': {'total': '100.30', 'surge': '10.50'},
        'currency': {'code': 'RUB'},
        'is_price_hidden': is_price_hidden,
    }
    await __test_cargo_multipoints_order(pricing, is_price_hidden)


@pytest.fixture()
def __test_cargo_multipoints_order(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        mock_cargo_setcar_data,
        order_proc,
):
    async def __internal(pricing, is_price_hidden):
        cargo_ref_id = 'cargo_claim_pid_1'
        mock_cargo_setcar_data(
            comment='Заказ с подтверждением по СМС.\n'
            'Комментарий из сервиса cargo-dispatch',
            points_count=2,
            pricing=pricing,
            tariff_class='courier',
        )

        order_proc.set_file(load_json, 'order_core_response3.json')
        proc_request = order_proc.order_proc['fields']['order']['request']
        proc_request['requirements'] = {'cargo_type': 'lcv_l'}
        proc_request['cargo_ref_id'] = cargo_ref_id
        proc_request['corp_comment'] = 'Корп комментарий'
        proc_request[
            'comment'
        ] = 'Негодный комментарий из сервиса cargo-dispatch'
        proc_request['corp'] = {
            'client_id': 'corp_client_id_12312312312312312',
        }

        setcar_json = load_json('setcar_requirements.json')
        request = copy.deepcopy(PARAMS)
        request['original_setcar'] = setcar_json
        response = await taxi_driver_orders_builder.post(
            SETCAR_CREATE_URL, json=request,
        )
        assert response.status_code == 200, response.text
        resp = response.json()['setcar']
        assert (
            resp['description'] == 'Заказ с подтверждением по СМС.\n'
            'Комментарий из сервиса cargo-dispatch'
        )
        if is_price_hidden:
            assert (
                resp['ui']['acceptance_button_params']['subtitle']
                == 'Эконом * 2 точек'
            ), resp['ui']['acceptance_button_params']
        else:
            assert (
                resp['ui']['acceptance_button_params']['subtitle']
                == 'Эконом * 2 точек * 100 ₽'
            ), resp['ui']['acceptance_button_params']
        assert (
            resp['ui']['accept_toolbar_params']['title'] == 'Эконом * 2 точек'
        ), resp['ui']['accept_toolbar_params']
        assert (
            resp['ui']['accept_toolbar_params']['subtitle']
            == 'Займет около 2 ч 10 мин'
        ), resp['ui']['accept_toolbar_params']

    return __internal


@pytest.mark.parametrize('is_price_hidden', [True, False])
@pytest.mark.config(
    DRIVER_ORDERS_BUILDER_IS_PRICE_HIDDEN_FROM_CARGO_ORDERS=False,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enable_requirements_rebuild': True,
        'enable_cargo_multipoints': True,
    },
)
@pytest.mark.now(MOCKED_NOW)
async def test_cargo_subtitle_with_price(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        mock_cargo_setcar_data,
        experiments3,
        is_price_hidden,
        order_proc,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_orders_builder_cargo_driver_settings',
        consumers=['driver-orders-builder/setcar'],
        clauses=[],
        default_value={'is_hiding_price': is_price_hidden},
    )
    await taxi_driver_orders_builder.invalidate_caches()

    cargo_ref_id = 'cargo_claim_pid_1'
    mock_cargo_setcar_data(
        comment='Заказ с подтверждением по СМС.\n'
        'Комментарий из сервиса cargo-dispatch',
        points_count=1,
        pricing={
            'price': {'total': '100.30', 'surge': '10.50'},
            'currency': {'code': 'RUB'},
        },
        tariff_class='courier',
    )

    order_proc.set_file(load_json, 'order_core_response3.json')
    proc_request = order_proc.order_proc['fields']['order']['request']
    proc_request['requirements'] = {'cargo_type': 'lcv_l'}
    proc_request['cargo_ref_id'] = cargo_ref_id
    proc_request['corp_comment'] = 'Корп комментарий'
    proc_request['comment'] = 'Негодный комментарий из сервиса cargo-dispatch'
    proc_request['corp'] = {'client_id': 'corp_client_id_12312312312312312'}

    setcar_json = load_json('setcar_requirements.json')
    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200, response.text
    resp = response.json()['setcar']
    if is_price_hidden:
        assert resp['ui']['acceptance_button_params']['subtitle'] == ''
    else:
        assert (
            resp['ui']['acceptance_button_params']['subtitle']
            == 'Эконом * 1 точек * 100 ₽'
        )


@pytest.mark.parametrize('is_price_hidden', [True, False])
@pytest.mark.config(
    DRIVER_ORDERS_BUILDER_IS_PRICE_HIDDEN_FROM_CARGO_ORDERS=True,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enable_requirements_rebuild': True,
        'enable_cargo_multipoints': True,
    },
)
@pytest.mark.now(MOCKED_NOW)
async def test_cargo_subtitle_with_price_is_price_hidden_from_cargo_orders(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        mock_cargo_setcar_data,
        is_price_hidden,
        order_proc,
):
    await taxi_driver_orders_builder.invalidate_caches()

    cargo_ref_id = 'cargo_claim_pid_1'
    mock_cargo_setcar_data(
        comment='Заказ с подтверждением по СМС.\n'
        'Комментарий из сервиса cargo-dispatch',
        points_count=1,
        pricing={
            'price': {'total': '100.30', 'surge': '10.50'},
            'currency': {'code': 'RUB'},
            'is_price_hidden': is_price_hidden,
        },
        tariff_class='courier',
    )

    order_proc.set_file(load_json, 'order_core_response3.json')
    proc_request = order_proc.order_proc['fields']['order']['request']
    proc_request['requirements'] = {'cargo_type': 'lcv_l'}
    proc_request['cargo_ref_id'] = cargo_ref_id
    proc_request['corp_comment'] = 'Корп комментарий'
    proc_request['comment'] = 'Негодный комментарий из сервиса cargo-dispatch'
    proc_request['corp'] = {'client_id': 'corp_client_id_12312312312312312'}

    setcar_json = load_json('setcar_requirements.json')
    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200, response.text
    resp = response.json()['setcar']
    if is_price_hidden:
        assert resp['ui']['acceptance_button_params']['subtitle'] == ''
    else:
        assert (
            resp['ui']['acceptance_button_params']['subtitle']
            == 'Эконом * 1 точек * 100 ₽'
        )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enable_requirements_rebuild': True,
        'enable_cargo_multipoints': True,
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.now(MOCKED_NOW)
async def test_cargo_empty_corp_comment(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        mock_cargo_setcar_data,
        setcar_create_params,
        order_proc,
):
    mock_cargo_setcar_data(skip_eta=True)

    order_proc.set_file(load_json, 'order_core_response3.json')
    proc_request = order_proc.order_proc['fields']['order']['request']
    proc_request['cargo_ref_id'] = 'cargo_claim_id_1'
    proc_request['corp_comment'] = ''
    proc_request['comment'] = ''

    setcar_push = load_json('setcar_push.json')
    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text
    assert response.json()['setcar_push'] == setcar_push


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_driver_tags_request': True},
)
@pytest.mark.driver_tags_match(
    dbid='park1', uuid='driver1', tags=['walking_courier'],
)
@pytest.mark.now(MOCKED_NOW)
async def test_walking_courier(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        setcar_create_params,
):
    setcar_json = load_json('setcar.json')
    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text()
    response_json = response.json()['setcar_push']
    assert response_json['taximeter_settings']['show_walk_route_button']

    setcar_redis = json.loads(
        redis_store.hget('Order:SetCar:Items:park1', setcar_json['id']),
    )
    assert 'driver_tags' not in response_json
    assert setcar_redis['driver_tags'] == ['walking_courier']


@pytest.mark.parametrize(
    'subvention_setcar,subvention_push,locale,title',
    [
        (
            'subventions/subvention1.json',
            'subventions/subvention_push1.json',
            'ru',
            '1,3 км · 24 мин',
        ),
        (
            'subventions/subvention2.json',
            'subventions/subvention_push2.json',
            'ru',
            '1,3 км · 24 мин',
        ),
        (
            'subventions/subvention3.json',
            'subventions/subvention_push3.json',
            'en',
            '1.3 km · 24 min',
        ),
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.now(MOCKED_NOW)
async def test_subventions_push(
        taxi_driver_orders_builder,
        load_json,
        subvention_setcar,
        subvention_push,
        locale,
        title,
        mockserver,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_setcar_data(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'park1_driver1',
                    'data': {
                        'locale': locale,
                        'taximeter_version': '9.50',
                        'taximeter_version_type': '',
                        'taximeter_platform': 'android',
                        'fleet_type': 'taximeter',
                    },
                },
            ],
        }

    setcar_json = load_json('setcar.json')
    setcar_json['subvention'] = load_json(subvention_setcar)
    setcar_push = load_json('setcar_push.json')
    setcar_push['subvention'] = load_json(subvention_push)

    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200, response.text
    setcar_push['ui']['accept_toolbar_params']['title'] = title
    assert response.json()['setcar_push'] == setcar_push


FIXED_PRICE_SETCAR_VALUE = {
    'max_distance': 501.0,
    'price': 353.0,
    'show': True,
}
FIXED_PRICE_SETCAR_HIDDEN_VALUE = {
    'max_distance': 501.0,
    'price': 353.0,
    'show': False,
}
BASE_PRICE_EXPECTED = {
    'boarding': 49,
    'destination_waiting': 0,
    'distance': 2514.358041402936,
    'requirements': 0,
    'time': 89.63333333333333,
    'transit_waiting': 0,
    'waiting': 0,
}


@pytest.mark.parametrize(
    [
        'setcar_fixed_price',
        'fixed_price_in_order_proc',
        'expected_base_price',
        'expected_redis_base_price',
    ],
    [
        (None, False, None, None),
        (None, True, None, BASE_PRICE_EXPECTED),
        (FIXED_PRICE_SETCAR_VALUE, False, None, None),
        (
            FIXED_PRICE_SETCAR_VALUE,
            True,
            BASE_PRICE_EXPECTED,
            BASE_PRICE_EXPECTED,
        ),
        (FIXED_PRICE_SETCAR_HIDDEN_VALUE, True, None, BASE_PRICE_EXPECTED),
    ],
    ids=[
        'no_base_price_no_fixed_price',
        'only_orderproc_base_price',
        'fixed_price_without_order_proc_base_price',
        'fixed_price_with_base_price',
        'hidden_prices',
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_requirements_rebuild': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.now(MOCKED_NOW)
async def test_base_price_passing(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        redis_store,
        setcar_fixed_price,
        fixed_price_in_order_proc,
        expected_base_price,
        expected_redis_base_price,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response2.json')
    if fixed_price_in_order_proc:
        order_proc.order_proc['fields']['order']['pricing_data']['user'][
            'base_price'
        ] = BASE_PRICE_EXPECTED
        order_proc.order_proc['fields']['order']['pricing_data']['driver'][
            'base_price'
        ] = BASE_PRICE_EXPECTED

    def order_proc_assert(request_fields):
        assert 'order.pricing_data.user.base_price' in request_fields
        assert 'order.pricing_data.driver.base_price' in request_fields

    order_proc.set_fields_request_assert = order_proc_assert

    setcar_json = load_json('setcar.json')

    if setcar_fixed_price is None:
        setcar_json.pop('fixed_price')
        setcar_json.pop('driver_fixed_price')
    else:
        setcar_json['fixed_price'] = setcar_fixed_price
        setcar_json['driver_fixed_price'] = setcar_fixed_price

    setcar_push = load_json('setcar_push.json')
    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200, response.text
    if expected_base_price is not None:
        setcar_push['base_price'] = {
            'user': expected_base_price,
            'driver': expected_base_price,
        }
    if expected_redis_base_price is not None:
        setcar_json['base_price'] = {
            'user': expected_redis_base_price,
            'driver': expected_redis_base_price,
        }

    if not setcar_fixed_price or not setcar_fixed_price['show']:
        del setcar_push['fixed_price']
        del setcar_push['driver_fixed_price']

    assert response.json()['setcar_push'] == setcar_push

    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    utils.add_accents(setcar_json)
    assert redis_dict == setcar_json


@pytest.mark.parametrize(
    'driver_profile_id, expected_reasons',
    (
        pytest.param(
            'driver1',
            [
                {'id': 'CUSTOM_REASON1', 'text': 'custom_reason1'},
                {'id': 'CUSTOM_REASON2', 'text': 'custom_reason2'},
            ],
            id='driver_has_experiment3',
        ),
        pytest.param(
            'driver2',
            [
                {'id': 'REASON1', 'text': 'reason1'},
                {'id': 'REASON2', 'text': 'reason2'},
            ],
            id='driver_no_experiment3',
        ),
        pytest.param('321', [], id='driver_no_reasons'),
    ),
)
@pytest.mark.translations(
    taximeter_messages={
        'cancel_reason_text.REASON1': {'ru': 'reason1'},
        'cancel_reason_text.REASON2': {'ru': 'reason2'},
        'cancel_reason_text.CUSTOM_REASON1': {'ru': 'custom_reason1'},
        'cancel_reason_text.CUSTOM_REASON2': {'ru': 'custom_reason2'},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_cancel_reasons',
    consumers=['driver-orders-builder/setcar'],
    clauses=[
        {
            'title': 'driver_123',
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': ['driver1'],
                    'arg_name': 'driver_profile_id',
                    'set_elem_type': 'string',
                },
            },
            'value': {'driving': ['CUSTOM_REASON1', 'CUSTOM_REASON2']},
        },
        {
            'title': 'driver_321',
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': ['321'],
                    'arg_name': 'driver_profile_id',
                    'set_elem_type': 'string',
                },
            },
            'value': {},
        },
    ],
    default_value={'driving': ['REASON1', 'REASON2']},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.now(MOCKED_NOW)
async def test_cancel_reasons(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        redis_store,
        driver_profile_id,
        expected_reasons,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response.json')
    order_proc.order_proc['fields']['candidates'][0][
        'driver_id'
    ] = driver_profile_id

    setcar_json = load_json('setcar.json')
    setcar_json['driver_id'] = driver_profile_id
    request = {
        'driver': {
            'park_id': 'park1',
            'driver_profile_id': driver_profile_id,
            'alias_id': '4d605a2849d747079b5d8c7012830419',
        },
        'order_id': 'test_order_id',
    }
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']
    assert (
        response_json.get('cancel_reason_info', {}).get('reasons', {})
        == expected_reasons
    )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enable_driver_points_info': True,
        'enable_replace_driver_points_info': True,
    },
)
@pytest.mark.parametrize(
    'expected_points',
    [
        (
            {
                'c': 5,
                'n': -5,
                'p': 0,
                'long_wait_cancel': 0,
                'c_subtitle': 'Теперь действует бонус',
                'c_title': 'Активность: 5 баллов',
                'long_wait_cancel_title': 'Укажите причину отмены',
                'n_subtitle': (
                    'При потере ещё 36 баллов наступит блокировка на 1 час'
                ),
                'n_title': 'Активность: -5 баллов',
                'p_subtitle': (
                    'Примите следующий заказ, чтобы восстановить показатель'
                ),
                'p_title': 'Активность: 0 баллов',
            }
        ),
    ],
)
@pytest.mark.now(MOCKED_NOW)
async def test_driver_points_info(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        redis_store,
        expected_points,
        setcar_create_params,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response1.json')

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']
    assert response_json.get('driver_points_info', {}) == expected_points


LOGISTIC_DATA = {'logistic': {'shift': {'id': 'shift_id'}}}


def _get_courier_header(
        show_type,
        subtitle_show_type,
        tanker_key=None,
        subtitle_tanker_key=None,
        time_interval_type=None,
):
    return {
        'show_type': show_type,
        'subtitle_show_type': subtitle_show_type,
        'tanker_key': tanker_key,
        'subtitle_tanker_key': subtitle_tanker_key,
        'time_interval_type': time_interval_type,
    }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False, 'autocancel_processing': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_cargo_multipoints': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_courier_autocancel',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'autocancel': 666},
)
@pytest.mark.parametrize(
    'is_default_layout_for_chain_order_by_exp', [True, False],
)
@pytest.mark.parametrize('is_enabled_timer_description_by_exp', [True, False])
@pytest.mark.parametrize('is_enabled_chain_order_by_exp', [True, False])
@pytest.mark.parametrize('is_rear_card_enabled', [True, False])
@pytest.mark.parametrize(
    [
        'show_type',
        'subtitle_show_type',
        'tanker_key',
        'subtitle_tanker_key',
        'set_brand_name',
        'time_interval_type',
    ],
    [
        pytest.param(
            'restaurant_name',
            'pickup_time',
            None,
            None,
            True,
            None,
            id='rest/pickup',
        ),
        pytest.param(
            'tanker_string',
            'pickup_time',
            'eats_courier_order_title',
            None,
            True,
            None,
            id='tanker/pickup',
        ),
        pytest.param(
            'restaurant_name',
            'tanker_string',
            None,
            'eats_courier_order_subtitle',
            True,
            None,
            id='rest/tanker',
        ),
        pytest.param(
            'tanker_string',
            'tanker_string',
            'eats_courier_order_title',
            'eats_courier_order_subtitle',
            True,
            None,
            id='tanker/tanker',
        ),
        pytest.param(
            'restaurant_name',
            'tanker_string',
            'eats_courier_order_title',
            'eats_courier_order_subtitle',
            False,
            None,
            id='rest/tanker fallback',
        ),
        pytest.param('as_is', 'as_is', None, None, False, None, id='as is'),
        pytest.param(
            'tanker_string',
            'tanker_string',
            'eats_courier_order_title',
            'eats_courier_order_subtitle',
            True,
            'b_a',
            id='tanker/tanker_ba',
        ),
        pytest.param(
            'restaurant_name',
            'tanker_string',
            'eats_courier_order_title',
            'eats_courier_order_subtitle',
            False,
            'b_a',
            id='rest/tanker_ba fallback',
        ),
    ],
)
@pytest.mark.now(MOCKED_NOW)
async def test_courier_shift(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        redis_store,
        experiments3,
        mock_cargo_setcar_data,
        show_type,
        subtitle_show_type,
        tanker_key,
        subtitle_tanker_key,
        set_brand_name,
        time_interval_type,
        setcar_create_params,
        is_default_layout_for_chain_order_by_exp,
        is_enabled_chain_order_by_exp,
        is_enabled_timer_description_by_exp,
        is_rear_card_enabled,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response_courier.json')
    if time_interval_type:
        order_proc.order_proc['fields']['candidates'][0]['cp'] = {
            'dest': [39.1841354, 51.66608211],
            'left_time': 1600,
            'left_dist': 1395,
            'id': '41bbe72753cf23ab86eba994c231085c',
        }
        order_proc.order_proc['fields']['candidates'][0]['time'] = 2000

    def _update_setcar(setcar):
        setcar['internal']['payment_type'] = 'cash'

        setcar['ui']['acceptance_items'][0] = {
            'background': {'type': 'balloon'},
            'markdown': True,
            'primary_max_lines': 3,
            'reverse': True,
            'secondary_max_lines': 1,
            'subtitle': 'Какой-то комментарий',
            'title': 'Комментарий',
            'type': 'default',
        }

        title_overrides = {
            'pickup_time': '24 мин',
            'restaurant_name': 'McDonalds',
            'tanker_string': 'Доставка Яндекс.Еды',
        }
        subtitle_overrides = {
            'pickup_time': '24 мин',
            'restaurant_name': 'McDonalds',
            'tanker_string': 'Заказ по цепочке через 24 мин',
            'as_is': '',
        }
        if time_interval_type:
            title_overrides['pickup_time'] = '7 мин'
            subtitle_overrides[
                'tanker_string'
            ] = 'Заказ по цепочке через 7 мин'
        setcar.update(LOGISTIC_DATA)
        setcar.update({'autocancel': 666})

        if show_type != 'as_is':
            setcar['ui']['accept_toolbar_params']['title'] = title_overrides[
                show_type
            ]
        setcar['ui']['accept_toolbar_params']['subtitle'] = subtitle_overrides[
            subtitle_show_type
        ]

        setcar['ui']['acceptance_button_params']['bg_color'] = '#f2e15c'
        setcar['ui']['acceptance_button_params']['text_color'] = '#21201f'

        if is_enabled_chain_order_by_exp:
            if time_interval_type:
                if is_enabled_timer_description_by_exp:
                    setcar['ui']['acceptance_items'].insert(
                        0,
                        {
                            'background': {
                                'color_day': 'main_bg',
                                'corner_radius': 'mu_1',
                                'type': 'rect',
                            },
                            'horizontal_divider_type': 'full',
                            'left_tip': {
                                'icon': {
                                    'icon_type': 'info',
                                    'tint_color': '#2F5BC7',
                                },
                            },
                            'title': (
                                'Таймер начнёт работать,'
                                ' после окончания текущего заказа'
                            ),
                            'type': 'tip_detail',
                        },
                    )
                setcar['ui']['rear_card_title'] = 'Следующий заказ'
                if not is_default_layout_for_chain_order_by_exp:
                    setcar['ui']['rear_card'] = {
                        'background_color': '#000000',
                        'text_color': '#ffffff',
                        'title': setcar['ui']['rear_card_title'],
                    }

        if not set_brand_name and show_type == 'restaurant_name':
            setcar['ui']['accept_toolbar_params']['title'] = title_overrides[
                'pickup_time'
            ]

    exp_default_value = {
        'header': _get_courier_header(
            show_type,
            subtitle_show_type,
            tanker_key,
            subtitle_tanker_key,
            time_interval_type,
        ),
        'acceptance_button': {'use_default': True},
    }
    clauses = []
    if is_enabled_chain_order_by_exp:
        exp_clause_value = exp_default_value.copy()
        exp_clause_value['rear_card_layout'] = (
            'default' if is_default_layout_for_chain_order_by_exp else 'custom'
        )
        if is_enabled_timer_description_by_exp:
            exp_clause_value[
                'timer_description_tanker_key'
            ] = 'cargo_order_timer_description'
        clauses = [
            {
                'title': 'for_chain_order',
                'predicate': {
                    'type': 'bool',
                    'init': {'arg_name': 'has_chain_parent'},
                },
                'value': exp_clause_value,
            },
        ]
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        consumers=['driver-orders-builder/setcar'],
        clauses=clauses,
        name='driver_orders_builder_courier_screen_settings',
        default_value=exp_default_value,
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        consumers=['driver-orders-builder/setcar'],
        clauses=[],
        name='driver_orders_builder_rear_card_settings',
        default_value={
            'enabled': is_rear_card_enabled,
            'background_color': '#FFFFFF',
            'text_color': '#000000',
        },
    )
    await taxi_driver_orders_builder.invalidate_caches()

    custom_context = {}
    if set_brand_name:
        custom_context['brand_name'] = 'McDonalds'
    mock_cargo_setcar_data(custom_context=custom_context)

    setcar_json = load_json('setcar.json')
    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200

    response_data = response.json()['setcar_push']

    assert 'logistic' in response_data
    assert response_data['logistic'] == LOGISTIC_DATA['logistic']

    setcar_push = load_json('setcar_push.json')
    _update_setcar(setcar_push)
    del response_data['cargo']
    assert response_data == setcar_push

    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    utils.add_accents(setcar_json)
    _update_setcar(setcar_json)
    del redis_dict['cargo']
    assert redis_dict == setcar_json


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_cargo_multipoints': True},
)
@pytest.mark.parametrize(
    'tg_notify_times_called',
    [
        pytest.param(
            2,
            marks=[
                pytest.mark.config(
                    ENABLE_TG_NOTIFICATION_FOR_EATS_COURIER=True,
                ),
            ],
            id='enabled',
        ),
        pytest.param(
            0,
            marks=[
                pytest.mark.config(
                    ENABLE_TG_NOTIFICATION_FOR_EATS_COURIER=False,
                ),
            ],
            id='disabled',
        ),
        pytest.param(
            2,
            marks=[
                pytest.mark.config(
                    ENABLE_TG_NOTIFICATION_FOR_EATS_COURIER=True,
                ),
                pytest.mark.config(
                    CORP_BLOCKLIST_FOR_TG_NOTIFICATION=['corp_client_id'],
                ),
            ],
            id='allowed',
        ),
        pytest.param(
            0,
            marks=[
                pytest.mark.config(
                    ENABLE_TG_NOTIFICATION_FOR_EATS_COURIER=True,
                ),
                pytest.mark.config(
                    CORP_BLOCKLIST_FOR_TG_NOTIFICATION=['corp_client_id_1'],
                ),
            ],
            id='blocked',
        ),
    ],
)
@pytest.mark.now(MOCKED_NOW)
async def test_courier_tg_notification(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        stq,
        mock_cargo_setcar_data,
        tg_notify_times_called,
        setcar_create_params,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response_courier.json')

    mock_cargo_setcar_data(claim_ids=['claim_id_1', 'claim_id_2'])

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200

    assert (
        stq.eats_logistics_performer_pre_assign.times_called
        == tg_notify_times_called
    )
    if tg_notify_times_called:
        kwargs = stq.eats_logistics_performer_pre_assign.next_call()['kwargs']
        assert kwargs['claim_id'] == 'claim_id_1'
        assert (
            kwargs['park_driver_profile_id']
            == f'{PARAMS["driver"]["park_id"]}_'
            f'{PARAMS["driver"]["driver_profile_id"]}'
        )

        kwargs = stq.eats_logistics_performer_pre_assign.next_call()['kwargs']
        assert kwargs['claim_id'] == 'claim_id_2'
        assert (
            kwargs['park_driver_profile_id']
            == f'{PARAMS["driver"]["park_id"]}_'
            f'{PARAMS["driver"]["driver_profile_id"]}'
        )


def _get_courier_surge_setting(enable, message_template=None):
    return {
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'is_config': False,
        'name': 'driver_orders_builder_courier_surge_settings',
        'consumers': ['driver-orders-builder/setcar'],
        'clauses': [],
        'default_value': {
            'enable': enable,
            'message_template': message_template,
        },
    }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False, 'autocancel_processing': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_cargo_multipoints': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_courier_screen_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'header': _get_courier_header('restaurant_name', 'pickup_time'),
        'acceptance_button': {'use_default': True},
    },
)
@pytest.mark.parametrize(
    'surge_offer,surge_enable,have_message',
    [
        pytest.param(
            {'price': '123.45', 'currency': '₽', 'currency_code': 'RUB'},
            True,
            True,
            marks=[
                pytest.mark.experiments3(
                    **_get_courier_surge_setting(
                        enable=True,
                        message_template='eats_courier_surge_message',
                    ),
                ),
            ],
            id='ok',
        ),
        pytest.param(
            {'price': '123.45', 'currency': '₽', 'currency_code': 'RUB'},
            True,
            False,
            marks=[
                pytest.mark.experiments3(
                    **_get_courier_surge_setting(enable=True),
                ),
            ],
            id='ok without message',
        ),
        pytest.param(
            None,
            False,
            False,
            marks=[
                pytest.mark.experiments3(
                    **_get_courier_surge_setting(
                        enable=True,
                        message_template='eats_courier_surge_message',
                    ),
                ),
            ],
            id='Without surge',
        ),
        pytest.param(
            {'price': '123.45', 'currency': '₽', 'currency_code': 'RUB'},
            False,
            False,
            marks=[
                pytest.mark.experiments3(
                    **_get_courier_surge_setting(enable=False),
                ),
            ],
            id='Surge off',
        ),
    ],
)
@pytest.mark.now(MOCKED_NOW)
async def test_courier_eats_surge(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        redis_store,
        mock_cargo_setcar_data,
        surge_offer,
        surge_enable,
        have_message,
        setcar_create_params,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response_courier.json')

    def _update_setcar(setcar):
        setcar['internal']['payment_type'] = 'cash'

        setcar['ui']['acceptance_items'][0] = {
            'background': {'type': 'balloon'},
            'markdown': True,
            'primary_max_lines': 3,
            'reverse': True,
            'secondary_max_lines': 1,
            'subtitle': 'Какой-то комментарий',
            'title': 'Комментарий',
            'type': 'default',
        }

        setcar.update(LOGISTIC_DATA)
        setcar.update({'autocancel': 60})
        setcar['ui']['accept_toolbar_params']['title'] = 'McDonalds'
        setcar['ui']['accept_toolbar_params']['subtitle'] = '24 мин'
        if surge_enable:
            setcar['ui']['acceptance_button_params']['bg_color'] = '#820abe'
            setcar['ui']['acceptance_button_params']['text_color'] = '#ffffff'
            if have_message:
                setcar['ui']['acceptance_button_params'][
                    'subtitle'
                ] = f'Доплата: {surge_offer["price"]}{surge_offer["currency"]}'
        else:
            setcar['ui']['acceptance_button_params']['bg_color'] = '#f2e15c'
            setcar['ui']['acceptance_button_params']['text_color'] = '#21201f'

    custom_context = {'brand_name': 'McDonalds'}
    mock_cargo_setcar_data(
        surge_offer=surge_offer, custom_context=custom_context,
    )

    setcar_json = load_json('setcar.json')
    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200

    response_data = response.json()['setcar_push']

    assert 'logistic' in response_data
    assert response_data['logistic'] == LOGISTIC_DATA['logistic']

    setcar_push = load_json('setcar_push.json')
    _update_setcar(setcar_push)
    del response_data['cargo']
    assert response_data == setcar_push

    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    utils.add_accents(setcar_json)
    _update_setcar(setcar_json)
    del redis_dict['cargo']
    assert redis_dict == setcar_json


def build_feature_support(is_detail_tip, is_semantic_colors):
    feature_support = {}
    if is_detail_tip:
        feature_support['detail_tip'] = '9.49'
    if is_semantic_colors:
        feature_support['semantic_color_scheme'] = '9.49'
    return feature_support


@pytest.mark.experiments3(
    match={
        'predicate': {'init': {'arg_name': 'shift_id'}, 'type': 'not_null'},
        'enabled': True,
    },
    is_config=True,
    name='taximeter_courier_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'some_int_value': 100, 'some_bool_value': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.config(
    EXPERIMENTS3_TO_TAXIMETER_SETTINGS_MAP={
        'experiments': [],
        'configs': [
            {
                'name': 'taximeter_courier_settings',
                'taximeter_settings_property': 'courier_settings',
            },
        ],
    },
)
@pytest.mark.now(MOCKED_NOW)
async def test_courier_shift_kwarg(
        taxi_driver_orders_builder,
        mockserver,
        load_json,
        setcar_create_params,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response_courier.json')

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200
    response_json = response.json()['setcar']
    assert response_json['taximeter_settings']['courier_settings'] == {
        'some_int_value': 100,
        'some_bool_value': True,
    }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_driver_tags_request': True},
)
@pytest.mark.driver_tags_match(dbid='park1', uuid='driver1', tags=['some_tag'])
@pytest.mark.parametrize(
    'config, subtitle, category_localized, driver_fixed_price, fixed_price',
    [
        (
            {'show_income_cost': True},
            'Комфорт · 453 ₽',
            True,
            {'max_distance': 501.0, 'price': 453.0, 'show': True},
            {'max_distance': 501.0, 'price': 353.0, 'show': True},
        ),
        (
            {'show_income_cost': True},
            '353 ₽',
            False,
            None,
            {'max_distance': 501.0, 'price': 353.0, 'show': True},
        ),
        ({'show_income_cost': True}, 'Комфорт', True, None, None),
        (
            {'show_income_cost': False},
            'Комфорт',
            True,
            {'max_distance': 501.0, 'price': 353.0, 'show': False},
            {'max_distance': 501.0, 'price': 353.0, 'show': False},
        ),
        (
            {'show_income_cost': False},
            '',
            False,
            {'max_distance': 501.0, 'price': 353.0, 'show': False},
            {'max_distance': 501.0, 'price': 353.0, 'show': False},
        ),
        (
            {},
            '',
            False,
            {'max_distance': 501.0, 'price': 353.0, 'show': False},
            {'max_distance': 501.0, 'price': 353.0, 'show': False},
        ),
    ],
)
@pytest.mark.now(MOCKED_NOW)
async def test_show_price_on_accept(
        taxi_driver_orders_builder,
        load_json,
        experiments3,
        config,
        subtitle,
        category_localized,
        driver_fixed_price,
        fixed_price,
        redis_store,
):
    setcar_json = load_json('setcar.json')
    del setcar_json['category_localized']
    del setcar_json['driver_fixed_price']
    del setcar_json['fixed_price']
    if category_localized:
        setcar_json['category_localized'] = 'Комфорт'
    if driver_fixed_price is not None:
        setcar_json['driver_fixed_price'] = driver_fixed_price
    if fixed_price is not None:
        setcar_json['fixed_price'] = fixed_price

    experiments3.add_config(
        consumers=['driver-orders-builder/setcar'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        name='taximeter_cost_settings_accept',
        default_value=config,
    )
    await taxi_driver_orders_builder.invalidate_caches()
    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200, response.text()
    assert (
        response.json()['setcar']['ui']['acceptance_button_params']['subtitle']
        == subtitle
    )

    if 'show_income_cost' in config and config['show_income_cost']:
        redis_str = redis_store.hget(
            'Order:SetCar:Items:park1', setcar_json['id'],
        )
        redis_dict = json.loads(redis_str)
        if driver_fixed_price is not None:
            assert redis_dict['driver_fixed_price']['show']
        if fixed_price is not None:
            assert redis_dict['fixed_price']['show']


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enable_requirements_rebuild': True,
        'enable_cargo_multipoints': True,
    },
)
@pytest.mark.parametrize(
    'tariff_class, expected_comment',
    [
        ('eda', 'eda comment'),
        ('lavka', 'lavka comment'),
        ('courier', 'default cargo comment'),
    ],
)
@pytest.mark.experiments3()
@pytest.mark.now(MOCKED_NOW)
async def test_cargo_order_overwrite(
        order_proc,
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        mock_cargo_setcar_data,
        tariff_class: str,
        expected_comment: str,
        cargo_ref_id='cargo_claim_id_1',
):
    mock_cargo_setcar_data(
        comment='default cargo comment',
        comment_overwrites=[
            {'tariff': 'eda', 'comment': 'eda comment'},
            {'tariff': 'lavka', 'comment': 'lavka comment'},
        ],
    )

    order_proc.set_file(load_json, 'order_core_response3.json')
    order_proc.order_proc['fields']['candidates'][0][
        'tariff_class'
    ] = tariff_class
    proc_request = order_proc.order_proc['fields']['order']['request']
    proc_request['requirements'] = {'cargo_type': 'lcv_l'}
    proc_request['cargo_ref_id'] = cargo_ref_id
    proc_request['corp_comment'] = 'Корп комментарий'
    proc_request['comment'] = 'Негодный комментарий из сервиса cargo-dispatch'
    proc_request['corp'] = {'client_id': 'corp_client_id_12312312312312312'}

    setcar_json = load_json('setcar_requirements.json')
    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200, response.text
    resp = response.json()['setcar']
    assert resp['description'] == expected_comment

    subtitle = next(
        i['subtitle']
        for i in resp['ui']['acceptance_items']
        if i['type'] == 'default'
    )
    assert subtitle == '**Большой кузов.**  \n' + expected_comment


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enable_requirements_rebuild': True,
        'enable_cargo_multipoints': True,
    },
)
@pytest.mark.config(
    DRIVER_ORDERS_BUILDER_HIDE_COMMENT={
        'enabled': True,
        'min_version': '9.20',
    },
)
@pytest.mark.experiments3()
@pytest.mark.now(MOCKED_NOW)
async def test_cargo_hide_comment(
        taxi_driver_orders_builder,
        order_proc,
        load_json,
        mockserver,
        mock_cargo_setcar_data,
        exp_cargo_setcar_requirements,
        tariff_class='eda',
        cargo_ref_id='cargo_claim_id_1',
):
    mock_cargo_setcar_data(
        comment='default cargo comment',
        comment_overwrites=[{'tariff': 'eda', 'comment': ''}],
    )
    await exp_cargo_setcar_requirements(
        tariff=tariff_class, hidden_requirements=['cargo_type'],
    )

    order_proc.set_file(load_json, 'order_core_response3.json')
    order_proc.order_proc['fields']['candidates'][0][
        'tariff_class'
    ] = tariff_class
    proc_request = order_proc.order_proc['fields']['order']['request']
    proc_request['requirements'] = {'cargo_type': 'lcv_l'}
    proc_request['cargo_ref_id'] = cargo_ref_id
    proc_request['corp_comment'] = 'Корп комментарий'
    proc_request['comment'] = 'Негодный комментарий из сервиса cargo-dispatch'
    proc_request['corp'] = {'client_id': 'corp_client_id_12312312312312312'}

    setcar_json = load_json('setcar_requirements.json')
    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200, response.text
    resp = response.json()['setcar']
    assert 'description' not in resp

    assert (
        next(
            i.get('subtitle')
            for i in resp['ui']['acceptance_items']
            if i['type'] == 'default' and i['title'] == 'Комментарий'
        )
        == '**Большой кузов.**'
    )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.now(MOCKED_NOW)
async def test_create_setcar_caches(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        parks,
        legal_entities,
        mocked_time,
        setcar_create_params,
):
    async def _round():
        setcar_json = load_json('setcar.json')
        setcar_push = load_json('setcar_push.json')

        response = await taxi_driver_orders_builder.post(
            **setcar_create_params,
        )

        assert response.status_code == 200, response.text
        resp = response.json()
        redis_str = redis_store.hget(
            'Order:SetCar:Items:park1', setcar_json['id'],
        )
        redis_dict = json.loads(redis_str)
        utils.add_accents(setcar_json)
        setcar_json['number'] = redis_dict['number']
        setcar_push['number'] = redis_dict['number']
        assert redis_dict == setcar_json
        assert resp['setcar'] == setcar_json
        assert resp['setcar_push'] == setcar_push

    # Ideal
    await _round()
    assert len(parks.get_requests()) == 1
    assert len(legal_entities.get_requests()) == 1

    # Get actual data from cache
    await _round()
    assert len(parks.get_requests()) == 1
    assert len(legal_entities.get_requests()) == 1

    # Get expired data from cache because other services are gone
    mocked_time.sleep(3600)
    parks.set_error(True)
    legal_entities.set_error(True)
    await _round()
    assert len(parks.get_requests()) > 1
    assert len(legal_entities.get_requests()) > 1


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='people_combo_order_taximeter',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enabled': True,
        'combo_inner': {
            'accept_toolbar': {
                'subtitle': 'people_combo_order.inner.taximeter.comment.title',
            },
            'comment_prefix': (
                'people_combo_order.inner.taximeter.comment.text'
            ),
        },
        'combo_outer': {
            'accept_toolbar': {
                'subtitle': 'people_combo_order.outer.taximeter.comment.title',
            },
            'comment_prefix': (
                'people_combo_order.outer.taximeter.comment.text'
            ),
        },
    },
)
@pytest.mark.now(MOCKED_NOW)
async def test_create_setcar_people_combo_order(
        taxi_driver_orders_builder,
        mockserver,
        load_json,
        params_wo_original_setcar,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response3.json')
    order_proc.order_proc['fields']['order']['calc'] = {
        'alternative_type': 'combo_inner',
    }

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )

    assert response.status_code == 200, response.text
    resp = response.json()
    assert (
        resp['setcar']['ui']['accept_toolbar_params']['subtitle']
        == 'combo inner title'
    )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='setcar_constructor_modifications_items',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'tyler': {'id': 'iamtyler'},
        'activity': {'id': 'activity_item'},
        'surge': {'id': 'surge_item'},
    },
)
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'modifications_items': '2.00'}},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_price_activity_rebuild': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.now(MOCKED_NOW)
async def test_modificators_items(taxi_driver_orders_builder, load_json):
    setcar_json = load_json('setcar.json')

    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    setcar_json['ui']['acceptance_items'][0] = {
        'id': 'iamtyler',
        'items': [
            {'id': 'activity_item', 'short_info': '+5', 'title': 'Активность'},
        ],
    }

    assert response.status_code == 200, response.text
    resp = response.json()
    assert resp['setcar'] == setcar_json


@pytest.mark.config(
    DA_OFFER_TIMEOUT_BY_TARIFF={
        '__default__': {'__default__': 10, 'lavka': 20},
        'spb': {'__default__': 121, 'lavka': 17},
    },
    TAXIMETER_SHOW_SURGE_DRIVER_BY_STATUS={
        '__default__': {
            'show_for_statuses': ['assigned', 'driving', 'waiting'],
        },
    },
    TAXIMETER_SHOW_PAYMENT_TYPE_DRIVER_BY_STATUS={
        '__default__': {
            'show_for_statuses': ['waiting', 'transporting', 'complete'],
        },
    },
    TAXIMETER_SHOW_TIME_DELAY={
        '__default__': {
            '__default__': {
                'assigned': 0,
                'complete': 3,
                'driving': 0,
                'transporting': 3,
                'waiting': 0,
            },
        },
    },
    TAXIMETER_DRIVERCOST_HIDE={
        '__default__': {
            'enable': True,
            'fixed_price': False,
            'hide_plate': False,
            'hide_widget': True,
            'payment_types': [],
        },
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enable_candidate_meta_request': True,
        'enable_requirements_rebuild': True,
        'enable_park_aggregator_redis_source': True,
    },
)
@pytest.mark.parametrize(
    'monkey_patches',
    [
        {'name': 'vanilla'},
        {
            'name': 'payment_type',
            'order_proc': {'payment_tech': {'type': 'card'}},
            'pretty_setcar': {
                'pay_type': PAY_TYPE_CASHLESS,
                'internal': {'payment_type': 'card'},
                'type_name': 'Яндекс.Безналичный',
                'type_color': '#FFFF8000',
                'type_id': '123456',
            },
        },
        {
            'name': 'booking_time_settings_1',
            'order_proc': {
                'aliases': {
                    '$patch': {
                        'due': datetime.datetime(2021, 8, 18, 6, 22, 00),
                    },
                },
                'order': {'_type': 'soon'},
            },
            'pretty_setcar': {
                'date_drive': utils.date_to_taximeter_str(
                    '2021-08-18T09:22:00+03:00',
                ),
                'date_last_change': utils.date_to_taximeter_str(MOCKED_NOW),
                'kind': 1,
            },
        },
        {
            'name': 'booking_time_settings_2',
            'order_proc': {
                'aliases': {
                    '$patch': {
                        'due': datetime.datetime(2021, 8, 18, 6, 22, 00),
                    },
                },
            },
            'pretty_setcar': {
                'date_drive': utils.date_to_taximeter_str(
                    '2021-08-18T09:22:00+03:00',
                ),
                'date_last_change': utils.date_to_taximeter_str(MOCKED_NOW),
                'kind': 2,
            },
        },
        {
            'name': 'autocancel_1',
            'order_proc': {'order': {'nz': 'spb'}},
            'pretty_setcar': {'autocancel': 121},
        },
        {
            'name': 'autocancel_2',
            'order_proc': {
                'candidates': {'$patch': {'tariff_class': 'lavka'}},
                'order': {'nz': 'spb'},
            },
            'pretty_setcar': {'autocancel': 17},
            'stubborn_setcar': {'category': 1 << 30, 'category_v2': 'lavka'},
        },
        {
            'name': 'autocancel_3',
            'order_proc': {
                'candidates': {'$patch': {'tariff_class': 'lavka'}},
                'order': {'nz': 'moscow'},
            },
            'pretty_setcar': {'autocancel': 20},
            'stubborn_setcar': {'category': 1 << 30, 'category_v2': 'lavka'},
        },
        {
            'name': 'reposition_1',
            'order_proc': {
                'candidates': {
                    '$patch': {'reposition': {'mode': 'highway to hell'}},
                },
            },
            'pretty_setcar': {'Reposition': True},
        },
        {
            'name': 'cargo_1',
            'order_proc': {
                'order': {
                    'request': {
                        'cargo_ref_id': 'cargo_id',
                        'corp': {
                            'cost_center': '',
                            'client_comment': '',
                            'client_id': 'cargo_corp_client_id',
                        },
                    },
                },
            },
            'original_setcar': {
                'driver_tariff': {'type': 0},
                'tariff': {'type': 0},
            },
            'pretty_setcar': {
                'cargo_ref_id': 'cargo_id',
                'driver_tariff': {'type': 2},
                'tariff': {'type': 2},
            },
            'stubborn_setcar': {'cargo': {'is_batch_order': True}},
        },
        {
            'name': 'geo_sharing_enabled',
            'order_proc': {'order': {'client_geo_sharing_enabled': True}},
            'pretty_setcar': {
                'client_geo_sharing': {
                    'is_enabled': True,
                    'track_id': '40d4167a527340caac75e55040bfd49e',
                },
            },
        },
        {
            'name': 'voucher',
            'order_proc': {'order': {'svo_car_number': 'Е520ВС799'}},
            'pretty_setcar': {'taximeter_settings': {'voucher': True}},
        },
        {
            'name': 'code_dispatch',
            'order_proc': {
                'order': {'extra_data': {'code_dispatch': {'code': '123456'}}},
            },
            'pretty_setcar': {
                'auto_confirmation': {
                    'settings': {
                        'flow': 'code_dispatch',
                        'enabled': True,
                        'set_status': 5,
                    },
                },
                'taximeter_settings': {
                    'auto_confirmation': {
                        'flow': 'code_dispatch',
                        'enabled': True,
                        'set_status': 5,
                    },
                },
            },
        },
        {
            'name': 'dont_check_distance_to_source_point',
            'order_proc': {'order': {'source_within_pp_zone': True}},
            'pretty_setcar': {
                'taximeter_settings': {
                    'dont_check_distance_to_source_point': True,
                },
            },
        },
        {
            'name': 'taximeter_non_default_base_settings',
            'config': {
                'TAXIMETER_SHOW_SURGE_DRIVER_BY_STATUS': {
                    '__default__': {
                        'show_for_statuses': ['assigned', 'driving'],
                    },
                },
                'TAXIMETER_SHOW_PAYMENT_TYPE_DRIVER_BY_STATUS': {
                    '__default__': {
                        'show_for_statuses': ['transporting', 'complete'],
                    },
                },
                'TAXIMETER_SHOW_TIME_DELAY': {
                    '__default__': {
                        '__default__': {
                            'assigned': 0,
                            'complete': 5,
                            'driving': 0,
                            'transporting': 5,
                            'waiting': 0,
                        },
                    },
                },
                'TAXIMETER_DRIVERCOST_HIDE': {
                    '__default__': {
                        'enable': True,
                        'fixed_price': False,
                        'hide_plate': True,
                        'hide_widget': False,
                        'payment_types': ['cash'],
                    },
                },
                'TAXIMETER_SHOW_USER_COST_SETTINGS': {
                    'countries': ['rus'],
                    'enable': False,
                },
            },
            'pretty_setcar': {
                'taximeter_settings': {
                    'hide_cost_counter': True,
                    'hide_cost_plate': True,
                    'show_user_cost': True,
                    'showing_payment_type_for': [5, 7],
                    'showing_surge_for': [1, 2],
                    'status_change_delays': {
                        '1': 0,
                        '2': 0,
                        '3': 0,
                        '5': 5,
                        '7': 5,
                    },
                },
            },
        },
        {
            'name': 'requirements_base',
            'order_proc': {
                'order': {
                    'request': {'payment': {'type': 'card'}},
                    'dont_call': True,
                },
                'payment_tech': {'type': 'card'},
            },
            'pretty_setcar': {
                'internal': {'payment_type': 'card'},
                'requirement_list': [
                    {'id': 'creditcard'},
                    {'id': 'dont_call'},
                ],
                'pay_type': 1,
                'type_color': '#FFFF8000',
                'type_id': '123456',
                'type_name': 'Яндекс.Безналичный',
                'ui': {
                    'acceptance_items': {
                        '$insert-1': [
                            {
                                'title': 'Комментарий',
                                'subtitle': (
                                    '**Пассажир попросил ему не звонить.**'
                                ),
                                'markdown': True,
                                'primary_max_lines': 3,
                                'reverse': True,
                                'secondary_max_lines': 1,
                                'type': 'default',
                            },
                        ],
                    },
                },
            },
        },
        {
            'name': 'requirements_driver_editable',
            'order_proc': {
                'order': {
                    'nz': 'tel_aviv',
                    'request': {'requirements': {'luggage_count': 2}},
                },
            },
            'config': {
                'EDITABLE_REQUIREMENTS_BY_ZONE': {
                    '__default__': {
                        'linear_overweight': {
                            'default_value': 0,
                            'max_value': 100,
                            'min_value': 0,
                            'show_to_driver': False,
                        },
                        'luggage_count': {
                            'default_value': 0,
                            'max_value': 3,
                            'min_value': 0,
                        },
                        'third_passenger': {
                            'default_value': 0,
                            'max_value': 1,
                            'min_value': 0,
                        },
                        'toll_road_payment': {
                            'default_value': 0,
                            'max_value': 1,
                            'min_value': 0,
                        },
                    },
                },
            },
            'pretty_setcar': {
                'requirement_list': [
                    {
                        'id': 'luggage_count',
                        'amount': 2,
                        'is_editable': True,
                        'min_amount': 0,
                        'max_amount': 3,
                    },
                    {
                        'id': 'third_passenger',
                        'amount': 0,
                        'is_editable': True,
                        'min_amount': 0,
                        'max_amount': 1,
                    },
                    {
                        'id': 'toll_road_payment',
                        'amount': 0,
                        'is_editable': True,
                        'min_amount': 0,
                        'max_amount': 1,
                    },
                ],
                'ui': {
                    'acceptance_items': {
                        '$insert-1': [
                            {
                                'title': 'Комментарий',
                                'subtitle': '**Кол-во багажа: 2.**',
                                'markdown': True,
                                'primary_max_lines': 3,
                                'reverse': True,
                                'secondary_max_lines': 1,
                                'type': 'default',
                            },
                        ],
                    },
                },
            },
        },
        {
            'name': 'requirements_numerical',
            'order_proc': {
                'order': {'request': {'requirements': {'cargo_loaders': 2}}},
            },
            'pretty_setcar': {
                'requirement_list': [{'id': 'cargo_loaders', 'amount': 2}],
                'ui': {
                    'acceptance_items': {
                        '$insert-1': [
                            {
                                'title': 'Комментарий',
                                'subtitle': '**2 грузчика.**',
                                'markdown': True,
                                'primary_max_lines': 3,
                                'reverse': True,
                                'secondary_max_lines': 1,
                                'type': 'default',
                            },
                        ],
                    },
                },
            },
        },
        {
            'name': 'requirements_childchair_1',
            'order_proc': {
                'order': {
                    'request': {'requirements': {'childchair_moscow': 3}},
                },
            },
            'pretty_setcar': {
                'requirement_list': [{'id': 'child_chair.chair', 'amount': 1}],
                'ui': {
                    'acceptance_items': {
                        '$insert-1': [
                            {
                                'title': 'Комментарий',
                                'subtitle': '**Кресло, 3–7 лет.**',
                                'markdown': True,
                                'primary_max_lines': 3,
                                'reverse': True,
                                'secondary_max_lines': 1,
                                'type': 'default',
                            },
                        ],
                    },
                },
            },
        },
        {
            'name': 'requirements_childchair_2',
            'order_proc': {
                'order': {
                    'request': {'requirements': {'childchair_v2': [1, 7]}},
                },
            },
            'pretty_setcar': {
                'requirement_list': [
                    {'id': 'child_chair.infant', 'amount': 1},
                    {'id': 'child_chair.booster', 'amount': 1},
                ],
                'ui': {
                    'acceptance_items': {
                        '$insert-1': [
                            {
                                'title': 'Комментарий',
                                'subtitle': '**Бустер, Кресло, до 3–4 лет.**',
                                'markdown': True,
                                'primary_max_lines': 3,
                                'reverse': True,
                                'secondary_max_lines': 1,
                                'type': 'default',
                            },
                        ],
                    },
                },
            },
        },
        {
            'name': 'requirements_childchair_uber',
            'order_proc': {
                'order': {'request': {'class': ['uberkids']}},
                'candidates': {'$patch': {'tariff_class': 'uberkids'}},
            },
            'pretty_setcar': {
                'ui': {
                    'acceptance_items': {
                        '$insert-1': [
                            {
                                'title': 'Комментарий',
                                'subtitle': '**Детское кресло.**',
                                'markdown': True,
                                'primary_max_lines': 3,
                                'reverse': True,
                                'secondary_max_lines': 1,
                                'type': 'default',
                            },
                        ],
                    },
                },
                'requirement_list': [{'id': 'child_chair'}],
            },
            'stubborn_setcar': {
                'category': 1 << 14,
                'category_v2': 'child_tariff',
            },
        },
        {
            'name': 'requirements_cargo',
            'order_proc': {
                'order': {
                    'request': {
                        'class': ['lavka'],
                        'requirements': {'door_to_door': True},
                    },
                },
                'candidates': {'$patch': {'tariff_class': 'lavka'}},
            },
            'original_setcar': {'requirement_list': [{'id': 'door_to_door'}]},
            'pretty_setcar': {'autocancel': 20, 'requirement_list': []},
            'stubborn_setcar': {'category': 1 << 30, 'category_v2': 'lavka'},
        },
        {
            'name': 'requirements_backward_compatibility',
            'skips_for': ['disabled'],
            'order_proc': {
                'order': {
                    'request': {
                        'requirements': {
                            'animaltransport': True,
                            'door_to_door': True,
                        },
                    },
                },
            },
            'stubborn_setcar': {
                'requirement_list': [
                    {'id': 'door_to_door'},
                    {'id': 'animal_transport'},
                ],
            },
        },
        {
            'name': 'tariffs_v2',
            'order_proc': {
                'order': {
                    'pricing_data': {
                        'geoarea_ids': ['g/through_the_looking_glass'],
                        'driver': {
                            'category_prices_id': (
                                'c/d62355b05dd04b9eb24738c225462025'
                            ),
                        },
                        'user': {
                            'category_prices_id': (
                                'c/d62355b05dd04b9eb24738c225462025'
                            ),
                        },
                    },
                },
            },
            'pretty_setcar': {
                'tariffs_v2': {
                    'driver': {
                        'category_prices_id': (
                            'c/d62355b05dd04b9eb24738c225462025'
                        ),
                        'geoareas': ['g/through_the_looking_glass'],
                    },
                    'user': {
                        'category_prices_id': (
                            'c/d62355b05dd04b9eb24738c225462025'
                        ),
                        'geoareas': ['g/through_the_looking_glass'],
                    },
                },
            },
        },
        {
            'name': 'fixed_price_normal',
            'order_proc': {
                'order': {
                    'fixed_price': {
                        'max_distance_from_b': 501,
                        'price': 666,
                        'show_price_in_taximeter': False,
                    },
                    'pricing_data': {
                        'driver': {'price': {'total': 300}},
                        'user': {'price': {'total': 400}},
                    },
                },
            },
            'pretty_setcar': {
                'driver_fixed_price': {
                    'max_distance': 500,
                    'price': 300,
                    'show': False,
                },
                'fixed_price': {
                    'max_distance': 500,
                    'price': 400,
                    'show': False,
                },
            },
        },
        {
            'name': 'dont_play_welcome_yandex',
            'order_proc': {'order': {'nz': 'baku'}},
            'pretty_setcar': {
                'experiments': [
                    'direct_assignment',
                    'taximeter_complete',
                    'open_near_point_a',
                    'use_lbs_for_waiting_status',
                    'dont_play_welcome_yandex',
                ],
            },
        },
        {
            'name': 'has_hidden_discount',
            'order_proc': {
                'order': {
                    'discount': {
                        'by_classes': [{'class': 'econom', 'value': 0.5}],
                    },
                },
            },
            'pretty_setcar': {'hidden_discount': True},
        },
        {
            'name': 'agent_user_type_corporate',
            'order_proc': {
                'order': {'agent': {'agent_user_type': 'corporate'}},
            },
            'pretty_setcar': {'agent': {'is_corp': True}},
        },
        {
            'name': 'agent_user_type_no_corporate',
            'order_proc': {
                'order': {'agent': {'agent_user_type': 'no_corporate'}},
            },
            'pretty_setcar': {'agent': {'is_corp': False}},
        },
        {
            'name': 'addresses',
            'order_proc': {'order': {'request': {'destinations': []}}},
            'pretty_setcar': {'route_points': []},
        },
        {
            'name': 'address_from',
            'order_proc': {
                'order': {
                    'request': {'source': {'geopoint': [37.46666, 55.66009]}},
                },
            },
            'pretty_setcar': {
                'address_from': {'Lon': 37.46666, 'Lat': 55.66009},
            },
        },
    ],
    ids=lambda params: params['name'],
)
@pytest.mark.now(MOCKED_NOW)
async def test_create_setcar_migration_processings(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        mockserver,
        parks,
        order_proc,
        experiments3,
        taxi_config,
        monkey_patches,
):
    order_proc.set_file(load_json, 'order_core_response_migration.json')
    experiments_data = load_json('experiments3_defaults.json')
    for config in experiments_data['configs']:
        if config['name'] == 'driver_orders_builder_requirements':
            for clause in config['clauses']:
                for entry in clause['value'].values():
                    entry.pop('dryrun', None)
            for entry in config['default_value'].values():
                entry.pop('dryrun', None)

    experiments3.add_experiments_json(experiments_data)

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_orders_builder_processings_settings',
        consumers=['driver-orders-builder/setcar'],
        clauses=[],
        default_value={
            '__default__': False,
            'address_processing': True,
            'agent_processing': True,
            'auto_confirmation_processing': True,
            'autocancel_processing': True,
            'booking_time_processing': True,
            'cargo_processing': True,
            'geo_sharing_processing': True,
            'hidden_discount_info_processing': True,
            'fixed_price_processing': True,
            'legacy_experiments_processing': True,
            'order_source_processing': True,
            'park_aggregator_processing': True,
            'park_clid_processing': True,
            'pay_type_processing': True,
            'reposition_processing': True,
            'requirements_processing': True,
            'route_info_processing': True,
            'set_driver_and_car_processing': True,
            'tariffs_v2_processing': True,
            'taximeter_settings_processing': True,
            'work_rules_processing': True,
            'extended_comment_processing': False,
        },
    )

    if 'config' in monkey_patches:
        taxi_config.set_values(monkey_patches['config'])

    setcar_push_ignore = [
        'client_geo_sharing',
        'driver_fixed_price',
        'fixed_price',
        'route_points',
    ]
    parks.set_aggregators_id({'park1': 'aggregator1'})
    redis_store.hmset(
        'Aggregator:YandexClid', {'aggregator1_clid': 'aggregator_guid_new'},
    )

    order_proc_patch = {
        'order': {
            'calc': {'distance': 20000, 'time': 666},
            'dont_call': utils.DELETE_KEY,
            'source': 'yauber',
        },
    }

    utils.apply_patch(order_proc.order_proc['fields'], order_proc_patch)
    utils.apply_patch(
        order_proc.order_proc['fields'], monkey_patches.get('order_proc', {}),
    )

    candidate_time = math.ceil(
        order_proc.order_proc['fields']['candidates'][0]['time'],
    )
    expected_route_time = utils.parse_date_str(
        MOCKED_NOW,
    ) + datetime.timedelta(seconds=candidate_time)

    @mockserver.json_handler('/candidate-meta/v1/candidate/meta/get')
    def _mock_candidate_meta(request):
        return {'metadata': {}}

    setcar_original_patch = {
        'agg': 'aggregator_guid_old',
        'client_geo_sharing': {'track_id': 'old_track_id'},
        'autocancel': 30,
        'source': 'yauber_old',
        'date_create': '2021-08-18T13:13:13.666000Z',
        'date_drive': '2021-08-18T13:13:13.999000Z',
        'date_last_change': '2021-08-18T13:13:13.666000Z',
        'kind': 13,
        'order_details': [
            {
                'title': 'I\'m on the highway to hell',
                'subtitle': 'Highway to hell',
                'type': 'highway_to_hell',
            },
        ],
    }
    setcar_stubborn_patch = {
        'fixed_price': utils.DELETE_KEY,
        'driver_fixed_price': utils.DELETE_KEY,
        'experiments': [
            'direct_assignment',
            'taximeter_complete',
            'open_near_point_a',
            'use_lbs_for_waiting_status',
        ],
        'tariffs_v2': {
            'driver': {
                'category_prices_id': 'c/168c3ba42916455ca95cbbdd96ea6678',
                'geoareas': ['g/2bab7eff1aa848b681370b2bd83cfbf9'],
            },
            'user': {
                'category_prices_id': 'c/168c3ba42916455ca95cbbdd96ea6678',
                'geoareas': ['g/2bab7eff1aa848b681370b2bd83cfbf9'],
            },
        },
    }
    setcar_pretty_patch = {
        'agg': 'aggregator_guid_new',
        'client_geo_sharing': {'track_id': '40d4167a527340caac75e55040bfd49e'},
        'source': 'uber',
        'date_create': utils.date_to_taximeter_str(MOCKED_NOW),
        'route_time': utils.date_to_taximeter_str(expected_route_time),
        'is_long_order': True,
        'order_details': [
            {'subtitle': '12 мин, 20 км', 'title': '', 'type': 'long_route'},
        ],
        'clid': 'aggregator1_clid',
        'car_name': 'Pagani Zonda R',
        'car_number': 'X666XXX666',
        'driver_signal': 'rogue_one',
        'car_franchise': True,
        'car_id': '13e21f1abac24eb78f8ffaf8db872a28',
        'driver_id': 'driver1',
        'driver_name': 'Иванов Иван Иванович',
        'tariffs_v2': {'is_fallback_pricing': False},
        'type_name': 'Яндекс',
        'type_color': '#FF7AFF00',
        'type_id': 'abcdef',
    }

    await taxi_driver_orders_builder.invalidate_caches()

    setcar_original = load_json('setcar_migration.json')
    setcar_json = load_json('setcar_migration.json')
    setcar_push = load_json('setcar_migration_push.json')

    for target in [setcar_original, setcar_json, setcar_push]:
        for patch in [setcar_stubborn_patch]:
            utils.apply_patch(target, patch)
    for target in [setcar_original]:
        for patch in [
                setcar_original_patch,
                monkey_patches.get('original_setcar', {}),
        ]:
            utils.apply_patch(target, patch)
    for target in [setcar_json, setcar_push]:
        for patch in [
                setcar_pretty_patch,
                monkey_patches.get('pretty_setcar', {}),
        ]:
            utils.apply_patch(target, patch)
    for target in [setcar_json, setcar_push]:
        for patch in [monkey_patches.get('stubborn_setcar', {})]:
            utils.apply_patch(target, patch)
    for key in setcar_push_ignore:
        if key in setcar_push:
            del setcar_push[key]

    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_original
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )

    assert response.status_code == 200, response.text
    resp = response.json()
    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    utils.add_accents(setcar_json)
    normalize = utils.normalize_setcar
    assert normalize(redis_dict) == normalize(setcar_json)
    assert normalize(resp['setcar']) == normalize(setcar_json)
    assert normalize(resp['setcar_push']) == normalize(setcar_push)


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_requirements_rebuild': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_discounted_comfort_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[
        {
            'title': 'true',
            'predicate': {
                'init': {
                    'arg_name': 'category',
                    'arg_type': 'string',
                    'value': 'comfortplus',
                },
                'type': 'eq',
            },
            'value': {
                'enabled': True,
                'comment_tanker_key': 'discounted_comfort.comment.text',
            },
        },
    ],
    default_value={'enabled': False, 'comment_tanker_key': ''},
)
@pytest.mark.parametrize(
    ('category', 'pricing_data_user_meta', 'initial_comment', 'comment'),
    [
        ('econom', None, '', None),
        ('econom', None, 'important user comment', 'important user comment'),
        (
            'econom',
            {'driver_funded_discount_value': 0.1},
            'important user comment',
            'important user comment',
        ),
        (
            'comfortplus',
            {'not_driver_funded_discount_value': 0.1},
            'important user comment',
            'important user comment',
        ),
        (
            'comfortplus',
            {'driver_funded_discount_value': 0.1},
            'important user comment',
            'discounted comfort comment\nimportant user comment',
        ),
        (
            'comfortplus',
            {'driver_funded_discount_value': 0.1},
            '',
            'discounted comfort comment',
        ),
    ],
    ids=[
        'no_comments',
        'only_user_comment',
        'discount_no_match_by_experiment',
        'discount_no_match_by_pricing_transformation',
        'discount_matches_with_user_comment',
        'discount_matches_no_user_comment',
    ],
)
async def test_create_setcar_discounted_comfort(
        taxi_driver_orders_builder,
        mockserver,
        load_json,
        category,
        pricing_data_user_meta,
        initial_comment,
        comment,
        order_proc,
):
    setcar_json = load_json('setcar.json')
    setcar_json['category_v2'] = category
    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json

    order_proc.set_file(load_json, 'order_core_response2.json')
    order_proc.order_proc['fields']['candidates'][0]['tariff_class'] = category
    order_proc.order_proc['fields']['order']['pricing_data']['user'][
        'meta'
    ] = pricing_data_user_meta
    order_proc.order_proc['fields']['order']['request'][
        'comment'
    ] = initial_comment
    order_proc.drop_nones = False

    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )

    assert response.status_code == 200, response.text
    resp = response.json()
    acceptance_items = resp['setcar']['ui']['acceptance_items']
    comments = list(
        filter(
            lambda item: item.get('title') == 'Комментарий', acceptance_items,
        ),
    )
    assert len(comments) == (1 if comment is not None else 0)
    if comment:
        assert comments[0]['subtitle'] == comment


@pytest.mark.config(
    TAXIMETER_SHOW_SURGE_DRIVER_BY_STATUS={
        '__default__': {
            'show_for_statuses': ['assigned', 'driving', 'waiting'],
        },
    },
    TAXIMETER_SHOW_PAYMENT_TYPE_DRIVER_BY_STATUS={
        '__default__': {
            'show_for_statuses': ['waiting', 'transporting', 'complete'],
        },
    },
    TAXIMETER_SHOW_TIME_DELAY={
        '__default__': {
            '__default__': {
                'assigned': 0,
                'complete': 3,
                'driving': 0,
                'transporting': 3,
                'waiting': 0,
            },
        },
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        # TODO Actual config from stable, clarify what it's really needed
        # 'enable_candidate_meta_request': True,
        # 'enable_cargo_multipoints': True,
        # 'enable_cashbox_integration_request': True,
        # 'enable_driver_mode_request': True,
        # 'enable_driver_points_info': True,
        # 'enable_driver_profiles_request': True,
        # 'enable_driver_tags_request': True,
        # 'enable_park_aggregator_redis_source': True,
        # 'enable_price_activity_rebuild': True,
        'enable_requirements_rebuild': True,
        'enable_eulas_request': True,
        # 'enable_setcar_update_patching': True,
        # 'remove_pay_type_for_client_setcar': True,
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': True},
)
@pytest.mark.experiments3()
@pytest.mark.now(MOCKED_NOW)
async def test_create_setcar_without_original_setcar(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        mockserver,
        order_proc,
        params_wo_original_setcar,
):
    @mockserver.json_handler('/candidate-meta/v1/candidate/meta/get')
    def _mock_candidate_meta(request):
        return {'metadata': {}}

    order_proc.order_proc['fields']['order'].pop('dont_call', None)
    order_proc.order_proc['fields']['order']['request']['destinations'].append(
        {
            'country': 'Россия',
            'description': 'Москва, Россия',
            'fullname': 'Россия, Москва, ТРЦ Европейский, Выход №1',
            'geopoint': [37.56530594673405, 55.74553754198694],
            'locality': 'Москва',
            'metrica_method': 'suggest.zero_suggest',
            'object_type': 'другое',
            'short_text': 'ТРЦ Европейский, Выход №1',
            'uris': ['ymapsbm1://geo?ll=37.565%2C55.750&spn=0.001%2C0.001'],
        },
    )

    setcar_json = load_json('setcar.json')
    setcar_push = load_json('setcar_push.json')

    def _update_acceptance_items(setcar):
        # TODO could be removed after show_address=True
        setcar['ui']['acceptance_items'] = setcar['ui']['acceptance_items'][
            :2
        ]  # double_section and adress_from

    # TODO This patch is supposed to inspiring the necessary fear
    # Fields with utils.DELETE_KEY are the most suspucios
    address_from = (
        'Рядом с: Москва, улица 26 Бакинских Комиссаров, 8к3, подъезд 4'
    )
    suffer_patch = {
        'address_from': {
            'ApartmentInfo': '4 подъезд.',
            'City': utils.DELETE_KEY,
            'Description': utils.DELETE_KEY,
            'House': utils.DELETE_KEY,
            'HouseSub1': utils.DELETE_KEY,
            'HouseSub2': utils.DELETE_KEY,
            'Lat': 55.66009198731399,
            'Lon': 37.49133517428459,
            'Porch': '4',
            'Region': '',
            'Street': address_from,
        },
        'address_to': {
            'ArrivalDistance': 20.0,
            'City': utils.DELETE_KEY,
            'Lat': 55.74553754198694,
            'Lon': 37.56530594673405,
            'Order': 2,
            'Region': '',
            'Street': 'Москва, ТРЦ Европейский, Выход №1',
        },
        'cancel_reason_info': utils.DELETE_KEY,
        'car_id': '13e21f1abac24eb78f8ffaf8db872a28',
        'car_franchise': True,
        'car_name': 'Pagani Zonda R',
        'car_number': 'X666XXX666',
        'category_localized': utils.DELETE_KEY,
        'client_geo_sharing': {'track_id': '40d4167a527340caac75e55040bfd49e'},
        'date_create': '2021-08-18T06:00:00.000000Z',
        'date_view': utils.DELETE_KEY,
        'driver_fixed_price': utils.DELETE_KEY,
        'driver_name': 'Иванов Иван Иванович',
        'driver_signal': 'rogue_one',
        'experiments': [
            'direct_assignment',
            'taximeter_complete',
            'open_near_point_a',
            'use_lbs_for_waiting_status',
        ],
        'fio': utils.DELETE_KEY,
        'fixed_price': utils.DELETE_KEY,
        'order_details': utils.DELETE_KEY,
        'phone_show': utils.DELETE_KEY,
        'phones': utils.DELETE_KEY,
        'pickup_distance_type': utils.DELETE_KEY,
        'route_distance': utils.DELETE_KEY,
        'route_points': [
            {
                'ArrivalDistance': 20,
                'Lat': 55.745537,
                'Lon': 37.565306,
                'Order': 1,
                'Region': '',
                'Street': 'Москва, Есенинский бульвар, 3, подъезд 1',
            },
        ],
        'route_time': '2021-08-18T06:23:56.000000Z',
        'requirement_list': [],
        'show_address': False,
        'sms': utils.DELETE_KEY,
        'source': 'service',
        'tariff': utils.DELETE_KEY,
        'tariffs_v2': {
            'driver': {
                'category_prices_id': 'c/168c3ba42916455ca95cbbdd96ea6678',
                'geoareas': ['g/2bab7eff1aa848b681370b2bd83cfbf9'],
            },
            'is_fallback_pricing': False,
            'user': {
                'category_prices_id': 'c/168c3ba42916455ca95cbbdd96ea6678',
                'geoareas': ['g/2bab7eff1aa848b681370b2bd83cfbf9'],
            },
        },
        'taximeter_settings': {'hide_cost_widget': utils.DELETE_KEY},
        'type_color': '#FF7AFF00',
        'type_id': 'abcdef',
        'type_name': 'Яндекс',
        'ui': {
            'acceptance_items': {
                '$patch-0': {
                    'left': {
                        'left_icon': {'tint_color': '#00ca50'},
                        'primary_text_color': '#00945e',
                        'subtitle': '+5',
                    },
                },
                '$patch-1': {'subtitle': address_from},
            },
        },
    }
    push_patch = {
        'address_to': utils.DELETE_KEY,
        'client_geo_sharing': utils.DELETE_KEY,
        'route_points': utils.DELETE_KEY,
    }
    utils.apply_patch(setcar_json, suffer_patch)
    utils.apply_patch(setcar_push, suffer_patch)
    utils.apply_patch(setcar_push, push_patch)
    _update_acceptance_items(setcar_json)
    _update_acceptance_items(setcar_push)

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )

    assert response.status_code == 200, response.text
    resp = response.json()
    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    utils.add_accents(setcar_json)
    normalize = utils.normalize_setcar
    assert normalize(redis_dict) == normalize(setcar_json)
    assert normalize(resp['setcar']) == normalize(setcar_json)
    assert normalize(resp['setcar_push']) == normalize(setcar_push)


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.now(MOCKED_NOW)
@pytest.mark.parametrize(
    'is_driver_check_in, is_order_check_in, modify_check_in_orders_only',
    [
        # not check-in driver cases don't have sence
        (False, False, False),
        (True, False, False),
        (True, False, True),
        (True, True, False),
        (True, True, True),
    ],
)
async def test_pickup_line(
        taxi_driver_orders_builder,
        load_json,
        redis_store,
        mockserver,
        taxi_config,
        is_driver_check_in,
        is_order_check_in,
        modify_check_in_orders_only,
        order_proc,
):
    taxi_config.set_values(
        dict(
            DISPATCH_AIRPORT_ZONES={
                'moscow': {
                    'airport_title_key': 'moscow_airport_key',
                    'enabled': True,
                    'main_area': 'moscow_airport',
                    'notification_area': 'moscow_airport_notification',
                    'old_mode_enabled': False,
                    'tariff_home_zone': 'moscow',
                    'update_interval_sec': 5,
                    'use_queue': True,
                    'waiting_area': 'moscow_airport_waiting',
                    'whitelist_classes': {},
                    'distributive_zone_type': (
                        'check_in' if is_driver_check_in else None
                    ),
                },
            },
            DISPATCH_AIRPORT_PICKUP_LINE_SETCAR_SETTINGS={
                'moscow': {
                    'point_from': [1, 2],
                    'modify_check_in_orders_only': modify_check_in_orders_only,
                },
            },
        ),
    )

    @mockserver.json_handler('/dispatch-airport/v1/active-drivers-queues')
    def _active_drivers_queues(request):
        return {
            'queues': [
                {
                    'tariff': 'econom',
                    'active_drivers': [
                        {
                            'dbid_uuid': 'park1_driver1',
                            'queued': '2019-06-10T13:02:20Z',
                        },
                    ],
                    'driver_needs_predict': 10,
                },
            ],
        }

    order_proc.set_file(load_json, 'order_core_response.json')
    if is_order_check_in:
        order_proc.order_proc['fields']['dispatch_check_in'] = {
            'pickup_line': 'first_line',
        }

    def order_proc_assert(request_fields):
        assert 'dispatch_check_in.pickup_line' in request_fields

    order_proc.set_fields_request_assert = order_proc_assert

    setcar_json = load_json('setcar.json')
    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200
    r_json = response.json()['setcar']
    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)

    set_car_modified = is_driver_check_in and (
        is_order_check_in or not modify_check_in_orders_only
    )
    for struct in (r_json, redis_dict):
        if set_car_modified:
            assert struct['address_from']['Lat'] == 2.0
            assert struct['address_from']['Lon'] == 1.0
        else:
            assert struct['address_from']['Lat'] == 55.688142
            assert struct['address_from']['Lon'] == 37.618561


@pytest.mark.parametrize('is_enabled_experiment', [False, True])
@pytest.mark.parametrize('icon_id', ['taxi', '', 'lavka_yellow'])
async def test_autoconfirmation(
        taxi_driver_orders_builder,
        load_json,
        experiments3,
        is_enabled_experiment,
        icon_id,
):
    experiments3.add_experiment(
        match={
            'predicate': {'type': 'true'},
            'enabled': is_enabled_experiment,
        },
        name='driver_orders_builder_autoconfirmation',
        consumers=['driver-orders-builder/setcar'],
        clauses=[],
        default_value={'icon_id': icon_id},
    )

    setcar_json = load_json('setcar.json')

    request = copy.deepcopy(PARAMS)
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200, response.text()

    if not is_enabled_experiment:
        assert 'auto_confirmation' not in response.json()['setcar']
        return

    assert 'auto_confirmation' in response.json()['setcar']
    assert 'icon_id' in response.json()['setcar']['auto_confirmation']
    assert 'pickup_distance' in response.json()['setcar']['auto_confirmation']
    assert 'pickup_time' in response.json()['setcar']['auto_confirmation']

    if icon_id == '':
        assert (
            response.json()['setcar']['auto_confirmation']['icon_id'] == 'taxi'
        )
    else:
        assert (
            response.json()['setcar']['auto_confirmation']['icon_id']
            == icon_id
        )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_ui_parts_settings',
    consumers=['driver-orders-builder/ui-parts-settings-experiment'],
    merge_values_by=[
        {
            'tag': 'ui_experiments',
            'consumer': 'driver-orders-builder/ui-parts-settings-experiment',
            'merge_method': 'dicts_recursive_merge',
        },
    ],
    default_value={
        'hide_ui_parts': {},
        'show_ui_parts': {},
        'is_corp_no_vat_acceptance_message_enabled': True,
    },
)
@pytest.mark.parametrize(
    """
    is_without_vat_contract,
    has_corp_without_vat_contract,
    no_vat_acceptance_message,
    """,
    [(False, False, False), (True, True, False), (True, False, True)],
    ids=['ordinary_order', 'already_has_contract', 'no_contract'],
)
async def test_no_vat_corp_orders(
        taxi_driver_orders_builder,
        order_proc,
        load_json,
        parks_activation,
        params_wo_original_setcar,
        is_without_vat_contract,
        has_corp_without_vat_contract,
        no_vat_acceptance_message,
):
    parks_activation.has_corp_without_vat_contract_(
        has_corp_without_vat_contract,
    )
    await taxi_driver_orders_builder.invalidate_caches()

    order_proc.set_file(load_json, 'order_core_response1.json')
    if is_without_vat_contract:
        order_proc.order_proc['fields']['order']['request']['corp'] = {
            'client_id': 'corp_client_id',
            'without_vat_contract': True,
        }

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )
    assert response.status_code == 200
    acceptance_items = response.json()['setcar_push']['ui']['acceptance_items']
    assert len(acceptance_items) == (4 if no_vat_acceptance_message else 3)
    if no_vat_acceptance_message:
        assert acceptance_items[2] == {
            'type': 'default',
            'reverse': True,
            'background': {'type': 'balloon'},
            'subtitle': (
                'Корпоративный заказ — согласие с офертой ООО «Яндекс.Такси»'
            ),
        }
