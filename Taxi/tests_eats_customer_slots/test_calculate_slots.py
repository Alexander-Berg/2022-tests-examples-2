# pylint: disable=too-many-lines

import datetime

import pytest

from tests_eats_customer_slots import utils


@pytest.mark.now('2021-03-05T12:00:00+03:00')
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.experiments3(
    is_config=True,
    name='eats_customer_slots_slots_enabled',
    consumers=['eats-customer-slots/calculate-slots'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'empty_phone_id',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'personal_phone_id',
                    'arg_type': 'string',
                    'value': '',
                },
            },
            'value': {'enabled': False, 'is_asap_enabled': True},
        },
        {
            'title': 'personal_phone_id_qwerty',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'personal_phone_id',
                    'arg_type': 'string',
                    'value': 'qwerty',
                },
            },
            'value': {'enabled': True, 'is_asap_enabled': True},
        },
    ],
    default_value={'enabled': True, 'is_asap_enabled': True},
)
@utils.daily_slots_config()
@utils.settings_config(asap_disable_threshold=1800)
@pytest.mark.parametrize(
    'headers, slots_available',
    [
        [{'X-Eats-User': 'user_id=user_1,personal_phone_id=qwerty'}, True],
        [{'X-Eats-User': 'user_id=user_1'}, False],
        [{'X-Eats-User': 'personal_phone_id=qwerty'}, True],
    ],
)
async def test_calculate_slots_personal_phone_id(
        taxi_eats_customer_slots, headers, slots_available,
):
    order = utils.make_order(estimated_picking_time=200)

    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', headers=headers, json=order,
    )
    assert response.status == 200
    response_body = response.json()
    assert response_body['available_asap']
    assert bool(response_body['available_slots']) == slots_available


@pytest.mark.now('2021-03-05T12:00:00+03:00')
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.experiments3(
    is_config=True,
    name='eats_customer_slots_slots_enabled',
    consumers=['eats-customer-slots/calculate-slots'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'empty_device_id',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'device_id',
                    'arg_type': 'string',
                    'value': '',
                },
            },
            'value': {'enabled': False, 'is_asap_enabled': True},
        },
        {
            'title': 'device_id_qwerty',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'device_id',
                    'arg_type': 'string',
                    'value': 'qwerty',
                },
            },
            'value': {'enabled': True, 'is_asap_enabled': True},
        },
    ],
    default_value={'enabled': True, 'is_asap_enabled': True},
)
@utils.daily_slots_config()
@utils.settings_config(asap_disable_threshold=1800)
@pytest.mark.parametrize(
    'headers, slots_available',
    [
        [{'X-Eats-User': 'user_id=user_1', 'X-Device-Id': 'qwerty'}, True],
        [{'X-Eats-User': 'user_id=user_1', 'X-Device-Id': ''}, False],
        [{'X-Eats-User': 'user_id=user_1'}, False],
        [{'X-Device-Id': 'qwerty'}, True],
    ],
)
async def test_calculate_slots_device_id(
        taxi_eats_customer_slots,
        mock_calculate_load,
        headers,
        slots_available,
):
    order = utils.make_order(estimated_picking_time=200)

    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', headers=headers, json=order,
    )
    assert response.status == 200
    response_body = response.json()
    assert response_body['available_asap']
    assert bool(response_body['available_slots']) == slots_available


@pytest.mark.now('2021-03-05T12:00:00+03:00')
@pytest.mark.experiments3(
    is_config=True,
    name='eats_customer_slots_slots_enabled',
    consumers=['eats-customer-slots/calculate-slots'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'user_id_qwerty',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'user_id',
                    'arg_type': 'string',
                    'value': 'qwerty',
                },
            },
            'value': {'enabled': True, 'is_asap_enabled': True},
        },
    ],
    default_value={'enabled': False, 'is_asap_enabled': True},
)
@utils.daily_slots_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@utils.settings_config(asap_disable_threshold=1800)
@pytest.mark.parametrize(
    'headers, slots_available',
    [
        [{}, False],
        [{'X-Eats-User': 'personal_phone_id=qwerty'}, False],
        [{'X-Eats-User': f'user_id=qwerty'}, True],
    ],
)
async def test_calculate_slots_user_id(
        taxi_eats_customer_slots,
        mock_calculate_load,
        headers,
        slots_available,
):
    order = utils.make_order(estimated_picking_time=200)

    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', headers=headers, json=order,
    )
    assert response.status == 200
    response_body = response.json()
    assert response_body['available_asap']
    assert bool(response_body['available_slots']) == slots_available


def make_param_free_pickers(
        expected_slots,
        expected_asap_availability,
        order_eta=200,
        order_estimate_response=None,
        delivery_time=None,
        estimated_delivery_timepoint_shift=0,
        time_zone='Europe/Moscow',
):
    if order_estimate_response is None:
        order_estimate_response = {'json': {'eta_seconds': 200}}
    return [
        order_eta,
        order_estimate_response,
        delivery_time,
        estimated_delivery_timepoint_shift,
        time_zone,
        expected_slots,
        expected_asap_availability,
    ]


