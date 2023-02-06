import pytest

from metrika.admin.python.cms.judge.lib.decider.checks import check_max_tasks_per_host
from metrika.admin.python.cms.judge.lib.decider.decision import Decision


def test_check_max_tasks_per_host_from_other_host(decider_mock, client_mock):
    assert check_max_tasks_per_host(decider_mock(
        max_active_tasks_per_host=1,
        host='1',
        client=client_mock([{'walle_hosts': [str(i)]} for i in range(2, 5)])
    )) is None


@pytest.mark.parametrize('unloaded, result', [
    (10, Decision.IN_PROGRESS),
    (0, None)
])
def test_check_max_tasks_per_host_from_same_host(decider_mock, client_mock, unloaded, result):
    assert check_max_tasks_per_host(decider_mock(
        max_active_tasks_per_host=1,
        host='1',
        client=client_mock([{'walle_hosts': ['1']}] * unloaded)
    )) is result
