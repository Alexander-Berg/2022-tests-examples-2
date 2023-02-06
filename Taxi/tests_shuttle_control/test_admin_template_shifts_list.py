# pylint: disable=import-only-modules, import-error, redefined-outer-name
import pytest


@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'date, include_first',
    [('2000-01-17T18:17:38+0000', True), ('2021-06-28T10:40:55+0000', False)],
)
async def test_main(taxi_shuttle_control, date, include_first):
    response = await taxi_shuttle_control.get(
        '/admin/shuttle-control/v1/template-shifts/list',
        params={
            'route_name': 'route1',
            'date_from': date,
            'date_to': '2050-01-17T18:17:38+0000',
        },
    )
    assert response.status_code == 200
    sorted_response = sorted(response.json(), key=lambda x: x['id'])

    expected_response = [
        {
            'id': '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            'schedule': {
                'timezone': 'UTC',
                'intervals': [
                    {'exclude': False, 'day': [5, 6, 7]},
                    {
                        'exclude': False,
                        'daytime': [{'from': '10:30:00', 'to': '14:00:00'}],
                    },
                ],
            },
            'max_simultaneous_subscriptions': 11,
            'in_operation_since': '2020-05-28T10:40:55+00:00',
            'personal_goal': {'trips_target': 30, 'payout_amount': 50},
            'pause_settings': {
                'max_pauses_allowed': 2,
                'pause_duration': 30,
                'simultaneous_pauses_per_shift': 2,
            },
        },
    ]

    if include_first:
        expected_response.insert(
            0,
            {
                'id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
                'schedule': {
                    'timezone': 'UTC',
                    'intervals': [
                        {'exclude': False, 'day': [4]},
                        {
                            'exclude': False,
                            'daytime': [
                                {'from': '10:30:00', 'to': '14:00:00'},
                            ],
                        },
                    ],
                },
                'max_simultaneous_subscriptions': 10,
                'in_operation_since': '2020-05-28T10:40:55+00:00',
                'deprecated_since': '2021-05-28T10:40:55+00:00',
                'pause_settings': {
                    'max_pauses_allowed': 1,
                    'pause_duration': 15,
                    'simultaneous_pauses_per_shift': 1,
                },
            },
        )

    assert sorted_response == expected_response


@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'route, date_from, date_to',
    [
        ('route1', '2000-06-17T18:17:38+0000', '2002-01-17T18:17:38+0000'),
        ('route2', '2000-06-17T18:17:38+0000', '2050-01-17T18:17:38+0000'),
    ],
)
async def test_no_templates(taxi_shuttle_control, route, date_from, date_to):
    response = await taxi_shuttle_control.get(
        '/admin/shuttle-control/v1/template-shifts/list',
        params={
            'route_name': route,
            'date_from': date_from,
            'date_to': date_to,
        },
    )
    assert response.status_code == 200
    assert response.json() == []
