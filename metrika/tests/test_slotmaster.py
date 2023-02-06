import pytest

from metrika.pylib.test_utils.mock_kazoo import get_zk

import metrika.pylib.zkconnect as mtzc
import metrika.pylib.daemon.slot_strategy as slot_strategy
import metrika.pylib.daemon.exceptions as mde


class SlotMasterTestError(Exception):
    pass


def test_validate_config_is_called_on_init(monkeypatch, slotmaster_factory):
    def mock_validate_config(*args, **kwargs):
        raise SlotMasterTestError

    monkeypatch.setattr(slot_strategy.ZkSlotLockStrategyMixin, 'validate_slotmaster_config', mock_validate_config)
    monkeypatch.setattr(mtzc, 'get_zk', get_zk)

    with pytest.raises(SlotMasterTestError):
        slotmaster_factory()


def test_validate_config_required_options_check(slotmaster):
    for option in slot_strategy.SLOTMASTER_REQUIRED_OPTS:
        value = slotmaster.master_config.pop(option)
        with pytest.raises(mde.InvalidConfig):
            slotmaster.validate_slotmaster_config()
        slotmaster.master_config[option] = value


def test_validate_slots_is_called_on_validate_config(slotmaster, monkeypatch):
    def mock_validate_slots(*args, **kwargs):
        raise SlotMasterTestError

    monkeypatch.setattr(slotmaster, 'validate_slots', mock_validate_slots)

    with pytest.raises(SlotMasterTestError):
        slotmaster.validate_slotmaster_config()


def test_validate_slots(slotmaster):
    slotmaster.master_config.slots = 'not_digit_slots'
    with pytest.raises(mde.InvalidConfig):
        slotmaster.validate_slots()

    slotmaster.master_config.slots = -1
    with pytest.raises(mde.InvalidConfig):
        slotmaster.validate_slots()

    slotmaster.master_config.slots = 0
    with pytest.raises(mde.InvalidConfig):
        slotmaster.validate_slots()


def test_stop_on_exception(slotmaster, monkeypatch):
    def mock_run(*args, **kwargs):
        raise Exception("Exception")

    def mock__initiate_stop(*args, **kwargs):
        raise SlotMasterTestError

    monkeypatch.setattr(slotmaster, 'run', mock_run)
    monkeypatch.setattr(slotmaster, '_initiate_stop', mock__initiate_stop)
    monkeypatch.setattr(slotmaster, 'start_daemon_services', lambda: True)

    with pytest.raises(SlotMasterTestError):
        slotmaster.start()


def test_start_operations_order(slotmaster, monkeypatch):
    order = {}

    def mock_start_daemon_services(*args, **kwargs):
        order['start_daemon_services'] = len(order.keys())

    def mock_await_startup_lock(*args, **kwargs):
        order['await_startup_lock'] = len(order.keys())

    def mock_run(*args, **kwargs):
        order['run'] = len(order.keys())

    monkeypatch.setattr(slotmaster, 'start_daemon_services', mock_start_daemon_services)
    monkeypatch.setattr(slotmaster, 'await_startup_lock', mock_await_startup_lock)
    monkeypatch.setattr(slotmaster, 'run', mock_run)

    slotmaster.start()
    assert order['start_daemon_services'] < order['await_startup_lock'] < order['run']


def test_get_slot_lock(slotmaster):
    lock_path = '{}/{}'.format(slotmaster.lock_path, 1)
    lock = slotmaster.zk.Lock(
        path=lock_path,
        identifier='test',
    )
    lock.acquire()

    slotmaster.lock = 'not None'
    result = slotmaster.get_slot_lock(1)
    assert result is False
    assert slotmaster.lock is None

    result = slotmaster.get_slot_lock(2)
    assert result is True
    assert slotmaster.lock is not None


def test_await_lock_checks_all_slots(slotmaster, monkeypatch):
    values = {}

    def mock_get_slot_lock(slot, *args, **kwargs):
        values[slot] = True
        if values.get(1) and values.get(2) and values.get(3):
            slotmaster.shutdown.set()
        return False

    monkeypatch.setattr(slotmaster, 'get_slot_lock', mock_get_slot_lock)

    slotmaster.await_startup_lock()
    assert len(values.keys()) == 3


def test_await_lock_awaits_if_not_locked(slotmaster, monkeypatch):
    def mock_get_slot_lock(slot, *args, **kwargs):
        return False

    def mock_await_shutdown(*args, **kwargs):
        raise SlotMasterTestError

    monkeypatch.setattr(slotmaster, 'get_slot_lock', mock_get_slot_lock)
    monkeypatch.setattr(slotmaster, 'await_shutdown', mock_await_shutdown)

    with pytest.raises(SlotMasterTestError):
        slotmaster.await_startup_lock()


def test_await_lock_returns_if_locked(slotmaster, monkeypatch):
    def mock_get_slot_lock(slot, *args, **kwargs):
        return True

    def mock_await_shutdown(*args, **kwargs):
        raise SlotMasterTestError

    monkeypatch.setattr(slotmaster, 'get_slot_lock', mock_get_slot_lock)
    monkeypatch.setattr(slotmaster, 'await_shutdown', mock_await_shutdown)

    assert slotmaster.await_startup_lock()


def test_await_lock_returns_if_shutdown(slotmaster, monkeypatch):
    def mock_get_slot_lock(slot, *args, **kwargs):
        return True

    def mock_await_shutdown(*args, **kwargs):
        return True

    monkeypatch.setattr(slotmaster, 'get_slot_lock', mock_get_slot_lock)
    monkeypatch.setattr(slotmaster, 'await_shutdown', mock_await_shutdown)

    slotmaster.shutdown.set()
    assert slotmaster.await_startup_lock()
