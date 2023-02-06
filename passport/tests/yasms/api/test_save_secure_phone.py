# -*- coding: utf-8 -*-

from contextlib import contextmanager
from datetime import (
    datetime,
    timedelta,
)

from flask import request
from nose.tools import (
    eq_,
    istest,
    nottest,
    ok_,
    raises,
)
from passport.backend.api.common.account import (
    build_default_person_registration_info,
    default_account,
)
from passport.backend.api.env import APIEnvironment
from passport.backend.api.test.emails import (
    assert_user_notified_about_alias_as_login_and_email_disabled,
    assert_user_notified_about_alias_as_login_and_email_enabled,
    assert_user_notified_about_alias_as_login_disabled,
    assert_user_notified_about_alias_as_login_enabled,
    assert_user_notified_about_secure_phone_bound_to_passwordless_account,
)
from passport.backend.api.yasms.api import SaveSecurePhone
from passport.backend.api.yasms.exceptions import (
    YaSmsSecureNumberExists,
    YaSmsSecureNumberNotAllowed,
)
from passport.backend.core.builders.blackbox.exceptions import BlackboxTemporaryError
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_json_error_response,
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.conf import settings
from passport.backend.core.models.email import build_emails
from passport.backend.core.models.phones.faker import (
    assert_account_has_phonenumber_alias,
    assert_phone_unbound,
    assert_phonenumber_alias_missing,
    assert_phonenumber_alias_removed,
    assert_secure_phone_being_replaced,
    assert_secure_phone_bound,
    build_account,
    build_phone_being_bound,
    build_phone_being_bound_replaces_secure_operations,
    build_phone_bound,
    build_phone_secured,
    build_phone_unbound,
    build_secure_phone_being_bound,
    build_securify_operation,
    event_lines_phone_created,
    event_lines_phone_secured,
    event_lines_secure_bind_operation_created,
    event_lines_secure_bind_operation_deleted,
    event_lines_secure_phone_bound,
    event_lines_securify_operation_created,
    event_lines_securify_operation_deleted,
)
from passport.backend.core.models.phones.phones import SECURITY_IDENTITY
from passport.backend.core.runner.context_managers import (
    CREATE,
    UPDATE,
)
from passport.backend.core.test.consts import (
    TEST_PHONISH_LOGIN1,
    TEST_SOCIAL_LOGIN1,
)
from passport.backend.core.test.data import TEST_SERIALIZED_PASSWORD
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.core.yasms.test.emails import (
    assert_user_notified_about_realiasify,
    assert_user_notified_about_secure_phone_bound,
)
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)

from .base import BaseYasmsTestCase


TEST_UID1 = 1
TEST_UID2 = 2
TEST_UID3 = 3
TEST_PHONE_NUMBER1 = PhoneNumber.parse('+79123456789')
TEST_PHONE_NUMBER2 = PhoneNumber.parse('+79234567891')
TEST_PHONE_ID1 = 1
TEST_CONSUMER1 = 'dev'
TEST_ACTION1 = 'action'
TEST_USER_IP1 = '1.2.3.4'
TEST_USER_AGENT1 = 'curl'
TEST_ENV1 = APIEnvironment(user_ip=TEST_USER_IP1, user_agent=TEST_USER_AGENT1)
TEST_OPERATION_TTL1 = timedelta(seconds=5)
TEST_OPERATION_ID1 = 1
TEST_PASSWORD_HASH1 = '1:deadbeef'
TEST_PASSWORD1 = 'password1'
TEST_PASSWORD_QUALITY1 = 80
TEST_PHONE_ID2 = 2
TEST_PHONE_ID3 = 3
TEST_PHONE_ID4 = 4
TEST_PHONE_ID5 = 5
TEST_OPERATION_ID2 = 2
TEST_OPERATION_ID3 = 3
TEST_LOGIN1 = 'testuser1'
TEST_LOGIN2 = 'testuser2'
TEST_EMAIL1 = TEST_LOGIN1 + '@yandex-team.ru'
TEST_EMAIL2 = TEST_LOGIN2 + '@yandex-team.ru'
TEST_FIRSTNAME1 = u'Василий'
TEST_FIRSTNAME2 = u'Мария'
TEST_DATETIME1 = datetime(2000, 1, 1, 0, 0, 1)


