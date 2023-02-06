import datetime

import psycopg2
import pytest

DEFAULT_WAYBILL_REF = 'waybill_ref_0'
DEFAULT_WAYBILL_REVISION = 0
DEFAULT_ORDER_NRS = ['order_nr_123']
DEFAULT_WAYBILL_RESOLUTION = 'complete'
DEFAULT_CARGO_WAYBILL_CREATED_ASSERT = datetime.datetime(
    2020,
    10,
    28,
    3,
    0,
    tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
)
DEFAULT_CARGO_WAYBILL_CREATED_AT = '2020-10-28T00:00:00.00+00:00'
DEFAULT_POINTS = [
    {
        'id': 1,
        'claim_id': 'alias_123',
        'address': {'coordinates': [35.8, 55.4]},
        'type': 'source',
        'visit_order': 1,
        'visit_status': 'pending',
        'corp_client_id': 'corp_id_123',
        'external_order_id': 'order_nr_123',
    },
    {
        'id': 2,
        'claim_id': 'alias_123',
        'address': {'coordinates': [37.8, 55.4]},
        'type': 'destination',
        'visit_order': 2,
        'visit_status': 'pending',
        'corp_client_id': 'corp_id_123',
        'external_order_id': 'order_nr_123',
    },
]
DEFAULT_PERFORMER_INFO = {
    'park_id': 'park_123',
    'driver_id': 'driver_123',
    'name': 'Happy Batman',
    'car_model': 'Moskvich',
    'car_number': '123',
    'is_deaf': True,
    'phone_pd_id': '123456789',
    'transport_type': 'car',
}


def build_db_performer_info(
        stq_performer_info,
        builded_courier_type,
        builded_performer_name,
        builded_car_model=None,
        builded_car_number=None,
):
    db_performer_info = {
        'park_id': stq_performer_info['park_id'],
        'driver_id': stq_performer_info['driver_id'],
        'name': builded_performer_name,
        'is_hard_of_hearing': stq_performer_info['is_deaf'],
        'personal_phone_id': stq_performer_info['phone_pd_id'],
        'raw_type': stq_performer_info['transport_type'],
        'type': builded_courier_type,
    }
    if builded_car_model:
        db_performer_info['car_model'] = builded_car_model
    if builded_car_number:
        db_performer_info['car_number'] = builded_car_number
    return db_performer_info


def make_config_stq_retry(
        max_exec_tries=10, max_reschedule_counter=10, reschedule_seconds=10,
):
    return {
        'stq_orders': {
            'max_exec_tries': 10,
            'max_reschedule_counter': 10,
            'reschedule_seconds': 10,
        },
        'stq_couriers': {
            'max_exec_tries': 10,
            'max_reschedule_counter': 10,
            'reschedule_seconds': 10,
        },
        'stq_orders_eta': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
        'stq_picker_orders': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
        'stq_cargo_waybill_changes': {
            'max_exec_tries': max_exec_tries,
            'max_reschedule_counter': max_reschedule_counter,
            'reschedule_seconds': reschedule_seconds,
        },
        'stq_order_taken_push': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
        'stq_order_to_another_eater_sms': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
    }


def get_stq_waybill_kwargs(
        points,
        performer_info,
        chained_previous_waybill_ref=None,
        waybill_ref=DEFAULT_WAYBILL_REF,
        waybill_revision=DEFAULT_WAYBILL_REVISION,
        waybill_resolution=DEFAULT_WAYBILL_RESOLUTION,
        cargo_waybill_created_at=DEFAULT_CARGO_WAYBILL_CREATED_AT,
        is_actual_waybill=True,
):
    kwargs = {
        'points': points,
        'waybill_ref': waybill_ref,
        'waybill_revision': waybill_revision,
        'is_actual_waybill': is_actual_waybill,
        'waybill_resolution': waybill_resolution,
        'waybill_created_ts': cargo_waybill_created_at,
    }
    if performer_info:
        kwargs['performer_info'] = performer_info
    if chained_previous_waybill_ref:
        kwargs['chain_parent_waybill_ref'] = chained_previous_waybill_ref
    return kwargs


def get_db_waybill(waybill_ref, get_cursor):
    cursor = get_cursor()
    cursor.execute(
        'SELECT waybill_ref, points, performer_info, order_nrs,'
        'chained_previous_waybill_ref,'
        'waybill_revision, cargo_waybill_created_at, '
        'is_actual_waybill, waybill_resolution '
        'FROM eats_orders_tracking.waybills '
        'WHERE waybill_ref = %s',
        [waybill_ref],
    )
    return cursor.fetchone()


