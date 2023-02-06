# -*- coding: utf-8 -*-
from contextlib import contextmanager

from passport.backend.api.app import create_app
from passport.backend.api.test.views import ViewsTestEnvironment
from passport.backend.api.yasms.api import Yasms
from passport.backend.api.yasms.utils import get_account_by_uid
from passport.backend.core.builders.blackbox.blackbox import Blackbox as BlackboxBuilder
from passport.backend.core.builders.blackbox.faker.blackbox import BlackboxYasmsConfigurator
from passport.backend.core.builders.yasms.yasms import YaSms as YasmsBuilder
from passport.backend.core.env.env import Environment
from passport.backend.core.logging_utils.loggers import StatboxLogger
from passport.backend.core.models.phones.faker import PhoneIdGeneratorFaker
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_hosts,
)
from passport.backend.core.test.test_utils.utils import (
    PassportTestCase,
    settings_context,
)
from passport.backend.utils.common import merge_dicts


BLACKBOX_URL = u'http://blac.kb.ox/'
YASMS_SENDER = u'test-yasms-sender'
YASMS_URL = u'http://ya.s.ms/'


class BaseYasmsTestCase(PassportTestCase):
    _DEFAULT_SETTINGS = dict(
        BLACKBOX_ATTRIBUTES=tuple(),
        BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=tuple(),
        HOSTS=mock_hosts(),
        **mock_counters()
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self._blackbox_builder = BlackboxBuilder(BLACKBOX_URL)
        self._yasms_builder = YasmsBuilder(sender=YASMS_SENDER, url=YASMS_URL)
        self._yasms = Yasms(
            self._blackbox_builder,
            self._yasms_builder,
            self._build_env(),
        )
        self._statbox = StatboxLogger()

        self.env.grants.set_grants_return_value({})

        self._phone_id_generator_faker = PhoneIdGeneratorFaker()
        self.__patches = [
            self._phone_id_generator_faker,
        ]
        for patch in self.__patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        self.env.stop()
        del self._blackbox_builder
        del self._yasms_builder
        del self._yasms
        del self._statbox
        del self._phone_id_generator_faker
        del self.__patches
        del self.env

    def run(self, result=None):
        with self._default_settings():
            with create_app().test_request_context():
                super(BaseYasmsTestCase, self).run(result)

    def debug(self):
        with self._default_settings():
            with create_app().test_request_context():
                super(BaseYasmsTestCase, self).debug()

    def _init_blackbox_yasms_configurator(self):
        return BlackboxYasmsConfigurator(self.env.blackbox)

    def _get_account_by_uid(self, uid):
        return get_account_by_uid(uid, self._blackbox_builder)

    @staticmethod
    def _build_env():
        return Environment()

    @contextmanager
    def _default_settings(self, **settings):
        with settings_context(**merge_dicts(self._DEFAULT_SETTINGS, settings)):
            yield
