# pylint: disable=protected-access
import datetime

import pytest


from taxi.util import dates

from replication.targets.yt import partitioning


@pytest.mark.nofilldb
@pytest.mark.now('2019-04-19T12:08:12')
def test_partitioning_info():
    info_daily = partitioning.PartitioningInfo(
        type=partitioning.PartitionType.BY_DAYS.value,
        field_name='data.created',
        items_to_keep=3,
        rotate_policy=partitioning.RotatePolicy.remove,
    )
    assert (
        info_daily.select_table(
            {
                'data': {
                    'created': dates.timestamp_us(
                        datetime.datetime(2019, 4, 18),
                    ),
                },
            },
        )
        == '2019-04-18'
    )
    assert (
        info_daily.select_table(
            {
                'data': {
                    'created': dates.timestamp_us(
                        datetime.datetime(2019, 4, 18, 23, 59),
                    ),
                },
            },
        )
        == '2019-04-18'
    )
    with pytest.raises(partitioning.DocTooOldError):
        info_daily.select_table(
            {
                'data': {
                    'created': dates.timestamp_us(
                        datetime.datetime(2019, 4, 15, 23),
                    ),
                },
            },
        )
    with pytest.raises(partitioning.DocDistantFutureError):
        info_daily.select_table(
            {
                'data': {
                    'created': dates.timestamp_us(
                        datetime.datetime(2019, 4, 21, 23),
                    ),
                },
            },
        )

    with pytest.raises(partitioning.PartitionSelectionError):
        info_daily.select_table({'data': {'created': None}})

    assert info_daily.next_table == '2019-04-20'
    assert info_daily.current_table == '2019-04-19'
    assert info_daily.all_active_tables == [
        '2019-04-19',
        '2019-04-18',
        '2019-04-17',
        '2019-04-16',
    ]
    assert info_daily.last_expired_table == '2019-04-15'


@pytest.mark.nofilldb
@pytest.mark.now('2019-04-19T12:08:12')
def test_partitioning_info_month_slice():
    info_month_slice = partitioning.PartitioningInfo(
        type=partitioning.PartitionType.MONTHS_SLICE.value,
        field_name='data.created',
        items_to_keep=3,
        rotate_policy=partitioning.RotatePolicy.none,
        items_in_partition=2,
    )
    with pytest.raises(partitioning.DocDistantFutureError):
        info_month_slice.select_table(
            {
                'data': {
                    'created': dates.timestamp_us(
                        datetime.datetime(2019, 11, 28),
                    ),
                },
            },
        )
    with pytest.raises(partitioning.DocDistantFutureError):
        info_month_slice.select_table(
            {
                'data': {
                    'created': dates.timestamp_us(
                        datetime.datetime(2019, 7, 28),
                    ),
                },
            },
        )
    info_month_slice.select_table(
        {
            'data': {
                'created': dates.timestamp_us(datetime.datetime(2019, 6, 28)),
            },
        },
    )

    with pytest.raises(partitioning.DocTooOldError):
        info_month_slice.select_table(
            {
                'data': {
                    'created': dates.timestamp_us(
                        datetime.datetime(2018, 8, 28),
                    ),
                },
            },
        )
    info_month_slice.select_table(
        {
            'data': {
                'created': dates.timestamp_us(datetime.datetime(2018, 9, 28)),
            },
        },
    )


@pytest.mark.nofilldb
@pytest.mark.now('2019-04-19T12:08:12')
def test_partitioning_info_monthly():
    info_monthly = partitioning.PartitioningInfo(
        type=partitioning.PartitionType.BY_MONTHS.value,
        field_name='data.created',
        items_to_keep=3,
        rotate_policy=partitioning.RotatePolicy.none,
    )
    _asserts_for_monthly(info_monthly)
    with pytest.raises(partitioning.DocTooOldError):
        info_monthly.select_table(
            {
                'data': {
                    'created': dates.timestamp_us(
                        datetime.datetime(2018, 11, 28),
                    ),
                },
            },
        )
    with pytest.raises(partitioning.DocDistantFutureError):
        info_monthly.select_table(
            {
                'data': {
                    'created': dates.timestamp_us(
                        datetime.datetime(2019, 6, 28),
                    ),
                },
            },
        )
    assert info_monthly.next_table == '2019-05'
    assert info_monthly.current_table == '2019-04'
    assert info_monthly.all_active_tables == [
        '2019-04',
        '2019-03',
        '2019-02',
        '2019-01',
    ]
    assert info_monthly.last_expired_table == '2018-12'


