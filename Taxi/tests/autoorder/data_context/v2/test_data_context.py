import datetime

import pytest

from nile.api.v1 import Record
from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.autoorder.data_context.v2.data_context import (
    timestamp_2_local_dt,
    get_day_start_ts_range,
    calc_cutoff,
    items_history_reducer,
    items_cutoff_reducer,
)


def test_timestamp_2_local_dt():
    assert timestamp_2_local_dt(1646949600, 'Asia/Jerusalem') == '2022-03-11'
    assert (
        timestamp_2_local_dt(1648414800, 'utc', '%Y-%m-%d %H:%M:%S')
        == '2022-03-27 21:00:00'
    )
    assert (
        timestamp_2_local_dt(1648414800, 'Asia/Jerusalem', '%Y-%m-%d %H:%M:%S')
        == '2022-03-28 00:00:00'
    )
    assert (
        timestamp_2_local_dt(1648414800, 'Europe/Moscow', '%Y-%m-%d %H:%M:%S')
        == '2022-03-28 00:00:00'
    )
    assert (
        timestamp_2_local_dt(1647295200, 'utc', '%Y-%m-%d %H:%M:%S')
        == '2022-03-14 22:00:00'
    )
    assert (
        timestamp_2_local_dt(1647295200, 'Asia/Jerusalem', '%Y-%m-%d %H:%M:%S')
        == '2022-03-15 00:00:00'
    )
    assert (
        timestamp_2_local_dt(1647295200, 'Europe/Moscow', '%Y-%m-%d %H:%M:%S')
        == '2022-03-15 01:00:00'
    )


def test_get_day_start_ts_range():
    start_dttm = datetime.datetime.strptime('2022-03-24', '%Y-%m-%d')
    end_dttm = datetime.datetime.strptime('2022-03-26', '%Y-%m-%d')
    assert get_day_start_ts_range(start_dttm, end_dttm, 'Asia/Jerusalem') == [
        1648072800,
        1648159200,
        1648242000,
    ]
    assert get_day_start_ts_range(start_dttm, end_dttm, 'Europe/Moscow') == [
        1648069200,
        1648155600,
        1648242000,
    ]


def test_calc_cutoff():
    assert pytest.approx(calc_cutoff([1, 2, 7, 1, 4], 0.9, 1)) == 5.8
    assert calc_cutoff([1, 2, 7, 1, 4], 1.5, 1) == 8.5
    assert calc_cutoff([], 1.5, 1) is None
    assert calc_cutoff([1, 2, 3], None, 1) is None
    assert calc_cutoff([1], 1.5, 1) == 2.5


def test_cutoff_reducer():
    test_input = [
        Record(
            organization_id=1,
            dt='2022-03-11',
            day_start_timestamp=1646949600,
            quantity=4,
        ),
        Record(
            organization_id=1,
            dt='2022-03-11',
            day_start_timestamp=1646949600,
            quantity=1,
        ),
        Record(
            organization_id=1,
            dt='2022-03-11',
            day_start_timestamp=1646949600,
            quantity=2,
        ),
        Record(
            organization_id=1,
            dt='2022-03-12',
            day_start_timestamp=1647036000,
            quantity=1,
        ),
        Record(
            organization_id=1,
            dt='2022-03-12',
            day_start_timestamp=1647036000,
            quantity=2,
        ),
        Record(
            organization_id=1,
            dt='2022-03-12',
            day_start_timestamp=1647036000,
            quantity=1,
        ),
        Record(
            organization_id=1,
            dt='2022-03-13',
            day_start_timestamp=1647122400,
            quantity=2,
        ),
        Record(
            organization_id=1,
            dt='2022-03-13',
            day_start_timestamp=1647122400,
            quantity=3,
        ),
        Record(
            organization_id=1,
            dt='2022-03-15',
            day_start_timestamp=1647295200,
            quantity=1,
        ),
        Record(
            organization_id=1,
            dt='2022-03-26',
            day_start_timestamp=1648242000,
            quantity=3,
        ),
        Record(
            organization_id=1,
            dt='2022-03-26',
            day_start_timestamp=1648242000,
            quantity=1,
        ),
        Record(
            organization_id=1,
            dt='2022-03-27',
            day_start_timestamp=1648328400,
            quantity=1,
        ),
        Record(
            organization_id=1,
            dt='2022-03-27',
            day_start_timestamp=1648328400,
            quantity=50,
        ),
        Record(
            organization_id=1,
            dt='2022-03-28',
            day_start_timestamp=1648414800,
            quantity=2,
        ),
        Record(
            organization_id=1,
            dt='2022-03-29',
            day_start_timestamp=1648501200,
            quantity=1,
        ),
    ]

    expected_output = [
        Record(
            organization_id=1,
            day_start_timestamp=1648328400,
            quantity_cutoff=4.0,
        ),
        Record(
            organization_id=1,
            day_start_timestamp=1648414800,
            quantity_cutoff=35.375,
        ),
        Record(
            organization_id=1,
            day_start_timestamp=1648501200,
            quantity_cutoff=6.0,
        ),
    ]
    output = []

    job = clusters.MockCluster().job()

    job.table('').label('input').groupby('organization_id').sort(
        'day_start_timestamp',
    ).reduce(
        items_cutoff_reducer(
            output_start_dttm=datetime.datetime.strptime(
                '2022-03-20', '%Y-%m-%d',
            ),
            end_dttm=datetime.datetime.strptime('2022-03-31', '%Y-%m-%d'),
            clip_outliers_window=10,
            clip_outliers_param=1.5,
            min_len_of_history=1,
            timezones_dict={1: 'Asia/Jerusalem'},
        ),
    ).put(
        '',
    ).label(
        'output',
    )

    job.local_run(
        sources={'input': StreamSource(test_input)},
        sinks={'output': ListSink(output)},
    )
    assert output == expected_output


