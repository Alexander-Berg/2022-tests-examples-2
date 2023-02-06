import pytest

from metrika.admin.python.cms.judge.lib.decider.checks import check_neighborhoods
from metrika.admin.python.cms.judge.lib.decider.decision import Decision
from metrika.admin.python.cms.lib.agent import client
from metrika.admin.python.cms.lib.agent.steps.state import State
from metrika.pylib.structures.dotdict import DotDict


class AgentMock:
    def __init__(self, ping_ok=True, status_ok=True, state_ok=True):
        self.ping_ok = ping_ok
        self.status_ok = status_ok
        self.state_ok = state_ok

    def ping(self):
        return self.ping_ok

    def get_status(self):
        if self.status_ok:
            return {'state': State.SUCCESS if self.state_ok else State.FAIL, 'reason': 'Check'}
        else:
            raise Exception()


def test_check_neighborhoods_ok(decider_mock, monkeypatch):
    monkeypatch.setattr(client, 'get_agent', lambda *args, **kwargs: AgentMock())
    assert check_neighborhoods(decider_mock(neighborhoods=['1'], config=DotDict(agent_port=1))) is None


@pytest.mark.parametrize('agent_kwargs, reason', [
    pytest.param({'ping_ok': False}, 'Ping neighborhood failed', id='ping fail'),
    pytest.param({'status_ok': False}, 'Unable to get neighborhood state', id='status fail'),
    pytest.param({'state_ok': False}, 'Check', id='state fail')
])
def test_check_neighborhoods_error(decider_mock, monkeypatch, agent_kwargs, reason):
    monkeypatch.setattr(client, 'get_agent', lambda *args, **kwargs: AgentMock(**agent_kwargs))
    decider = decider_mock(neighborhoods=['1'], config=DotDict(agent_port=1))
    assert check_neighborhoods(decider) == Decision.IN_PROGRESS
    assert decider.audit[-1]['reason'] == reason
