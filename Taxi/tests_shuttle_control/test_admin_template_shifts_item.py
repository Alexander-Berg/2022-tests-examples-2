# pylint: disable=import-only-modules, import-error, redefined-outer-name
# pylint: disable=len-as-condition
import datetime

import pytest

from tests_shuttle_control.utils import select_named


@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'template_id, request_update, response_code',
    [
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730779', {}, 200),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730779',
            {
                'pause_settings': {
                    'max_pauses_allowed': 1,
                    'pause_duration': 0,
                    'simultaneous_pauses_per_shift': 2,
                },
            },
            400,
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730779',
            {
                'pause_settings': {
                    'max_pauses_allowed': 2,
                    'pause_duration': 60 * 15,
                    'simultaneous_pauses_per_shift': 0,
                },
            },
            400,
        ),
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730777', {}, 500),
    ],
)
@pytest.mark.parametrize('is_check', [False, True])
async def test_put_new(
        taxi_shuttle_control,
        pgsql,
        template_id,
        request_update,
        response_code,
        is_check,
):
    uri = '/admin/shuttle-control/v1/template-shifts/item'
    if is_check:
        uri = uri + '/check'

    request = {
        'new_template_shift_id': template_id,
        'route_name': 'route2',
        'schedule': {
            'timezone': 'Europe/Moscow',
            'intervals': [
                {'exclude': False, 'day': [1, 2]},
                {
                    'exclude': False,
                    'daytime': [{'from': '10:30:00', 'to': '14:00:00'}],
                },
            ],
        },
        'in_operation_since': '2020-01-01T19:17:38+0000',
        'max_simultaneous_subscriptions': 20,
        'personal_goal': {'trips_target': 20, 'payout_amount': 30},
        'pause_settings': {
            'max_pauses_allowed': 1,
            'pause_duration': 15,
            'simultaneous_pauses_per_shift': 2,
        },
    }
    if request_update:
        request.update(request_update)

    response = await taxi_shuttle_control.put(uri, json=request)
    assert response.status_code == response_code
    rows = select_named(
        f'SELECT * FROM config.workshift_templates '
        f'WHERE template_id = \'{template_id}\'::UUID',
        pgsql['shuttle_control'],
    )

    if response_code == 200:
        assert rows == (
            []
            if is_check
            else [
                {
                    'template_id': template_id,
                    'route_name': 'route2',
                    'schedule': {
                        'timezone': 'Europe/Moscow',
                        'intervals': [
                            {'exclude': False, 'day': [1, 2]},
                            {
                                'exclude': False,
                                'daytime': [
                                    {'from': '10:30:00', 'to': '14:00:00'},
                                ],
                            },
                        ],
                    },
                    'in_operation_since': datetime.datetime(
                        2020, 1, 1, 19, 17, 38,
                    ),
                    'deprecated_since': None,
                    'max_simultaneous_subscriptions': 20,
                    'personal_goal': '(20,30)',
                    'max_pauses_allowed': 1,
                    'pause_duration': datetime.timedelta(minutes=15),
                    'simultaneous_pauses_per_shift': 2,
                    'generated_up_to': None,
                },
            ]
        )
    elif response_code == 400:
        assert rows == []
    else:
        assert len(rows) == 1


