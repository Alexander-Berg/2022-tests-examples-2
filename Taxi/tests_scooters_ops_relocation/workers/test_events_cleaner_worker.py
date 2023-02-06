import pytest

from tests_scooters_ops_relocation import utils

NOW = '2022-07-10T12:00:00+0300'


@pytest.mark.config(
    SCOOTERS_OPS_RELOCATION_WORKERS_V2={
        'events-cleaner': {
            'enabled': True,
            'period_seconds': 60,
            'deletion_limit': 1000,
            'events_lifetime_seconds': 86400,  # 86400 = 24 * 60 * 60
        },
    },
)
@pytest.mark.parametrize(
    'db_events, expected_events_ids',
    [
        pytest.param(
            [  # db_events
                {
                    'id': 'event1',
                    'type': 'outcome',
                    'occured_at': '2022-07-01T12:00:00+0300',
                    'location': (35, 51),
                },
                {
                    'id': 'event2',
                    'type': 'income',
                    'occured_at': '2022-07-01T11:00:00+0300',
                    'location': (35, 53),
                },
            ],
            [],  # expected_events_ids
            id='delete_all',
        ),
        pytest.param(
            [  # db_events
                {
                    'id': 'event1',
                    'type': 'outcome',
                    'occured_at': '2022-07-01T12:00:00+0300',
                    'location': (35, 51),
                },
                {
                    'id': 'event2',
                    'type': 'income',
                    'occured_at': '2022-07-10T10:00:00+0300',
                    'location': (35, 53),
                },
            ],
            ['event1', 'event2'],  # expected_events_ids
            marks=[
                pytest.mark.config(
                    SCOOTERS_OPS_RELOCATION_WORKERS_V2={
                        'events-cleaner': {
                            'enabled': False,
                            'period_seconds': 60,
                            'deletion_limit': 1000,
                            'events_lifetime_seconds': (
                                86400  # 86400 = 24 * 60 * 60
                            ),
                        },
                    },
                ),
            ],
            id='disabled_worker_no_deletion',
        ),
        pytest.param(
            [  # db_events
                {
                    'id': 'event1',
                    'type': 'outcome',
                    'occured_at': '2022-07-01T12:00:00+0300',
                    'location': (35, 51),
                },  # outdated
                {
                    'id': 'event2',
                    'type': 'income',
                    'occured_at': '2022-07-10T11:00:00+0300',
                    'location': (35, 53),
                },  # actual
                {
                    'id': 'event3',
                    'type': 'outcome',
                    'occured_at': '2022-07-09T12:00:00+0300',
                    'location': (35, 51),
                },  # actual
                {
                    'id': 'event4',
                    'type': 'income',
                    'occured_at': '2022-07-09T11:59:59+0300',
                    'location': (35, 53),
                },  # outdated
            ],
            ['event2', 'event3'],  # expected_events_ids
            id='only_outdated_deletion',
        ),
        pytest.param(
            [  # db_events
                {
                    'id': 'event1',
                    'type': 'outcome',
                    'occured_at': '2022-07-01T12:00:00+0300',
                    'location': (35, 51),
                },  # outdated
                {
                    'id': 'event2',
                    'type': 'income',
                    'occured_at': '2022-07-10T11:00:00+0300',
                    'location': (35, 53),
                },  # actual
                {
                    'id': 'event3',
                    'type': 'outcome',
                    'occured_at': '2022-07-09T12:00:00+0300',
                    'location': (35, 51),
                },  # actual
                {
                    'id': 'event4',
                    'type': 'income',
                    'occured_at': '2022-07-09T11:59:59+0300',
                    'location': (35, 53),
                },  # outdated
                {
                    'id': 'event5',
                    'type': 'income',
                    'occured_at': '2022-07-09T11:59:58+0300',
                    'location': (35, 53),
                },  # outdated
            ],
            ['event2', 'event3', 'event5'],  # expected_events_ids
            marks=[
                pytest.mark.config(
                    SCOOTERS_OPS_RELOCATION_WORKERS_V2={
                        'events-cleaner': {
                            'enabled': True,
                            'period_seconds': 60,
                            'deletion_limit': 2,
                            'events_lifetime_seconds': (
                                86400  # 86400 = 24 * 60 * 60
                            ),
                        },
                    },
                ),
            ],
            id='deletion_limit',
        ),
    ],
)
@pytest.mark.now(NOW)
async def test_check_deletion_correctness(
        taxi_scooters_ops_relocation,
        pgsql,
        testpoint,
        stq,
        db_events,
        expected_events_ids,
):
    def _flatten_events_id(events: list) -> list:
        return [event['id'] for event in events]

    for event in db_events:
        utils.add_event(pgsql, event)

    await taxi_scooters_ops_relocation.run_task('testsuite-events-cleaner')

    events_ids = _flatten_events_id(utils.get_events(pgsql))
    events_ids.sort()
    expected_events_ids.sort()

    assert events_ids == expected_events_ids
