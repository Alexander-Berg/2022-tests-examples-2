import pytest
import dmp_suite.yt.operation

from unittest import TestCase
from dmp_suite import datetime_utils as dtu, logfeller_utils as lu, scales
from dmp_suite.exceptions import DWHError, MissingTablesError
from dmp_suite.yt import join_path_parts


class TestLogfellerUtils(TestCase):
    def test_check_period_for_scale(self):
        self.assertRaises(
            DWHError,
            lu._assert_period_for_scale,
            dtu.period('2018-11-23', '2018-11-25'),
            lu.LogfellerScale.DAY
        )
        self.assertRaises(
            DWHError,
            lu._assert_period_for_scale,
            dtu.period('2018-11-23 03:20:00', '2018-11-25 03:00:00'),
            lu.LogfellerScale.DAY
        )
        self.assertRaises(
            DWHError,
            lu._assert_period_for_scale,
            dtu.period('2018-11-23 03:20:00', '2018-11-25 03:00:00'),
            lu.LogfellerScale.HOUR
        )
        self.assertRaises(
            DWHError,
            lu._assert_period_for_scale,
            dtu.period('2018-11-23 03:20:00', '2018-11-25 03:00:00'),
            lu.LogfellerScale.HALFHOUR
        )
        self.assertRaises(
            DWHError,
            lu._assert_period_for_scale,
            dtu.period('2018-11-23 03:12:00', '2018-11-23 03:22:00'),
            lu.LogfellerScale.FIVEMIN
        )
        try:
            lu._assert_period_for_scale(
                dtu.period('2018-11-23 00:00:00', '2018-11-25 23:59:59.999999'),
                lu.LogfellerScale.DAY
            )
            lu._assert_period_for_scale(
                dtu.period('2018-11-23 03:00:00', '2018-11-25 04:59:59.999999'),
                lu.LogfellerScale.HOUR
            )
            lu._assert_period_for_scale(
                dtu.period('2018-11-23 03:30:00', '2018-11-25 04:29:59.999999'),
                lu.LogfellerScale.HALFHOUR
            )
            lu._assert_period_for_scale(
                dtu.period('2018-11-23 03:10:00', '2018-11-23 03:24:59.999999'),
                lu.LogfellerScale.FIVEMIN
            )

        except DWHError as e:
            self.fail(e.args[0])


def test_logfeller_scales_is_supported():
    for ls in lu.LogfellerScale:
        assert scales.get_scale_by_name(ls.value) is not None


