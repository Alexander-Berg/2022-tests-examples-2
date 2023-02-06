import datetime

import pytest

from tests_driver_metrics_storage import util

# XXX: this set of tests implements unit-testing due to have no possibilities
# to implement them using utests


def get_selectable_partitions(
        pgsql, table_schema, table_name, only_names=True,
):
    result = util.select_named(
        """
            SELECT
                nmsp_parent.nspname        AS table_schema,
                child.relname              AS table_name,
                child.relispartition       AS is_partition
            FROM pg_inherits
                JOIN pg_class parent
                  ON pg_inherits.inhparent = parent.oid
                JOIN pg_class child
                  ON pg_inherits.inhrelid   = child.oid
                JOIN pg_namespace nmsp_parent
                  ON nmsp_parent.oid  = parent.relnamespace
            LEFT JOIN common.range_partitions_metadata as meta
              ON table_schema=nmsp_parent.nspname AND table_name=child.relname
            WHERE nmsp_parent.nspname='{}' AND parent.relname='{}'
              AND meta.state = 'ready'::PartitionState
            ORDER BY child.relname;
        """.format(
            table_schema, table_name,
        ),
        pgsql,
    )
    if only_names:
        return [row['table_name'] for row in result]
    return result


def get_known_partitions(pgsql, table_schema, table_name, only_names=True):
    result = util.select_named(
        """
            SELECT * FROM common.range_partitions_metadata
            WHERE origin_table_schema='{}' AND origin_table_name='{}'
            ORDER BY table_name;
        """.format(
            table_schema, table_name,
        ),
        pgsql,
    )
    if only_names:
        return [row['table_name'] for row in result]
    return result


def aggregated_data(pgsql, since, until):
    return util.select_named(
        f"""
                select
                    udid_id,
                    sum(loyalty_summary) as loyalty_summary,
                    sum(records_count) as records_count,
                    min(since) as since,
                    max(until) as until
                from data.logs_64_loyalty_daily_aggregated
                where since >= '{since}'
                  and until < '{until}'
                group by udid_id;
            """,
        pgsql,
    )


def origin_data(pgsql, since, until):
    return util.select_named(
        f"""
            select
                udid_id,
                sum(loyalty_increment) as loyalty_summary,
                count(*) as records_count,
                min(created) as since,
                max(created) as until
            from data.logs_64_partitioned
            where created >= '{since}'
              and created < '{until}'
            group by udid_id;
        """,
        pgsql,
    )


def datetime_floor(time_to_floor, delta):
    floor = (
        datetime.datetime.combine(datetime.date.min, time_to_floor.time())
        - datetime.datetime.min
    ).total_seconds() % delta.total_seconds()
    return time_to_floor - datetime.timedelta(seconds=floor)


def gen_table_names(prefix, since, until, delta):
    tzone = datetime.timezone
    if since.replace(tzinfo=tzone.utc) >= until.replace(tzinfo=tzone.utc):
        return []

    floor_since = datetime_floor(since, delta)
    count = int(
        abs(
            until.replace(tzinfo=tzone.utc)
            - floor_since.replace(tzinfo=tzone.utc),
        ).total_seconds()
        / delta.total_seconds(),
    )

    names = []
    for offset in range(count):
        since_cur = floor_since + offset * delta
        names.append(
            '{}_{}_{}'.format(
                prefix,
                since_cur.strftime('%Y%m%d%H%M%S'),
                (since_cur + delta).strftime('%Y%m%d%H%M%S'),
            ),
        )
    return names


class PartitionsChecker:
    def __init__(self, pgsql, table_schema, table_name):
        self._pgsql = pgsql
        self._table_schema = table_schema
        self._table_name = table_name

    def get_selectable(self):
        return get_selectable_partitions(
            self._pgsql, self._table_schema, self._table_name,
        )

    def get_known(self):
        return get_known_partitions(
            self._pgsql, self._table_schema, self._table_name,
        )


HOURLY_CHUNKS_TO_FILL = 5
DAILY_CHUNKS_TO_FILL = int(24 / 3)  # 3 hours per aggregator shot


