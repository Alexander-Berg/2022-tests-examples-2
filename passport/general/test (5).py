# -*- coding: utf-8 -*-

from passport.backend.core.logging_utils.faker.fake_tskv_logger import TskvLoggerFaker
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
)
from passport.backend.social.common.chrono import now
from passport.backend.social.common.test.fake_redis_client import (
    FakeRedisClient,
    RedisPatch,
)
from passport.backend.social.common.test.fake_throttle import FakeThrottle
from passport.backend.social.common.test.grants import FakeGrantsConfig
from passport.backend.social.common.test.test_case import TestCase as _TestCase
from passport.backend.social.proxy2.app import (
    create_app,
    prepare_interprocess_environment,
    prepare_intraprocess_environment,
)
from passport.backend.social.proxy2.logging_settings import logging_settings_deinit
from passport.backend.social.proxylib.test import (
    deezer,
    facebook,
    google,
    mail_ru,
    microsoft,
    mts,
    mts_belarus,
    yahoo,
    yandex,
)
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse


_STATBOX_TEMPLATES = {
    'base': {
        'tskv_format': 'social-proxy2-log',
        'unixtime': lambda: str(now.i()),
    },
}


class TestCase(_TestCase):
    def setUp(self):
        super(TestCase, self).setUp()

        self.__patches = []

        fake_objects = {
            '_fake_deezer': deezer.FakeProxy(),
            '_fake_facebook': facebook.FakeProxy(),
            '_fake_mts': mts.FakeProxy(),
            '_fake_mts_belarus': mts_belarus.FakeProxy(),
            '_fake_mail_ru': mail_ru.FakeProxy(),
            '_fake_microsoft': microsoft.FakeProxy(),
            '_fake_google': google.FakeProxy(),
            '_fake_yahoo': yahoo.FakeProxy(),
            '_fake_yandex': yandex.FakeProxy(),
        }
        for fake_name, fake_object in fake_objects.items():
            setattr(self, fake_name, fake_object)
            self.__patches.append(fake_object)

        self._fake_redis = FakeRedisClient()

        self._fake_grants_config = FakeGrantsConfig()

        self._fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self._fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data())

        self._fake_throttle = FakeThrottle()

        self._fake_statbox_friends = FakeStatboxFriendsLogger()

        self.__patches.extend([
            RedisPatch(self._fake_redis),
            self._fake_grants_config,
            self._fake_tvm_credentials_manager,
            self._fake_throttle,
            self._fake_statbox_friends,
        ])

        for patch in self.__patches:
            patch.start()

        prepare_interprocess_environment()
        prepare_intraprocess_environment()
        app = create_app()
        self._client = Client(app, BaseResponse)

    def tearDown(self):
        logging_settings_deinit()
        for patch in reversed(self.__patches):
            patch.stop()
        super(TestCase, self).tearDown()


class FakeStatboxFriendsLogger(TskvLoggerFaker):
    logger_class_module = 'passport.backend.social.proxy2.statbox.StatboxFriendsLogger'
    templates = _STATBOX_TEMPLATES
