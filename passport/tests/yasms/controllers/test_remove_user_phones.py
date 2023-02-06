# -*- coding: utf-8 -*-

from datetime import datetime
import json
from uuid import uuid1

import mock
from nose.tools import (
    eq_,
    istest,
)
from passport.backend.api.yasms import grants
from passport.backend.api.yasms.controllers import RemoveUserPhonesView
from passport.backend.core import Undefined
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_response,
    blackbox_userinfo_response,
)
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.models.phones.faker import (
    assert_no_default_phone_chosen,
    assert_no_phone_in_db,
    assert_no_secure_phone,
    assert_phone_has_been_bound,
    assert_phonenumber_alias_removed,
    assert_simple_phone_bound,
    build_phone_bound,
    build_phone_secured,
    build_remove_operation,
    build_securify_operation,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.bit_vector.bit_vector import PhoneBindingsFlags
from passport.backend.utils.common import deep_merge
from six.moves.urllib.parse import (
    parse_qs,
    urlparse,
)

from .base import (
    BaseTestCase,
    BlackboxCommonTestCase,
    TEST_PROXY_IP,
)


ALIAS_SID = 65
UID_ALPHA = 4814
UID_BETA = 9141
PHONE_ID = 2331
PHONE_NUMBER = u'+79012233444'
OPERATION_ID = 44
TEST_DATE = datetime(2014, 3, 3, 0, 0, 0)
PHONISH_LOGIN1 = 'phne-test1'


@with_settings_hosts(
    YASMS_SENDER=u'passport',
    YASMS_RETRIES=1,
    YASMS_URL=u'http://ya.sms/',
)
@istest
class TestRemoveUserPhonesView(BaseTestCase, BlackboxCommonTestCase):
    def setUp(self):
        super(TestRemoveUserPhonesView, self).setUp()
        self._session_id_to_response = {}
        self.env.blackbox.set_response_side_effect(
            u'sessionid',
            self._handle_blackbox_session_id,
        )
        self.env.statbox_logger.bind_entry(
            'base',
            ip=u'1.2.3.4',
            consumer=u'hello',
        )
        self.env.statbox_logger.bind_entry(
            u'subscription_removed',
            _inherit_from=['base'],
            operation=u'removed',
            entity=u'subscriptions',
            user_agent=u'-',
            event=u'account_modification',
        )
        self.env.statbox_logger.bind_entry(
            u'phonenumber_alias_removed',
            _inherit_from=['phonenumber_alias_removed', 'base'],
        )

    def _handle_blackbox_session_id(self, http_method, url, data, files=None,
                                    headers=None, cookies=None):
        query = parse_qs(urlparse(url).query)
        eq_(len(query[u'sessionid']), 1)
        session_id = query[u'sessionid'][0]
        return mock.Mock(
            name=u'blackbox_session_id_response',
            content=self._session_id_to_response[session_id],
            status_code=200,
        )

    def _get_valid_session_id(self, uid):
        session_id = uuid1().hex
        self._session_id_to_response[session_id] = blackbox_sessionid_response(
            uid=uid,
        )
        return session_id

    def _get_invalid_session_id(self, uid=None):
        session_id = uuid1().hex
        self._session_id_to_response[session_id] = blackbox_sessionid_response(
            uid=uid,
            status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
        )
        return session_id

    def make_request(self, sender=u'dev', uid=UID_ALPHA, block=None,
                     session_id=Undefined, headers=None):
        if headers is None:
            headers = [
                (
                    u'Ya-Client-Host',
                    u'passport.yandex.ru',
                ),
            ]
        if session_id is Undefined:
            session_id = self._get_valid_session_id(uid)
        if session_id is not None:
            headers = [
                (
                    u'Ya-Client-Cookie',
                    u'Session_id={session_id}'.format(session_id=session_id),
                ),
            ] + headers
        self.response = self.env.client.get(
            u'/yasms/api/removeuserphones',
            query_string={u'sender': sender, u'uid': uid, u'block': block},
            headers=headers,
        )
        return self.response

    def assert_response_is_good_response(self):
        eq_(self.response.status_code, 200)
        response = json.loads(self.response.data)
        eq_(response, {u'status': u'OK'})

    def assert_response_is_404(self):
        eq_(self.response.status_code, 404)

    def assert_response_is_cant_found_uid(self):
        eq_(self.response.status_code, 200)
        response = json.loads(self.response.data)
        eq_(response, {u'status': u'Error', u'error': u"Can't found uid"})

    def assert_response_is_internal_error(self):
        eq_(self.response.status_code, 200)
        response = json.loads(self.response.data)
        eq_(response, {u'status': u'Error', u'error': u"Internal error"})

    def assert_response_is_error(self, message, code=None):
        eq_(self.response.status_code, 200)
        response = json.loads(self.response.data)
        eq_(response, {u'status': u'Error', u'error': message})

    def setup_blackbox_to_serve_good_response(self):
        self._given_account(
            uid=UID_ALPHA,
            **build_phone_bound(
                phone_id=PHONE_ID,
                phone_number=PHONE_NUMBER,
                is_default=True,
            )
        )

    def _given_account(self, **kwargs):
        kwargs.setdefault(u'uid', UID_ALPHA)
        kwargs.setdefault(u'firstname', u'Андрей')
        kwargs.setdefault(u'login', u'andrey1931')
        kwargs = deep_merge({u'aliases': {u'portal': u'andrey1931'}}, kwargs)
        kwargs.setdefault(u'language', u'ru')
        kwargs.setdefault(
            u'emails',
            [
                self.env.email_toolkit.create_native_email(
                    login=u'andrey1931',
                    domain=u'yandex-team.ru',
                ),
            ],
        )
        user_info = blackbox_userinfo_response(**kwargs)
        self.env.blackbox.set_response_value(u'userinfo', user_info)
        self.env.db.serialize(user_info)

    def test_unhandled_exception_is_processed(self):
        self.assign_all_grants()
        with mock.patch.object(
            RemoveUserPhonesView,
            u'process_request',
            side_effect=Exception(u'Test exception'),
        ):
            r = self.make_request()
            eq_(r.status_code, 200)
            self.assert_response_is_internal_error()

    def test_404_when_no_sender(self):
        self.assign_all_grants()

        self.make_request(sender=None)

        self.assert_response_is_404()

    def test_404_when_invalid_sender(self):
        self.assign_all_grants()

        self.make_request(sender=u'\u0000')

        self.assert_response_is_404()

    def test_404_when_unknown_sender(self):
        self.assign_all_grants()

        self.make_request(sender=u'unknown')

        self.assert_response_is_404()

    def test_404_when_ip_is_not_allowed(self):
        self.assign_grants([grants.REMOVE_USER_PHONES], u'known_sender', [])

        self.make_request(sender=u'known_sender')

        self.assert_response_is_404()

    def test_404_when_not_enough_rights(self):
        self.assign_grants([])

        self.make_request()

        self.assert_response_is_404()

    def test_cant_found_uid_when_no_uid_and_no_session_id(self):
        self.assign_all_grants()

        self.make_request(uid=None, session_id=None)

        self.assert_response_is_cant_found_uid()

    def test_cant_found_uid_when_invalid_uid_and_no_session_id(self):
        self.assign_all_grants()

        self.make_request(uid=u'invalid', session_id=None)

        self.assert_response_is_cant_found_uid()

    def test_cant_found_uid_when_no_uid_and_invalid_session(self):
        self.assign_all_grants()

        self.make_request(uid=None, session_id=self._get_invalid_session_id())

        self.assert_response_is_cant_found_uid()

    def test_cant_found_uid_when_invalid_uid_and_invalid_session(self):
        self.assign_all_grants()

        self.make_request(uid=u'invalid', session_id=self._get_invalid_session_id())

        self.assert_response_is_cant_found_uid()

    def test_ok_when_block_is_true(self):
        self.assign_grants([grants.REMOVE_USER_PHONES])
        self.setup_blackbox_to_serve_good_response()

        self.make_request(block=u'1')

        self.assert_response_is_good_response()

    def test_ok_when_block_is_false(self):
        self.assign_grants([grants.REMOVE_USER_PHONES])
        self.setup_blackbox_to_serve_good_response()

        self.make_request(block=u'0')

        self.assert_response_is_good_response()

    def test_ok_when_no_session_id(self):
        self.assign_grants([grants.REMOVE_USER_PHONES])
        self.setup_blackbox_to_serve_good_response()

        self.make_request(session_id=None)

        self.assert_response_is_good_response()

    def test_ok_when_no_uid_and_session_id_is_valid(self):
        self.assign_grants([grants.REMOVE_USER_PHONES])
        self.setup_blackbox_to_serve_good_response()

        self.make_request(
            uid=None,
            session_id=self._get_valid_session_id(UID_ALPHA),
        )

        self.assert_response_is_good_response()

    def test_uses_uid_from_query_when_query_uid_and_session_id_uid_are_correct_but_different(self):
        self.assign_grants([grants.REMOVE_USER_PHONES])
        self.setup_blackbox_to_serve_good_response()

        self.make_request(
            uid=UID_ALPHA,
            session_id=self._get_valid_session_id(UID_BETA),
        )

        self.assert_response_is_good_response()

    def test_account_not_found(self):
        """
        Учётная запись не найдена.
        """
        self.assign_grants([grants.REMOVE_USER_PHONES])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        self.make_request()

        self.assert_response_is_good_response()

    def test_account_blocked(self):
        """
        Учётная запись заблокирована.
        """
        self.assign_grants([grants.REMOVE_USER_PHONES])
        self._given_account(
            uid=UID_ALPHA,
            enabled=False,
            **build_phone_bound(PHONE_ID, PHONE_NUMBER, is_default=True)
        )

        self.make_request(uid=UID_ALPHA)

        self.assert_response_is_good_response()

    def test_database_fault(self):
        """
        Отказывает БД.
        """
        self.assign_grants([grants.REMOVE_USER_PHONES])
        self._given_account(
            uid=UID_ALPHA,
            **build_phone_bound(
                PHONE_ID,
                PHONE_NUMBER,
                phone_created=TEST_DATE,
                phone_bound=TEST_DATE,
                phone_confirmed=TEST_DATE,
            )
        )
        self.env.db.set_side_effect_for_db(u'passportdbshard1', DBError())

        self.make_request(uid=UID_ALPHA)

        self.assert_response_is_internal_error()

        # Номер не удалился
        assert_simple_phone_bound.check_db(
            self.env.db,
            UID_ALPHA,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
        )

    def test_many_numbers(self):
        """
        На аккуанте несколько номеров.
        """
        self.assign_grants(
            [grants.REMOVE_USER_PHONES],
            consumer=u'old_yasms_grants_hello',
        )
        self._given_account(
            uid=UID_ALPHA,
            **deep_merge(
                build_phone_bound(
                    1,
                    u'+79012233444',
                ),
                build_phone_secured(
                    2,
                    u'+79023344555',
                    is_default=True,
                ),
                build_remove_operation(
                    operation_id=2,
                    phone_id=2,
                ),
            )
        )

        self.make_request(sender=u'hello', uid=UID_ALPHA)

        self.assert_response_is_good_response()

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                u'action': 'remove_user_phones',
                u'consumer': u'hello',
                u'phone.1.action': u'deleted',
                u'phone.1.number': u'+79012233444',
                u'phone.2.action': u'deleted',
                u'phone.2.number': u'+79023344555',
                u'phone.2.operation.2.action': u'deleted',
                u'phone.2.operation.2.type': u'remove',
                u'phone.2.operation.2.security_identity': u'1',
                u'phones.default': u'0',
                u'phones.secure': u'0',
            },
        )

    def test_insecure_phone_number__with_operation(self):
        """
        На аккаунте есть обычный номер с операцией.
        """
        self.assign_grants(
            [grants.REMOVE_USER_PHONES],
            consumer=u'old_yasms_grants_hello',
        )
        self._given_account(
            uid=UID_ALPHA,
            **deep_merge(
                build_phone_bound(
                    phone_id=101,
                    phone_number=PHONE_NUMBER,
                    is_default=True,
                ),
                build_securify_operation(
                    operation_id=5,
                    phone_id=101,
                ),
            )
        )

        self.make_request(sender=u'hello', uid=UID_ALPHA)

        self.assert_response_is_good_response()

        # Проверить, что номера нет в БД
        assert_no_phone_in_db(self.env.db, UID_ALPHA, 101, PHONE_NUMBER)
        assert_no_default_phone_chosen(self.env.db, UID_ALPHA)

        # В истории привязок остался
        assert_phone_has_been_bound(self.env.db, UID_ALPHA, PHONE_NUMBER, times=1)

        self.env.statbox_logger.assert_has_written([])
        eq_(len(self.env.mailer.messages), 0)
        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                u'action': 'remove_user_phones',
                u'consumer': u'hello',
                u'phone.101.action': u'deleted',
                u'phone.101.number': PHONE_NUMBER,
                u'phone.101.operation.5.action': u'deleted',
                u'phone.101.operation.5.type': u'securify',
                u'phone.101.operation.5.security_identity': u'1',
                u'phones.default': u'0',
            },
        )

    def test_secure_phone_number__with_operation__alias(self):
        """
        На аккаунте есть защищённый номер с операцией и алиасом.
        """
        self.assign_grants(
            [grants.REMOVE_USER_PHONES],
            consumer=u'old_yasms_grants_hello',
            networks=[u'1.2.3.4'],
        )
        self._given_account(
            uid=UID_ALPHA,
            emails=[
                self.env.email_toolkit.create_native_email(
                    login=u'andrey1931',
                    domain=u'yandex-team.ru',
                ),
            ],
            **deep_merge(
                build_phone_secured(
                    phone_id=101,
                    phone_number=u'+79045566777',
                    is_default=True,
                    is_alias=True,
                ),
                build_remove_operation(
                    operation_id=5,
                    phone_id=101,
                ),
            )
        )

        self.make_request(
            sender=u'hello',
            uid=UID_ALPHA,
            headers=[
                (u'X-Real-IP', TEST_PROXY_IP),
                (u'Ya-Consumer-Real-Ip', u'1.2.3.4'),
                (u'Ya-Consumer-Client-Ip', u'4.3.2.1'),
            ],
        )

        self.assert_response_is_good_response()

        # Проверить, что номера нет в БД
        assert_no_phone_in_db(self.env.db, UID_ALPHA, 101, u'+79045566777')
        assert_no_default_phone_chosen(self.env.db, UID_ALPHA)
        assert_no_secure_phone(self.env.db, UID_ALPHA)

        # В истории привязок остался
        assert_phone_has_been_bound(
            self.env.db,
            UID_ALPHA,
            u'+79045566777',
            times=1,
        )

        assert_phonenumber_alias_removed(
            self.env.db,
            uid=UID_ALPHA,
            alias=u'79045566777',
        )

        self.env.statbox_logger.assert_has_written([
            self.env.statbox_logger.entry(
                u'phonenumber_alias_removed',
                uid=str(UID_ALPHA),
                ip=u'4.3.2.1',
            ),
            self.env.statbox_logger.entry(
                u'account_modification',
                entity=u'phones.secure',
                operation=u'deleted',
                old=u'+79045******',
                old_entity_id='101',
                new=u'-',
                new_entity_id=u'-',
                uid=str(UID_ALPHA),
                ip=u'4.3.2.1',
                consumer=u'hello',
            ),
            self.env.statbox_logger.entry(
                u'subscription_removed',
                uid=str(UID_ALPHA),
                sid=str(ALIAS_SID),
                ip=u'4.3.2.1',
            ),
        ])

        eq_(len(self.env.mailer.messages), 1)

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                u'action': 'remove_user_phones',
                u'consumer': u'hello',
                u'phone.101.action': u'deleted',
                u'phone.101.number': u'+79045566777',
                u'phone.101.operation.5.action': u'deleted',
                u'phone.101.operation.5.type': u'remove',
                u'phone.101.operation.5.security_identity': u'1',
                u'phones.default': u'0',
                u'phones.secure': u'0',
                u'alias.phonenumber.rm': u'+7 904 556-67-77',
            },
        )

    def test_secure_phone_number__2fa_enabled(self):
        """
        На аккаунте включен 2ФА.
        """
        self.assign_grants(
            [grants.REMOVE_USER_PHONES],
            consumer=u'old_yasms_grants_hello',
            networks=[u'1.2.3.4'],
        )
        self._given_account(
            uid=UID_ALPHA,
            **deep_merge(
                {
                    'attributes': {'account.2fa_on': '1'},
                },
                build_phone_secured(
                    phone_id=101,
                    phone_number=u'+79045566777',
                ),
            )
        )

        self.make_request(
            sender=u'hello',
            uid=UID_ALPHA,
            headers=[
                (u'X-Real-IP', TEST_PROXY_IP),
                (u'Ya-Consumer-Real-Ip', u'1.2.3.4'),
            ],
        )

        self.assert_response_is_internal_error()

    def test_phonish(self):
        self.assign_grants([grants.REMOVE_USER_PHONES])
        flags = PhoneBindingsFlags()
        flags.should_ignore_binding_limit = True
        self._given_account(
            **deep_merge(
                {
                    'uid': UID_ALPHA,
                    'aliases': {
                        'portal': None,
                        'phonish': PHONISH_LOGIN1,
                    },
                },
                build_phone_bound(
                    phone_id=PHONE_ID,
                    phone_number=PHONE_NUMBER,
                    binding_flags=flags,
                ),
            )
        )

        self.make_request()

        self.assert_response_is_error(u'Phonish must has exactly one phone')
        assert_simple_phone_bound.check_db(
            self.env.db,
            UID_ALPHA,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
        )
