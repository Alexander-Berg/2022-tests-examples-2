import pytest

from tests_scooters_ops import common
from tests_scooters_ops import db_utils
from tests_scooters_ops import utils


@common.TRANSLATIONS
@common.DEEPLINKS_CONFIG
@pytest.mark.parametrize('job_type', ['pickup_batteries', 'return_batteries'])
@pytest.mark.parametrize(
    'is_remove_failed_button',
    [
        pytest.param(False, id='with_button'),
        pytest.param(True, id='no_button', marks=common.OLD_SCREENS_SETTINGS),
    ],
)
async def test_handler(
        taxi_scooters_ops,
        pgsql,
        load_json,
        mockserver,
        job_type,
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
                        'booking_id': 'booking_id',
                        'cabinet_id': 'cabinet_id',
                        'cell_id': 'cell_id',
                        'cabinet_type': 'cabinet',
                        'ui_status': utils.init_ui_status_by_job_type(
                            job_type,
                        ),
                    },
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
        '/scooter-accumulator/scooter-accumulator/v1/cabinet/cell/open-booked',
    )
    async def _accumulator_open_booked(request):
        assert request.args['booking_id'] == 'booking_id'
        return mockserver.make_response(
            status=200, json={'cell_id': 'cell_id'},
        )

    resp = await taxi_scooters_ops.post(
        '/driver/v1/scooters/v1/old-flow/screens/battery-exchange/open',
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id',
            'cargo_point_id': 'cargo_point_id',
            'booking_id': 'booking_id',
            'cell_id': 'cell_id',
            'job_type': job_type,
        },
    )

    assert _accumulator_open_booked.times_called == 1

    assert resp.status == 200

    ui_items = load_json(f'job_type_{job_type}/response_ui.json')
    if is_remove_failed_button:
        del ui_items[-1]
    assert resp.json() == {'ui_items': ui_items}

    assert (
        db_utils.get_jobs(
            pgsql, ids=['job_id'], fields=['typed_extra'], flatten=True,
        )[0][item_type][0]['ui_status']
        == 'pending'
    )


