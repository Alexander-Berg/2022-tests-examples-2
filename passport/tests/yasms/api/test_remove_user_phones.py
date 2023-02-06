# -*- coding: utf-8 -*-

from datetime import datetime

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.emails import assert_user_notified_about_alias_as_login_and_email_disabled
from passport.backend.api.yasms import exceptions
from passport.backend.core.models.phones.faker import (
    build_account,
    build_phone_being_bound,
    build_phone_bound,
    build_phone_secured,
    build_phone_unbound,
    build_remove_operation,
    build_securify_operation,
)
from passport.backend.utils.common import deep_merge

from .base import BaseYasmsTestCase


UID = 712
PHONE_ID = 101
PHONE_NUMBER = u'+79019988777'
TEST_DATE = datetime(2012, 2, 1, 10, 20, 30)
CONSUMER = u'test_consumer'
CONSUMER_IP = u'1.9.3.1'
OPERATION_ID = 22


class RemoveUserPhonesTestCase(BaseYasmsTestCase):
    _DEFAULT_SETTINGS = dict(
        BaseYasmsTestCase._DEFAULT_SETTINGS,
    )

    def _build_args(self, **kwargs):
        kwargs.setdefault(u'statbox', self._statbox)
        kwargs.setdefault(u'consumer', CONSUMER)
        return kwargs

    def _build_account(self, **kwargs):
        kwargs.setdefault(u'uid', UID)
        kwargs.setdefault(u'firstname', u'Андрей')
        kwargs.setdefault(u'login', u'andrey1931')
        kwargs['aliases'] = deep_merge(
            {'portal': kwargs[u'login']},
            kwargs.get('aliases', {}),
        )
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
        return build_account(**kwargs)

    def test_account_has_no_phones(self):
        """
        На аккаунте нет телефонов.
        """
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        response = self._yasms.remove_userphones(**self._build_args(
            account=account,
        ))

        eq_(response, {u'status': u'ok'})

    def test_account_blocked(self):
        """
        Аккаунт заблокирован.
        """
        account = self._build_account(
            uid=UID,
            enabled=False,
            **build_phone_bound(PHONE_ID, PHONE_NUMBER, is_default=True)
        )

        response = self._yasms.remove_userphones(**self._build_args(
            account=account,
        ))

        eq_(response, {u'status': u'ok'})

    def test_phone_bound(self):
        """
        Привязан один простой номер.
        """
        account = self._build_account(
            uid=UID,
            **build_phone_bound(PHONE_ID, PHONE_NUMBER, is_default=True)
        )

        response = self._yasms.remove_userphones(**self._build_args(
            account=account,
        ))

        eq_(response, {u'status': u'ok'})
        eq_(len(account.phones.all()), 0)
        self.env.statbox.assert_has_written([])
        eq_(len(self.env.mailer.messages), 0)

    def test_phone_bound_with_operation(self):
        """
        Привязан один простой номер с операцией.
        """
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_bound(PHONE_ID, PHONE_NUMBER, is_default=True),
                build_securify_operation(OPERATION_ID, PHONE_ID),
            )
        )

        response = self._yasms.remove_userphones(**self._build_args(
            account=account,
        ))

        eq_(response, {u'status': u'ok'})
        eq_(len(account.phones.all()), 0)
        self.env.statbox.assert_has_written([])
        eq_(len(self.env.mailer.messages), 0)

    def test_secure_phone(self):
        """
        Один защищённый номер.
        """
        account = self._build_account(
            uid=UID,
            **build_phone_secured(PHONE_ID, PHONE_NUMBER, is_default=True)
        )

        response = self._yasms.remove_userphones(**self._build_args(
            account=account,
        ))

        eq_(response, {u'status': u'ok'})
        eq_(len(account.phones.all()), 0)
        self.env.statbox.assert_has_written([])
        eq_(len(self.env.yasms.requests), 0)
        eq_(len(self.env.mailer.messages), 0)

    def test_secure_phone_with_alias(self):
        """
        Один защищённый номер, является алиасом.
        """
        account = self._build_account(
            **deep_merge(
                dict(
                    uid=UID,
                    firstname=u'Пётр',
                    login=u'qqck',
                    language=u'ru',
                    emails=[
                        self.env.email_toolkit.create_native_email(
                            login=u'qqck',
                            domain=u'yandex.ru',
                        ),
                    ],
                ),
                build_phone_secured(
                    PHONE_ID,
                    phone_number=u'+79023344555',
                    is_default=True,
                    is_alias=True,
                ),
            )
        )

        response = self._yasms.remove_userphones(**self._build_args(
            account=account,
        ))

        eq_(response, {u'status': u'ok'})
        eq_(len(account.phones.all()), 0)
        self.env.statbox.assert_has_written([])

        eq_(len(self.env.mailer.messages), 1)
        assert_user_notified_about_alias_as_login_and_email_disabled(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=u'qqck@yandex.ru',
            firstname=u'Пётр',
            login=u'qqck',
            portal_email=u'qqck@yandex.ru',
            phonenumber_alias=u'79023344555',
        )

    def test_secure_phone_with_operation(self):
        """
        Один защищённый номер с операцией.
        """
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_secured(
                    PHONE_ID,
                    PHONE_NUMBER,
                    is_default=True,
                ),
                build_remove_operation(OPERATION_ID, PHONE_ID),
            )
        )

        response = self._yasms.remove_userphones(**self._build_args(
            account=account,
        ))

        eq_(response, {u'status': u'ok'})
        eq_(len(account.phones.all()), 0)
        self.env.statbox.assert_has_written([])
        eq_(len(self.env.mailer.messages), 0)

    def test_phone_being_bound(self):
        """
        Номер привязывается.
        """
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER,
                OPERATION_ID,
            )
        )

        response = self._yasms.remove_userphones(**self._build_args(
            account=account,
        ))

        eq_(response, {u'status': u'ok'})
        eq_(len(account.phones.all()), 0)
        self.env.statbox.assert_has_written([])
        eq_(len(self.env.mailer.messages), 0)

    def test_phone_unbound(self):
        """
        Номер отвязан.
        """
        account = self._build_account(
            uid=UID,
            **build_phone_unbound(
                PHONE_ID,
                PHONE_NUMBER,
            )
        )

        response = self._yasms.remove_userphones(**self._build_args(
            account=account,
        ))

        eq_(response, {u'status': u'ok'})
        eq_(len(account.phones.all()), 0)
        self.env.statbox.assert_has_written([])
        eq_(len(self.env.mailer.messages), 0)

    def test_many_numbers(self):
        """
        Несколько номеров.
        """
        account = self._build_account(
            uid=UID,
            emails=[
                self.env.email_toolkit.create_native_email(
                    login=u'andrey1931',
                    domain=u'yandex-team.ru',
                ),
            ],
            **deep_merge(
                build_phone_secured(
                    phone_id=1,
                    phone_number=u'+79012233444',
                    is_default=True,
                    is_alias=True,
                ),
                build_phone_bound(
                    phone_id=2,
                    phone_number=u'+79023344555',
                ),
                build_phone_being_bound(
                    phone_id=3,
                    phone_number=u'+79034455666',
                    operation_id=3,
                ),
                build_phone_unbound(
                    phone_id=4,
                    phone_number=u'+79045566777',
                ),
            )
        )

        response = self._yasms.remove_userphones(**self._build_args(
            account=account,
        ))

        eq_(response, {u'status': u'ok'})
        eq_(len(account.phones.all()), 0)
        self.env.statbox.assert_has_written([])
        eq_(len(self.env.mailer.messages), 1)

    def test_secure_phone__2fa_enabled(self):
        account = self._build_account(**deep_merge(
            {
                u'uid': UID,
                u'firstname': u'Пётр',
                u'login': u'qqck',
                u'attributes': {u'account.2fa_on': True},
            },
            build_phone_secured(
                PHONE_ID,
                phone_number=u'+79023344555',
                is_default=True,
                is_alias=True,
            ),
        ))

        with self.assertRaises(exceptions.YaSmsOperationInapplicable):
            self._yasms.remove_userphones(**self._build_args(account=account))

        eq_(len(account.phones.all()), 1)
        ok_(account.phonenumber_alias)

    def test_secure_phone__sms_2fa_enabled(self):
        account = self._build_account(**deep_merge(
            {
                u'uid': UID,
                u'firstname': u'Пётр',
                u'login': u'qqck',
                u'attributes': {u'account.sms_2fa_on': True},
            },
            build_phone_secured(
                PHONE_ID,
                phone_number=u'+79023344555',
                is_default=True,
                is_alias=True,
            ),
        ))

        with self.assertRaises(exceptions.YaSmsOperationInapplicable):
            self._yasms.remove_userphones(**self._build_args(account=account))

        eq_(len(account.phones.all()), 1)
        ok_(account.phonenumber_alias)