@nottest
class BaseTest(BaseYasmsTestCase):
    is_new_phone = False
    is_binding = False

    # Идентификатор операции создающей защищённый телефон
    operation_id = TEST_OPERATION_ID1

    _DEFAULT_SETTINGS = dict(
        BaseYasmsTestCase._DEFAULT_SETTINGS,
        YASMS_VALIDATION_LIMIT=1,
        YASMS_PHONE_BINDING_LIMIT=1,
        YASMS_MARK_OPERATION_TTL=TEST_OPERATION_TTL1.total_seconds(),
        BLACKBOX_RETRIES=1,
        BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    )

    def setUp(self):
        super(BaseTest, self).setUp()
        self._env = {
            'consumer': TEST_CONSUMER1,
            'ip': TEST_USER_IP1,
            'user_agent': TEST_USER_AGENT1,
        }

        request.env = TEST_ENV1

        self._phone_id_generator_faker.set_list([TEST_PHONE_ID1])
        self._setup_statbox()

    def tearDown(self):
        del self._env
        super(BaseTest, self).tearDown()

    def _setup_statbox(self):
        exclude = list(self._env.keys()) + ['operation_id']
        self.env.statbox.bind_entry(
            'phone_confirmed',
            _inherit_from=['phone_confirmed'],
            _exclude=exclude,
            code_checks_count='0',
        )

    def _test_hit_binding_limit__should_not_ignore_limit(self):
        account = self._given(
            bindings_history__requested=True,
            other_binding__exists=True,
            other_binding__userinfo__requested=True,
        )

        self._save_secure_phone(account=account, phone_number=TEST_PHONE_NUMBER1)

        self._assert_secure_phone_bound(
            account,
            is_new_phone=self.is_new_phone,
            operation_id=self.operation_id,
        )
        self._assert_old_phone_unbound()

    def _test_cancel_operation(self):
        account = self._given(bindings_history__requested=self.is_binding)

        save_secure_phone = self._build_save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
        )

        save_secure_phone.submit()

        self._assert_operation_cancelled()

    def _test_blackbox_bindings_history_fail(self):
        account = self._given(
            bindings_history__requested=True,
            bindings_history__blackbox__fail=True,
        )

        save_secure_phone = self._build_save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
        )

        with self.assertRaises(BlackboxTemporaryError):
            save_secure_phone.submit()

    def _test_current_bindings__fail(self):
        account = self._given(
            bindings_history__requested=True,
            current_bindings__fail=True,
        )

        self._save_secure_phone(account=account, phone_number=TEST_PHONE_NUMBER1)

        self._assert_secure_phone_bound(
            account,
            is_new_phone=self.is_new_phone,
            operation_id=self.operation_id,
        )

    def _test_other_binding__userinfo__fail(self):
        account = self._given(
            bindings_history__requested=True,
            other_binding__exists=True,
            other_binding__userinfo__requested=True,
            other_binding__userinfo__fail=True,
        )

        self._save_secure_phone(account=account, phone_number=TEST_PHONE_NUMBER1)

        self._assert_secure_phone_bound(
            account,
            is_new_phone=self.is_new_phone,
            operation_id=self.operation_id,
        )

    def _test_dont_unbind_old_phones__no_binding(self):
        account = self._given(
            other_binding__exists=True,
            current_bindings__requested=False,
        )

        self._save_secure_phone(account=account, phone_number=TEST_PHONE_NUMBER1)

        self._assert_simple_phone_securified(account)
        assert_secure_phone_bound.check_db(self.env.db, TEST_UID3, {'id': TEST_PHONE_ID3})

    def _given(self, account__exists=True, account_phone_number_alias__exists=False,
               prev_alias_owner__exists=False, prev_alias_owner__primary_alias_type='portal',
               prev_alias_owner__search_alias_enabled=True,
               prev_alias_owner__userinfo__requested=False, prev_alias_owner__userinfo__fail=False,
               history_binding__exists=False,
               bindings_history__requested=False, bindings_history__blackbox__fail=False,
               other_binding__exists=False,
               current_bindings__requested=True, current_bindings__fail=False,
               other_binding__userinfo__requested=False, other_binding__userinfo__fail=False,
               create_pwd_hash__requested=False):
        if account__exists:
            kwargs = {}
            if account_phone_number_alias__exists:
                kwargs['aliases'] = {
                    'portal': TEST_LOGIN1,
                    'phonenumber': TEST_PHONE_NUMBER2.digital,
                }
                kwargs['attributes'] = {'account.enable_search_by_phone_alias': '1'}
            account = self._build_account(**kwargs)
        else:
            account = None

        userinfo = [None, None]
        phone_bindings = [None, None]

        emails = [
            self.env.email_toolkit.create_native_email(
                login=TEST_EMAIL2.split(u'@')[0],
                domain=TEST_EMAIL2.split(u'@')[1],
            ),
        ]
        prev_alias_owner_args = deep_merge(
            dict(
                uid=TEST_UID2,
                login=TEST_LOGIN2,
                aliases={
                    prev_alias_owner__primary_alias_type: TEST_LOGIN2,
                },
                crypt_password=TEST_PASSWORD_HASH1,
                firstname=TEST_FIRSTNAME2,
                emails=emails,
            ),
            build_phone_secured(
                TEST_PHONE_ID2,
                TEST_PHONE_NUMBER1.e164,
                is_alias=True,
                is_enabled_search_for_alias=prev_alias_owner__search_alias_enabled,
            ),
        )

        if prev_alias_owner__exists:
            build_account(db_faker=self.env.db, **prev_alias_owner_args)

        if prev_alias_owner__userinfo__requested:
            if prev_alias_owner__userinfo__fail:
                userinfo[0] = blackbox_json_error_response('DB_FETCHFAILED')
            else:
                if prev_alias_owner__exists:
                    userinfo[0] = blackbox_userinfo_response(**prev_alias_owner_args)
                else:
                    userinfo[0] = blackbox_userinfo_response(uid=None)

        if bindings_history__requested:
            if bindings_history__blackbox__fail:
                phone_bindings[0] = blackbox_json_error_response('DB_FETCHFAILED')
            else:
                if history_binding__exists:
                    phone_bindings[0] = blackbox_phone_bindings_response([
                        {
                            u'type': 'history',
                            u'number': TEST_PHONE_NUMBER1.e164,
                            u'phone_id': TEST_PHONE_ID2,
                            u'uid': TEST_UID1,
                            u'bound': TEST_DATETIME1,
                        },
                    ])
                else:
                    phone_bindings[0] = blackbox_phone_bindings_response([])

        other_binding_owner_userinfo_args = dict(
            uid=TEST_UID3,
            **build_phone_secured(
                TEST_PHONE_ID3,
                TEST_PHONE_NUMBER1.e164,
                phone_bound=TEST_DATETIME1,
                phone_created=TEST_DATETIME1,
                phone_confirmed=TEST_DATETIME1,
                phone_secured=TEST_DATETIME1,
            )
        )

        if other_binding__exists:
            build_account(db_faker=self.env.db, **other_binding_owner_userinfo_args)

        if current_bindings__requested:
            if current_bindings__fail:
                phone_bindings[1] = blackbox_json_error_response('DB_FETCHFAILED')
            else:
                current_bindings = []
                if other_binding__exists:
                    current_bindings.append({
                        'type': 'current',
                        'number': TEST_PHONE_NUMBER1.e164,
                        'phone_id': TEST_PHONE_ID3,
                        'uid': TEST_UID3,
                        'bound': TEST_DATETIME1,
                    })

                current_bindings.append({
                    'type': 'current',
                    'number': TEST_PHONE_NUMBER1.e164,
                    'phone_id': TEST_PHONE_ID1,
                    'uid': TEST_UID1,
                    'bound': datetime.now(),
                })
                phone_bindings[1] = blackbox_phone_bindings_response(current_bindings)

        if other_binding__userinfo__requested:
            if other_binding__userinfo__fail:
                userinfo[1] = blackbox_json_error_response('DB_FETCHFAILED')
            else:
                userinfo[1] = blackbox_userinfo_response_multiple([other_binding_owner_userinfo_args])

        if create_pwd_hash__requested:
            self.env.blackbox.set_blackbox_response_value(
                'create_pwd_hash',
                blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
            )

        userinfo = [i for i in userinfo if i is not None]
        self.env.blackbox.set_response_side_effect('userinfo', userinfo)

        phone_bindings = [b for b in phone_bindings if b is not None]
        self.env.blackbox.set_response_side_effect('phone_bindings', phone_bindings)

        return account

    def _build_account(self, **kwargs):
        return self._build_portal_account(**kwargs)

    def _build_portal_account(self, **kwargs):
        emails = [
            self.env.email_toolkit.create_native_email(
                login=TEST_EMAIL1.split(u'@')[0],
                domain=TEST_EMAIL1.split(u'@')[1],
            ),
        ]
        kwargs = merge_dicts(
            {
                'uid': TEST_UID1,
                'login': TEST_LOGIN1,
                'crypt_password': TEST_PASSWORD_HASH1,
                'firstname': TEST_FIRSTNAME1,
                'emails': emails,
            },
            kwargs,
        )
        return build_account(db_faker=self.env.db, **kwargs)

    def _build_social_account(self, **kwargs):
        if (
            'aliases' in kwargs and
            'portal' in kwargs['aliases']
        ):
            del kwargs['aliases']['portal']

        return self._build_portal_account(
            **deep_merge(
                dict(
                    aliases=dict(social=TEST_SOCIAL_LOGIN1),
                    crypt_password=None,
                    login=TEST_SOCIAL_LOGIN1,
                ),
                kwargs,
            )
        )

    def _build_phonish_account(self, **kwargs):
        kwargs = merge_dicts(
            dict(
                uid=TEST_UID1,
                login=TEST_PHONISH_LOGIN1,
                crypt_password=None,
                aliases=dict(phonish=TEST_PHONISH_LOGIN1),
            ),
            kwargs,
        )
        return build_account(db_faker=self.env.db, **kwargs)

    def _assert_karma_prefix_equals(self, account, uid, karma):
        eq_(account.karma.prefix, karma)

        actual_karma = self.env.db.get(u'attributes', u'karma.value', uid=uid, db=u'passportdbshard1')
        eq_(int(actual_karma) // 1000, karma)

    def _assert_secure_phone_bound(self, account, is_new_phone=True, operation_id=None,
                                   with_operation=True, notified=False):
        expected_attrs = {
            'id': TEST_PHONE_ID1,
            'confirmed': DatetimeNow(),
            'bound': DatetimeNow(),
            'secured': DatetimeNow(),
        }
        if is_new_phone:
            expected_attrs['created'] = DatetimeNow()
        assert_secure_phone_bound(account, expected_attrs)
        assert_secure_phone_bound.check_db(self.env.db, TEST_UID1, expected_attrs)

        exclude = list(self._env.keys())
        kwargs = {}

        if with_operation:
            operation_id = self.operation_id
            kwargs['operation_id'] = str(operation_id)
        else:
            operation_id = None
            exclude.append('operation_id')

        expected_statbox_entries = []
        if with_operation:
            expected_statbox_entries += [
                self.env.statbox.entry(
                    'secure_bind_operation_created',
                    **merge_dicts(self._env, kwargs)
                ),
            ]
        expected_statbox_entries += [
            self.env.statbox.entry(
                'phone_confirmed',
                **kwargs
            ),
            self.env.statbox.entry(
                'secure_phone_bound',
                _exclude=exclude,
                **kwargs
            ),
        ]
        self.env.statbox.assert_contains(expected_statbox_entries)

        expected_event_lines = tuple()
        if with_operation:
            expected_event_lines = (
                expected_event_lines +
                self._event_lines_secure_bind_operation_created(is_new_phone=is_new_phone, operation_id=operation_id) +
                self._event_lines_secure_bind_operation_deleted(operation_id=operation_id)
            )
        expected_event_lines = (
            expected_event_lines +
            self._event_lines_secure_phone_bound(operation_id=operation_id)
        )
        if is_new_phone and with_operation:
            expected_event_lines = expected_event_lines + self._event_lines_phone_created()
        self.env.event_logger.assert_contains(expected_event_lines)

    def _assert_user_notified_about_secure_phone_bound(
        self,
        language='ru',
        login=TEST_LOGIN1,
    ):
        assert_user_notified_about_secure_phone_bound(
            mailer_faker=self.env.mailer,
            language=language,
            email_address=TEST_EMAIL1,
            firstname=TEST_FIRSTNAME1,
            login=login,
        )

    def _assert_user_notified_about_alias_as_login_and_email_enabled(self, language='ru'):
        assert_user_notified_about_alias_as_login_and_email_enabled(
            self.env.mailer,
            language,
            TEST_EMAIL1,
            TEST_FIRSTNAME1,
            TEST_LOGIN1,
            TEST_EMAIL1,
            TEST_PHONE_NUMBER1.digital,
        )

    def _assert_user_notified_about_alias_as_login_enabled(self, language='ru'):
        assert_user_notified_about_alias_as_login_enabled(
            mailer_faker=self.env.mailer,
            language=language,
            email_address=TEST_EMAIL1,
            firstname=TEST_FIRSTNAME1,
            phone_number=TEST_PHONE_NUMBER1,

        )

    def _assert_simple_phone_securified(self, account):
        expected_attrs = {
            'id': TEST_PHONE_ID1,
            'confirmed': DatetimeNow(),
            'secured': DatetimeNow(),
        }
        assert_secure_phone_bound(account, expected_attrs)
        assert_secure_phone_bound.check_db(self.env.db, TEST_UID1, expected_attrs)

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'securify_operation_created',
                operation_id=str(self.operation_id),
                **self._env
            ),
            self.env.statbox.entry(
                'phone_confirmed',
                operation_id=str(self.operation_id),
            ),
            self.env.statbox.entry('phone_secured', operation_id=str(self.operation_id), _exclude=self._env.keys()),
        ])

        self.env.event_logger.assert_contains(
            self._event_lines_securify_operation_created() +
            self._event_lines_securify_operation_deleted() +
            self._event_lines_phone_secured(),
        )

    def _event_lines_phone_created(self):
        return event_lines_phone_created(
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1,
        )

    def _event_lines_secure_bind_operation_created(self, is_new_phone=True, operation_id=TEST_OPERATION_ID1):
        return event_lines_secure_bind_operation_created(
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1,
            operation_id=operation_id,
            operation_ttl=TEST_OPERATION_TTL1,
            is_new_phone=is_new_phone,
        )

    def _event_lines_secure_bind_operation_deleted(self, operation_id=TEST_OPERATION_ID1):
        return event_lines_secure_bind_operation_deleted(
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1,
            operation_id=operation_id,
            action=TEST_ACTION1,
        )

    def _event_lines_secure_phone_bound(self, operation_id=TEST_OPERATION_ID1):
        return event_lines_secure_phone_bound(
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1,
            operation_id=operation_id,
            action=TEST_ACTION1,
        )

    def _event_lines_account_washed(self):
        return (
            {'uid': str(TEST_UID1), 'name': 'action', 'value': TEST_ACTION1},
            {'uid': str(TEST_UID1), 'name': 'info.karma_prefix', 'value': str(settings.KARMA_PREFIX_WASHED)},
            {'uid': str(TEST_UID1), 'name': 'info.karma_full', 'value': str(settings.KARMA_PREFIX_WASHED) + '000'},
            {'uid': str(TEST_UID1), 'name': 'user_agent', 'value': TEST_USER_AGENT1},
            {'uid': str(TEST_UID1), 'name': 'consumer', 'value': TEST_CONSUMER1},
        )

    def _event_lines_securify_operation_created(self):
        return event_lines_securify_operation_created(
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1,
            operation_id=self.operation_id,
            operation_ttl=TEST_OPERATION_TTL1,
        )

    def _event_lines_securify_operation_deleted(self):
        return event_lines_securify_operation_deleted(
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1,
            operation_id=self.operation_id,
            action=TEST_ACTION1,
        )

    def _event_lines_phone_secured(self):
        return event_lines_phone_secured(
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1,
        )

    def _assert_account_washed(self, account, login=TEST_LOGIN1):
        eq_(account.karma.prefix, settings.KARMA_PREFIX_WASHED)
        self.env.db.check('attributes', 'karma.value', '6000', uid=TEST_UID1, db=u'passportdbshard1')

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'frodo_karma',
                action=TEST_ACTION1,
                new='6000',
                old='0',
                login=login,
                registration_datetime='-',
                **self._env
            ),
        ])

        self.env.event_logger.assert_contains(self._event_lines_account_washed())

    def _build_save_secure_phone(self, **kwargs):
        return SaveSecurePhone(
            consumer=TEST_CONSUMER1,
            env=TEST_ENV1,
            statbox=self._statbox,
            blackbox=self._blackbox_builder,
            yasms=self._yasms,
            **kwargs
        )

    def _event_lines_operation_cancelled(self, type='bind', security_identity=str(SECURITY_IDENTITY),
                                         phone_number=TEST_PHONE_NUMBER1, phone_id=TEST_PHONE_ID2,
                                         operation_id=TEST_OPERATION_ID1):
        phone_fmt = 'phone.%d.' % phone_id
        op_fmt = phone_fmt + 'operation.%d.' % operation_id

        event_lines = (
            {'uid': str(TEST_UID1), 'name': 'action', 'value': 'acquire_phone'},
            {'uid': str(TEST_UID1), 'name': phone_fmt + 'number', 'value': phone_number.e164},
            {'uid': str(TEST_UID1), 'name': op_fmt + 'type', 'value': type},
            {'uid': str(TEST_UID1), 'name': op_fmt + 'action', 'value': 'deleted'},
            {'uid': str(TEST_UID1), 'name': op_fmt + 'security_identity', 'value': security_identity},
            {'uid': str(TEST_UID1), 'name': 'consumer', 'value': TEST_CONSUMER1},
            {'uid': str(TEST_UID1), 'name': 'user_agent', 'value': TEST_USER_AGENT1},
        )

        if self.is_binding:
            event_lines = event_lines + (
                {'uid': str(TEST_UID1), 'name': phone_fmt + 'action', 'value': 'deleted'},
            )

        return event_lines

    def _save_secure_phone(self, account, *args, **kwargs):
        save_secure_phone = self._build_save_secure_phone(account=account, *args, **kwargs)

        save_secure_phone.submit()
        with UPDATE(
            account,
            TEST_ENV1,
            {'action': TEST_ACTION1, 'consumer': TEST_CONSUMER1},
        ):
            save_secure_phone.commit()
        save_secure_phone.after_commit()

    def _assert_phonenumber_alias_given_out(
        self,
        account,
        language='ru',
        is_owner_changed=False,
        is_new_account=False,
        enable_search=True,
        login=TEST_LOGIN1,
    ):
        eq_(account.phonenumber_alias.alias, TEST_PHONE_NUMBER1.digital)
        assert_account_has_phonenumber_alias(
            self.env.db,
            TEST_UID1,
            TEST_PHONE_NUMBER1.digital,
            enable_search=enable_search,
        )

        if is_new_account:
            uid = '-'
        else:
            uid = str(TEST_UID1)

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'phonenumber_alias_given_out',
                _exclude=self._env.keys(),
                login=login,
                is_owner_changed=str(int(is_owner_changed)),
                uid=uid,
            ),
            self.env.statbox.entry(
                'phonenumber_alias_added',
                **self._env
            ),
            self.env.statbox.entry(
                'phonenumber_alias_subscription_added',
                **self._env
            ),
            self.env.statbox.entry(
                'phonenumber_alias_search_enabled',
                new='1' if enable_search else '0',
                **self._env
            ),
        ])

        self.env.event_logger.assert_contains(self._event_lines_phonenumber_alias_given_out(enable_search=enable_search))

    def _event_lines_phonenumber_alias_given_out(self, enable_search=True):
        return (
            {'uid': str(TEST_UID1), 'name': 'action', 'value': TEST_ACTION1},
            {'uid': str(TEST_UID1), 'name': 'alias.phonenumber.add', 'value': TEST_PHONE_NUMBER1.international},
            {'uid': str(TEST_UID1), 'name': 'info.phonenumber_alias_search_enabled', 'value': '1' if enable_search else '0'},
            {'uid': str(TEST_UID1), 'name': 'consumer', 'value': TEST_CONSUMER1},
            {'uid': str(TEST_UID1), 'name': 'user_agent', 'value': TEST_USER_AGENT1},
        )

    def _assert_phonenumber_alias_taken_away(self, language='ru'):
        assert_phonenumber_alias_missing(self.env.db, TEST_UID2)
        assert_phonenumber_alias_removed(self.env.db, TEST_UID2, TEST_PHONE_NUMBER1.digital)

        assert_user_notified_about_realiasify(
            self.env.mailer,
            language,
            TEST_EMAIL2,
            TEST_FIRSTNAME2,
            TEST_LOGIN2,
            TEST_EMAIL2,
            TEST_PHONE_NUMBER1.digital,
        )

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'phonenumber_alias_taken_away',
                _exclude=self._env.keys(),
                uid=str(TEST_UID2),
            ),
            self.env.statbox.entry(
                'phonenumber_alias_subscription_removed',
                uid=str(TEST_UID2),
                **self._env
            ),
        ])

        self.env.event_logger.assert_contains(self._event_lines_phonenumber_alias_taken_away())

    def _assert_old_phonenumber_alias_taken_away(
        self,
        account,
        language='ru',
        email_as_login_enabled=True,
    ):
        ok_(not account.phonenumber_alias or account.phonenumber_alias.alias != TEST_PHONE_NUMBER2.digital)
        assert_phonenumber_alias_removed(self.env.db, TEST_UID1, TEST_PHONE_NUMBER2.digital)

        if email_as_login_enabled:
            assert_user_notified_about_alias_as_login_and_email_disabled(
                self.env.mailer,
                language,
                TEST_EMAIL1,
                TEST_FIRSTNAME1,
                TEST_LOGIN1,
                TEST_EMAIL1,
                TEST_PHONE_NUMBER2.digital,
            )
        else:
            assert_user_notified_about_alias_as_login_disabled(
                self.env.mailer,
                language,
                TEST_EMAIL1,
                TEST_FIRSTNAME1,
                TEST_LOGIN1,
                TEST_EMAIL1,
                TEST_PHONE_NUMBER2.digital,
            )

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'phonenumber_alias_taken_away',
                _exclude=self._env.keys(),
                number=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                reason='off',
                uid=str(TEST_UID1),
            ),
            self.env.statbox.entry(
                'phonenumber_alias_subscription_removed',
                uid=str(TEST_UID1),
                **self._env
            ),
        ])

        self.env.event_logger.assert_contains(
            self._event_lines_phonenumber_alias_taken_away(
                action=TEST_ACTION1,
                uid=TEST_UID1,
                phone_number=TEST_PHONE_NUMBER2,
            ),
        )

    def _event_lines_phonenumber_alias_taken_away(self, action='phone_alias_delete', uid=TEST_UID2, phone_number=TEST_PHONE_NUMBER1):
        return (
            {'uid': str(uid), 'name': 'action', 'value': action},
            {'uid': str(uid), 'name': 'alias.phonenumber.rm', 'value': phone_number.international},
            {'uid': str(uid), 'name': 'consumer', 'value': TEST_CONSUMER1},
        )

    def _assert_old_phone_unbound(self):
        assert_phone_unbound.check_db(
            self.env.db,
            TEST_UID3,
            {u'id': TEST_PHONE_ID3, 'number': TEST_PHONE_NUMBER1.e164},
        )
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'phone_unbound',
                _exclude=self._env.keys(),
                uid=str(TEST_UID3),
                phone_id=str(TEST_PHONE_ID3),
            ),
        ])

        self.env.event_logger.assert_contains(self._event_lines_old_phone_unbound())

    def _event_lines_old_phone_unbound(self):
        phone_fmt = 'phone.%d.' % TEST_PHONE_ID3
        op_fmt = phone_fmt + 'operation.%d.' % (self.operation_id + 1)
        return (
            {'uid': str(TEST_UID3), 'name': 'action', 'value': 'acquire_phone'},
            {'uid': str(TEST_UID3), 'name': phone_fmt + 'number', 'value': TEST_PHONE_NUMBER1.e164},
            {'uid': str(TEST_UID3), 'name': op_fmt + 'action', 'value': 'created'},
            {'uid': str(TEST_UID3), 'name': op_fmt + 'type', 'value': 'mark'},
            {'uid': str(TEST_UID3), 'name': op_fmt + 'security_identity', 'value': TEST_PHONE_NUMBER1.digital},
            {'uid': str(TEST_UID3), 'name': op_fmt + 'started', 'value': TimeNow()},
            {'uid': str(TEST_UID3), 'name': op_fmt + 'finished', 'value': TimeNow(offset=TEST_OPERATION_TTL1.total_seconds())},
            {'uid': str(TEST_UID3), 'name': 'consumer', 'value': TEST_CONSUMER1},

            {'uid': str(TEST_UID3), 'name': 'action', 'value': 'unbind_phone_from_account'},
            {'uid': str(TEST_UID3), 'name': 'reason_uid', 'value': str(TEST_UID1)},
            {'uid': str(TEST_UID3), 'name': phone_fmt + 'action', 'value': 'changed'},
            {'uid': str(TEST_UID3), 'name': phone_fmt + 'number', 'value': TEST_PHONE_NUMBER1.e164},
            {'uid': str(TEST_UID3), 'name': phone_fmt + 'bound', 'value': '0'},
            {'uid': str(TEST_UID3), 'name': op_fmt + 'action', 'value': 'deleted'},
            {'uid': str(TEST_UID3), 'name': op_fmt + 'type', 'value': 'mark'},
            {'uid': str(TEST_UID3), 'name': op_fmt + 'security_identity', 'value': TEST_PHONE_NUMBER1.digital},
            {'uid': str(TEST_UID3), 'name': 'consumer', 'value': TEST_CONSUMER1},

            {'uid': str(TEST_UID1), 'name': 'unbind_phone_from_account.%d' % TEST_UID3, 'value': TEST_PHONE_NUMBER1.e164},
            {'uid': str(TEST_UID1), 'name': 'consumer', 'value': TEST_CONSUMER1},
            {'uid': str(TEST_UID1), 'name': 'user_agent', 'value': TEST_USER_AGENT1},
        )


