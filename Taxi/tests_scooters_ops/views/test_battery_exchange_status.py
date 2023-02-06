import re

import pytest

from tests_scooters_ops import common
from tests_scooters_ops import db_utils
from tests_scooters_ops import utils


@common.TRANSLATIONS
@common.DEEPLINKS_CONFIG
@pytest.mark.parametrize(
    [
        'job_type',
        'ui_statuses',
        'ui_items_filename',
        'is_remove_failed_button',
    ],
    [
        pytest.param(
            'pickup_batteries',
            ['booked'],
            'job_type_pickup_batteries/booked_no_failed.json',
            False,
            id='job_type_pickup_batteries/booked_no_failed',
        ),
        pytest.param(
            'return_batteries',
            ['pickuped'],
            'job_type_return_batteries/pickuped_no_failed.json',
            False,
            id='job_type_return_batteries/pickuped_no_failed',
        ),
        pytest.param(
            'pickup_batteries',
            ['pickuped', 'booked'],
            'job_type_pickup_batteries/booked_pickuped_no_failed.json',
            False,
            id='job_type_pickup_batteries/booked_pickuped_no_failed',
        ),
        pytest.param(
            'return_batteries',
            ['returned', 'pickuped'],
            'job_type_return_batteries/returned_pickuped_no_failed.json',
            False,
            id='job_type_return_batteries/returned_pickuped_no_failed',
        ),
        pytest.param(
            'pickup_batteries',
            ['booked', 'failed'],
            'job_type_pickup_batteries/booked_and_failed.json',
            False,
            id='job_type_pickup_batteries/booked_and_failed',
        ),
        pytest.param(
            'return_batteries',
            ['pickuped', 'failed'],
            'job_type_return_batteries/pickuped_and_failed.json',
            False,
            id='job_type_return_batteries/pickuped_and_failed',
        ),
        pytest.param(
            'pickup_batteries',
            ['pickuped', 'failed'],
            'job_type_pickup_batteries/only_failed_remains.json',
            False,
            id='job_type_pickup_batteries/only_failed_remains',
        ),
        pytest.param(
            'return_batteries',
            ['returned', 'failed'],
            'job_type_return_batteries/only_failed_remains.json',
            False,
            id='job_type_return_batteries/only_failed_remains',
        ),
        pytest.param(
            'pickup_batteries',
            ['failed'],
            'job_type_pickup_batteries/only_failed_at_all.json',
            False,
            id='pickup/only_failed_at_all',
        ),
        pytest.param(
            'return_batteries',
            ['failed'],
            'job_type_return_batteries/only_failed_at_all.json',
            False,
            id='return/only_failed_at_all',
        ),
        pytest.param(
            'pickup_batteries',
            ['pickuped', 'pickuped'],
            'job_type_pickup_batteries/all_pickuped.json',
            False,
            id='all_pickuped',
        ),
        pytest.param(
            'return_batteries',
            ['returned', 'returned'],
            'job_type_return_batteries/all_returned.json',
            False,
            id='all_returned',
        ),
        pytest.param(
            'pickup_batteries',
            ['booked', 'pending'],
            'job_type_pickup_batteries/pending.json',
            False,
            id='pickup pending',
        ),
        pytest.param(
            'return_batteries',
            ['pickuped', 'pending'],
            'job_type_return_batteries/pending.json',
            False,
            id='return pending',
        ),
        pytest.param(
            'pickup_batteries',
            ['booked', 'pending'],
            'job_type_pickup_batteries/pending.json',
            True,
            id='pickup pending',
            marks=common.OLD_SCREENS_SETTINGS,
        ),
        pytest.param(
            'return_batteries',
            ['pickuped', 'pending'],
            'job_type_return_batteries/pending.json',
            True,
            id='return pending',
            marks=common.OLD_SCREENS_SETTINGS,
        ),
    ],
)
async def test_handler(
        taxi_scooters_ops,
        pgsql,
        load_json,
        mockserver,
        job_type,
        ui_statuses,
        ui_items_filename,
        is_remove_failed_button,
):
    item_type = utils.extra_item_type_by_job_type(job_type)
    db_utils.add_job(
        pgsql,
        {
            'job_id': 'job_id',
            'type': job_type,
            'status': 'performing',
            'point_id': 'point_id',
            'order_at_point': 1,
            'typed_extra': {
                'quantity': 1,
                item_type: [
                    {
                        'booking_id': f'booking_{i}',
                        'cabinet_id': 'cabinet_id_1',
                        'cabinet_type': 'charge_station',
                        'cell_id': (
                            f'cell_{i}' if status == 'failed' else 'cell_id'
                        ),
                        'ui_status': status,
                    }
                    for i, status in enumerate(ui_statuses)
                ],
            },
        },
    )

    db_utils.add_point(
        pgsql,
        {
            'point_id': 'point_id',
            'cargo_point_id': 'cargo_point_id',
            'type': 'depot',
            'status': 'arrived',
            'location': (37, 55),
            'mission_id': 'mission_id',
            'order_in_mission': 1,
            'typed_extra': {'depot': {'id': 'depot_id'}},
        },
    )

    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_id',
            'performer_id': 'performer_id',
            'status': 'performing',
        },
    )

    resp = await taxi_scooters_ops.post(
        '/driver/v1/scooters/v1/old-flow/screens/battery-exchange/status',
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id',
            'cargo_point_id': 'cargo_point_id',
            'job_type': job_type,
        },
    )

    assert resp.status == 200

    ui_items = load_json(ui_items_filename)
    if is_remove_failed_button:
        del ui_items[-1]
    assert resp.json() == {'ui_items': ui_items}


