import pytest

from tests_scooters_ops import common
from tests_scooters_ops import db_utils

HANDLER = '/driver/v1/scooters/v1/accumulators/process-with-plain-cabinet'
PROCESS_PICKUP_ACCUMULATORS_HANDLER = (
    '/scooter-accumulator/scooter-accumulator/v1/fallback-api/'
    'cabinet/booking/accumulator-taken-processed'
)
PROCESS_RETURN_ACCUMULATORS_HANDLER = (
    '/scooter-accumulator/scooter-accumulator/v1/fallback-api/'
    'cabinet/booking/accumulator-return-processed'
)

MISSION_1 = {
    'mission_id': 'mission_id_1',
    'status': 'performing',
    'performer_id': 'performer_1',
    'points': [
        {
            'type': 'depot',
            'status': 'arrived',
            'point_id': 'point_id_depot_1',
            'typed_extra': {'depot': {'id': 'depot_id_1'}},
            'jobs': [
                {
                    'job_id': 'job_id_depot_1',
                    'type': 'pickup_batteries',
                    'status': 'performing',
                    'typed_extra': {
                        'accumulators': [
                            {
                                'cell_id': '413',
                                'ui_status': 'booked',
                                'booking_id': 'booking_id_1',
                                'cabinet_id': 'plain_cabinet_id_1',
                                'cabinet_type': 'cabinet',
                                'accumulator_id': 'acc_1',
                            },
                            {
                                'cell_id': '409',
                                'ui_status': 'booked',
                                'booking_id': 'booking_id_2',
                                'cabinet_id': 'plain_cabinet_id_1',
                                'cabinet_type': 'cabinet',
                                'accumulator_id': 'acc_2',
                            },
                        ],
                    },
                },
                {
                    'job_id': 'job_id_2_depot_1',
                    'type': 'pickup_batteries',
                    'status': 'performing',
                    'typed_extra': {
                        'accumulators': [
                            {
                                'cell_id': '42',
                                'ui_status': 'booked',
                                'booking_id': 'booking_id_2',
                                'cabinet_id': 'charge_station_id_1',
                                'cabinet_type': 'charge_station',
                                'accumulator_id': 'acc_42',
                            },
                        ],
                    },
                },
            ],
        },
    ],
}

MISSION_2 = {
    'mission_id': 'mission_id_2',
    'status': 'performing',
    'performer_id': 'performer_1',
    'points': [
        {
            'type': 'depot',
            'status': 'arrived',
            'point_id': 'return_point_1',
            'typed_extra': {'depot': {'id': 'depot_id_2'}},
            'jobs': [
                {
                    'job_id': 'return_job_1',
                    'type': 'return_batteries',
                    'status': 'performing',
                    'typed_extra': {
                        'cells': [
                            {
                                'cell_id': '413',
                                'ui_status': 'pickuped',
                                'booking_id': 'booking_id_1',
                                'cabinet_id': 'plain_cabinet_id_1',
                                'cabinet_type': 'cabinet',
                            },
                            {
                                'cell_id': '409',
                                'ui_status': 'pickuped',
                                'booking_id': 'booking_id_2',
                                'cabinet_id': 'plain_cabinet_id_1',
                                'cabinet_type': 'cabinet',
                            },
                        ],
                    },
                },
                {
                    'job_id': 'return_job_2',
                    'type': 'return_batteries',
                    'status': 'performing',
                    'typed_extra': {
                        'cells': [
                            {
                                'cell_id': '42',
                                'ui_status': 'pickuped',
                                'booking_id': 'booking_id_3',
                                'cabinet_id': 'charge_station_id_1',
                                'cabinet_type': 'charge_station',
                                'accumulator_id': 'acc_42',
                            },
                        ],
                    },
                },
            ],
        },
    ],
}


def _get_accumulators_status(job):
    accumulators = job['typed_extra']['accumulators']
    result = []
    for acc in accumulators:
        result.append(
            {
                'accumulator_id': acc['accumulator_id'],
                'ui_status': acc['ui_status'],
            },
        )

    sorted(result, key=lambda x: x['accumulator_id'])
    return result


def _get_cells_status(job):
    cells = job['typed_extra']['cells']
    result = []
    for cell in cells:
        result.append(
            {'booking_id': cell['booking_id'], 'ui_status': cell['ui_status']},
        )

    sorted(result, key=lambda x: x['booking_id'])
    return result


