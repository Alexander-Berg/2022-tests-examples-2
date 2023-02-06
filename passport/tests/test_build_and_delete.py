# -*- coding: utf-8 -*-
import os
import tempfile
from unittest import TestCase

from passport.backend.library.nginx_config_generator import (
    BaseConfig,
    build_configs,
    delete_configs,
)
from passport.backend.library.nginx_config_generator.test.utils import (
    assert_configs_ok,
    FakeEnvironment,
)
import yatest.common as yc


class Config1(BaseConfig):
    _cert_names = {'localhost': {'production': 'cert1'}}
    _server_names = {'localhost': {'production': ['servername1.yandex.ru', 'm.servername1.yandex.ru']}}
    _slb_ips = {'localhost': {'production': ['10.0.0.1', '10.0.0.2']}}


CONFIG_CLASSES_WITH_PROPERTIES = {
    0: Config1,
}


class TestBuildAndDelete(TestCase):
    def setUp(self):
        self.env = FakeEnvironment()
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_ok(self):
        expected_dir = yc.source_path('passport/backend/library/nginx_config_generator/tests/expected_configs')
        config_dir = tempfile.mkdtemp()
        build_configs(
            config_classes_with_priorities=CONFIG_CLASSES_WITH_PROPERTIES,
            config_dir=config_dir,
        )
        assert_configs_ok(actual_dir=config_dir, expected_dir=expected_dir)

        # Если конфиги сгенерились корректно - удалим их и проверим, что не осталось неудалённых хвостов
        delete_configs(
            config_classes_with_priorities=CONFIG_CLASSES_WITH_PROPERTIES,
            config_dir=config_dir,
        )
        assert os.listdir(config_dir) == []