@pytest.mark.parametrize(
    ['job_type', 'mission_status', 'point_status', 'job_status', 'response'],
    [
        pytest.param(
            'pickup_batteries',
            'created',
            'arrived',
            'performing',
            {'code': '400', 'message': 'Mission is in incorrect state'},
        ),
        pytest.param(
            'pickup_batteries',
            'performing',
            'cancelled',
            'performing',
            {'code': '400', 'message': 'Point is in incorrect state'},
        ),
        pytest.param(
            'pickup_batteries',
            'performing',
            'arrived',
            'cancelled',
            {'code': '400', 'message': 'Job is in incorrect state'},
        ),
    ],
)
async def test_mission_point_job_validation(
        taxi_scooters_ops,
        pgsql,
        mockserver,
        job_type,
        mission_status,
        point_status,
        job_status,
        response,
):
    item_type = utils.extra_item_type_by_job_type(job_type)
    db_utils.add_job(
        pgsql,
        {
            'job_id': 'job_id',
            'type': job_type,
            'status': job_status,
            'point_id': 'point_id',
            'order_at_point': 1,
            'typed_extra': {
                'quantity': 1,
                item_type: [
                    {
                        'booking_id': 'booking_id',
                        'cabinet_type': 'charge_station',
                        'cell_id': 'cell_id',
                        'ui_status': 'pending',
                    },
                ],
            },
        },
    )

    db_utils.add_point(
        pgsql,
        {
            'point_id': 'point_id',
            'cargo_point_id': 'cargo_point_id',
            'type': 'depot',
            'status': point_status,
            'location': (37, 55),
            'mission_id': 'mission_id',
            'order_in_mission': 1,
            'typed_extra': {'depot': {'id': 'depot_id'}},
        },
    )

    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_id',
            'performer_id': 'performer_id',
            'status': mission_status,
        },
    )

    resp = await taxi_scooters_ops.post(
        '/driver/v1/scooters/v1/old-flow/screens/battery-exchange/status',
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id',
            'cargo_point_id': 'cargo_point_id',
            'job_type': job_type,
        },
    )

    assert resp.status == 400
    assert resp.json() == response