class TimeMachine:
    def __init__(self, mocked_time, service, testpoint_callback):
        self._mocked_time = mocked_time
        self._service = service
        self._testpoint = testpoint_callback

    async def eval_periodic_task(self):
        await self._service.run_task('dist-loyalty-aggregator')
        await self._testpoint.wait_call()

    async def shift_until_next_hour(self):
        now = self._mocked_time.now()
        self._mocked_time.set(now + datetime.timedelta(hours=1))
        await self._service.invalidate_caches()

    async def fill_until_next_hour(self, fill_daily=False):
        await self.shift_until_next_hour()
        for _ in range(HOURLY_CHUNKS_TO_FILL):
            await self.eval_periodic_task()
        if fill_daily and self._mocked_time.now().hour == 2:
            for _ in range(DAILY_CHUNKS_TO_FILL):
                await self.eval_periodic_task()

    async def fill_until_next_day(self, trim_hours=False):
        target = self._mocked_time.now() + datetime.timedelta(days=1)
        time_it = self._mocked_time.now()
        while time_it < target:
            time_it += datetime.timedelta(hours=1)
            await self.shift_until_next_hour()
            for _ in range(HOURLY_CHUNKS_TO_FILL):
                await self.eval_periodic_task()
            if (
                    trim_hours
                    and time_it.day == target.day
                    and self._mocked_time.now().hour == 0
            ):
                break
            if self._mocked_time.now().hour == 2:
                for _ in range(DAILY_CHUNKS_TO_FILL):
                    await self.eval_periodic_task()


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_AGGREGATOR_SETTINGS={
        'is_aggregation_enabled': True,
        'is_selection_enabled': False,
        'fetch_partitions_period_sec': 1,
        'partitions': {
            'data.logs_64_loyalty_hourly_aggregated': {
                'deprecation_after_mins': 60 * 28,  # day + 4 hours
                'erasure_after_mins': 60 * 29,  # day + 5 hours
            },
            'data.logs_64_loyalty_daily_aggregated': {
                'deprecation_after_mins': 60 * 24 * 40,  # 40 days
                'erasure_after_mins': 60 * 24 * 40 + 60 * 24,  # 41 day
            },
        },
        'aggregators': {
            'data.logs_64_loyalty_hourly_aggregated': {
                'initial_partition_offset': '1hour',
                'data_aggregation_period': '15min',
            },
            'data.logs_64_loyalty_daily_aggregated': {
                'initial_partition_offset': '1hour',
                'data_aggregation_period': '2hours',
            },
        },
    },
)
@pytest.mark.now('2021-12-22T12:00:03+0000')
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
async def test_wallet_aggregators_first_fill(
        taxi_driver_metrics_storage,
        testpoint,
        pgsql,
        clear_range_partitions,
        mocked_time,
):
    initial_datetime = mocked_time.now() - datetime.timedelta(hours=2)

    @testpoint('periodic::dist-loyalty-aggregator')
    def testpoint_callback(data):
        pass

    time_machine = TimeMachine(
        mocked_time, taxi_driver_metrics_storage, testpoint_callback,
    )
    hourly_partitions = PartitionsChecker(
        pgsql, 'data', 'logs_64_loyalty_hourly_aggregated',
    )
    daily_partitions = PartitionsChecker(
        pgsql, 'data', 'logs_64_loyalty_daily_aggregated',
    )

    # Make first shot of hourly aggregator for initial
    # anchoring aggregation sequence
    await time_machine.eval_periodic_task()
    # Current hourly partition still in state
    assert hourly_partitions.get_selectable() == []
    assert hourly_partitions.get_known() == [
        'logs_64_loyalty_hourly_aggregated_20211222100000_20211222110000',
    ]
    for _ in range(HOURLY_CHUNKS_TO_FILL):
        await time_machine.eval_periodic_task()
    assert hourly_partitions.get_selectable() == [
        'logs_64_loyalty_hourly_aggregated_20211222100000_20211222110000',
    ]
    assert hourly_partitions.get_known() == [
        'logs_64_loyalty_hourly_aggregated_20211222100000_20211222110000',
    ]

    # Check that nothing will change in idle cases
    mocked_time.sleep(10)
    await taxi_driver_metrics_storage.invalidate_caches()
    for _ in range(3):
        await time_machine.eval_periodic_task()
    assert hourly_partitions.get_selectable() == [
        'logs_64_loyalty_hourly_aggregated_20211222100000_20211222110000',
    ]
    assert hourly_partitions.get_known() == [
        'logs_64_loyalty_hourly_aggregated_20211222100000_20211222110000',
    ]

    await time_machine.fill_until_next_hour()
    assert hourly_partitions.get_selectable() == [
        'logs_64_loyalty_hourly_aggregated_20211222100000_20211222110000',
        'logs_64_loyalty_hourly_aggregated_20211222110000_20211222120000',
    ]

    # roll forward for a few hours after deprecation
    await time_machine.fill_until_next_day(trim_hours=True)
    await time_machine.fill_until_next_hour()
    assert hourly_partitions.get_selectable() == gen_table_names(
        'logs_64_loyalty_hourly_aggregated',
        initial_datetime,
        datetime.datetime(2021, 12, 23, 0, 0, 0, tzinfo=datetime.timezone.utc),
        datetime.timedelta(hours=1),
    )
    assert hourly_partitions.get_known() == gen_table_names(
        'logs_64_loyalty_hourly_aggregated',
        initial_datetime,
        datetime.datetime(2021, 12, 23, 0, 0, 0, tzinfo=datetime.timezone.utc),
        datetime.timedelta(hours=1),
    )

    await time_machine.eval_periodic_task()

    # First daily aggregation is skipped due to incomplete filling
    assert daily_partitions.get_known() == []

    await time_machine.fill_until_next_hour()
    assert hourly_partitions.get_selectable() == gen_table_names(
        'logs_64_loyalty_hourly_aggregated',
        initial_datetime,
        datetime.datetime(2021, 12, 23, 1, 0, 0, tzinfo=datetime.timezone.utc),
        datetime.timedelta(hours=1),
    )
    assert hourly_partitions.get_known() == gen_table_names(
        'logs_64_loyalty_hourly_aggregated',
        initial_datetime,
        datetime.datetime(2021, 12, 23, 1, 0, 0, tzinfo=datetime.timezone.utc),
        datetime.timedelta(hours=1),
    )

    # Keep sequentially daily aggregation from first filled day
    for _ in range(2):
        await time_machine.eval_periodic_task()
    for _ in range(DAILY_CHUNKS_TO_FILL):
        await time_machine.eval_periodic_task()

    # Check first-time daily aggregator did not created due to
    # incomplete hourly aggregated data
    await time_machine.fill_until_next_day(trim_hours=True)
    for _ in range(2):
        await time_machine.fill_until_next_hour()
    for _ in range(DAILY_CHUNKS_TO_FILL):
        await time_machine.eval_periodic_task()

    assert daily_partitions.get_known() == gen_table_names(
        'logs_64_loyalty_daily_aggregated',
        mocked_time.now() - datetime.timedelta(days=1),
        mocked_time.now(),
        datetime.timedelta(days=1),
    )

    # there is few partitions from incomplete first-day left
    for _ in range(2):
        await time_machine.fill_until_next_hour()
    await time_machine.eval_periodic_task()
    await time_machine.eval_periodic_task()
    await time_machine.eval_periodic_task()
    assert hourly_partitions.get_selectable() == gen_table_names(
        'logs_64_loyalty_hourly_aggregated',
        datetime.datetime(2021, 12, 24, 0, 0, 0, tzinfo=datetime.timezone.utc),
        mocked_time.now() - datetime.timedelta(hours=1),
        datetime.timedelta(hours=1),
    )
    assert hourly_partitions.get_known() == gen_table_names(
        'logs_64_loyalty_hourly_aggregated',
        datetime.datetime(2021, 12, 23, 0, 0, 0, tzinfo=datetime.timezone.utc),
        mocked_time.now() - datetime.timedelta(hours=1),
        datetime.timedelta(hours=1),
    )

    await time_machine.fill_until_next_day(trim_hours=True)
    # Take into account the offset of hourly partition generation
    # shift for a few hours after midnight to start daily aggregation
    for _ in range(2):
        await time_machine.eval_periodic_task()
    for _ in range(DAILY_CHUNKS_TO_FILL):
        await time_machine.eval_periodic_task()

    assert hourly_partitions.get_selectable() == gen_table_names(
        'logs_64_loyalty_hourly_aggregated',
        datetime_floor(
            initial_datetime + datetime.timedelta(days=2),
            datetime.timedelta(days=1),
        ),
        mocked_time.now() - datetime.timedelta(hours=1),
        datetime.timedelta(hours=1),
    )
    assert hourly_partitions.get_known() == gen_table_names(
        'logs_64_loyalty_hourly_aggregated',
        datetime.datetime(2021, 12, 23, 0, 0, 0, tzinfo=datetime.timezone.utc),
        mocked_time.now() - datetime.timedelta(hours=1),
        datetime.timedelta(hours=1),
    )

    assert daily_partitions.get_selectable() == gen_table_names(
        'logs_64_loyalty_daily_aggregated',
        mocked_time.now() - datetime.timedelta(days=2),
        mocked_time.now() - datetime.timedelta(days=1),
        datetime.timedelta(days=1),
    )
    assert daily_partitions.get_known() == gen_table_names(
        'logs_64_loyalty_daily_aggregated',
        mocked_time.now() - datetime.timedelta(days=2),
        mocked_time.now() - datetime.timedelta(days=1),
        datetime.timedelta(days=1),
    )


