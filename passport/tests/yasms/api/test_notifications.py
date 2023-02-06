# -*- coding: utf-8 -*-

from contextlib import contextmanager
from datetime import datetime

from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.api.test.emails import assert_user_notified_about_secure_phone_bound_to_passwordless_account
from passport.backend.core.builders.yasms.exceptions import YaSmsError
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.mailer.faker.mail_utils import create_native_email
from passport.backend.core.models.phones.faker import (
    build_account,
    build_phone_bound,
    build_phone_secured,
    build_remove_operation,
    build_simple_replaces_secure_operations,
)
from passport.backend.core.models.phones.phones import (
    RemoveSecureOperation,
    ReplaceSecurePhoneWithNonboundPhoneOperation,
)
from passport.backend.core.test.consts import (
    TEST_PASSWORD_HASH1,
    TEST_SOCIAL_LOGIN1,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.bit_vector import PhoneOperationFlags
from passport.backend.core.yasms.notifications import (
    notify_about_phone_changes,
    notify_user_by_email_that_phone_removal_started,
    notify_user_by_sms_that_secure_phone_removal_started,
)
from passport.backend.core.yasms.test import sms as sms_notifications
from passport.backend.core.yasms.test.emails import (
    assert_user_notified_about_secure_phone_bound,
    assert_user_notified_about_secure_phone_removal_started,
    assert_user_notified_about_secure_phone_removed_with_quarantine,
    assert_user_notified_about_secure_phone_removed_without_quarantine,
    assert_user_notified_about_secure_phone_replaced,
    assert_user_notified_about_secure_phone_replacement_started,
)
from passport.backend.utils.common import deep_merge

from .base import BaseYasmsTestCase
from .consts import (
    TEST_CONFIRMATION_CODE1,
    TEST_CONSUMER1,
    TEST_EMAIL1,
    TEST_FIRSTNAME1,
    TEST_IP,
    TEST_LOGIN1,
    TEST_OPERATION_ID1,
    TEST_OPERATION_ID2,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_PHONE_NUMBER1,
    TEST_PHONE_NUMBER2,
    TEST_TIME1,
    TEST_UID1,
    TEST_USER_AGENT,
)


@with_settings_hosts(
    BLACKBOX_URL='http://blackbox.url/',
    BLACKBOX_ATTRIBUTES=tuple(),
    BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=tuple(),
)
class TestNotifyAboutPhoneChanges(BaseYasmsTestCase):
    def setUp(self):
        super(TestNotifyAboutPhoneChanges, self).setUp()
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

    def test_no_secure_phone(self):
        account = self._build_account()

        with self._notify_about_phone_changes(account):
            pass

        self._assert_no_mail_sent()

    def test_secure_phone__no_secure_op(self):
        account = self._build_account(
            **build_phone_secured(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164)
        )

        with self._notify_about_phone_changes(account):
            pass

        self._assert_no_mail_sent()

    def test_bind_secure_phone(self):
        account = self._build_account()

        with self._notify_about_phone_changes(account):
            now = datetime.now()
            account.phones.secure = account.phones.create(
                number=TEST_PHONE_NUMBER1.e164,
                bound=now,
                confirmed=now,
                secured=now,
            )

        self._assert_user_notified_about_secure_phone_bound()

    def test_bind_secure_phone__passwordless_account(self):
        account = self._build_account(
            aliases=dict(social=TEST_SOCIAL_LOGIN1),
            crypt_password=None,
            login=TEST_SOCIAL_LOGIN1,
        )

        with self._notify_about_phone_changes(account):
            now = datetime.now()
            account.phones.secure = account.phones.create(
                number=TEST_PHONE_NUMBER1.e164,
                bound=now,
                confirmed=now,
                secured=now,
            )

        self._assert_user_notified_about_secure_phone_bound_to_passwordless_account()

    def test_securify_simple_phone(self):
        account = self._build_account(
            **build_phone_bound(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164)
        )

        with self._notify_about_phone_changes(account):
            phone = account.phones.by_id(TEST_PHONE_ID1)
            phone.secured = datetime.now()
            account.phones.secure = phone

        self._assert_user_notified_about_secure_phone_bound()

    def test_start_replace_with_quarantine(self):
        account = self._build_account(
            **build_phone_secured(TEST_PHONE_ID2, TEST_PHONE_NUMBER2.e164)
        )

        with self._notify_about_phone_changes(account):
            now = datetime.now()
            account.phones.create(
                number=TEST_PHONE_NUMBER1.e164,
                existing_phone_id=TEST_PHONE_ID1,
            )
            logical_op = ReplaceSecurePhoneWithNonboundPhoneOperation.create(
                phone_manager=account.phones,
                secure_phone_id=TEST_PHONE_ID2,
                being_bound_phone_id=TEST_PHONE_ID1,
                secure_code=None,
                being_bound_code=TEST_CONFIRMATION_CODE1,
                statbox=self._statbox,
            )
            logical_op.password_verified = now
            logical_op.confirm_phone(TEST_PHONE_ID1, TEST_CONFIRMATION_CODE1)

        self._assert_user_notified_about_secure_phone_replacement_started()
        self._assert_user_notified_about_secure_phone_replacement_started_by_sms()

    def test_start_replace_without_quarantine(self):
        account = self._build_account(
            **build_phone_secured(TEST_PHONE_ID2, TEST_PHONE_NUMBER2.e164)
        )

        with self._notify_about_phone_changes(account):
            now = datetime.now()
            account.phones.create(
                number=TEST_PHONE_NUMBER1.e164,
                existing_phone_id=TEST_PHONE_ID1,
            )
            logical_op = ReplaceSecurePhoneWithNonboundPhoneOperation.create(
                phone_manager=account.phones,
                secure_phone_id=TEST_PHONE_ID2,
                being_bound_phone_id=TEST_PHONE_ID1,
                secure_code=TEST_CONFIRMATION_CODE1,
                being_bound_code=TEST_CONFIRMATION_CODE1,
                statbox=self._statbox,
            )
            logical_op.password_verified = now
            logical_op.confirm_phone(TEST_PHONE_ID1, TEST_CONFIRMATION_CODE1)

        self._assert_no_mail_sent()
        self._assert_user_notified_about_secure_phone_replacement_started_by_sms()

    def test_start_replace_not_ready_for_quarantine(self):
        account = self._build_account(
            **build_phone_secured(TEST_PHONE_ID2, TEST_PHONE_NUMBER2.e164)
        )

        with self._notify_about_phone_changes(account):
            account.phones.create(
                number=TEST_PHONE_NUMBER1.e164,
                existing_phone_id=TEST_PHONE_ID1,
            )
            ReplaceSecurePhoneWithNonboundPhoneOperation.create(
                phone_manager=account.phones,
                secure_phone_id=TEST_PHONE_ID2,
                being_bound_phone_id=TEST_PHONE_ID1,
                secure_code=None,
                being_bound_code=TEST_CONFIRMATION_CODE1,
                statbox=self._statbox,
            )

        self._assert_no_mail_sent()
        self._assert_no_sms_sent()

    def test_start_replace_without_quarantine__no_confirmations(self):
        account = self._build_account(
            **build_phone_secured(TEST_PHONE_ID2, TEST_PHONE_NUMBER2.e164)
        )

        with self._notify_about_phone_changes(account):
            account.phones.create(
                number=TEST_PHONE_NUMBER1.e164,
                existing_phone_id=TEST_PHONE_ID1,
            )
            ReplaceSecurePhoneWithNonboundPhoneOperation.create(
                phone_manager=account.phones,
                secure_phone_id=TEST_PHONE_ID2,
                being_bound_phone_id=TEST_PHONE_ID1,
                secure_code=TEST_CONFIRMATION_CODE1,
                being_bound_code=TEST_CONFIRMATION_CODE1,
                statbox=self._statbox,
            )

        self._assert_no_mail_sent()
        self._assert_user_notified_about_secure_phone_replacement_started_by_sms()

    def test_replace_secure_phone__no_operation(self):
        account = self._build_account(
            **build_phone_secured(TEST_PHONE_ID2, TEST_PHONE_NUMBER2.e164)
        )

        with self._notify_about_phone_changes(account):
            account.phones.remove(TEST_PHONE_ID2)
            now = datetime.now()
            account.phones.secure = account.phones.create(
                number=TEST_PHONE_NUMBER1.e164,
                bound=now,
                confirmed=now,
                secured=now,
            )

        self._assert_user_notified_about_secure_phone_replaced()

    def test_replace_secure_phone__not_removed(self):
        account = self._build_account(
            **build_phone_secured(TEST_PHONE_ID2, TEST_PHONE_NUMBER2.e164)
        )

        with self._notify_about_phone_changes(account):
            now = datetime.now()
            account.phones.secure = account.phones.create(
                number=TEST_PHONE_NUMBER1.e164,
                bound=now,
                confirmed=now,
                secured=now,
            )
            phone = account.phones.by_id(TEST_PHONE_ID2)
            phone.secured = None

        self._assert_user_notified_about_secure_phone_replaced()

    def test_replace_secure_phone__without_quarantine(self):
        now = datetime.now()

        account = self._build_account(
            **deep_merge(
                build_phone_secured(TEST_PHONE_ID2, TEST_PHONE_NUMBER2.e164),
                build_phone_bound(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164),
                build_simple_replaces_secure_operations(
                    secure_operation_id=TEST_OPERATION_ID1,
                    secure_phone_id=TEST_PHONE_ID2,
                    simple_operation_id=TEST_OPERATION_ID2,
                    simple_phone_id=TEST_PHONE_ID1,
                    simple_phone_number=TEST_PHONE_NUMBER1.e164,
                    simple_code_confirmed=now,
                    secure_code_confirmed=now,
                    password_verified=now,
                ),
            )
        )

        with self._notify_about_phone_changes(account):
            phone = account.phones.by_id(TEST_PHONE_ID1)
            logical_op = phone.get_logical_operation(self._statbox)
            logical_op.apply()

        self._assert_user_notified_about_secure_phone_replaced()

    def test_replace_secure_phone__with_quarantine(self):
        now = datetime.now()
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True

        account = self._build_account(
            **deep_merge(
                build_phone_secured(TEST_PHONE_ID2, TEST_PHONE_NUMBER2.e164),
                build_phone_bound(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164),
                build_simple_replaces_secure_operations(
                    secure_operation_id=TEST_OPERATION_ID1,
                    secure_phone_id=TEST_PHONE_ID2,
                    simple_operation_id=TEST_OPERATION_ID2,
                    simple_phone_id=TEST_PHONE_ID1,
                    simple_phone_number=TEST_PHONE_NUMBER1.e164,
                    simple_code_confirmed=now,
                    secure_code_value=None,
                    password_verified=now,
                    finished=now,
                    flags=phone_operation_flags,
                ),
            )
        )

        with self._notify_about_phone_changes(account):
            phone = account.phones.by_id(TEST_PHONE_ID1)
            logical_op = phone.get_logical_operation(self._statbox)
            logical_op.apply(is_harvester=True)

        self._assert_user_notified_about_secure_phone_replaced()

    def test_start_removal_with_quarantine(self):
        account = self._build_account(
            **build_phone_secured(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164)
        )

        with self._notify_about_phone_changes(account):
            logical_op = RemoveSecureOperation.create(
                phone_manager=account.phones,
                phone_id=TEST_PHONE_ID1,
                code=None,
                statbox=self._statbox,
            )
            logical_op.password_verified = datetime.now()

        self._assert_user_notified_about_secure_phone_removal_started()
        self._assert_user_notified_about_secure_phone_removal_started_by_sms()

    def test_start_removal_without_quarantine(self):
        account = self._build_account(
            **build_phone_secured(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164)
        )

        with self._notify_about_phone_changes(account):
            logical_op = RemoveSecureOperation.create(
                phone_manager=account.phones,
                phone_id=TEST_PHONE_ID1,
                code=TEST_CONFIRMATION_CODE1,
                statbox=self._statbox,
            )
            logical_op.password_verified = datetime.now()

        self._assert_no_mail_sent()
        self._assert_user_notified_about_secure_phone_removal_started_by_sms()

    def test_start_removal_not_ready_for_quarantine(self):
        account = self._build_account(
            **build_phone_secured(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164)
        )

        with self._notify_about_phone_changes(account):
            RemoveSecureOperation.create(
                phone_manager=account.phones,
                phone_id=TEST_PHONE_ID1,
                code=None,
                statbox=self._statbox,
            )

        self._assert_no_mail_sent()
        self._assert_no_sms_sent()

    def test_start_removal_without_quarantine__no_confirmations(self):
        account = self._build_account(
            **build_phone_secured(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164)
        )

        with self._notify_about_phone_changes(account):
            RemoveSecureOperation.create(
                phone_manager=account.phones,
                phone_id=TEST_PHONE_ID1,
                code=TEST_CONFIRMATION_CODE1,
                statbox=self._statbox,
            )

        self._assert_no_mail_sent()
        self._assert_user_notified_about_secure_phone_removal_started_by_sms()

    def test_secure_phone_removed__no_operation(self):
        account = self._build_account(
            **build_phone_secured(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164)
        )

        with self._notify_about_phone_changes(account):
            account.phones.remove(TEST_PHONE_ID1)

        self._assert_user_notified_about_secure_phone_removed_without_quarantine()

    def test_secure_phone_removed__without_quarantine(self):
        now = datetime.now()

        account = self._build_account(
            **deep_merge(
                build_phone_secured(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164),
                build_remove_operation(
                    operation_id=TEST_OPERATION_ID1,
                    phone_id=TEST_PHONE_ID1,
                    code_confirmed=now,
                    password_verified=now,
                ),
            )
        )

        with self._notify_about_phone_changes(account):
            logical_op = account.phones.secure.get_logical_operation(self._statbox)
            logical_op.apply()

        self._assert_user_notified_about_secure_phone_removed_without_quarantine()

    def test_secure_phone_removed__with_quarantine(self):
        now = datetime.now()
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True

        account = self._build_account(
            **deep_merge(
                build_phone_secured(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164),
                build_remove_operation(
                    operation_id=TEST_OPERATION_ID1,
                    phone_id=TEST_PHONE_ID1,
                    code_value=None,
                    password_verified=now,
                    finished=now,
                    flags=phone_operation_flags,
                ),
            )
        )

        with self._notify_about_phone_changes(account):
            logical_op = account.phones.secure.get_logical_operation(self._statbox)
            logical_op.apply(is_harvester=True)

        self._assert_user_notified_about_secure_phone_removed_with_quarantine()

    def _build_account(self, **kwargs):
        defaults = {
            'uid': TEST_UID1,
            'login': TEST_LOGIN1,
            'firstname': TEST_FIRSTNAME1,
            'crypt_password': TEST_PASSWORD_HASH1,
            'emails': [
                create_native_email(
                    login=TEST_EMAIL1.split(u'@')[0],
                    domain=TEST_EMAIL1.split(u'@')[1],
                ),
            ],
        }
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return build_account(
            blackbox_faker=self.env.blackbox,
            **kwargs
        )

    @contextmanager
    def _notify_about_phone_changes(self, account):
        with notify_about_phone_changes(
            account=account,
            yasms_builder=self._yasms_builder,
            statbox=self._statbox,
            consumer=TEST_CONSUMER1,
            language='ru',
            client_ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
        ):
            yield

    def _assert_no_mail_sent(self):
        eq_(self.env.mailer.message_count, 0)

    def _assert_user_notified_about_secure_phone_bound(self):
        assert_user_notified_about_secure_phone_bound(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_EMAIL1,
            firstname=TEST_FIRSTNAME1,
            login=TEST_LOGIN1,
        )

    def _assert_user_notified_about_secure_phone_bound_to_passwordless_account(self):
        assert_user_notified_about_secure_phone_bound_to_passwordless_account(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_EMAIL1,
            firstname=TEST_FIRSTNAME1,
            login=TEST_FIRSTNAME1,
        )

    def _assert_user_notified_about_secure_phone_replaced(self):
        assert_user_notified_about_secure_phone_replaced(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_EMAIL1,
            firstname=TEST_FIRSTNAME1,
            login=TEST_LOGIN1,
        )

    def _assert_user_notified_about_secure_phone_replacement_started(self):
        assert_user_notified_about_secure_phone_replacement_started(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_EMAIL1,
            firstname=TEST_FIRSTNAME1,
            login=TEST_LOGIN1,
        )

    def _assert_user_notified_about_secure_phone_removal_started(self):
        assert_user_notified_about_secure_phone_removal_started(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_EMAIL1,
            firstname=TEST_FIRSTNAME1,
            login=TEST_LOGIN1,
        )

    def _assert_user_notified_about_secure_phone_removed_without_quarantine(self):
        assert_user_notified_about_secure_phone_removed_without_quarantine(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_EMAIL1,
            firstname=TEST_FIRSTNAME1,
            login=TEST_LOGIN1,
        )

    def _assert_user_notified_about_secure_phone_removed_with_quarantine(self):
        assert_user_notified_about_secure_phone_removed_with_quarantine(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_EMAIL1,
            firstname=TEST_FIRSTNAME1,
            login=TEST_LOGIN1,
        )

    def _assert_user_notified_about_secure_phone_replacement_started_by_sms(self):
        sms_notifications.assert_user_notified_about_secure_phone_replacement_started(
            yasms_builder_faker=self.env.yasms,
            language='ru',
            phone_number=TEST_PHONE_NUMBER2,
            uid=TEST_UID1,
        )

    def _assert_user_notified_about_secure_phone_removal_started_by_sms(self):
        sms_notifications.assert_user_notified_about_secure_phone_removal_started(
            yasms_builder_faker=self.env.yasms,
            language='ru',
            phone_number=TEST_PHONE_NUMBER1,
            uid=TEST_UID1,
        )

    def _assert_no_sms_sent(self):
        eq_(len(self.env.yasms.requests), 0)


class TestNotifyUserBySmsThatPhoneRemovalStarted(BaseYasmsTestCase):
    def _setup_yasms_to_serve_good_response(self):
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )

    def _build_args(self, **kwargs):
        kwargs.setdefault(u'account', self._build_account())
        kwargs.setdefault(u'yasms_builder', self._yasms_builder)
        kwargs.setdefault(u'statbox', self._statbox)
        kwargs.setdefault(u'consumer', TEST_CONSUMER1)
        kwargs.setdefault(u'user_agent', TEST_USER_AGENT)
        kwargs.setdefault(u'client_ip', TEST_IP)
        return kwargs

    def _build_account(self, **kwargs):
        kwargs.setdefault(u'uid', TEST_UID1)
        kwargs.setdefault(u'language', u'ru')
        kwargs.setdefault(u'phones', [{
            u'id': 1,
            u'number': u'+79010000001',
            u'created': datetime(2001, 2, 3, 4, 5, 6),
            u'bound': datetime(2001, 2, 3, 4, 5, 6),
            u'confirmed': datetime(2001, 2, 3, 4, 5, 6),
            u'secured': datetime(2001, 2, 3, 4, 5, 6),
        }])
        kwargs.setdefault(u'attributes', {u'phones.secure': 1})
        return build_account(**kwargs)

    def test_account_language_russian(self):
        """
        Когда язык учётной записи русский, текст уведомления на русском языке.
        """
        self._setup_yasms_to_serve_good_response()

        notify_user_by_sms_that_secure_phone_removal_started(
            **self._build_args(account=self._build_account(language=u'ru'))
        )

        requests = self.env.yasms.get_requests_by_method(u'send_sms')
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            u'text': u'Начато удаление телефона на Яндексе: https://ya.cc/sms-help-ru',
        })

    def test_account_language_english(self):
        """
        Когда язык учётной записи английский, текст уведомления на английском языке.
        """
        self._setup_yasms_to_serve_good_response()

        notify_user_by_sms_that_secure_phone_removal_started(
            **self._build_args(account=self._build_account(language=u'en'))
        )

        requests = self.env.yasms.get_requests_by_method(u'send_sms')
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            u'text': u'Phone number has been recently deleted on Yandex: https://ya.cc/sms-help-com',
        })

    def test_pass_consumer(self):
        """
        Потребитель передаётся в Я.Смс.
        """
        self._setup_yasms_to_serve_good_response()

        notify_user_by_sms_that_secure_phone_removal_started(
            **self._build_args(consumer=u'test_consumer')
        )

        requests = self.env.yasms.get_requests_by_method(u'send_sms')
        eq_(len(requests), 1)
        requests[0].assert_query_contains({u'caller': u'test_consumer'})

    def test_uses_secure_phone_number(self):
        """
        Уведомление отправляется на защищённый номер.
        """
        self._setup_yasms_to_serve_good_response()

        notify_user_by_sms_that_secure_phone_removal_started(
            **self._build_args(
                account=self._build_account(
                    phones=[{
                        u'id': 1,
                        u'number': TEST_PHONE_NUMBER1.e164,
                        u'created': TEST_TIME1,
                        u'bound': TEST_TIME1,
                        u'confirmed': TEST_TIME1,
                        u'secured': TEST_TIME1,
                    }],
                    attributes={u'phones.secure': 1},
                ),
            )
        )

        requests = self.env.yasms.get_requests_by_method(u'send_sms')
        eq_(len(requests), 1)
        requests[0].assert_query_contains({u'phone': TEST_PHONE_NUMBER1.e164})

    def test_pass_identity(self):
        """
        В Я.Смс передаётся правильный identity.
        """
        self._setup_yasms_to_serve_good_response()

        notify_user_by_sms_that_secure_phone_removal_started(
            **self._build_args(statbox=self._statbox)
        )

        requests = self.env.yasms.get_requests_by_method(u'send_sms')
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            u'identity': u'notify_user_by_sms_that_secure_phone_removal_started.notify',
        })

    def test_pass_account_uid(self):
        """
        В Я.Смс передаётся идентификатор учётной записи.
        """
        self._setup_yasms_to_serve_good_response()

        notify_user_by_sms_that_secure_phone_removal_started(
            **self._build_args(account=self._build_account(uid=TEST_UID1))
        )

        requests = self.env.yasms.get_requests_by_method(u'send_sms')
        eq_(len(requests), 1)
        requests[0].assert_query_contains({u'from_uid': str(TEST_UID1)})

    def test_write_success_to_statbox(self):
        """
        Делаем запись в статбокс об отправленном уведомлении.
        """
        self._setup_yasms_to_serve_good_response()

        notify_user_by_sms_that_secure_phone_removal_started(
            **self._build_args(
                account=self._build_account(
                    uid=TEST_UID1,
                    phones=[{
                        u'id': 1,
                        u'number': u'+79012345678',
                        u'created': TEST_TIME1,
                        u'bound': TEST_TIME1,
                        u'confirmed': TEST_TIME1,
                        u'secured': TEST_TIME1,
                    }],
                    attributes={u'phones.secure': 1},
                ),
            )
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'base',
                action=u'notify_user_by_sms_that_secure_phone_removal_started.notification_sent',
                number=u'+79012******',
                uid=str(TEST_UID1),
                sms_id='1',
            ),
        ])

    @raises(AttributeError)
    def test_no_secure_number(self):
        """
        Нет защищённого номера, некуда высылать уведомление, падаем с ошибкой.
        """
        self._setup_yasms_to_serve_good_response()

        notify_user_by_sms_that_secure_phone_removal_started(
            **self._build_args(
                account=self._build_account(
                    phones=[{
                        u'id': 1,
                        u'number': TEST_PHONE_NUMBER1.e164,
                        u'created': TEST_TIME1,
                        u'bound': TEST_TIME1,
                        u'confirmed': TEST_TIME1,
                        u'secured': TEST_TIME1,
                    }],
                    attributes={},
                ),
            )
        )

    def test_log_yasms_failed_to_statbox(self):
        """
        Не падаем, когда падает Я.Смс и делаем запись в статбокс.
        """
        self.env.yasms.set_response_side_effect('send_sms', YaSmsError())

        notify_user_by_sms_that_secure_phone_removal_started(
            **self._build_args(
                account=self._build_account(
                    uid=TEST_UID1,
                    phones=[{
                        u'id': 1,
                        u'number': u'+79012345678',
                        u'created': TEST_TIME1,
                        u'bound': TEST_TIME1,
                        u'confirmed': TEST_TIME1,
                        u'secured': TEST_TIME1,
                    }],
                    attributes={u'phones.secure': 1},
                ),
            )
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'base',
                error=u'sms.isnt_sent',
                action=u'notify_user_by_sms_that_secure_phone_removal_started',
                number=u'+79012******',
                uid=str(TEST_UID1),
            ),
        ])