@utils.slots_enabled()
@utils.daily_slots_config()
@pytest.mark.now('2021-03-05T12:00:00+03:00')
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.parametrize(
    'order_eta, order_estimate_response, delivery_time, '
    'estimated_delivery_timepoint_shift, '
    'time_zone, expected_slots, expected_asap_availability',
    [
        make_param_free_pickers(
            time_zone='Etc/GMT+10',
            expected_slots=[
                {
                    'start': '2021-03-05T10:00:00-10:00',
                    'end': '2021-03-05T11:00:00-10:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T10:00:00-10:00'
                    ),
                    'select_by_default': True,
                },
                {
                    'start': '2021-03-05T11:00:00-10:00',
                    'end': '2021-03-05T12:00:00-10:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T11:00:00-10:00'
                    ),
                },
            ],
            expected_asap_availability=False,  # place is closed
        ),
        make_param_free_pickers(
            time_zone='UTC',
            expected_slots=[
                {
                    'start': '2021-03-05T10:00:00+00:00',
                    'end': '2021-03-05T11:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T10:00:00+00:00'
                    ),
                    'select_by_default': True,
                },
                {
                    'start': '2021-03-05T11:00:00+00:00',
                    'end': '2021-03-05T12:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T11:00:00+00:00'
                    ),
                },
                {
                    'start': '2021-03-05T12:00:00+00:00',
                    'end': '2021-03-05T13:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T12:00:00+00:00'
                    ),
                },
                {
                    'start': '2021-03-05T13:00:00+00:00',
                    'end': '2021-03-05T14:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T13:00:00+00:00'
                    ),
                },
                {
                    'start': '2021-03-05T14:00:00+00:00',
                    'end': '2021-03-05T15:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T14:00:00+00:00'
                    ),
                },
                {
                    'start': '2021-03-05T15:00:00+00:00',
                    'end': '2021-03-05T16:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T15:00:00+00:00'
                    ),
                },
                {
                    'start': '2021-03-05T16:00:00+00:00',
                    'end': '2021-03-05T17:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T16:00:00+00:00'
                    ),
                },
                {
                    'start': '2021-03-05T17:00:00+00:00',
                    'end': '2021-03-05T18:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T17:00:00+00:00'
                    ),
                },
                {
                    'start': '2021-03-05T18:00:00+00:00',
                    'end': '2021-03-05T19:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T18:00:00+00:00'
                    ),
                },
                {
                    'start': '2021-03-05T19:00:00+00:00',
                    'end': '2021-03-05T20:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T19:00:00+00:00'
                    ),
                },
                {
                    'start': '2021-03-06T10:00:00+00:00',
                    'end': '2021-03-06T11:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T10:00:00+00:00'
                    ),
                },
                {
                    'start': '2021-03-06T11:00:00+00:00',
                    'end': '2021-03-06T12:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T11:00:00+00:00'
                    ),
                },
            ],
            expected_asap_availability=False,  # place is closed
        ),
        make_param_free_pickers(
            expected_slots=[
                {
                    'start': '2021-03-05T13:00:00+03:00',
                    'end': '2021-03-05T14:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T13:00:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-05T14:00:00+03:00',
                    'end': '2021-03-05T15:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T14:00:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-05T15:00:00+03:00',
                    'end': '2021-03-05T16:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T15:00:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-05T16:00:00+03:00',
                    'end': '2021-03-05T17:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T16:00:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-05T17:00:00+03:00',
                    'end': '2021-03-05T18:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T17:00:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-05T18:00:00+03:00',
                    'end': '2021-03-05T19:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T18:00:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-05T19:00:00+03:00',
                    'end': '2021-03-05T20:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T19:00:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-06T10:00:00+03:00',
                    'end': '2021-03-06T11:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T10:00:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-06T11:00:00+03:00',
                    'end': '2021-03-06T12:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T11:00:00+03:00'
                    ),
                },
            ],
            expected_asap_availability=True,
        ),
        make_param_free_pickers(
            order_eta=1801,
            expected_slots=[
                {
                    'start': '2021-03-05T13:00:00+03:00',
                    'end': '2021-03-05T14:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T13:00:00+03:00'
                    ),
                    'select_by_default': True,
                },
                {
                    'start': '2021-03-05T14:00:00+03:00',
                    'end': '2021-03-05T15:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T14:00:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-05T15:00:00+03:00',
                    'end': '2021-03-05T16:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T15:00:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-05T16:00:00+03:00',
                    'end': '2021-03-05T17:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T16:00:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-05T17:00:00+03:00',
                    'end': '2021-03-05T18:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T17:00:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-05T18:00:00+03:00',
                    'end': '2021-03-05T19:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T18:00:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-05T19:00:00+03:00',
                    'end': '2021-03-05T20:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T19:00:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-06T10:00:00+03:00',
                    'end': '2021-03-06T11:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T10:00:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-06T11:00:00+03:00',
                    'end': '2021-03-06T12:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T11:00:00+03:00'
                    ),
                },
            ],
            expected_asap_availability=False,  # > asap_disable_threshold
        ),
        make_param_free_pickers(
            order_eta=3600 * 6,
            expected_slots=[
                {
                    'start': '2021-03-05T19:00:00+03:00',
                    'end': '2021-03-05T20:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T19:00:00+03:00'
                    ),
                    'select_by_default': True,
                },
                {
                    'start': '2021-03-06T10:00:00+03:00',
                    'end': '2021-03-06T11:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T10:00:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-06T11:00:00+03:00',
                    'end': '2021-03-06T12:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T11:00:00+03:00'
                    ),
                },
            ],
            expected_asap_availability=False,  # > asap_disable_threshold
        ),
        make_param_free_pickers(
            time_zone='Asia/Vladivostok',
            expected_slots=[
                {
                    'start': '2021-03-06T10:00:00+10:00',
                    'end': '2021-03-06T11:00:00+10:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T10:00:00+10:00'
                    ),
                },
                {
                    'start': '2021-03-06T11:00:00+10:00',
                    'end': '2021-03-06T12:00:00+10:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T11:00:00+10:00'
                    ),
                },
            ],
            expected_asap_availability=True,
        ),
        make_param_free_pickers(
            time_zone='Asia/Kamchatka',
            expected_slots=[
                {
                    'start': '2021-03-06T10:00:00+12:00',
                    'end': '2021-03-06T11:00:00+12:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T10:00:00+12:00'
                    ),
                    'select_by_default': True,
                },
                {
                    'start': '2021-03-06T11:00:00+12:00',
                    'end': '2021-03-06T12:00:00+12:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T11:00:00+12:00'
                    ),
                },
            ],
            expected_asap_availability=False,  # place is closed
        ),
        make_param_free_pickers(
            time_zone='Etc/GMT-14',
            expected_slots=[
                {
                    'start': '2021-03-06T10:00:00+14:00',
                    'end': '2021-03-06T11:00:00+14:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T10:00:00+14:00'
                    ),
                    'select_by_default': True,
                },
                {
                    'start': '2021-03-06T11:00:00+14:00',
                    'end': '2021-03-06T12:00:00+14:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T11:00:00+14:00'
                    ),
                },
            ],
            expected_asap_availability=False,  # place is closed
        ),
        make_param_free_pickers(
            delivery_time='2021-03-05T18:30:00+03:00',
            expected_slots=[
                {
                    'start': '2021-03-05T19:00:00+03:00',
                    'end': '2021-03-05T20:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T19:00:00+03:00'
                    ),
                    'select_by_default': True,
                },
                {
                    'start': '2021-03-06T10:00:00+03:00',
                    'end': '2021-03-06T11:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T10:00:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-06T11:00:00+03:00',
                    'end': '2021-03-06T12:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T11:00:00+03:00'
                    ),
                },
            ],
            # pre-order (> asap_delivery_time_max_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            time_zone='UTC',
            delivery_time='2021-03-06T09:00:00+00:00',
            expected_slots=[
                {
                    'start': '2021-03-06T10:00:00+00:00',
                    'end': '2021-03-06T11:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T10:00:00+00:00'
                    ),
                    'select_by_default': True,
                },
                {
                    'start': '2021-03-06T11:00:00+00:00',
                    'end': '2021-03-06T12:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T11:00:00+00:00'
                    ),
                },
            ],
            # pre-order (> asap_delivery_time_max_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            time_zone='UTC',
            delivery_time='2021-03-06T10:30:00+00:00',
            expected_slots=[
                {
                    'start': '2021-03-06T11:00:00+00:00',
                    'end': '2021-03-06T12:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T11:00:00+00:00'
                    ),
                    'select_by_default': True,
                },
            ],
            # pre-order (> asap_delivery_time_max_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            time_zone='UTC',
            delivery_time='2021-03-06T10:00:00+00:00',
            expected_slots=[
                {
                    'start': '2021-03-06T10:00:00+00:00',
                    'end': '2021-03-06T11:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T10:00:00+00:00'
                    ),
                    'select_by_default': True,
                },
                {
                    'start': '2021-03-06T11:00:00+00:00',
                    'end': '2021-03-06T12:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T11:00:00+00:00'
                    ),
                },
            ],
            # pre-order (> asap_delivery_time_max_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            time_zone='UTC',
            delivery_time='2021-03-06T07:00:00+00:00',
            expected_slots=[
                {
                    'start': '2021-03-06T10:00:00+00:00',
                    'end': '2021-03-06T11:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T10:00:00+00:00'
                    ),
                    'select_by_default': True,
                },
                {
                    'start': '2021-03-06T11:00:00+00:00',
                    'end': '2021-03-06T12:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T11:00:00+00:00'
                    ),
                },
            ],
            # pre-order (> asap_delivery_time_max_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            time_zone='UTC',
            delivery_time='2021-03-06T15:00:00+00:00',
            expected_slots=[],
            # pre-order (> asap_delivery_time_max_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            delivery_time='2021-03-05T18:15:00+03:00',
            estimated_delivery_timepoint_shift=600,
            expected_slots=[
                {
                    'start': '2021-03-05T19:00:00+03:00',
                    'end': '2021-03-05T20:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T19:10:00+03:00'
                    ),
                    'select_by_default': True,
                },
                {
                    'start': '2021-03-06T10:00:00+03:00',
                    'end': '2021-03-06T11:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T10:10:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-06T11:00:00+03:00',
                    'end': '2021-03-06T12:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T11:10:00+03:00'
                    ),
                },
            ],
            # pre-order (> asap_delivery_time_max_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            delivery_time='2021-03-05T18:15:00+03:00',
            estimated_delivery_timepoint_shift=1800,
            expected_slots=[
                {
                    'start': '2021-03-05T18:00:00+03:00',
                    'end': '2021-03-05T19:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T18:30:00+03:00'
                    ),
                    'select_by_default': True,
                },
                {
                    'start': '2021-03-05T19:00:00+03:00',
                    'end': '2021-03-05T20:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-05T19:30:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-06T10:00:00+03:00',
                    'end': '2021-03-06T11:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T10:30:00+03:00'
                    ),
                },
                {
                    'start': '2021-03-06T11:00:00+03:00',
                    'end': '2021-03-06T12:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T11:30:00+03:00'
                    ),
                },
            ],
            # pre-order (> asap_delivery_time_max_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            time_zone='UTC',
            delivery_time='2021-03-06T11:15:00+00:00',
            estimated_delivery_timepoint_shift=600,
            expected_slots=[],
            expected_asap_availability=False,  # place is closed
        ),
        make_param_free_pickers(
            order_eta=2701,
            time_zone='UTC',
            delivery_time='2021-03-06T11:15:00+00:00',
            estimated_delivery_timepoint_shift=600,
            expected_slots=[],
            expected_asap_availability=False,  # place is closed
        ),
        make_param_free_pickers(
            time_zone='UTC',
            delivery_time='2021-03-06T11:15:00+00:00',
            estimated_delivery_timepoint_shift=1800,
            expected_slots=[
                {
                    'start': '2021-03-06T11:00:00+00:00',
                    'end': '2021-03-06T12:00:00+00:00',
                    'estimated_delivery_timepoint': (
                        '2021-03-06T11:30:00+00:00'
                    ),
                    'select_by_default': True,
                },
            ],
            expected_asap_availability=False,  # place is closed
        ),
    ],
)
async def test_calculate_slots_free_pickers(
        taxi_eats_customer_slots,
        experiments3,
        mockserver,
        mock_calculate_load,
        order_eta,
        delivery_time,
        estimated_delivery_timepoint_shift,
        order_estimate_response,
        time_zone,
        now,
        expected_slots,
        expected_asap_availability,
):
    experiments3.add_experiment3_from_marker(
        utils.settings_config(
            estimated_delivery_timepoint_shift, asap_disable_threshold=1800,
        ),
        None,
    )
    brand_id = 1
    now = utils.localize(now, time_zone)
    mock_calculate_load.response['json']['places_load_info'][0].update(
        brand_id=brand_id,
        time_zone=time_zone,
        working_intervals=utils.make_working_intervals(
            now,
            [
                {
                    'day_from': 0,
                    'time_from': '10:00',
                    'day_to': 0,
                    'time_to': '21:00',
                },
                {
                    'day_from': 1,
                    'time_from': '10:00',
                    'day_to': 1,
                    # 12:00 здесь для уменьшения размера expected_slots
                    'time_to': '12:00',
                },
            ],
        ),
        shop_picking_type='our_picking',
    )

    @mockserver.json_handler(
        '/eats-picking-time-estimator/api/v1/order/estimate',
    )
    async def mock_order_estimate(request):
        return mockserver.make_response(**order_estimate_response)

    order = utils.make_order(
        estimated_picking_time=order_eta,
        brand_id=str(brand_id),
        delivery_time=delivery_time,
    )
    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert mock_order_estimate.times_called == int(order_eta is None)
    response_body = response.json()
    slots = response_body['available_slots']
    assert slots == expected_slots
    assert response_body['available_asap'] == expected_asap_availability