def assert_correct_db_waybill(
        input_db_waybill,
        points,
        performer_info,
        order_nrs,
        waybill_ref=DEFAULT_WAYBILL_REF,
        waybill_revision=DEFAULT_WAYBILL_REVISION,
        chained_previous_waybill_ref=None,
        waybill_resolution=DEFAULT_WAYBILL_RESOLUTION,
        cargo_waybill_created_at=DEFAULT_CARGO_WAYBILL_CREATED_ASSERT,
        is_actual_waybill=True,
):
    expected_db_waybill = {
        'waybill_ref': waybill_ref,
        'waybill_revision': waybill_revision,
        'points': points,
        'order_nrs': order_nrs,
        'performer_info': performer_info,
        'is_actual_waybill': is_actual_waybill,
        'waybill_resolution': waybill_resolution,
        'cargo_waybill_created_at': cargo_waybill_created_at,
    }
    if chained_previous_waybill_ref:
        expected_db_waybill[
            'chained_previous_waybill_ref'
        ] = chained_previous_waybill_ref

    assert input_db_waybill[0] == expected_db_waybill['waybill_ref']
    assert input_db_waybill[5] == expected_db_waybill['waybill_revision']
    assert input_db_waybill[1] == expected_db_waybill['points']
    assert input_db_waybill[2] == expected_db_waybill['performer_info']
    assert set(input_db_waybill[3]) == set(expected_db_waybill['order_nrs'])
    assert (
        input_db_waybill[6] == expected_db_waybill['cargo_waybill_created_at']
    )
    assert input_db_waybill[7] == expected_db_waybill['is_actual_waybill']
    assert input_db_waybill[8] == expected_db_waybill['waybill_resolution']
    if chained_previous_waybill_ref:
        assert (
            input_db_waybill[4]
            == expected_db_waybill['chained_previous_waybill_ref']
        )
    else:
        assert not input_db_waybill[4]


@pytest.mark.parametrize(
    'waybill_ref, points, performer_info, exp_order_nrs, '
    'exp_courier_type, exp_performer_name,'
    'exp_car_model, exp_car_number, exp_prev_waybill_ref',
    [
        pytest.param(
            DEFAULT_WAYBILL_REF,
            DEFAULT_POINTS,
            DEFAULT_PERFORMER_INFO,
            DEFAULT_ORDER_NRS,
            'vehicle',
            'Batman',
            'Moskvich',
            '123',
            None,
            id='insert_without_prev_waybill',
        ),
        pytest.param(
            'waybill_ref_11',
            DEFAULT_POINTS,
            {
                'driver_id': 'driver_1',
                'park_id': 'park_1',
                'name': 'Super New',
                'transport_type': 'pedestrian',
                'is_deaf': False,
                'car_model': 'xxx',
                'car_number': 'xxx',
                'phone_pd_id': 'pd_123',
            },
            DEFAULT_ORDER_NRS,
            'pedestrian',
            'Super',
            None,
            None,
            'waybill_ref_2',
            id='insert_with_prev_waybill',
        ),
    ],
)
@pytest.mark.pgsql('eats_orders_tracking', files=['waybills.sql'])
@pytest.mark.config(
    EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry(),
    EATS_ORDERS_TRACKING_WAYBILL_CONSUMER_SETTINGS={
        'is_short_order_nr_exchange_enabled': True,
    },
)
async def test_stq_waybill_new_waybill(
        stq_runner,
        get_cursor,
        mockserver,
        # parameters
        waybill_ref,
        points,
        performer_info,
        exp_order_nrs,
        exp_courier_type,
        exp_performer_name,
        exp_car_model,
        exp_car_number,
        exp_prev_waybill_ref,
):
    kwargs = get_stq_waybill_kwargs(
        waybill_ref=waybill_ref,
        points=points,
        performer_info=performer_info,
        chained_previous_waybill_ref=exp_prev_waybill_ref,
    )

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def mock_driver_profiles(request):
        return mockserver.make_response(
            json={
                'profiles': [
                    {
                        'park_driver_profile_id': 'park_123_driver_123',
                        'data': (
                            {'full_name': {'first_name': exp_performer_name}}
                        ),
                    },
                ],
            },
        )

    await stq_runner.eats_orders_tracking_cargo_waybill_changes.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )
    db_waybill = get_db_waybill(kwargs['waybill_ref'], get_cursor)
    assert_correct_db_waybill(
        input_db_waybill=db_waybill,
        waybill_ref=waybill_ref,
        points=points,
        order_nrs=exp_order_nrs,
        performer_info=build_db_performer_info(
            performer_info,
            exp_courier_type,
            builded_performer_name=exp_performer_name,
            builded_car_model=exp_car_model,
            builded_car_number=exp_car_number,
        ),
        chained_previous_waybill_ref=exp_prev_waybill_ref,
    )
    assert mock_driver_profiles.times_called == 1