class CommonTestMixin(object):
    def test_save_clean_phone(self):
        account = self._given(bindings_history__requested=self.is_binding)

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
        )

        if self.is_binding:
            self._assert_secure_phone_bound(
                account,
                is_new_phone=self.is_new_phone,
                operation_id=self.operation_id,
            )
            self._assert_account_washed(account)
        else:
            self._assert_simple_phone_securified(account)

    def test_user_notified_about_secure_phone_bound(self):
        account = self._given(bindings_history__requested=self.is_binding)

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            should_notify_by_email=True,
        )

        self._assert_user_notified_about_secure_phone_bound()

    def test_aliasify__no_prev_owner(self):
        account = self._given(
            prev_alias_owner__userinfo__requested=True,
            bindings_history__requested=self.is_binding,
        )

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
        )

        if self.is_binding:
            self._assert_secure_phone_bound(account, is_new_phone=self.is_new_phone)
        else:
            self._assert_simple_phone_securified(account)

        self._assert_phonenumber_alias_given_out(account)

        eq_(len(self.env.mailer.messages), 0)

    def test_aliasify__no_prev_owner__notify(self):
        account = self._given(
            prev_alias_owner__userinfo__requested=True,
            bindings_history__requested=self.is_binding,
        )

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
            should_notify_by_email=True,
        )

        if self.is_binding:
            self._assert_secure_phone_bound(account, is_new_phone=self.is_new_phone)
        else:
            self._assert_simple_phone_securified(account)

        self._assert_phonenumber_alias_given_out(account)
        self._assert_user_notified_about_alias_as_login_and_email_enabled()
        eq_(len(self.env.mailer.messages), 2)

    def test_aliasify__has_prev_owner(self):
        account = self._given(
            prev_alias_owner__exists=True,
            prev_alias_owner__userinfo__requested=True,
            bindings_history__requested=self.is_binding,
        )

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
        )

        if self.is_binding:
            self._assert_secure_phone_bound(account, is_new_phone=self.is_new_phone)
        else:
            self._assert_simple_phone_securified(account)

        self._assert_phonenumber_alias_given_out(account, is_owner_changed=True)
        self._assert_phonenumber_alias_taken_away()

        eq_(len(self.env.mailer.messages), 1)

    def test_aliasify__has_prev_owner__notify(self):
        account = self._given(
            prev_alias_owner__exists=True,
            prev_alias_owner__userinfo__requested=True,
            bindings_history__requested=self.is_binding,
        )

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
            should_notify_by_email=True,
        )

        if self.is_binding:
            self._assert_secure_phone_bound(account, is_new_phone=self.is_new_phone)
        else:
            self._assert_simple_phone_securified(account)

        self._assert_phonenumber_alias_given_out(account, is_owner_changed=True)
        self._assert_user_notified_about_alias_as_login_and_email_enabled()
        self._assert_phonenumber_alias_taken_away()

        eq_(len(self.env.mailer.messages), 3)

    def test_aliasify__has_old_alias(self):
        # Такую ситуацию следует считать ошибкой.
        # Здесь проверяется восстановление после ошибки.

        account = self._given(
            account_phone_number_alias__exists=True,
            prev_alias_owner__userinfo__requested=True,
            bindings_history__requested=self.is_binding,
        )

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
        )

        if self.is_binding:
            self._assert_secure_phone_bound(account, is_new_phone=self.is_new_phone)
        else:
            self._assert_simple_phone_securified(account)

        self._assert_phonenumber_alias_given_out(account)
        self._assert_old_phonenumber_alias_taken_away(account)

    def test_save_dirty_phone(self):
        account = self._given(
            bindings_history__requested=self.is_binding,
            history_binding__exists=True,
        )

        self._save_secure_phone(account=account, phone_number=TEST_PHONE_NUMBER1)

        if self.is_binding:
            self._assert_secure_phone_bound(
                account,
                is_new_phone=self.is_new_phone,
                operation_id=self.operation_id,
            )
        else:
            self._assert_simple_phone_securified(account)

    def test_language(self):
        account = self._given(
            account_phone_number_alias__exists=True,
            prev_alias_owner__exists=True,
            prev_alias_owner__userinfo__requested=True,
            bindings_history__requested=self.is_binding,
        )

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
            should_notify_by_email=True,
            language='en',
            notification_language='en',
        )

        self._assert_user_notified_about_secure_phone_bound(language='en')
        self._assert_phonenumber_alias_given_out(account, language='en', is_owner_changed=True)
        self._assert_old_phonenumber_alias_taken_away(account, language='en')
        self._assert_phonenumber_alias_taken_away(language='ru')

    @raises(BlackboxTemporaryError)
    def test_prev_alias_owner_userinfo_fail(self):
        account = self._given(
            prev_alias_owner__userinfo__requested=True,
            prev_alias_owner__userinfo__fail=True,
        )

        save_secure_phone = self._build_save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
        )

        save_secure_phone.submit()