@utils.slots_enabled()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@utils.daily_slots_config()
@utils.settings_config(asap_disable_threshold=300)
@pytest.mark.now('2021-03-05T12:00:00+03:00')
@pytest.mark.parametrize(
    'order_eta, order_estimate_response, time_zone, expected_asap',
    [
        # place is closed
        [200, {'json': {'eta_seconds': 200}}, 'Etc/GMT+10', False],
        # place is closed
        [200, {'json': {'eta_seconds': 200}}, 'UTC', False],
        # > asap_disable_threshold
        [301, {'json': {'eta_seconds': 200}}, 'Europe/Moscow', False],
        [300, {'json': {'eta_seconds': 300}}, 'Europe/Moscow', True],
        [200, {'json': {'eta_seconds': 200}}, 'Europe/Moscow', True],
        # > asap_disable_threshold
        [301, {'json': {'eta_seconds': 200}}, 'Asia/Vladivostok', False],
        [300, {'json': {'eta_seconds': 300}}, 'Asia/Vladivostok', True],
        [200, {'json': {'eta_seconds': 200}}, 'Asia/Vladivostok', True],
        # place is closed
        [None, {'json': {'eta_seconds': 200}}, 'Asia/Kamchatka', False],
        # place is closed
        [None, {'json': {'eta_seconds': 200}}, 'Etc/GMT-14', False],
    ],
)
async def test_calculate_slots_free_pickers_midnight_slot(
        taxi_eats_customer_slots,
        mockserver,
        order_eta,
        order_estimate_response,
        mock_calculate_load,
        time_zone,
        now,
        expected_asap,
):
    brand_id = utils.MIDNIGHT_BRAND
    now = utils.localize(now, time_zone)
    mock_calculate_load.response['json']['places_load_info'][0].update(
        brand_id=brand_id,
        time_zone=time_zone,
        working_intervals=utils.make_working_intervals(
            now,
            [
                {
                    'day_from': 0,
                    'time_from': '10:00',
                    'day_to': 0,
                    'time_to': '21:00',
                },
                {
                    'day_from': 1,
                    'time_from': '10:00',
                    'day_to': 1,
                    'time_to': '21:00',
                },
            ],
        ),
        shop_picking_type='our_picking',
    )

    @mockserver.json_handler(
        '/eats-picking-time-estimator/api/v1/order/estimate',
    )
    async def mock_order_estimate(request):
        return mockserver.make_response(**order_estimate_response)

    order = utils.make_order(
        estimated_picking_time=order_eta,
        brand_id=str(brand_id),
        time_to_customer=60,
    )
    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert mock_order_estimate.times_called == int(order_eta is None)
    response_body = response.json()
    assert response_body['available_slots'] == []
    assert response_body['available_asap'] == expected_asap


