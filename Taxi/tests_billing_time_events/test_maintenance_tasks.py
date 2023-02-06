import pytest

# pylint: disable=import-error,wildcard-import
from billing_time_events_plugins.generated_tests import *  # noqa

_FETCH_TABLE_PARTITIONS_SQL = """
        SELECT inhrelid::regclass AS child
        FROM   pg_catalog.pg_inherits
        WHERE  inhparent = 'bte.{}'::regclass;
"""


@pytest.mark.config(
    BILLING_TIME_EVENTS_EVENTS_MAINTENANCE_SETTINGS={
        'enabled': True,
        'partition-range-duration-hours': 1,
        'partitions-in-future-hours': 3,
        'partitions-in-past-hours': 1,
    },
)
@pytest.mark.parametrize(
    'expected_partitions_per_shard',
    [
        pytest.param(
            {
                'events_0': [
                    ('bte.events_0_default',),
                    ('bte.events_0_2020_070114_2020_070115',),
                    ('bte.events_0_2020_070115_2020_070116',),
                    ('bte.events_0_2020_070116_2020_070117',),
                    ('bte.events_0_2020_070117_2020_070118',),
                ],
                'events_1': [
                    ('bte.events_1_default',),
                    ('bte.events_1_2020_070114_2020_070115',),
                    ('bte.events_1_2020_070115_2020_070116',),
                    ('bte.events_1_2020_070116_2020_070117',),
                    ('bte.events_1_2020_070117_2020_070118',),
                ],
            },
            marks=[
                pytest.mark.now('2020-07-01T15:00:06+00:00'),
                pytest.mark.pgsql(
                    'billing_time_events@0',
                    files=[
                        'pg_drop_events_partitions.sql',
                        'pg_events_maintenance.sql',
                    ],
                ),
            ],
            id='default',
        ),
        # existing partitions in the past
        pytest.param(
            {
                'events_0': [
                    ('bte.events_0_default',),
                    ('bte.events_0_2020_070117_2020_070118',),
                    ('bte.events_0_2020_070118_2020_070119',),
                    ('bte.events_0_2020_070119_2020_070120',),
                    ('bte.events_0_2020_070120_2020_070121',),
                ],
                'events_1': [
                    ('bte.events_1_default',),
                    ('bte.events_1_2020_070117_2020_070118',),
                    ('bte.events_1_2020_070118_2020_070119',),
                    ('bte.events_1_2020_070119_2020_070120',),
                    ('bte.events_1_2020_070120_2020_070121',),
                ],
            },
            marks=[
                pytest.mark.now('2020-07-01T18:00:06+00:00'),
                pytest.mark.pgsql(
                    'billing_time_events@0',
                    files=[
                        'pg_drop_events_partitions.sql',
                        'pg_events_maintenance.sql',
                    ],
                ),
            ],
            id='partitions in the past',
        ),
        pytest.param(
            {
                'events_0': [
                    ('bte.events_0_default',),
                    ('bte.events_0_2020_070115_2020_070116',),
                    ('bte.events_0_2020_070116_2020_070117',),
                    ('bte.events_0_2020_070117_2020_070118',),
                ],
                'events_1': [
                    ('bte.events_1_default',),
                    ('bte.events_1_2020_070115_2020_070116',),
                    ('bte.events_1_2020_070116_2020_070117',),
                    ('bte.events_1_2020_070117_2020_070118',),
                ],
            },
            marks=[
                pytest.mark.now('2020-07-01T15:00:06+00:00'),
                pytest.mark.pgsql(
                    'billing_time_events@0',
                    files=['pg_drop_events_partitions.sql'],
                ),
            ],
            id='no partitions, create only future',
        ),
    ],
)
async def test_events_maintenance(
        expected_partitions_per_shard, *, taxi_billing_time_events, pgsql,
):
    await taxi_billing_time_events.run_distlock_task('events-maintenance-0')
    cursor = pgsql['billing_time_events@0'].cursor()
    for table in ('events_0', 'events_1'):
        cursor.execute(_FETCH_TABLE_PARTITIONS_SQL.format(table))
        assert list(cursor) == expected_partitions_per_shard[table]


@pytest.mark.config(
    BILLING_TIME_EVENTS_PAYLOADS_MAINTENANCE_SETTINGS={
        'enabled': True,
        'partition-range-duration-hours': 1,
        'partitions-in-future-hours': 3,
        'partitions-in-past-hours': 1,
    },
)
@pytest.mark.parametrize(
    'expected_partitions',
    [
        pytest.param(
            [
                ('bte.payloads_default',),
                ('bte.payloads_2020_070114_2020_070115',),
                ('bte.payloads_2020_070115_2020_070116',),
                ('bte.payloads_2020_070116_2020_070117',),
                ('bte.payloads_2020_070117_2020_070118',),
            ],
            marks=[
                pytest.mark.now('2020-07-01T15:00:06+00:00'),
                pytest.mark.pgsql(
                    'billing_time_events@0',
                    files=[
                        'pg_drop_payloads_partitions.sql',
                        'pg_payloads_maintenance.sql',
                    ],
                ),
            ],
            id='default',
        ),
        pytest.param(
            [
                ('bte.payloads_default',),
                ('bte.payloads_2020_070115_2020_070116',),
                ('bte.payloads_2020_070116_2020_070117',),
                ('bte.payloads_2020_070117_2020_070118',),
                ('bte.payloads_2020_070118_2020_070119',),
            ],
            marks=[
                pytest.mark.now('2020-07-01T16:00:06+00:00'),
                pytest.mark.pgsql(
                    'billing_time_events@0',
                    files=[
                        'pg_drop_payloads_partitions.sql',
                        'pg_payloads_maintenance.sql',
                    ],
                ),
            ],
            id='existing partitions in the past',
        ),
        pytest.param(
            [
                ('bte.payloads_default',),
                ('bte.payloads_2020_070115_2020_070116',),
                ('bte.payloads_2020_070116_2020_070117',),
                ('bte.payloads_2020_070117_2020_070118',),
            ],
            marks=[
                pytest.mark.now('2020-07-01T15:00:00+00:00'),
                pytest.mark.pgsql(
                    'billing_time_events@0',
                    files=['pg_drop_payloads_partitions.sql'],
                ),
            ],
            id='no partitions, create only future',
        ),
    ],
)
async def test_payloads_maintenance(
        expected_partitions, *, taxi_billing_time_events, pgsql,
):
    await taxi_billing_time_events.run_distlock_task('payloads-maintenance-0')
    cursor = pgsql['billing_time_events@0'].cursor()
    cursor.execute(_FETCH_TABLE_PARTITIONS_SQL.format('payloads'))
    assert list(cursor) == expected_partitions