@istest
class TestNoPhone(BaseTest, CommonTestMixin):
    is_new_phone = True
    is_binding = True

    def test_hit_binding_limit__should_not_ignore_limit(self):
        self._test_hit_binding_limit__should_not_ignore_limit()

    def test_blackbox_bindings_history_fail(self):
        self._test_blackbox_bindings_history_fail()

    def test_current_bindings__fail(self):
        self._test_current_bindings__fail()

    def test_other_binding__userinfo__fail(self):
        self._test_other_binding__userinfo__fail()


@istest
class TestNoPhonePasswordlessAccount(BaseTest, CommonTestMixin):
    is_new_phone = True
    is_binding = True

    def test_aliasify__no_prev_owner__notify(self):
        account = self._given(
            prev_alias_owner__userinfo__requested=True,
            bindings_history__requested=True,
        )

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
            should_notify_by_email=True,
        )

        self._assert_secure_phone_bound(account, is_new_phone=True)

        self._assert_phonenumber_alias_given_out(account)
        self._assert_user_notified_about_alias_as_login_enabled()
        eq_(len(self.env.mailer.messages), 2)

    def test_aliasify__has_prev_owner__notify(self):
        account = self._given(
            prev_alias_owner__exists=True,
            prev_alias_owner__userinfo__requested=True,
            bindings_history__requested=True,
        )

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
            should_notify_by_email=True,
        )

        self._assert_secure_phone_bound(account, is_new_phone=True)

        self._assert_phonenumber_alias_given_out(account, is_owner_changed=True)
        self._assert_user_notified_about_alias_as_login_enabled()
        self._assert_phonenumber_alias_taken_away()

        eq_(len(self.env.mailer.messages), 3)

    def _build_account(self, **kwargs):
        return self._build_social_account(**kwargs)

    def _build_save_secure_phone(self, **kwargs):
        return SaveSecurePhone(
            consumer=TEST_CONSUMER1,
            env=TEST_ENV1,
            statbox=self._statbox,
            blackbox=self._blackbox_builder,
            yasms=self._yasms,
            enable_search_alias=False,
            **kwargs
        )

    def _assert_phonenumber_alias_given_out(self, account, **kwargs):
        defaults = dict(
            enable_search=False,
            login=TEST_SOCIAL_LOGIN1,
        )
        for key, val in defaults.items():
            kwargs.setdefault(key, val)

        super(TestNoPhonePasswordlessAccount, self)._assert_phonenumber_alias_given_out(account, **kwargs)

    def _assert_account_washed(self, account, **kwargs):
        kwargs.setdefault('login', TEST_SOCIAL_LOGIN1)
        super(TestNoPhonePasswordlessAccount, self)._assert_account_washed(account, **kwargs)

    def _assert_user_notified_about_secure_phone_bound(
        self,
        language='ru',
        login=TEST_FIRSTNAME1,
    ):
        assert_user_notified_about_secure_phone_bound_to_passwordless_account(
            mailer_faker=self.env.mailer,
            language=language,
            email_address=TEST_EMAIL1,
            firstname=TEST_FIRSTNAME1,
            login=login,
        )

    def _assert_old_phonenumber_alias_taken_away(self, account, **kwargs):
        kwargs.setdefault('email_as_login_enabled', False)
        super(TestNoPhonePasswordlessAccount, self)._assert_old_phonenumber_alias_taken_away(account, **kwargs)