@utils.slots_enabled()
@utils.daily_slots_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.now('2021-03-05T12:00:00+03:00')
@pytest.mark.parametrize(
    'time_to_customer, estimated_waiting_time, '
    'asap_by_picker_without_delivery_time',
    [
        [100, 4000, False],
        [4000, 100, False],
        [100, 9, True],
        [100, 10, True],
        [100, 11, False],
    ],
)
@pytest.mark.parametrize(
    'total_pickers_count, asap_by_total_pickers', [(0, False), (2, True)],
)
@pytest.mark.parametrize(
    'order_eta, order_estimate_response, eta_seconds',
    [
        [100, None, 100],
        [4000, None, 4000],
        pytest.param(
            None,
            {'status': 500},
            100,
            marks=[
                pytest.mark.config(
                    EATS_PICKING_TIME_ESTIMATOR_CLIENT_QOS={
                        '__default__': {'attempts': 1, 'timeout-ms': 100},
                    },
                ),
                utils.eta_fallback_config(100),
            ],
        ),
        pytest.param(
            None,
            {'status': 500},
            4000,
            marks=[
                pytest.mark.config(
                    EATS_PICKING_TIME_ESTIMATOR_CLIENT_QOS={
                        '__default__': {'attempts': 1, 'timeout-ms': 100},
                    },
                ),
                utils.eta_fallback_config(4000),
            ],
        ),
        [None, {'json': {'eta_seconds': 100}}, 100],
        [None, {'json': {'eta_seconds': 4000}}, 4000],
    ],
)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.parametrize(
    'time_zone, delivery_time, asap_by_place',
    [
        ('Etc/GMT+10', None, False),
        ('UTC', None, False),
        ('Europe/Moscow', None, True),
        ('Asia/Vladivostok', None, True),
        ('Asia/Kamchatka', None, False),
        ('Etc/GMT-14', None, False),
        ('Europe/Moscow', '2021-03-05T09:00:00+03:00', True),
        ('Europe/Moscow', '2021-03-05T12:01:00+03:00', True),
        ('Europe/Moscow', '2021-03-05T12:06:00+03:00', False),
        ('Europe/Moscow', '2021-03-05T22:00:00+03:00', False),
    ],
)
async def test_calculate_slots_no_free_pickers(
        taxi_eats_customer_slots,
        mockserver,
        mock_calculate_load,
        make_expected_slots,
        time_to_customer,
        estimated_waiting_time,
        asap_by_picker_without_delivery_time,
        order_eta,
        order_estimate_response,
        eta_seconds,
        total_pickers_count,
        asap_by_total_pickers,
        time_zone,
        delivery_time,
        asap_by_place,
        now,
        experiments3,
):
    asap_disable_threshold = 110
    experiments3.add_experiment3_from_marker(
        utils.settings_config(asap_disable_threshold=asap_disable_threshold),
        None,
    )
    brand_id = 1
    now = utils.localize(now, time_zone)
    working_intervals = utils.make_working_intervals(
        now,
        [
            {
                'day_from': 0,
                'time_from': '10:00',
                'day_to': 0,
                'time_to': '21:00',
            },
            {
                'day_from': 1,
                'time_from': '10:00',
                'day_to': 1,
                'time_to': '21:00',
            },
        ],
    )

    @mockserver.json_handler(
        '/eats-picking-time-estimator/api/v1/order/estimate',
    )
    async def mock_order_estimate(request):
        return mockserver.make_response(**order_estimate_response)

    mock_calculate_load.response['json']['places_load_info'][0].update(
        brand_id=brand_id,
        time_zone=time_zone,
        free_pickers_count=0,
        total_pickers_count=total_pickers_count,
        estimated_waiting_time=estimated_waiting_time,
        working_intervals=working_intervals,
        shop_picking_type='our_picking',
    )

    order = utils.make_order(
        time_to_customer=time_to_customer,
        estimated_picking_time=order_eta,
        brand_id=str(brand_id),
        delivery_time=delivery_time,
    )
    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert mock_order_estimate.times_called == int(order_eta is None)
    response_body = response.json()
    estimated_picking_time = now + datetime.timedelta(
        seconds=estimated_waiting_time + eta_seconds,
    )
    estimated_completion_time = estimated_picking_time + datetime.timedelta(
        seconds=time_to_customer,
    )

    asap_by_disable_threshold = estimated_picking_time <= (
        now + datetime.timedelta(seconds=asap_disable_threshold)
    )

    asap_expected = (
        asap_by_disable_threshold
        and asap_by_picker_without_delivery_time
        and asap_by_total_pickers
        and asap_by_place
    )

    if delivery_time:
        delivery_time = datetime.datetime.fromisoformat(delivery_time)
        estimated_completion_time = max(
            estimated_completion_time, delivery_time,
        )

    assert response_body['available_asap'] == asap_expected
    slots = response_body['available_slots']
    expected_slots = make_expected_slots(
        estimated_completion_time, brand_id, working_intervals,
    )
    if not response_body['available_asap']:
        expected_slots[0]['select_by_default'] = True
    assert slots == expected_slots