@pytest.mark.nofilldb
@pytest.mark.now('2019-04-19T12:08:12')
def test_partitioning_info_eternal():
    info_monthly = partitioning.PartitioningInfo(
        type=partitioning.PartitionType.BY_MONTHS.value,
        field_name='data.created',
        rotate_policy=partitioning.RotatePolicy.eternal,
    )
    assert info_monthly.no_rotation
    _asserts_for_monthly(info_monthly)
    assert (
        info_monthly.select_table(
            {
                'data': {
                    'created': dates.timestamp_us(
                        datetime.datetime(2018, 11, 28),
                    ),
                },
            },
        )
        == '2018-11'
    )
    with pytest.raises(partitioning.PartitionSelectionError):
        info_monthly.last_expired_table  # pylint: disable=pointless-statement


def _asserts_for_monthly(info_monthly):
    assert (
        info_monthly.select_table(
            {
                'data': {
                    'created': dates.timestamp_us(
                        datetime.datetime(2019, 2, 1),
                    ),
                },
            },
        )
        == '2019-02'
    )
    assert (
        info_monthly.select_table(
            {
                'data': {
                    'created': dates.timestamp_us(
                        datetime.datetime(2019, 2, 28, 23, 59),
                    ),
                },
            },
        )
        == '2019-02'
    )
    with pytest.raises(partitioning.PartitionSelectionError):
        info_monthly.select_table({'data': {'created': None}})


@pytest.mark.nofilldb
@pytest.mark.parametrize(
    'created, expected_partition',
    [
        (datetime.datetime(2019, 4, 18), '2019'),
        (datetime.datetime(2017, 12, 31, 23, 59, 59, 999999), '2017'),
        (datetime.datetime(2017, 1, 1, 0, 0, 0, 0), '2017'),
    ],
)
@pytest.mark.now('2019-04-19T12:08:12')
def test_partitioning_info_by_years(created, expected_partition):
    partitioning_info = partitioning.PartitioningInfo(
        type=partitioning.PartitionType.BY_YEARS.value,
        field_name='data.created',
        rotate_policy=partitioning.RotatePolicy.eternal,
    )
    assert (
        partitioning_info.select_table(
            {'data': {'created': dates.timestamp_us(created)}},
        )
        == expected_partition
    )


@pytest.mark.nofilldb
@pytest.mark.parametrize(
    'expected_select, expected_partitions',
    [
        pytest.param(
            (
                (datetime.datetime(1970, 1, 18), '1970-01_1970-05'),
                (datetime.datetime(1970, 2, 18), '1970-01_1970-05'),
            ),
            (
                ('current_table', '1970-01_1970-05'),
                ('next_table', '1970-06_1970-10'),
                ('last_expired_table', '1969-03_1969-07'),
                ('all_active_tables', ['1970-01_1970-05', '1969-08_1969-12']),
            ),
            marks=pytest.mark.now('1970-02-10T12:08:12'),
        ),
        pytest.param(
            (
                (datetime.datetime(2019, 1, 1), '2018-10_2019-02'),
                (datetime.datetime(2019, 4, 18), '2019-03_2019-07'),
                (datetime.datetime(2018, 12, 18), '2018-10_2019-02'),
            ),
            (
                ('current_table', '2019-03_2019-07'),
                ('next_table', '2019-08_2019-12'),
                ('last_expired_table', '2018-05_2018-09'),
                ('all_active_tables', ['2019-03_2019-07', '2018-10_2019-02']),
            ),
            marks=pytest.mark.now('2019-04-19T12:08:12'),
        ),
        pytest.param(
            (
                (datetime.datetime(2020, 2, 3, 10), '2020-01_2020-05'),
                (datetime.datetime(2020, 1, 3, 10), '2020-01_2020-05'),
                (datetime.datetime(2020, 1, 1, 0), '2020-01_2020-05'),
                (datetime.datetime(2019, 12, 31, 23, 59), '2019-08_2019-12'),
                (datetime.datetime(2019, 12, 1), '2019-08_2019-12'),
            ),
            (
                ('current_table', '2020-01_2020-05'),
                ('next_table', '2020-06_2020-10'),
                ('last_expired_table', '2019-03_2019-07'),
                ('all_active_tables', ['2020-01_2020-05', '2019-08_2019-12']),
            ),
            marks=pytest.mark.now('2020-03-03T12:08:12'),
        ),
    ],
)
def test_partitioning_months_slice(expected_select, expected_partitions):
    partitioning_info = partitioning.PartitioningInfo(
        type=partitioning.PartitionType.MONTHS_SLICE.value,
        field_name='data.created',
        rotate_policy=partitioning.RotatePolicy.remove,
        items_to_keep=1,
        items_in_partition=5,
    )

    assert expected_select
    for created, expected in expected_select:
        doc = {'data': {'created': dates.timestamp_us(created)}}
        selected = partitioning_info.select_table(doc)
        assert selected == expected, f'created: {created}'

    assert expected_partitions
    for key, value in expected_partitions:
        assert getattr(partitioning_info, key) == value, key