@pytest.mark.skip(reason='long-play test, disabled for manual run')
@pytest.mark.config(
    DRIVER_METRICS_STORAGE_AGGREGATOR_SETTINGS={
        'is_aggregation_enabled': True,
        'is_selection_enabled': False,
        'fetch_partitions_period_sec': 1,
        'aggregators': {
            'data.logs_64_loyalty_hourly_aggregated': {
                'initial_partition_offset': '1hour',
                'data_aggregation_period': '15min',
            },
            'data.logs_64_loyalty_daily_aggregated': {
                'initial_partition_offset': '1hour',
                'data_aggregation_period': '2hours',
            },
        },
    },
)
@pytest.mark.now('2021-12-22T12:00:03+0000')
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
async def test_wallet_aggregators_long_period(
        taxi_driver_metrics_storage,
        testpoint,
        pgsql,
        clear_range_partitions,
        mocked_time,
):
    @testpoint('periodic::dist-loyalty-aggregator')
    def testpoint_callback(data):
        pass

    time_machine = TimeMachine(
        mocked_time, taxi_driver_metrics_storage, testpoint_callback,
    )
    hourly_partitions = PartitionsChecker(
        pgsql, 'data', 'logs_64_loyalty_hourly_aggregated',
    )
    daily_partitions = PartitionsChecker(
        pgsql, 'data', 'logs_64_loyalty_daily_aggregated',
    )

    # Make first shot of hourly aggregator for initial
    # anchoring aggregation sequence
    for _ in range(HOURLY_CHUNKS_TO_FILL):
        await time_machine.eval_periodic_task()
    await time_machine.fill_until_next_hour()

    tzone = datetime.timezone
    # skip till the end of month
    for day in range(42):
        await time_machine.fill_until_next_day(trim_hours=True)
        for _ in range(3):
            await time_machine.fill_until_next_hour(fill_daily=True)

        # Seek at least one filled daily and skip first incomplete day
        selectable = daily_partitions.get_selectable()
        daily_since = datetime.datetime(2021, 12, 23, 0, 0, 0)
        if daily_since < mocked_time.now() - datetime.timedelta(days=40):
            daily_since = mocked_time.now() - datetime.timedelta(days=40)
        assert selectable == gen_table_names(
            'logs_64_loyalty_daily_aggregated',
            daily_since,
            mocked_time.now(),
            datetime.timedelta(days=1),
        )

        if day < 3:
            continue

        assert (
            hourly_partitions.get_known()[-1:]
            == gen_table_names(
                'logs_64_loyalty_hourly_aggregated',
                mocked_time.now() - datetime.timedelta(hours=2),
                mocked_time.now() - datetime.timedelta(hours=1),
                # datetime.datetime(2021, 12, 23, 0, 0, 0),
                # mocked_time.now(),
                datetime.timedelta(hours=1),
            )[-1:]
        )

        now = mocked_time.now()
        until = datetime.datetime(
            now.year,
            now.month,
            now.day,
            0,
            0,
            0,
            tzinfo=datetime.timezone.utc,
        )
        since = until - datetime.timedelta(days=1)
        assert (
            aggregated_data(
                pgsql,
                since.replace(tzinfo=tzone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                until.replace(tzinfo=tzone.utc).strftime('%Y-%m-%d %H:%M:%S'),
            )
            == origin_data(
                pgsql,
                since.replace(tzinfo=tzone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                until.replace(tzinfo=tzone.utc).strftime('%Y-%m-%d %H:%M:%S'),
            )
        )

    assert aggregated_data(
        pgsql, '2021-12-24 00:00:00', '2022-02-01 00:00:00',
    ) == origin_data(pgsql, '2021-12-24 00:00:00', '2022-02-01 00:00:00')