@istest
class TestPhoneUnbound(BaseTest, CommonTestMixin):
    is_binding = True

    def _build_account(self, **kwargs):
        return super(TestPhoneUnbound, self)._build_account(
            **deep_merge(
                build_phone_unbound(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164),
                kwargs,
            )
        )

    def test_hit_binding_limit__should_not_ignore_limit(self):
        self._test_hit_binding_limit__should_not_ignore_limit()

    def test_blackbox_bindings_history_fail(self):
        self._test_blackbox_bindings_history_fail()

    def test_current_bindings__fail(self):
        self._test_current_bindings__fail()

    def test_other_binding__userinfo__fail(self):
        self._test_other_binding__userinfo__fail()


@istest
class TestSimplePhoneBeingBound(BaseTest, CommonTestMixin):
    is_binding = True
    is_new_phone = True
    operation_id = TEST_OPERATION_ID2

    def _build_account(self, **kwargs):
        return super(TestSimplePhoneBeingBound, self)._build_account(
            **deep_merge(
                build_phone_being_bound(TEST_PHONE_ID4, TEST_PHONE_NUMBER1.e164, TEST_OPERATION_ID1),
                kwargs,
            )
        )

    def test_cancel_operation(self):
        self._test_cancel_operation()

    def test_hit_binding_limit__should_not_ignore_limit(self):
        self._test_hit_binding_limit__should_not_ignore_limit()

    def test_blackbox_bindings_history_fail(self):
        self._test_blackbox_bindings_history_fail()

    def test_current_bindings__fail(self):
        self._test_current_bindings__fail()

    def test_other_binding__userinfo__fail(self):
        self._test_other_binding__userinfo__fail()

    def _assert_operation_cancelled(self):
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'phone_operation_cancelled',
                _exclude=self._env.keys(),
                operation_type='simple_bind',
            ),
        ])
        self.env.event_logger.assert_contains(
            self._event_lines_operation_cancelled(
                security_identity=TEST_PHONE_NUMBER1.digital,
                phone_id=TEST_PHONE_ID4,
            ),
        )


