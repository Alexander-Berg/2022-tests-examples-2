import pytest

from tests_scooters_ops import common
from tests_scooters_ops import db_utils

HANDLER = '/scooters-ops/old-flow/v1/validation/point-visited'


def add_mission(pgsql, cell_statuses):
    cells = []
    for i, status in enumerate(cell_statuses):
        cells.append(
            {
                'booking_id': f'cell_book_id_{i}',
                'cell_id': f'cell_{i}',
                'cabinet_id': 'cab_1',
                'cabinet_type': 'charge_station',
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
                    'status': 'visited',
                    'cargo_point_id': 'cargo_point_id_depot_1',
                    'typed_extra': {},
                    'jobs': [
                        {
                            'status': 'completed',
                            'type': 'pickup_batteries',
                            'typed_extra': {'quantity': 2},
                        },
                    ],
                },
                {
                    'type': 'depot',
                    'status': 'arrived',
                    'cargo_point_id': 'cargo_point_id_depot_2',
                    'typed_extra': {},
                    'jobs': [
                        {
                            'status': 'performing',
                            'type': 'return_batteries',
                            'typed_extra': {'cells': cells},
                        },
                    ],
                },
            ],
        },
    )


@common.TRANSLATIONS
@pytest.mark.parametrize(
    [
        'cell_statuses',
        'scooters_accumulator_response',
        'expected_response',
        'expected_history',
    ],
    [
        pytest.param(
            ['returned', 'returned'],
            {'code': 200, 'json': {}},
            {'code': 200, 'json': {}},
            [{'type': 'job_completed'}, {'type': 'point_completed'}],
            id='test_ok',
        ),
        pytest.param(
            ['pickuped', 'booked'],
            {},
            {
                'code': 400,
                'json': {
                    'code': '400',
                    'message': 'Надо бы все таки вернуть все аккумы',
                },
            },
            [],
            id='test_not_all_batteries_returned',
        ),
        *[
            pytest.param(
                ['returned', 'returned'],
                {'code': 400, 'json': {'code': code, 'booking_id': 'book_0'}},
                {'code': 400, 'json': {'code': '400', 'message': message}},
                [],
                id=code,
            )
            for (code, message) in [
                ('booking_with_accumulator', 'Какая-то ужасная ошибка'),
                ('wrong_booking', 'Какая-то ужасная ошибка'),
                ('cell_is_open', 'Одна из ячеек открыта. Закройте её'),
                (
                    'accumulator_was_not_returned',
                    'Вы не вернули аккум. Верните',
                ),
                (
                    'non_processed_booking',
                    'Надо бы все таки вернуть все аккумы',
                ),
            ]
        ],
    ],
)
async def test_handler(
        taxi_scooters_ops,
        pgsql,
        mockserver,
        cell_statuses,
        scooters_accumulator_response,
        expected_response,
        expected_history,
):
    add_mission(pgsql, cell_statuses)

    @mockserver.json_handler(
        '/scooter-accumulator/scooter-accumulator/v1/'
        'cabinet/accumulator/validate-return',
    )
    async def _validate_booked_taken(request):
        assert sorted(request.query['booking_ids'].split(',')) == [
            f'cell_book_id_{i}' for (i, _) in enumerate(cell_statuses)
        ]
        return mockserver.make_response(
            status=scooters_accumulator_response['code'],
            json=scooters_accumulator_response['json'],
        )

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={
            'locale': 'ru-ru',
            'mission_id': 'mission_id_1',
            'cargo_point_id': 'cargo_point_id_depot_2',
        },
    )

    assert resp.status == expected_response['code']
    assert resp.json() == expected_response['json']

    assert _validate_booked_taken.times_called == (
        1 if scooters_accumulator_response else 0
    )

    history = db_utils.get_history(pgsql, fields=['type'])
    assert history == expected_history
