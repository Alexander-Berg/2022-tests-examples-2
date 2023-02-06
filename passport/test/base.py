# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os.path

from passport.backend.core.builders.blackbox.faker.blackbox import FakeBlackbox
from passport.backend.core.builders.mail_apis.faker import FakeHuskyApi
from passport.backend.core.builders.yasms.faker import FakeYaSms
from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.logging_utils.faker.fake_tskv_logger import (
    FamilyLoggerFaker,
    StatboxLoggerFaker,
)
from passport.backend.core.logging_utils.loggers import StatboxLogger
from passport.backend.core.mailer.faker import FakeMailer
from passport.backend.core.test.events import EventLoggerFaker
from passport.backend.core.test.test_utils.utils import PassportTestCase
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_TICKET,
)
from passport.backend.core.ydb.faker.ydb import FakeYdb
from passport.backend.dbscripts import templating


class TestCase(PassportTestCase):
    """
    Базовый класс для тестирования сборщика.
    """
    def setUp(self):
        LazyLoader.flush()

        template_base_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)),
            ),
            'templates',
        )
        templating.initialize(template_base_dir)

        self.__patches = []
        self._statbox_faker = StatboxLoggerFaker()
        self._event_logger_faker = EventLoggerFaker()
        self._family_log_faker = FamilyLoggerFaker()
        self._db_faker = FakeDB()
        self._blackbox_faker = FakeBlackbox()
        self._mailer_faker = FakeMailer()
        self._yasms_builder_faker = FakeYaSms()
        self._husky_api = FakeHuskyApi()
        self._tvm_credential_manager_faker = FakeTvmCredentialsManager()
        self.fake_ydb = FakeYdb()
        self.fake_ydb.set_execute_return_value([])

        self._tvm_credential_manager_faker.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    str(TEST_CLIENT_ID): {
                        'alias': 'yasms',
                        'ticket': TEST_TICKET,
                    },
                    str(TEST_CLIENT_ID * 2): {
                        'alias': 'blackbox',
                        'ticket': TEST_TICKET,
                    },
                    str(TEST_CLIENT_ID * 3): {
                        'alias': 'husky',
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )

        self.__patches = (
            self._statbox_faker,
            self._event_logger_faker,
            self._family_log_faker,
            self._db_faker,
            self._blackbox_faker,
            self._mailer_faker,
            self._yasms_builder_faker,
            self._husky_api,
            self._tvm_credential_manager_faker,
            self.fake_ydb,
        )
        for patch in self.__patches:
            patch.start()

        self._statbox = StatboxLogger(is_harvester=True)

        self._setup_statbox_templates()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()

    def _setup_statbox_templates(self):
        pass

    def _phone_fmt(self, phone_id, postfix):
        """
        Форма записи события о телефоне в HistoryDB.
        """
        return 'phone.%d.%s' % (phone_id, postfix)

    def _op_fmt(self, phone_id, operation_id, postfix):
        """
        Форма записи события о телефонной операции в HistoryDB.
        """
        return self._phone_fmt(phone_id, 'operation.%d.%s' % (operation_id, postfix))

    def _events(self, uid, events):
        return tuple({'uid': str(uid), 'name': name, 'value': value} for name, value in events.items())