@istest
class TestSecurePhoneBeingBound(BaseTest, CommonTestMixin):
    is_binding = True
    is_new_phone = True
    operation_id = TEST_OPERATION_ID2

    def _build_account(self, **kwargs):
        return super(TestSecurePhoneBeingBound, self)._build_account(
            **deep_merge(
                build_secure_phone_being_bound(TEST_PHONE_ID4, TEST_PHONE_NUMBER1.e164, TEST_OPERATION_ID1),
                kwargs,
            )
        )

    def test_cancel_operation(self):
        self._test_cancel_operation()

    def test_hit_binding_limit__should_not_ignore_limit(self):
        self._test_hit_binding_limit__should_not_ignore_limit()

    def test_blackbox_bindings_history_fail(self):
        self._test_blackbox_bindings_history_fail()

    def test_current_bindings__fail(self):
        self._test_current_bindings__fail()

    def test_other_binding__userinfo__fail(self):
        self._test_other_binding__userinfo__fail()

    def _assert_operation_cancelled(self):
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'phone_operation_cancelled',
                _exclude=self._env.keys(),
                operation_type='secure_bind',
            ),
        ])
        self.env.event_logger.assert_contains(
            self._event_lines_operation_cancelled(phone_id=TEST_PHONE_ID4),
        )


@istest
class TestOtherSecurePhoneBeingBound(BaseTest, CommonTestMixin):
    is_binding = True
    is_new_phone = True
    operation_id = TEST_OPERATION_ID2

    def _build_account(self, **kwargs):
        return super(TestOtherSecurePhoneBeingBound, self)._build_account(
            **deep_merge(
                build_secure_phone_being_bound(TEST_PHONE_ID4, TEST_PHONE_NUMBER2.e164, TEST_OPERATION_ID1),
                kwargs,
            )
        )

    def test_cancel_operation(self):
        self._test_cancel_operation()

    def test_hit_binding_limit__should_not_ignore_limit(self):
        self._test_hit_binding_limit__should_not_ignore_limit()

    def test_blackbox_bindings_history_fail(self):
        self._test_blackbox_bindings_history_fail()

    def test_current_bindings__fail(self):
        self._test_current_bindings__fail()

    def test_other_binding__userinfo__fail(self):
        self._test_other_binding__userinfo__fail()

    def _assert_operation_cancelled(self):
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'phone_operation_cancelled',
                _exclude=self._env.keys(),
                operation_type='secure_bind',
            ),
        ])
        self.env.event_logger.assert_contains(
            self._event_lines_operation_cancelled(
                phone_number=TEST_PHONE_NUMBER2,
                phone_id=TEST_PHONE_ID4,
            ),
        )