async def test_pickup_ok(pgsql, mockserver, taxi_scooters_ops):
    db_utils.add_mission(pgsql, MISSION_1)

    @mockserver.json_handler(PROCESS_PICKUP_ACCUMULATORS_HANDLER)
    async def _accumulator_taken_processed(request):
        assert request.args == {
            'consumer_id': 'performer_1',
            'contractor_id': 'performer_1',
            'accumulator_id': 'acc_1',
            'cabinet_id': 'plain_cabinet_id_1',
        }
        return {
            'booking_id': 'booking_id_1',
            'cell_id': '413',
            'status': 'PROCESSED',
        }

    response = await taxi_scooters_ops.post(
        HANDLER,
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id_1',
            'point_id': 'point_id_depot_1',
            'job_id': 'job_id_depot_1',
            'accumulator_id': 'acc_1',
        },
    )

    assert response.status == 200
    assert _accumulator_taken_processed.times_called == 1
    job = db_utils.get_jobs(pgsql, ids=['job_id_depot_1'])[0]
    assert _get_accumulators_status(job) == [
        {'accumulator_id': 'acc_1', 'ui_status': 'pickuped'},
        {'accumulator_id': 'acc_2', 'ui_status': 'booked'},
    ]


async def test_return_ok(pgsql, mockserver, taxi_scooters_ops):
    db_utils.add_mission(pgsql, MISSION_2)

    @mockserver.json_handler(PROCESS_RETURN_ACCUMULATORS_HANDLER)
    async def _accumulator_return_processed(request):
        assert request.args == {
            'consumer_id': 'performer_1',
            'contractor_id': 'performer_1',
            'accumulator_id': 'acc_1',
            'cabinet_id': 'plain_cabinet_id_1',
        }
        return {
            'booking_id': 'booking_id_1',
            'cell_id': '413',
            'status': 'PROCESSED',
        }

    response = await taxi_scooters_ops.post(
        HANDLER,
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id_2',
            'point_id': 'return_point_1',
            'job_id': 'return_job_1',
            'accumulator_id': 'acc_1',
        },
    )

    assert response.status == 200
    assert _accumulator_return_processed.times_called == 1
    job = db_utils.get_jobs(pgsql, ids=['return_job_1'])[0]
    assert _get_cells_status(job) == [
        {'booking_id': 'booking_id_1', 'ui_status': 'returned'},
        {'booking_id': 'booking_id_2', 'ui_status': 'pickuped'},
    ]


async def test_pickup_retry(pgsql, mockserver, taxi_scooters_ops):
    db_utils.add_mission(pgsql, MISSION_1)

    @mockserver.json_handler(PROCESS_PICKUP_ACCUMULATORS_HANDLER)
    async def _accumulator_taken_processed(request):
        return {
            'booking_id': 'booking_id_1',
            'cell_id': '413',
            'status': 'PROCESSED',
        }

    request_params = {
        'mission_id': 'mission_id_1',
        'point_id': 'point_id_depot_1',
        'job_id': 'job_id_depot_1',
        'accumulator_id': 'acc_1',
    }

    response1 = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, params=request_params,
    )
    response2 = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, params=request_params,
    )

    assert response1.status == 200
    assert response2.status == 200
    assert _accumulator_taken_processed.times_called == 1


async def test_return_retry(pgsql, mockserver, taxi_scooters_ops):
    db_utils.add_mission(pgsql, MISSION_2)

    @mockserver.json_handler(PROCESS_RETURN_ACCUMULATORS_HANDLER)
    async def _accumulator_return_processed(request):
        return {
            'booking_id': 'booking_id_1',
            'cell_id': '413',
            'status': 'PROCESSED',
        }

    request_params = {
        'mission_id': 'mission_id_2',
        'point_id': 'return_point_1',
        'job_id': 'return_job_1',
        'accumulator_id': 'acc_1',
    }

    response1 = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, params=request_params,
    )
    response2 = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, params=request_params,
    )

    assert response1.status == 200
    assert response2.status == 200
    assert _accumulator_return_processed.times_called == 1