@utils.slots_enabled()
@utils.daily_slots_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@utils.settings_config()
@pytest.mark.now('2021-03-05T12:00:00+03:00')
async def test_calculate_slots_no_day_0(
        taxi_eats_customer_slots, mock_calculate_load,
):
    mock_calculate_load.response['json']['places_load_info'][0].update(
        brand_id=utils.NEXT_DAY_BRAND,
    )

    order = utils.make_order(brand_id=str(utils.NEXT_DAY_BRAND))
    await taxi_eats_customer_slots.invalidate_caches()
    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert response.json()['available_asap']
    assert response.json()['available_slots']


@utils.slots_enabled()
@utils.daily_slots_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@utils.settings_config()
async def test_calculate_slots_place_disabled(
        taxi_eats_customer_slots, mock_calculate_load,
):
    mock_calculate_load.response['json']['places_load_info'][0].update(
        enabled=False,
    )

    order = utils.make_order()
    await taxi_eats_customer_slots.invalidate_caches()
    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert response.json() == {'available_asap': False, 'available_slots': []}


@utils.slots_enabled()
@utils.settings_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.parametrize(
    '', [pytest.param(), pytest.param(marks=utils.daily_slots_config())],
)
async def test_calculate_slots_empty_slots(
        taxi_eats_customer_slots, mock_calculate_load,
):
    mock_calculate_load.response['json']['places_load_info'][0].update(
        brand_id=utils.EMPTY_BRAND,
    )
    order = utils.make_order()
    await taxi_eats_customer_slots.invalidate_caches()
    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert response.json() == {'available_asap': True, 'available_slots': []}


