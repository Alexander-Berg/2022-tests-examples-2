import pytest
import mock

from datetime import datetime

from dmp_suite.ext_source_proxy import ExternalSourceProxy
from dmp_suite.ext_source_proxy.base import map_external_source_proxy_to_storage_entity
from dmp_suite.ext_source_proxy.updater import ExtSourceCtlUpdateTask
from dmp_suite.task.execution import run_task
from dmp_suite.ctl.storage import DictStorage
from connection.ctl import WrapCtl
from dmp_suite.ctl import CTL_LAST_LOAD_DATE


@pytest.fixture
def ctl_mock():
    ctl = WrapCtl(DictStorage())
    patch_ = mock.patch('connection.ctl.get_ctl', return_value=ctl)
    with patch_:
        yield ctl


class DummyExternalSourceProxyBase(ExternalSourceProxy):

    @property
    def ctl_entity(self):
        return 'dummy_ext_source_entity'

    def get_new_ctl_value(self):
        return None


def _get_ctl_param(ctl):
    return ctl.source.get_param(
        'dummy_ext_source_entity',
        CTL_LAST_LOAD_DATE,
    )


def _set_ctl_param(ctl, val):
    return ctl.source.set_param(
        'dummy_ext_source_entity',
        CTL_LAST_LOAD_DATE,
        val,
    )


def _get_collect_proxies_func_to_mock():
    import dmp_suite.ext_source_proxy.updater
    module = dmp_suite.ext_source_proxy.updater.__name__
    func = dmp_suite.ext_source_proxy.updater.collect_external_source_proxies.__name__
    return module + '.' + func


def test_ext_ctl_updated_when_no_current_ctl_set(ctl_mock):

    class ExtSource(DummyExternalSourceProxyBase):
        def get_new_ctl_value(self):
            return datetime(2020, 10, 10)

    cur_val = _get_ctl_param(ctl_mock)
    assert cur_val is None

    ExtSource().update_source_ctl()

    cur_val = _get_ctl_param(ctl_mock)
    assert cur_val == datetime(2020, 10, 10)


def test_ext_ctl_not_updated_when_new_value_is_not_set(ctl_mock):
    class ExtSource(DummyExternalSourceProxyBase):
        def get_new_ctl_value(self):
            return None

    _set_ctl_param(ctl_mock, datetime(2020, 10, 11))

    ExtSource().update_source_ctl()

    cur_val = _get_ctl_param(ctl_mock)
    assert cur_val == datetime(2020, 10, 11)


def test_no_crash_if_neither_new_nor_old_ctl_val_provided(ctl_mock):
    class ExtSource(DummyExternalSourceProxyBase):
        def get_new_ctl_value(self):
            return None

    cur_val = _get_ctl_param(ctl_mock)
    assert cur_val is None

    ExtSource().update_source_ctl()

    cur_val = _get_ctl_param(ctl_mock)
    assert cur_val is None


def test_ext_ctl_updated_when_new_value_is_bigger(ctl_mock):
    class ExtSource(DummyExternalSourceProxyBase):
        def get_new_ctl_value(self):
            return datetime(2020, 10, 13)

    _set_ctl_param(ctl_mock, datetime(2020, 10, 12))

    ExtSource().update_source_ctl()

    cur_val = _get_ctl_param(ctl_mock)
    assert cur_val == datetime(2020, 10, 13)


def test_ext_ctl_not_updated_when_new_value_is_the_same(ctl_mock):
    class ExtSource(DummyExternalSourceProxyBase):
        def get_new_ctl_value(self):
            return datetime(2020, 10, 14)

    _set_ctl_param(ctl_mock, datetime(2020, 10, 14))

    ExtSource().update_source_ctl()

    cur_val = _get_ctl_param(ctl_mock)
    assert cur_val == datetime(2020, 10, 14)


def test_ext_ctl_not_updated_when_new_value_is_less(ctl_mock):
    class ExtSource(DummyExternalSourceProxyBase):
        def get_new_ctl_value(self):
            return datetime(2020, 10, 15)

    _set_ctl_param(ctl_mock, datetime(2020, 10, 16))

    ExtSource().update_source_ctl()

    cur_val = _get_ctl_param(ctl_mock)
    assert cur_val == datetime(2020, 10, 16)


def test_map_external_source_proxy_to_storage_entity():

    ext_source = DummyExternalSourceProxyBase()

    actual = map_external_source_proxy_to_storage_entity(ext_source)

    assert actual == 'dummy_ext_source_entity'


def test_updater_task_update_ctl():

    class ExtSource(DummyExternalSourceProxyBase):
        update_source_ctl = mock.MagicMock()

    patch_ = mock.patch(
        _get_collect_proxies_func_to_mock(),
        return_value=[ExtSource(), ExtSource()]
    )
    with patch_:
        run_task(ExtSourceCtlUpdateTask('dummy'))

    assert ExtSource.update_source_ctl.call_count == 2


def test_updater_task_reports_failure():

    class ExtSource(DummyExternalSourceProxyBase):
        def update_source_ctl(self) -> None:
            raise Exception

    patch_collect = mock.patch(
        _get_collect_proxies_func_to_mock(),
        return_value=[ExtSource()]
    )
    report_mock = mock.MagicMock()
    patch_report = mock.patch(
        'dmp_suite.ext_source_proxy.updater.report_failure',
        new_callable=report_mock,
    )
    with patch_collect, patch_report:
        run_task(ExtSourceCtlUpdateTask('dummy'))

    assert report_mock.called


def test_updater_task_continues_to_run_if_failure():

    class ExtSourceRaise(DummyExternalSourceProxyBase):
        def update_source_ctl(self) -> None:
            raise Exception

    class ExtSourceGood(DummyExternalSourceProxyBase):
        update_source_ctl = mock.MagicMock()

    patch_collect = mock.patch(
        _get_collect_proxies_func_to_mock(),
        return_value=[ExtSourceRaise(), ExtSourceGood()]
    )
    report_mock = mock.MagicMock()
    patch_report = mock.patch(
        'dmp_suite.ext_source_proxy.updater.report_failure',
        new_callable=report_mock,
    )
    with patch_collect, patch_report:
        run_task(ExtSourceCtlUpdateTask('dummy'))

    assert report_mock.call_count == 1
    assert ExtSourceGood.update_source_ctl.call_count == 1