def test_items_history_reducer():
    test_input = [
        Record(
            organization_id=1,
            dt='2022-03-11',
            day_start_timestamp=1646949600,
            quantity=4,
        ),
        Record(
            organization_id=1,
            dt='2022-03-11',
            day_start_timestamp=1646949600,
            quantity=1,
        ),
        Record(
            organization_id=1,
            dt='2022-03-11',
            day_start_timestamp=1646949600,
            quantity=2,
        ),
        Record(
            organization_id=1,
            dt='2022-03-12',
            day_start_timestamp=1647036000,
            quantity=1,
        ),
        Record(
            organization_id=1,
            dt='2022-03-12',
            day_start_timestamp=1647036000,
            quantity=2,
        ),
        Record(
            organization_id=1,
            dt='2022-03-12',
            day_start_timestamp=1647036000,
            quantity=1,
        ),
        Record(
            organization_id=1,
            dt='2022-03-13',
            day_start_timestamp=1647122400,
            quantity=2,
        ),
        Record(
            organization_id=1,
            dt='2022-03-13',
            day_start_timestamp=1647122400,
            quantity=3,
        ),
        Record(
            organization_id=1,
            dt='2022-03-15',
            day_start_timestamp=1647295200,
            quantity=1,
        ),
        Record(
            organization_id=1,
            dt='2022-03-26',
            day_start_timestamp=1648242000,
            quantity=3,
        ),
        Record(
            organization_id=1,
            dt='2022-03-26',
            day_start_timestamp=1648242000,
            quantity=1,
        ),
        Record(
            organization_id=1,
            dt='2022-03-27',
            day_start_timestamp=1648328400,
            quantity=1,
        ),
        Record(
            organization_id=1,
            dt='2022-03-27',
            day_start_timestamp=1648328400,
            quantity=50,
        ),
        Record(
            organization_id=1,
            dt='2022-03-28',
            day_start_timestamp=1648414800,
            quantity=2,
        ),
        Record(
            organization_id=1,
            dt='2022-03-29',
            day_start_timestamp=1648501200,
            quantity=1,
        ),
    ]

    expected_output = [
        Record(
            organization_id=1, timestamp=1647727200, date_local='2022-03-20',
        ),
        Record(
            organization_id=1, timestamp=1648328400, date_local='2022-03-27',
        ),
        Record(
            organization_id=1, timestamp=1648414800, date_local='2022-03-28',
        ),
        Record(
            organization_id=1, timestamp=1648501200, date_local='2022-03-29',
        ),
        Record(
            organization_id=1, timestamp=1648587600, date_local='2022-03-30',
        ),
    ]
    output = []

    job = clusters.MockCluster().job()

    job.table('').label('input').groupby('organization_id').sort(
        'day_start_timestamp',
    ).reduce(
        items_history_reducer(
            output_start_dttm=datetime.datetime.strptime(
                '2022-03-20', '%Y-%m-%d',
            ),
            end_dttm=datetime.datetime.strptime('2022-03-31', '%Y-%m-%d'),
            required_history_window=5,
            timezones_dict={1: 'Asia/Jerusalem'},
        ),
    ).put(
        '',
    ).label(
        'output',
    )

    job.local_run(
        sources={'input': StreamSource(test_input)},
        sinks={'output': ListSink(output)},
    )
    assert output == expected_output

    expected_output = [
        Record(
            organization_id=1, timestamp=1648674000, date_local='2022-03-31',
        ),
    ]
    output = []

    job = clusters.MockCluster().job()

    job.table('').label('input').groupby('organization_id').sort(
        'day_start_timestamp',
    ).reduce(
        items_history_reducer(
            output_start_dttm=datetime.datetime.strptime(
                '2022-03-31', '%Y-%m-%d',
            ),
            end_dttm=datetime.datetime.strptime('2022-03-31', '%Y-%m-%d'),
            required_history_window=5,
            timezones_dict={1: 'Asia/Jerusalem'},
        ),
    ).put(
        '',
    ).label(
        'output',
    )

    job.local_run(
        sources={'input': StreamSource(test_input)},
        sinks={'output': ListSink(output)},
    )
    assert output == expected_output


if __name__ == '__main__':
    test_calc_cutoff()
    test_cutoff_reducer()
    test_items_history_reducer()
    test_timestamp_2_local_dt()
