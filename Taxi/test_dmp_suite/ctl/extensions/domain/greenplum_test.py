# coding: utf-8
import pytest
from dmp_suite.ctl.extensions.domain.greenplum import (
    GP_DOMAIN,
    map_gp_to_storage_entity,
    GPDomainProvider
)
from dmp_suite.ctl.exceptions import CtlError
from dmp_suite.ctl.core import StorageEntity
from dmp_suite.greenplum import GPMeta, ExternalGPLayout, ExternalGPTable


class TestGPTable(ExternalGPTable):
    __layout__ = ExternalGPLayout('test_schema', 'test_entity')

    @classmethod
    def get_layout_prefix(cls):
        return 'test'


class Foo(object):
    pass


def assert_map_callback(callback):
    with pytest.raises(CtlError):
        callback(None)

    with pytest.raises(CtlError):
        callback('')

    with pytest.raises(CtlError):
        callback(Foo)

    string_path = GPMeta(TestGPTable).table_full_name
    assert string_path == 'test_schema.test_entity'

    expected = StorageEntity(GP_DOMAIN, string_path)
    assert callback(string_path) == expected
    assert callback(TestGPTable) == expected
    assert callback(GPMeta(TestGPTable)) == expected


def test_map_gp_to_storage_entity():
    assert_map_callback(map_gp_to_storage_entity)


def test_gp_ctl_provider():
    assert_map_callback(GPDomainProvider(None).to_storage_entity)
