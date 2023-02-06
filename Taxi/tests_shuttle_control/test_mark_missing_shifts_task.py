# pylint: disable=import-only-modules
import pytest

from tests_shuttle_control.utils import select_named


@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'result',
    (
        pytest.param(
            'planned', marks=[pytest.mark.now('2020-06-04T14:15:00+0300')],
        ),  # MSK time here
        pytest.param(
            'planned', marks=[pytest.mark.now('2020-06-04T14:40:00+0300')],
        ),  # MSK time here
        pytest.param(
            'missed', marks=[pytest.mark.now('2020-06-04T17:01:00+0300')],
        ),  # MSK time here
    ),
)
async def test_mark_missing_shifts(
        taxi_shuttle_control, experiments3, pgsql, result,
):
    experiments3.add_config(
        name='shuttle_shift_time_control',
        consumers=['shuttle-control/shift_time_control'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/shift_time_control'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'route_1',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'reservation_available': {
                        'from': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'backward',
                            'time_amount': {'unit': 'hour', 'value': 2},
                        },
                        'to': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'backward',
                            'time_amount': {'unit': 'minute', 'value': 10},
                        },
                    },
                    'start_shift_available': {
                        'from': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'backward',
                            'time_amount': {'unit': 'minute', 'value': 10},
                        },
                        'to': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'forward',
                            'time_amount': {'unit': 'minute', 'value': 30},
                        },
                    },
                    'stop_shift_available': {
                        'from': {
                            'starting_point': 'scheduled_shift_end',
                            'time_direction': 'backward',
                            'time_amount': {'unit': 'minute', 'value': 10},
                        },
                        'to': {
                            'starting_point': 'scheduled_shift_end',
                            'time_direction': 'forward',
                            'time_amount': {'unit': 'hour', 'value': 1000},
                        },
                    },
                    'cancel_reservation_available': {
                        'from': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'backward',
                            'time_amount': {'unit': 'minute', 'value': 30},
                        },
                        'to': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'forward',
                            'time_amount': {'unit': 'minute', 'value': 15},
                        },
                    },
                },
            },
        ],
    )

    response = await taxi_shuttle_control.post(
        'service/cron', json={'task_name': 'mark-missing-shifts-cron'},
    )
    assert response.status_code == 200

    rows = select_named(
        'SELECT status FROM state.drivers_workshifts_subscriptions '
        'ORDER BY subscription_id',
        pgsql['shuttle_control'],
    )
    assert rows == [
        {'status': result},
        {'status': 'finished'},
        {'status': 'ongoing'},
        {'status': result},
        {'status': 'missed'},
    ]
