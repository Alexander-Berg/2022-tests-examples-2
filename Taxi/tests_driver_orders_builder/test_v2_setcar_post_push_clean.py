# pylint: disable=too-many-lines

import copy
import json

import pytest

from tests_driver_orders_builder import utils

V2_SETCAR_PUSH_URL = '/v2/setcar_push'

PARAMS = {
    'driver': {
        'park_id': 'park1',
        'driver_profile_id': 'driver1',
        'alias_id': '4d605a2849d747079b5d8c7012830419',
    },
    'order_id': 'test_order_id',
}

ANDROID_EXP_MATCH = {
    'predicate': {
        'type': 'all_of',
        'init': {
            'predicates': [
                {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'taximeter_platform',
                        'arg_type': 'string',
                        'value': 'android',
                    },
                },
            ],
        },
    },
    'enabled': True,
}

FIELDS_TO_CLEAN = [
    'driver_experiments',
    'order_details',
    'phones',
    'requirement_list',
    'route_points',
]

DEFAULT_PLATFORM_CLEANUP_SETTINGS = {
    'create': {
        'optional_fields': FIELDS_TO_CLEAN,
        'required_fields': [
            'AcceptRangeBegin',
            'AcceptRangeEnd',
            'address_from',
            'autocancel',
            'cargo_ref_id',
            'chain',
            'date_create',
            'date_drive',
            'date_booking',
            'date_last_change',
            'date_view',
            'driver_fixed_price',
            'driver_points_info',
            'driver_tariff',
            'experiments',
            'fixed_price',
            'has_online_cashbox',
            'id',
            'provider',
            'source',
            'status',
            'sum',
            'tariff',
            'tariffs_v2',
            'taximeter_settings',
            'ui',
        ],
        'required_experiments': ['direct_assignment'],
    },
}

DEFAULT_CLEAN_VALUE = {
    'push_cleanup_enabled': True,
    'push_cleanup_settings': {'android': DEFAULT_PLATFORM_CLEANUP_SETTINGS},
}

MOCKED_NOW = '2021-08-18T09:00:00+03:00'


@pytest.mark.experiments3(
    match=ANDROID_EXP_MATCH,
    is_config=True,
    name='driver_orders_builder_push_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value=DEFAULT_CLEAN_VALUE,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_driver_profiles_request': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.parametrize('taximeter_platform', ['android', 'ios'])
@pytest.mark.now(MOCKED_NOW)
async def test_push_builder_cleaner(
        mockserver,
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        taximeter_platform,
        setcar_create_params,
):
    setcar_json = load_json('setcar.json')
    setcar_push = load_json('setcar_push.json')
    if taximeter_platform == 'android':
        for field in FIELDS_TO_CLEAN:
            setcar_push.pop(field, None)
        setcar_push['experiments'] = ['direct_assignment']
    else:
        setcar_push['internal']['title'] = 'Новый заказ'
        setcar_json['internal']['title'] = 'Новый заказ'

    setcar_push['notification']['sound'] = 'new_order.wav'
    setcar_json['notification']['sound'] = 'new_order.wav'

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_setcar_data(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'park1_driver1',
                    'data': {
                        'locale': 'ru',
                        'taximeter_version': '9.50',
                        'taximeter_version_type': '',
                        'taximeter_platform': taximeter_platform,
                        'fleet_type': 'taximeter',
                    },
                },
            ],
        }

    response = await taxi_driver_orders_builder.post(**setcar_create_params)

    assert response.status_code == 200, response.text
    assert response.json()['setcar_push'] == setcar_push

    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)

    request = copy.deepcopy(PARAMS)
    responsev2 = await taxi_driver_orders_builder.post(
        V2_SETCAR_PUSH_URL, json=request,
    )
    assert responsev2.json()['setcar_push'] == setcar_push

    utils.add_accents(setcar_json)
    assert redis_dict == setcar_json


