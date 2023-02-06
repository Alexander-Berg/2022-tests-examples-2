# coding: utf-8
import pytest

from nile.api.v1 import MockCluster, Record
from nile.local.sink import ListSink
from nile.local.source import StreamSource

from dmp_suite.nile import temporal_any_left_join


RIGHT_TABLE = [
    Record(
        k1="x",
        k2="y",
        effective_from_dttm="2019-01-05 10:00:00",
        effective_to_dttm="2019-01-05 12:00:00",
        v="a",
    ),
    Record(
        k1="x",
        k2="y",
        effective_from_dttm="2019-01-05 12:00:00",
        effective_to_dttm="2019-01-05 14:00:00",
        v="b",
    ),
]


@pytest.mark.parametrize(
    "given_left_table, given_right_table, expect_output",
    [
        [
            [Record(k1="x", k2="y", d="2019-01-05 09:00:00")],
            RIGHT_TABLE,
            [Record(k1="x", k2="y", d="2019-01-05 09:00:00")],
        ],
        [
            [Record(k1="x", k2="y", d="2019-01-05 10:00:00")],
            RIGHT_TABLE,
            [Record(k1="x", k2="y", d="2019-01-05 10:00:00", v="a")],
        ],
        [
            [Record(k1="x", k2="y", d="2019-01-05 13:00:00")],
            RIGHT_TABLE,
            [Record(k1="x", k2="y", d="2019-01-05 13:00:00", v="b")],
        ],
        [
            [Record(k1="x", k2="y", d="2019-01-05 14:00:00")],
            RIGHT_TABLE,
            [Record(k1="x", k2="y", d="2019-01-05 14:00:00", v="b")],
        ],
        [
            [Record(k1="x", k2="y", d="2019-01-05 15:00:00")],
            RIGHT_TABLE,
            [Record(k1="x", k2="y", d="2019-01-05 15:00:00")],
        ],
        [
            [Record(k1="x", k2=None, d="2019-01-05 10:00:00")],
            [
                Record(
                    k1="x",
                    k2=None,
                    effective_from_dttm="2019-01-05 10:00:00",
                    effective_to_dttm="2019-01-05 12:00:00",
                    v="a",
                )
            ],
            [Record(k1="x", k2=None, d="2019-01-05 10:00:00", v="a")],
        ],
    ],
)
@pytest.mark.parametrize("assume_small_right", [False, True])
def test_temporal_any_left_join(
    given_left_table, given_right_table, expect_output, assume_small_right
):
    cluster = MockCluster()
    job = cluster.job()
    left_table = job.table("left_table").label("left_table")
    right_table = job.table("right_table").label("right_table")
    (
        left_table.call(
            temporal_any_left_join,
            right_table,
            by=("k1", "k2"),
            by_left_dttm="d",
            assume_small_right=assume_small_right,
        ).label("actual")
    )

    actual_output = []
    job.local_run(
        sources={
            "left_table": StreamSource(given_left_table),
            "right_table": StreamSource(given_right_table),
        },
        sinks={"actual": ListSink(actual_output)},
    )
    assert sorted(expect_output) == sorted(actual_output)