@pytest.mark.now('2020-01-01T18:17:38+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'replaced_template_id, deprecated_since, response_code',
    [
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730779',
            '2020-01-01T19:17:38+0000',
            404,
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            '2020-01-16T15:17:38+0000',
            400,
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            '2020-01-17T15:17:38+0000',
            200,
        ),
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730777', None, 200),
    ],
)
@pytest.mark.parametrize('is_check', [False, True])
@pytest.mark.parametrize(
    'from_time',
    ['2020-05-28T10:40:00+0000', '2020-05-28T10:40:55.209743+0000'],
    ids=('`new workshift`', '`old workshift`'),
)
async def test_put_replaced(
        taxi_shuttle_control,
        pgsql,
        replaced_template_id,
        deprecated_since,
        response_code,
        from_time,
        is_check,
):
    uri = '/admin/shuttle-control/v1/template-shifts/item'
    if is_check:
        uri = uri + '/check'

    pgsql['shuttle_control'].cursor().execute(
        f"""
        UPDATE config.workshift_templates
        SET in_operation_since = \'{from_time}\'::timestamp
        WHERE template_id = \'2fef68c9-25d0-4174-9dd0-bdd1b3730779\'::UUID
        """,
    )

    response = await taxi_shuttle_control.put(
        uri,
        json={
            'new_template_shift_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730779',
            'replaced_shift_id': replaced_template_id,
            'route_name': 'route2',
            'schedule': {
                'timezone': 'Europe/Moscow',
                'intervals': [
                    {'exclude': False, 'day': [1, 2]},
                    {
                        'exclude': False,
                        'daytime': [{'from': '10:30:00', 'to': '14:00:00'}],
                    },
                ],
            },
            'in_operation_since': '2020-05-28T10:40:00+0000',
            'deprecated_since': deprecated_since,
            'max_simultaneous_subscriptions': 20,
            'personal_goal': {'trips_target': 20, 'payout_amount': 30},
        },
    )
    assert response.status_code == response_code
    rows = select_named(
        'SELECT * FROM config.workshift_templates '
        'WHERE template_id = \'2fef68c9-25d0-4174-9dd0-bdd1b3730779\'::UUID',
        pgsql['shuttle_control'],
    )

    if response_code == 200 and not is_check:
        replaced_deprecated_since = datetime.datetime(2020, 1, 16, 16, 0, 1)

        if deprecated_since is None:
            new_deprecated_since = None
        else:
            new_deprecated_since = datetime.datetime(2020, 1, 17, 15, 17, 38)

        assert rows == [
            {
                'template_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730779',
                'route_name': 'route2',
                'schedule': {
                    'timezone': 'Europe/Moscow',
                    'intervals': [
                        {'exclude': False, 'day': [1, 2]},
                        {
                            'exclude': False,
                            'daytime': [
                                {'from': '10:30:00', 'to': '14:00:00'},
                            ],
                        },
                    ],
                },
                'in_operation_since': replaced_deprecated_since,
                'deprecated_since': new_deprecated_since,
                'max_simultaneous_subscriptions': 20,
                'personal_goal': '(20,30)',
                'max_pauses_allowed': 0,
                'pause_duration': datetime.timedelta(0),
                'simultaneous_pauses_per_shift': 0,
                'generated_up_to': None,
            },
        ]

        rows = select_named(
            'SELECT * FROM config.workshift_templates '
            'WHERE template_id = '
            '\'2fef68c9-25d0-4174-9dd0-bdd1b3730777\'::UUID',
            pgsql['shuttle_control'],
        )
        assert rows == [
            {
                'template_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
                'route_name': 'route1',
                'schedule': {
                    'timezone': 'UTC',
                    'intervals': [
                        {'exclude': False, 'day': [5, 6, 7]},
                        {
                            'exclude': False,
                            'daytime': [
                                {'from': '10:30:00', 'to': '14:00:00'},
                            ],
                        },
                    ],
                },
                'in_operation_since': datetime.datetime(
                    2020, 5, 28, 10, 40, 55,
                ),
                'deprecated_since': replaced_deprecated_since,
                'max_simultaneous_subscriptions': 11,
                'personal_goal': '(30,50)',
                'max_pauses_allowed': 0,
                'pause_duration': datetime.timedelta(0),
                'simultaneous_pauses_per_shift': 0,
                'generated_up_to': None,
            },
        ]

        rows = select_named(
            'SELECT workshift_id FROM config.workshifts '
            'WHERE template_id = '
            '\'2fef68c9-25d0-4174-9dd0-bdd1b3730777\'::UUID '
            'ORDER BY workshift_id',
            pgsql['shuttle_control'],
        )
        assert rows == [
            {'workshift_id': '427a330d-2506-464a-accf-346b31e288b6'},
            {'workshift_id': '427a330d-2506-464a-accf-346b31e288c1'},
        ]

    else:
        assert len(rows) == 0


@pytest.mark.now('2020-01-01T18:17:38+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'template_id, response_code',
    [
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730775', 200),
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730777', 400),
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730779', 404),
    ],
)
@pytest.mark.parametrize('is_check', [False, True])
async def test_delete(
        taxi_shuttle_control, pgsql, template_id, response_code, is_check,
):
    uri = '/admin/shuttle-control/v1/template-shifts/item'
    if is_check:
        uri = uri + '/check'

    response = await taxi_shuttle_control.delete(
        uri, params={'template_shift_id': template_id},
    )
    assert response.status_code == response_code

    if response_code == 200 and not is_check:
        rows = select_named(
            'SELECT * FROM config.workshift_templates',
            pgsql['shuttle_control'],
        )
        assert len(rows) == 1
        assert rows[0]['template_id'] == '2fef68c9-25d0-4174-9dd0-bdd1b3730777'

        rows = select_named(
            'SELECT template_id FROM config.workshifts',
            pgsql['shuttle_control'],
        )
        assert rows == [
            {'template_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730777'},
            {'template_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730777'},
            {'template_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730777'},
        ]

        rows = select_named(
            'SELECT workshift_id FROM state.drivers_workshifts_subscriptions '
            'ORDER BY workshift_id',
            pgsql['shuttle_control'],
        )
        assert rows == [
            {'workshift_id': '427a330d-2506-464a-accf-346b31e288b6'},
            {'workshift_id': '427a330d-2506-464a-accf-346b31e288c1'},
        ]
    else:
        rows = select_named(
            'SELECT * FROM config.workshift_templates',
            pgsql['shuttle_control'],
        )
        assert len(rows) == 2