@utils.slots_enabled()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@utils.settings_config()
@pytest.mark.parametrize(
    'calculate_load_response',
    [{'status': 500}, {'json': {'places_load_info': []}}],
    ids=['calculate_load_error', 'empty_places_load_info'],
)
async def test_calculate_slots_empty_cache(
        taxi_eats_customer_slots, mock_calculate_load, calculate_load_response,
):
    mock_calculate_load.response = calculate_load_response
    order = utils.make_order()
    await taxi_eats_customer_slots.invalidate_caches()
    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert response.json() == {'available_asap': True, 'available_slots': []}


@utils.daily_slots_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@utils.settings_config()
@pytest.mark.now('2021-03-05T12:00:00+03:00')
async def test_calculate_slots_slots_disabled(taxi_eats_customer_slots):
    order = utils.make_order()
    await taxi_eats_customer_slots.invalidate_caches()
    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert response.json() == {'available_asap': False, 'available_slots': []}


@utils.slots_enabled()
@utils.daily_slots_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@utils.settings_config(asap_disable_threshold=1800)
@pytest.mark.now('2021-04-06T08:00:00+03:00')
@pytest.mark.parametrize(
    'total_pickers, free_pickers, estimated_waiting_time, expected_asap',
    [
        # Все слоты отфильтрованы, нет пикеров вообще - asap недоступен
        (0, 0, 50, False),
        # Все слоты отфильтрованы, есть свободные пикеры - asap доступен
        (1, 1, 50, True),
        # Все слоты отфильтрованы, нет свободных пикеров,
        # estimated_waiting_time меньше, чем asap_disable_threshold -
        # asap доступен
        (1, 0, 50, True),
        # Все слоты отфильтрованы, нет свободных пикеров,
        # estimated_waiting_time + estimated_picking_time больше,
        # чем asap_disable_threshold - asap не доступен
        (1, 0, 1790, False),
    ],
)
async def test_calculate_slots_no_matched_slots(
        taxi_eats_customer_slots,
        mock_calculate_load,
        now,
        total_pickers,
        free_pickers,
        estimated_waiting_time,
        expected_asap,
):
    now = utils.localize(now, 'Europe/Moscow')
    working_intervals = utils.make_working_intervals(
        now,
        [
            {
                'day_from': 0,
                'time_from': '08:00',
                'day_to': 0,
                'time_to': '11:30',
            },
        ],
    )
    mock_calculate_load.response['json']['places_load_info'][0].update(
        brand_id=utils.MIDNIGHT_BRAND,
        free_pickers_count=free_pickers,
        total_pickers_count=total_pickers,
        estimated_waiting_time=estimated_waiting_time,
        working_intervals=working_intervals,
        shop_picking_type='our_picking',
    )
    order = utils.make_order(
        estimated_picking_time=20, brand_id=str(utils.MIDNIGHT_BRAND),
    )

    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert response.json()['available_asap'] == expected_asap
    assert not response.json()['available_slots']


