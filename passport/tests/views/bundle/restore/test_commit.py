# -*- coding: utf-8 -*-

import base64
from functools import partial
import json

from nose.tools import ok_
from nose_parameterized import parameterized
from passport.backend.api.common.authorization import SessionScope
from passport.backend.api.test.mixins import (
    AccountModificationNotifyTestMixin,
    EmailTestMixin,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.tests.views.bundle.restore.test.test_base import (
    AccountValidityTestsMixin,
    CommonTestsMixin,
    eq_,
    RestoreBaseTestCase,
)
from passport.backend.api.views.bundle.restore.base import *
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_family_info_response,
    blackbox_hosted_domains_response,
    blackbox_phone_bindings_response,
    blackbox_pwdhistory_response,
    blackbox_test_pwd_hashes_response,
)
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.counters.change_password_counter import get_per_phone_number_buckets
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
)
from passport.backend.core.models.phones.faker import (
    assert_no_phone_in_db,
    assert_no_secure_phone,
    assert_secure_phone_being_aliasified,
    assert_secure_phone_being_removed,
    assert_secure_phone_being_replaced,
    assert_secure_phone_bound,
    assert_simple_phone_bound,
    assert_simple_phone_replace_secure,
    PhoneIdGeneratorFaker,
)
from passport.backend.core.support_link_types import (
    SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
    SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
    SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
)
from passport.backend.core.test.data import TEST_SERIALIZED_PASSWORD
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.core.types.email.email import mask_email_for_challenge
from passport.backend.core.types.login.login import masked_login
from passport.backend.core.types.phone_number.phone_number import mask_phone_number
from passport.backend.core.yasms.test.emails import (
    assert_user_notified_about_secure_phone_bound,
    assert_user_notified_about_secure_phone_replacement_started,
)
from passport.backend.utils.common import (
    merge_dicts,
    remove_none_values,
)


TEST_APP_ID = 'app-id'


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:login_method_change': 5,
            'push:restore': 5,
        },
    )
)
class RestoreCommitTestCaseBase(RestoreBaseTestCase, EmailTestMixin, AccountModificationNotifyTestMixin):
    restore_step = 'commit'

    default_url = '/1/bundle/restore/commit/'

    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        super(RestoreCommitTestCaseBase, self).setUp()
        _, self.next_track_id = self.env.track_manager.get_manager_and_trackid('register')
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.next_track_id)

        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=False),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )
        encoded_hash = base64.b64encode(TEST_OLD_SERIALIZED_PASSWORD)
        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response({encoded_hash: False}),
        )
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )
        self.setup_kolmogor()
        self.start_account_modification_notify_mocks(ip=TEST_IP)

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        self.track_id_generator.stop()
        del self.track_id_generator
        super(RestoreCommitTestCaseBase, self).tearDown()

    def set_track_values(self, current_restore_method=RESTORE_METHOD_PHONE,
                         restore_state=RESTORE_STATE_METHOD_PASSED, **params):
        params.update(
            restore_state=restore_state,
            current_restore_method=current_restore_method,
        )
        super(RestoreCommitTestCaseBase, self).set_track_values(**params)

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
                str(rate),
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK', 'OK', 'OK'])

    def query_params(self, password=TEST_PASSWORD, display_language='ru', new_method=None, **extra_args):
        return dict(
            extra_args,
            password=password,
            display_language=display_language,
            new_method=new_method,
        )

    def assert_track_updated(self, restore_state=RESTORE_STATE_COMMIT_PASSED,
                             is_2fa_restore=False,
                             human_readable_login=TEST_DEFAULT_LOGIN,
                             machine_readable_login=TEST_DEFAULT_LOGIN,
                             country='ru',
                             language='ru',
                             has_restorable_email=False,
                             has_secure_phone_number=True,
                             allow_authorization=True,
                             have_password=True,
                             is_password_passed=True,
                             allow_oauth_authorization=False,
                             is_glogouted=True,
                             session_scope=str(SessionScope.xsession),
                             **data):
        data.update(
            allow_authorization=allow_authorization,
            allow_oauth_authorization=allow_oauth_authorization,
            country=country,
            has_restorable_email=has_restorable_email,
            has_secure_phone_number=has_secure_phone_number,
            have_password=have_password,
            human_readable_login=human_readable_login,
            is_otp_restore_passed=is_2fa_restore,
            is_password_passed=is_password_passed,
            is_web_sessions_logout=True if is_glogouted else None,
            language=language,
            machine_readable_login=machine_readable_login,
            restore_state=restore_state,
            session_scope=session_scope,
        )
        if has_secure_phone_number:
            data.update(secure_phone_number=TEST_PHONE)
        data = remove_none_values(data)
        super(RestoreCommitTestCaseBase, self).assert_track_updated(**data)

    def build_expected_2fa_emails_context(self, send_to_external=True, with_login_method_change_email=False):
        def build_email(address, is_native):
            return {
                'language': 'ru',
                'addresses': [address],
                'subject': '2fa_disabled_on_restore.subject',
                'tanker_keys': {
                    'greeting': {'FIRST_NAME': TEST_DEFAULT_FIRSTNAME},
                    '2fa_disabled_on_restore.auth': {
                        'ACCESS_CONTROL_URL_BEGIN': '<a href=\'https://passport.yandex.ru/profile/access\'>',
                        'ACCESS_CONTROL_URL_END': '</a>',
                    },
                    '2fa_disabled_on_restore.enable': {
                        'ACCESS_CONTROL_URL_BEGIN': '<a href=\'https://passport.yandex.ru/profile/access\'>',
                        'ACCESS_CONTROL_URL_END': '</a>',
                    },
                    '2fa_disabled_on_restore.feedback': {
                        'FEEDBACK_2FA_URL_BEGIN': '<a href=\'https://feedback2.yandex.ru/passport/problems/\'>',
                        'FEEDBACK_2FA_URL_END': '</a>',
                        'HELP_2FA_URL_BEGIN': '<a href=\'https://yandex.ru/support/passport/authorization/twofa.html\'>',
                        'HELP_2FA_URL_END': '</a>',
                    },
                    'signature.secure': {},
                    'feedback': {
                        'FEEDBACK_URL_BEGIN': '<a href=\'https://feedback2.yandex.ru/\'>',
                        'FEEDBACK_URL_END': '</a>',
                    },
                },
            }
        emails = [
            build_email(address='%s@%s' % (TEST_DEFAULT_LOGIN, 'yandex.ru'), is_native=True),
        ]
        if with_login_method_change_email:
            emails = [
                self.create_account_modification_mail(
                    'login_method_change',
                    '%s@%s' % (TEST_DEFAULT_LOGIN, 'gmail.com'),
                    dict(
                        login=TEST_DEFAULT_LOGIN,
                        USER_IP=TEST_IP,
                    ),
                    is_native=False,
                ),
                self.create_account_modification_mail(
                    'login_method_change',
                    '%s@%s' % (TEST_DEFAULT_LOGIN, 'yandex.ru'),
                    dict(
                        login=TEST_DEFAULT_LOGIN,
                        USER_IP=TEST_IP,
                    ),
                ),
            ] + emails
        if send_to_external:
            emails.insert(2, build_email(address='%s@%s' % (TEST_DEFAULT_LOGIN, 'gmail.com'), is_native=False))
        return emails

    def assert_2fa_emails_sent(self, send_to_external=True, with_login_method_change_email=False):
        expected_emails = self.build_expected_2fa_emails_context(
            send_to_external=send_to_external,
            with_login_method_change_email=with_login_method_change_email,
        )
        self.assert_emails_sent(expected_emails)

    def build_expected_secure_phone_replaced_with_quarantine_notifications(self, send_to_external=True):
        def build_email(address, is_native):
            return partial(
                assert_user_notified_about_secure_phone_replacement_started,
                mailer_faker=self.env.mailer,
                language='ru',
                email_address=address,
                firstname=TEST_DEFAULT_FIRSTNAME,
                login=masked_login(TEST_DEFAULT_LOGIN) if not is_native else TEST_DEFAULT_LOGIN,
            )
        emails = [
            build_email(address='%s@%s' % (TEST_DEFAULT_LOGIN, 'yandex.ru'), is_native=True),
        ]
        if send_to_external:
            emails.insert(0, build_email(address='%s@%s' % (TEST_DEFAULT_LOGIN, 'gmail.com'), is_native=False))
        return emails

    def build_expected_secure_phone_bound_notifications_context(self, send_to_external=True):
        def build_email(address, is_native):
            return partial(
                assert_user_notified_about_secure_phone_bound,
                mailer_faker=self.env.mailer,
                language='ru',
                email_address=address,
                firstname=TEST_DEFAULT_FIRSTNAME,
                login=masked_login(TEST_DEFAULT_LOGIN) if not is_native else TEST_DEFAULT_LOGIN,
            )
        emails = [
            build_email(address='%s@%s' % (TEST_DEFAULT_LOGIN, 'yandex.ru'), is_native=True),
        ]
        if send_to_external:
            emails.insert(0, build_email(address='%s@%s' % (TEST_DEFAULT_LOGIN, 'gmail.com'), is_native=False))
        return emails

    def assert_secure_phone_bound_notifications_sent(self, send_to_external=True):
        expected_emails = self.build_expected_secure_phone_bound_notifications_context(send_to_external=send_to_external)
        self.assert_emails_sent(expected_emails)

    def build_expected_phone_restore_passed_email_context(self, send_to_external=True):
        def build_email(address, is_native):
            return {
                'language': 'ru',
                'addresses': [address],
                'subject': 'restore.auto.passed.subject',
                'tanker_keys': {
                    'greeting': {'FIRST_NAME': TEST_DEFAULT_FIRSTNAME},
                    'restore.auto.passed_by_phone.restored': {
                        'PHONE': TEST_PHONE_MASKED_FOR_EMAIL,
                        'LOGIN': TEST_DEFAULT_LOGIN if is_native else masked_login(TEST_DEFAULT_LOGIN),
                    },
                    'restore.auto.passed.in_that_case': {},
                    'restore.auto.passed.restore_again': {
                        'RESTORE_URL_BEGIN': '<a href=\'https://passport.yandex.ru/restoration\'>',
                        'RESTORE_URL_END': '</a>',
                    },
                    'restore.auto.passed_by_phone.check_phone': {
                        'PROFILE_PHONES_URL_BEGIN': '<a href=\'https://passport.yandex.ru/profile/phones\'>',
                        'PROFILE_PHONES_URL_END': '</a>',
                        'PHONE_ALERT_URL_BEGIN': '<a href=\'https://ya.cc/sms-help-ru\'>',
                        'PHONE_ALERT_URL_END': '</a>',
                    },
                    'signature.secure': {},
                    'feedback': {
                        'FEEDBACK_URL_BEGIN': '<a href=\'https://feedback2.yandex.ru/\'>',
                        'FEEDBACK_URL_END': '</a>',
                    },
                },
            }
        emails = [
            build_email(address='%s@%s' % (TEST_DEFAULT_LOGIN, 'yandex.ru'), is_native=True),
        ]
        if send_to_external:
            emails.insert(0, build_email(address='%s@%s' % (TEST_DEFAULT_LOGIN, 'gmail.com'), is_native=False))
        return emails

    def build_expected_hint_restore_passed_email_context(self, login=TEST_DEFAULT_LOGIN,
                                                         is_secure_phone_bound=False):
        def build_email(address, is_native):
            context = {
                'language': 'ru',
                'addresses': [address],
                'subject': 'restore.auto.passed.subject',
                'tanker_keys': {
                    'greeting': {'FIRST_NAME': TEST_DEFAULT_FIRSTNAME},
                    'restore.auto.passed_by_hint.restored': {
                        'LOGIN': login if is_native else masked_login(login),
                    },
                    'restore.auto.passed.in_that_case': {},
                    'restore.auto.passed.restore_again': {
                        'RESTORE_URL_BEGIN': '<a href=\'https://passport.yandex.ru/restoration\'>',
                        'RESTORE_URL_END': '</a>',
                    },
                    'restore.auto.passed_by_hint.change_hint': {
                        'CHANGE_HINT_URL_BEGIN': '<a href=\'https://passport.yandex.ru/passport?mode=changehint\'>',
                        'CHANGE_HINT_URL_END': '</a>',
                    },
                    'signature.secure': {},
                    'feedback': {
                        'FEEDBACK_URL_BEGIN': '<a href=\'https://feedback2.yandex.ru/\'>',
                        'FEEDBACK_URL_END': '</a>',
                    },
                },
            }
            if not is_secure_phone_bound:
                context['tanker_keys'].update({
                    'restore.auto.passed_by_hint.advice': {
                        'PROFILE_PHONES_URL_BEGIN': '<a href=\'https://passport.yandex.ru/profile/phones\'>',
                        'PROFILE_PHONES_URL_END': '</a>',
                        'HELP_PHONES_URL_BEGIN': '<a href=\'https://yandex.ru/support/passport/authorization/phone.html\'>',
                        'HELP_PHONES_URL_END': '</a>',
                    },
                })
            return context

        if '@' not in login:
            address = '%s@%s' % (TEST_DEFAULT_LOGIN, 'yandex.ru')
        else:
            address = login  # ПДД
        emails = [
            build_email(address=address, is_native=True),
        ]
        return emails

    def build_expected_email_restore_passed_email_context(self, login=TEST_DEFAULT_LOGIN, send_to_external=True,
                                                          is_secure_phone_bound=False, email=TEST_RESTORABLE_EMAIL):
        def build_email(address, is_native):
            context = {
                'language': 'ru',
                'addresses': [address],
                'subject': 'restore.auto.passed.subject',
                'tanker_keys': {
                    'greeting': {'FIRST_NAME': TEST_DEFAULT_FIRSTNAME},
                    'restore.auto.passed_by_email.restored': {
                        'LOGIN': login if is_native else masked_login(login),
                        'EMAIL': email if is_native else mask_email_for_challenge(email),
                    },
                    'restore.auto.passed.in_that_case': {},
                    'restore.auto.passed.restore_again': {
                        'RESTORE_URL_BEGIN': '<a href=\'https://passport.yandex.ru/restoration\'>',
                        'RESTORE_URL_END': '</a>',
                    },
                    'restore.auto.passed_by_email.check_emails': {
                        'EMAIL_VALIDATOR_URL_BEGIN': '<a href=\'https://passport.yandex.ru/profile/emails\'>',
                        'EMAIL_VALIDATOR_URL_END': '</a>',
                    },
                    'signature.secure': {},
                    'feedback': {
                        'FEEDBACK_URL_BEGIN': '<a href=\'https://feedback2.yandex.ru/\'>',
                        'FEEDBACK_URL_END': '</a>',
                    },
                },
            }
            if not is_secure_phone_bound:
                context['tanker_keys'].update({
                    'restore.auto.passed_by_email.advice': {
                        'PROFILE_PHONES_URL_BEGIN': '<a href=\'https://passport.yandex.ru/profile/phones\'>',
                        'PROFILE_PHONES_URL_END': '</a>',
                        'HELP_PHONES_URL_BEGIN': '<a href=\'https://yandex.ru/support/passport/authorization/phone.html\'>',
                        'HELP_PHONES_URL_END': '</a>',
                    },
                })
            return context

        emails = [
            build_email(address='%s@%s' % (TEST_DEFAULT_LOGIN, 'yandex.ru'), is_native=True),
        ]
        if send_to_external:
            emails.insert(0, build_email(address='%s@%s' % (TEST_DEFAULT_LOGIN, 'gmail.com'), is_native=False))
        return emails

    def build_expected_semi_auto_form_restore_passed_email_context(self, send_to_external=True, tld='ru'):
        def build_email(address):
            context = {
                'language': 'ru',
                'addresses': [address],
                'subject': 'restore.auto.passed.subject',
                'tanker_keys': {
                    'greeting': {'FIRST_NAME': TEST_DEFAULT_FIRSTNAME},
                    'restore.semi_auto_passed.congrats': {},
                    'restore.semi_auto_passed.settings_flushed': {
                        'profile_url': 'https://0.passportdev.yandex.%s/profile' % tld,
                        'profile_emails_url': 'https://0.passportdev.yandex.%s/profile/emails' % tld,
                    },
                    'restore.semi_auto_passed.app_passwords_flushed': {
                        'profile_access_url': 'https://0.passportdev.yandex.%s/profile/access' % tld,
                    },
                    'restore.semi_auto_passed.check_for_viruses': {
                        'CHECK_VIRUSES_DRWEB_URL': '<a href=\'http://www.freedrweb.com/cureit\'>http://www.freedrweb.com/cureit</a>',
                        'CHECK_VIRUSES_KASPERSKY_URL': '<a href=\'http://www.kaspersky.ru/antivirus-removal-tool\'>http://www.kaspersky.ru/antivirus-removal-tool</a>',
                    },
                    'restore.semi_auto_passed.check_personal_data': {
                        'profile_url': 'https://0.passportdev.yandex.%s/profile' % tld,
                    },
                    'restore.semi_auto_passed.check_journals': {
                        'mail_journal_url': 'https://mail.yandex.%s/neo2/#setup/journal' % tld,
                        'disk_journal_url': 'https://disk.yandex.%s/client/journal' % tld,
                    },
                    'restore.semi_auto_passed.security_reminder': {
                        'account_security_help_url': 'https://yandex.ru/support/passport/security.html',
                        'profile_journal_url': 'https://0.passportdev.yandex.%s/profile/journal' % tld,
                    },
                    'feedback': {
                        'FEEDBACK_URL_BEGIN': '<a href=\'https://feedback2.yandex.ru/\'>',
                        'FEEDBACK_URL_END': '</a>',
                    },
                },
            }
            return context

        emails = [
            build_email(address='%s@%s' % (TEST_DEFAULT_LOGIN, 'yandex.ru')),
        ]
        if send_to_external:
            emails.insert(0, build_email(address='%s@%s' % (TEST_DEFAULT_LOGIN, 'gmail.com')))
        return emails

    def assert_restore_passed_notifications_sent(self, method, send_to_external=True, **kwargs):
        if method == RESTORE_METHOD_PHONE:
            emails = self.build_expected_phone_restore_passed_email_context(send_to_external=send_to_external)
        elif method == RESTORE_METHOD_HINT:
            emails = self.build_expected_hint_restore_passed_email_context(**kwargs)
        elif method == RESTORE_METHOD_SEMI_AUTO_FORM:
            emails = self.build_expected_semi_auto_form_restore_passed_email_context(
                send_to_external=send_to_external,
                **kwargs
            )
        else:
            emails = self.build_expected_email_restore_passed_email_context(send_to_external=send_to_external, **kwargs)
        self.assert_emails_sent(emails)


