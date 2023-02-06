import pytest

from kazoo.client import KazooState

import metrika.pylib.daemon.slot_strategy as slot_strategy
import metrika.pylib.daemon.exceptions as mde


class ZooMasterTestError(Exception):
    pass


def test_validate_config_is_called_on_init(monkeypatch, zoomaster_factory):
    def mock_validate_config(*args, **kwargs):
        raise ZooMasterTestError

    monkeypatch.setattr(slot_strategy.ZooAwareMixin, 'validate_zoomaster_config', mock_validate_config)

    with pytest.raises(ZooMasterTestError):
        zoomaster_factory()


def test_validate_config_required_options_check(zoomaster):
    for option in slot_strategy.ZOOMASTER_REQUIRED_OPTS:
        value = zoomaster.master_config.pop(option)
        with pytest.raises(mde.InvalidConfig):
            zoomaster.validate_zoomaster_config()
        zoomaster.master_config[option] = value


def test_validate_zk_root_is_called_on_validate_config(zoomaster, monkeypatch):
    def mock_validate_zk_root(*args, **kwargs):
        raise ZooMasterTestError

    monkeypatch.setattr(zoomaster, 'validate_zk_root', mock_validate_zk_root)

    with pytest.raises(ZooMasterTestError):
        zoomaster.validate_zoomaster_config()


def test_validate_zk_root(zoomaster):
    zoomaster.master_config['zk_root'] = 'no_slash_root'
    with pytest.raises(mde.InvalidConfig):
        zoomaster.validate_zk_root()


def test_run_initiate_stop_on_kazoo_state_change(monkeypatch, zoomaster):
    def mock__initiate_stop(*args, **kwargs):
        raise ZooMasterTestError

    monkeypatch.setattr(zoomaster, '_initiate_stop', mock__initiate_stop)

    with pytest.raises(ZooMasterTestError):
        for listener in zoomaster.zk.listeners:
            listener(KazooState.LOST)