@common.TRANSLATIONS
@common.DEEPLINKS_CONFIG
@pytest.mark.parametrize(
    [
        'job_type',
        'src_booking_status',
        'cabinet_id',
        'cell_id',
        'error_message',
    ],
    [
        pytest.param(
            'pickup_batteries',
            'booked',
            None,
            'cell_id',
            'Booking has no cabinet id',
            id='no cabinet booking pickup job_type',
        ),
        pytest.param(
            'pickup_batteries',
            'booked',
            'cabinet_id',
            None,
            'Booking has no cell id',
            id='no cell booking pickup job_type',
        ),
        pytest.param(
            'return_batteries',
            'pickuped',
            None,
            'cell_id',
            'Booking has no cabinet id',
            id='no cabinet return job_type',
        ),
        pytest.param(
            'return_batteries',
            'pickuped',
            'cabinet_id',
            None,
            'Booking has no cell id',
            id='no cell booking return job_type',
        ),
    ],
)
async def test_booking_validation(
        taxi_scooters_ops,
        pgsql,
        job_type,
        src_booking_status,
        cabinet_id,
        cell_id,
        error_message,
):
    item_type = utils.extra_item_type_by_job_type(job_type)
    db_utils.add_job(
        pgsql,
        {
            'job_id': 'job_id',
            'type': job_type,
            'status': 'performing',
            'point_id': 'point_id',
            'order_at_point': 1,
            'typed_extra': {
                'quantity': 1,
                item_type: [
                    {
                        'booking_id': 'booking_id',
                        'cabinet_type': 'charge_station',
                        'cabinet_id': cabinet_id,
                        'cell_id': cell_id,
                        'ui_status': src_booking_status,
                    },
                ],
            },
        },
    )

    db_utils.add_point(
        pgsql,
        {
            'point_id': 'point_id',
            'cargo_point_id': 'cargo_point_id',
            'type': 'depot',
            'status': 'arrived',
            'location': (37, 55),
            'mission_id': 'mission_id',
            'order_in_mission': 1,
            'typed_extra': {'depot': {'id': 'depot_id'}},
        },
    )

    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_id',
            'performer_id': 'performer_id',
            'status': 'performing',
        },
    )

    resp = await taxi_scooters_ops.post(
        '/driver/v1/scooters/v1/old-flow/screens/battery-exchange/status',
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id',
            'cargo_point_id': 'cargo_point_id',
            'job_type': job_type,
        },
    )
    assert resp.status_code == 400
    assert resp.json()['message'] == error_message


def _get_next_to_pickup_item(response):
    deeplink = response.json()['ui_items'][-1]['payload']['url']
    return re.search('booking_id=([a-z0-9_]+)', deeplink).group(1)


@common.TRANSLATIONS
@common.DEEPLINKS_CONFIG
@pytest.mark.parametrize(
    'cabinet_type', ['cabinet', 'cabinet_without_validation'],
)
@pytest.mark.parametrize(
    ['job_type', 'src_booking_status', 'dst_booking_status'],
    [
        pytest.param(
            'pickup_batteries',
            'booked',
            'failed',
            id='cabinet pickup job_type',
        ),
        pytest.param(
            'return_batteries',
            'pickuped',
            'failed',
            id='cabinet return job_type',
        ),
    ],
)
async def test_cabinet_fast_track_job_type(
        taxi_scooters_ops,
        pgsql,
        load_json,
        mockserver,
        cabinet_type,
        job_type,
        src_booking_status,
        dst_booking_status,
):

    item_type = utils.extra_item_type_by_job_type(job_type)
    db_utils.add_job(
        pgsql,
        {
            'job_id': 'job_id',
            'type': job_type,
            'status': 'performing',
            'point_id': 'point_id',
            'order_at_point': 1,
            'typed_extra': {
                'quantity': 1,
                item_type: [
                    {
                        'booking_id': 'booking_id',
                        'cabinet_id': 'cabinet_id_4',
                        'cabinet_type': cabinet_type,
                        'cell_id': 'cell_id',
                        'ui_status': src_booking_status,
                    },
                ],
            },
        },
    )

    db_utils.add_point(
        pgsql,
        {
            'point_id': 'point_id',
            'cargo_point_id': 'cargo_point_id',
            'type': 'depot',
            'status': 'arrived',
            'location': (37, 55),
            'mission_id': 'mission_id',
            'order_in_mission': 1,
            'typed_extra': {'depot': {'id': 'depot_id'}},
        },
    )

    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_id',
            'performer_id': 'performer_id',
            'status': 'performing',
        },
    )

    resp = await taxi_scooters_ops.post(
        '/driver/v1/scooters/v1/old-flow/screens/battery-exchange/status',
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id',
            'cargo_point_id': 'cargo_point_id',
            'job_type': job_type,
        },
    )

    assert {dst_booking_status} == {
        booking['ui_status']
        for booking in db_utils.get_jobs(
            pgsql, ids=['job_id'], fields=['typed_extra'], flatten=True,
        )[0][item_type]
    }

    assert resp.status_code == 200
    assert resp.json() == {
        'ui_items': load_json(
            f'job_type_{job_type}/only_failed_at_all_manual.json',
        ),
    }