COMMON_URL_SETTINGS = dict(
    BLACKBOX_URL='localhost',
    YASMS_URL='http://yasms',
    SOCIAL_API_URL='http://social/api/',
    RESTORE_DEFAULT_URL_TEMPLATE='https://0.passportdev.yandex.%(tld)s/restoration',
    PROFILE_URL_TEMPLATE='https://0.passportdev.yandex.%(tld)s/profile',
    PROFILE_EMAILS_URL_TEMPLATE='https://0.passportdev.yandex.%(tld)s/profile/emails',
    PROFILE_PHONES_URL_TEMPLATE='https://0.passportdev.yandex.%(tld)s/profile/phones',
    PROFILE_ACCESS_URL_TEMPLATE='https://0.passportdev.yandex.%(tld)s/profile/access',
    PROFILE_JOURNAL_URL_TEMPLATE='https://0.passportdev.yandex.%(tld)s/profile/journal',
    MAIL_JOURNAL_URL_TEMPLATE='https://mail.yandex.%(tld)s/neo2/#setup/journal',
    DISK_JOURNAL_URL_TEMPLATE='https://disk.yandex.%(tld)s/client/journal',
    PROFILE_CHANGE_HINT_URL_TEMPLATE='https://0.passportdev.yandex.%(tld)s/profile/change-hint',
)