@istest
class TestOtherSecurePhoneBeingBoundSimpleBeingPhoneBound(BaseTest, CommonTestMixin):
    is_binding = True
    is_new_phone = True
    operation_id = TEST_OPERATION_ID3

    def _build_account(self, **kwargs):
        return super(TestOtherSecurePhoneBeingBoundSimpleBeingPhoneBound, self)._build_account(
            **deep_merge(
                build_secure_phone_being_bound(TEST_PHONE_ID4, TEST_PHONE_NUMBER2.e164, TEST_OPERATION_ID1),
                build_phone_being_bound(TEST_PHONE_ID5, TEST_PHONE_NUMBER1.e164, TEST_OPERATION_ID2),
                kwargs,
            )
        )

    def test_cancel_operation(self):
        self._test_cancel_operation()

    def test_hit_binding_limit__should_not_ignore_limit(self):
        self._test_hit_binding_limit__should_not_ignore_limit()

    def test_blackbox_bindings_history_fail(self):
        self._test_blackbox_bindings_history_fail()

    def test_current_bindings__fail(self):
        self._test_current_bindings__fail()

    def test_other_binding__userinfo__fail(self):
        self._test_other_binding__userinfo__fail()

    def _assert_operation_cancelled(self):
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'phone_operation_cancelled',
                _exclude=self._env.keys(),
                operation_type='simple_bind',
                operation_id=str(TEST_OPERATION_ID2),
            ),
            self.env.statbox.entry(
                'phone_operation_cancelled',
                _exclude=self._env.keys(),
                operation_type='secure_bind',
                operation_id=str(TEST_OPERATION_ID1),
            ),
        ])
        self.env.event_logger.assert_contains(
            self._event_lines_operation_cancelled(
                phone_id=TEST_PHONE_ID4,
                phone_number=TEST_PHONE_NUMBER2,
            ) +
            self._event_lines_operation_cancelled(
                security_identity=TEST_PHONE_NUMBER1.digital,
                phone_id=TEST_PHONE_ID5,
                operation_id=TEST_OPERATION_ID2,
            ),
        )


@istest
class TestSimplePhoneNoOperation(BaseTest, CommonTestMixin):

    def _build_account(self, **kwargs):
        return super(TestSimplePhoneNoOperation, self)._build_account(
            **deep_merge(
                build_phone_bound(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164),
                kwargs,
            )
        )

    def test_dont_unbind_old_phones__no_binding(self):
        self._test_dont_unbind_old_phones__no_binding()


@istest
class TestSimplePhoneNoOperationPasswordlessAccount(BaseTest, CommonTestMixin):
    def test_aliasify__no_prev_owner__notify(self):
        account = self._given(prev_alias_owner__userinfo__requested=True)

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
            should_notify_by_email=True,
        )

        self._assert_simple_phone_securified(account)

        self._assert_phonenumber_alias_given_out(account)
        self._assert_user_notified_about_alias_as_login_enabled()
        eq_(len(self.env.mailer.messages), 2)

    def test_aliasify__has_prev_owner__notify(self):
        account = self._given(
            prev_alias_owner__exists=True,
            prev_alias_owner__userinfo__requested=True,
        )

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
            should_notify_by_email=True,
        )

        self._assert_simple_phone_securified(account)

        self._assert_phonenumber_alias_given_out(account, is_owner_changed=True)
        self._assert_user_notified_about_alias_as_login_enabled()
        self._assert_phonenumber_alias_taken_away()

        eq_(len(self.env.mailer.messages), 3)

    def _build_account(self, **kwargs):
        return self._build_social_account(
            **deep_merge(
                build_phone_bound(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164),
                kwargs,
            )
        )

    def _build_save_secure_phone(self, **kwargs):
        return SaveSecurePhone(
            consumer=TEST_CONSUMER1,
            env=TEST_ENV1,
            statbox=self._statbox,
            blackbox=self._blackbox_builder,
            yasms=self._yasms,
            enable_search_alias=False,
            **kwargs
        )

    def _assert_phonenumber_alias_given_out(self, account, **kwargs):
        defaults = dict(
            enable_search=False,
            login=TEST_SOCIAL_LOGIN1,
        )
        for key, val in defaults.items():
            kwargs.setdefault(key, val)

        super(TestSimplePhoneNoOperationPasswordlessAccount, self)._assert_phonenumber_alias_given_out(account, **kwargs)

    def _assert_user_notified_about_secure_phone_bound(
        self,
        language='ru',
        login=TEST_FIRSTNAME1,
    ):
        assert_user_notified_about_secure_phone_bound_to_passwordless_account(
            mailer_faker=self.env.mailer,
            language=language,
            email_address=TEST_EMAIL1,
            firstname=TEST_FIRSTNAME1,
            login=login,
        )

    def _assert_old_phonenumber_alias_taken_away(self, account, **kwargs):
        kwargs.setdefault('email_as_login_enabled', False)
        super(TestSimplePhoneNoOperationPasswordlessAccount, self)._assert_old_phonenumber_alias_taken_away(account, **kwargs)


@istest
class TestSimplePhoneBeingSecurified(BaseTest, CommonTestMixin):
    operation_id = TEST_OPERATION_ID2

    def _build_account(self, **kwargs):
        return super(TestSimplePhoneBeingSecurified, self)._build_account(
            **deep_merge(
                build_phone_bound(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164),
                build_securify_operation(TEST_OPERATION_ID1, TEST_PHONE_ID1),
                kwargs,
            )
        )

    def test_cancel_operation(self):
        self._test_cancel_operation()

    def test_dont_unbind_old_phones__no_binding(self):
        self._test_dont_unbind_old_phones__no_binding()

    def _assert_operation_cancelled(self):
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'phone_operation_cancelled',
                _exclude=self._env.keys(),
                operation_type='securify',
            ),
        ])
        self.env.event_logger.assert_contains(
            self._event_lines_operation_cancelled(type='securify', phone_number=TEST_PHONE_NUMBER1, phone_id=TEST_PHONE_ID1),
        )


