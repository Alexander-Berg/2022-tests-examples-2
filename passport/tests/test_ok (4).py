import os
import tempfile
from unittest import TestCase

from nose.tools import eq_
from passport.backend.library.nginx_config_generator.test.utils import (
    assert_configs_ok,
    FakeEnvironment,
)
from passport.backend.passport_nginx_config.build_configs import build
from passport.backend.passport_nginx_config.delete_configs import delete
import yatest.common as yc


class TestBuildAndDelete(TestCase):
    env_name = 'localhost'

    def setUp(self):
        self.env = FakeEnvironment(
            env_name=self.env_name,
            env_type='production',
            hostname='passport-m1.passport.yandex.net',
        )
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_ok(self):
        expected_dir = yc.source_path('passport/backend/passport_nginx_config/tests/expected/%s' % self.env_name)
        config_dir = tempfile.mkdtemp()

        build(config_dir=config_dir)
        assert_configs_ok(actual_dir=config_dir, expected_dir=expected_dir)

        # Если конфиги сгенерились корректно - удалим их и проверим, что не осталось неудалённых хвостов
        delete(config_dir=config_dir)
        eq_(
            os.listdir(config_dir),
            [],
        )


class TestBuildAndDeleteIntranet(TestBuildAndDelete):
    env_name = 'intranet'