@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config(asap_disable_threshold=1700)
@pytest.mark.now('2021-07-14T11:00:00+03:00')
@pytest.mark.parametrize(
    'total_pickers, free_pickers, estimated_waiting_time,'
    'estimated_picking_time, expected_asap',
    [
        # Нет пикеров вообще - нет asap
        (0, 0, 1200, 500, False),
        # Нет свободных пикеров и ждать слишком долго - asap недоступен
        (2, 0, 1200, 550, False),
        # Нет свободных сборщиков, но скоро будут, и заказ успеем собрать
        # до закрытия - asap доступен
        (2, 0, 600, 120, True),
        # Нет свободных сборщиков, но скоро будут, и заказ успеем собрать
        # до закрытия, но не успеем до asap_disable_threshold -
        # asap недоступен
        (2, 0, 600, 1150, False),
        # Нет свободных сборщиков, но скоро будут, и заказ до закрытия
        # не успеем собрать - asap недоступен
        (2, 0, 600, 1300, False),
        # Есть свободные сборщики, и заказ успеем собрать до закрытия -
        # asap доступен
        (2, 2, 600, 120, True),
        # Есть свободные сборщики, и заказ успеем собрать до закрытия,
        # но не успеем до asap_disable_threshold -
        # asap недоступен
        (2, 2, 600, 1750, False),
        # Есть свободные сборщики, но заказ до закрытия не успеем собрать -
        # asap недоступен
        (2, 2, 600, 2000, False),
    ],
)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_calculate_slots_asap_before_closing(
        taxi_eats_customer_slots,
        mock_calculate_load,
        now,
        total_pickers,
        free_pickers,
        estimated_waiting_time,
        estimated_picking_time,
        expected_asap,
):
    now = utils.localize(now, 'Europe/Moscow')
    working_intervals = utils.make_working_intervals(
        now,
        [
            {
                'day_from': 0,
                'time_from': '08:00',
                'day_to': 0,
                'time_to': '11:30',
            },
        ],
    )
    mock_calculate_load.response['json']['places_load_info'][0].update(
        free_pickers_count=free_pickers,
        total_pickers_count=total_pickers,
        estimated_waiting_time=estimated_waiting_time,
        working_intervals=working_intervals,
        shop_picking_type='our_picking',
    )
    order = utils.make_order(estimated_picking_time=estimated_picking_time)

    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert response.json()['available_asap'] == expected_asap


EXPECTED_ONE_SLOT = [
    {
        'end': '2021-07-15T15:00:00+03:00',
        'estimated_delivery_timepoint': '2021-07-15T14:30:00+03:00',
        'start': '2021-07-15T14:00:00+03:00',
        'select_by_default': True,
    },
]

EXPECTED_TWO_SLOTS = [
    {
        'end': '2021-07-15T14:00:00+03:00',
        'estimated_delivery_timepoint': '2021-07-15T13:30:00+03:00',
        'start': '2021-07-15T13:00:00+03:00',
        'select_by_default': True,
    },
    {
        'end': '2021-07-15T15:00:00+03:00',
        'estimated_delivery_timepoint': '2021-07-15T14:30:00+03:00',
        'start': '2021-07-15T14:00:00+03:00',
    },
]


