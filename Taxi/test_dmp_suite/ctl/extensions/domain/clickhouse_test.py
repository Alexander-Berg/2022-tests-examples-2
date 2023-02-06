# coding: utf-8
import mock
import pytest
from dmp_suite.ctl.extensions.domain.clickhouse import (
    CH_DOMAIN,
    map_ch_to_storage_entity,
    CHDomainProvider
)
from dmp_suite.ctl.exceptions import CtlError
from dmp_suite.ctl.core import StorageEntity
from dmp_suite.clickhouse import CHTable, CHMeta, CHLayout


class TestCHTable(CHTable):
    __layout__ = CHLayout('test_entity', db='test_db')


class Foo(object):
    pass


def assert_map_callback(callback):
    with pytest.raises(CtlError):
        callback(None, None)

    with pytest.raises(CtlError):
        callback('', None)

    with pytest.raises(CtlError):
        callback(Foo, None)

    string_path = 'test_db.test_entity'
    expected = StorageEntity(CH_DOMAIN, string_path)
    assert expected == callback(string_path, None)
    assert expected == callback(TestCHTable, None)
    assert expected == callback(CHMeta(TestCHTable), None)

    conn_name = 'foo'
    expected = StorageEntity(CH_DOMAIN, conn_name + '.' + string_path)
    assert expected == callback(string_path, conn_name)
    assert expected == callback(TestCHTable, conn_name)
    assert expected == callback(CHMeta(TestCHTable), conn_name)


@mock.patch('dmp_suite.ctl.extensions.domain.clickhouse.CHMeta.table_full_name', return_value='test_db.test_entity')
def test_map_ch_to_storage_entity(_):
    assert_map_callback(map_ch_to_storage_entity)


@mock.patch('dmp_suite.ctl.extensions.domain.clickhouse.CHMeta.table_full_name', return_value='test_db.test_entity')
def test_ch_ctl_provider(_):
    assert_map_callback(CHDomainProvider(None).to_storage_entity)
