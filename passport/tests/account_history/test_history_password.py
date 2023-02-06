# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.core.test.test_utils import with_settings_hosts

from .base import (
    BaseHistoryParserTestCase,
    TEST_HISTORYDB_API_URL,
)


@with_settings_hosts(
    HISTORYDB_API_URL=TEST_HISTORYDB_API_URL,
)
class HistoryParsePasswordTestCase(BaseHistoryParserTestCase):
    def test_password_change(self):
        events = self.make_historydb_events(
            {
                'info.web_sessions_revoked': '1463589034',
                'info.password_update_time': '1463589034',
                'info.password': '$1$W.ICQca.$n1PBpx8Ky0LLLcN3s6UDg0',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'password')
        self.assert_events_equal(
            parsed_events[0].actions,
            [
                {
                    'type': 'password_change',
                },
                {
                    'type': 'web_sessions_revoked',
                },
            ],
        )

    def test_force_password_change(self):
        """Принудительная смена пароля, добавляется новый телефон"""
        events = self.make_historydb_events(
            {
                'action': 'change_password',
                'sid.login_rule': '8|1',
                'phone.12830347.confirmed': '1461747980',
                'phone.12830347.operation.289675.type': 'bind',
                'phone.12830347.operation.289675.action': 'deleted',
                'phone.12830347.operation.289675.security_identity': '1',
                'phone.12830347.action': 'changed',
                'phone.12830347.secured': '1461747980',
                'phone.12830347.number': '+79010010000',
                'phone.12830347.bound': '1461747980',
                'phone.add': '+7 901 001-00-00',
                'phones.secure': '12830347',
                'info.glogout': '1461747980',
                'info.password_update_time': '1461747980',
                'info.password': '$1$Nky1FGgW$feInYYTiKg3f2GTHMQciH1',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'forced_password_change')
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
                    'type': 'secure_phone_set',
                    'phone_set': '+7 901 ***-**-00',
                },
            ],
        )

    def test_force_password_change_phone_confirm(self):
        """Принудительная смена пароля, подтверждаем старый телефон"""
        events = self.make_historydb_events(
            {
                'action': 'change_password',
                'sid.login_rule': '8|1',
                'info.glogout': '1461748022',
                'info.password_update_time': '1461748022',
                'phone.12830347.action': 'changed',
                'phone.12830347.confirmed': '1461748022',
                'phone.12830347.number': '+79010010000',
                'info.password': '$1$u8yFszCl$wWQPGqE7EM/k/P/5d1Aaj0',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'forced_password_change')
        self.assert_events_equal(
            parsed_events[0].actions,
            [
                {
                    'type': 'global_logout',
                },
                {
                    'type': 'password_change',
                },
            ],
        )

    def test_force_password_change_phone_replace_with_quarantine(self):
        """Принудительная смена пароля, замена телефона с карантином"""
        events = self.make_historydb_events(
            {
                'action': 'change_password',

                'phone.12820065.action': 'changed',
                'phone.12820065.number': '+79020020000',
                'phone.12820065.confirmed': '1461589858',
                'phone.12820065.bound': '1461589858',
                'phone.12820065.operation.281531.action': 'created',
                'phone.12820065.operation.281531.security_identity': '79020020000',
                'phone.12820065.operation.281531.type': 'mark',
                'phone.12820065.operation.281531.code_confirmed': '1461589858',
                'phone.12820065.operation.281531.phone_id2': '12814667',
                'phone.12820065.operation.281531.started': '1461589858',
                'phone.12820065.operation.281531.password_verified': '1461589858',
                'phone.12820065.operation.281531.finished': '1464181858',

                'phone.12820065.operation.281527.action': 'deleted',
                'phone.12820065.operation.281527.type': 'bind',
                'phone.12820065.operation.281527.security_identity': '79020020000',

                'phone.12814667.number': '+79010010000',
                'phone.12814667.operation.281529.password_verified': '1461589858',
                'phone.12814667.operation.281529.type': 'replace',
                'phone.12814667.operation.281529.finished': '1464181858',  # это маркер
                'phone.12814667.operation.281529.security_identity': '1',
                'phone.12814667.operation.281529.action': 'changed',  # это маркер
                # если есть телефон с такими маркерами, то другой телефон будет секьюрным после карантина

                'info.glogout': '1461589858',
                'info.password_update_time': '1461589858',
                'info.password': '$1$SOZyR560$j/SZZ1XEtuvPKQ7bRF4F20',

                'sid.login_rule': '8|1',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'forced_password_change')
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
                    'type': 'secure_phone_replace',
                    'phone_set': '+7 902 ***-**-00',
                    'phone_unset': '+7 901 ***-**-00',
                    'delayed_until': 1464181858,
                },
            ],
        )