@pytest.mark.parametrize(
    'waybill_revision, expected_revision,'
    'expected_points, expected_performer_info,'
    'expected_order_nrs',
    [
        pytest.param(
            2,
            2,
            DEFAULT_POINTS,
            {
                'driver_id': 'driver_11',
                'park_id': 'park_11',
                'name': 'Super',
                'raw_type': 'courier_car',
                'type': 'vehicle',
                'is_hard_of_hearing': True,
                'car_model': 'xxx',
                'car_number': 'xxx',
                'personal_phone_id': 'pd_12345',
            },
            DEFAULT_ORDER_NRS,
            id='fresh_revision',
        ),
        pytest.param(
            0,
            1,
            [
                {
                    'id': 3,
                    'claim_id': '789',
                    'address': {'coordinates': [1.0, 1.0]},
                    'type': 'source',
                    'visit_order': 2,
                    'visit_status': 'pending',
                    'corp_client_id': 'corp_111',
                    'external_order_id': 'order_3',
                },
                {
                    'id': 4,
                    'claim_id': '789',
                    'address': {'coordinates': [1.0, 1.0]},
                    'type': 'destination',
                    'visit_order': 4,
                    'visit_status': 'pending',
                    'corp_client_id': 'corp_111',
                    'external_order_id': 'order_3',
                },
            ],
            {
                'driver_id': 'driver_1',
                'park_id': 'park_1',
                'name': 'Super',
                'raw_type': 'pedestrian',
                'type': 'pedestrian',
                'is_hard_of_hearing': False,
                'car_model': 'xxx',
                'car_number': 'xxx',
                'personal_phone_id': 'pd_123',
            },
            ['order_3'],
            id='old_revision',
        ),
    ],
)
@pytest.mark.now('2020-10-28T00:00:00.00+00:00')
@pytest.mark.config(EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry())
@pytest.mark.pgsql('eats_orders_tracking', files=['waybills.sql'])
async def test_stq_waybill_update_waybill(
        stq_runner,
        get_cursor,
        mockserver,
        # parameters
        waybill_revision,
        expected_revision,
        expected_points,
        expected_performer_info,
        expected_order_nrs,
):
    waybill_ref = 'waybill_ref_2'
    stq_performer_info = {
        'driver_id': 'driver_11',
        'park_id': 'park_11',
        'name': 'Super New',
        'transport_type': 'courier_car',
        'is_deaf': True,
        'car_model': 'xxx',
        'car_number': 'xxx',
        'phone_pd_id': 'pd_12345',
    }

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def mock_driver_profiles(request):
        return mockserver.make_response(
            json={
                'profiles': [
                    {
                        'park_driver_profile_id': 'park_123_driver_123',
                        'data': ({'full_name': {'first_name': 'Super'}}),
                    },
                ],
            },
        )

    kwargs = get_stq_waybill_kwargs(
        # existed waybill_ref
        waybill_ref=waybill_ref,
        waybill_revision=waybill_revision,
        points=DEFAULT_POINTS,
        performer_info=stq_performer_info,
    )
    await stq_runner.eats_orders_tracking_cargo_waybill_changes.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )
    db_waybill = get_db_waybill(kwargs['waybill_ref'], get_cursor)
    assert_correct_db_waybill(
        input_db_waybill=db_waybill,
        waybill_ref=waybill_ref,
        waybill_revision=expected_revision,
        points=expected_points,
        order_nrs=expected_order_nrs,
        performer_info=expected_performer_info,
        chained_previous_waybill_ref='waybill_ref_1',
    )
    assert mock_driver_profiles.times_called == 1


