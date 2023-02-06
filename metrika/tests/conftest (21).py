import pytest

from metrika.pylib.test_utils.mock_kazoo import get_zk

import metrika.pylib.zkconnect as mtzc
import metrika.pylib.daemon.master as mmaster
import metrika.pylib.daemon.start_strategy as start_strategy
import metrika.pylib.daemon.slot_strategy as slot_strategy
import metrika.pylib.daemon.slave as mslave
import metrika.pylib.config as lib_config

import yatest.common


def get_config(name):
    return lib_config.get_yaml_config_from_file(yatest.common.source_path('metrika/pylib/daemon/tests/data/{}'.format(name)))


class ConfiguredMixin:
    def get_config(self):
        return get_config('config.yaml')


class ZooMaster(ConfiguredMixin,
                mmaster.MasterBase,
                slot_strategy.ZooAwareMixin,
                start_strategy.UnboundedStartStrategyMixin):
    def __init__(self):
        mmaster.MasterBase.__init__(self)
        slot_strategy.ZooAwareMixin.__init__(self)


class Master(ConfiguredMixin, mmaster.Master):
    pass


class SlotMaster(ConfiguredMixin, mmaster.SlotMaster):
    pass


@pytest.fixture
def master():
    return Master()


@pytest.fixture
def zoomaster_factory(monkeypatch):
    monkeypatch.setattr(mtzc, 'get_zk', get_zk)

    def factory():
        return ZooMaster()

    return factory


@pytest.fixture
def zoomaster(zoomaster_factory):
    return zoomaster_factory()


@pytest.fixture
def slotmaster_factory(monkeypatch):
    monkeypatch.setattr(mtzc, 'get_zk', get_zk)

    def factory():
        return SlotMaster()

    return factory


@pytest.fixture
def slotmaster(slotmaster_factory):
    return slotmaster_factory()


@pytest.fixture
def slave(master):
    return mslave.Slave(name='TestSlave', master=master)
