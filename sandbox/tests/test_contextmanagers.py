import os
import traceback

import mock
import pytest

from sandbox.projects.browser.common.contextmanagers import ExitStack, TempEnvironment


class BrokenContextManager(object):
    def broken_function(self):
        raise ValueError('bla bla bla')

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.broken_function()


class TestExitStack(object):
    def test_exit_raise_error(self):
        with pytest.raises(ValueError, match='bla bla bla') as exc_info:
            with ExitStack() as exit_stack:
                exit_stack.enter_context(BrokenContextManager())
                raise BaseException('wrong error')
        exception_string = ''.join(traceback.format_exception(
            exc_info.type, exc_info.value, exc_info.tb))
        assert 'broken_function' in exception_string


class TestTempEnvironment(object):
    TEST_VAR = 'TEST_VAR'

    @mock.patch.dict(os.environ, clear=True)
    def test_override_var(self):
        os.environ[self.TEST_VAR] = '0'
        with TempEnvironment() as env:
            env.set_var(self.TEST_VAR, '1')
            assert os.environ[self.TEST_VAR] == '1'
            env.set_var(self.TEST_VAR, '2')
            assert os.environ[self.TEST_VAR] == '2'
        assert os.environ[self.TEST_VAR] == '0'

    @mock.patch.dict(os.environ, clear=True)
    def test_override_var_manually(self):
        os.environ[self.TEST_VAR] = '0'
        with TempEnvironment():
            os.environ[self.TEST_VAR] = '1'
        assert os.environ[self.TEST_VAR] == '1'

    @mock.patch.dict(os.environ, clear=True)
    def test_del_var(self):
        os.environ[self.TEST_VAR] = '0'
        with TempEnvironment() as env:
            env.del_var(self.TEST_VAR)
            assert self.TEST_VAR not in os.environ
        assert os.environ[self.TEST_VAR] == '0'

    @mock.patch.dict(os.environ, clear=True)
    def test_new_var(self):
        with TempEnvironment() as env:
            env.set_var(self.TEST_VAR, '1')
            assert os.environ[self.TEST_VAR] == '1'
            env.set_var(self.TEST_VAR, '2')
            assert os.environ[self.TEST_VAR] == '2'
        assert self.TEST_VAR not in os.environ