@pytest.mark.pgsql('eats_orders_tracking', files=['waybills.sql'])
@pytest.mark.config(EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry())
async def test_stq_destroy_waybill(stq_runner, get_cursor, mockserver):
    stq_performer_info = {
        'driver_id': 'driver_1',
        'park_id': 'park_1',
        'name': 'Super New',
        'transport_type': 'courier_car',
        'is_deaf': False,
        'car_number': 'xxx',
        'car_model': 'xxx',
        'phone_pd_id': 'pd_123',
    }

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def mock_driver_profiles(request):
        return mockserver.make_response(
            json={
                'profiles': [
                    {
                        'park_driver_profile_id': 'park_123_driver_123',
                        'data': ({'full_name': {'first_name': 'Super'}}),
                    },
                ],
            },
        )

    kwargs = get_stq_waybill_kwargs(
        waybill_ref='waybill_ref2',
        points=DEFAULT_POINTS,
        waybill_resolution='failed',
        performer_info=stq_performer_info,
        waybill_revision=100,
    )
    await stq_runner.eats_orders_tracking_cargo_waybill_changes.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )
    db_waybill = get_db_waybill(kwargs['waybill_ref'], get_cursor)
    assert_correct_db_waybill(
        input_db_waybill=db_waybill,
        waybill_ref='waybill_ref2',
        points=None,
        order_nrs=[],
        waybill_revision=100,
        waybill_resolution='failed',
        performer_info={
            'driver_id': 'driver_1',
            'park_id': 'park_1',
            'name': 'Super',
            'raw_type': 'courier_car',
            'type': 'vehicle',
            'is_hard_of_hearing': False,
            'car_model': 'xxx',
            'car_number': 'xxx',
            'personal_phone_id': 'pd_123',
        },
    )
    assert mock_driver_profiles.times_called == 1


@pytest.mark.parametrize(
    'points, expected_points, exp_order_nrs',
    [
        pytest.param(
            [
                {
                    'id': 1,
                    'claim_id': 'alias_123',
                    'address': {'coordinates': [35.8, 55.4]},
                    'type': 'source',
                    'visit_order': 1,
                    'visit_status': 'pending',
                    'corp_client_id': 'corp_id_123',
                    'external_order_id': '111111-222-3333',
                },
                {
                    'id': 2,
                    'claim_id': 'alias_123',
                    'address': {'coordinates': [37.8, 55.4]},
                    'type': 'destination',
                    'visit_order': 2,
                    'visit_status': 'pending',
                    'corp_client_id': 'corp_id_123',
                    'external_order_id': '333333-222-1111',
                },
            ],
            [
                {
                    'id': 1,
                    'claim_id': 'alias_123',
                    'address': {'coordinates': [35.8, 55.4]},
                    'type': 'source',
                    'visit_order': 1,
                    'visit_status': 'pending',
                    'corp_client_id': 'corp_id_123',
                    'external_order_id': 'grocery-extended-order-nr',
                },
                {
                    'id': 2,
                    'claim_id': 'alias_123',
                    'address': {'coordinates': [37.8, 55.4]},
                    'type': 'destination',
                    'visit_order': 2,
                    'visit_status': 'pending',
                    'corp_client_id': 'corp_id_123',
                    'external_order_id': 'grocery-extended-order-nr-2',
                },
            ],
            ['grocery-extended-order-nr', 'grocery-extended-order-nr-2'],
            id='grocery_convert_short_order_nr_to_extended',
        ),
    ],
)
@pytest.mark.pgsql('eats_orders_tracking', files=['grocery_order.sql'])
@pytest.mark.config(
    EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry(),
    EATS_ORDERS_TRACKING_WAYBILL_CONSUMER_SETTINGS={
        'is_short_order_nr_exchange_enabled': True,
    },
)
async def test_stq_waybill_grocery_waybill(
        stq_runner,
        get_cursor,
        mockserver,
        # parameters
        points,
        expected_points,
        exp_order_nrs,
):
    kwargs = get_stq_waybill_kwargs(
        waybill_ref=DEFAULT_WAYBILL_REF,
        points=points,
        performer_info=DEFAULT_PERFORMER_INFO,
    )

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def mock_driver_profiles(request):
        return mockserver.make_response(
            json={
                'profiles': [
                    {
                        'park_driver_profile_id': 'park_123_driver_123',
                        'data': ({'full_name': {'first_name': 'Batman'}}),
                    },
                ],
            },
        )

    await stq_runner.eats_orders_tracking_cargo_waybill_changes.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )
    db_waybill = get_db_waybill(kwargs['waybill_ref'], get_cursor)
    assert_correct_db_waybill(
        input_db_waybill=db_waybill,
        waybill_ref=DEFAULT_WAYBILL_REF,
        points=expected_points,
        order_nrs=exp_order_nrs,
        performer_info={
            'driver_id': 'driver_123',
            'park_id': 'park_123',
            'name': 'Batman',
            'raw_type': 'car',
            'type': 'vehicle',
            'is_hard_of_hearing': True,
            'car_model': 'Moskvich',
            'car_number': '123',
            'personal_phone_id': '123456789',
        },
    )
    assert mock_driver_profiles.times_called == 1