@with_settings_hosts(
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=1,
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    YASMS_MARK_OPERATION_TTL=TEST_OPERATION_TTL.total_seconds(),
    RESTORE_TO_FORCED_LITE_COMPLETION_ENABLED=True,
    BIND_RELATED_PHONISH_ACCOUNT_APP_IDS={TEST_APP_ID},
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'login_method_change', 'restore'},
    ACCOUNT_MODIFICATION_MAIL_ENABLE={'login_method_change'},
    ACCOUNT_MODIFICATION_NOTIFY_DENOMINATOR=1,
    **merge_dicts(mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:login_method_change': 5,
            'email:login_method_change': 5,
            'push:restore': 5,
        },
    ), COMMON_URL_SETTINGS)
)
class RestoreCommitTestCase(
    RestoreCommitTestCaseBase,
    CommonTestsMixin,
    AccountValidityTestsMixin,
):

    def setUp(self):
        super(RestoreCommitTestCase, self).setUp()

        self._phone_id_generator = PhoneIdGeneratorFaker()
        self._phone_id_generator.set_list([TEST_PHONE_ID3])
        self._phone_id_generator.start()
        self.start_account_modification_notify_mocks(
            ip=TEST_IP,
        )
        self.setup_kolmogor()

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        self._phone_id_generator.stop()
        del self._phone_id_generator
        super(RestoreCommitTestCase, self).tearDown()

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
                str(rate),
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK', 'OK', 'OK'])

    def check_db(self, uid=TEST_DEFAULT_UID, pdd=False, sharddb_query_count=2, centraldb_query_count=0,
                 question=None, answer=None, is_secure_phone_bound=False, new_phone_id=TEST_PHONE_ID,
                 phone_action_date=TEST_PHONE_ACTION_DEFAULT_DATE, is_secure_phone_being_removed=False,
                 is_secure_phone_replaced_with_quarantine=False, is_secure_phone_updated=False,
                 is_secure_phone_being_aliasified=False, is_glogouted=True):
        timenow = TimeNow()
        db = 'passportdbshard2' if pdd else 'passportdbshard1'

        eq_(self.env.db.query_count('passportdbcentral'), centraldb_query_count)
        eq_(self.env.db.query_count(db), sharddb_query_count)

        self.env.db.check_missing('attributes', 'account.is_disabled', uid=uid, db=db)
        self.env.db.check('attributes', 'password.update_datetime', timenow, uid=uid, db=db)
        self.env.db.check('attributes', 'password.quality', '3:%d' % TEST_PASSWORD_QUALITY, uid=uid, db=db)
        if is_glogouted:
            self.env.db.check('attributes', 'account.global_logout_datetime', timenow, uid=uid, db=db)
        else:
            self.env.db.check_missing('attributes', 'account.global_logout_datetime', uid=uid, db=db)
        if question:
            self.env.db.check('attributes', 'hint.question.serialized', question.encode('utf-8'), uid=uid, db=db)
            self.env.db.check('attributes', 'hint.answer.encrypted', answer.encode('utf-8'), uid=uid, db=db)
        else:
            self.env.db.check_missing('attributes', 'hint.question.serialized', uid=uid, db=db)
            self.env.db.check_missing('attributes', 'hint.answer.encrypted', uid=uid, db=db)
        self.env.db.check('attributes', 'person.firstname', TEST_DEFAULT_FIRSTNAME.encode('utf-8'), uid=uid, db=db)
        self.env.db.check('attributes', 'person.lastname', TEST_DEFAULT_LASTNAME.encode('utf-8'), uid=uid, db=db)
        self.env.db.check('attributes', 'person.birthday', TEST_DEFAULT_BIRTHDAY, uid=uid, db=db)
        self.env.db.check('attributes', 'person.gender', 'm', uid=uid, db=db)

        self.env.db.check_missing('attributes', 'password.forced_changing_reason', uid=uid, db=db)
        self.env.db.check_missing('attributes', 'password.is_creating_required', uid=uid, db=db)
        self.env.db.check_missing('attributes', 'password.pwn_forced_changing_suspended_at', uid=uid, db=db)

        self.env.db.check_missing('attributes', 'account.totp.secret', uid=uid, db=db)
        self.env.db.check_missing('attributes', 'account.totp.check_time', uid=uid, db=db)

        self.env.db.check_missing('attributes', 'account.sms_2fa_on', uid=uid, db=db)

        self.env.db.check_missing('attributes', 'account.deletion_operation_started_at', db=db, uid=uid)

        self.check_pin_check_counter(0, db=db)

        if is_secure_phone_bound or is_secure_phone_updated:
            assert_secure_phone_bound.check_db(
                self.env.db,
                uid=uid,
                phone_attributes={
                    'id': new_phone_id,
                    'number': TEST_PHONE,
                    'created': phone_action_date,
                    'bound': phone_action_date,
                    'confirmed': phone_action_date if is_secure_phone_bound else DatetimeNow(),
                    'secured': phone_action_date,
                },
            )
        elif is_secure_phone_being_removed:
            assert_secure_phone_being_removed.check_db(
                self.env.db,
                uid=uid,
                phone_attributes={
                    'id': TEST_PHONE_ID,
                    'number': TEST_PHONE,
                    'created': phone_action_date,
                    'bound': phone_action_date,
                    'confirmed': phone_action_date,
                    'secured': phone_action_date,
                },
            )
            assert_simple_phone_bound.check_db(
                db_faker=self.env.db,
                uid=TEST_DEFAULT_UID,
                phone_attributes={
                    'id': TEST_PHONE_ID3,
                    'number': TEST_PHONE2_OBJECT.e164,
                },
            )
        elif is_secure_phone_replaced_with_quarantine:
            assert_secure_phone_being_replaced.check_db(
                db_faker=self.env.db,
                uid=TEST_DEFAULT_UID,
                phone_attributes={
                    'id': TEST_PHONE_ID,
                    'number': TEST_PHONE_OBJECT.e164,
                },
                operation_attributes={
                    'password_verified': DatetimeNow(),
                    'code_confirmed': None,
                    'finished': DatetimeNow() + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
                },
            )
            assert_simple_phone_replace_secure.check_db(
                db_faker=self.env.db,
                uid=TEST_DEFAULT_UID,
                phone_attributes={
                    'id': TEST_PHONE_ID3,
                    'number': TEST_PHONE2_OBJECT.e164,
                },
                operation_attributes={
                    'password_verified': DatetimeNow(),
                    'code_confirmed': DatetimeNow(),
                    'finished': DatetimeNow() + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
                },
            )
        elif is_secure_phone_being_aliasified:
            assert_secure_phone_being_aliasified.check_db(
                self.env.db,
                uid=uid,
                phone_attributes={
                    'id': new_phone_id,
                    'number': TEST_PHONE,
                    'created': phone_action_date,
                    'bound': phone_action_date,
                    'confirmed': phone_action_date,
                    'secured': phone_action_date,
                },
            )
        else:
            assert_no_secure_phone(self.env.db, uid)

        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=uid, db=db)
        if self.is_password_hash_from_blackbox:
            eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)
        else:
            eq_(len(eav_pass_hash), 36)
            ok_(eav_pass_hash.startswith('1:'))

    def check_event_log(self, method=RESTORE_METHOD_PHONE, uid=TEST_DEFAULT_UID, pdd=False, is_2fa_restore=False,
                        flushed_entities=None, are_phones_flushed=False, new_question=None, new_answer=None,
                        account_was_disabled=False, old_phone_object=TEST_PHONE_OBJECT, is_old_phone_secure=True,
                        had_old_phone=True, new_phone=None, is_conflicted_operation_exists=False,
                        is_secure_phone_replaced_with_quarantine=False, is_secure_phone_updated=False,
                        support_link_type=None, is_phone_removal_operation_cancelled=False,
                        is_phone_replacement_by_being_bound_operation_cancelled=False,
                        is_phone_replacement_by_simple_operation_cancelled=False, is_glogouted=True,
                        was_password_change_required=False, had_sms_2fa=False,
                        had_pwn_forced_changing_suspension=False, was_old_phone_just_unsecured=False,
                        was_child_returned_to_family=False):
        db = 'passportdbshard%s' % (2 if pdd else 1)
        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=uid, db=db)
        expected_log_entries = []

        if was_child_returned_to_family:
            expected_log_entries += [
                {'name': 'family.%s.family_member' % TEST_FAMILY_ID, 'value': str(uid)},
                {'name': 'action', 'value': 'family_restore_child'},
                {'name': 'consumer', 'value': 'dev'},
                {'name': 'user_agent', 'value': 'curl'},
            ]

        parsed_events = self.env.event_logger.parse_events()
        replace_secure_phone_event = None
        flush_event = None
        if not flushed_entities:
            eq_(len(parsed_events), 1)
            restore_event = parsed_events[0]
        elif is_secure_phone_replaced_with_quarantine:
            eq_(len(parsed_events), 3)
            restore_event, replace_secure_phone_event, flush_event = parsed_events
        else:
            eq_(len(parsed_events), 2)
            restore_event, flush_event = parsed_events

        eq_(restore_event.event_type, 'restore')
        if flush_event:
            eq_(flush_event.event_type, 'restore_entities_flushed')
        if replace_secure_phone_event:
            eq_(replace_secure_phone_event.event_type, 'secure_phone_replace')

        expected_restore_actions = []
        expected_phone_actions = []
        expected_flush_actions = []

        if flushed_entities:
            if 'phones' in flushed_entities:
                # 2ФА и смс-2ФА сбрасываются отдельно от смены пароля, если делаем сброс телефонов
                if is_2fa_restore:
                    expected_log_entries += [
                        {'name': 'info.totp', 'value': 'disabled'},
                        {'name': 'info.totp_update_time', 'value': '-'},
                    ]
                    expected_flush_actions.append({'type': 'totp_disabled'})
                if had_sms_2fa:
                    expected_log_entries += [
                        {'name': 'info.sms_2fa_on', 'value': '0'},
                    ]
            if 'hint' in flushed_entities:
                expected_log_entries += [
                    {'name': 'info.hintq', 'value': '-'},
                    {'name': 'info.hinta', 'value': '-'},
                ]
                expected_flush_actions.append({'type': 'questions_remove'})
            if 'phones' in flushed_entities:
                if had_old_phone:
                    if is_old_phone_secure:
                        if was_old_phone_just_unsecured:
                            expected_log_entries += [
                                {'name': 'phone.1.action', 'value': 'changed'},
                                {'name': 'phone.1.number', 'value': old_phone_object.e164},
                                {'name': 'phone.1.secured', 'value': '0'},
                                {'name': 'phones.secure', 'value': '0'},
                            ]
                        else:
                            expected_log_entries += [
                                {'name': 'phone.1.action', 'value': 'deleted'},
                                {'name': 'phone.1.number', 'value': old_phone_object.e164},
                                {'name': 'phones.secure', 'value': '0'},
                            ]
                        expected_flush_actions.append({
                            'type': 'secure_phone_unset',
                            'phone_unset': mask_phone_number(old_phone_object.international),
                        })
                    else:
                        expected_log_entries += [
                            {'name': 'phone.1.action', 'value': 'deleted'},
                            {'name': 'phone.1.number', 'value': old_phone_object.e164},
                        ]
            expected_log_entries += [
                {'name': 'action', 'value': 'restore_entities_flushed'},
                {'name': 'info.flushed_entities', 'value': ','.join(sorted(flushed_entities))},
                {'name': 'consumer', 'value': 'dev'},
                {'name': 'user_agent', 'value': 'curl'},
            ]
            if 'emails' in flushed_entities:
                expected_flush_actions.append({'type': 'email_remove_all'})
        if new_phone:
            expected_log_entries += [
                {'name': 'phone.1.action', 'value': 'created'},
                {'name': 'phone.1.created', 'value': TimeNow()},
                {'name': 'phone.1.number', 'value': TEST_PHONE},
                {'name': 'phone.1.operation.1.action', 'value': 'created'},
                {'name': 'phone.1.operation.1.finished', 'value': TimeNow(offset=TEST_OPERATION_TTL.total_seconds())},
                {'name': 'phone.1.operation.1.security_identity', 'value': '1'},
                {'name': 'phone.1.operation.1.started', 'value': TimeNow()},
                {'name': 'phone.1.operation.1.type', 'value': 'bind'},

                {'name': 'action', 'value': 'acquire_phone'},
                {'name': 'consumer', 'value': 'dev'},
                {'name': 'user_agent', 'value': 'curl'},
            ]
        elif is_conflicted_operation_exists:
            expected_log_entries += [
                {'name': 'phone.3.action', 'value': 'created'},
                {'name': 'phone.3.created', 'value': TimeNow()},
                {'name': 'phone.3.number', 'value': TEST_PHONE2},
                {'name': 'phone.3.operation.2.action', 'value': 'created'},
                {'name': 'phone.3.operation.2.finished', 'value': TimeNow(offset=TEST_OPERATION_TTL.total_seconds())},
                {'name': 'phone.3.operation.2.security_identity', 'value': TEST_PHONE2_OBJECT.digital},
                {'name': 'phone.3.operation.2.started', 'value': TimeNow()},
                {'name': 'phone.3.operation.2.type', 'value': 'bind'},
                {'name': 'action', 'value': 'acquire_phone'},
                {'name': 'consumer', 'value': 'dev'},
                {'name': 'user_agent', 'value': 'curl'},
            ]
        elif is_secure_phone_replaced_with_quarantine:
            expected_log_entries += [
                {'name': 'phone.1.number', 'value': TEST_PHONE},
                {'name': 'phone.1.operation.1.action', 'value': 'created'},
                {'name': 'phone.1.operation.1.finished', 'value': TimeNow(offset=TEST_OPERATION_TTL.total_seconds())},
                {'name': 'phone.1.operation.1.phone_id2', 'value': str(TEST_PHONE_ID3)},
                {'name': 'phone.1.operation.1.security_identity', 'value': '1'},
                {'name': 'phone.1.operation.1.started', 'value': TimeNow()},
                {'name': 'phone.1.operation.1.type', 'value': 'replace'},
                {'name': 'phone.3.action', 'value': 'created'},
                {'name': 'phone.3.created', 'value': TimeNow()},
                {'name': 'phone.3.number', 'value': TEST_PHONE2},
                {'name': 'phone.3.operation.2.action', 'value': 'created'},
                {'name': 'phone.3.operation.2.finished', 'value': TimeNow(offset=TEST_OPERATION_TTL.total_seconds())},
                {'name': 'phone.3.operation.2.phone_id2', 'value': str(TEST_PHONE_ID)},
                {'name': 'phone.3.operation.2.security_identity', 'value': TEST_PHONE2_OBJECT.digital},
                {'name': 'phone.3.operation.2.started', 'value': TimeNow()},
                {'name': 'phone.3.operation.2.type', 'value': 'bind'},
                {'name': 'action', 'value': 'phone_secure_replace_submit'},
                {'name': 'consumer', 'value': 'dev'},
                {'name': 'user_agent', 'value': 'curl'},
            ]

        if account_was_disabled:
            expected_log_entries += [
                {'name': 'info.ena', 'value': '1'},
                {'name': 'info.disabled_status', 'value': '0'},
            ]
        if is_glogouted:
            expected_log_entries.append({'name': 'info.glogout', 'value': TimeNow()})
            expected_restore_actions.append({'type': 'global_logout'})
        if was_child_returned_to_family:
            expected_log_entries.append({'name': 'account.last_child_family', 'value': '-'})
        expected_log_entries += [
            {'name': 'info.password', 'value': eav_pass_hash},
            {'name': 'info.password_quality', 'value': str(TEST_PASSWORD_QUALITY)},
            {'name': 'info.password_update_time', 'value': TimeNow()},
        ]
        if had_pwn_forced_changing_suspension:
            expected_log_entries.append({'name': 'info.password_pwn_forced_changing_suspension_time', 'value': '-'})
        if was_password_change_required:
            expected_log_entries.append({'name': 'sid.login_rule', 'value': '8|1'})
        expected_restore_actions.append({'type': 'password_change'})
        if is_2fa_restore and (not flushed_entities or 'phones' not in flushed_entities):
            expected_log_entries += [
                {'name': 'info.totp', 'value': 'disabled'},
                {'name': 'info.totp_update_time', 'value': '-'},
            ]
            expected_restore_actions.append({'type': 'totp_disabled'})
        if new_question:
            expected_log_entries += [
                {'name': 'info.hintq', 'value': new_question.encode('utf-8')},
                {'name': 'info.hinta', 'value': new_answer.encode('utf-8')},
            ]
            expected_restore_actions.append({'type': 'questions_change'})
        if new_phone or is_secure_phone_replaced_with_quarantine or is_conflicted_operation_exists or support_link_type:
            new_karma = '2000' if support_link_type else '6000'
            expected_log_entries += [
                {'name': 'info.karma_prefix', 'value': new_karma[0]},  # Обеление
                {'name': 'info.karma_full', 'value': new_karma},
            ]
        if new_phone:
            expected_log_entries += [
                {'name': 'phone.1.action', 'value': 'changed'},
                {'name': 'phone.1.bound', 'value': TimeNow()},
                {'name': 'phone.1.confirmed', 'value': TimeNow()},
                {'name': 'phone.1.number', 'value': TEST_PHONE_OBJECT.e164},
                {'name': 'phone.1.operation.1.action', 'value': 'deleted'},
                {'name': 'phone.1.operation.1.security_identity', 'value': '1'},
                {'name': 'phone.1.operation.1.type', 'value': 'bind'},
                {'name': 'phone.1.secured', 'value': TimeNow()},
                {'name': 'phones.secure', 'value': '1'},
            ]
            expected_restore_actions.append({
                'type': 'secure_phone_set',
                'phone_set': mask_phone_number(TEST_PHONE_OBJECT.international),
            })
        elif is_secure_phone_updated:
            expected_log_entries += [
                {'name': 'phone.1.action', 'value': 'changed'},
                {'name': 'phone.1.confirmed', 'value': TimeNow()},
                {'name': 'phone.1.number', 'value': TEST_PHONE_OBJECT.e164},
            ]
        elif is_conflicted_operation_exists:
            expected_log_entries += [
                {'name': 'phone.3.action', 'value': 'changed'},
                {'name': 'phone.3.bound', 'value': TimeNow()},
                {'name': 'phone.3.confirmed', 'value': TimeNow()},
                {'name': 'phone.3.number', 'value': TEST_PHONE2_OBJECT.e164},
                {'name': 'phone.3.operation.2.action', 'value': 'deleted'},
                {'name': 'phone.3.operation.2.security_identity', 'value': TEST_PHONE2_OBJECT.digital},
                {'name': 'phone.3.operation.2.type', 'value': 'bind'},
            ]
            expected_restore_actions.append({
                'type': 'phone_bind',
                'phone_bind': mask_phone_number(TEST_PHONE2_OBJECT.international),
            })
        elif is_secure_phone_replaced_with_quarantine:
            expected_log_entries += [
                {'name': 'phone.1.number', 'value': TEST_PHONE},
                {'name': 'phone.1.operation.1.action', 'value': 'changed'},
                {'name': 'phone.1.operation.1.finished', 'value': TimeNow(offset=TEST_OPERATION_TTL.total_seconds())},
                {'name': 'phone.1.operation.1.password_verified', 'value': TimeNow()},
                {'name': 'phone.1.operation.1.security_identity', 'value': '1'},
                {'name': 'phone.1.operation.1.type', 'value': 'replace'},
                {'name': 'phone.3.action', 'value': 'changed'},
                {'name': 'phone.3.bound', 'value': TimeNow()},
                {'name': 'phone.3.confirmed', 'value': TimeNow()},
                {'name': 'phone.3.number', 'value': TEST_PHONE2},
                {'name': 'phone.3.operation.2.action', 'value': 'deleted'},
                {'name': 'phone.3.operation.2.security_identity', 'value': TEST_PHONE2_OBJECT.digital},
                {'name': 'phone.3.operation.2.type', 'value': 'bind'},
                {'name': 'phone.3.operation.3.action', 'value': 'created'},
                {'name': 'phone.3.operation.3.code_confirmed', 'value': TimeNow()},
                {'name': 'phone.3.operation.3.finished', 'value': TimeNow(offset=TEST_OPERATION_TTL.total_seconds())},
                {'name': 'phone.3.operation.3.password_verified', 'value': TimeNow()},
                {'name': 'phone.3.operation.3.phone_id2', 'value': str(TEST_PHONE_ID)},
                {'name': 'phone.3.operation.3.security_identity', 'value': TEST_PHONE2_OBJECT.digital},
                {'name': 'phone.3.operation.3.started', 'value': TimeNow()},
                {'name': 'phone.3.operation.3.type', 'value': 'mark'},
            ]
            expected_restore_actions.append({
                'type': 'secure_phone_replace',
                'phone_set': mask_phone_number(TEST_PHONE2_OBJECT.international),
                'phone_unset': mask_phone_number(TEST_PHONE_OBJECT.international),
                'delayed_until': TimeNow(offset=TEST_OPERATION_TTL.total_seconds()),
            })
            expected_phone_actions.append({
                'type': 'secure_phone_replace',
                'phone_set': mask_phone_number(TEST_PHONE2_OBJECT.international),
                'phone_unset': mask_phone_number(TEST_PHONE_OBJECT.international),
                'delayed_until': TimeNow(offset=TEST_OPERATION_TTL.total_seconds()),
            })
        if is_phone_removal_operation_cancelled:
            expected_log_entries += [
                {'name': 'phone.1.number', 'value': TEST_PHONE},
                {'name': 'phone.1.operation.1.action', 'value': 'deleted'},
                {'name': 'phone.1.operation.1.security_identity', 'value': '1'},
                {'name': 'phone.1.operation.1.type', 'value': 'remove'},
            ]
        elif is_phone_replacement_by_being_bound_operation_cancelled:
            expected_log_entries += [
                {'name': 'phone.1.number', 'value': TEST_PHONE},
                {'name': 'phone.1.operation.1.action', 'value': 'deleted'},
                {'name': 'phone.1.operation.1.security_identity', 'value': '1'},
                {'name': 'phone.1.operation.1.type', 'value': 'replace'},
                {'name': 'phone.2.action', 'value': 'deleted'},
                {'name': 'phone.2.number', 'value': TEST_PHONE2},
                {'name': 'phone.2.operation.2.action', 'value': 'deleted'},
                {'name': 'phone.2.operation.2.security_identity', 'value': TEST_PHONE2_OBJECT.digital},
                {'name': 'phone.2.operation.2.type', 'value': 'bind'},
            ]
        elif is_phone_replacement_by_simple_operation_cancelled:
            expected_log_entries += [
                {'name': 'phone.1.number', 'value': TEST_PHONE},
                {'name': 'phone.1.operation.1.action', 'value': 'deleted'},
                {'name': 'phone.1.operation.1.security_identity', 'value': '1'},
                {'name': 'phone.1.operation.1.type', 'value': 'replace'},
                {'name': 'phone.2.number', 'value': TEST_PHONE2},
                {'name': 'phone.2.operation.2.action', 'value': 'deleted'},
                {'name': 'phone.2.operation.2.security_identity', 'value': TEST_PHONE2_OBJECT.digital},
                {'name': 'phone.2.operation.2.type', 'value': 'mark'},
            ]
        expected_log_entries.append({'name': 'action', 'value': 'restore_passed_by_%s' % method})
        if method in PHONE_BASED_RESTORE_METHODS:
            expected_log_entries.append({'name': 'info.used_phone', 'value': TEST_PHONE})

        expected_log_entries += [
            {'name': 'consumer', 'value': 'dev'},
            {'name': 'user_agent', 'value': 'curl'},
        ]

        if method in PHONE_BASED_RESTORE_METHODS:
            expected_restore_actions.append({
                'type': 'restore',
                'restore_by': method,
                'phone': mask_phone_number(TEST_PHONE_OBJECT.international),
            })
        elif method == RESTORE_METHOD_EMAIL:
            expected_log_entries.append({'name': 'info.used_email', 'value': TEST_DEFAULT_LOGIN + '@gmail.com'})
            expected_restore_actions.append({
                'type': 'restore',
                'restore_by': method,
                'email': mask_email_for_challenge(TEST_DEFAULT_LOGIN + '@gmail.com'),
            })
        elif method == RESTORE_METHOD_HINT:
            expected_log_entries.append({'name': 'info.used_question', 'value': TEST_DEFAULT_HINT_QUESTION})
            expected_restore_actions.append({
                'type': 'restore',
                'restore_by': method,
            })
        else:
            expected_restore_actions.append({
                'type': 'restore',
                'restore_by': method,
            })

        if support_link_type:
            expected_log_entries.append({'name': 'info.support_link_type', 'value': support_link_type})

        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            expected_log_entries,
        )

        if flush_event and expected_flush_actions:
            eq_(
                sorted(expected_flush_actions, key=lambda d: d['type']),
                sorted(flush_event.actions, key=lambda d: d['type']),
            )
        elif expected_flush_actions:  # pragma: no cover
            ok_(False, 'Expected flush event but it\'s not present.')
        elif flush_event:  # pragma: no cover
            ok_(False, 'Got unexpected flush event.')

        if restore_event and expected_restore_actions:
            eq_(
                sorted(expected_restore_actions, key=lambda d: d['type']),
                sorted(restore_event.actions, key=lambda d: d['type']),
            )
        elif expected_restore_actions:  # pragma: no cover
            ok_(False, 'Expected restore event but it\'s not present.')
        elif restore_event:  # pragma: no cover
            ok_(False, 'Got unexpected restore event.')

    def get_expected_statbox_entries(self, uid=TEST_DEFAULT_UID, login=TEST_DEFAULT_LOGIN,
                                     is_2fa_restore=False, current_restore_method=RESTORE_METHOD_PHONE,
                                     suitable_restore_methods=None, is_hint_masked=None, flushed_entities=None,
                                     support_link_type=None, new_method=None,
                                     allowed_methods_to_bind=None, is_new_method_required=False,
                                     new_phone_status=None, had_no_password=False,
                                     had_secure_phone=True, retpath=None, host=TEST_HOST,
                                     is_phone_removal_operation_cancelled=False,
                                     is_phone_replacement_by_being_bound_operation_cancelled=False,
                                     is_phone_replacement_by_simple_operation_cancelled=False,
                                     operation_type=None, restored_from_deletion=False, account_was_disabled=False,
                                     is_glogouted=True, was_password_change_required=False, had_sms_2fa=False,
                                     old_karma=None, had_pwn_forced_changing_suspension=False,
                                     was_child_returned_to_family=False):
        entries = []

        if was_child_returned_to_family:
            entries += [
                self.env.statbox.entry(
                    'family_info_modification',
                    consumer='dev',
                    event='family_info_modification',
                    ip=TEST_IP,
                    user_agent='curl',
                    family_id=TEST_FAMILY_ID,
                    entity='members',
                    entity_id=str(uid),
                    old='-',
                    attribute='members.%s.uid' % uid,
                    new=str(uid),
                    operation='created',
                ),
            ]

        if flushed_entities and 'phones' in flushed_entities and had_secure_phone:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    entity='phones.secure',
                    operation='deleted',
                    old=TEST_PHONE_MASKED_FOR_STATBOX,
                    old_entity_id=str(TEST_PHONE_ID),
                    new='-',
                    new_entity_id='-',
                ),
            ]

        extra_context = dict(
            current_restore_method=current_restore_method,
            suitable_restore_methods=','.join(suitable_restore_methods),
            selected_methods_order=current_restore_method,
            uid=str(uid),
            login=login,
            allowed_methods_to_bind=','.join(allowed_methods_to_bind or []),
            is_new_method_required=tskv_bool(is_new_method_required),
            host=host,
        )
        if retpath:
            extra_context['retpath'] = retpath
        if is_hint_masked:
            extra_context['is_hint_masked'] = tskv_bool(is_hint_masked)
        if support_link_type:
            extra_context['support_link_type'] = support_link_type
        if new_method:
            extra_context['new_method'] = new_method
        if had_no_password:
            extra_context['is_password_missing'] = '1'
        if restored_from_deletion:
            extra_context['restored_from_deletion'] = '1'
        if new_phone_status:
            if new_phone_status['is_replaced_phone_with_quarantine']:
                entries += [
                    self.env.statbox.entry(
                        'phone_operation_created',
                        operation_type='replace_secure_phone_with_nonbound_phone',
                        being_bound_number=TEST_PHONE_MASKED_FOR_STATBOX,
                        being_bound_phone_id=str(TEST_PHONE_ID3),
                        secure_number=TEST_PHONE_MASKED_FOR_STATBOX,
                        secure_phone_id=str(TEST_PHONE_ID),
                        uid=str(uid),
                        _exclude=['number', 'phone_id'],
                    ),
                    self.env.statbox.entry(
                        'sms_notification_sent',
                        **extra_context
                    ),
                ]
            if new_method == RESTORE_METHOD_PHONE:
                if new_phone_status['is_conflicted_operation_exists'] or new_phone_status['is_bound_new_secure_phone']:
                    extra_phone_args = {}
                    bind_type = 'secure_bind'
                    if new_phone_status['is_conflicted_operation_exists']:
                        bind_type = 'simple_bind'
                        extra_phone_args.update(
                            operation_id=str(TEST_OPERATION_ID2),
                            phone_id=str(TEST_PHONE_ID3),
                        )
                    entries += [
                        self.env.statbox.entry(
                            'phone_operation_created',
                            operation_type=bind_type,
                            uid=str(uid),
                            **extra_phone_args
                        ),
                    ]
            for key, value in new_phone_status.items():
                if key == 'secure_phone_pending_until':
                    continue
                extra_context[key] = tskv_bool(value)

        if (is_phone_removal_operation_cancelled or
                is_phone_replacement_by_being_bound_operation_cancelled or
                is_phone_replacement_by_simple_operation_cancelled):
            entries += [
                self.env.statbox.entry(
                    'phone_operation_cancelled',
                    operation_type=operation_type,
                    **extra_context
                ),
            ]

        if had_sms_2fa:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    entity='account.sms_2fa_on',
                    operation='updated',
                    new='0',
                    old='1',
                    uid=str(uid),
                ),
            ]

        if is_glogouted:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    entity='account.global_logout_datetime',
                    operation='updated',
                    new=DatetimeNow(convert_to_datetime=True),
                    old=TEST_GLOBAL_LOGOUT_DATETIME,
                    uid=str(uid),
                ),
            ]
        if account_was_disabled:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    entity='account.disabled_status',
                    operation='updated',
                    new='enabled',
                    old='disabled_on_deletion' if restored_from_deletion else 'disabled',
                    uid=str(uid),
                ),
            ]

        if was_child_returned_to_family:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    entity='account.last_child_family',
                    operation='deleted',
                    new='-',
                    old=TEST_FAMILY_ID,
                    uid=str(uid),
                ),
            ]

        if new_method == RESTORE_METHOD_PHONE and new_phone_status['is_bound_new_secure_phone']:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    entity='phones.secure',
                    operation='created',
                    old='-',
                    old_entity_id='-',
                    new=TEST_PHONE_MASKED_FOR_STATBOX,
                    new_entity_id=str(TEST_PHONE_ID),
                ),
            ]

        entries += [
            self.env.statbox.entry(
                'account_modification',
                entity='password.encrypted',
                operation='created' if (is_2fa_restore or had_no_password) else 'updated',
                uid=str(uid),
            ),
        ]
        if had_no_password or is_2fa_restore:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    entity='password.encoding_version',
                    operation='created',
                    uid=str(uid),
                    old='-',
                    new=str(self.password_hash_version),
                ),
            ]
        elif self.password_hash_version == PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    entity='password.encoding_version',
                    operation='updated',
                    uid=str(uid),
                    old=str(PASSWORD_ENCODING_VERSION_MD5_CRYPT),
                    new=str(PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON),
                ),
            ]

        entries += [
            self.env.statbox.entry(
                'account_modification',
                entity='password.quality',
                operation='created' if (is_2fa_restore or had_no_password) else 'updated',
                new=str(TEST_PASSWORD_QUALITY),
                old=str(TEST_PASSWORD_QUALITY_OLD) if not (is_2fa_restore or had_no_password) else '-',
                uid=str(uid),
            ),
        ]
        if was_password_change_required:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    entity='password.is_changing_required',
                    operation='deleted',
                    new='-',
                    old='1',
                    uid=str(uid),
                ),
            ]
        if had_pwn_forced_changing_suspension:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    entity='password.pwn_forced_changing_suspended_at',
                    operation='deleted',
                    new='-',
                    old=DatetimeNow(convert_to_datetime=True),
                    uid=str(uid),
                ),
            ]
        if new_method == RESTORE_METHOD_HINT:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    entity='hint.question',
                    operation='created',
                    uid=str(uid),
                ),
                self.env.statbox.entry(
                    'account_modification',
                    entity='hint.answer',
                    operation='created',
                    uid=str(uid),
                ),
            ]
        if (new_method == RESTORE_METHOD_PHONE and not new_phone_status['is_updated_current_secure_phone']) or support_link_type:
            entries.append(self.env.statbox.entry(
                'account_modification',
                login=login,
                action='restore_passed_by_%s' % current_restore_method,
                entity='karma',
                destination='frodo',
                uid=str(uid),
                old=old_karma or '0',
                new='2000' if support_link_type else '6000',
                suid='-',
                registration_datetime=TEST_DEFAULT_REGISTRATION_DATETIME,
                _exclude=['operation'],
            ))

        if new_method == RESTORE_METHOD_PHONE:
            if new_phone_status['is_replaced_phone_with_quarantine']:
                entries += [
                    self.env.statbox.entry(
                        'phone_confirmed',
                        code_checks_count='0',
                        confirmation_time=DatetimeNow(convert_to_datetime=True),
                        phone_id=str(TEST_PHONE_ID3),
                        **extra_context
                    ),
                    self.env.statbox.entry(
                        'simple_phone_bound',
                        operation_id=str(TEST_OPERATION_ID1),
                        phone_id=str(TEST_PHONE_ID3),
                        **extra_context
                    ),
                ]
            elif new_phone_status['is_conflicted_operation_exists'] or new_phone_status['is_bound_new_secure_phone']:
                extra_phone_args = {}
                bound_action = 'secure_phone_bound'
                if new_phone_status['is_conflicted_operation_exists']:
                    bound_action = 'simple_phone_bound'
                    extra_phone_args.update(
                        operation_id=str(TEST_OPERATION_ID2),
                        phone_id=str(TEST_PHONE_ID3),
                    )
                entries += [
                    self.env.statbox.entry(
                        'phone_confirmed',
                        code_checks_count='0',
                        confirmation_time=DatetimeNow(convert_to_datetime=True),
                        **merge_dicts(extra_context, extra_phone_args)
                    ),
                    self.env.statbox.entry(
                        bound_action,
                        **merge_dicts(extra_context, extra_phone_args)
                    ),
                ]

        entries.append(self.env.statbox.entry('passed', **extra_context))
        return entries

    def assert_social_binding_log_written(self):
        self.env.social_binding_logger.assert_has_written([
            self.env.social_binding_logger.entry(
                'bind_phonish_account_by_track',
                uid=str(TEST_DEFAULT_UID),
                track_id=self.track_id,
                ip=TEST_IP,
            ),
        ])

    def assert_social_binding_log_empty(self):
        self.env.social_binding_logger.assert_has_written([])

    def assert_external_api_called_for_flushing(self):
        eq_(len(self.env.social_api.requests), 1)
        social_api_request = self.env.social_api.requests[0]
        social_api_request.assert_properties_equal(
            method='DELETE',
            url='http://social/api/user/1?consumer=passport',
        )

    def test_incorrect_method_in_track_fails(self):
        """В треке указан неизвестный способ восстановления"""
        self.track_invalid_state_case(current_restore_method='not_a_method')

    def test_new_method_phone_with_phone_not_confirmed_in_track_fails(self):
        """Необходима привязка нового средства восстановления, выбран телефон но в треке нет признака подтверждения"""
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_LINK,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            phone_confirmation_phone_number=TEST_PHONE,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(self.query_params(new_method=RESTORE_METHOD_PHONE), headers=self.get_headers())

        self.assert_error_response(resp, ['track.invalid_state'], **self.base_expected_response())
        self.assert_track_unchanged()

    def test_new_method_phone_with_no_phone_in_track_fails(self):
        """Необходима привязка нового средства восстановления, выбран телефон но значение не задано в треке"""
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_LINK,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            phone_confirmation_is_confirmed=True,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(self.query_params(new_method=RESTORE_METHOD_PHONE), headers=self.get_headers())

        self.assert_error_response(resp, ['track.invalid_state'], **self.base_expected_response())
        self.assert_track_unchanged()

    def test_new_method_phone_number_is_compromised(self):
        """Использованный номер телефона нельзя привязать как защищенный"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_HINT,
            phone_confirmation_is_confirmed=True,
            phone_confirmation_phone_number=TEST_PHONE,
        )
        counter = get_per_phone_number_buckets()
        for _ in range(counter.limit):
            counter.incr(TEST_PHONE)
        eq_(counter.get(TEST_PHONE), counter.limit)

        resp = self.make_request(
            self.query_params(
                password=TEST_PASSWORD_2,
                new_method=RESTORE_METHOD_PHONE,
            ),
            headers=self.get_headers(),
        )

        self.assert_error_response(resp, ['phone.compromised'], **self.base_expected_response())
        self.assert_track_unchanged()
        eq_(counter.get(TEST_PHONE), counter.limit)  # счетчик не увеличивается
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='phone.compromised',
                current_restore_method=RESTORE_METHOD_HINT,
                suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
            ),
        ])

    def test_not_suitable_method_in_track_fails(self):
        """В треке указан способ восстановления, недоступный для аккаунта"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(resp, ['method.not_allowed'], **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='method.not_allowed',
                suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
            ),
        ])

    def test_password_like_login_validation_fails(self):
        """Пароль совпадает с логином - ошибка"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(phone=TEST_PHONE, is_phone_secure=True),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(password=TEST_DEFAULT_LOGIN), headers=self.get_headers())

        self.assert_error_response(resp, ['password.likelogin', 'password.short'], **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'password_validation_error',
                like_login='1',
                policy='basic',
            ),
            self.env.statbox.entry(
                'finished_with_error',
                error='password.invalid',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
                allowed_methods_to_bind='',
                is_new_method_required='0',
            ),
        ])

    def test_password_like_previous_validation_fails(self):
        """Пароль совпадает с предыдущим - ошибка"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(phone=TEST_PHONE, is_phone_secure=True),
        )
        self.set_track_values()
        encoded_hash = base64.b64encode(TEST_OLD_SERIALIZED_PASSWORD)
        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response({encoded_hash: True}),
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(resp, ['password.equals_previous'], **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'password_validation_error',
                like_old_password='1',
                policy='basic',
            ),
            self.env.statbox.entry(
                'finished_with_error',
                error='password.invalid',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
                allowed_methods_to_bind='',
                is_new_method_required='0',
            ),
        ])

    def test_password_found_in_history_validation_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(subscribed_to=[67], phone=TEST_PHONE, is_phone_secure=True),
        )
        self.set_track_values()
        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=True),
        )

        resp = self.make_request(self.query_params(password=TEST_PASSWORD_2), headers=self.get_headers())

        self.assert_error_response(resp, ['password.found_in_history'], **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'password_validation_error',
                found_in_history='1',
                policy='strong',
            ),
            self.env.statbox.entry(
                'finished_with_error',
                error='password.invalid',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
                allowed_methods_to_bind='',
                is_new_method_required='0',
            ),
        ])

    def test_password_like_confirmed_phone_fails(self):
        """Пароль совпадает с подтвержденным привязываемым телефоном"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(
            phone_confirmation_is_confirmed=True,
            phone_confirmation_phone_number=TEST_PHONE,
            current_restore_method=RESTORE_METHOD_LINK,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
        )

        resp = self.make_request(
            self.query_params(new_method=RESTORE_METHOD_PHONE, password=TEST_PHONE),
            headers=self.get_headers(),
        )

        self.assert_error_response(resp, ['password.likephonenumber'], **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'password_validation_error',
                like_phone_number='1',
                policy='basic',
            ),
            self.env.statbox.entry(
                'finished_with_error',
                error='password.invalid',
                suitable_restore_methods=','.join([RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_LINK,
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                new_method=RESTORE_METHOD_PHONE,
                allowed_methods_to_bind=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_HINT]),
                is_new_method_required='1',
            ),
        ])

    def test_password_like_secure_phone_fails(self):
        """Пароль совпадает с защищенным телефоном, не сохраненным в треке (не использованным для восстановления)"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(phone=TEST_PHONE, is_phone_secure=True),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(password=TEST_PHONE), headers=self.get_headers())

        self.assert_error_response(resp, ['password.likephonenumber'], **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'password_validation_error',
                like_phone_number='1',
                policy='basic',
            ),
            self.env.statbox.entry(
                'finished_with_error',
                error='password.invalid',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
                allowed_methods_to_bind='',
                is_new_method_required='0',
            ),
        ])

    def test_ok_phone_restoration(self):
        """Ручка успешно отрабатывает для обычного пользователя"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_PHONE],
            secure_phone_number=TEST_PHONE,
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_is_confirmed=True,
            device_application=TEST_APP_ID,
        )

        resp = self.make_request(self.query_params(password=TEST_PASSWORD_2), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            has_restorable_email=True,
            has_secure_phone_number=True,
        )
        self.check_db(
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
            is_secure_phone_bound=True,
        )
        self.check_event_log()
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
                is_hint_masked=True,
            ),
        )
        self.assert_social_binding_log_written()
        self.assert_restore_passed_notifications_sent(RESTORE_METHOD_PHONE)
        self.check_account_modification_push_sent(
            ip=TEST_IP,
            event_name='restore',
            uid=TEST_DEFAULT_UID,
            title='Доступ к аккаунту {} восстановлен'.format(TEST_DEFAULT_LOGIN),
            body='Если это вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
            context='{"track_id": "%s"}' % self.track_id,
        )

    def test_ok_phone_restoration__removed_pwn_forced_changing_suspension(self):
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            phone=TEST_PHONE,
            is_phone_secure=True,
            attributes={
                'password.pwn_forced_changing_suspended_at': str(int(time.time())),
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_PHONE],
            secure_phone_number=TEST_PHONE,
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_is_confirmed=True,
            device_application=TEST_APP_ID,
        )

        resp = self.make_request(self.query_params(password=TEST_PASSWORD_2), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            has_restorable_email=True,
            has_secure_phone_number=True,
        )
        self.check_db(
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
            is_secure_phone_bound=True,
        )
        self.check_event_log(had_pwn_forced_changing_suspension=True)
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
                is_hint_masked=True,
                had_pwn_forced_changing_suspension=True,
            ),
        )
        self.assert_social_binding_log_written()
        self.assert_restore_passed_notifications_sent(RESTORE_METHOD_PHONE)

    def test_ok_phone_restoration__removal_operation_cancelled(self):
        """Восстановление по телефону, на номере отложенная операция удаления - отменяем ее"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            phone=TEST_PHONE,
            is_phone_secure=True,
            is_secure_phone_being_removed=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_PHONE],
            secure_phone_number=TEST_PHONE,
        )

        resp = self.make_request(self.query_params(password=TEST_PASSWORD_2), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            has_restorable_email=True,
            has_secure_phone_number=True,
        )
        self.check_db(
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
            is_secure_phone_bound=True,
            sharddb_query_count=3,
        )
        for id_ in (TEST_OPERATION_ID1, TEST_OPERATION_ID2):
            self.env.db.check_missing(
                'phone_operations',
                db='passportdbshard1',
                uid=TEST_DEFAULT_UID,
                id=id_,
            )
        self.check_event_log(is_phone_removal_operation_cancelled=True)
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
                is_hint_masked=True,
                is_phone_removal_operation_cancelled=True,
                operation_type='remove_secure',
            ),
        )
        self.assert_restore_passed_notifications_sent(RESTORE_METHOD_PHONE)

    def test_ok_phone_restoration__secure_phone_replacement_by_phone_being_bound_cancelled(self):
        """Восстановление по телефону, на номере отложенная операция замены - отменяем ее"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            phone=TEST_PHONE,
            is_phone_secure=True,
            is_phone_being_bound_replaces_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_PHONE],
            secure_phone_number=TEST_PHONE,
        )

        resp = self.make_request(self.query_params(password=TEST_PASSWORD_2), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            has_restorable_email=True,
            has_secure_phone_number=True,
        )
        self.check_db(
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
            is_secure_phone_bound=True,
            sharddb_query_count=6,
        )
        assert_no_phone_in_db(self.env.db, TEST_DEFAULT_UID, TEST_PHONE_ID2, TEST_PHONE2)
        for id_ in (TEST_OPERATION_ID1, TEST_OPERATION_ID2):
            self.env.db.check_missing(
                'phone_operations',
                db='passportdbshard1',
                uid=TEST_DEFAULT_UID,
                id=id_,
            )
        self.check_event_log(is_phone_replacement_by_being_bound_operation_cancelled=True)
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
                is_hint_masked=True,
                is_phone_replacement_by_being_bound_operation_cancelled=True,
                operation_type='replace_secure_phone_with_nonbound_phone',
            ),
        )
        self.assert_restore_passed_notifications_sent(RESTORE_METHOD_PHONE)

    def test_ok_phone_restoration__secure_phone_replacement_by_simple_phone_cancelled(self):
        """Восстановление по телефону, на номере отложенная операция замены - отменяем ее"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            phone=TEST_PHONE,
            is_phone_secure=True,
            is_simple_phone_replaces_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_PHONE],
            secure_phone_number=TEST_PHONE,
        )

        resp = self.make_request(self.query_params(password=TEST_PASSWORD_2), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            has_restorable_email=True,
            has_secure_phone_number=True,
        )
        self.check_db(
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
            is_secure_phone_bound=True,
            sharddb_query_count=4,
        )
        for id_ in (TEST_OPERATION_ID1, TEST_OPERATION_ID2):
            self.env.db.check_missing(
                'phone_operations',
                db='passportdbshard1',
                uid=TEST_DEFAULT_UID,
                id=id_,
            )
        self.check_event_log(is_phone_replacement_by_simple_operation_cancelled=True)
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
                is_hint_masked=True,
                is_phone_replacement_by_simple_operation_cancelled=True,
                operation_type='replace_secure_phone_with_bound_phone',
            ),
        )
        self.assert_restore_passed_notifications_sent(RESTORE_METHOD_PHONE)

    def test_ok_phone_restoration__aliasification_operation_not_cancelled(self):
        """Восстановление по телефону, на номере операция алиасификации - не трогаем ее"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            phone=TEST_PHONE,
            is_phone_secure=True,
            is_secure_phone_being_aliasified=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_PHONE],
            secure_phone_number=TEST_PHONE,
        )

        resp = self.make_request(self.query_params(password=TEST_PASSWORD_2), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            has_restorable_email=True,
            has_secure_phone_number=True,
        )
        self.check_db(
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
            is_secure_phone_being_aliasified=True,
        )
        assert_secure_phone_being_aliasified.check_db(
            db_faker=self.env.db,
            uid=TEST_DEFAULT_UID,
            phone_attributes={
                'id': TEST_PHONE_ID,
                'number': TEST_PHONE_OBJECT.e164,
            },
            operation_attributes={
                'password_verified': DatetimeNow(),
                'code_confirmed': None,
                'finished': DatetimeNow() + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
            },
        )
        self.check_event_log()
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
                is_hint_masked=True,
            ),
        )
        self.assert_restore_passed_notifications_sent(RESTORE_METHOD_PHONE)

    def test_ok_email_restoration_with_secure_phone(self):
        """Ручка успешно отрабатывает для обычного пользователя, восстановление по email, на аккаунте есть телефон"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_EMAIL],
            user_entered_email='%s@gmail.com' % TEST_DEFAULT_LOGIN,
            current_restore_method=RESTORE_METHOD_EMAIL,
        )

        resp = self.make_request(self.query_params(password=TEST_PASSWORD_2), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            has_restorable_email=True,
            has_secure_phone_number=True,
        )
        self.check_db(
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
            is_secure_phone_bound=True,
        )
        self.check_event_log(method=RESTORE_METHOD_EMAIL)
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                current_restore_method=RESTORE_METHOD_EMAIL,
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
                is_hint_masked=True,
            ),
        )
        self.assert_social_binding_log_empty()
        self.assert_restore_passed_notifications_sent(RESTORE_METHOD_EMAIL, is_secure_phone_bound=True)

    def test_ok_email_restoration_without_secure_phone(self):
        """Ручка успешно отрабатывает для обычного пользователя, восстановление по email, на аккаунте нет телефона"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_EMAIL],
            user_entered_email='%s@gmail.com' % TEST_DEFAULT_LOGIN,
            current_restore_method=RESTORE_METHOD_EMAIL,
        )

        resp = self.make_request(self.query_params(password=TEST_PASSWORD_2), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            has_restorable_email=True,
            has_secure_phone_number=False,
        )
        self.check_db(
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
        )
        self.check_event_log(method=RESTORE_METHOD_EMAIL)
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                current_restore_method=RESTORE_METHOD_EMAIL,
                suitable_restore_methods=[RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE],
                is_hint_masked=True,
            ),
        )
        self.assert_restore_passed_notifications_sent(RESTORE_METHOD_EMAIL, is_secure_phone_bound=False)

    def test_ok_hint_restoration(self):
        """Ручка успешно отрабатывает для обычного пользователя, восстановление по КВ/КО"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_HINT],
            current_restore_method=RESTORE_METHOD_HINT,
        )

        resp = self.make_request(self.query_params(password=TEST_PASSWORD_2), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            has_restorable_email=False,
            has_secure_phone_number=False,
        )
        self.check_db(
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
        )
        self.check_event_log(method=RESTORE_METHOD_HINT)
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                current_restore_method=RESTORE_METHOD_HINT,
                suitable_restore_methods=[RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM],
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE],
            ),
        )
        self.assert_restore_passed_notifications_sent(RESTORE_METHOD_HINT)

    def test_with_session_ok(self):
        """Ручка успешно отрабатывает для обычного пользователя с существующей сессией"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_PHONE],
            secure_phone_number=TEST_PHONE,
        )

        resp = self.make_request(
            self.query_params(password=TEST_PASSWORD_2),
            headers=self.get_headers(cookie=TEST_USER_COOKIES),
        )

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated()
        self.check_db(
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
            is_secure_phone_bound=True,  # Телефон остался на месте
        )
        self.check_event_log()
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM],
                is_hint_masked=True,
            ),
        )
        self.assert_restore_passed_notifications_sent(RESTORE_METHOD_PHONE, send_to_external=False)

    def test_2fa_ok(self):
        """Ручка успешно отрабатывает для 2ФА-пользователя"""
        userinfo = self.default_userinfo_response(
            with_password=False,
            attributes={
                'account.2fa_on': '1',
            },
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
            restore_methods_select_order=[RESTORE_METHOD_PHONE_AND_2FA_FACTOR],
            secure_phone_number=TEST_PHONE,
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            is_2fa_restore=True,
            next_track_id=self.next_track_id,
            state='show_2fa_promo',
            has_restorable_email=True,
            has_secure_phone_number=True,
        )
        self.check_db(
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
            is_secure_phone_bound=True,  # Телефон без изменений
        )
        self.check_event_log(
            method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
            is_2fa_restore=True,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                suitable_restore_methods=USUAL_2FA_RESTORE_METHODS,
                current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
                is_2fa_restore=True,
            ),
        )
        self.assert_2fa_emails_sent(with_login_method_change_email=True)
        auth_track = self.track_manager.read(self.next_track_id)
        ok_(auth_track.is_otp_restore_passed)
        self.check_account_modification_push_sent(
            ip=TEST_IP,
            event_name='login_method_change',
            uid=TEST_DEFAULT_UID,
            title='Изменён способ входа в аккаунт {}'.format(TEST_DEFAULT_LOGIN),
            body='Если это изменение внесли вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
            context='{"track_id": "%s"}' % self.track_id,
        )

    def test_without_glogout_ok(self):
        """Пользователь попросил ничего не отзывать - глогаут не выставляем"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_PHONE],
            secure_phone_number=TEST_PHONE,
        )

        resp = self.make_request(
            self.query_params(
                password=TEST_PASSWORD_2,
                revoke_web_sessions=False,
                revoke_tokens=False,
                revoke_app_passwords=False,
            ),
            headers=self.get_headers(),
        )

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(is_glogouted=False)
        self.check_db(
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
            is_secure_phone_bound=True,  # Телефон остался на месте
            is_glogouted=False,
        )
        self.check_event_log(is_glogouted=False)
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM],
                is_hint_masked=True,
                is_glogouted=False,
            ),
        )
        self.assert_restore_passed_notifications_sent(RESTORE_METHOD_PHONE, send_to_external=False)

    def test_glogout_obligatory_by_strong_password_ok(self):
        """Пользователь попросил ничего не отзывать, но у него 67 сид - выставляем глогаут"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            phone=TEST_PHONE,
            is_phone_secure=True,
            subscribed_to=[67],
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_PHONE],
            secure_phone_number=TEST_PHONE,
        )

        resp = self.make_request(
            self.query_params(
                password=TEST_PASSWORD_2,
                revoke_web_sessions=False,
                revoke_tokens=False,
                revoke_app_passwords=False,
            ),
            headers=self.get_headers(),
        )

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated()
        self.check_db(
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
            is_secure_phone_bound=True,  # Телефон остался на месте
            sharddb_query_count=3,
        )
        self.check_event_log()
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM],
                is_hint_masked=True,
            ),
        )
        self.assert_restore_passed_notifications_sent(RESTORE_METHOD_PHONE, send_to_external=False)

    def test_glogout_obligatory_by_password_change_ok(self):
        """Пользователь попросил ничего не отзывать, но он принуждён к смене пароля - выставляем глогаут"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            phone=TEST_PHONE,
            is_phone_secure=True,
            password_changing_required=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_PHONE],
            secure_phone_number=TEST_PHONE,
        )

        resp = self.make_request(
            self.query_params(
                password=TEST_PASSWORD_2,
                revoke_web_sessions=False,
                revoke_tokens=False,
                revoke_app_passwords=False,
            ),
            headers=self.get_headers(),
        )

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated()
        self.check_db(
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
            is_secure_phone_bound=True,  # Телефон остался на месте
            sharddb_query_count=3,
        )
        self.check_event_log(was_password_change_required=True)
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM],
                is_hint_masked=True,
                was_password_change_required=True,
            ),
        )
        self.assert_restore_passed_notifications_sent(RESTORE_METHOD_PHONE, send_to_external=False)

    def test_pdd_ok(self):
        """Ручка успешно отрабатывает для ПДД-пользователя"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            emails=[
                self.create_native_email(*TEST_PDD_LOGIN.split('@')),
            ],
            alias_type='pdd',
            subscribed_to=[102],
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                can_users_change_password='1',
                domain=TEST_PDD_DOMAIN,
            ),
        )
        self.env.db.serialize(userinfo)
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_HINT,
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            user_entered_login=TEST_PDD_LOGIN,
            restore_methods_select_order=[RESTORE_METHOD_HINT],
        )

        resp = self.make_request(self.query_params(password=TEST_PASSWORD_2), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response(user_entered_login=TEST_PDD_LOGIN))
        self.assert_blackbox_userinfo_called(uid=str(TEST_PDD_UID))
        self.assert_track_updated(
            human_readable_login=TEST_PDD_LOGIN,
            machine_readable_login=TEST_PDD_LOGIN,
            domain=TEST_PDD_DOMAIN,
            has_restorable_email=False,
            has_secure_phone_number=False,
        )
        self.check_db(
            pdd=True,
            uid=TEST_PDD_UID,
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
        )
        self.check_event_log(method=RESTORE_METHOD_HINT, pdd=True, uid=TEST_PDD_UID)
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                current_restore_method=RESTORE_METHOD_HINT,
                suitable_restore_methods=[RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM],
                login=TEST_PDD_LOGIN,
                uid=TEST_PDD_UID,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE],
            ),
        )
        self.assert_restore_passed_notifications_sent(
            RESTORE_METHOD_HINT,
            send_to_external=False,
            login=TEST_PDD_LOGIN,
        )

    def test_lite_ok_redirected_to_completion(self):
        """Ручка успешно отрабатывает для лайт-пользователя, принуждает к дорегистрации"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            login=TEST_LITE_LOGIN,
            emails=[
                self.create_native_email(*TEST_LITE_LOGIN.split('@')),
            ],
            alias_type='lite',
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_HINT,
            login=TEST_LITE_LOGIN,
            user_entered_login=TEST_LITE_LOGIN,
            restore_methods_select_order=[RESTORE_METHOD_HINT],
            retpath=TEST_RETPATH,
        )

        resp = self.make_request(self.query_params(password=TEST_PASSWORD_2), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response(user_entered_login=TEST_LITE_LOGIN))
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            allow_authorization=None,
            allow_oauth_authorization=None,
            country=None,
            has_restorable_email=False,
            has_secure_phone_number=False,
            have_password=None,
            human_readable_login=None,
            is_2fa_restore=None,
            is_otp_restore_passed=None,
            is_password_passed=None,
            language=None,
            machine_readable_login=None,
            next_track_id=self.next_track_id,
            session_scope=None,
            state='force_complete_lite',
        )
        self.check_db(
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
        )
        self.check_event_log(method=RESTORE_METHOD_HINT)
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                current_restore_method=RESTORE_METHOD_HINT,
                suitable_restore_methods=[RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM],
                login=TEST_LITE_LOGIN,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE],
                retpath=TEST_RETPATH,
            ),
        )
        self.assert_restore_passed_notifications_sent(
            RESTORE_METHOD_HINT,
            send_to_external=False,
            login=TEST_LITE_LOGIN,
        )
        auth_track = self.track_manager.read(self.next_track_id)
        ok_(auth_track.is_force_complete_lite)
        eq_(auth_track.uid, str(TEST_DEFAULT_UID))
        eq_(auth_track.login, TEST_LITE_LOGIN)
        ok_(auth_track.have_password)
        ok_(auth_track.is_password_passed)
        ok_(auth_track.password_hash)
        eq_(auth_track.retpath, TEST_RETPATH)

    def test_lite_ok_redirect_disabled(self):
        """Ручка успешно отрабатывает для лайт-пользователя, принуждение выключено в настройках"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            login=TEST_LITE_LOGIN,
            emails=[
                self.create_native_email(*TEST_LITE_LOGIN.split('@')),
            ],
            alias_type='lite',
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_HINT,
            login=TEST_LITE_LOGIN,
            user_entered_login=TEST_LITE_LOGIN,
            restore_methods_select_order=[RESTORE_METHOD_HINT],
            retpath=TEST_RETPATH,
        )

        with settings_context(
            RESTORE_TO_FORCED_LITE_COMPLETION_ENABLED=False,
            DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
            SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=1,
            PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
            BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=settings.BLACKBOX_MD5_ARGON_HASH_DENOMINATOR,
            **merge_dicts(
                mock_counters(
                    ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
                        'push:changed_password': 5,
                        'push:login_method_change': 5,
                        'push:restore': 5,
                    },
                ),
                COMMON_URL_SETTINGS,
            )

        ):
            resp = self.make_request(self.query_params(password=TEST_PASSWORD_2), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response(user_entered_login=TEST_LITE_LOGIN))
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            login=TEST_LITE_LOGIN,
            human_readable_login=TEST_LITE_LOGIN,
            machine_readable_login=TEST_LITE_LOGIN,
            has_secure_phone_number=False,
        )
        self.check_db(
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
        )
        self.check_event_log(method=RESTORE_METHOD_HINT)
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                current_restore_method=RESTORE_METHOD_HINT,
                suitable_restore_methods=[RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM],
                login=TEST_LITE_LOGIN,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE],
                retpath=TEST_RETPATH,
            ),
        )
        self.assert_restore_passed_notifications_sent(
            RESTORE_METHOD_HINT,
            send_to_external=False,
            login=TEST_LITE_LOGIN,
        )

    def test_support_link_force_hint_restoration_with_data_flushed_ok(self):
        """Работаем по ссылке от саппорта для восстановления по КВ/КО, удаляем данные на аккаунте"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_HINT],
            current_restore_method=RESTORE_METHOD_HINT,
            support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
        )
        # Настраиваем ответы ручек, вызываемых для удаления данных
        self.env.social_api.set_social_api_response_value('')

        resp = self.make_request(self.query_params(password=TEST_PASSWORD_2), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            has_restorable_email=False,
            has_secure_phone_number=False,
        )
        self.check_db(
            sharddb_query_count=7,
            # КВ/КО должны остаться без изменений
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
        )
        self.check_event_log(
            method=RESTORE_METHOD_HINT,
            flushed_entities={'phones', 'social_profiles', 'emails'},
            support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
                suitable_restore_methods=[RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_HINT,
                flushed_entities={'phones', 'social_profiles', 'emails'},
                # При восстановлении по ссылке на КВ предлагаем привязать телефон
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE],
            ),
        )
        self.assert_no_emails_sent()
        self.assert_external_api_called_for_flushing()

    def test_support_link_change_password_set_method_with_new_method_phone_and_bank_phone_ok(self):
        """
        Работаем по ссылке от саппорта для восстановления по КВ/КО, удаляем данные на аккаунте,
        кроме банковского телефона (его просто делаем несекьюрным)
        """
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            phone=TEST_PHONE,
            is_phone_secure=True,
            is_phone_bank=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_HINT],
            current_restore_method=RESTORE_METHOD_HINT,
            support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
        )
        # Настраиваем ответы ручек, вызываемых для удаления данных
        self.env.social_api.set_social_api_response_value('')

        resp = self.make_request(self.query_params(password=TEST_PASSWORD_2), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            has_restorable_email=False,
            has_secure_phone_number=False,
        )
        self.check_db(
            sharddb_query_count=6,
            # КВ/КО должны остаться без изменений
            question=TEST_DEFAULT_HINT_QUESTION,
            answer=TEST_DEFAULT_HINT_ANSWER,
        )
        self.check_event_log(
            method=RESTORE_METHOD_HINT,
            flushed_entities={'phones', 'social_profiles', 'emails'},
            support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
            was_old_phone_just_unsecured=True,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
                suitable_restore_methods=[RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_HINT,
                flushed_entities={'phones', 'social_profiles', 'emails'},
                # При восстановлении по ссылке на КВ предлагаем привязать телефон
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE],
            ),
        )
        self.assert_no_emails_sent()
        self.assert_external_api_called_for_flushing()

    @parameterized.expand([
        ('0',),
        ('1000',),
        ('3000',),
        ('4000',),
        ('6000',),
        ('7000',),
        ('8000',),
    ])
    def test_support_link_force_phone_restoration_with_data_flushed_ok(self, karma):
        u"""Работаем по ссылке от саппорта для восстановления по телефону, удаляем данные на аккаунте"""
        userinfo = self.default_userinfo_response(
            with_password=False,
            attributes={
                'account.2fa_on': '1',
            },
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            phone=TEST_PHONE,
            is_phone_secure=True,
            karma=int(karma),
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_PHONE],
            current_restore_method=RESTORE_METHOD_PHONE,
            support_link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            secure_phone_number=TEST_PHONE,
        )
        # Настраиваем ответы ручек, вызываемых для удаления данных
        self.env.social_api.set_social_api_response_value('')

        resp = self.make_request(self.query_params(password=TEST_PASSWORD_2), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            is_2fa_restore=True,
            next_track_id=self.next_track_id,
            state='show_2fa_promo',
        )
        self.check_db(
            sharddb_query_count=5,
            # КВ/КО удаляются
            question=None,
            answer=None,
            # Телефон остался на аккаунте
            is_secure_phone_bound=True,
        )
        self.check_event_log(
            method=RESTORE_METHOD_PHONE,
            is_2fa_restore=True,
            flushed_entities={'hint', 'social_profiles', 'emails'},
            support_link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                is_2fa_restore=True,
                support_link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_PHONE,
                flushed_entities={'hint', 'social_profiles', 'emails'},
                old_karma=karma,
            ),
        )
        self.assert_2fa_emails_sent(send_to_external=False, with_login_method_change_email=True)
        self.assert_external_api_called_for_flushing()

    def test_support_link_change_password_set_method_with_new_method_hint_ok(self):
        """Работаем по ссылке от саппорта для ввода пароля и нового средства - КВ/КО, удаляем данные на аккаунте"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            enabled=False,
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_LINK],
            current_restore_method=RESTORE_METHOD_LINK,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
        )
        # Настраиваем ответы ручек, вызываемых для удаления данных
        self.env.social_api.set_social_api_response_value('')

        resp = self.make_request(
            self.query_params(
                new_method=RESTORE_METHOD_HINT,
                password=TEST_PASSWORD_2,
                question=TEST_HINT_QUESTION_TEXT_2,
                answer=TEST_HINT_ANSWER_2,
            ),
            headers=self.get_headers(),
        )

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            has_restorable_email=False,
            has_secure_phone_number=False,
        )
        self.check_db(
            sharddb_query_count=8,
            # Заданы новые КВ/КО
            question=TEST_HINT_QUESTION_2,
            answer=TEST_HINT_ANSWER_2,
        )
        self.check_event_log(
            method=RESTORE_METHOD_LINK,
            flushed_entities={'phones', 'hint', 'social_profiles', 'emails'},
            new_question=TEST_HINT_QUESTION_2,
            new_answer=TEST_HINT_ANSWER_2,
            account_was_disabled=True,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                suitable_restore_methods=[RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_LINK,
                flushed_entities={'phones', 'hint', 'social_profiles', 'emails'},
                new_method=RESTORE_METHOD_HINT,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE, RESTORE_METHOD_HINT],
                is_new_method_required=True,
                account_was_disabled=True,
            ),
        )
        self.assert_no_emails_sent()
        self.assert_external_api_called_for_flushing()

    def test_support_link_change_password_set_method_2fa_with_new_method_hint_ok(self):
        """Работаем по ссылке от саппорта для ввода пароля и нового средства - КВ/КО,
        удаляем данные на аккаунте, 2ФА-пользователь. Промо 2ФА не показываем, т.к. телефона нет"""
        userinfo = self.default_userinfo_response(
            with_password=False,
            attributes={
                'account.2fa_on': '1',
            },
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            enabled=False,
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_LINK],
            current_restore_method=RESTORE_METHOD_LINK,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
        )
        # Настраиваем ответы ручек, вызываемых для удаления данных
        self.env.social_api.set_social_api_response_value('')

        resp = self.make_request(
            self.query_params(
                new_method=RESTORE_METHOD_HINT,
                password=TEST_PASSWORD_2,
                question=TEST_HINT_QUESTION_TEXT_2,
                answer=TEST_HINT_ANSWER_2,
            ),
            headers=self.get_headers(),
        )

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            is_2fa_restore=True,
            has_restorable_email=False,
            has_secure_phone_number=False,
        )
        self.check_db(
            sharddb_query_count=8,
            # Заданы новые КВ/КО
            question=TEST_HINT_QUESTION_2,
            answer=TEST_HINT_ANSWER_2,
        )
        self.check_event_log(
            method=RESTORE_METHOD_LINK,
            flushed_entities={'phones', 'hint', 'social_profiles', 'emails'},
            new_question=TEST_HINT_QUESTION_2,
            new_answer=TEST_HINT_ANSWER_2,
            account_was_disabled=True,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            is_2fa_restore=True,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                suitable_restore_methods=[RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_LINK,
                flushed_entities={'phones', 'hint', 'social_profiles', 'emails'},
                new_method=RESTORE_METHOD_HINT,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE, RESTORE_METHOD_HINT],
                is_new_method_required=True,
                is_2fa_restore=True,
                account_was_disabled=True,
            ),
        )
        self.assert_2fa_emails_sent(send_to_external=False)
        self.assert_external_api_called_for_flushing()
        self.check_account_modification_push_sent(
            ip=TEST_IP,
            event_name='login_method_change',
            uid=TEST_DEFAULT_UID,
            title='Изменён способ входа в аккаунт {}'.format(TEST_DEFAULT_LOGIN),
            body='Если это изменение внесли вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
            context='{"track_id": "%s"}' % self.track_id,
        )
        self.check_account_modification_push_sent(
            ip=TEST_IP,
            event_name='restore',
            uid=TEST_DEFAULT_UID,
            title='Доступ к аккаунту {} восстановлен'.format(TEST_DEFAULT_LOGIN),
            body='Если это вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
            context='{"track_id": "%s"}' % self.track_id,
            index=1,
        )

    def test_support_link_change_password_set_method_sms_2fa_with_new_method_hint_ok(self):
        """Работаем по ссылке от саппорта для ввода пароля и нового средства - КВ/КО,
        удаляем данные на аккаунте, sms-2ФА-пользователь. Промо 2ФА не показываем, т.к. телефона нет"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            enabled=False,
            phone=TEST_PHONE,
            is_phone_secure=True,
            sms_2fa_on=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_LINK],
            current_restore_method=RESTORE_METHOD_LINK,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
        )
        # Настраиваем ответы ручек, вызываемых для удаления данных
        self.env.social_api.set_social_api_response_value('')

        resp = self.make_request(
            self.query_params(
                new_method=RESTORE_METHOD_HINT,
                password=TEST_PASSWORD_2,
                question=TEST_HINT_QUESTION_TEXT_2,
                answer=TEST_HINT_ANSWER_2,
            ),
            headers=self.get_headers(),
        )

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            has_restorable_email=False,
            has_secure_phone_number=False,
        )
        self.check_db(
            sharddb_query_count=8,
            # Заданы новые КВ/КО
            question=TEST_HINT_QUESTION_2,
            answer=TEST_HINT_ANSWER_2,
        )
        self.check_event_log(
            method=RESTORE_METHOD_LINK,
            flushed_entities={'phones', 'hint', 'social_profiles', 'emails'},
            new_question=TEST_HINT_QUESTION_2,
            new_answer=TEST_HINT_ANSWER_2,
            account_was_disabled=True,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            had_sms_2fa=True,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                suitable_restore_methods=[RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_LINK,
                flushed_entities={'phones', 'hint', 'social_profiles', 'emails'},
                new_method=RESTORE_METHOD_HINT,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE, RESTORE_METHOD_HINT],
                is_new_method_required=True,
                account_was_disabled=True,
                had_sms_2fa=True,
            ),
        )
        self.assert_external_api_called_for_flushing()

    def test_support_link_change_password_set_method_with_new_method_phone_ok(self):
        """Работаем по ссылке от саппорта для ввода пароля и нового средства - телефона, удаляем данные на аккаунте"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            enabled=False,
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self._phone_id_generator.set_list([TEST_PHONE_ID])
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_LINK],
            current_restore_method=RESTORE_METHOD_LINK,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            phone_confirmation_is_confirmed=True,
            phone_confirmation_phone_number=TEST_PHONE,
        )
        # Настраиваем ответы ручек, вызываемых для удаления данных
        self.env.social_api.set_social_api_response_value('')

        resp = self.make_request(
            self.query_params(
                new_method=RESTORE_METHOD_PHONE,
                password=TEST_PASSWORD_2,
            ),
            headers=self.get_headers(),
        )

        new_phone_status = {
            u'is_conflicted_operation_exists': False,
            u'is_bound_new_secure_phone': True,
            u'is_updated_current_secure_phone': False,
            u'is_replaced_phone_with_quarantine': False,
        }
        self.assert_ok_response(resp, new_phone_status=new_phone_status, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated()
        self.check_db(
            sharddb_query_count=16,
            # КВ/КО удалены
            question=None,
            answer=None,
            # Телефон (тот же, что и был) перепривязан
            is_secure_phone_bound=True,
            phone_action_date=DatetimeNow(),
        )
        self.check_event_log(
            method=RESTORE_METHOD_LINK,
            flushed_entities={'phones', 'hint', 'social_profiles', 'emails'},
            account_was_disabled=True,
            new_phone=TEST_PHONE,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                suitable_restore_methods=[RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_LINK,
                flushed_entities={'phones', 'hint', 'social_profiles', 'emails'},
                new_method=RESTORE_METHOD_PHONE,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE, RESTORE_METHOD_HINT],
                is_new_method_required=True,
                new_phone_status=new_phone_status,
                account_was_disabled=True,
            ),
        )
        self.assert_secure_phone_bound_notifications_sent()
        self.assert_external_api_called_for_flushing()

    def test_support_link_change_password_set_method_2fa_with_new_method_phone_ok(self):
        """Работаем по ссылке от саппорта для ввода пароля и нового средства - телефона, удаляем данные на 2ФА-аккаунте"""
        userinfo = self.default_userinfo_response(
            with_password=False,
            attributes={
                'account.2fa_on': '1',
            },
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            enabled=False,
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self._phone_id_generator.set_list([TEST_PHONE_ID])
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_LINK],
            current_restore_method=RESTORE_METHOD_LINK,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            phone_confirmation_is_confirmed=True,
            phone_confirmation_phone_number=TEST_PHONE,
        )
        # Настраиваем ответы ручек, вызываемых для удаления данных
        self.env.social_api.set_social_api_response_value('')

        resp = self.make_request(
            self.query_params(
                new_method=RESTORE_METHOD_PHONE,
                password=TEST_PASSWORD_2,
            ),
            headers=self.get_headers(),
        )

        new_phone_status = {
            u'is_conflicted_operation_exists': False,
            u'is_bound_new_secure_phone': True,
            u'is_updated_current_secure_phone': False,
            u'is_replaced_phone_with_quarantine': False,
        }
        self.assert_ok_response(resp, new_phone_status=new_phone_status, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            is_2fa_restore=True,
            next_track_id=self.next_track_id,
            state='show_2fa_promo',
        )
        self.check_db(
            sharddb_query_count=16,
            # КВ/КО удалены
            question=None,
            answer=None,
            # Телефон (тот же, что и был) перепривязан
            is_secure_phone_bound=True,
            phone_action_date=DatetimeNow(),
        )
        self.check_event_log(
            is_2fa_restore=True,
            method=RESTORE_METHOD_LINK,
            flushed_entities={'phones', 'hint', 'social_profiles', 'emails'},
            account_was_disabled=True,
            new_phone=TEST_PHONE,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                is_2fa_restore=True,
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                suitable_restore_methods=[RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_LINK,
                flushed_entities={'phones', 'hint', 'social_profiles', 'emails'},
                new_method=RESTORE_METHOD_PHONE,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE, RESTORE_METHOD_HINT],
                is_new_method_required=True,
                new_phone_status=new_phone_status,
                account_was_disabled=True,
            ),
        )
        expected_emails = self.build_expected_secure_phone_bound_notifications_context()
        expected_emails.extend(self.build_expected_2fa_emails_context(send_to_external=False))
        self.assert_emails_sent(expected_emails)
        self.assert_external_api_called_for_flushing()

    def test_support_link_change_password_set_method_with_no_password_with_new_method_phone_ok(self):
        """Работаем по ссылке от саппорта для ввода пароля и нового средства - телефона, удаляем данные на
        аккаунте без пароля"""
        userinfo = self.default_userinfo_response(
            with_password=False,  # случился сбой, аккаунт без пароля
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            enabled=False,
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self._phone_id_generator.set_list([TEST_PHONE_ID])
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_LINK],
            current_restore_method=RESTORE_METHOD_LINK,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            phone_confirmation_is_confirmed=True,
            phone_confirmation_phone_number=TEST_PHONE,
        )
        # Настраиваем ответы ручек, вызываемых для удаления данных
        self.env.social_api.set_social_api_response_value('')

        resp = self.make_request(
            self.query_params(
                new_method=RESTORE_METHOD_PHONE,
                password=TEST_PASSWORD_2,
            ),
            headers=self.get_headers(),
        )

        new_phone_status = {
            u'is_conflicted_operation_exists': False,
            u'is_bound_new_secure_phone': True,
            u'is_updated_current_secure_phone': False,
            u'is_replaced_phone_with_quarantine': False,
        }
        self.assert_ok_response(resp, new_phone_status=new_phone_status, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated()
        self.check_db(
            sharddb_query_count=16,
            # КВ/КО удалены
            question=None,
            answer=None,
            # Телефон (тот же, что и был) перепривязан
            is_secure_phone_bound=True,
            phone_action_date=DatetimeNow(),
        )
        self.check_event_log(
            method=RESTORE_METHOD_LINK,
            flushed_entities={'phones', 'hint', 'social_profiles', 'emails'},
            account_was_disabled=True,
            new_phone=TEST_PHONE,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                had_no_password=True,
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                suitable_restore_methods=[RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_LINK,
                flushed_entities={'phones', 'hint', 'social_profiles', 'emails'},
                new_method=RESTORE_METHOD_PHONE,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE, RESTORE_METHOD_HINT],
                is_new_method_required=True,
                new_phone_status=new_phone_status,
                account_was_disabled=True,
            ),
        )
        self.assert_secure_phone_bound_notifications_sent()
        self.assert_external_api_called_for_flushing()

    def test_support_link_change_password_set_method_with_new_method_phone_with_different_old_phone_ok(self):
        """Работаем по ссылке от саппорта для ввода пароля и нового средства - телефона, старый телефон отличается"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            enabled=False,
            # Есть старый незащищенный телефон
            phone=TEST_PHONE2,
            is_phone_secure=False,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self._phone_id_generator.set_list([TEST_PHONE_ID])
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_LINK],
            current_restore_method=RESTORE_METHOD_LINK,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            phone_confirmation_is_confirmed=True,
            phone_confirmation_phone_number=TEST_PHONE,
        )
        # Настраиваем ответы ручек, вызываемых для удаления данных
        self.env.social_api.set_social_api_response_value('')

        resp = self.make_request(
            self.query_params(
                new_method=RESTORE_METHOD_PHONE,
                password=TEST_PASSWORD_2,
            ),
            headers=self.get_headers(),
        )

        new_phone_status = {
            u'is_conflicted_operation_exists': False,
            u'is_bound_new_secure_phone': True,
            u'is_updated_current_secure_phone': False,
            u'is_replaced_phone_with_quarantine': False,
        }
        self.assert_ok_response(resp, new_phone_status=new_phone_status, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated()
        self.check_db(
            sharddb_query_count=15,
            centraldb_query_count=0,
            # КВ/КО удалены
            question=None,
            answer=None,
            # Новый телефон привязан
            is_secure_phone_bound=True,
            phone_action_date=DatetimeNow(),
        )
        self.check_event_log(
            method=RESTORE_METHOD_LINK,
            flushed_entities={'phones', 'hint', 'social_profiles', 'emails'},
            account_was_disabled=True,
            old_phone_object=TEST_PHONE2_OBJECT,
            is_old_phone_secure=False,
            new_phone=TEST_PHONE,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                suitable_restore_methods=[RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_LINK,
                flushed_entities={'phones', 'hint', 'social_profiles', 'emails'},
                new_method=RESTORE_METHOD_PHONE,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE, RESTORE_METHOD_HINT],
                is_new_method_required=True,
                new_phone_status=new_phone_status,
                had_secure_phone=False,
                account_was_disabled=True,
            ),
        )
        self.assert_secure_phone_bound_notifications_sent()
        self.assert_external_api_called_for_flushing()

    def test_support_link_with_missing_password_with_new_method_hint_ok(self):
        """Восстановление пользователя с портальным алиасом но без пароля, новое средство восстановления - КВ/КО"""
        userinfo = self.default_userinfo_response(
            with_password=False,
            enabled=False,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_LINK,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            restore_methods_select_order=[RESTORE_METHOD_LINK],
        )
        # Настраиваем ответы ручек, вызываемых для удаления данных
        self.env.social_api.set_social_api_response_value('')

        resp = self.make_request(
            self.query_params(
                new_method=RESTORE_METHOD_HINT,
                password=TEST_PASSWORD_2,
                question=TEST_HINT_QUESTION_TEXT_2,
                answer=TEST_HINT_ANSWER_2,
            ),
            headers=self.get_headers(),
        )

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            has_restorable_email=False,
            has_secure_phone_number=False,
        )
        self.check_db(
            sharddb_query_count=5,
            # Заданы новые КВ/КО
            question=TEST_HINT_QUESTION_2,
            answer=TEST_HINT_ANSWER_2,
        )
        self.check_event_log(
            account_was_disabled=True,
            had_old_phone=False,
            flushed_entities={'phones', 'hint', 'social_profiles', 'emails'},
            method=RESTORE_METHOD_LINK,
            new_question=TEST_HINT_QUESTION_2,
            new_answer=TEST_HINT_ANSWER_2,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                had_no_password=True,
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                suitable_restore_methods=[RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_LINK,
                flushed_entities={'phones', 'hint', 'social_profiles', 'emails'},
                new_method=RESTORE_METHOD_HINT,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE, RESTORE_METHOD_HINT],
                is_new_method_required=True,
                had_secure_phone=False,
                account_was_disabled=True,
            ),
        )
        self.assert_no_emails_sent()
        self.assert_external_api_called_for_flushing()

    def test_semi_auto_passed_with_new_secure_phone(self):
        """Пройдено восстановление по анкете, привязка нового защищенного номера"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
        )
        self._phone_id_generator.set_list([TEST_PHONE_ID])
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
            restore_methods_select_order=[RESTORE_METHOD_SEMI_AUTO_FORM],
            phone_confirmation_is_confirmed=True,
            phone_confirmation_phone_number=TEST_PHONE,
        )
        # Настраиваем ответы ручек, вызываемых для удаления данных
        self.env.social_api.set_social_api_response_value('')

        resp = self.make_request(
            self.query_params(
                new_method=RESTORE_METHOD_PHONE,
                password=TEST_PASSWORD_2,
            ),
            headers=self.get_headers(),
        )

        new_phone_status = {
            u'is_conflicted_operation_exists': False,
            u'is_bound_new_secure_phone': True,
            u'is_updated_current_secure_phone': False,
            u'is_replaced_phone_with_quarantine': False,
        }
        self.assert_ok_response(resp, new_phone_status=new_phone_status, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated()
        self.check_db(
            sharddb_query_count=13,
            # КВ/КО удалены
            question=None,
            answer=None,
            is_secure_phone_bound=True,
            phone_action_date=DatetimeNow(),
        )
        self.check_event_log(
            method=RESTORE_METHOD_SEMI_AUTO_FORM,
            flushed_entities={'social_profiles', 'emails', 'hint'},
            new_phone=TEST_PHONE,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                suitable_restore_methods=[RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
                flushed_entities={'hint', 'social_profiles', 'emails'},
                new_method=RESTORE_METHOD_PHONE,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE],
                is_new_method_required=True,
                new_phone_status=new_phone_status,
                is_hint_masked=True,
            ),
        )
        expected_emails = self.build_expected_secure_phone_bound_notifications_context()
        expected_emails.extend(self.build_expected_semi_auto_form_restore_passed_email_context())
        self.assert_emails_sent(expected_emails)
        self.assert_external_api_called_for_flushing()
        counter = get_per_phone_number_buckets()
        eq_(counter.get(TEST_PHONE), 1)  # Привязка телефона прошла, счетчик увеличился

    def test_semi_auto_passed_with_secure_phone_updated__com_tr_host(self):
        """Пройдено восстановление по анкете, подтверждение того же номера телефона"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
            restore_methods_select_order=[RESTORE_METHOD_SEMI_AUTO_FORM],
            phone_confirmation_is_confirmed=True,
            phone_confirmation_phone_number=TEST_PHONE,
        )
        # Настраиваем ответы ручек, вызываемых для удаления данных
        self.env.social_api.set_social_api_response_value('')

        resp = self.make_request(
            self.query_params(
                new_method=RESTORE_METHOD_PHONE,
                password=TEST_PASSWORD_2,
            ),
            headers=self.get_headers(host=TEST_HOST_TR),
        )

        new_phone_status = {
            u'is_conflicted_operation_exists': False,
            u'is_bound_new_secure_phone': False,
            u'is_updated_current_secure_phone': True,
            u'is_replaced_phone_with_quarantine': False,
        }
        self.assert_ok_response(resp, new_phone_status=new_phone_status, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated()
        self.check_db(
            sharddb_query_count=6,
            # КВ/КО удалены
            question=None,
            answer=None,
            is_secure_phone_updated=True,
        )
        self.check_event_log(
            method=RESTORE_METHOD_SEMI_AUTO_FORM,
            flushed_entities={'social_profiles', 'emails', 'hint'},
            is_secure_phone_updated=True,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
                flushed_entities={'hint', 'social_profiles', 'emails'},
                new_method=RESTORE_METHOD_PHONE,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE],
                is_new_method_required=True,
                new_phone_status=new_phone_status,
                is_hint_masked=True,
                host=TEST_HOST_TR,
            ),
        )
        self.assert_restore_passed_notifications_sent(RESTORE_METHOD_SEMI_AUTO_FORM, tld='com.tr')
        self.assert_external_api_called_for_flushing()
        counter = get_per_phone_number_buckets()
        eq_(counter.get(TEST_PHONE), 0)

    def test_semi_auto_passed_with_phone_replaced_with_quarantine(self):
        """Пройдено восстановление по анкете, привязка телефона через карантин"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
            restore_methods_select_order=[RESTORE_METHOD_SEMI_AUTO_FORM],
            phone_confirmation_is_confirmed=True,
            phone_confirmation_phone_number=TEST_PHONE2,
        )
        # Настраиваем ответы ручек, вызываемых для удаления данных
        self.env.social_api.set_social_api_response_value('')

        resp = self.make_request(
            self.query_params(
                new_method=RESTORE_METHOD_PHONE,
                password=TEST_PASSWORD_2,
            ),
            headers=self.get_headers(),
        )

        new_phone_status = {
            u'is_conflicted_operation_exists': False,
            u'is_bound_new_secure_phone': False,
            u'is_updated_current_secure_phone': False,
            u'is_replaced_phone_with_quarantine': True,
            u'secure_phone_pending_until': TimeNow(offset=settings.PHONE_QUARANTINE_SECONDS),
        }
        self.assert_ok_response(resp, new_phone_status=new_phone_status, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated()
        self.check_db(
            sharddb_query_count=15,
            # КВ/КО удалены
            question=None,
            answer=None,
            is_secure_phone_replaced_with_quarantine=True,
        )
        self.check_event_log(
            method=RESTORE_METHOD_SEMI_AUTO_FORM,
            flushed_entities={'social_profiles', 'emails', 'hint'},
            is_secure_phone_replaced_with_quarantine=True,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
                flushed_entities={'hint', 'social_profiles', 'emails'},
                new_method=RESTORE_METHOD_PHONE,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE],
                is_new_method_required=True,
                new_phone_status=new_phone_status,
                is_hint_masked=True,
            ),
        )
        requests = self.env.yasms.requests
        requests[-1].assert_query_contains({
            'from_uid': str(TEST_DEFAULT_UID),
            'text': u'Начата замена телефона на Яндексе: https://ya.cc/sms-help-ru',
        })
        expected_emails = self.build_expected_secure_phone_replaced_with_quarantine_notifications()
        expected_emails.extend(self.build_expected_semi_auto_form_restore_passed_email_context())
        self.assert_emails_sent(expected_emails)
        self.assert_external_api_called_for_flushing()
        counter = get_per_phone_number_buckets()
        eq_(counter.get(TEST_PHONE2), 1)  # Привязка телефона прошла, счетчик увеличился

    def test_semi_auto_passed_with_phone_conflicted_operation_ok(self):
        """Пройдено восстановление по анкете, при привязке телефона найдена конфликтующая операция"""
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            phone=TEST_PHONE,
            is_phone_secure=True,
            is_secure_phone_being_removed=True,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
            restore_methods_select_order=[RESTORE_METHOD_SEMI_AUTO_FORM],
            phone_confirmation_is_confirmed=True,
            phone_confirmation_phone_number=TEST_PHONE2,
        )
        # Настраиваем ответы ручек, вызываемых для удаления данных
        self.env.social_api.set_social_api_response_value('')

        resp = self.make_request(
            self.query_params(
                new_method=RESTORE_METHOD_PHONE,
                password=TEST_PASSWORD_2,
            ),
            headers=self.get_headers(),
        )

        new_phone_status = {
            u'is_conflicted_operation_exists': True,
            u'is_bound_new_secure_phone': False,
            u'is_updated_current_secure_phone': False,
            u'is_replaced_phone_with_quarantine': False,
        }
        self.assert_ok_response(resp, new_phone_status=new_phone_status, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated()
        self.check_db(
            sharddb_query_count=12,
            # КВ/КО удалены
            question=None,
            answer=None,
            # Защищенный телефон без изменений
            is_secure_phone_being_removed=True,
        )
        self.check_event_log(
            method=RESTORE_METHOD_SEMI_AUTO_FORM,
            flushed_entities={'social_profiles', 'emails', 'hint'},
            new_phone=None,  # Секьюрный телефон не менялся
            is_conflicted_operation_exists=True,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
                flushed_entities={'hint', 'social_profiles', 'emails'},
                new_method=RESTORE_METHOD_PHONE,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE],
                is_new_method_required=True,
                new_phone_status=new_phone_status,
                is_hint_masked=True,
            ),
        )
        self.assert_restore_passed_notifications_sent(RESTORE_METHOD_SEMI_AUTO_FORM)
        self.assert_external_api_called_for_flushing()
        counter = get_per_phone_number_buckets()
        eq_(counter.get(TEST_PHONE), 0)

    def test_account_disabled_on_deletion_restored_ok(self):
        """Аккаунт заблокирован при удалении не слишком давно, восстановление возможно"""
        # Запас 50 секунд на запуск теста
        deletion_started_at = time.time() - TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD.total_seconds() + 50
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            attributes={
                'account.deletion_operation_started_at': deletion_started_at,
                'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
            },
            phone=TEST_PHONE,
            is_phone_secure=True,
            hintq=None,
            hinta=None,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_PHONE],
            current_restore_method=RESTORE_METHOD_PHONE,
            secure_phone_number=TEST_PHONE,
            phone_confirmation_is_confirmed=True,
        )

        resp = self.make_request(
            self.query_params(password=TEST_PASSWORD_2),
            headers=self.get_headers(),
        )

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            has_restorable_email=True,
            phone_confirmation_phone_number=TEST_PHONE,
        )
        self.check_db(
            sharddb_query_count=4,
            is_secure_phone_bound=True,
        )
        self.check_event_log(
            method=RESTORE_METHOD_PHONE,
            account_was_disabled=True,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_PHONE,
                restored_from_deletion=True,
                account_was_disabled=True,
            ),
        )
        self.assert_restore_passed_notifications_sent(RESTORE_METHOD_PHONE)

    def test_child_disabled_on_deletion_restored_ok(self):
        """
        Аккаунт ребёнка заблокирован при удалении не слишком давно, восстановление возможно,
        при этом возвращаем ребёнка в семью
        """
        # Запас 50 секунд на запуск теста
        deletion_started_at = time.time() - TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD.total_seconds() + 50
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            attributes={
                'account.is_child': '1',
                'account.last_child_family': TEST_FAMILY_ID,
                'account.deletion_operation_started_at': deletion_started_at,
                'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
            },
            phone=TEST_PHONE,
            is_phone_secure=True,
            hintq=None,
            hinta=None,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.env.db.serialize(userinfo)
        self.env.blackbox.set_blackbox_response_value(
            'family_info',
            blackbox_family_info_response(family_id=TEST_FAMILY_ID),
        )
        self.set_track_values(
            restore_methods_select_order=[RESTORE_METHOD_PHONE],
            current_restore_method=RESTORE_METHOD_PHONE,
            secure_phone_number=TEST_PHONE,
            phone_confirmation_is_confirmed=True,
        )

        resp = self.make_request(
            self.query_params(password=TEST_PASSWORD_2),
            headers=self.get_headers(),
        )

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_blackbox_userinfo_called()
        self.assert_track_updated(
            has_restorable_email=True,
            phone_confirmation_phone_number=TEST_PHONE,
        )
        self.check_db(
            sharddb_query_count=4,
            centraldb_query_count=1,
            is_secure_phone_bound=True,
        )
        self.check_event_log(
            method=RESTORE_METHOD_PHONE,
            account_was_disabled=True,
            was_child_returned_to_family=True,
        )
        self.env.statbox.assert_has_written(
            self.get_expected_statbox_entries(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_PHONE,
                restored_from_deletion=True,
                account_was_disabled=True,
                was_child_returned_to_family=True,
            ),
        )
        self.assert_restore_passed_notifications_sent(RESTORE_METHOD_PHONE)


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:login_method_change': 5,
            'email:login_method_change': 5,
            'push:restore': 5,
        },
    )
)
class RestoreCommitTestCaseNoBlackboxHash(RestoreCommitTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
