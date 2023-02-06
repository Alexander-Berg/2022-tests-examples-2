import pytest

from taxi.conf import settings
from taxi.internal.yt_replication import consts as replication_consts
from taxi.internal.yt_tools import command_wrapper


NO_ARGS_COMMANDS = ()


class FakeParser(object):
    def __init__(self):
        self.calls = 0

    def add_argument(self, *args, **kwargs):
        self.calls += 1


class AttrCatcher(Exception):
    pass


class FakeArgs(object):
    def __getattr__(self, item):
        raise AttrCatcher


FakeArgs = FakeArgs()


MAP_REDUCE = ('mr_1', 'mr_2')
RUNTIME = ('runtime_1', 'runtime_2')


@pytest.mark.config(YT_REPLICATION_CLUSTERS=MAP_REDUCE,
                    YT_REPLICATION_RUNTIME_CLUSTERS=RUNTIME)
@pytest.mark.parametrize(
    'command_name', sorted(command_wrapper._COMMANDS.keys())
)
@pytest.mark.asyncenv('blocking')
def test_commands(monkeypatch, command_name):
    monkeypatch.setattr(settings, 'YT_CLUSTER_GROUPS', {
        replication_consts.MAP_REDUCE_GROUP: MAP_REDUCE,
        replication_consts.RUNTIME_GROUP: RUNTIME,
    })

    command_object = command_wrapper._COMMANDS[command_name]
    assert issubclass(command_object, command_wrapper.BaseCommand)

    fake_parser = FakeParser()
    command_object.configure(fake_parser)

    if command_name not in NO_ARGS_COMMANDS:
        assert fake_parser.calls
        with pytest.raises(AttrCatcher):
            command_object.handler(FakeArgs)
    else:
        assert not fake_parser.calls
