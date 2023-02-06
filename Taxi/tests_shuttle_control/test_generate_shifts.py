# pylint: disable=C5521, W0621
import datetime

from psycopg2.extras import DateTimeRange
import pytest


from tests_shuttle_control.utils import select_named


class AnyString:
    def __eq__(self, other):
        return isinstance(other, str)


class AnyDatetime:
    def __eq__(self, other):
        return isinstance(other, datetime.datetime)


@pytest.mark.now('2020-05-28T13:40:55')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_shift_generation(taxi_shuttle_control, pgsql):
    assert (
        await taxi_shuttle_control.post(
            '/service/cron', json={'task_name': 'generate-shifts-cron'},
        )
    ).status_code == 200

    rows = select_named(
        """
        SELECT * FROM config.workshifts
        ORDER BY route_name, work_time
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'template_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'workshift_id': AnyString(),
            'route_name': 'route1',
            'work_time': DateTimeRange(
                datetime.datetime(2020, 6, 4, 10, 30),
                datetime.datetime(2020, 6, 4, 14, 0),
                '[]',
            ),
            'schedule': None,
            'created_at': AnyDatetime(),
            'max_simultaneous_subscriptions': 10,
            'in_operation_since': None,
            'deprecated_since': None,
            'personal_goal': None,
            'max_pauses_allowed': 1,
            'pause_duration': datetime.timedelta(minutes=15),
            'simultaneous_pauses_per_shift': 1,
        },
        {
            'template_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
            'workshift_id': AnyString(),
            'route_name': 'route2',
            'work_time': DateTimeRange(
                datetime.datetime(2020, 6, 2, 11, 30),
                datetime.datetime(2020, 6, 2, 12, 0),
                '[]',
            ),
            'schedule': None,
            'created_at': AnyDatetime(),
            'max_simultaneous_subscriptions': 11,
            'in_operation_since': None,
            'deprecated_since': None,
            'personal_goal': '(30,50)',
            'max_pauses_allowed': 10,
            'pause_duration': datetime.timedelta(minutes=15),
            'simultaneous_pauses_per_shift': 5,
        },
        {
            'template_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
            'workshift_id': AnyString(),
            'route_name': 'route2',
            'work_time': DateTimeRange(
                datetime.datetime(2020, 6, 9, 11, 30),
                datetime.datetime(2020, 6, 9, 12, 0),
                '[]',
            ),
            'schedule': None,
            'created_at': AnyDatetime(),
            'max_simultaneous_subscriptions': 11,
            'in_operation_since': None,
            'deprecated_since': None,
            'personal_goal': '(30,50)',
            'max_pauses_allowed': 10,
            'pause_duration': datetime.timedelta(minutes=15),
            'simultaneous_pauses_per_shift': 5,
        },
        {
            'template_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            'workshift_id': AnyString(),
            'route_name': 'route3',
            'work_time': DateTimeRange(
                datetime.datetime(2020, 6, 6, 12, 30),
                datetime.datetime(2020, 6, 6, 13, 0),
                '[]',
            ),
            'schedule': None,
            'created_at': AnyDatetime(),
            'max_simultaneous_subscriptions': 12,
            'in_operation_since': None,
            'deprecated_since': None,
            'personal_goal': None,
            'max_pauses_allowed': 1,
            'pause_duration': datetime.timedelta(minutes=30),
            'simultaneous_pauses_per_shift': 2,
        },
    ]