@pytest.mark.nofilldb
@pytest.mark.parametrize(
    'partitioning_field, expected_partition, expected_error',
    [
        ('foo', 'foo/table', None),
        ('bar', 'bar/table', None),
        ('foo/bar', None, partitioning.PartitionSelectionError),
        ('foo@bar', None, partitioning.PartitionSelectionError),
        (None, None, partitioning.PartitionSelectionError),
    ],
)
def test_partitioning_by_field(
        partitioning_field, expected_partition, expected_error,
):
    partitioning_info = partitioning.PartitioningInfo(
        type=partitioning.PartitionType.BY_FIELD.value,
        field_name='data.field',
        rotate_policy=partitioning.RotatePolicy.eternal,
        output_table='table',
    )
    doc = {'data': {'field': partitioning_field}}
    if expected_error is not None:
        with pytest.raises(expected_error):
            partitioning_info.select_table(doc)
    else:
        assert partitioning_info.select_table(doc) == expected_partition


@pytest.mark.nofilldb
@pytest.mark.parametrize(
    'cast_to_date, created, expected_partition',
    [
        ('utc_from_timestamp', 1555597826, '2019'),  # 2019-08-04 14:30:26
        ('utc_from_timestamp', 1514764800, '2018'),  # 2018-01-01 00:00:00
        ('utc_from_timestamp', 1546300799, '2018'),  # 2018-12-31 23:59:59
        (
            'utc_from_microseconds',
            1555597826000000,
            '2019',
        ),  # 2019-08-04 14:30:26
        (
            'utc_from_microseconds',
            1546300799000000,
            '2018',
        ),  # 2018-12-31 23:59:59
        ('utc_from_isostring', '2019-08-04 14:30:26', '2019'),
        ('utc_from_isostring', '2018-01-01 00:00:00.000', '2018'),
        ('utc_from_isostring', '2018-12-31 23:59:59.999', '2018'),
        ('utc_from_isostring', '2019-08-04T14:30:26+0300', '2019'),
        ('utc_from_isostring', '2018-01-01T00:00:00.000Z', '2018'),
        ('utc_from_isostring', '2018-01-01T00:00:00.000+0100', '2017'),
        ('utc_from_isostring', '2018-12-31 23:59:59.999-0100', '2019'),
    ],
)
@pytest.mark.now('2019-04-19T12:08:12')
def test_partitioning_casts(cast_to_date, created, expected_partition):
    partitioning_info = partitioning.PartitioningInfo(
        cast_to_date=cast_to_date,  # type: ignore
        type=partitioning.PartitionType.BY_YEARS.value,
        field_name='data.created',
        rotate_policy=partitioning.RotatePolicy.eternal,
    )
    assert (
        partitioning_info.select_table({'data': {'created': created}})
        == expected_partition
    )


