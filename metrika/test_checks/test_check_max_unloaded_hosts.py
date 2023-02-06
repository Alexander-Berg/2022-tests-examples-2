import pytest

from metrika.admin.python.cms.judge.lib.decider.checks import check_max_unloaded_hosts
from metrika.admin.python.cms.judge.lib.decider.decision import Decision


@pytest.mark.parametrize('unloaded, result', [
    (10, Decision.IN_PROGRESS),
    (0, None)
])
def test_check_max_unloaded_hosts(decider_mock, unloaded, result):
    assert check_max_unloaded_hosts(decider_mock(max_unloaded_hosts=1, unloaded_hosts=list(range(unloaded)))) == result
