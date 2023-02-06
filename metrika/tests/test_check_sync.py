from datetime import datetime
from unittest.mock import Mock

import pytest


def test_sync_all_are_empty(restorer):
    restorer.clickhouse.get_tables_size = Mock(return_value=0)
    restorer.donors_ch.get_tables_size = Mock(return_value=0)
    assert restorer.check_sync(0, datetime.now())[0]


def test_sync_donor_is_empty_but_local_isnt(restorer):
    restorer.clickhouse.get_tables_size = Mock(return_value=1)
    restorer.donors_ch.get_tables_size = Mock(return_value=0)
    with pytest.raises(Exception, match='Donor donor is empty but local CH isn\'t!'):
        restorer.check_sync(0, datetime.now())


def test_sync_all_are_empty_but_old_shard(restorer):
    restorer.new_shard = False
    restorer.clickhouse.get_tables_size = Mock(return_value=0)
    restorer.donors_ch.get_tables_size = Mock(return_value=0)
    with pytest.raises(Exception, match='Donor donor is empty but it\'s not a new shard!'):
        restorer.check_sync(0, datetime.now())


def test_last_sync(restorer):
    restorer.clickhouse.get_tables_size = Mock(side_effect=[0, 1, 100])
    restorer.donors_ch.get_tables_size = Mock(return_value=100)
    last_sync = 0
    sync_changed = datetime.now()
    sync, last_sync, _ = restorer.check_sync(last_sync, sync_changed)
    assert not sync
    assert last_sync == 0

    sync, last_sync, _ = restorer.check_sync(last_sync, sync_changed)
    assert not sync
    assert last_sync == 1

    sync, last_sync, _ = restorer.check_sync(last_sync, sync_changed)
    assert sync
    assert last_sync == 100


def test_sync_hangs(restorer):
    results = [0, 1, 1, 2]
    restorer.clickhouse.get_tables_size = Mock(side_effect=results)
    restorer.donors_ch.get_tables_size = Mock(return_value=100)
    restorer.MAX_HANG_SECONDS = 0
    last_sync = 0
    sync_changed = datetime.now()
    for i in range(len(results) - 1):
        _, last_sync, sync_changed = restorer.check_sync(last_sync, sync_changed)
    assert restorer.juggler.send_event.call_args[0][0] == 'CRIT'
    restorer.check_sync(last_sync, sync_changed)
    assert restorer.juggler.send_event.call_args[0][0] == 'OK'


def test_sync_decreases(restorer):
    results = [0, 1, 2, 1]
    restorer.clickhouse.get_tables_size = Mock(side_effect=results)
    restorer.donors_ch.get_tables_size = Mock(return_value=100)
    restorer.MAX_HANG_SECONDS = 0
    last_sync = 0
    sync_changed = datetime.now()
    for i in range(len(results) - 1):
        _, last_sync, sync_changed = restorer.check_sync(last_sync, sync_changed)
    assert restorer.juggler.send_event.call_args[0][0] == 'OK'
    restorer.check_sync(last_sync, sync_changed)
    assert restorer.juggler.send_event.call_args[0][0] == 'CRIT'


def test_wait_sync_exceptions(restorer):
    results = [Exception()] * 5 + [[True, None, None]]
    restorer.check_sync = Mock(side_effect=results)
    restorer.SYNC_SLEEP = 1
    restorer.wait_sync()
    assert restorer.check_sync.call_count == len(results)
