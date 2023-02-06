# -*- coding: utf-8 -*-
from nose.tools import eq_
from nose_parameterized import parameterized
from passport.backend.core.test.test_utils import with_settings_hosts

from .base import (
    BaseHistoryParserTestCase,
    TEST_EMAIL,
    TEST_HISTORYDB_API_URL,
    TEST_MASKED_EMAIL,
    TEST_MASKED_PUNICODE_EMAIL,
    TEST_PUNICODE_EMAIL,
)


@with_settings_hosts(
    HISTORYDB_API_URL=TEST_HISTORYDB_API_URL,
)
class HistoryParseRestoreTestCase(BaseHistoryParserTestCase):
    def test_restore_entities_flushed(self):
        events = self.make_historydb_events(
            {
                'action': 'restore_entities_flushed',
                'phone.12329391.action': 'deleted',
                'phone.12329391.number': '+79010010000',
                'info.hinta': None,
                'info.flushed_entities': 'phones,hint,social_profiles,emails',
                'info.hintq': None,
                'info.totp_update_time': None,
                'phone.rm': '+7 901 001-00-00',
                'info.totp_secret': None,
                'phones.secure': '0',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()
        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'restore_entities_flushed')
        self.assert_events_equal(
            parsed_events[0].actions,
            [
                {
                    'type': 'secure_phone_unset',
                    'phone_unset': '+7 901 ***-**-00',
                },
                {
                    'type': 'email_remove_all',
                },
                {
                    'type': 'questions_remove',
                },
                {
                    'type': 'totp_disabled',
                },
            ],
        )

    @parameterized.expand([(TEST_EMAIL, TEST_MASKED_EMAIL),
                           (TEST_PUNICODE_EMAIL, TEST_MASKED_PUNICODE_EMAIL),
                           ])
    def test_restore_entities_flushed_new_email_validator(self, email, masked_email):
        events = self.make_historydb_events(
            {
                'action': 'restore_entities_flushed',
                'phone.12329391.action': 'deleted',
                'phone.12329391.number': '+79010010000',
                'info.hinta': None,
                'info.flushed_entities': 'phones,hint,social_profiles,emails',
                'info.hintq': None,
                'info.totp_update_time': None,
                'phone.rm': '+7 901 001-00-00',
                'info.totp_secret': None,
                'phones.secure': '0',
                'email.369': 'deleted',
                'email.369.address': email,
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()
        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'restore_entities_flushed')
        self.assert_events_equal(
            parsed_events[0].actions,
            [
                {
                    'type': 'email_remove',
                    'email_unbind': masked_email,
                },
                {
                    'type': 'questions_remove',
                },
                {
                    'type': 'secure_phone_unset',
                    'phone_unset': '+7 901 ***-**-00',
                },
                {
                    'type': 'totp_disabled',
                },
            ],
        )

    def test_restore_by_hint(self):
        events = self.make_historydb_events(
            {
                'info.password_quality': '100',
                'info.glogout': '1461247590',
                'info.password_update_time': '1461247590',
                'info.password': '$1$1skOY7vc$IygMm8QK5dI.2Jd/2mmSB1',
                'info.used_question': '12:\u0424\u0430\u043c\u0438\u043b\u0438\u044f '
                                      '\u0432\u0430\u0448\u0435\u0433\u043e '
                                      '\u043b\u044e\u0431\u0438\u043c\u043e\u0433\u043e '
                                      '\u043c\u0443\u0437\u044b\u043a\u0430\u043d\u0442\u0430',
                'action': 'restore_passed_by_hint',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'restore')
        self.assert_events_equal(
            parsed_events[0].actions,
            [
                {
                    'type': 'global_logout',
                },
                {
                    'type': 'password_change',
                },
                {
                    'type': 'restore',
                    'restore_by': 'hint'
                },
            ],
        )

    @parameterized.expand([(TEST_EMAIL, TEST_MASKED_EMAIL),
                           (TEST_PUNICODE_EMAIL, TEST_MASKED_PUNICODE_EMAIL),
                           ])
    def test_restore_by_email(self, email, masked_email):
        events = self.make_historydb_events(
            {
                'info.glogout': '1461336521',
                'info.password_update_time': '1461336521',
                'info.password': '$1$hr/vSWCd$Vel4ZIWGYx/UjvCJsuUpY/',
                'info.used_email': email,
                'action': 'restore_passed_by_email',
                'consumer': 'passport',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'restore')
        self.assert_events_equal(
            parsed_events[0].actions,
            [
                {
                    'type': 'restore',
                    'restore_by': 'email',
                    'email': masked_email,
                },
                {
                    'type': 'global_logout',
                },
                {
                    'type': 'password_change',
                },
            ],
        )

    def test_restore_by_phone(self):
        events = self.make_historydb_events(
            {
                'action': 'restore_passed_by_phone',
                'info.glogout': '1461335770',
                'info.password_update_time': '1461335770',
                'info.password': '$1$LX/.o8ED$AQo4ePnvAhiBAB3TwaeRP/',
                'info.used_phone': '+7 901 001-00-00',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'restore')
        self.assert_events_equal(
            parsed_events[0].actions,
            [
                {
                    'type': 'global_logout',
                },
                {
                    'type': 'password_change',
                },
                {
                    'type': 'restore',
                    'restore_by': 'phone',
                    'phone': '+7 901 ***-**-00',
                },
            ],
        )

    def test_restore_by_impossible_phone(self):
        events = self.make_historydb_events(
            {
                'action': 'restore_passed_by_phone',
                'info.glogout': '1461335770',
                'info.password_update_time': '1461335770',
                'info.password': '$1$LX/.o8ED$AQo4ePnvAhiBAB3TwaeRP/',
                'info.used_phone': '+0 000 000-00-00',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'restore')
        self.assert_events_equal(
            parsed_events[0].actions,
            [
                {
                    'type': 'global_logout',
                },
                {
                    'type': 'password_change',
                },
                {
                    'type': 'restore',
                    'restore_by': 'phone',
                    'phone': '+0 000 ***-**-00',
                },
            ],
        )

    def test_restore_by_email_with_forced_password_change(self):
        events = self.make_historydb_events(
            {
                'sid.login_rule': '8|1',
                'phone.12464159.operation.210917.action': 'deleted',
                'phone.12464159.number': '+78130001100',
                'phone.12464159.confirmed': '1456924342',
                'phone.12464159.operation.210917.security_identity': '1',
                'phone.12464159.secured': '1456924342',
                'phone.12464159.action': 'changed',
                'phone.12464159.operation.210917.type': 'securify',
                'info.password_quality': '60',
                'info.glogout': '1456924342',
                'info.password_update_time': '1456924342',
                'phone.add': '+7 813 000-11-00',
                'info.password': '$1$xL7RJ5kP$dr/yaApp4fQ4wadmZHk7M1',
                'action': 'restore_passed_by_email',
                'phones.secure': '12464159',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'restore')
        self.assert_events_equal(
            parsed_events[0].actions,
            [
                {
                    'type': 'global_logout',
                },
                {
                    'type': 'password_change',
                },
                {
                    'type': 'restore',
                    'restore_by': 'email',
                },
                {
                    'type': 'secure_phone_set',
                    'phone_set': '+7 813 ***-**-00',
                },
            ],
        )