@pytest.mark.parametrize(
    ["tables_on_cluster", "scale", "period", "missing_table_behaviour", "prompt_scale", "expect_tables"],
    [
        pytest.param(
            # tables_on_cluster
            {
                lu.LogfellerScale.DAY: [
                    "2018-12-30",
                    "2018-12-31",
                    # "2019-01-01",
                    "2019-01-02",
                    "2019-01-03",
                ]
            },
            # *args
            lu.LogfellerScale.DAY,
            dtu.date_period("2018-12-31", "2019-01-02"),
            "exclude",
            None,
            # expectations
            {
                lu.LogfellerScale.DAY: [
                    "2018-12-31",
                    # "2019-01-01",
                    "2019-01-02",
                ],
            },
        ),
        pytest.param(
            # tables_on_cluster
            {
                lu.LogfellerScale.HALFHOUR: [
                    "2019-01-01T10:00:00",
                    # "2019-01-01T10:30:00",
                    "2019-01-01T11:00:00",
                    "2019-01-01T11:30:00",
                ]
            },
            # *args
            lu.LogfellerScale.HALFHOUR,
            dtu.period("2019-01-01 10:30:00.000000", "2019-01-01 11:29:59.999999"),
            "exclude",
            None,
            # expectations
            {
                lu.LogfellerScale.HALFHOUR: [
                    # "2019-01-01T10:30:00",
                    "2019-01-01T11:00:00",
                ],
            },
        ),
        pytest.param(
            # tables_on_cluster
            {
                lu.LogfellerScale.FIVEMIN: [
                    "2019-01-01T10:05:00",
                    "2019-01-01T10:10:00",
                    # "2019-01-01T10:15:00",
                    "2019-01-01T10:20:00",
                ]
            },
            # *args
            lu.LogfellerScale.FIVEMIN,
            dtu.period("2019-01-01 10:10:00.000000", "2019-01-01 10:19:59.999999"),
            "exclude",
            None,
            # expectations
            {
                lu.LogfellerScale.FIVEMIN: [
                    "2019-01-01T10:10:00",
                    # "2019-01-01T10:15:00",
                ],
            },
        ),
            pytest.param(
            # tables_on_cluster
            {
                lu.LogfellerScale.DAY: [
                    "2018-12-30",
                    "2018-12-31",
                    # "2019-01-01",
                    "2019-01-02",
                    "2019-01-03",
                ]
            },
            # *args
            lu.LogfellerScale.DAY,
            dtu.date_period("2018-12-31", "2019-01-02"),
            "raise",
             None,
            # expectations
            None,
            marks=pytest.mark.xfail(raises=MissingTablesError),
        ),
        pytest.param(
            # tables_on_cluster
            {
                lu.LogfellerScale.DAY: [
                    "2018-12-30",
                    "2018-12-31",
                    # "2019-01-01",
                    "2019-01-02",
                    "2019-01-03",
                ]
            },
            # *args
            lu.LogfellerScale.DAY,
            dtu.date_period("2018-12-31", "2019-01-02"),
            "include",
            None,
            # expectations
            {
                lu.LogfellerScale.DAY: [
                    "2018-12-31",
                    "2019-01-01",
                    "2019-01-02",
                ],
            },
        ),
        pytest.param(
            # tables_on_cluster
            {
                lu.LogfellerScale.DAY: [
                    dtu.format_date(dt)
                    for dt in dtu.period('2020-04-01', '2020-04-13').split_in_days()
                ],
                lu.LogfellerScale.HOUR: [
                    dttm.isoformat()
                    for dttm in dtu.period('2020-04-13 15:00:00', '2020-04-14 15:00:00').split_in_hours()
                ]
            },
            # *args
            lu.LogfellerScale.DAY,
            dtu.date_period("2020-04-13", "2020-04-14"),
            "exclude",
            lu.LogfellerScale.HOUR,
            # expectations
            {
                lu.LogfellerScale.DAY: [
                    "2020-04-13",
                ],
                lu.LogfellerScale.HOUR: [
                    dttm.isoformat()
                    for dttm in dtu.period('2020-04-14 00:00:00', '2020-04-14 15:00:00').split_in_hours()
                ]

            },
            id='test prompt scale hour'
        ),
        pytest.param(
            # tables_on_cluster
            {
                lu.LogfellerScale.DAY: [
                    dtu.format_date(dt)
                    for dt in dtu.period('2020-04-01', '2020-04-13').split_in_days()
                ],
                lu.LogfellerScale.HALFHOUR: [
                    dttm.isoformat()
                    for dttm in dtu.period('2020-04-13 15:00:00', '2020-04-14 15:00:00').split_in_halfhours()
                ]
            },
            # *args
            lu.LogfellerScale.DAY,
            dtu.date_period("2020-04-13", "2020-04-14"),
            "exclude",
            lu.LogfellerScale.HALFHOUR,
            # expectations
            {
                lu.LogfellerScale.DAY: [
                    "2020-04-13",
                ],
                lu.LogfellerScale.HALFHOUR: [
                    dttm.isoformat() for dttm in
                    dtu.period('2020-04-14 00:00:00', '2020-04-14 15:00:00').split_in_halfhours()
                ]

            },
            id='test prompt scale halfhour'
        ),
        pytest.param(
            # tables_on_cluster
            {
                lu.LogfellerScale.DAY: [
                    dtu.format_date(dt)
                    for dt in dtu.period('2020-04-01', '2020-04-13').split_in_days()
                ],
                lu.LogfellerScale.HALFHOUR: [
                    dttm.isoformat()
                    for dttm in dtu.period('2020-04-14 14:00:00', '2020-04-14 15:00:00').split_in_halfhours()
                ]
            },
            # *args
            lu.LogfellerScale.DAY,
            dtu.date_period("2020-04-13", "2020-04-14"),
            "raise",
            lu.LogfellerScale.HALFHOUR,
            # expectations
            None,
            marks=pytest.mark.xfail(raises=MissingTablesError),
            id='test raise with prompt scale'
        ),
        pytest.param(
            # tables_on_cluster
            {
                lu.LogfellerScale.DAY: [
                    dtu.format_date(dt)
                    for dt in dtu.period('2020-04-13', '2020-04-13').split_in_days()
                ],
                lu.LogfellerScale.HOUR: [
                    dt.isoformat()
                    for dt in dtu.period('2020-04-12 23:00:00', '2020-04-14 02:00:00').split_in_hours()
                ]
            },
            # *args
            lu.LogfellerScale.DAY,
            dtu.period('2020-04-12 23:00:00', '2020-04-14 00:59:59.999999'),
            'raise',
            lu.LogfellerScale.HOUR,
            # expectations
            {
                lu.LogfellerScale.DAY: [
                    "2020-04-13"
                ],
                lu.LogfellerScale.HOUR: [
                    "2020-04-12T23:00:00",
                    "2020-04-14T00:00:00"
                ]
            },
            id='scale intersection'
        ),
        pytest.param(
            # tables_on_cluster
            {
                lu.LogfellerScale.DAY: [
                    dtu.format_date(dt)
                    for dt in dtu.period('2020-04-13', '2020-04-13').split_in_days()
                ],
                lu.LogfellerScale.HOUR: [
                    dttm.isoformat()
                    for dttm in dtu.period('2020-04-12 23:00:00', '2020-04-14 02:00:00').split_in_hours()
                    if dtu.format_datetime(dttm) != '2020-04-13 14:00:00'
                ]
            },
            # *args
            lu.LogfellerScale.DAY,
            dtu.period('2020-04-12 23:00:00', '2020-04-14 00:59:59.999999'),
            'raise',
            lu.LogfellerScale.HOUR,
            # expectations
            {
                lu.LogfellerScale.DAY: ['2020-04-13'],
                lu.LogfellerScale.HOUR: [
                    dttm.isoformat()
                    for dttm in dtu.period('2020-04-12 23:00:00', '2020-04-14 00:00:00').split_in_hours()
                    if dtu.format_date(dttm) != '2020-04-13'
                ]
            },
            id='scale intersection with gap'
        ),
        pytest.param(
            # tables_on_cluster
            {
                lu.LogfellerScale.DAY: [
                    '2020-05-30',
                    '2020-05-30.rebuild.2',
                ],
                lu.LogfellerScale.HOUR: [
                    '2020-05-31T00:00:00',
                    '2020-05-31T00:00:00.rebuild.2',
                    '2020-05-31T00:00:00.rebuild.3',
                ]
            },
            # *args
            lu.LogfellerScale.DAY,
            dtu.period("2020-05-30 00:00:00.000000", "2020-05-31 23:59:59.999999"),
            "exclude",
            lu.LogfellerScale.HOUR,
            # expectations
            {
                lu.LogfellerScale.DAY: [
                    '2020-05-30',
                    '2020-05-30.rebuild.2',
                ],
                lu.LogfellerScale.HOUR: [
                    '2020-05-31T00:00:00',
                    '2020-05-31T00:00:00.rebuild.2',
                    '2020-05-31T00:00:00.rebuild.3',
                ]
            },
            id='suffix .rebuild.N for scale and promt_scale'
        ),
        pytest.param(
            # tables_on_cluster
            {
                lu.LogfellerScale.DAY: [
                    '2020-05-30',
                    '2020-05-30.rebuild.2',
                    '2020-05-31',
                ]
            },
            # *args
            lu.LogfellerScale.DAY,
            dtu.period("2020-05-30 00:00:00.000000", "2020-05-31 23:59:59.999999"),
            "exclude",
            None,
            # expectations
            {
                lu.LogfellerScale.DAY: [
                    '2020-05-30',
                    '2020-05-30.rebuild.2',
                    '2020-05-31',
                ]
            },
            id='suffix .rebuild.N for scale without promt_scale'
        ),
        pytest.param(
            # tables_on_cluster
            {
                lu.LogfellerScale.DAY: [
                    dtu.format_date(dt)
                    for dt in dtu.period('2020-04-12', '2020-04-13').split_in_days()
                ],
                lu.LogfellerScale.HALFHOUR: [
                    dttm.isoformat()
                    for dttm in dtu.period('2020-04-14 00:00:00', '2020-04-14 23:30:00').split_in_halfhours()
                ]
            },
            # *args
            lu.LogfellerScale.DAY,
            dtu.date_period("2020-04-13", "2020-04-14"),
            "raise",
            lu.LogfellerScale.HALFHOUR,
            # expectations
            {
                lu.LogfellerScale.DAY: [
                    '2020-04-13',
                ],
                lu.LogfellerScale.HALFHOUR: [
                    dttm.isoformat()
                    for dttm in dtu.period('2020-04-14 00:00:00', '2020-04-14 23:30:00').split_in_halfhours()
                ]
            },
            id='test last date by prompt scale'
        ),
    ],
    ids=lambda param: str(param) if isinstance(param, (str, lu.LogfellerScale)) else "..."
)
def test_logfeller_partition_paths(
    tables_on_cluster,
    scale,
    period,
    missing_table_behaviour,
    expect_tables,
    prompt_scale,
    monkeypatch,
):
    def yt_children_mock(path, *args, **kwargs):
        for requested_scale in lu.LogfellerScale:
            if path.endswith(requested_scale.value):
                return tables_on_cluster.get(requested_scale, [])
        raise RuntimeError("Unexpected call: get_yt_children({!r})".format(path))

    monkeypatch.setattr(dmp_suite.yt.operation, "get_yt_children", yt_children_mock)
    result = lu.logfeller_partition_paths(
        "dummy", scale, period, missing_table_behaviour=missing_table_behaviour, prompt_scale=prompt_scale
    )

    expect_result = [
        join_path_parts("//logs", "dummy", expected_scale.value, table)
        for expected_scale, tables in expect_tables.items()
        for table in tables
    ]

    assert sorted(result) == sorted(expect_result)
