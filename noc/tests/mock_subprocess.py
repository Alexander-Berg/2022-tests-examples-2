import pathlib
import shlex
from typing import Any, List, Tuple
import unittest
from unittest import mock

from tests import input_parser
import commit_api


def shlex_join(split_command: List[str]) -> str:
    """Join splitted shell command parts.

    Backport `shlex.join` from Python 3.8.
    """
    return ' '.join(shlex.quote(arg) for arg in split_command)


class FakeProcess:
    def __init__(self, command_mock_data: input_parser.CommandMockData) -> None:
        self.command_mock_data = command_mock_data

    def communicate(self, *args: Any, **kwargs: Any) -> Tuple[bytes, bytes]:
        if self.command_mock_data.stdout is not None:
            stdout = self.command_mock_data.stdout.encode()
        else:
            stdout = b""
        if self.command_mock_data.stderr is not None:
            stderr = self.command_mock_data.stderr.encode()
        else:
            stderr = b""
        return (stdout, stderr)

    def wait(self, timeout=None) -> int:
        return self.command_mock_data.exit_code

    @property
    def returncode(self) -> int:
        return self.command_mock_data.exit_code

    @property
    def pid(self) -> int:
        return 0


class MockedSubprocessTestCase(unittest.TestCase):

    def get_input_path(self) -> str:
        """Return input file path for the current test."""
        # self.id() returns something like "tests.test_module.TestCaseClass.test_method"
        parts = self.id().split(".")
        if parts[0] != "tests":
            raise RuntimeError("Test id doesn't starts with 'tests.'")
        input_file_name = "-".join(parts[1:]) + ".txt"
        input_path = pathlib.Path(__file__).parent.absolute() / ".inputs" / input_file_name
        return str(input_path)

    def fake_subprocess_popen(self, args: List[str], *fargs: Any, **fkwargs: Any) -> FakeProcess:
        actual = shlex_join(args)
        if not self.command_mocks:
            self.fail(f"Executed command is `$ {actual}', but no more commands expected")
        command_mock_data = self.command_mocks.pop(0)
        if args != command_mock_data.command:
            expected = shlex_join(command_mock_data.command)
            self.fail(f"Executed command is `$ {actual}', but want `$ {expected}'")
        return FakeProcess(command_mock_data)

    def clear_lru_caches(self):
        commit_api.get_systemd_analyze_dump.cache_clear()
        commit_api.get_systemd_show.cache_clear()

    def setUp(self) -> None:
        self.subprocess_popen_patcher = mock.patch("subprocess.Popen", new=self.fake_subprocess_popen)
        self.subprocess_popen_patcher.start()
        self.getpass_getuser_patcher = mock.patch("getpass.getuser", return_value="test-user")
        self.getpass_getuser_patcher.start()
        self.command_mocks = input_parser.parse_input_file(self.get_input_path())
        self.clear_lru_caches()
        super().setUp()

    def tearDown(self) -> None:
        self.subprocess_popen_patcher.stop()
        self.getpass_getuser_patcher.stop()
        self.clear_lru_caches()
        super().tearDown()

        if self.command_mocks:
            unexecuted_commands = "\n".join(
                ("$ " + shlex_join(command_mock_data.command))
                for command_mock_data in self.command_mocks
            )
            self.fail(f"Unexecuted commands:\n{unexecuted_commands}")
