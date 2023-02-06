# coding: utf-8
import pytest

from dmp_suite.ctl.extensions.domain.yt import (
    YT_DOMAIN,
    map_yt_to_storage_entity,
    YTDomainProvider
)
from dmp_suite.ctl.exceptions import CtlError
from dmp_suite.ctl.core import StorageEntity
from dmp_suite.yt import NotLayeredYtTable, NotLayeredYtLayout, YTMeta, join_path_parts, DayPartitionScale, String


class TestYtTable(NotLayeredYtTable):
    __layout__ = NotLayeredYtLayout('test', 'test_entity')


class TestYtTableWScale(NotLayeredYtTable):
    __layout__ = NotLayeredYtLayout('test', 'test_entity')
    __partition_scale__ = DayPartitionScale('d')
    d = String()


class Foo(object):
    pass


_path_prefix = '//dummy'


def assert_map_callback(callback):
    with pytest.raises(CtlError):
        callback(None)
    
    with pytest.raises(CtlError):
        callback('')

    with pytest.raises(CtlError):
        callback(Foo)

    yt_string_path = join_path_parts(_path_prefix, 'test', 'test_entity')
    expected = StorageEntity(YT_DOMAIN, yt_string_path)
    assert expected == callback(yt_string_path)
    assert expected == callback(TestYtTable)
    assert expected == callback(YTMeta(TestYtTable))
    assert expected == callback(TestYtTable())

    yt_string_path = join_path_parts(_path_prefix, 'test', 'test_entity')
    expected = StorageEntity(YT_DOMAIN, yt_string_path)
    assert expected == callback(TestYtTableWScale)


def test_map_yt_to_storage_entity():
    assert_map_callback(map_yt_to_storage_entity)


def test_yt_ctl_provider():
    assert_map_callback(YTDomainProvider(None).to_storage_entity)