@istest
class TestOther(BaseTest):
    @raises(YaSmsSecureNumberExists)
    def test_account_has_secure_phone(self):
        account = self._build_account(
            **build_phone_secured(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164)
        )

        save_secure_phone = self._build_save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
        )

        save_secure_phone.submit()

    def test_secure_phone_being_replaced(self):
        account = self._build_account(
            **deep_merge(
                build_phone_secured(TEST_PHONE_ID2, TEST_PHONE_NUMBER2.e164),
                build_phone_unbound(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=TEST_OPERATION_ID2,
                    secure_phone_id=TEST_PHONE_ID2,
                    being_bound_operation_id=TEST_OPERATION_ID1,
                    being_bound_phone_id=TEST_PHONE_ID1,
                    being_bound_phone_number=TEST_PHONE_NUMBER1.e164,
                ),
            )
        )

        save_secure_phone = self._build_save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
        )

        with self.assertRaises(YaSmsSecureNumberExists):
            save_secure_phone.submit()

        assert_secure_phone_being_replaced(
            account,
            {'id': TEST_PHONE_ID2},
            {'id': TEST_OPERATION_ID2},
        )

    def test_account_disabled(self):
        account = self._build_account(
            enabled=False,
            **build_phone_bound(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164)
        )

        self._save_secure_phone(account=account, phone_number=TEST_PHONE_NUMBER1)

        self._assert_simple_phone_securified(account)

    @raises(YaSmsSecureNumberNotAllowed)
    def test_phonish(self):
        self._given(account__exists=False)
        account = self._build_phonish_account(crypt_password=None)

        save_secure_phone = self._build_save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
        )
        save_secure_phone.submit()

    def test_save_clean_phone__account_is_new(self):
        self._given(account__exists=False, create_pwd_hash__requested=True)

        with self._create_account() as account:
            save_secure_phone = self._build_save_secure_phone(
                account=account,
                phone_number=TEST_PHONE_NUMBER1,
                is_new_account=True,
            )
            save_secure_phone.submit()
            save_secure_phone.commit()
        save_secure_phone.after_commit()

        self._assert_secure_phone_bound(
            account,
            is_new_phone=self.is_new_phone,
            with_operation=False,
        )

    def test_aliasify__no_prev_owner__account_is_new(self):
        self._given(
            account__exists=False,
            prev_alias_owner__userinfo__requested=True,
            create_pwd_hash__requested=True,
        )

        with self._create_account() as account:
            save_secure_phone = self._build_save_secure_phone(
                account=account,
                phone_number=TEST_PHONE_NUMBER1,
                aliasify=True,
                is_new_account=True,
            )
            save_secure_phone.submit()
            save_secure_phone.commit()
        save_secure_phone.after_commit()

        self._assert_secure_phone_bound(account, is_new_phone=self.is_new_phone, with_operation=False)
        self._assert_phonenumber_alias_given_out(account, is_new_account=True)

    def test_aliasify__has_prev_owner__account_is_new(self):
        self._given(
            account__exists=False,
            prev_alias_owner__userinfo__requested=True,
            prev_alias_owner__exists=True,
            create_pwd_hash__requested=True,
        )

        with self._create_account() as account:
            save_secure_phone = self._build_save_secure_phone(
                account=account,
                phone_number=TEST_PHONE_NUMBER1,
                aliasify=True,
                is_new_account=True,
            )
            save_secure_phone.submit()
            save_secure_phone.commit()
        save_secure_phone.after_commit()

        self._assert_secure_phone_bound(account, is_new_phone=True, with_operation=False)
        self._assert_phonenumber_alias_given_out(account, is_owner_changed=True, is_new_account=True)
        self._assert_phonenumber_alias_taken_away()

    def test_phone_bindings_history_request(self):
        account = self._given(bindings_history__requested=True)

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
        )

        self._assert_secure_phone_bound(account, is_new_phone=True)

        request = self.env.blackbox.requests[0]
        request.assert_query_contains({
            'method': 'phone_bindings',
            'type': 'history',
            'ignorebindlimit': '0',
            'numbers': TEST_PHONE_NUMBER1.e164,
        })

    def test_dont_wash_account__no_binding(self):
        self._given(account__exists=False)

        account = self._build_account(
            **deep_merge(
                {'karma': '1100'},
                build_phone_bound(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164),
            )
        )

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
        )

        self._assert_simple_phone_securified(account)
        self._assert_karma_prefix_equals(account, TEST_UID1, 1)

    def test_dont_wash_account__dirty_phone(self):
        self._given(
            account__exists=False,
            history_binding__exists=True,
            bindings_history__requested=True,
        )
        account = self._build_account(karma='1100')

        self._save_secure_phone(account=account, phone_number=TEST_PHONE_NUMBER1)

        self._assert_secure_phone_bound(
            account,
            is_new_phone=True,
            operation_id=self.operation_id,
        )
        self._assert_karma_prefix_equals(account, TEST_UID1, 1)

    def test_bind_silently(self):
        account = self._given(bindings_history__requested=True)

        self._save_secure_phone(account=account, phone_number=TEST_PHONE_NUMBER1)

        self._assert_secure_phone_bound(
            account,
            is_new_phone=True,
            operation_id=self.operation_id,
        )
        eq_(self.env.mailer.message_count, 0)

    def test_aliasify__search_disabled(self):
        account = self._given(
            prev_alias_owner__userinfo__requested=True,
            bindings_history__requested=True,
        )

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
            enable_search_alias=False,
        )

        self._assert_phonenumber_alias_given_out(account, enable_search=False)

    def test_aliasify__not_take_busy_alias__alias_occupied(self):
        account = self._given(
            prev_alias_owner__userinfo__requested=True,
            prev_alias_owner__exists=True,
            bindings_history__requested=True,
        )

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
            allow_to_take_busy_alias_from_any_account=False,
        )

        self._assert_secure_phone_bound(account)
        assert_account_has_phonenumber_alias(self.env.db, TEST_UID2, TEST_PHONE_NUMBER1.digital)
        assert_phonenumber_alias_missing(self.env.db, account.uid)

    def test_aliasify__take_busy_alias__alias_free(self):
        account = self._given(
            prev_alias_owner__userinfo__requested=True,
            bindings_history__requested=True,
        )

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
            allow_to_take_busy_alias_from_any_account=False,
        )

        self._assert_phonenumber_alias_given_out(account)

    def test_aliasify__not_take_busy_alias__alias_belongs_to_neophonish(self):
        account = self._given(
            prev_alias_owner__userinfo__requested=True,
            prev_alias_owner__exists=True,
            prev_alias_owner__primary_alias_type='neophonish',
            bindings_history__requested=True,
        )

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
            allow_to_take_busy_alias_from_any_account=False,
        )

        self._assert_secure_phone_bound(account)
        assert_account_has_phonenumber_alias(self.env.db, TEST_UID2, TEST_PHONE_NUMBER1.digital)
        assert_phonenumber_alias_missing(self.env.db, account.uid)

    def test_aliasify__take_busy_alias__alias_belongs_to_neophonish(self):
        account = self._given(
            prev_alias_owner__userinfo__requested=True,
            prev_alias_owner__exists=True,
            prev_alias_owner__primary_alias_type='neophonish',
            bindings_history__requested=True,
        )

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
            allow_to_take_busy_alias_from_any_account=False,
            allow_to_take_busy_alias_from_neophonish=True,
        )

        self._assert_phonenumber_alias_given_out(account, is_owner_changed=True)

    def test_aliasify__not_take_busy_alias__search_alias_enabled(self):
        account = self._given(
            prev_alias_owner__userinfo__requested=True,
            prev_alias_owner__exists=True,
            bindings_history__requested=True,
        )

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
            allow_to_take_busy_alias_from_any_account=False,
            allow_to_take_busy_alias_if_not_search=True,
        )

        self._assert_secure_phone_bound(account)
        assert_account_has_phonenumber_alias(self.env.db, TEST_UID2, TEST_PHONE_NUMBER1.digital)
        assert_phonenumber_alias_missing(self.env.db, account.uid)

    def test_aliasify__take_busy_alias__search_alias_disabled(self):
        account = self._given(
            prev_alias_owner__userinfo__requested=True,
            prev_alias_owner__exists=True,
            prev_alias_owner__search_alias_enabled=False,
            bindings_history__requested=True,
        )

        self._save_secure_phone(
            account=account,
            phone_number=TEST_PHONE_NUMBER1,
            aliasify=True,
            allow_to_take_busy_alias_from_any_account=False,
            allow_to_take_busy_alias_if_not_search=True,
        )

        self._assert_phonenumber_alias_given_out(account, is_owner_changed=True)

    @contextmanager
    def _create_account(self):
        with CREATE(
            default_account(
                TEST_LOGIN1,
                TEST_DATETIME1,
                {
                    'password': TEST_PASSWORD1,
                    'quality': TEST_PASSWORD_QUALITY1,
                    'firstname': TEST_FIRSTNAME1,
                },
                build_default_person_registration_info(TEST_USER_IP1),
            ),
            TEST_ENV1,
            {'action': TEST_ACTION1, 'consumer': TEST_CONSUMER1},
        ) as account:
            account.emails = build_emails([{
                'native': True,
                'validated': True,
                'rpop': False,
                'unsafe': False,
                'default': True,
                'silent': False,
                'address': TEST_EMAIL1,
            }])
            account.emails.parent = account
            yield account
