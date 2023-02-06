import pytest
from .yt_fixture import YtFixture
from dmp_suite.yt.table import NotLayeredYtTable, NotLayeredYtLayout, MonthPartitionScale, Date
from dmp_suite.yt.meta import YTMeta

path_splitter = YtFixture.PATH_SPLITTER


class FakeTable(NotLayeredYtTable):
    __layout__ = NotLayeredYtLayout('foo', 'tab')


class FakeTableScale(NotLayeredYtTable):
    __layout__ = NotLayeredYtLayout('foo', 'name')
    __partition_scale__ = MonthPartitionScale('order_created')

    order_created = Date()


folder = '/boo'


def test_target_path():
    assert YtFixture(FakeTable, folder).target_path == YTMeta(FakeTable).target_path()


def test_file_name_by_meta():
    fixture = YtFixture(YTMeta(FakeTableScale, partition='2018-01-01'), folder)
    assert fixture.file_name == 'foo{0}name{0}2018-01-01.json'.format(path_splitter)
    assert fixture.file_full_path == '{0}/foo{1}name{1}2018-01-01.json'.format(folder, path_splitter)


def test_file_name_by_table():
    fixture = YtFixture(FakeTable, folder)
    assert fixture.file_name == 'foo{}tab.json'.format(path_splitter)


def test_file_name_custom():
    fixture = YtFixture(FakeTable, folder, custom_file_name='foo/boo.j')
    assert fixture.file_name == 'foo/boo.j'


def test_yt_path_to_file_name():
    with pytest.raises(ValueError):
        YtFixture.yt_path_to_file_name('foo{}1'.format(path_splitter))
