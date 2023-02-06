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
class HistoryParsePhoneTestCase(BaseHistoryParserTestCase):
    def test_secure_phone_bind(self):
        """Привязка секьюрного телефона"""
        events = self.make_historydb_events(
            {
                'action': 'secure_bind_commit',
                'info.karma_prefix': '6',
                'phone.12807201.action': 'changed',
                'phone.12807201.bound': '1461244074',
                'phone.12807201.confirmed': '1461244074',
                'phone.12807201.number': '+79010010000',
                'phone.12807201.operation.271791.action': 'deleted',
                'phone.12807201.operation.271791.security_identity': '1',
                'phone.12807201.operation.271791.type': 'bind',
                'phone.12807201.secured': '1461244074',
                'phone.add': '+7 901 001-00-00',
                'phones.secure': '12807201',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'secure_phone_set')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'secure_phone_set',
                    'phone_set': '+7 901 ***-**-00',
                },
            ],
        )

    def test_secure_phone_bind__no_phones_secure(self):
        """Событие не должно распознаться"""
        events = self.make_historydb_events(
            {
                'action': 'secure_bind_commit',
                'info.karma_prefix': '6',
                'phone.12807201.action': 'changed',
                'phone.12807201.bound': '1461244074',
                'phone.12807201.confirmed': '1461244074',
                'phone.12807201.number': '+79010010000',
                'phone.12807201.operation.271791.action': 'deleted',
                'phone.12807201.operation.271791.security_identity': '1',
                'phone.12807201.operation.271791.type': 'bind',
                'phone.12807201.secured': '1461244074',
                'phone.add': '+7 901 001-00-00',
                # тут нету phones.secure
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(parsed_events, [])

    def test_secure_phone_unbind(self):
        """Отвязка телефона"""
        events = self.make_historydb_events(
            {
                'action': 'remove_secure_commit',
                'phone.12807201.action': 'deleted',
                'phone.12807201.number': '+79010010000',
                'phone.12807201.operation.272245.action': 'deleted',
                'phone.12807201.operation.272245.security_identity': '1',
                'phone.12807201.operation.272245.type': 'remove',
                'phone.rm': '+7 901 001-00-00',
                'phones.secure': '0',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'secure_phone_unset')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'secure_phone_unset',
                    'phone_unset': '+7 901 ***-**-00',
                },
            ],
        )

    def test_secure_phone_replace(self):
        """Замена телефона одного на другой"""
        events = self.make_historydb_events(
            {
                'action': 'phone_secure_replace_commit',
                'phone.12813937.action': 'deleted',
                'phone.12813937.number': '+79010010000',
                'phone.12813937.operation.277337.action': 'deleted',
                'phone.12813937.operation.277337.security_identity': '1',
                'phone.12813937.operation.277337.type': 'replace',
                'phone.12813939.action': 'changed',
                'phone.12813939.bound': '1461324236',
                'phone.12813939.confirmed': '1461324236',
                'phone.12813939.number': '+79020020000',
                'phone.12813939.operation.277339.action': 'deleted',
                'phone.12813939.operation.277339.security_identity': '79020020000',
                'phone.12813939.operation.277339.type': 'bind',
                'phone.12813939.secured': '1461324236',
                'phone.add': '+7 902 002-00-00',
                'phones.secure': '12813939',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'secure_phone_replace')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'secure_phone_replace',
                    'phone_set': '+7 902 ***-**-00',
                    'phone_unset': '+7 901 ***-**-00',
                },
            ],
        )

    def test_lost_phone(self):
        """Телефон отвязался в связи с тем, что его привязали большое кол-во раз другие люди"""
        events = self.make_historydb_events(
            {
                'phone.12814667.action': 'changed',
                'phone.rm': '+7 901 001-00-00',
                'phone.12814667.operation.277969.type': 'mark',
                'phone.12814667.number': '+79010010000',
                'phone.12814667.operation.277969.security_identity': '79010010000',
                'phone.12814667.secured': '0',
                'phones.secure': '0',
                'action': 'unbind_phone_from_account',
                'reason_uid': '4002801755',
                'phone.12814667.operation.277969.action': 'deleted',
                'phone.12814667.bound': '0'
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'secure_phone_unset')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'secure_phone_unset',
                    'phone_unset': '+7 901 ***-**-00',
                    'reason_uid': 4002801755,
                },
            ],
        )

    def test_unbind_unparseable_phone(self):
        """Невалидный телефон. Ничего не должно упасть."""
        events = self.make_historydb_events(
            {
                'action': 'remove_secure_commit',
                'phone.12807201.action': 'deleted',
                'phone.12807201.number': '+00000000000',
                'phone.12807201.operation.272245.action': 'deleted',
                'phone.12807201.operation.272245.security_identity': '1',
                'phone.12807201.operation.272245.type': 'remove',
                'phone.rm': '+0 000 000-00-00',
                'phones.secure': '0',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'secure_phone_unset')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'secure_phone_unset',
                    'phone_unset': '+0000*****00',
                },
            ],
        )

    def test_phone_bind(self):
        """Привязали несекьюрный телефон"""
        events = self.make_historydb_events(
            {
                'action': 'simple_bind_commit',
                'phone.14484544.action': 'changed',
                'phone.14484544.bound': '1491986790',
                'phone.14484544.confirmed': '1491986790',
                'phone.14484544.number': '+79010010000',
                'phone.14484544.operation.1421582.action': 'deleted',
                'phone.14484544.operation.1421582.security_identity': '79010010000',
                'phone.14484544.operation.1421582.type': 'bind',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'phone_bind')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'phone_bind',
                    'phone_bind': '+7 901 ***-**-00',
                },
            ],
        )

    def test_phone_unbind(self):
        """Отвязка несекьюрного телефона"""
        events = self.make_historydb_events(
            {
                'action': 'simple_phone_remove',
                'phone.14484544.action': 'deleted',
                'phone.14484544.number': '+79010010000',
                'phone.14484544.operation.1421796.action': 'deleted',
                'phone.14484544.operation.1421796.security_identity': '79010010000',
                'phone.14484544.operation.1421796.type': 'mark',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'phone_unbind')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'phone_unbind',
                    'phone_unbind': '+7 901 ***-**-00',
                },
            ],
        )

    def test_phone_operation_cancel(self):
        """Тут нету phone.*.operation.*.finished, поэтому это не распознается, как смена телефонов."""
        events = self.make_historydb_events(
            {
                'action': 'cancel_operation',
                'consumer': 'passport',
                'phone.14484534.number': '+79265828122',
                'phone.14484534.operation.1429574.action': 'deleted',
                'phone.14484534.operation.1429574.security_identity': '1',
                'phone.14484534.operation.1429574.type': 'replace',
                'phone.14495560.action': 'deleted',
                'phone.14495560.number': '+79155187696',
                'phone.14495560.operation.1429572.action': 'deleted',
                'phone.14495560.operation.1429572.security_identity': '79155187696',
                'phone.14495560.operation.1429572.type': 'bind',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()
        eq_(parsed_events, [])

    def test_secure_phone_replace_with_quarantine(self):
        """Замена секьюрного телефона с карантином, т.е. сама замена произойдёт через какакое-то время в будущем"""
        events = self.make_historydb_events(
            {
                u'action': u'phone_secure_replace_submit',
                u'consumer': u'passport',
                u'phone.14484534.number': u'+79010010000',
                u'phone.14484534.operation.1429574.action': u'created',
                u'phone.14484534.operation.1429574.finished': u'1494684006',
                u'phone.14484534.operation.1429574.phone_id2': u'14495560',
                u'phone.14484534.operation.1429574.security_identity': u'1',
                u'phone.14484534.operation.1429574.started': u'1492092006',
                u'phone.14484534.operation.1429574.type': u'replace',
                u'phone.14495560.action': u'created',
                u'phone.14495560.created': u'1492092006',
                u'phone.14495560.number': u'+79020010000',
                u'phone.14495560.operation.1429572.action': u'created',
                u'phone.14495560.operation.1429572.finished': u'1494684006',
                u'phone.14495560.operation.1429572.phone_id2': u'14484534',
                u'phone.14495560.operation.1429572.security_identity': u'79020010000',
                u'phone.14495560.operation.1429572.started': u'1492092006',
                u'phone.14495560.operation.1429572.type': u'bind',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()
        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'secure_phone_replace')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'secure_phone_replace',
                    'phone_set': '+7 902 ***-**-00',
                    'phone_unset': '+7 901 ***-**-00',
                    'delayed_until': 1494684006,
                },
            ],
        )

    def test_secure_phone_replace_with_quarantine__broken_finished(self):
        """Плохое событие, нельзя вычислить время карантина"""
        events = self.make_historydb_events(
            {
                u'action': u'phone_secure_replace_submit',
                u'consumer': u'passport',
                u'phone.14484534.number': u'+79010010000',
                u'phone.14484534.operation.1429574.action': u'created',
                u'phone.14484534.operation.1429574.finished': u'SURPRISE',
                u'phone.14484534.operation.1429574.phone_id2': u'14495560',
                u'phone.14484534.operation.1429574.security_identity': u'1',
                u'phone.14484534.operation.1429574.started': u'1492092006',
                u'phone.14484534.operation.1429574.type': u'replace',
                u'phone.14495560.action': u'created',
                u'phone.14495560.created': u'1492092006',
                u'phone.14495560.number': u'+79020010000',
                u'phone.14495560.operation.1429572.action': u'created',
                u'phone.14495560.operation.1429572.finished': u'SURPRISE',
                u'phone.14495560.operation.1429572.phone_id2': u'14484534',
                u'phone.14495560.operation.1429572.security_identity': u'79020010000',
                u'phone.14495560.operation.1429572.started': u'1492092006',
                u'phone.14495560.operation.1429572.type': u'bind',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()
        eq_(parsed_events, [])
