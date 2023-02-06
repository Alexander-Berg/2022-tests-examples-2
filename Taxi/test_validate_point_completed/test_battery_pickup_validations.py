import pytest

from tests_scooters_ops import common
from tests_scooters_ops import db_utils
from tests_scooters_ops import utils

HANDLER = '/scooters-ops/old-flow/v1/validation/point-visited'


RETURN_BATTERIES_JOB_WITHOUT_BOOKED_CELLS = {
    'type': 'return_batteries',
    'typed_extra': {'quantity': 2},
}

RETURN_BATTERIES_JOB_WITH_EMTY_BOOKINGS = {
    'type': 'return_batteries',
    'typed_extra': {
        'cells': [
            {'ui_status': 'pending', 'booking_id': utils.AnyValue()},
            {'ui_status': 'pending', 'booking_id': utils.AnyValue()},
        ],
    },
}

RETURN_BATTERIES_JOB_WITH_BOOKED_CELLS = {
    'type': 'return_batteries',
    'typed_extra': {
        'cells': [
            {
                'booking_id': utils.AnyValue(),
                'cabinet_id': 'cab_1',
                'cabinet_type': 'charge_station',
                'cell_id': 'cell_0',
                'ui_status': 'pickuped',
            },
            {
                'booking_id': utils.AnyValue(),
                'cabinet_id': 'cab_1',
                'cabinet_type': 'charge_station',
                'cell_id': 'cell_1',
                'ui_status': 'pickuped',
            },
        ],
    },
}

REBOOKINGS_INFO = {
    'bookings': [
        {
            'booking_id': 'any_value_1',
            'status': 'CREATED',
            'cell_id': 'cell_0',
            'cabinet_id': 'cab_1',
            'cells_count': 1,
            'cabinet_type': 'charge_station',
        },
        {
            'booking_id': 'any_value_2',
            'status': 'CREATED',
            'cell_id': 'cell_1',
            'cabinet_id': 'cab_1',
            'cells_count': 1,
            'cabinet_type': 'charge_station',
        },
    ],
}


def add_mission(pgsql, accumulator_statuses):
    accumulators = []
    for i, status in enumerate(accumulator_statuses):
        accumulators.append(
            {
                'booking_id': f'accumulator_book_id_{i}',
                'cell_id': f'cell_{i}',
                'cabinet_id': 'cab_1',
                'cabinet_type': 'charge_station',
                'accumulator_id': f'accumulator_{i}',
                'ui_status': status,
            },
        )
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_id_1',
            'status': 'performing',
            'points': [
                {
                    'type': 'depot',
                    'status': 'arrived',
                    'cargo_point_id': 'cargo_point_id_depot_1',
                    'typed_extra': {},
                    'jobs': [
                        {
                            'status': 'performing',
                            'type': 'pickup_batteries',
                            'typed_extra': {'accumulators': accumulators},
                        },
                    ],
                },
                {
                    'type': 'depot',
                    'status': 'planned',
                    'cargo_point_id': 'cargo_point_id_depot_2',
                    'typed_extra': {},
                    'jobs': [
                        {
                            'status': 'planned',
                            'type': 'return_batteries',
                            'typed_extra': {'quantity': 2},
                        },
                    ],
                },
            ],
        },
    )


@common.TRANSLATIONS
@pytest.mark.parametrize(
    [
        'accumulator_statuses',
        'scooters_accumulator_response',
        'expected_return_batteries_job',
        'expected_response',
        'expected_history',
    ],
    [
        pytest.param(
            ['pickuped', 'pickuped'],
            {'code': 200, 'json': REBOOKINGS_INFO},
            RETURN_BATTERIES_JOB_WITH_BOOKED_CELLS,
            {'code': 200, 'json': {}},
            [{'type': 'job_completed'}, {'type': 'point_completed'}],
            id='test_ok',
        ),
        pytest.param(
            ['pickuped', 'booked'],
            {},
            RETURN_BATTERIES_JOB_WITHOUT_BOOKED_CELLS,
            {
                'code': 400,
                'json': {
                    'code': '400',
                    'message': 'Надо бы все таки забрать все аккумы',
                },
            },
            [],
            id='test_not_all_batteries_pickuped',
        ),
        *[
            pytest.param(
                ['pickuped', 'pickuped'],
                {'code': 400, 'json': {'code': code, 'booking_id': 'book_0'}},
                RETURN_BATTERIES_JOB_WITH_EMTY_BOOKINGS,
                {'code': 400, 'json': {'code': '400', 'message': message}},
                [],
                id=code,
            )
            for (code, message) in [
                ('booking_without_accumulator', 'Какая-то ужасная ошибка'),
                ('wrong_booking', 'Какая-то ужасная ошибка'),
                ('cell_is_open', 'Одна из ячеек открыта. Закройте её'),
                ('accumulator_was_not_taken', 'Вы не забрали аккум. Заберите'),
                (
                    'non_processed_booking',
                    'Надо бы все таки забрать все аккумы',
                ),
            ]
        ],
    ],
)
async def test_handler(
        taxi_scooters_ops,
        pgsql,
        mockserver,
        accumulator_statuses,
        scooters_accumulator_response,
        expected_return_batteries_job,
        expected_response,
        expected_history,
):
    add_mission(pgsql, accumulator_statuses)

    @mockserver.json_handler(
        '/scooter-accumulator/scooter-accumulator/'
        'v2/cabinet/accumulator/validate-booked-taken',
    )
    async def _validate_booked_taken(request):
        assert sorted(request.json['booking_ids']) == [
            f'accumulator_book_id_{i}'
            for (i, _) in enumerate(accumulator_statuses)
        ]
        assert len(request.json['rebooking_ids']) == 2

        return mockserver.make_response(
            status=scooters_accumulator_response['code'],
            json=scooters_accumulator_response['json'],
        )

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={
            'locale': 'ru-ru',
            'mission_id': 'mission_id_1',
            'cargo_point_id': 'cargo_point_id_depot_1',
        },
    )

    assert resp.status == expected_response['code']
    assert resp.json() == expected_response['json']

    assert _validate_booked_taken.times_called == (
        1 if scooters_accumulator_response else 0
    )

    jobs = db_utils.get_jobs(pgsql, fields=['type', 'typed_extra'])
    return_batteries_jobs = [
        job for job in jobs if job['type'] == 'return_batteries'
    ]
    assert return_batteries_jobs == [expected_return_batteries_job]

    history = db_utils.get_history(pgsql, fields=['type'])
    assert history == expected_history
