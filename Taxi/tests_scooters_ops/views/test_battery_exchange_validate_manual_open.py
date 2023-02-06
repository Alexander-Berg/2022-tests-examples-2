import pytest

from tests_scooters_ops import common
from tests_scooters_ops import db_utils
from tests_scooters_ops import utils


@common.TRANSLATIONS
@common.DEEPLINKS_CONFIG
@pytest.mark.parametrize(
    'cabinet_type', ['cabinet', 'cabinet_without_validation'],
)
@pytest.mark.parametrize(
    ['job_type', 'src_statuses', 'dst_status'],
    [
        pytest.param(
            'pickup_batteries', ['pickuped', 'failed', 'failed'], 'pickuped',
        ),
        pytest.param(
            'return_batteries', ['returned', 'failed', 'failed'], 'returned',
        ),
    ],
)
async def test_handler(
        taxi_scooters_ops,
        pgsql,
        load_json,
        mockserver,
        cabinet_type,
        job_type,
        src_statuses,
        dst_status,
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
                        'booking_id': f'booking_id_{i}',
                        'cabinet_id': 'cabinet_id',
                        'cell_id': f'cell_{i}',
                        'cabinet_type': cabinet_type,
                        'ui_status': status,
                    }
                    for i, status in enumerate(src_statuses)
                ],
            },
        },
    )

    db_utils.add_point(
        pgsql,
        {
            'point_id': 'point_id',
            'type': 'depot',
            'cargo_point_id': 'cargo_point_id',
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

    @mockserver.json_handler(
        (
            '/scooter-accumulator/scooter-accumulator/v1/cabinet/cell/'
            'check-processed'
        ),
    )
    async def _accumulator_check_processed(request):
        assert request.args['booking_id'] in [
            f'booking_id_{i}' for i in range(len(src_statuses))
        ]
        return mockserver.make_response(
            status=200, json={'cell_id': 'cell_id'},
        )

    resp = await taxi_scooters_ops.post(
        '/driver/v1/scooters/v1/old-flow/screens'
        '/battery-exchange/validate-manual-open',
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id',
            'cargo_point_id': 'cargo_point_id',
            'job_type': job_type,
        },
    )

    assert resp.status == 200
    assert resp.json() == {
        'ui_items': load_json(f'job_type_{job_type}/response_ui.json'),
    }

    assert _accumulator_check_processed.times_called == 2

    bookings = db_utils.get_jobs(
        pgsql, ids=['job_id'], fields=['typed_extra'], flatten=True,
    )[0][item_type]
    for booking in bookings:
        assert booking['ui_status'] == dst_status, booking


@pytest.mark.parametrize(
    ['job_type', 'mission_props', 'point_props', 'job_props', 'response'],
    [
        pytest.param(
            'pickup_batteries',
            {'status': 'created'},
            {},
            {},
            {'code': '400', 'message': 'Mission is in incorrect state'},
            id='Mission incorrect state (pickup)',
        ),
        pytest.param(
            'pickup_batteries',
            {'status': 'performing'},
            {'status': 'cancelled'},
            {},
            {'code': '400', 'message': 'Point is in incorrect state'},
            id='Point incorrect state (pickup)',
        ),
        pytest.param(
            'pickup_batteries',
            {'status': 'performing'},
            {'status': 'arrived'},
            {'status': 'created'},
            {'code': '400', 'message': 'Job is in incorrect state'},
            id='Job incorrect state (pickup)',
        ),
    ],
)
async def test_validation(
        taxi_scooters_ops,
        pgsql,
        job_type,
        mission_props,
        point_props,
        job_props,
        response,
):
    item_type = utils.extra_item_type_by_job_type(job_type)

    db_utils.add_job(
        pgsql,
        {
            **{
                'job_id': 'job_id',
                'status': 'performing',
                'type': job_type,
                'point_id': 'point_id',
                'order_at_point': 1,
                'typed_extra': {
                    'quantity': 1,
                    item_type: [
                        {'booking_id': f'booking_id', 'ui_status': 'failed'},
                    ],
                },
            },
            **job_props,
        },
    )

    db_utils.add_point(
        pgsql,
        {
            **{
                'point_id': 'point_id',
                'type': 'depot',
                'cargo_point_id': 'cargo_point_id',
                'location': (37, 55),
                'mission_id': 'mission_id',
                'order_in_mission': 1,
                'typed_extra': {'depot': {'id': 'depot_id'}},
            },
            **point_props,
        },
    )

    db_utils.add_mission(
        pgsql, {**{'mission_id': 'mission_id'}, **mission_props},
    )

    resp = await taxi_scooters_ops.post(
        '/driver/v1/scooters/v1/old-flow/screens'
        '/battery-exchange/validate-manual-open',
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
    ['job_type', 'error_code', 'cabinet_type', 'error_message'],
    [
        pytest.param(
            'pickup_batteries',
            'accumulator_was_not_taken',
            'charge_station',
            'Заберите аккумулятор',
            id='pickup/accumulator_was_not_taken/charge_station',
        ),
        pytest.param(
            'pickup_batteries',
            'accumulator_was_not_taken',
            'cabinet',
            'Кладовщик хреново работает. Надо лучше',
            id='pickup/accumulator_was_not_taken/cabinet',
        ),
        pytest.param(
            'pickup_batteries',
            'accumulator_was_not_taken',
            'cabinet_without_validation',
            'Кладовщик хреново работает. Надо лучше',
            id='pickup/accumulator_was_not_taken/cabinet_without_validation',
        ),
        pytest.param(
            'return_batteries',
            'accumulator_was_not_returned',
            'charge_station',
            'Верните аккумулятор',
            id='return/accumulator_was_not_returned/charge_station',
        ),
        pytest.param(
            'return_batteries',
            'accumulator_was_not_returned',
            'cabinet',
            'Кладовщик хреново работает. Надо лучше',
            id='return/accumulator_was_not_returned/cabinet',
        ),
        pytest.param(
            'return_batteries',
            'accumulator_was_not_returned',
            'cabinet_without_validation',
            'Кладовщик хреново работает. Надо лучше',
            id='return/accumulator_was_not_returned/'
            'cabinet_without_validation',
        ),
        pytest.param(
            'pickup_batteries',
            'cell_was_not_closed',
            'charge_station',
            'Закройте ячейку',
            id='pickup/cell_was_not_closed',
        ),
        pytest.param(
            'return_batteries',
            'cell_was_not_closed',
            'charge_station',
            'Закройте ячейку',
            id='return/cell_was_not_closed',
        ),
        pytest.param(
            'pickup_batteries',
            'cabinet_is_not_responding',
            'charge_station',
            'Случилось что-то странное',
            id='pickup/cabinet_is_not_responding',
        ),
        pytest.param(
            'return_batteries',
            'cabinet_is_not_responding',
            'charge_station',
            'Случилось что-то странное',
            id='return/cabinet_is_not_responding',
        ),
        pytest.param(
            'pickup_batteries',
            'check_processed_failed',
            'charge_station',
            'Случилось что-то странное',
            id='pickup/check_processed_failed',
        ),
        pytest.param(
            'pickup_batteries',
            'check_processed_failed',
            'cabinet',
            'Кладовщик хреново работает. Надо лучше',
            id='pickup/check_processed_failed/cabinet',
        ),
        pytest.param(
            'pickup_batteries',
            'check_processed_failed',
            'cabinet_without_validation',
            'Кладовщик хреново работает. Надо лучше',
            id='pickup/check_processed_failed/cabinet_without_validation',
        ),
        pytest.param(
            'return_batteries',
            'check_processed_failed',
            'charge_station',
            'Случилось что-то странное',
            id='return/check_processed_failed',
        ),
        pytest.param(
            'return_batteries',
            'check_processed_failed',
            'cabinet',
            'Кладовщик хреново работает. Надо лучше',
            id='return/check_processed_failed/cabinet',
        ),
        pytest.param(
            'return_batteries',
            'check_processed_failed',
            'cabinet_without_validation',
            'Кладовщик хреново работает. Надо лучше',
            id='return/check_processed_failed/cabinet_without_validation',
        ),
    ],
)
async def test_errors_not_resolved(
        taxi_scooters_ops,
        pgsql,
        mockserver,
        load_json,
        job_type,
        error_code,
        cabinet_type,
        error_message,
):

    item_type = utils.extra_item_type_by_job_type(job_type)

    db_utils.add_job(
        pgsql,
        {
            'job_id': 'job_id',
            'status': 'performing',
            'type': job_type,
            'point_id': 'point_id',
            'order_at_point': 1,
            'typed_extra': {
                'quantity': 1,
                item_type: [
                    {
                        'booking_id': f'booking_id_{i}',
                        'ui_status': 'failed',
                        'cabinet_id': 'cabinet_id',
                        'cell_id': f'cell_{i}',
                        'cabinet_type': cabinet_type,
                    }
                    for i in range(2)
                ],
            },
        },
    )

    db_utils.add_point(
        pgsql,
        {
            'point_id': 'point_id',
            'status': 'arrived',
            'type': 'depot',
            'cargo_point_id': 'cargo_point_id',
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

    @mockserver.json_handler(
        (
            '/scooter-accumulator/scooter-accumulator/v1/cabinet/cell/'
            'check-processed'
        ),
    )
    async def _accumulator_check_processed(request):
        assert request.args['booking_id'] in [
            f'booking_id_{i}' for i in range(2)
        ]
        return mockserver.make_response(
            status=400,
            json={
                'code': error_code,
                'message': 'error',
                'cell_id': 'cell_id',
            },
        )

    resp = await taxi_scooters_ops.post(
        '/driver/v1/scooters/v1/old-flow/screens'
        '/battery-exchange/validate-manual-open',
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id',
            'cargo_point_id': 'cargo_point_id',
            'job_type': job_type,
        },
    )

    assert _accumulator_check_processed.times_called == 2

    assert resp.status == 200

    bookings = db_utils.get_jobs(
        pgsql, ids=['job_id'], fields=['typed_extra'], flatten=True,
    )[0][item_type]
    for booking in bookings:
        assert booking['ui_status'] == 'failed', booking

    if cabinet_type in ('cabinet', 'cabinet_without_validation'):
        ui_items = load_json(f'job_type_{job_type}/not_resolved_ui.json')
    else:
        ui_items = load_json(
            f'job_type_{job_type}/not_resolved_with_cells_ui.json',
        )

    ui_items[3]['text'] = error_message

    assert resp.json() == {'ui_items': ui_items}
