import pytest

from metrika.admin.python.cms.judge.lib.decider.checks import check_max_unloaded_hosts_per_cluster
from metrika.admin.python.cms.judge.lib.decider.decision import Decision


def test_check_max_unloaded_hosts_per_cluster_all_loaded(decider_mock):
    assert check_max_unloaded_hosts_per_cluster(decider_mock(unloaded_hosts=[])) is None


def test_check_max_unloaded_hosts_per_cluster_unloaded_from_other_cluster(decider_mock):
    assert check_max_unloaded_hosts_per_cluster(decider_mock(
        max_unloaded_hosts_per_cluster=1,
        cluster='1',
        environment='test',
        unloaded_hosts=list(range(2, 5)),
        unloaded_hosts_info=[{'type': str(i), 'environment': 'test'} for i in range(2, 5)],
    )) is None


@pytest.mark.parametrize('unloaded, result', [
    (10, Decision.IN_PROGRESS),
    (0, None)
])
def test_check_max_unloaded_hosts_per_cluster_from_same_cluster(decider_mock, unloaded, result):
    assert check_max_unloaded_hosts_per_cluster(decider_mock(
        max_unloaded_hosts_per_cluster=1,
        cluster='1',
        environment='test',
        unloaded_hosts=list(range(unloaded)),
        unloaded_hosts_info=[{'type': '1', 'environment': 'test'}] * unloaded,
    )) is result
