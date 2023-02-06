# -*- coding: utf-8 -*-

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.api.test.emails import assert_user_notified_about_alias_as_login_and_email_disabled
from passport.backend.api.yasms.exceptions import YaSmsPhoneBindingsLimitExceeded
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


UID = 7722
PHONE_ID = 2376
PHONE_NUMBER = u'+79012233444'
OPERATION_ID = 2421
CONSUMER = u'TEST_CONSUMER'
CONSUMER_IP = u'5.6.7.8'


class TestDropPhone(BaseYasmsTestCase):
    _DEFAULT_SETTINGS = dict(
        BaseYasmsTestCase._DEFAULT_SETTINGS,
    )

    def _build_args(self, **kwargs):
        kwargs.setdefault(u'phone_id', PHONE_ID)
        kwargs.setdefault(u'statbox', self._statbox)
        kwargs.setdefault(u'consumer', CONSUMER)
        return kwargs

    def _build_account(self, **kwargs):
        kwargs.setdefault(u'uid', UID)
        kwargs.setdefault(u'firstname', u'Андрей')
        kwargs.setdefault(u'login', u'andrey1931')
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

    def test_account_blocked__ok(self):
        """
        Не обращаем внимание на блокированность учётной записи.
        """
        account = self._build_account(
            uid=UID,
            enabled=False,
            **build_phone_bound(PHONE_ID, PHONE_NUMBER, is_default=True)
        )

        result = self._yasms.drop_phone(**self._build_args(
            account=account,
            phone_id=PHONE_ID,
        ))

        eq_(result, dict(status=u'ok'))

    def test_no_phone_number__not_found(self):
        """
        Номера нет среди телефонов учётной записи.
        """
        account = self._build_account(uid=UID, phones=[], phone_operations=[])

        result = self._yasms.drop_phone(**self._build_args(
            account=account,
            phone_id=PHONE_ID
        ))

        eq_(result, dict(status=u'notfound'))

    def test_phone_being_bound__not_found(self):
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

        result = self._yasms.drop_phone(**self._build_args(
            account=account,
            phone_id=PHONE_ID
        ))

        eq_(result, dict(status=u'notfound'))

    def test_phone_unbound__not_found(self):
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

        result = self._yasms.drop_phone(**self._build_args(
            account=account,
            phone_id=PHONE_ID
        ))

        eq_(result, dict(status=u'notfound'))

    def test_insecure_phone_number__no_operation__ok(self):
        """
        Удаляем простой номер без операции.
        """
        account = self._build_account(
            uid=UID,
            **build_phone_bound(
                PHONE_ID,
                PHONE_NUMBER,
                is_default=True,
            )
        )

        result = self._yasms.drop_phone(**self._build_args(
            account=account,
            phone_id=PHONE_ID
        ))

        eq_(result, dict(status=u'ok'))

        self.env.statbox.assert_has_written([])
        ok_(not account.phones.has_id(PHONE_ID))
        ok_(not account.phones.default)
        eq_(len(self.env.yasms.requests), 0)
        eq_(len(self.env.mailer.messages), 0)

    def test_insecure_phone_number__with_operation__ok(self):
        """
        Удаляем простой номер с операцией.
        """
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_bound(
                    PHONE_ID,
                    PHONE_NUMBER,
                    is_default=True,
                ),
                build_securify_operation(OPERATION_ID, PHONE_ID),
            )
        )

        result = self._yasms.drop_phone(**self._build_args(
            account=account,
            phone_id=PHONE_ID
        ))

        eq_(result, dict(status=u'ok'))

        self.env.statbox.assert_has_written([])
        ok_(not account.phones.has_id(PHONE_ID))
        ok_(not account.phones.default)
        eq_(len(self.env.yasms.requests), 0)
        eq_(len(self.env.mailer.messages), 0)

    def test_secure_phone_number__no_operation__ok(self):
        """
        Удаляем защищённый номер без операции.
        """
        account = self._build_account(
            uid=UID,
            **build_phone_secured(
                PHONE_ID,
                PHONE_NUMBER,
                is_default=True,
            )
        )

        result = self._yasms.drop_phone(**self._build_args(
            account=account,
            phone_id=PHONE_ID
        ))

        eq_(result, dict(status=u'ok'))

        self.env.statbox.assert_has_written([])
        ok_(not account.phones.has_id(PHONE_ID))
        ok_(not account.phones.default)
        eq_(len(self.env.yasms.requests), 0)
        eq_(len(self.env.mailer.messages), 0)

    def test_secure_phone_number__with_operation__ok(self):
        """
        Удаляем защищённый номер с операцией.
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

        result = self._yasms.drop_phone(**self._build_args(
            account=account,
            phone_id=PHONE_ID
        ))

        eq_(result, dict(status=u'ok'))

        self.env.statbox.assert_has_written([])
        ok_(not account.phones.has_id(PHONE_ID))
        ok_(not account.phones.default)
        eq_(len(self.env.yasms.requests), 0)
        eq_(len(self.env.mailer.messages), 0)

    def test_secure_phone_number__with_alias__ok(self):
        """
        Удаляем защищённый номер с алиасом.
        """
        account = self._build_account(
            **deep_merge(
                dict(
                    uid=UID,
                    firstname=u'Андрей',
                    login=u'andrey1931',
                    aliases={u'portal': u'andrey1931'},
                    language=u'ru',
                    emails=[
                        self.env.email_toolkit.create_native_email(
                            login=u'andrey1931',
                            domain=u'yandex-team.ru',
                        ),
                    ],
                ),
                build_phone_secured(
                    PHONE_ID,
                    PHONE_NUMBER,
                    is_default=True,
                    is_alias=True,
                ),
            )
        )

        result = self._yasms.drop_phone(**self._build_args(
            account=account,
            phone_id=PHONE_ID
        ))

        eq_(result, dict(status=u'ok'))

        self.env.statbox.assert_has_written([])
        ok_(not account.phones.has_id(PHONE_ID))
        ok_(not account.phones.default)
        eq_(len(self.env.yasms.requests), 0)

        eq_(len(self.env.mailer.messages), 1)
        assert_user_notified_about_alias_as_login_and_email_disabled(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=u'andrey1931@yandex-team.ru',
            firstname=u'Андрей',
            login=u'andrey1931',
            portal_email=u'andrey1931@yandex-team.ru',
            phonenumber_alias=u'79012233444',
        )

    def test_secure_phone_number__2fa_on__error(self):
        """
        Номер защищён и 2fa активна.
        """
        account = self._build_account(
            **deep_merge(
                dict(
                    uid=UID,
                    attributes={
                        u'account.2fa_on': True,
                    },
                ),
                build_phone_secured(
                    PHONE_ID,
                    PHONE_NUMBER,
                    is_default=True,
                ),
            )
        )

        with assert_raises(YaSmsPhoneBindingsLimitExceeded):
            self._yasms.drop_phone(**self._build_args(
                account=account,
                phone_id=PHONE_ID
            ))

    def test_secure_phone_number__sms_2fa_on__error(self):
        """
        Номер защищён и sms-2fa активна.
        """
        account = self._build_account(
            **deep_merge(
                dict(
                    uid=UID,
                    attributes={
                        u'account.sms_2fa_on': True,
                    },
                ),
                build_phone_secured(
                    PHONE_ID,
                    PHONE_NUMBER,
                    is_default=True,
                ),
            )
        )

        with assert_raises(YaSmsPhoneBindingsLimitExceeded):
            self._yasms.drop_phone(**self._build_args(
                account=account,
                phone_id=PHONE_ID
            ))