@pytest.mark.experiments3(
    match=ANDROID_EXP_MATCH,
    is_config=True,
    name='driver_orders_builder_push_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value=DEFAULT_CLEAN_VALUE,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_driver_profiles_request': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.parametrize('taximeter_platform', ['android', 'ios'])
@pytest.mark.now(MOCKED_NOW)
async def test_push_builder_cleaner_platform_from_profiles(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        mockserver,
        taximeter_platform,
        setcar_create_params,
):
    setcar_json = load_json('setcar.json')
    setcar_push = load_json('setcar_push.json')
    if taximeter_platform == 'android':
        for field in FIELDS_TO_CLEAN:
            setcar_push.pop(field, None)
        setcar_push['experiments'] = ['direct_assignment']
    else:
        setcar_push['internal']['title'] = 'Новый заказ'
        setcar_json['internal']['title'] = 'Новый заказ'

    setcar_push['notification']['sound'] = 'new_order.wav'
    setcar_json['notification']['sound'] = 'new_order.wav'

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_setcar_data(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'park1_driver1',
                    'data': {
                        'locale': 'ru',
                        'taximeter_version': '9.50',
                        'taximeter_version_type': '',
                        'taximeter_platform': taximeter_platform,
                        'fleet_type': 'taximeter',
                    },
                },
            ],
        }

    response = await taxi_driver_orders_builder.post(**setcar_create_params)

    assert response.status_code == 200, response.text
    assert response.json()['setcar_push'] == setcar_push

    request = copy.deepcopy(PARAMS)
    responsev2 = await taxi_driver_orders_builder.post(
        V2_SETCAR_PUSH_URL, json=request,
    )
    assert responsev2.json()['setcar_push'] == setcar_push

    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    utils.add_accents(setcar_json)
    assert redis_dict == setcar_json


TAXIMETER_SETTINGS_FIELDS_TO_CLEAN = ['show_user_cost']

DEFAULT_PLATFORM_CLEANUP_SETTINGS_EXTENDED = {
    'create': {
        'optional_fields': FIELDS_TO_CLEAN,
        'optional_fields_v2': [
            'show_address',
            'sms',
            {
                'field': 'taximeter_settings',
                'optional_fields': TAXIMETER_SETTINGS_FIELDS_TO_CLEAN,
            },
            {
                'field': 'ui',
                'optional_fields': [
                    {
                        'field': 'acceptance_button_params',
                        'optional_fields': [
                            'progress_text_color',
                            'text_color',
                        ],
                    },
                ],
            },
        ],
        'required_fields': [
            'AcceptRangeBegin',
            'AcceptRangeEnd',
            'address_from',
            'autocancel',
            'cargo_ref_id',
            'chain',
            'date_create',
            'date_drive',
            'date_booking',
            'date_last_change',
            'date_view',
            'driver_fixed_price',
            'driver_points_info',
            'driver_tariff',
            'experiments',
            'fixed_price',
            'has_online_cashbox',
            'id',
            'provider',
            'source',
            'status',
            'sum',
            'tariff',
            'tariffs_v2',
        ],
        'required_experiments': ['direct_assignment'],
    },
}

DEFAULT_CLEAN_VALUE_EXTENDED = {
    'push_cleanup_enabled': True,
    'push_cleanup_settings': {
        'android': DEFAULT_PLATFORM_CLEANUP_SETTINGS_EXTENDED,
    },
}


@pytest.mark.experiments3(
    match=ANDROID_EXP_MATCH,
    is_config=True,
    name='driver_orders_builder_push_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value=DEFAULT_CLEAN_VALUE_EXTENDED,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_driver_profiles_request': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.parametrize('taximeter_platform', ['android', 'ios'])
@pytest.mark.now(MOCKED_NOW)
async def test_push_builder_cleaner_extended(
        mockserver,
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        taximeter_platform,
        setcar_create_params,
):
    setcar_json = load_json('setcar.json')
    setcar_push = load_json('setcar_push.json')
    if taximeter_platform == 'android':
        for field in FIELDS_TO_CLEAN:
            setcar_push.pop(field, None)
        setcar_push['experiments'] = ['direct_assignment']
        for field in TAXIMETER_SETTINGS_FIELDS_TO_CLEAN:
            setcar_push['taximeter_settings'].pop(field, None)
        setcar_push['ui']['acceptance_button_params'].pop(
            'progress_text_color', None,
        )
        setcar_push['ui']['acceptance_button_params'].pop('text_color', None)
        setcar_push.pop('sms', None)
        setcar_push.pop('show_address', None)
    else:
        setcar_push['internal']['title'] = 'Новый заказ'
        setcar_json['internal']['title'] = 'Новый заказ'

    setcar_push['notification']['sound'] = 'new_order.wav'
    setcar_json['notification']['sound'] = 'new_order.wav'

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_setcar_data(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'park1_driver1',
                    'data': {
                        'locale': 'ru',
                        'taximeter_version': '9.50',
                        'taximeter_version_type': '',
                        'taximeter_platform': taximeter_platform,
                        'fleet_type': 'taximeter',
                    },
                },
            ],
        }

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text
    assert response.json()['setcar_push'] == setcar_push

    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)

    request = copy.deepcopy(PARAMS)
    responsev2 = await taxi_driver_orders_builder.post(
        V2_SETCAR_PUSH_URL, json=request,
    )
    assert responsev2.json()['setcar_push'] == setcar_push

    utils.add_accents(setcar_json)
    assert redis_dict == setcar_json
