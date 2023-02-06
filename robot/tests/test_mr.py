import random
from copy import copy
from os.path import join as pj

import yatest.common
from hamcrest import assert_that, contains, calling, raises

from yt.wrapper import YtHttpResponseError

from favicon import yt
from robot.favicon.tests.protos.tables_pb2 import TFoo, TBar, TBoxes


JOB_BINARY = yatest.common.binary_path("robot/favicon/tests/mrjob/mrjob")


def test_sorted_append(config):
    t = yt.Table("t", TBar).sorted(unique=True, by=[TBar.INT_FIELD_NUMBER])
    r1 = [TBar(Int=i, Boxes=TBoxes(X=i)) for i in xrange(10, 20)]
    r2 = [TBar(Int=i) for i in xrange(10)]
    yt.create_table(t)
    yt.write_table(t, r1)
    assert_that(yt.read_table(t), contains(*r1))
    yt.write_table(t, r2)
    assert_that(yt.read_table(t), contains(*r2))
    yt.write_table(t.for_append(), r1)
    assert_that(yt.read_table(t), contains(*(r2 + r1)))
    assert_that(calling(yt.write_table)
                .with_args(t.for_append(), [TBar(Int=19)]),
                raises(YtHttpResponseError))


def test_select_fields(config):
    t = yt.Table("t", TFoo)
    yt.write_table(t, [TFoo(String=str(i), Uint=i) for i in xrange(10)])
    assert_that(yt.read_table(t.select_fields([TFoo.UINT_FIELD_NUMBER])),
                contains(*[TFoo(Uint=i) for i in xrange(10)]))


def test_exclude_fields(config):
    t = yt.Table("t", TFoo)
    yt.write_table(t, [TFoo(String=str(i), Uint=i) for i in xrange(10)])
    assert_that(yt.read_table(t.exclude_fields([TFoo.UINT_FIELD_NUMBER])),
                contains(*[TFoo(String=str(i)) for i in xrange(10)]))


def test_sort(config):
    t = yt.Table("t", TFoo)
    ordered_rows = [TFoo(String=str(i).zfill(3), Uint=100 - i) for i in xrange(10)]
    input_stream = copy(ordered_rows)
    random.shuffle(input_stream)
    yt.write_table(t, input_stream)
    yt.run_sort(t.sorted(unique=True))
    assert_that(yt.read_table(t), contains(*ordered_rows))
    assert_that(yt.get_attribute(t, "schema/@unique_keys"))
    yt.run_sort(t.sorted(unique=True, by=["Uint"]))
    assert_that(yt.read_table(t), contains(*reversed(ordered_rows)))


def test_merge(config):
    ta = yt.Table("a", TFoo).sorted(by=["Uint"], unique=True)
    yt.write_table(ta, [TFoo(Uint=i) for i in xrange(10)])
    tb = yt.Table("b", TFoo).sorted(by=["Uint"], unique=True)
    yt.write_table(tb, [TFoo(Uint=i) for i in xrange(10, 20)])
    tc = yt.Table("c", TFoo).sorted(by=["Uint"], unique=True)
    yt.run_merge([ta, tb], tc, mode='sorted')
    assert_that(yt.read_table(tc), contains(*[TFoo(Uint=i) for i in xrange(20)]))


def test_map(config):
    map_a = [TFoo(String=str(i).zfill(3), Enum=-1, Uint=i, Bool=i % 2)
             for i in xrange(10)]
    ta = yt.Table("a", TFoo).sorted(by=["String"], unique=True)
    yt.write_table(ta, map_a)

    map_b = [TFoo(String=str(i).zfill(3), Enum=5, Uint=2 * i, Bool=1 - i % 2)
             for i in xrange(10)]
    tb = yt.Table("b", TFoo).sorted(by=["String"], unique=True)
    yt.write_table(tb, map_b)

    tc = yt.Table("c", TBar).sorted(unique=True)
    yt.run_map(yt.JobClass(pj(config.BinDir, config.JobBinary), "NFaviconTest::TFooToBar"), [ta, tb], tc, ordered=True)
    for row in yt.read_table(tc):
        assert_that(row.Bytes, str(i).zfill(3))
        assert_that(row.Int, i * (0 if i % 2 else -1))
        assert_that(row.Double, 5.0)
        assert_that(len(row.Boxes.Box), 2)


def test_reduce(config):
    ta = yt.Table("a", TBar).sorted()
    yt.write_table(ta, [TBar(Bytes=str(i), Int=42) for i in xrange(10)])
    tb = yt.Table("b", TBar).sorted()
    yt.write_table(tb, [TBar(Bytes=str(i), Int=24) for i in xrange(10)])
    yt.run_reduce(
        yt.JobClass(pj(config.BinDir, config.JobBinary), "NFaviconTest::TCountWords"),
        [ta, tb],  # source_table
        ta,  # destination_table
        reduce_by=["bytes"]
    )
    assert_that(
        list(yt.read_table(ta)),
        contains(*[TBar(Bytes=str(i), Int=66) for i in xrange(10)])
    )
