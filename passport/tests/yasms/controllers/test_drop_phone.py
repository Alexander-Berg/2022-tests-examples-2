# -*- coding: utf-8 -*-

from datetime import datetime

from nose.tools import (
    eq_,
    istest,
)
from passport.backend.api.test.emails import assert_user_notified_about_alias_as_login_and_email_disabled
from passport.backend.api.yasms import grants
from passport.backend.api.yasms.controllers import DropPhoneView
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.yasms.faker import yasms_drop_phone_response
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

from .base import (
    BaseTestCase,
    BlackboxCommonTestCase,
    RequiredSenderWhenGrantsAreRequiredTestMixin,
    RequiredUidWhenGrantsAreRequiredTestMixin,
    TEST_PROXY_IP,
)


UID = 4814
PHONE_ID = 19
PHONE_NUMBER = u'+79012233444'
OPERATION_ID = 711
TEST_DATE = datetime(2001, 2, 3, 4, 5, 6)
PHONISH_LOGIN1 = 'phne-test1'

ALIAS_SID = 65


@with_settings_hosts
@istest
class TestDropPhoneView(BaseTestCase,
                        RequiredSenderWhenGrantsAreRequiredTestMixin,
                        RequiredUidWhenGrantsAreRequiredTestMixin,
                        BlackboxCommonTestCase):
    def test_unhandled_exception(self):
        self.assert_unhandled_exception_is_processed(DropPhoneView)

    def test_account_not_found(self):
        """
        Учётная запись не найдена.
        """
        self.assign_grants([grants.DROP_PHONE])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        response = self.make_request(uid=UID)

        eq_(response.status_code, 200)
        self.assert_json_responses_equal(
            response,
            yasms_drop_phone_response(uid=UID, status=u'NOTFOUND'),
        )

    def test_database_fault__internal_error(self):
        """
        Отказывает БД.
        """
        self.assign_grants([grants.DROP_PHONE])
        self._given_account(
            uid=UID,
            **build_phone_bound(
                PHONE_ID,
                PHONE_NUMBER,
                phone_bound=TEST_DATE,
                phone_created=TEST_DATE,
                phone_confirmed=TEST_DATE,
            )
        )
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError())

        response = self.make_request(uid=UID, phone_id=PHONE_ID)

        eq_(response.status_code, 200)
        self.assert_response_is_error(u'INTERROR', u'INTERROR')

        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])
        self.assert_events_are_empty(self.env.handle_mock)
        eq_(len(self.env.yasms.requests), 0)
        eq_(len(self.env.mailer.messages), 0)

        # Проверим, что номер не удалился
        assert_simple_phone_bound.check_db(
            self.env.db,
            UID,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
        )

    def test_insecure_phone_number__with_operation__ok(self):
        """
        Удаляем простой номер с операцией.
        """
        self.assign_grants([grants.DROP_PHONE])
        self._given_account(
            uid=UID,
            **deep_merge(
                build_phone_bound(
                    phone_id=31,
                    phone_number=PHONE_NUMBER,
                    is_default=True,
                ),
                build_securify_operation(
                    operation_id=72,
                    phone_id=31,
                ),
            )
        )

        response = self.make_request(sender=u'dev', uid=UID, phone_id=31)

        eq_(response.status_code, 200)
        self.assert_json_responses_equal(
            response,
            yasms_drop_phone_response(uid=UID, status=u'OK'),
        )

        # Проверить, что номера нет в БД
        assert_no_phone_in_db(self.env.db, UID, 31, PHONE_NUMBER)
        assert_no_default_phone_chosen(self.env.db, UID)
        assert_phone_has_been_bound(self.env.db, UID, PHONE_NUMBER, times=1)

        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])
        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                u'action': u'drop_phone',
                u'consumer': u'dev',
                u'phone.31.action': u'deleted',
                u'phone.31.number': PHONE_NUMBER,
                u'phone.31.operation.72.action': u'deleted',
                u'phone.31.operation.72.type': u'securify',
                u'phone.31.operation.72.security_identity': u'1',
                u'phones.default': u'0',
            },
        )
        eq_(len(self.env.yasms.requests), 0)
        eq_(len(self.env.mailer.messages), 0)

    def test_secure_phone_number__with_operation_and_alias__ok(self):
        """
        Удаляем защищённый номер с операцией и алиасом.
        """
        self.assign_grants([grants.DROP_PHONE], networks=[u'1.2.3.4'])
        self._given_account(
            uid=UID,
            firstname=u'Андрей',
            login=u'andrey1931',
            language=u'ru',
            emails=[
                self.env.email_toolkit.create_native_email(
                    login=u'andrey1931',
                    domain=u'yandex-team.ru',
                ),
            ],
            **deep_merge(
                build_phone_secured(
                    phone_id=31,
                    phone_number=u'+79023344555',
                    is_default=True,
                    is_alias=True,
                ),
                build_remove_operation(
                    operation_id=17,
                    phone_id=31,
                ),
            )
        )

        response = self.make_request(
            sender=u'dev',
            uid=UID,
            phone_id=31,
            headers={
                u'X-Real-IP': TEST_PROXY_IP,
                u'Ya-Consumer-Real-Ip': u'1.2.3.4',
            },
        )

        eq_(response.status_code, 200)
        self.assert_json_responses_equal(
            response,
            yasms_drop_phone_response(uid=UID, status=u'OK'),
        )

        # Проверим, что номера нет в БД
        assert_no_phone_in_db(self.env.db, UID, 31, u'+79023344555')
        assert_no_default_phone_chosen(self.env.db, UID)
        assert_phone_has_been_bound(self.env.db, UID, u'+79023344555', times=1)
        assert_no_secure_phone(self.env.db, UID)
        assert_phonenumber_alias_removed(
            self.env.db,
            UID,
            alias=u'79023344555',
        )

        self.env.statbox_logger.assert_has_written([
            self.env.statbox_logger.entry(u'phonenumber_alias_removed'),
            self.env.statbox_logger.entry(
                u'account_modification',
                entity=u'phones.secure',
                operation=u'deleted',
                new=u'-',
                new_entity_id=u'-',
                old='+79023******',
                old_entity_id='31',
            ),
            self.env.statbox_logger.entry(
                u'account_modification',
                sid=str(ALIAS_SID),
                entity=u'subscriptions',
                operation=u'removed',
            ),
        ])
        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                u'action': u'drop_phone',
                u'consumer': u'dev',
                u'phone.31.action': u'deleted',
                u'phone.31.number': u'+79023344555',
                u'phone.31.operation.17.action': u'deleted',
                u'phone.31.operation.17.security_identity': u'1',
                u'phone.31.operation.17.type': u'remove',
                u'phones.default': u'0',
                u'phones.secure': u'0',
                u'alias.phonenumber.rm': u'+7 902 334-45-55',
            },
        )

        eq_(len(self.env.yasms.requests), 0)

        eq_(len(self.env.mailer.messages), 1)
        assert_user_notified_about_alias_as_login_and_email_disabled(
            mailer_faker=self.env.mailer,
            language=u'ru',
            email_address=u'andrey1931@yandex-team.ru',
            firstname=u'Андрей',
            login=u'andrey1931',
            portal_email=u'andrey1931@yandex-team.ru',
            phonenumber_alias=u'79023344555',
        )

    def test_secure_phone_number__many_numbers__ok(self):
        """
        Удаляем защищённый номер, когда на аккаунте есть и другие номера.
        """
        self.assign_grants([grants.DROP_PHONE])
        self._given_account(
            uid=UID,
            **deep_merge(
                build_phone_bound(
                    phone_id=30,
                    phone_number=u'+79012233444',
                    is_default=False,
                ),
                build_phone_secured(
                    phone_id=31,
                    phone_number=u'+79023344555',
                    is_default=True,
                    is_alias=True,
                ),
            )
        )

        response = self.make_request(uid=UID, phone_id=31)

        eq_(response.status_code, 200)
        self.assert_json_responses_equal(
            response,
            yasms_drop_phone_response(uid=UID, status=u'OK'),
        )

        assert_no_phone_in_db(
            self.env.db,
            UID,
            phone_id=31,
            phone_number=u'+79023344555',
        )
        assert_simple_phone_bound.check_db(
            self.env.db,
            UID,
            {u'id': 30, u'number': u'+79012233444'},
        )
        self.env.db.check_missing(
            u'attributes',
            attr=u'phones.default',
            uid=UID,
            db=u'passportdbshard1',
        )
        self.env.db.check_missing(
            u'attributes',
            attr=u'phones.secure',
            uid=UID,
            db=u'passportdbshard1',
        )

    def test_last_phonish_phone(self):
        self.assign_grants([grants.DROP_PHONE])
        flags = PhoneBindingsFlags()
        flags.should_ignore_binding_limit = True
        self._given_account(
            uid=UID,
            login=PHONISH_LOGIN1,
            aliases={
                'phonish': PHONISH_LOGIN1,
                'portal': None,
            },
            **build_phone_bound(
                phone_id=30,
                phone_number=u'+79012233444',
                binding_flags=flags,
            )
        )

        self.make_request(uid=UID, phone_id=30)

        self.assert_response_is_error(u'INTERROR', u'INTERROR')
        assert_simple_phone_bound.check_db(
            self.env.db,
            UID,
            {u'id': 30, u'number': u'+79012233444'},
        )

    def test_not_last_phonish_phone(self):
        self.assign_grants([grants.DROP_PHONE])
        flags = PhoneBindingsFlags()
        flags.should_ignore_binding_limit = True
        self._given_account(
            uid=UID,
            login=PHONISH_LOGIN1,
            aliases={
                'phonish': PHONISH_LOGIN1,
                'portal': None,
            },
            **deep_merge(
                build_phone_bound(
                    phone_id=30,
                    phone_number=u'+79012233444',
                    binding_flags=flags,
                ),
                build_phone_bound(
                    phone_id=31,
                    phone_number=u'+79023344555',
                    binding_flags=flags,
                ),
            )
        )

        response = self.make_request(uid=UID, phone_id=31)

        eq_(response.status_code, 200)
        self.assert_json_responses_equal(
            response,
            yasms_drop_phone_response(uid=UID, status=u'OK'),
        )
        assert_no_phone_in_db(
            self.env.db,
            UID,
            phone_id=31,
            phone_number=u'+79023344555',
        )
        assert_simple_phone_bound.check_db(
            self.env.db,
            UID,
            {u'id': 30, u'number': u'+79012233444'},
        )

    def assert_response_is_good_response(self):
        eq_(self.response.status_code, 200)
        self.assert_json_responses_equal(
            self.response,
            yasms_drop_phone_response(UID, u'OK'),
        )

    def make_request(self, sender='dev', uid=UID, phone_id=PHONE_ID,
                     headers=None):
        self.response = self.env.client.get(
            u'/yasms/api/dropphone',
            query_string={u'sender': sender, u'uid': uid, u'phoneid': phone_id},
            headers=headers,
        )
        return self.response

    def assert_response_is_error(self, message, code, encoding=u'utf-8'):
        self.assert_response_is_json_error(code)

    def setUp(self):
        super(TestDropPhoneView, self).setUp()
        self.env.statbox_logger.bind_entry(
            'base',
            ip=u'1.2.3.4',
            uid=str(UID),
            user_agent=u'-',
            consumer=u'dev',
        )
        self.env.statbox_logger.bind_entry(
            'account_modification',
            _inherit_from=['account_modification', 'base'],
        )
        self.env.statbox_logger.bind_entry(
            'phonenumber_alias_removed',
            _inherit_from=['phonenumber_alias_removed', 'base'],
        )

    def _given_account(self, **kwargs):
        kwargs.setdefault(u'uid', UID)
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

    def setup_blackbox_to_serve_good_response(self):
        self._given_account(
            uid=UID,
            **deep_merge(
                build_phone_bound(
                    phone_id=PHONE_ID,
                    phone_number=PHONE_NUMBER,
                    is_default=True,
                ),
                build_securify_operation(
                    operation_id=OPERATION_ID,
                    phone_id=PHONE_ID,
                ),
            )
        )
