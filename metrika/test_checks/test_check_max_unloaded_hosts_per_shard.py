import pytest

from metrika.admin.python.cms.judge.lib.decider.checks import check_max_unloaded_hosts_per_shard
from metrika.admin.python.cms.judge.lib.decider.decision import Decision


def test_check_max_unloaded_hosts_per_shard_all_loaded(decider_mock):
    assert check_max_unloaded_hosts_per_shard(decider_mock(unloaded_hosts=[])) is None


def test_check_max_unloaded_hosts_per_shard_unloaded_from_other_shard(decider_mock):
    assert check_max_unloaded_hosts_per_shard(decider_mock(
        max_unloaded_hosts_per_shard=1,
        shard_id=1,
        unloaded_hosts=list(range(2, 5)),
        unloaded_hosts_info=[{'shard_id': str(i)} for i in range(2, 5)],
    )) is None


@pytest.mark.parametrize('unloaded, result', [
    (10, Decision.IN_PROGRESS),
    (0, None)
])
def test_check_max_unloaded_hosts_per_shard_from_same_shard(decider_mock, unloaded, result):
    assert check_max_unloaded_hosts_per_shard(decider_mock(
        max_unloaded_hosts_per_shard=1,
        shard_id='1',
        unloaded_hosts=list(range(unloaded)),
        unloaded_hosts_info=[{'shard_id': '1'}] * unloaded,
    )) is result