@utils.slots_enabled()
@utils.daily_slots_config()
@pytest.mark.now('2021-07-14T17:00:00+00:00')
@pytest.mark.parametrize(
    'shop_picking_type, overall_time, expected_slots',
    [
        # estimated_delivery_timepoint - overall_time дял первого слота
        #  меньше, чем время открытия магазина, поэтому не берем его
        ('our_picking', 2000, EXPECTED_ONE_SLOT),
        ('shop_picking', 2000, EXPECTED_ONE_SLOT),
        # estimated_delivery_timepoint - overall_time дял первого слота
        #  больше, чем время открытия магазина, поэтому ожидаем два слота
        ('our_picking', 1700, EXPECTED_TWO_SLOTS),
        ('shop_picking', 1700, EXPECTED_TWO_SLOTS),
    ],
)
@utils.settings_config(
    estimated_delivery_timepoint_shift=1800, asap_disable_threshold=3600,
)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_calculate_slots_overall_time(
        taxi_eats_customer_slots,
        mock_calculate_load,
        shop_picking_type,
        overall_time,
        expected_slots,
        now,
):
    now = utils.localize(now, 'UTC')
    mock_calculate_load.response['json']['places_load_info'][0].update(
        working_intervals=utils.make_working_intervals(
            now,
            [
                {
                    'day_from': 0,
                    'time_from': '10:00',
                    'day_to': 0,
                    'time_to': '21:00',
                },
                {
                    'day_from': 1,
                    'time_from': '10:00',
                    'day_to': 1,
                    'time_to': '12:00',
                },
            ],
        ),
        shop_picking_type=shop_picking_type,
    )

    order = utils.make_order(
        estimated_picking_time=200, delivery_time='2021-07-15T08:00:00+03:00',
    )
    order['overall_time'] = overall_time

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert response.json()['available_slots'] == expected_slots


@pytest.mark.parametrize(
    'slots_enabled, asap_enabled',
    [(True, True), (True, False), (False, True), (False, False)],
)
@utils.daily_slots_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@utils.settings_config()
async def test_enabling_disabling_slots_and_asap(
        taxi_eats_customer_slots, experiments3, slots_enabled, asap_enabled,
):
    experiments3.add_experiment3_from_marker(
        pytest.mark.experiments3(
            is_config=True,
            name='eats_customer_slots_slots_enabled',
            consumers=[
                'eats-customer-slots/calculate-slots',
                'eats-customer-slots/calculate-delivery-time',
                'eats-customer-slots/orders-per-slot-cache',
            ],
            default_value={
                'enabled': slots_enabled,
                'is_asap_enabled': asap_enabled,
            },
        ),
        None,
    )
    await taxi_eats_customer_slots.invalidate_caches()

    order = utils.make_order()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    if slots_enabled:
        assert response.json()['available_slots']
    else:
        assert not response.json()['available_slots']

    if asap_enabled:
        assert response.json()['available_asap']
    else:
        assert not response.json()['available_asap']


@pytest.mark.parametrize('asap_enabled', [True, False])
@utils.daily_slots_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_enabling_disabling_asap_when_no_settings(
        taxi_eats_customer_slots, experiments3, asap_enabled,
):
    experiments3.add_experiment3_from_marker(
        pytest.mark.experiments3(
            is_config=True,
            name='eats_customer_slots_slots_enabled',
            consumers=[
                'eats-customer-slots/calculate-slots',
                'eats-customer-slots/calculate-delivery-time',
                'eats-customer-slots/orders-per-slot-cache',
            ],
            default_value={'enabled': True, 'is_asap_enabled': asap_enabled},
        ),
        None,
    )
    await taxi_eats_customer_slots.invalidate_caches()

    order = utils.make_order()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert response.json()['available_asap'] == asap_enabled


@pytest.mark.parametrize('asap_enabled', [True, False])
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@utils.settings_config()
async def test_enabling_disabling_asap_no_daily_slots_config(
        taxi_eats_customer_slots, experiments3, asap_enabled,
):
    experiments3.add_experiment3_from_marker(
        pytest.mark.experiments3(
            is_config=True,
            name='eats_customer_slots_slots_enabled',
            consumers=[
                'eats-customer-slots/calculate-slots',
                'eats-customer-slots/calculate-delivery-time',
                'eats-customer-slots/orders-per-slot-cache',
            ],
            default_value={'enabled': True, 'is_asap_enabled': asap_enabled},
        ),
        None,
    )
    await taxi_eats_customer_slots.invalidate_caches()

    order = utils.make_order()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert response.json()['available_asap'] == asap_enabled


@pytest.mark.parametrize('asap_enabled', [True, False])
@utils.settings_config()
async def test_enabling_disabling_asap_no_place_info(
        taxi_eats_customer_slots, experiments3, asap_enabled,
):
    experiments3.add_experiment3_from_marker(
        pytest.mark.experiments3(
            is_config=True,
            name='eats_customer_slots_slots_enabled',
            consumers=[
                'eats-customer-slots/calculate-slots',
                'eats-customer-slots/calculate-delivery-time',
                'eats-customer-slots/orders-per-slot-cache',
            ],
            default_value={'enabled': True, 'is_asap_enabled': asap_enabled},
        ),
        None,
    )
    await taxi_eats_customer_slots.invalidate_caches()

    order = utils.make_order()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert response.json()['available_asap'] == asap_enabled
