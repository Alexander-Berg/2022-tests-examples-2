# coding: utf-8

from passport.backend.vault.cli.yav_deploy.tests.base import (
    BaseYavDeployTestCase,
    LogMock,
)
from vault_client_deploy.configs import UnsafeMixin


class _TestException(Exception):
    pass


class _TestUnsafeClass(UnsafeMixin):
    def __init__(self, env):
        self.environment = env
        self.failed = False


class Test(BaseYavDeployTestCase):
    def test_unsafe_method_with_failed(self):
        logger = LogMock()
        with self.get_environment('base', logger=logger, type_='development', name='localhost', config_files=['dev.conf']) as env:
            mixin = _TestUnsafeClass(env)
            with mixin.unsafe():
                raise _TestException(u'Тестовое исключение')
            self.assertListEqual(
                logger.entries,
                [(u'Тестовое исключение'.encode('utf-8'), 'ERROR')],
            )
