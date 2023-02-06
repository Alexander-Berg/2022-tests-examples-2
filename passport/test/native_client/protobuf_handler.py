# -*- coding: utf-8 -*-
import json

from passport.backend.core.builders.xunistater.faker.fake_xunistater import (
    FakeXunistater,
    TEST_XUNISTATER_OK_RESPONSE,
)
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.library.configurator import Configurator
from passport.backend.logbroker_client.core.run import Runner
from passport.backend.logbroker_client.core.test.native_client.native_client import native_client_header
from passport.backend.utils.logging_mock import LoggingMock


class BaseProtobufHandlerTestCase(PassportTestCase):
    MESSAGE_CLASS = 'TestMessageClass'
    HANDLER_CLASS = None
    TOPIC = 'topic1'
    CONFIGS = [
        'base.yaml',
        'logbroker-client/base.yaml',
        'logbroker-client/testing.yaml',
        'logging.yaml',
        'export.yaml',
        'logbroker-client/export.yaml',
    ]
    EXTRA_EXPORTED_CONFIGS = None

    def build_patches(self):
        self.fake_xunistater = FakeXunistater()
        self.fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
        self._patches.append(self.fake_xunistater)

        self.logging_mock = LoggingMock()
        self._patches.append(self.logging_mock)

    def setUp(self):
        self.config = Configurator(
            name='logbroker-client',
            configs=self.CONFIGS,
        )
        if self.EXTRA_EXPORTED_CONFIGS:
            Runner.patch_config_export(self.config, self.EXTRA_EXPORTED_CONFIGS, 'export.yaml')
        # Костыль, связанный с использованием PassportTestCase
        from passport.backend.core.conf import settings as passport_settings
        passport_settings._settings = None
        passport_settings._options = {}
        self.config.set_as_passport_settings()

        self._patches = []
        self.build_patches()
        for patch in self._patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self._patches):
            patch.stop()

    def _make_header(self, message_class):
        return native_client_header(message_class=message_class, topic=self.TOPIC)

    def process(self, handler, data, message_class=None):
        if message_class is None:
            message_class = self.MESSAGE_CLASS
        header = self._make_header(message_class)
        handler.process(header=header, data=data)

    def assert_xunistater_logged(self, data):
        self.fake_xunistater.requests[0].assert_properties_equal(**data)

    def assert_metrics_logged(self, entries):
        metrics_logger = self.logging_mock.getLogger('logbroker_client.metrics')
        self.assertEqual(metrics_logger.entries, entries)