class TestNotifyUserByEmailThatPhoneRemovalStarted(BaseYasmsTestCase):
    def _build_account(self, **kwargs):
        defaults = dict(
            uid=TEST_UID1,
            firstname=u'Андрей',
            lastname=u'Исаев',
            login=u'andrey1931',
            language=u'ru',
            crypt_password=TEST_PASSWORD_HASH1,
            emails=[
                self.env.email_toolkit.create_native_email(
                    login=u'andrey1931',
                    domain=u'yandex-team.ru',
                ),
            ],
        )
        for key, val in defaults.items():
            kwargs.setdefault(key, val)
        return build_account(**kwargs)

    def test_account_russian_language(self):
        """
        Используется русский язык, когда пользователь предпочитает его.
        """
        notify_user_by_email_that_phone_removal_started(
            account=self._build_account(language=u'ru'),
        )

        assert_user_notified_about_secure_phone_removal_started(
            mailer_faker=self.env.mailer,
            language=u'ru',
            email_address=u'andrey1931@yandex-team.ru',
            firstname=u'Андрей',
            login=u'andrey1931',
        )

    def test_account_english_language(self):
        """
        Используется английский язык, когда пользователь предпочитает его.
        """
        notify_user_by_email_that_phone_removal_started(
            account=self._build_account(language=u'en'),
        )

        assert_user_notified_about_secure_phone_removal_started(
            mailer_faker=self.env.mailer,
            language=u'en',
            email_address=u'andrey1931@yandex-team.ru',
            firstname=u'Андрей',
            login=u'andrey1931',
        )

    def test_mask_login_when_send_to_external_email(self):
        """
        Когда высылаем уведомление на внешний почтовый ящик, маскируем логин.
        """
        notify_user_by_email_that_phone_removal_started(
            account=self._build_account(
                login=u'andrey1931',
                emails=[
                    self.env.email_toolkit.create_validated_external_email(
                        login=u'andrey.isaeff',
                        domain=u'gmail.com',
                    ),
                ],
            ),
        )

        messages = self.env.mailer.messages
        eq_(len(messages), 1)
        ok_(u'andrey1931' not in messages[0].body)
        ok_(u'andr***' in messages[0].body)

    def test_no_firstname(self):
        """
        Ведём себя приемлимо, когда имя пользователя не известно.
        """
        notify_user_by_email_that_phone_removal_started(
            account=self._build_account(
                firstname=None,
                display_name={u'name': u'1931', u'default_avatar': u''},
            ),
        )

        messages = self.env.mailer.messages
        eq_(len(messages), 1)
        ok_(u'Здравствуйте, 1931!' in messages[0].body)

    def test_many_emails(self):
        """
        Уведомление высылаются на все почтовые ящики пользователя.
        """
        notify_user_by_email_that_phone_removal_started(
            account=self._build_account(
                emails=[
                    self.env.email_toolkit.create_native_email(
                        login=u'andrey1931',
                        domain=u'yandex-team.ru',
                    ),
                    self.env.email_toolkit.create_validated_external_email(
                        login=u'andrey.isaeff',
                        domain=u'gmail.com',
                    ),
                ],
            ),
        )
        eq_(len(self.env.mailer.messages), 2)

    def test_no_emails(self):
        """
        У пользователя нет почтовых адресов.
        """
        notify_user_by_email_that_phone_removal_started(
            account=self._build_account(emails=[]),
        )
        eq_(len(self.env.mailer.messages), 0)
