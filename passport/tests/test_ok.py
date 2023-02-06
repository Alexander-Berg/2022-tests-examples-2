import os
import tempfile
from unittest import TestCase

from nose.tools import eq_
from passport.backend.library.nginx_config_generator.test.utils import (
    assert_configs_ok,
    FakeEnvironment,
)
from passport.backend.mobileproxy_nginx.nginx.build_configs import build
from passport.backend.mobileproxy_nginx.nginx.delete_configs import delete
import yatest.common as yc


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
ACTUAL_DIR = os.path.join(ROOT_DIR, 'actual')
EXPECTED_DIR = os.path.join(ROOT_DIR, 'expected')


class TestBuildAndDeleteMobileproxy(TestCase):
    def setUp(self):
        self.env = FakeEnvironment(env_type='production', hostname='mobileproxy-f2.passport.yandex.net')
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_ok(self):
        expected_dir = yc.source_path('passport/backend/mobileproxy_nginx/nginx/tests/expected_mobileproxy/')
        config_dir = tempfile.mkdtemp()

        build(config_dir=config_dir)
        assert_configs_ok(actual_dir=config_dir, expected_dir=expected_dir)

        # Если конфиги сгенерились корректно - удалим их и проверим, что не осталось неудалённых хвостов
        delete(config_dir=config_dir)
        eq_(
            os.listdir(config_dir),
            [],
        )


class TestBuildAndDeleteCertificate(TestCase):
    def setUp(self):
        self.env = FakeEnvironment(env_type='production', hostname='certificate-s2.passport.yandex.net')
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_ok(self):
        expected_dir = yc.source_path('passport/backend/mobileproxy_nginx/nginx/tests/expected_certificate/')
        config_dir = tempfile.mkdtemp()

        build(config_dir=config_dir)
        assert_configs_ok(actual_dir=config_dir, expected_dir=expected_dir)

        # Если конфиги сгенерились корректно - удалим их и проверим, что не осталось неудалённых хвостов
        delete(config_dir=config_dir)
        eq_(
            os.listdir(config_dir),
            [],
        )