@pytest.mark.parametrize(
    'accumulators_error_code',
    [
        pytest.param('no_bookings_were_found'),
        pytest.param('accumulator_id_was_not_found'),
        pytest.param('processed_error'),
    ],
)
@common.TRANSLATIONS
async def test_scooter_accumulator_failed_on_pickup(
        pgsql, mockserver, taxi_scooters_ops, accumulators_error_code,
):
    db_utils.add_mission(pgsql, MISSION_1)

    accumulators_error_code = 'no_bookings_were_found'

    @mockserver.json_handler(PROCESS_PICKUP_ACCUMULATORS_HANDLER)
    async def _accumulator_taken_processed(request):
        return mockserver.make_response(
            status=400,
            json={'code': accumulators_error_code, 'message': 'error'},
        )

    request_params = {
        'mission_id': 'mission_id_1',
        'point_id': 'point_id_depot_1',
        'job_id': 'job_id_depot_1',
        'accumulator_id': 'acc_1',
    }

    response = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, params=request_params,
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'Ошибка',
        'message': 'Не получилось подтвердить выдачу аккумулятора',
    }
    assert _accumulator_taken_processed.times_called == 1

    job = db_utils.get_jobs(pgsql, ids=['job_id_depot_1'])[0]
    assert _get_accumulators_status(job) == [
        {'accumulator_id': 'acc_1', 'ui_status': 'booked'},
        {'accumulator_id': 'acc_2', 'ui_status': 'booked'},
    ]


@pytest.mark.parametrize(
    'accumulators_error_code',
    [
        pytest.param('no_bookings_were_found'),
        pytest.param('no_bookings_for_return_were_found'),
    ],
)
@common.TRANSLATIONS
async def test_scooter_accumulator_failed_on_return(
        pgsql, mockserver, taxi_scooters_ops, accumulators_error_code,
):
    db_utils.add_mission(pgsql, MISSION_2)

    @mockserver.json_handler(PROCESS_RETURN_ACCUMULATORS_HANDLER)
    async def _accumulator_taken_processed(request):
        return mockserver.make_response(
            status=400,
            json={'code': accumulators_error_code, 'message': 'error'},
        )

    request_params = {
        'mission_id': 'mission_id_2',
        'point_id': 'return_point_1',
        'job_id': 'return_job_1',
        'accumulator_id': 'acc_1',
    }

    response = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, params=request_params,
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'Ошибка',
        'message': 'Не получилось подтвердить сдачу аккумулятора',
    }
    assert _accumulator_taken_processed.times_called == 1

    job = db_utils.get_jobs(pgsql, ids=['return_job_1'])[0]
    assert _get_cells_status(job) == [
        {'booking_id': 'booking_id_1', 'ui_status': 'pickuped'},
        {'booking_id': 'booking_id_2', 'ui_status': 'pickuped'},
    ]


@pytest.mark.parametrize(
    'request_params, expected_message',
    [
        pytest.param(
            {
                'mission_id': 'mission_id_1',
                'point_id': 'point_id_depot_1',
                'job_id': 'job_id_depot_1',
                'accumulator_id': 'acc_unknown',
            },
            'Отсканирован не тот аккумулятор',
            id='unknown accumulator_id',
        ),
        pytest.param(
            {
                'mission_id': 'mission_id_1',
                'point_id': 'point_id_depot_1',
                'job_id': 'job_id_2_depot_1',
                'accumulator_id': 'acc_1',
            },
            'Что-то пошло не так...',
            id='invalid cabinet type on pickup',
        ),
        pytest.param(
            {
                'mission_id': 'mission_id_2',
                'point_id': 'return_point_1',
                'job_id': 'return_job_2',
                'accumulator_id': 'acc_1',
            },
            'Что-то пошло не так...',
            id='invalid cabinet type on return',
        ),
    ],
)
@common.TRANSLATIONS
async def test_wrong_request(
        pgsql, mockserver, taxi_scooters_ops, request_params, expected_message,
):
    db_utils.add_mission(pgsql, MISSION_1)
    db_utils.add_mission(pgsql, MISSION_2)

    @mockserver.json_handler(PROCESS_PICKUP_ACCUMULATORS_HANDLER)
    async def _accumulator_taken_processed(request):
        return {
            'booking_id': 'booking_id_1',
            'cell_id': '413',
            'status': 'PROCESSED',
        }

    response = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, params=request_params,
    )

    assert response.status == 400
    assert response.json() == {'code': 'Ошибка', 'message': expected_message}
    assert _accumulator_taken_processed.times_called == 0
