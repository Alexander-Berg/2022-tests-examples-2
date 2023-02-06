import enum

from taxi.util import decorators

from metrics_processing.models import action_abc
from metrics_processing.utils import action_journal


@enum.unique
class ActionTypes(enum.Enum):
    TEST_ACTION_TYPE = 'test'


class Counter:
    def __init__(self):
        self._value = 0

    def inc(self):
        self._value += 1


class Stats:
    def get_counter(self, *args, **kwargs):
        return Counter()


class Context:
    stats = Stats()


class TestAction(action_abc.AbstractAction):
    ACTION_TYPE = ActionTypes.TEST_ACTION_TYPE

    @decorators.store_calls
    async def _do(self, *args, **kwargs):
        pass

    @decorators.store_calls
    def _modify_local_context(self):
        pass


# pylint: disable=no-member,protected-access
async def test_action_journal():
    journal = action_journal.ActionJournal()
    context = Context()

    first_action = TestAction(app=context)
    second_action = TestAction(app=context)

    args_1, kwargs_1 = (1, 1, 1), {'a': 1, 'b': 1, 'c': 1}
    args_2, kwargs_2 = (2, 2, 2), {'x': 2, 'y': 2, 'z': 2}

    for _ in range(2):  # ensure action applied only once
        await journal.do_action(first_action, *args_1, **kwargs_1)
        await journal.do_action(second_action, *args_2, **kwargs_2)

        assert first_action.is_done
        assert second_action.is_done
        assert not first_action.is_done_locally
        assert not second_action.is_done_locally
        assert len(TestAction._do.calls) == 2
        assert TestAction._do.calls[0].args[1:] == args_1
        assert TestAction._do.calls[0].kwargs == kwargs_1
        assert TestAction._do.calls[1].args[1:] == args_2
        assert TestAction._do.calls[1].kwargs == kwargs_2
        assert first_action._rules_applied._value == 1
        assert second_action._rules_applied._value == 1
        assert not TestAction._modify_local_context.calls

    for _ in range(2):
        journal.modify_local_context()
        assert first_action.is_done_locally
        assert second_action.is_done_locally
        assert len(TestAction._modify_local_context.calls) == 2