@pytest.mark.nofilldb
@pytest.mark.parametrize(
    'partitioning_type, created, rotate_policy, correct',
    [
        (
            partitioning.PartitionType.BY_YEARS.value,
            datetime.datetime(2020, 4, 18),
            partitioning.RotatePolicy.none,
            True,
        ),
        (
            partitioning.PartitionType.BY_YEARS.value,
            datetime.datetime(2021, 4, 18),
            partitioning.RotatePolicy.none,
            False,
        ),
        (
            partitioning.PartitionType.BY_YEARS.value,
            datetime.datetime(2021, 4, 18),
            partitioning.RotatePolicy.eternal,
            True,
        ),
        (
            partitioning.PartitionType.BY_MONTHS.value,
            datetime.datetime(2019, 5, 18),
            partitioning.RotatePolicy.none,
            True,
        ),
        (
            partitioning.PartitionType.BY_MONTHS.value,
            datetime.datetime(2019, 6, 18),
            partitioning.RotatePolicy.none,
            False,
        ),
        (
            partitioning.PartitionType.BY_MONTHS.value,
            datetime.datetime(2019, 6, 18),
            partitioning.RotatePolicy.eternal,
            True,
        ),
        (
            partitioning.PartitionType.BY_DAYS.value,
            datetime.datetime(2019, 4, 20),
            partitioning.RotatePolicy.none,
            True,
        ),
        (
            partitioning.PartitionType.BY_DAYS.value,
            datetime.datetime(2019, 4, 21),
            partitioning.RotatePolicy.none,
            False,
        ),
        (
            partitioning.PartitionType.BY_DAYS.value,
            datetime.datetime(2019, 4, 21),
            partitioning.RotatePolicy.eternal,
            True,
        ),
        (
            partitioning.PartitionType.BY_YEARS.value,
            datetime.datetime(2020, 4, 18),
            partitioning.RotatePolicy.raw_history,
            True,
        ),
        (
            partitioning.PartitionType.BY_YEARS.value,
            datetime.datetime(2021, 4, 18),
            partitioning.RotatePolicy.raw_history,
            True,
        ),
        (
            partitioning.PartitionType.BY_MONTHS.value,
            datetime.datetime(2019, 6, 18),
            partitioning.RotatePolicy.raw_history,
            True,
        ),
    ],
)
@pytest.mark.now('2019-04-19T12:08:12')
def test_partitioning_info_incorrect_partition(
        partitioning_type, created, rotate_policy, correct,
):
    is_eternal = rotate_policy == partitioning.RotatePolicy.eternal
    partitioning_info = partitioning.PartitioningInfo(
        type=partitioning_type,
        field_name='data.created',
        rotate_policy=rotate_policy,
        items_to_keep=10 if not is_eternal else None,
    )
    try:
        partitioning_info.select_table(
            {'data': {'created': dates.timestamp_us(created)}},
        )
    except partitioning.PartitionSelectionError:
        assert not correct
    except partitioning.DocDistantFutureError:
        assert not correct
    else:
        assert correct


@pytest.mark.parametrize(
    'target_name, expected',
    [
        ('test_raw_history_month', 1),
        ('test_raw_history_years', 1),
        ('test_raw_history_days', 2),
    ],
)
@pytest.mark.now('2022-01-10T18:29:12')
async def test_ensure_items_to_keep(replication_ctx, target_name, expected):
    target = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        target_names=[target_name],
    )[0].targets[0]
    assert (
        target.meta.partitioning.rotate_policy
        == partitioning.RotatePolicy.raw_history
    )
    assert target.meta.partitioning.items_to_keep == expected


@pytest.mark.nofilldb
@pytest.mark.parametrize(
    'timestamp, partition, partition_type, expected',
    [
        (
            datetime.datetime(2019, 4, 18),
            '2019',
            partitioning.PartitionType.BY_YEARS.value,
            False,
        ),
        (
            datetime.datetime(2017, 1, 2, 0, 0, 0, 0),
            '2016',
            partitioning.PartitionType.BY_YEARS.value,
            True,
        ),
        (
            datetime.datetime(2017, 12, 31, 23, 59, 59, 999999),
            '2017-12',
            partitioning.PartitionType.BY_MONTHS.value,
            False,
        ),
        (
            datetime.datetime(2017, 11, 3, 23, 59, 59, 999999),
            '2017-10',
            partitioning.PartitionType.BY_MONTHS.value,
            True,
        ),
        (
            datetime.datetime(2017, 12, 31, 1, 0, 0, 0),
            '2017-12-30',
            partitioning.PartitionType.BY_DAYS.value,
            True,
        ),
        (
            datetime.datetime(2017, 12, 30, 0, 0, 0, 0),
            '2017-12-31',
            partitioning.PartitionType.BY_DAYS.value,
            False,
        ),
    ],
)
async def test_compare_partitioning(
        timestamp, partition, partition_type, expected,
):
    info = partitioning.PartitioningInfo(
        type=partition_type,
        field_name='data.created',
        rotate_policy=partitioning.RotatePolicy.raw_history,
    )
    result = info.is_partition_less_than_stamp(timestamp, partition)
    assert result == expected
