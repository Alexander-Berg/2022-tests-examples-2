import platform
import subprocess
from typing import NamedTuple

import pytest

ALLOWED_COMMANDS = ['git', 'arc', 'dpkg-deb', 'equivs-build']

# To avoid subprocess call in tests
platform.uname()

try:
    import yatest.common

    def is_arcadia_binary(path: str) -> bool:
        return path.startswith(yatest.common.build_path())


except ImportError:

    def is_arcadia_binary(path: str) -> bool:
        return False


class Result(NamedTuple):
    exit_code: int
    message: str
    stdio: str


@pytest.fixture(autouse=True)
def commands_mock(monkeypatch, mock):
    """Mock subprocess commands

    Usage:

    def test_something(commands_mock):
        @commands_mock('ls')
        def ls(args, **kwargs):
            return 'dir\nfile'

        data = utils.sh(['ls', '-l'], output=True)
        assert data == 'dir\nfile\n'
        calls = ls.calls
        assert len(calls) == 1
        assert calls[0]['args'] == ['ls', '-l']

        @commands_mock('debuild')
        def debuild(args, **kwargs):
            return 3

        with pytest.raises(utils.ShellError) as exc:
            data = utils.sh(['debuild', '-b'])
        assert exc.value.subject.endswith('exited with code 3')

    """
    mock_commands = {}
    errors = []

    class Popen(subprocess.Popen):
        def __init__(self, args, **kwargs):
            error_message = None
            if not isinstance(args, (list, tuple)):
                error_message = 'args is not list or tuple'
            elif not args:
                error_message = 'args empty'
            elif args[0] in mock_commands:
                try:
                    result = mock_commands[args[0]](args, **kwargs)
                except Exception as exc:
                    errors.append(exc)
                    raise
                if isinstance(result, str):
                    args = ['echo', result]
                elif isinstance(result, int):
                    args = [
                        'python',
                        '-c',
                        'import sys;sys.exit({})'.format(result),
                    ]
                elif isinstance(result, Result):
                    command = (
                        'import sys;'
                        'print({!r}, file=sys.{});'
                        'sys.exit({})'
                    ).format(result.message, result.stdio, result.exit_code)
                    args = ['python3', '-c', command]
                elif isinstance(result, tuple):
                    args = result
                else:
                    error_message = 'wrong value %r' % result
            elif is_arcadia_binary(args[0]):
                pass
            elif args[0] not in ALLOWED_COMMANDS:
                error_message = 'bad command %s' % args[0]
            if error_message:
                errors.append(error_message)
                raise subprocess.SubprocessError(error_message)
            super().__init__(args, **kwargs)

    monkeypatch.setattr('subprocess.Popen', Popen)

    class CommandsMock:
        def __call__(self, command):
            def _wraps(func):
                assert command not in mock_commands
                func = mock(func)
                mock_commands[command] = func
                return func

            return _wraps

        @staticmethod
        def result(exit_code, message, to_stderr=False):
            return Result(
                exit_code=exit_code,
                message=message,
                stdio='stderr' if to_stderr else 'stdout',
            )

        @staticmethod
        def pop_errors():
            nonlocal errors
            popped_errors = errors[:]
            errors = []
            return popped_errors

    yield CommandsMock()

    assert not errors