@pytest.mark.parametrize(
    ['job_type', 'mission', 'error_message'],
    [
        pytest.param(
            'pickup_batteries',
            {
                'mission_id': 'mission_id',
                'status': 'assigning',
                'points': [
                    {
                        'point_id': 'point_id',
                        'cargo_point_id': 'cargo_point_id',
                        'type': 'depot',
                        'typed_extra': {'depot': {'id': 'depot_id'}},
                        'jobs': [
                            {
                                'type': 'pickup_batteries',
                                'typed_extra': {
                                    'quantity': 1,
                                    'accumulators': [
                                        {
                                            'booking_id': 'booking_id',
                                            'cell_id': 'cell_id',
                                            'cabinet_id': 'cabinet_id_1',
                                            'cabinet_type': 'cabinet',
                                            'ui_status': 'pending',
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                ],
            },
            'Mission is in incorrect state',
        ),
        pytest.param(
            'return_batteries',
            {
                'mission_id': 'mission_id',
                'status': 'performing',
                'points': [
                    {
                        'point_id': 'point_id',
                        'cargo_point_id': 'cargo_point_id',
                        'type': 'depot',
                        'typed_extra': {'depot': {'id': 'depot_id'}},
                        'jobs': [
                            {
                                'type': 'return_batteries',
                                'typed_extra': {
                                    'quantity': 1,
                                    'cells': [
                                        {
                                            'booking_id': 'booking_id',
                                            'cell_id': 'cell_id',
                                            'cabinet_id': 'cabinet_id_1',
                                            'cabinet_type': 'cabinet',
                                            'ui_status': 'pending',
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                ],
            },
            'Mission has no performer',
        ),
        pytest.param(
            'pickup_batteries',
            {
                'mission_id': 'mission_id',
                'status': 'performing',
                'performer_id': 'performer_id',
                'points': [
                    {
                        'point_id': 'point_id',
                        'cargo_point_id': 'cargo_point_id',
                        'type': 'depot',
                        'typed_extra': {'depot': {'id': 'depot_id'}},
                        'status': 'cancelled',
                        'jobs': [
                            {
                                'type': 'pickup_batteries',
                                'typed_extra': {
                                    'quantity': 1,
                                    'accumulators': [
                                        {
                                            'booking_id': 'booking_id',
                                            'cell_id': 'cell_id',
                                            'cabinet_id': 'cabinet_id_1',
                                            'cabinet_type': 'cabinet',
                                            'ui_status': 'pending',
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                ],
            },
            'Point is in incorrect state',
        ),
        pytest.param(
            'return_batteries',
            {
                'mission_id': 'mission_id',
                'status': 'performing',
                'performer_id': 'performer_id',
                'points': [
                    {
                        'point_id': 'point_id',
                        'cargo_point_id': 'cargo_point_id',
                        'type': 'depot',
                        'typed_extra': {'depot': {'id': 'depot_id'}},
                        'status': 'arrived',
                        'jobs': [
                            {
                                'type': 'return_batteries',
                                'status': 'completed',
                                'typed_extra': {
                                    'quantity': 1,
                                    'cells': [
                                        {
                                            'booking_id': 'booking_id',
                                            'cell_id': 'cell_id',
                                            'cabinet_id': 'cabinet_id_1',
                                            'cabinet_type': 'cabinet',
                                            'ui_status': 'pending',
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                ],
            },
            'Job is in incorrect state',
        ),
        pytest.param(
            'return_batteries',
            {
                'mission_id': 'mission_id',
                'status': 'performing',
                'performer_id': 'performer_id',
                'points': [
                    {
                        'point_id': 'point_id',
                        'cargo_point_id': 'cargo_point_id',
                        'type': 'depot',
                        'typed_extra': {'depot': {'id': 'depot_id'}},
                        'status': 'arrived',
                        'jobs': [
                            {
                                'type': 'return_batteries',
                                'status': 'performing',
                                'typed_extra': {
                                    'quantity': 1,
                                    'cells': [
                                        {
                                            'booking_id': 'booking_id',
                                            'cell_id': 'cell_id',
                                            'cabinet_type': 'cabinet',
                                            'ui_status': 'failed',
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                ],
            },
            'Booking has no cabinet id',
        ),
    ],
)
async def test_validation(
        pgsql, taxi_scooters_ops, job_type, mission, error_message,
):
    db_utils.add_mission(pgsql, mission)

    resp = await taxi_scooters_ops.post(
        '/driver/v1/scooters/v1/old-flow/screens/battery-exchange/open',
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id',
            'cargo_point_id': 'cargo_point_id',
            'booking_id': 'booking_id',
            'cell_id': 'cell_id',
            'job_type': job_type,
        },
    )

    assert resp.status_code == 400
    assert resp.json() == {'code': '400', 'message': error_message}


@common.TRANSLATIONS
@common.DEEPLINKS_CONFIG
@pytest.mark.parametrize(
    ['job_type', 'accumulators_error_code'],
    [
        pytest.param('pickup_batteries', 'accumulator_was_taken'),
        pytest.param('return_batteries', 'accumulator_was_returned'),
    ],
)
async def test_open_handler_idempotency(
        taxi_scooters_ops,
        pgsql,
        load_json,
        mockserver,
        job_type,
        accumulators_error_code,
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
                        'cabinet_id': 'cabinet_id',
                        'cell_id': 'cell_id',
                        'cabinet_type': 'cabinet',
                        'ui_status': utils.init_ui_status_by_job_type(
                            job_type,
                        ),
                    },
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
        '/scooter-accumulator/scooter-accumulator/v1/cabinet/cell/open-booked',
    )
    async def _accumulator_open_booked(request):
        assert request.args['booking_id'] == 'booking_id'
        return mockserver.make_response(
            status=400,
            json={'code': accumulators_error_code, 'message': 'error'},
        )

    resp = await taxi_scooters_ops.post(
        '/driver/v1/scooters/v1/old-flow/screens/battery-exchange/open',
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id',
            'cargo_point_id': 'cargo_point_id',
            'booking_id': 'booking_id',
            'cell_id': 'cell_id',
            'job_type': job_type,
        },
    )

    assert _accumulator_open_booked.times_called == 1

    assert resp.status == 200
    assert resp.json() == {
        'ui_items': load_json(f'job_type_{job_type}/response_ui.json'),
    }


@common.TRANSLATIONS
@common.DEEPLINKS_CONFIG
@pytest.mark.parametrize('job_type', ['pickup_batteries', 'return_batteries'])
@pytest.mark.parametrize(
    [
        'error_response',
        'ui_items_filename',
        'calls',
        'is_remove_failed_button',
    ],
    [
        pytest.param(
            {'code': 'accumulator_was_taken', 'message': 'error'},
            'error_accumulator_was_taken.json',
            {},
            False,
            id='error accumulator_was_taken',
        ),
        pytest.param(
            {'code': 'accumulator_was_taken', 'message': 'error'},
            'error_accumulator_was_taken.json',
            {},
            True,
            id='error accumulator_was_taken_no_button',
            marks=common.OLD_SCREENS_SETTINGS,
        ),
        pytest.param(
            {'code': 'accumulator_was_returned', 'message': 'error'},
            'error_accumulator_was_returned.json',
            {},
            False,
            id='error accumulator_was_returned',
        ),
        pytest.param(
            {'code': 'accumulator_was_returned', 'message': 'error'},
            'error_accumulator_was_returned.json',
            {},
            True,
            id='error accumulator_was_returned_no_button',
            marks=common.OLD_SCREENS_SETTINGS,
        ),
        pytest.param(
            {'code': 'previous_cell_was_not_closed', 'message': 'error'},
            'error_previous_cell_was_not_closed.json',
            {},
            False,
            id='error previous_cell_was_not_closed',
        ),
        pytest.param(
            {'code': 'cabinet_is_not_responding', 'message': 'error'},
            'unresolvable_error.json',
            {'mock_accumulator': 1},
            False,
            id='error cabinet_is_not_responding',
        ),
        pytest.param(
            {'code': 'open_booked_failed', 'message': 'error'},
            'unresolvable_error.json',
            {'mock_accumulator': 1},
            False,
            id='error open_booked_failed',
        ),
    ],
)
async def test_scooter_accumulator_errors(
        taxi_scooters_ops,
        pgsql,
        load_json,
        mockserver,
        job_type,
        error_response,
        ui_items_filename,
        calls,
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
                        'booking_id': 'booking_id',
                        'cabinet_id': 'cabinet_id',
                        'cell_id': 'cell_id',
                        'cabinet_type': 'cabinet',
                        'ui_status': utils.init_ui_status_by_job_type(
                            job_type,
                        ),
                    },
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
        '/scooter-accumulator/scooter-accumulator/v1/cabinet/cell/open-booked',
    )
    async def _accumulator_open_booked(request):
        assert request.args['booking_id'] == 'booking_id'
        return mockserver.make_response(status=400, json=error_response)

    resp = await taxi_scooters_ops.post(
        '/driver/v1/scooters/v1/old-flow/screens/battery-exchange/open',
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id',
            'cargo_point_id': 'cargo_point_id',
            'booking_id': 'booking_id',
            'cell_id': 'cell_id',
            'job_type': job_type,
        },
    )

    assert resp.status == 200

    ui_items = load_json(f'job_type_{job_type}/' + ui_items_filename)
    if is_remove_failed_button:
        del ui_items[-1]
    assert resp.json() == {'ui_items': ui_items}

    assert _accumulator_open_booked.times_called == 1
