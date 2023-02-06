# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)
import json

from nose.tools import (
    eq_,
    istest,
    nottest,
    ok_,
)
from passport.backend.api.test.emails import (
    assert_user_notified_about_alias_as_login_and_email_disabled,
    assert_user_notified_about_alias_as_login_and_email_enabled,
    assert_user_notified_about_alias_as_login_disabled,
    assert_user_notified_about_secure_phone_removal_started_on_passwordless_account,
    assert_user_notified_about_secure_phone_removed_without_quarantine_from_passwordless_account,
)
from passport.backend.api.test.mixins import AccountModificationNotifyTestMixin
from passport.backend.api.tests.views.bundle.mixins.account import GetAccountBySessionOrTokenMixin
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AUTH_HEADER,
    TEST_OAUTH_SCOPE,
    TEST_OPERATION_ID,
    TEST_PASSWORD_HASH,
    TEST_PHONE_CREATED_DT,
    TEST_PHONE_NUMBER,
    TEST_PORTAL_ALIAS_TYPE,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.api.views.bundle.phone.helpers import dump_number
from passport.backend.api.views.bundle.phone.manage.base import Confirmation
from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_phone_bindings_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.conf import settings
from passport.backend.core.models.phones.faker import (
    assert_account_has_phonenumber_alias,
    assert_no_default_phone_chosen,
    assert_no_phone_in_db,
    assert_no_secure_phone,
    assert_phone_has_been_bound,
    assert_phonenumber_alias_missing,
    assert_phonenumber_alias_removed,
    assert_secure_phone_being_removed,
    assert_secure_phone_being_replaced,
    assert_secure_phone_bound,
    assert_simple_phone_replace_secure,
    build_account,
    build_account_from_session,
    build_aliasify_secure_operation,
    build_current_phone_binding,
    build_dealiasify_secure_operation,
    build_phone_being_bound,
    build_phone_being_bound_replaces_secure_operations,
    build_phone_bound,
    build_phone_secured,
    build_phone_unbound,
    build_remove_operation,
    build_secure_phone_being_bound,
    build_securify_operation,
    build_simple_replaces_secure_operations,
    build_unbound_phone_binding,
    predict_next_operation_id,
)
from passport.backend.core.models.phones.phones import SECURITY_IDENTITY
from passport.backend.core.serializers.eav.exceptions import EavUpdatedObjectNotFound
from passport.backend.core.test.events import EventCompositor
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.bit_vector.bit_vector import PhoneOperationFlags
from passport.backend.core.yasms.test import (
    emails as email_notifications,
    sms as sms_notifications,
)
from passport.backend.core.yasms.test.emails import (
    assert_user_notified_about_realiasify,
    assert_user_notified_about_secure_phone_bound,
    assert_user_notified_about_secure_phone_removed_without_quarantine,
    assert_user_notified_about_secure_phone_replaced,
)
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)
from passport.backend.utils.time import datetime_to_integer_unixtime as to_unixtime

from .base import PhoneManageBaseTestCase
from .base_test_data import (
    TEST_CONFIRMATION_CODE,
    TEST_EMAIL,
    TEST_EMAIL2,
    TEST_FIRSTNAME,
    TEST_FIRSTNAME2,
    TEST_LOGIN,
    TEST_LOGIN2,
    TEST_MARK_OPERATION_TTL,
    TEST_OP_CODE_LAST_SENT_DT,
    TEST_OPERATION_TTL,
    TEST_PHONE_BOUND_DT,
    TEST_PHONE_ID,
    TEST_PHONE_ID_EXTRA,
    TEST_REPLACEMENT_PHONE_ID,
    TEST_REPLACEMENT_PHONE_NUMBER,
    TEST_SECURE_PHONE_ID,
    TEST_SECURE_PHONE_NUMBER,
    TEST_SOCIAL_LOGIN,
    TEST_UID2,
)


TEST_OPERATION_CONFIRMED = TEST_PHONE_CREATED_DT + timedelta(hours=1)
TEST_OPERATION_ID_EXTRA = 500
TEST_PUBLIC_NAME = 'public name'


@nottest
class CommitBaseTestCase(PhoneManageBaseTestCase, AccountModificationNotifyTestMixin):
    base_request_args = {'operation_id': TEST_OPERATION_ID}
    step = 'commit'
    with_check_cookies = True

    def setUp(self):
        super(CommitBaseTestCase, self).setUp()
        self.env.statbox.bind_entry(
            'phone_operation_applied',
            operation_id=str(TEST_OPERATION_ID),
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
            ip=TEST_USER_IP,
            mode=self.mode,
            step=self.step,
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_search_enabled',
            ip=TEST_USER_IP,
        )
        self.start_account_modification_notify_mocks(ip=TEST_USER_IP)
        self.setup_kolmogor()

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        super(CommitBaseTestCase, self).tearDown()

    def assert_response_ok(self, rv):
        eq_(rv.status_code, 200)
        data = json.loads(rv.data)

        eq_(data['status'], 'ok')
        eq_(data['track_id'], self.track_id)
        eq_(data['phone'], {
            'number': dump_number(TEST_PHONE_NUMBER),
            'id': 1,
        })
        ok_('account' in data)

    def set_blackbox_response(self, scope=TEST_OAUTH_SCOPE, phones=None, operations=None, account_attributes=None,
                              password_is_set=True, login=TEST_LOGIN, alias_type=TEST_PORTAL_ALIAS_TYPE,
                              phonenumber_alias=None, karma='6000', public_name=TEST_PUBLIC_NAME):
        if phones is None:
            phones = [self.phone]

        phone_bindings = list()
        for phone in phones:
            if phone.get('bound'):
                binding = build_current_phone_binding(phone['id'], phone['number'], phone['bound'])
            else:
                binding = build_unbound_phone_binding(phone['id'], phone['number'])
            phone_bindings.append(binding)

        if operations is None:
            operations = [self.operation]

        if account_attributes is None:
            account_attributes = dict()

        if phones[0].get('secured'):
            account_attributes['phones.secure'] = phones[0]['id']

        args = {
            'aliases': {
                alias_type: login,
            },
        }
        if phonenumber_alias is not None:
            args['aliases']['phonenumber'] = phonenumber_alias
            account_attributes.setdefault('account.enable_search_by_phone_alias', '1')

        emails = [
            self.env.email_toolkit.create_native_email(
                login=TEST_EMAIL.split(u'@')[0],
                domain=TEST_EMAIL.split(u'@')[1],
            ),
        ]
        bb_kwargs = {
            'login': login,
            'emails': emails,
            'firstname': TEST_FIRSTNAME,
            'phones': phones,
            'phone_bindings': phone_bindings,
            'phone_operations': operations,
            'attributes': account_attributes,
            'crypt_password': '1:pass' if password_is_set else None,
            'karma': karma,
            'public_name': public_name,
        }

        sessionid_data = blackbox_sessionid_multi_response(
            have_password=password_is_set,
            **merge_dicts(bb_kwargs, args)
        )

        self.env.db.serialize_sessionid(sessionid_data)

        self.env.blackbox.set_response_value(
            'sessionid',
            sessionid_data,
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=scope,
                **merge_dicts(bb_kwargs, args)
            ),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK'])

    def _assert_events_are_ok(self, op_type, is_secure=False,
                              phoneid=TEST_PHONE_ID, number=TEST_PHONE_NUMBER,
                              secure_phone_id=None, became_bound=True,
                              confirmed=None,
                              expect_parsed_event=None):
        phone_key = 'phone.%s.' % phoneid
        phone_operation_key = '%soperation.%s.' % (phone_key, TEST_OPERATION_ID)
        security_identity = '1' if is_secure else str(int(number))
        if confirmed is None:
            confirmed = TimeNow()
        else:
            confirmed = str(to_unixtime(confirmed))
        historydb_entries = {
            phone_key + 'confirmed': confirmed,
            phone_key + 'number': number.e164,
            phone_key + 'action': 'changed',
            phone_operation_key + 'action': 'deleted',
            phone_operation_key + 'type': op_type,
            phone_operation_key + 'security_identity': security_identity,
            'action': self.action,
            'consumer': 'dev',
            'user_agent': TEST_USER_AGENT,
        }

        if became_bound:
            historydb_entries[phone_key + 'bound'] = TimeNow()

        if secure_phone_id is not None:
            historydb_entries['phones.secure'] = str(secure_phone_id)

        if secure_phone_id is not None:
            historydb_entries[phone_key + 'secured'] = TimeNow()

        self.assert_events_are_logged(self.env.handle_mock, historydb_entries)

        if expect_parsed_event:
            parsed_events = self.env.event_logger.parse_events()
            ok_(parsed_events)
            for event in parsed_events:
                eq_(event._asdict().get('event_type'), expect_parsed_event)

    def _given_track(self, display_language='ru', is_password_verified=False):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.display_language = display_language

            if is_password_verified:
                password_verification = Confirmation(
                    logical_operation_id=TEST_OPERATION_ID,
                    phone_id=TEST_PHONE_ID,
                    password_verified=datetime.now(),
                )
                track.phone_operation_confirmations.append(password_verification.to_json())

    def _assert_user_notified_about_aliasify(self, language='ru'):
        assert_user_notified_about_alias_as_login_and_email_enabled(
            self.env.mailer,
            language,
            TEST_EMAIL,
            TEST_FIRSTNAME,
            TEST_LOGIN,
            TEST_EMAIL,
            TEST_PHONE_NUMBER.digital,
        )

    def _test_error_phone_not_confirmed(self):
        """
        В операции нет отметки о том, что был успешно введен код из СМС.
        """
        self.set_blackbox_response(operations=[dict(self.operation, code_confirmed=None)])

        rv = self.make_request()
        self.assert_error_response(rv, ['phone.not_confirmed', 'phone.not_confirmed(%d)' % TEST_PHONE_ID])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('submitted', operation_id=str(TEST_OPERATION_ID)),
        ])

    def _test_error_phone_already_bound(self):
        """
        Телефон уже привязан.
        """
        self.set_blackbox_response(phones=[dict(self.phone, bound=datetime(2000, 1, 2, 12, 34, 56))])

        rv = self.make_request()
        self.assert_error_response(rv, ['phone.bound'])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('submitted', operation_id=str(TEST_OPERATION_ID)),
        ])

    def _test_error_phone_not_bound(self):
        """
        Телефон ещё не привязан.
        """
        self.set_blackbox_response(phones=[dict(self.phone, bound=None)])

        rv = self.make_request()
        self.assert_error_response(rv, ['phone.not_found'])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('submitted', operation_id=str(TEST_OPERATION_ID)),
        ])

    def _test_error_operation_invalid_type(
        self, operation_type='remove',
        security_identity=1, submitted_first=False,
    ):
        """
        Передаем id существующей операции, но с неправильным типом.
        Тест нужно добавить для всех ручек, принимающих operation_id.

        Замечания
            Сюда нужно передавать данные операций, которые действительно можно
            создать.
            На операции, которые не должны быть созданы мы должны отвечать
            UnhandledException и писать об этом в журнал.
        """
        self.set_blackbox_response(
            operations=[dict(self.operation, type=operation_type, security_identity=security_identity)],
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['operation.invalid_state'])

        entries = []
        if self.with_check_cookies:
            if submitted_first:
                entries.append(self.env.statbox.entry('submitted', operation_id=str(TEST_OPERATION_ID)))
                entries.append(self.env.statbox.entry('check_cookies'))
            else:
                entries.append(self.env.statbox.entry('check_cookies'))
                entries.append(self.env.statbox.entry('submitted', operation_id=str(TEST_OPERATION_ID)))
        else:
            entries.append(self.env.statbox.entry('submitted', operation_id=str(TEST_OPERATION_ID)))

        self.env.statbox.assert_has_written(entries)

    def _test_error_operation_invalid_security_identity__secure(self):
        """
        Ручка должна работать с обычным телефоном, но ей дали операцию над защищенным телефоном.
        """
        self.set_blackbox_response(operations=[dict(self.operation, security_identity=SECURITY_IDENTITY)])

        rv = self.make_request()
        self.assert_error_response(rv, ['operation.invalid_state'])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('submitted', operation_id=str(TEST_OPERATION_ID)),
        ])

    def _test_error_operation_invalid_security_identity__not_secure(self):
        """
        Ручка должна работать с защищенным телефоном, но ей дали операцию над обычным телефоном.
        """
        self.set_blackbox_response(operations=[dict(self.operation, security_identity=int(TEST_PHONE_NUMBER))])

        rv = self.make_request()
        self.assert_error_response(rv, ['operation.invalid_state'])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('submitted', operation_id=str(TEST_OPERATION_ID)),
        ])

    def test_error_operation_expired(self):
        # Время жизни операции вышло.
        self.set_blackbox_response(operations=[dict(self.operation, finished=datetime.now())])
        rv = self.make_request()
        self.assert_error_response(rv, ['operation.expired'])

    def _test_error_no_secure_phone(self):
        args = build_phone_bound(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164)
        phone = args['phones'][0]
        self.set_blackbox_response(phones=[phone])

        rv = self.make_request()

        self.assert_error_response(rv, ['phone_secure.not_found'])

    def _assert_user_notified_about_alias_as_login_and_email_disabled(self, language=u'ru'):
        assert_user_notified_about_alias_as_login_and_email_disabled(
            mailer_faker=self.env.mailer,
            language=language,
            email_address=TEST_EMAIL,
            firstname=TEST_FIRSTNAME,
            login=TEST_LOGIN,
            portal_email=TEST_EMAIL,
            phonenumber_alias=TEST_PHONE_NUMBER.digital,
        )

    def _assert_user_notified_about_alias_as_login_disabled(self):
        assert_user_notified_about_alias_as_login_disabled(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_EMAIL,
            firstname=TEST_FIRSTNAME,
            login=TEST_LOGIN,
            portal_email=TEST_EMAIL,
            phonenumber_alias=TEST_PHONE_NUMBER.digital,
        )

    def _assert_user_notified_about_realiasify(self, language='ru'):
        assert_user_notified_about_realiasify(
            self.env.mailer,
            language,
            TEST_EMAIL2,
            TEST_FIRSTNAME2,
            TEST_LOGIN2,
            TEST_EMAIL2,
            TEST_PHONE_NUMBER.digital,
        )

    def _assert_user_notified_about_secure_phone_removed(
        self,
        language=u'ru',
        login=TEST_LOGIN,
    ):
        assert_user_notified_about_secure_phone_removed_without_quarantine(
            mailer_faker=self.env.mailer,
            language=language,
            email_address=TEST_EMAIL,
            firstname=TEST_FIRSTNAME,
            login=login,
        )

    def _assert_user_notified_about_secure_phone_removed_from_passwordless_account(
        self,
        language=u'ru',
    ):
        assert_user_notified_about_secure_phone_removed_without_quarantine_from_passwordless_account(
            mailer_faker=self.env.mailer,
            language=language,
            email_address=TEST_EMAIL,
            firstname=TEST_FIRSTNAME,
            login=TEST_FIRSTNAME,
        )

    def _test_error_password_not_verified(self):
        self.set_blackbox_response(operations=[dict(self.operation, password_verified=None)])

        rv = self.make_request()
        self.assert_error_response(rv, ['password.not_confirmed'])


@with_settings_hosts(
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'phone_change'},
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:phone_change': 5,
        },
    )
)
@istest
class TestBindSimplePhoneCommit(CommitBaseTestCase, GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/bind_simple/commit/'
    action = 'simple_bind_commit'
    mode = 'simple_bind'
    with_check_cookies = True

    def setUp(self):
        super(TestBindSimplePhoneCommit, self).setUp()

        self.phone = {
            'number': TEST_PHONE_NUMBER.e164,
            'id': TEST_PHONE_ID,
            'created': TEST_PHONE_CREATED_DT,
        }

        self.operation = {
            'id': TEST_OPERATION_ID,
            'type': 'bind',
            'security_identity': int(TEST_PHONE_NUMBER),
            'phone_id': TEST_PHONE_ID,
            'code_confirmed': TEST_OPERATION_CONFIRMED,
            'started': DatetimeNow(),
            'finished': DatetimeNow() + TEST_OPERATION_TTL,
        }

    def _test_ok(
        self, by_token=False,
        alias_type=TEST_PORTAL_ALIAS_TYPE, login=TEST_LOGIN,
        push_login=None
    ):
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self.set_blackbox_response(alias_type=alias_type, login=login)

        rv = self.make_request(headers=headers)
        self.assert_response_ok(rv)
        self._assert_events_are_ok('bind', confirmed=TEST_OPERATION_CONFIRMED)

        self.check_db_phone_attr('bound', TimeNow())
        self.check_db_phone_attr(
            'confirmed',
            str(to_unixtime(TEST_OPERATION_CONFIRMED)),
        )

        self.env.db.check_missing('attributes', 'phones.secure', uid=TEST_UID, db='passportdbshard1')

        self.check_db_phone_operation_missing(TEST_OPERATION_ID)

        entries = []
        if self.with_check_cookies and not by_token:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry('submitted', operation_id=str(TEST_OPERATION_ID)),
            self.env.statbox.entry('simple_phone_bound'),
            self.env.statbox.entry('completed'),
        ])
        self.env.statbox.assert_has_written(entries)
        self.assert_blackbox_auth_method_ok(by_token)
        self.assert_account_history_parses_phone_bind(TEST_PHONE_NUMBER)
        self.check_account_modification_push_sent(
            ip=TEST_USER_IP,
            event_name='phone_change',
            uid=TEST_UID,
            title='В аккаунте {} изменён номер телефона'.format(push_login or login),
            body='Если это вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
        )

    def test_bad_phone_history__not_wash_karma(self):
        self.set_blackbox_response(karma='1100')
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    'type': 'history',
                    'number': TEST_PHONE_NUMBER.e164,
                    'bound': datetime(2000, 1, 1),
                },
                {
                    'type': 'history',
                    'number': TEST_PHONE_NUMBER.e164,
                    'bound': datetime(2000, 1, 2),
                },
            ]),
        )

        rv = self.make_request()

        self.assert_response_ok(rv)
        self.env.db.check('attributes', 'karma.value', '1100', uid=TEST_UID, db='passportdbshard1')

    def test_already_washed_karma__not_wash_karma(self):
        headers = self.build_headers(**dict(cookie=TEST_USER_COOKIE))
        self.set_blackbox_response(karma='2000')

        rv = self.make_request(headers=headers)
        self.assert_response_ok(rv)
        self.env.db.check('attributes', 'karma.value', '2000', uid=TEST_UID, db='passportdbshard1')

    def test_ok_by_session(self):
        self._test_ok()

    def test_ok_by_token(self):
        self._test_ok(by_token=True)

    def test_ok_with_existing_track(self):
        self._test_ok_with_existing_track()
        self.assert_account_history_parses_phone_bind(TEST_PHONE_NUMBER)

    def test_error_operation_not_found(self):
        self._test_error_operation_not_found()

    def test_error_operation_invalid_type(self):
        self._test_error_operation_invalid_type()

    def test_error_phone_not_confirmed(self):
        self._test_error_phone_not_confirmed()

    def test_error_operation_invalid_security_identity__secure(self):
        self._test_error_operation_invalid_security_identity__secure()

    def test_error_phone_already_bound(self):
        self._test_error_phone_already_bound()

    def test_error_account_disabled(self):
        self._test_error_account_disabled()

    def test_error_account_disabled_on_deletion(self):
        self._test_error_account_disabled_on_deletion()

    def test_ok_account_without_password(self):
        self._test_ok_account_without_password()
        self.assert_account_history_parses_phone_bind(TEST_PHONE_NUMBER)

    def test_social_ok(self):
        self._test_ok(
            alias_type='social',
            login=TEST_SOCIAL_LOGIN,
            push_login=TEST_PUBLIC_NAME,
        )


@with_settings_hosts(
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'phone_change'},
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:phone_change': 5,
        },
    )
)
@istest
class TestBindSecurePhoneCommit(CommitBaseTestCase, GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/bind_secure/commit/'
    action = 'secure_bind_commit'
    mode = 'secure_bind'
    with_check_cookies = True

    def setUp(self):
        super(TestBindSecurePhoneCommit, self).setUp()

        self.phone = {
            'number': TEST_PHONE_NUMBER.e164,
            'id': TEST_PHONE_ID,
            'created': TEST_PHONE_CREATED_DT,
        }

        self.operation = {
            'id': TEST_OPERATION_ID,
            'type': 'bind',
            'security_identity': SECURITY_IDENTITY,
            'phone_id': TEST_PHONE_ID,
            'code_confirmed': TEST_OPERATION_CONFIRMED,
            'password_verified': TEST_OPERATION_CONFIRMED,
            'started': DatetimeNow(),
            'finished': DatetimeNow() + TEST_OPERATION_TTL,
        }

    def _test_ok(self, by_token=False, alias_type=TEST_PORTAL_ALIAS_TYPE, login=TEST_LOGIN, with_check_cookies=False):
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self.set_blackbox_response(alias_type=alias_type, login=login)

        rv = self.make_request(headers=headers)
        self.assert_response_ok(rv)
        self._assert_events_are_ok(
            'bind',
            is_secure=True,
            secure_phone_id=TEST_PHONE_ID,
            confirmed=TEST_OPERATION_CONFIRMED,
            expect_parsed_event='secure_phone_set',
        )

        self.check_db_phone_attr('bound', TimeNow())
        self.check_db_phone_attr(
            'confirmed',
            str(to_unixtime(TEST_OPERATION_CONFIRMED)),
        )
        self.check_db_phone_attr('secured', TimeNow())
        self.env.db.check('attributes', 'phones.secure', str(TEST_PHONE_ID), uid=TEST_UID, db='passportdbshard1')

        self.check_db_phone_operation_missing(TEST_OPERATION_ID)

        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry('submitted', operation_id=str(TEST_OPERATION_ID)),
            self.env.statbox.entry('account_phones_secure'),
            self.env.statbox.entry('secure_phone_bound'),
            self.env.statbox.entry('completed'),
        ])

        self.env.statbox.assert_has_written(entries)
        self.assert_blackbox_auth_method_ok(by_token)
        self.assert_account_history_parses_secure_phone_set(TEST_PHONE_NUMBER)

    def test_ok_by_session(self):
        self._test_ok(with_check_cookies=True)

    def test_ok_by_token(self):
        self._test_ok(by_token=True)

    def test_ok_with_existing_track(self):
        self._test_ok_with_existing_track()

    def test_error_operation_not_found(self):
        self._test_error_operation_not_found()

    def test_error_operation_invalid_type(self):
        self._test_error_operation_invalid_type()

    def test_error_phone_not_confirmed(self):
        self._test_error_phone_not_confirmed()

    def test_error_operation_invalid_security_identity__not_secure(self):
        self._test_error_operation_invalid_security_identity__not_secure()

    def test_secure_phone_already_exists(self):
        """
        У пользователя уже есть защищенный телефон.
        """
        self.set_blackbox_response(
            account_attributes={'phones.secure': TEST_PHONE_ID},
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['phone_secure.already_exists'])

    def test_error_password_not_verified(self):
        self._test_error_password_not_verified()

    def test_error_phone_already_bound(self):
        self._test_error_phone_already_bound()

    def test_error_account_disabled(self):
        self._test_error_account_disabled()

    def test_aliasify__free_alias(self):
        flags = PhoneOperationFlags()
        flags.aliasify = True
        self.set_blackbox_response(operations=[dict(self.operation, flags=flags)])

        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([{'uid': None}]),
        )

        rv = self.make_request()

        self.assert_response_ok(rv)
        assert_account_has_phonenumber_alias(self.env.db, TEST_UID, TEST_PHONE_NUMBER.digital)
        self._assert_user_notified_about_aliasify()

    def test_aliasify__occupied_alias(self):
        flags = PhoneOperationFlags()
        flags.aliasify = True
        self.set_blackbox_response(operations=[dict(self.operation, flags=flags)])

        emails = [
            self.env.email_toolkit.create_native_email(
                login=TEST_EMAIL2.split(u'@')[0],
                domain=TEST_EMAIL2.split(u'@')[1],
            ),
        ]
        build_account(
            blackbox_faker=self.env.blackbox,
            db_faker=self.env.db,
            **deep_merge(
                dict(
                    uid=TEST_UID2,
                    login=TEST_LOGIN2,
                    firstname=TEST_FIRSTNAME2,
                    emails=emails,
                    aliases={'portal': TEST_LOGIN2},
                ),
                build_phone_secured(
                    TEST_PHONE_ID_EXTRA,
                    TEST_PHONE_NUMBER.e164,
                    is_alias=True,
                ),
            )
        )

        rv = self.make_request()

        self.assert_response_ok(rv)

        assert_account_has_phonenumber_alias(self.env.db, TEST_UID, TEST_PHONE_NUMBER.digital)
        self._assert_user_notified_about_aliasify()

        assert_phonenumber_alias_missing(self.env.db, TEST_UID2)
        assert_phonenumber_alias_removed(self.env.db, TEST_UID2, TEST_PHONE_NUMBER.digital)
        self._assert_user_notified_about_realiasify()

    def test_email_notification(self):
        self._build_account(
            **build_secure_phone_being_bound(
                TEST_PHONE_ID,
                TEST_PHONE_NUMBER.e164,
                TEST_OPERATION_ID,
                code_confirmed=datetime.now(),
                password_verified=datetime.now(),
            )
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        rv = self.make_request()

        self.assert_response_ok(rv)
        assert_user_notified_about_secure_phone_bound(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_EMAIL,
            firstname=TEST_FIRSTNAME,
            login=TEST_LOGIN,
        )

    def test_race_conditions_occurred__error_masked(self):
        self._build_account(
            **build_secure_phone_being_bound(
                TEST_PHONE_ID,
                TEST_PHONE_NUMBER.e164,
                TEST_OPERATION_ID,
                code_confirmed=datetime.now(),
                password_verified=datetime.now(),
            )
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.db.set_side_effect_for_db(
            'passportdbshard1',
            EavUpdatedObjectNotFound,
        )
        rv = self.make_request()

        self.assert_error_response(rv, ['internal.temporary'])

    def test_social_ok(self):
        self._test_ok(alias_type='social', login=TEST_SOCIAL_LOGIN, with_check_cookies=True)

    def test_ok_account_without_password(self):
        self._test_ok_account_without_password()

    def test_passwordless_account(self):
        self.operation['password_verified'] = None
        self.set_blackbox_response(
            login=TEST_SOCIAL_LOGIN,
            alias_type='social',
            password_is_set=False,
        )

        rv = self.make_request()

        self.assert_response_ok(rv)

        assert_secure_phone_bound.check_db(
            self.env.db,
            TEST_UID,
            phone_attributes=dict(
                id=TEST_PHONE_ID,
                number=TEST_PHONE_NUMBER.e164,
            ),
        )

        self._assert_events_are_ok(
            'bind',
            is_secure=True,
            secure_phone_id=TEST_PHONE_ID,
            confirmed=TEST_OPERATION_CONFIRMED,
            expect_parsed_event='secure_phone_set',
        )

        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry('check_cookies'),
                self.env.statbox.entry('submitted', operation_id='1'),
                self.env.statbox.entry('account_phones_secure'),
                self.env.statbox.entry('secure_phone_bound'),
                self.env.statbox.entry('completed'),
            ],
        )

    def test_aliasify__passwordless_account(self):
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.aliasify = True
        self.operation['flags'] = phone_operation_flags
        self.operation['password_verified'] = None
        self.set_blackbox_response(
            login=TEST_SOCIAL_LOGIN,
            alias_type='social',
            password_is_set=False,
        )

        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([{'uid': None}]),
        )

        rv = self.make_request()

        self.assert_response_ok(rv)
        assert_account_has_phonenumber_alias(
            self.env.db,
            TEST_UID,
            TEST_PHONE_NUMBER.digital,
            enable_search=False,
        )


@with_settings_hosts(
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'phone_change'},
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:phone_change': 5,
        },
    )
)
@istest
class TestSecurifyCommit(CommitBaseTestCase, GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/securify/commit/'
    action = 'securify_commit'
    mode = 'securify'

    def setUp(self):
        super(TestSecurifyCommit, self).setUp()

        self.phone = {
            'number': TEST_PHONE_NUMBER.e164,
            'id': TEST_PHONE_ID,
            'created': TEST_PHONE_CREATED_DT,
            'bound': TEST_PHONE_BOUND_DT,
        }

        self.operation = {
            'id': TEST_OPERATION_ID,
            'type': 'securify',
            'security_identity': SECURITY_IDENTITY,
            'phone_id': TEST_PHONE_ID,
            'code_confirmed': TEST_OPERATION_CONFIRMED,
            'password_verified': TEST_OPERATION_CONFIRMED,
            'started': DatetimeNow(),
            'finished': DatetimeNow() + TEST_OPERATION_TTL,
        }

    def _test_ok(self, by_token=False):
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self.set_blackbox_response()

        rv = self.make_request(headers=headers)
        self.assert_response_ok(rv)
        self._assert_events_are_ok(
            'securify',
            is_secure=True,
            secure_phone_id=TEST_PHONE_ID,
            became_bound=False,
            confirmed=TEST_OPERATION_CONFIRMED,
        )

        self.check_db_phone_attr('bound', str(to_unixtime(self.phone['bound'])))
        self.check_db_phone_attr(
            'confirmed',
            str(to_unixtime(TEST_OPERATION_CONFIRMED)),
        )
        self.check_db_phone_attr('secured', TimeNow())
        self.env.db.check('attributes', 'phones.secure', str(TEST_PHONE_ID), uid=TEST_UID, db='passportdbshard1')

        self.check_db_phone_operation_missing(TEST_OPERATION_ID)

        entries = []
        if not by_token:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend(
            [
                self.env.statbox.entry('submitted', operation_id=str(TEST_OPERATION_ID)),
                self.env.statbox.entry('account_phones_secure'),
                self.env.statbox.entry('phone_secured'),
                self.env.statbox.entry('completed'),
            ]
        )

        self.env.statbox.assert_has_written(entries)
        self.assert_blackbox_auth_method_ok(by_token)
        self.assert_account_history_parses_secure_phone_set(TEST_PHONE_NUMBER)

    def test_ok_by_session(self):
        self._test_ok()

    def test_ok_by_token(self):
        self._test_ok(by_token=True)

    def test_ok_with_existing_track(self):
        self._test_ok_with_existing_track()
        self.assert_account_history_parses_secure_phone_set(TEST_PHONE_NUMBER)

    def test_error_operation_not_found(self):
        self._test_error_operation_not_found()

    def test_error_operation_invalid_type(self):
        self._test_error_operation_invalid_type()

    def test_error_phone_not_confirmed(self):
        self._test_error_phone_not_confirmed()

    def test_error_password_not_verified(self):
        self._test_error_password_not_verified()

    def test_error_phone_not_bound(self):
        self._test_error_phone_not_bound()

    def test_error_account_disabled(self):
        self._test_error_account_disabled()

    def test_error_secure_number_exists(self):
        self._test_error_secure_number_exists()

    def test_ok_account_without_password(self):
        self._test_ok_account_without_password()

    def test_email_notification(self):
        self._build_account(
            **deep_merge(
                build_phone_bound(
                    TEST_PHONE_ID,
                    TEST_PHONE_NUMBER.e164,
                ),
                build_securify_operation(
                    TEST_OPERATION_ID,
                    TEST_PHONE_ID,
                    code_confirmed=datetime.now(),
                    password_verified=datetime.now(),
                ),
            )
        )

        rv = self.make_request()

        self.assert_response_ok(rv)
        assert_user_notified_about_secure_phone_bound(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_EMAIL,
            firstname=TEST_FIRSTNAME,
            login=TEST_LOGIN,
        )

    def test_passwordless_account(self, by_token=False):
        self.operation.update(password_verified=None)
        self.set_blackbox_response(
            alias_type='social',
            login=TEST_SOCIAL_LOGIN,
            password_is_set=False,
        )

        rv = self.make_request()

        self.assert_response_ok(rv)

        assert_secure_phone_bound.check_db(
            self.env.db,
            TEST_UID,
            phone_attributes=dict(
                id=TEST_PHONE_ID,
                number=TEST_PHONE_NUMBER.e164,
            ),
        )


class ReplaceSecurePhoneCommitTestSet(object):
    def test_simple__secure_is_alias(self):
        # В треке верная операция
        # Телефоны подтверждены
        # Пароль проверен
        # Защищённый телефон является алиасом

        self._given_accounts(
            self._build_subject_account_args(is_secure_alias=True, language=u'en'),
        )
        self._given_track()

        rv = self.make_request()

        self.assert_response_ok(rv)
        self._assert_db_ok()
        self._assert_events_ok(expect_parsed_event='secure_phone_replace')
        self._assert_statbox_ok(with_check_cookies=True)
        self._assert_user_notified_about_alias_as_login_and_email_disabled()
        self._assert_user_notified_about_secure_phone_replaced()
        self.assert_account_history_parses_secure_phone_replace(TEST_SECURE_PHONE_NUMBER, TEST_REPLACEMENT_PHONE_NUMBER)

    def test_use_account_language(self):
        self._given_accounts(
            self._build_subject_account_args(is_secure_alias=True, language=u'en'),
        )
        self._given_track(display_language=None)

        rv = self.make_request()

        self.assert_response_ok(rv)

        email_messages = self.env.mailer.messages
        eq_(len(email_messages), 2)
        assert_user_notified_about_alias_as_login_and_email_disabled(
            mailer_faker=self.env.mailer,
            language='en',
            email_address='testuser@yandex-team.ru',
            firstname=u'Василий',
            login='testuser',
            portal_email='testuser@yandex-team.ru',
            phonenumber_alias=TEST_SECURE_PHONE_NUMBER.digital,
        )
        self._assert_user_notified_about_secure_phone_replaced(language=u'en')

    def test_simple__secure_is_not_alias(self):
        # Трека нет
        # Телефоны подтверждены
        # Пароль проверен
        # Защищённый телефон не является алиасом

        self._given_accounts(
            self._build_subject_account_args(is_secure_alias=False),
        )

        rv = self.make_request()

        self.assert_response_ok(rv)
        self._assert_db_ok(was_secure_alias=False)
        self._assert_events_ok(was_secure_alias=False, expect_parsed_event='secure_phone_replace')
        self._assert_statbox_ok(was_secure_alias=False, with_check_cookies=True)
        self._assert_user_notified_about_secure_phone_replaced()
        self.assert_account_history_parses_secure_phone_replace(TEST_SECURE_PHONE_NUMBER, TEST_REPLACEMENT_PHONE_NUMBER)

    def test_error_operation_expired(self):
        # Телефоны подтверждены
        # Пароль проверен
        # Операция протухла

        started = datetime.now() - timedelta(hours=24 * 60)
        finished = datetime.now() - timedelta(hours=1)
        self._given_accounts(
            self._build_subject_account_args(operation_started=started, operation_finished=finished),
        )
        self._given_track()

        rv = self.make_request()

        self.assert_error_response(rv, [u'operation.expired'])
        self.assert_events_are_logged(self.env.handle_mock, [])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('submitted', track_id=self.track_id, operation_id=str(TEST_OPERATION_ID)),
        ])
        eq_(self.env.mailer.messages, [])

    def test_phones_not_confirmed__password_not_verified(self):
        self._given_accounts(
            self._build_subject_account_args(
                is_secure_confirmed=False,
                is_replacement_confirmed=False,
                is_password_verified=False,
            ),
        )
        self._given_track()

        rv = self.make_request()

        self.assert_error_response(
            rv,
            [
                u'password.not_confirmed',
                u'phone.not_confirmed',
                u'phone.not_confirmed(%d)' % TEST_SECURE_PHONE_ID,
                u'phone.not_confirmed(%d)' % TEST_REPLACEMENT_PHONE_ID,
            ],
        )
        self.assert_events_are_logged(self.env.handle_mock, [])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('submitted', track_id=self.track_id, operation_id=str(TEST_OPERATION_ID)),
        ])
        eq_(self.env.mailer.messages, [])

    def test_operation_does_not_exist(self):
        self._given_accounts(self._build_subject_account_args())
        self._given_track()

        rv = self.make_request(operation_id=3232)

        self.assert_error_response(rv, [u'operation.not_found'])
        self.assert_events_are_logged(self.env.handle_mock, [])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('submitted', track_id=self.track_id, operation_id='3232'),
        ])
        eq_(self.env.mailer.messages, [])

    def test_ready_for_quarantine(self):
        self._given_accounts(
            self._build_subject_account_args(
                is_secure_confirmed=False,
                secure_code_value=None,
                secure_code_last_sent=None,
            ),
        )
        self._given_track()

        rv = self.make_request()

        self.assert_response_ok(rv, in_quarantine=True)

        quarantine_finished = DatetimeNow(timestamp=datetime.now() + TEST_OPERATION_TTL)
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        assert_secure_phone_being_replaced.check_db(
            self.env.db,
            TEST_UID,
            {
                u'id': TEST_SECURE_PHONE_ID,
            },
            {
                u'finished': quarantine_finished,
                u'flags': phone_operation_flags,
            },
        )

        assert_simple_phone_replace_secure.check_db(
            self.env.db,
            TEST_UID,
            {
                u'id': TEST_REPLACEMENT_PHONE_ID,
            },
            {
                u'finished': quarantine_finished,
                u'flags': phone_operation_flags,
            },
        )

        email_notifications.assert_user_notified_about_secure_phone_replacement_started(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_EMAIL,
            firstname=TEST_FIRSTNAME,
            login=TEST_LOGIN,
        )
        sms_notifications.assert_user_notified_about_secure_phone_replacement_started(
            yasms_builder_faker=self.env.yasms,
            language='ru',
            phone_number=TEST_SECURE_PHONE_NUMBER,
            uid=TEST_UID,
        )
        self.assert_account_history_parses_secure_phone_replace(
            TEST_SECURE_PHONE_NUMBER,
            TEST_REPLACEMENT_PHONE_NUMBER,
            quarantine=TimeNow(offset=settings.PHONE_QUARANTINE_SECONDS),
        )

    def test_in_quarantine(self):
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        phone_operation_finished = datetime.now() + TEST_OPERATION_TTL / 2
        self._given_accounts(
            self._build_subject_account_args(
                is_secure_confirmed=False,
                secure_code_value=None,
                secure_code_last_sent=None,
                operation_finished=phone_operation_finished,
                flags=phone_operation_flags,
            ),
        )
        self._given_track()

        rv = self.make_request()

        self.assert_response_ok(rv, in_quarantine=True)

        assert_secure_phone_being_replaced.check_db(
            self.env.db,
            TEST_UID,
            {
                u'id': TEST_SECURE_PHONE_ID,
            },
            {
                u'finished': phone_operation_finished,
            },
        )

        assert_simple_phone_replace_secure.check_db(
            self.env.db,
            TEST_UID,
            {
                u'id': TEST_REPLACEMENT_PHONE_ID,
            },
            {
                u'finished': phone_operation_finished,
            },
        )

        # Раз карантин был и раньше, значит все уведомления уже высылались и
        # пользователя не надо уведомлять повторно.
        eq_(len(self.env.mailer.messages), 0)
        eq_(len(self.env.yasms.requests), 0)

    def test_start_quarantine(self):
        self._given_accounts(
            self._build_subject_account_args(
                is_secure_confirmed=False,
                secure_code_value=None,
                secure_code_last_sent=None,
                is_password_verified=False,
                is_replacement_confirmed=False,
            ),
        )
        self._given_track(is_password_verified=True, is_replacement_confirmed=True)

        rv = self.make_request()

        self.assert_response_ok(rv, in_quarantine=True)

        quarantine_finished = DatetimeNow(timestamp=datetime.now() + TEST_OPERATION_TTL)
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        assert_secure_phone_being_replaced.check_db(
            self.env.db,
            TEST_UID,
            {u'id': TEST_SECURE_PHONE_ID},
            # Т.к. начался карантин, нужно дать отсрочку на исполнения операции
            {
                u'finished': quarantine_finished,
                u'flags': phone_operation_flags,
            },
        )
        assert_simple_phone_replace_secure.check_db(
            self.env.db,
            TEST_UID,
            {u'id': TEST_REPLACEMENT_PHONE_ID},
            {
                u'finished': quarantine_finished,
                u'flags': phone_operation_flags,
            },
        )

        email_notifications.assert_user_notified_about_secure_phone_replacement_started(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_EMAIL,
            firstname=TEST_FIRSTNAME,
            login=TEST_LOGIN,
        )
        sms_notifications.assert_user_notified_about_secure_phone_replacement_started(
            yasms_builder_faker=self.env.yasms,
            language='ru',
            phone_number=TEST_SECURE_PHONE_NUMBER,
            uid=TEST_UID,
        )
        self.assert_account_history_parses_secure_phone_replace(
            TEST_SECURE_PHONE_NUMBER,
            TEST_REPLACEMENT_PHONE_NUMBER,
            quarantine=TimeNow(offset=settings.PHONE_QUARANTINE_SECONDS),
        )
        self.check_account_modification_push_sent(
            ip=TEST_USER_IP,
            event_name='phone_change',
            uid=TEST_UID,
            title='В аккаунте {} изменён номер телефона'.format(TEST_LOGIN),
            body='Если это вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
        )


class BaseReplaceSecurePhoneCommitTestCase(PhoneManageBaseTestCase, AccountModificationNotifyTestMixin):
    base_method_path = '/1/bundle/phone/manage/replace/commit/'
    mode = 'phone_secure_replace'
    step = 'commit'

    def setUp(self):
        super(BaseReplaceSecurePhoneCommitTestCase, self).setUp()
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.start_account_modification_notify_mocks(ip=TEST_USER_IP)
        self.setup_kolmogor()

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        super(BaseReplaceSecurePhoneCommitTestCase, self).tearDown()

    def set_blackbox_response(self, scope=TEST_OAUTH_SCOPE, **kwargs):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope=scope, **kwargs),
        )

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK', 'OK'])

    def assert_response_ok(self, rv, **kwargs):
        kwargs.setdefault(u'track_id', self.track_id)

        eq_(rv.status_code, 200)
        data = json.loads(rv.data)

        eq_(data[u'status'], u'ok')
        eq_(data[u'track_id'], kwargs[u'track_id'])

        if not kwargs.get(u'in_quarantine'):
            secure_phone = {
                u'id': TEST_REPLACEMENT_PHONE_ID,
                u'number': dump_number(TEST_REPLACEMENT_PHONE_NUMBER),
            }
            eq_(data[u'secure_phone'], secure_phone)
        else:
            secure_phone = {
                u'id': TEST_SECURE_PHONE_ID,
                u'number': dump_number(TEST_SECURE_PHONE_NUMBER),
                u'operation': {
                    u'id': TEST_OPERATION_ID,
                    u'security_identity': SECURITY_IDENTITY,
                    u'in_quarantine': True,
                },
            }
            eq_(data[u'secure_phone'], secure_phone)

        ok_(u'account' in data)

    def make_request(self, headers=None, **kwargs):
        kwargs.setdefault(u'operation_id', TEST_OPERATION_ID)
        return super(BaseReplaceSecurePhoneCommitTestCase, self).make_request(
            headers=headers,
            data=kwargs,
        )

    def _assert_db_ok(self, was_secure_alias=True):
        assert_secure_phone_bound.check_db(
            self.env.db,
            TEST_UID,
            {u'id': TEST_REPLACEMENT_PHONE_ID, u'confirmed': DatetimeNow(), u'secured': DatetimeNow()},
        )
        assert_no_phone_in_db(self.env.db, TEST_UID, TEST_SECURE_PHONE_ID, TEST_SECURE_PHONE_NUMBER.e164)
        self.env.db.check_missing(u'phone_operations', db=u'passportdbshard1', uid=TEST_UID, id=TEST_OPERATION_ID)
        self.env.db.check_missing(
            u'phone_operations',
            db=u'passportdbshard1',
            uid=TEST_UID,
            id=TEST_OPERATION_ID_EXTRA,
        )
        if was_secure_alias:
            assert_phonenumber_alias_removed(self.env.db, TEST_UID, TEST_SECURE_PHONE_NUMBER.digital)
        assert_phone_has_been_bound(self.env.db, TEST_UID, TEST_SECURE_PHONE_NUMBER.e164, times=1)
        assert_phone_has_been_bound(self.env.db, TEST_UID, TEST_REPLACEMENT_PHONE_NUMBER.e164, times=1)

    def _build_events(self, was_secure_alias=True):
        repl = (TEST_REPLACEMENT_PHONE_ID, TEST_OPERATION_ID_EXTRA)
        secure = (TEST_SECURE_PHONE_ID, TEST_OPERATION_ID)
        events = [
            {u'uid': str(TEST_UID), u'name': u'action', u'value': u'phone_secure_replace_commit'},
            {u'uid': str(TEST_UID), u'name': u'consumer', u'value': u'dev'},
            {u'uid': str(TEST_UID), u'name': u'user_agent', u'value': TEST_USER_AGENT},

            {u'uid': str(TEST_UID), u'name': u'phone.%d.action' % TEST_REPLACEMENT_PHONE_ID, u'value': u'changed'},
            {
                u'uid': str(TEST_UID),
                u'name': u'phone.%d.number' % TEST_REPLACEMENT_PHONE_ID,
                u'value': TEST_REPLACEMENT_PHONE_NUMBER.e164,
            },
            {u'uid': str(TEST_UID), u'name': u'phone.%d.secured' % TEST_REPLACEMENT_PHONE_ID, u'value': TimeNow()},
            {u'uid': str(TEST_UID), u'name': u'phone.%d.operation.%d.action' % repl, u'value': u'deleted'},
            {
                u'uid': str(TEST_UID),
                u'name': u'phone.%d.operation.%d.security_identity' % repl,
                u'value': TEST_REPLACEMENT_PHONE_NUMBER.digital,
            },
            {u'uid': str(TEST_UID), u'name': u'phones.secure', u'value': str(TEST_REPLACEMENT_PHONE_ID)},

            {u'uid': str(TEST_UID), u'name': u'phone.%d.action' % TEST_SECURE_PHONE_ID, u'value': u'deleted'},
            {
                u'uid': str(TEST_UID),
                u'name': u'phone.%d.number' % TEST_SECURE_PHONE_ID,
                u'value': TEST_SECURE_PHONE_NUMBER.e164,
            },
            {u'uid': str(TEST_UID), u'name': u'phone.%d.operation.%d.action' % secure, u'value': u'deleted'},
            {u'uid': str(TEST_UID), u'name': u'phone.%d.operation.%d.type' % secure, u'value': u'replace'},
            {u'uid': str(TEST_UID), u'name': u'phone.%d.operation.%d.security_identity' % secure, u'value': u'1'},
        ]
        if was_secure_alias:
            events += [
                {
                    u'uid': str(TEST_UID),
                    u'name': u'alias.phonenumber.rm',
                    u'value': TEST_SECURE_PHONE_NUMBER.international,
                },
            ]
        return events

    def _assert_user_notified_about_secure_phone_replaced(self, language=u'ru'):
        assert_user_notified_about_secure_phone_replaced(
            mailer_faker=self.env.mailer,
            language=language,
            email_address=TEST_EMAIL,
            firstname=TEST_FIRSTNAME,
            login=TEST_LOGIN,
        )

    def _assert_user_notified_about_alias_as_login_and_email_disabled(self, language=u'ru'):
        assert_user_notified_about_alias_as_login_and_email_disabled(
            mailer_faker=self.env.mailer,
            language=language,
            email_address=TEST_EMAIL,
            firstname=TEST_FIRSTNAME,
            login=TEST_LOGIN,
            portal_email=TEST_EMAIL,
            phonenumber_alias=TEST_SECURE_PHONE_NUMBER.digital,
        )

    def _build_subject_account_args(self,
                                    is_secure_confirmed=True,
                                    is_replacement_confirmed=True,
                                    is_password_verified=True,
                                    operation_started=None,
                                    operation_finished=None,
                                    is_secure_alias=False,
                                    language=u'ru',
                                    secure_code_last_sent=TEST_OP_CODE_LAST_SENT_DT,
                                    secure_code_value=TEST_CONFIRMATION_CODE,
                                    flags=None,
                                    alias_type=None,
                                    login=None,
                                    password=Undefined):
        phone_confirm_time = password_verify_time = datetime.now()
        if is_secure_confirmed:
            secure_code_confirmed = phone_confirm_time
        else:
            secure_code_confirmed = None
        if is_replacement_confirmed:
            replacement_code_confirmed = phone_confirm_time
        else:
            replacement_code_confirmed = None
        if is_password_verified:
            password_verified = password_verify_time
        else:
            password_verified = None
        if secure_code_last_sent:
            secure_code_send_count = 1
        else:
            secure_code_send_count = 0

        alias_type = alias_type or 'portal'

        if login is None:
            login = TEST_LOGIN

        if password is Undefined:
            password = TEST_PASSWORD_HASH

        return deep_merge(
            dict(
                uid=TEST_UID,
                crypt_password=password,
                have_password=bool(password),
                firstname=TEST_FIRSTNAME,
                aliases={alias_type: login},
                login=login,
                language=language,
                emails=[
                    self.env.email_toolkit.create_native_email(
                        login=TEST_EMAIL.split(u'@')[0],
                        domain=TEST_EMAIL.split(u'@')[1],
                    ),
                ],
            ),
            build_phone_secured(
                TEST_SECURE_PHONE_ID,
                TEST_SECURE_PHONE_NUMBER.e164,
                phone_confirmed=phone_confirm_time,
                is_alias=is_secure_alias,
            ),
            self._build_replace_operation(
                secure_operation_id=TEST_OPERATION_ID,
                secure_phone_id=TEST_SECURE_PHONE_ID,
                replacement_operation_id=TEST_OPERATION_ID_EXTRA,
                replacement_phone_id=TEST_REPLACEMENT_PHONE_ID,
                replacement_phone_number=TEST_REPLACEMENT_PHONE_NUMBER.e164,
                secure_code_value=secure_code_value,
                secure_code_confirmed=secure_code_confirmed,
                secure_code_last_sent=secure_code_last_sent,
                secure_code_send_count=secure_code_send_count,
                replacement_code_confirmed=replacement_code_confirmed,
                password_verified=password_verified,
                started=operation_started,
                finished=operation_finished,
                flags=flags,
            ),
            self._build_replacement_phone(
                phone_id=TEST_REPLACEMENT_PHONE_ID,
                phone_number=TEST_REPLACEMENT_PHONE_NUMBER.e164,
                phone_confirmed=phone_confirm_time,
            ),
        )

    def _given_accounts(self, subject_account, extra_accounts=None):
        if extra_accounts is None:
            extra_accounts = []

        build_account_from_session(db_faker=self.env.db, **subject_account)
        for extra_account in extra_accounts:
            build_account(db_faker=self.env.db, **extra_account)

        self.env.blackbox.set_response_value(
            u'sessionid',
            blackbox_sessionid_multi_response(**subject_account),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response_multiple(extra_accounts),
        )

        bindings = []
        for args in extra_accounts:
            for phone in args[u'phones']:
                if (phone[u'number'] == TEST_REPLACEMENT_PHONE_NUMBER.e164 and
                        phone[u'bound']):
                    bindings.append({
                        u'type': u'current',
                        u'number': phone[u'number'],
                        u'phone_id': phone[u'id'],
                        u'uid': args[u'uid'],
                        u'bound': phone[u'bound'],
                    })
        for phone in subject_account[u'phones']:
            if (phone[u'number'] == TEST_REPLACEMENT_PHONE_NUMBER.e164 and
                    not phone[u'bound']):
                bindings.append({
                    u'type': u'current',
                    u'number': phone[u'number'],
                    u'phone_id': phone[u'id'],
                    u'uid': subject_account[u'uid'],
                    u'bound': datetime.now(),
                })

        history_bindings = []
        for binding in bindings:
            if binding[u'uid'] != subject_account[u'uid']:
                binding = dict(binding, type=u'history')
                history_bindings.append(binding)

        self.env.blackbox.set_response_side_effect(
            u'phone_bindings',
            [
                blackbox_phone_bindings_response(history_bindings),
                blackbox_phone_bindings_response(bindings),
            ],
        )

    def _given_track(self, display_language=u'ru', is_password_verified=False,
                     is_replacement_confirmed=False):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.display_language = display_language

            if is_password_verified:
                password_verification = Confirmation(
                    logical_operation_id=TEST_OPERATION_ID,
                    phone_id=TEST_SECURE_PHONE_ID,
                    password_verified=datetime.now(),
                )
                track.phone_operation_confirmations.append(password_verification.to_json())

            if is_replacement_confirmed:
                phone_confirmation = Confirmation(
                    logical_operation_id=TEST_OPERATION_ID,
                    phone_id=TEST_REPLACEMENT_PHONE_ID,
                    phone_confirmed=datetime.now(),
                )
                track.phone_operation_confirmations.append(phone_confirmation.to_json())

    def setup_statbox_templates(self):
        super(BaseReplaceSecurePhoneCommitTestCase, self).setup_statbox_templates()

        self.env.statbox.bind_entry(
            'frodo_karma',
            _inherit_from=['frodo_karma'],
            _exclude=[
                'mode',
                'step',
                'track_id',
            ],
            registration_datetime='-',
        )


@with_settings_hosts(
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'phone_change'},
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:phone_change': 5,
        },
    )
)
class TestReplaceSecureWithBoundPhoneCommit(BaseReplaceSecurePhoneCommitTestCase,
                                            ReplaceSecurePhoneCommitTestSet,
                                            GetAccountBySessionOrTokenMixin):
    def _build_replace_operation(self, replacement_code_confirmed,
                                 replacement_operation_id,
                                 replacement_phone_id,
                                 replacement_phone_number, **kwargs):
        return build_simple_replaces_secure_operations(
            simple_code_confirmed=replacement_code_confirmed,
            simple_operation_id=replacement_operation_id,
            simple_phone_id=replacement_phone_id,
            simple_phone_number=replacement_phone_number,
            **kwargs
        )

    def _build_replacement_phone(self, **kwargs):
        return build_phone_bound(**kwargs)

    def _assert_events_ok(self, expect_parsed_event=None, **kwargs):
        events = self._build_events(**kwargs) + [
            {
                u'uid': str(TEST_UID),
                u'name': u'phone.%d.operation.%d.type' % (TEST_REPLACEMENT_PHONE_ID, TEST_OPERATION_ID_EXTRA),
                u'value': u'mark',
            },
        ]
        self.assert_events_are_logged(self.env.handle_mock, events)

        if expect_parsed_event:
            parsed_events = self.env.event_logger.parse_events()
            ok_(parsed_events)
            for event in parsed_events:
                eq_(event._asdict().get('event_type'), expect_parsed_event)

    def _assert_statbox_ok(self, was_secure_alias=True, excluded=None, with_check_cookies=False):
        excluded = excluded or []
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(
            self.env.statbox.entry(
                'submitted',
                _exclude=excluded,
                operation_id=str(TEST_OPERATION_ID),
            ),
        )
        if was_secure_alias:
            entries.extend([
                self.env.statbox.entry('phonenumber_alias_removed'),
            ])

        entries.extend([
            self.env.statbox.entry(
                'account_phones_secure',
                _exclude=excluded,
                operation='updated',
                old=TEST_SECURE_PHONE_NUMBER.masked_format_for_statbox,
                old_entity_id=str(TEST_SECURE_PHONE_ID),
                new=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
                new_entity_id=str(TEST_REPLACEMENT_PHONE_ID),
            ),
        ])
        if was_secure_alias:
            entries.append(self.env.statbox.entry('phonenumber_alias_subscription_removed', _exclude=excluded))
        entries.extend([
            self.env.statbox.entry('secure_phone_replaced', _exclude=excluded),
            self.env.statbox.entry('completed', _exclude=['number'] + excluded),
        ])
        self.env.statbox.assert_has_written(entries)


@with_settings_hosts(
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    YASMS_MARK_OPERATION_TTL=TEST_MARK_OPERATION_TTL,
    YASMS_PHONE_BINDING_LIMIT=2,
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'phone_change'},
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:phone_change': 5,
        },
    )
)
class TestReplaceSecureWithBeingBoundPhoneCommit(BaseReplaceSecurePhoneCommitTestCase,
                                                 ReplaceSecurePhoneCommitTestSet,
                                                 GetAccountBySessionOrTokenMixin):
    def test_bind_simple_phone(self):
        # Пароль не проверен
        # Код от защищённого телефона не проверен
        # Код от замены проверен
        # Защищённый телефон является алиасом
        # Замена привязана к другим учётным записям

        operation_started = datetime.now() - timedelta(seconds=5)
        operation_finished = operation_started + timedelta(hours=1)
        self._given_accounts(
            self._build_subject_account_args(
                is_secure_alias=True,
                is_secure_confirmed=False,
                is_password_verified=False,
                operation_started=operation_started,
                operation_finished=operation_finished,
            ),
        )
        expected_operation_id_on_bound_phone = predict_next_operation_id(TEST_UID)

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['password.not_confirmed', 'phone.not_confirmed', 'phone.not_confirmed(%d)' % TEST_SECURE_PHONE_ID],
        )

        assert_secure_phone_being_replaced.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_SECURE_PHONE_ID},
            {
                'id': TEST_OPERATION_ID,
                'password_verified': None,
                'code_confirmed': None,
                'phone_id2': TEST_REPLACEMENT_PHONE_ID,
            },
        )
        assert_simple_phone_replace_secure.check_db(
            self.env.db,
            TEST_UID,
            {
                'id': TEST_REPLACEMENT_PHONE_ID,
                'bound': DatetimeNow(),
                'confirmed': DatetimeNow(),
            },
            {
                'id': expected_operation_id_on_bound_phone,
                'password_verified': None,
                'code_confirmed': DatetimeNow(),
                'phone_id2': TEST_SECURE_PHONE_ID,
            },
        )
        self.env.db.check_missing(
            'phone_operations',
            db='passportdbshard1',
            uid=TEST_UID,
            id=TEST_OPERATION_ID_EXTRA,
        )

        e = EventCompositor(uid=str(TEST_UID))

        e('info.karma_prefix', '6')
        e('info.karma_full', '6000')

        self.assert_events_are_logged(
            self.env.handle_mock,
            self._build_operation_replaced_events(
                expected_operation_id_on_bound_phone,
                str(to_unixtime(operation_started)),
                str(to_unixtime(operation_finished)),
            ) +
            e.to_lines(),
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('submitted', operation_id=str(TEST_OPERATION_ID)),
            self.env.statbox.entry('frodo_karma'),
            self.env.statbox.entry(
                'simple_phone_bound',
                phone_id=str(TEST_REPLACEMENT_PHONE_ID),
                number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
            ),
        ])

        eq_(self.env.mailer.messages, [])

    def _build_replace_operation(self, replacement_code_confirmed, replacement_operation_id, replacement_phone_id,
                                 replacement_phone_number, **kwargs):
        return build_phone_being_bound_replaces_secure_operations(
            being_bound_code_confirmed=replacement_code_confirmed,
            being_bound_operation_id=replacement_operation_id,
            being_bound_phone_id=replacement_phone_id,
            being_bound_phone_number=replacement_phone_number,
            **kwargs
        )

    def _build_replacement_phone(self, **kwargs):
        return build_phone_unbound(**kwargs)

    def _assert_events_ok(self, expect_parsed_event=None, **kwargs):
        events = self._build_events(**kwargs) + [
            {u'uid': str(TEST_UID), u'name': u'phone.%d.bound' % TEST_REPLACEMENT_PHONE_ID, u'value': TimeNow()},
            {
                u'uid': str(TEST_UID),
                u'name': u'phone.%d.operation.%d.type' % (TEST_REPLACEMENT_PHONE_ID, TEST_OPERATION_ID_EXTRA),
                u'value': u'bind',
            },
            {u'uid': str(TEST_UID), u'name': u'info.karma_prefix', u'value': u'6'},
            {u'uid': str(TEST_UID), u'name': u'info.karma_full', u'value': u'6000'},
        ]
        self.assert_events_are_logged(self.env.handle_mock, events)

        if expect_parsed_event:
            parsed_events = self.env.event_logger.parse_events()
            ok_(parsed_events)
            for event in parsed_events:
                eq_(event._asdict().get('event_type'), expect_parsed_event)

    def _assert_statbox_ok(self, was_secure_alias=True, excluded=None, with_check_cookies=False):
        excluded = excluded or []
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry('submitted', _exclude=excluded, operation_id=str(TEST_OPERATION_ID)),
        ])
        if was_secure_alias:
            entries.extend([
                self.env.statbox.entry('phonenumber_alias_removed'),
            ])
        entries.extend([
            self.env.statbox.entry(
                'account_phones_secure',
                _exclude=excluded,
                operation='updated',
                old=TEST_SECURE_PHONE_NUMBER.masked_format_for_statbox,
                old_entity_id=str(TEST_SECURE_PHONE_ID),
                new=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
                new_entity_id=str(TEST_REPLACEMENT_PHONE_ID),
            ),
            self.env.statbox.entry('phone_secure_replace_commit', _exclude=excluded),
        ])
        if was_secure_alias:
            entries.append(self.env.statbox.entry('phonenumber_alias_subscription_removed', _exclude=excluded))
        entries.extend([
            self.env.statbox.entry(
                'simple_phone_bound',
                _exclude=excluded,
                phone_id=str(TEST_REPLACEMENT_PHONE_ID),
                number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
            ),
            self.env.statbox.entry('secure_phone_replaced', _exclude=excluded),
            self.env.statbox.entry('completed', _exclude=['number'] + excluded),
        ])
        self.env.statbox.assert_has_written(entries)

    def _build_operation_replaced_events(self, operation_id, operation_started, operation_finished):
        """
        События, которые должны быть записаны в eventlog, когда операция замены
        привязываемого номера меняется на операцию замены привязанного номера.
        """
        e = EventCompositor(uid=str(TEST_UID))

        e('action', 'phone_secure_replace_commit')
        e('consumer', 'dev')
        e('user_agent', TEST_USER_AGENT)

        with e.prefix('phone.%d.' % TEST_REPLACEMENT_PHONE_ID):
            e('action', 'changed')
            e('number', TEST_REPLACEMENT_PHONE_NUMBER.e164)
            e('bound', TimeNow())

            with e.prefix('operation.%d.' % TEST_OPERATION_ID_EXTRA):
                e('action', 'deleted')
                e('type', 'bind'),
                e('security_identity', TEST_REPLACEMENT_PHONE_NUMBER.digital)

            with e.prefix('operation.%d.' % operation_id):
                e('action', 'created')
                e('type', 'mark')
                e('security_identity', TEST_REPLACEMENT_PHONE_NUMBER.digital)
                e('started', operation_started)
                e('finished', operation_finished)
                e('code_confirmed', TimeNow())
                e('phone_id2', str(TEST_SECURE_PHONE_ID))

        return e.to_lines()

    def _build_extra_account_events(self, uid, phone_id, operation_id):
        """
        События, которые должны быть записаны в eventlog, когда замена
        отвязывается от других учёных записей.
        """
        unbound = (phone_id, operation_id)
        return [
            {u'uid': str(uid), u'name': u'action', u'value': u'acquire_phone'},
            {u'uid': str(uid), u'name': u'phone.%d.number' % phone_id, u'value': TEST_REPLACEMENT_PHONE_NUMBER.e164},
            {u'uid': str(uid), u'name': u'phone.%d.operation.%d.action' % unbound, u'value': u'created'},
            {u'uid': str(uid), u'name': u'phone.%d.operation.%d.type' % unbound, u'value': u'mark'},
            {u'uid': str(uid), u'name': u'phone.%d.operation.%d.started' % unbound, u'value': TimeNow()},
            {
                u'uid': str(uid),
                u'name': u'phone.%d.operation.%d.finished' % unbound,
                u'value': TimeNow(offset=TEST_MARK_OPERATION_TTL),
            },
            {
                u'uid': str(uid),
                u'name': u'phone.%d.operation.%d.security_identity' % unbound,
                u'value': TEST_REPLACEMENT_PHONE_NUMBER.digital,
            },
            {u'uid': str(uid), u'name': u'consumer', u'value': u'dev'},

            {u'uid': str(uid), u'name': u'action', u'value': u'unbind_phone_from_account'},
            {u'uid': str(uid), u'name': u'reason_uid', u'value': str(TEST_UID)},
            {u'uid': str(uid), u'name': u'phone.%d.action' % phone_id, u'value': u'changed'},
            {u'uid': str(uid), u'name': u'phone.%d.number' % phone_id, u'value': TEST_REPLACEMENT_PHONE_NUMBER.e164},
            {u'uid': str(uid), u'name': u'phone.%d.bound' % phone_id, u'value': u'0'},
            {u'uid': str(uid), u'name': u'phone.%d.operation.%d.action' % unbound, u'value': u'deleted'},
            {u'uid': str(uid), u'name': u'phone.%d.operation.%d.type' % unbound, u'value': u'mark'},
            {
                u'uid': str(uid),
                u'name': u'phone.%d.operation.%d.security_identity' % unbound,
                u'value': TEST_REPLACEMENT_PHONE_NUMBER.digital,
            },
            {u'uid': str(uid), u'name': u'consumer', u'value': u'dev'},

            {
                u'uid': str(TEST_UID),
                u'name': u'unbind_phone_from_account.%d' % uid,
                u'value': TEST_REPLACEMENT_PHONE_NUMBER.e164,
            },
        ]


@with_settings_hosts(
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'phone_change'},
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:phone_change': 5,
        },
    )
)
class TestReplaceSecurePhoneCommit(BaseReplaceSecurePhoneCommitTestCase,
                                   GetAccountBySessionOrTokenMixin):
    def test_different_operation(self):
        # Телефоны подтверждены
        # Пароль проверен
        # Другая операция

        self._given_accounts(
            dict(
                uid=TEST_UID,
                crypt_password=TEST_PASSWORD_HASH,
                firstname=TEST_FIRSTNAME,
                login=TEST_LOGIN,
                **build_secure_phone_being_bound(
                    TEST_PHONE_ID,
                    TEST_PHONE_NUMBER.e164,
                    TEST_OPERATION_ID,
                    password_verified=datetime.now(),
                    code_confirmed=datetime.now(),
                )
            ),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['operation.invalid_state'])
        self.assert_events_are_logged(self.env.handle_mock, [])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'submitted',
                operation_id=str(TEST_OPERATION_ID),
            ),
        ])
        eq_(self.env.mailer.messages, [])


@with_settings_hosts(
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'phone_change'},
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:phone_change': 5,
        },
    )
)
class TestReplaceSecurePhoneCommitPasswordlessAccount(BaseReplaceSecurePhoneCommitTestCase):
    def _build_replace_operation(
        self,
        replacement_code_confirmed,
        replacement_operation_id,
        replacement_phone_id,
        replacement_phone_number,
        **kwargs
    ):
        return build_phone_being_bound_replaces_secure_operations(
            being_bound_code_confirmed=replacement_code_confirmed,
            being_bound_operation_id=replacement_operation_id,
            being_bound_phone_id=replacement_phone_id,
            being_bound_phone_number=replacement_phone_number,
            **kwargs
        )

    def _build_replacement_phone(self, **kwargs):
        return build_phone_unbound(**kwargs)

    def test_passwordless_account(self):
        subject_account = self._build_subject_account_args(
            is_password_verified=False,
            alias_type='social',
            login=TEST_SOCIAL_LOGIN,
            password=None,
        )
        self._given_accounts(subject_account)
        self._given_track()

        rv = self.make_request()

        self.assert_response_ok(rv)
        self._assert_db_ok(was_secure_alias=False)

    def test_start_quarantine(self):
        account = self._build_subject_account_args(
            alias_type='social',
            is_password_verified=False,
            is_replacement_confirmed=False,
            is_secure_confirmed=False,
            login=TEST_SOCIAL_LOGIN,
            password=None,
            secure_code_last_sent=None,
            secure_code_value=None,
        )
        self._given_accounts(account)
        self._given_track(is_replacement_confirmed=True)

        rv = self.make_request()

        self.assert_response_ok(rv, in_quarantine=True)

        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        assert_secure_phone_being_replaced.check_db(
            self.env.db,
            TEST_UID,
            dict(id=TEST_SECURE_PHONE_ID),
            dict(flags=phone_operation_flags),
        )
        assert_simple_phone_replace_secure.check_db(
            self.env.db,
            TEST_UID,
            dict(id=TEST_REPLACEMENT_PHONE_ID),
            dict(flags=phone_operation_flags),
        )


@with_settings_hosts(
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'phone_change'},
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:phone_change': 5,
        },
    )
)
@istest
class TestRemoveSecurePhoneCommit(CommitBaseTestCase, GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/remove_secure/commit/'
    action = 'remove_secure_commit'
    mode = 'remove_secure'
    with_check_cookies = True

    def setUp(self):
        super(TestRemoveSecurePhoneCommit, self).setUp()
        args = build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164)
        self.phone = args['phones'][0]
        args = build_aliasify_secure_operation(TEST_OPERATION_ID, TEST_PHONE_ID, code_confirmed=datetime.now())
        self.operation = args['phone_operations'][0]

        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

    def _test_track_has_correct_operation(self, by_token=False, with_check_cookies=False):
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self._build_account(
            **deep_merge(
                dict(aliases={'portal': TEST_LOGIN}),
                build_phone_secured(
                    TEST_PHONE_ID,
                    TEST_PHONE_NUMBER.e164,
                    is_alias=True,
                    is_default=True,
                ),
                build_remove_operation(
                    TEST_OPERATION_ID,
                    TEST_PHONE_ID,
                    code_confirmed=datetime.now(),
                    password_verified=datetime.now(),
                ),
            )
        )
        self._given_track(display_language=u'en')

        rv = self.make_request(headers=headers)

        self.assert_response_ok(rv, track_id=self.track_id)

        assert_no_phone_in_db(self.env.db, TEST_UID, TEST_PHONE_ID, TEST_PHONE_NUMBER.e164)
        assert_no_secure_phone(self.env.db, TEST_UID)
        self.env.db.check_missing('phone_operations', id=TEST_OPERATION_ID, db='passportdbshard1')
        assert_no_default_phone_chosen(self.env.db, TEST_UID)
        assert_phonenumber_alias_removed(self.env.db, TEST_UID, TEST_PHONE_NUMBER.digital)

        self.assert_events_are_logged(
            self.env.handle_mock,
            merge_dicts(
                {
                    'action': self.action,
                    'phones.default': '0',
                    'alias.phonenumber.rm': TEST_PHONE_NUMBER.international,
                },
                self._event_lines_secure_phone_removed(),
                self._event_lines_environment(),
            ),
        )

        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('phonenumber_alias_removed'),
            self.env.statbox.entry('account_modification_secure_phone_removed'),
            self.env.statbox.entry('phonenumber_alias_subscription_removed'),
            self.env.statbox.entry('secure_phone_removed'),
            self.env.statbox.entry('completed'),
        ])

        self.env.statbox.assert_has_written(entries)

        self._assert_user_notified_about_alias_as_login_and_email_disabled(language='en')
        self._assert_user_notified_about_secure_phone_removed(language='en')
        self._assert_phone_data_asked_from_blackbox(self.env.blackbox.requests[0], by_token=by_token)
        self.assert_blackbox_auth_method_ok(by_token)

    def test_ok_with_track_by_session(self):
        self._test_track_has_correct_operation(with_check_cookies=True)
        self.check_account_modification_push_sent(
            ip=TEST_USER_IP,
            event_name='phone_change',
            uid=TEST_UID,
            title='В аккаунте {} изменён номер телефона'.format(TEST_LOGIN),
            body='Если это вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
        )

    def test_ok_with_track_by_token(self):
        self._test_track_has_correct_operation(by_token=True)

    def _test_without_phonenumber_alias(self, by_token=False):
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self._build_account(
            **deep_merge(
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164),
                build_remove_operation(
                    TEST_OPERATION_ID,
                    TEST_PHONE_ID,
                    code_confirmed=datetime.now(),
                    password_verified=datetime.now(),
                ),
            )
        )

        rv = self.make_request(headers=headers)

        self.assert_response_ok(rv, track_id=self.track_id)

        assert_no_phone_in_db(self.env.db, TEST_UID, TEST_PHONE_ID, TEST_PHONE_NUMBER.e164)
        assert_no_secure_phone(self.env.db, TEST_UID)
        self.env.db.check_missing('phone_operations', id=TEST_OPERATION_ID, db='passportdbshard1')

        self.assert_events_are_logged(
            self.env.handle_mock,
            merge_dicts(
                {'action': self.action},
                self._event_lines_secure_phone_removed(),
                self._event_lines_environment(),
            ),
        )

        entries = []
        if not by_token:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend(
            [
                self.env.statbox.entry('submitted'),
                self.env.statbox.entry('account_modification_secure_phone_removed'),
                self.env.statbox.entry('secure_phone_removed'),
                self.env.statbox.entry('completed'),
            ],
        )

        self.env.statbox.assert_has_written(entries)

        self._assert_phone_data_asked_from_blackbox(self.env.blackbox.requests[0], by_token=by_token)
        self.assert_blackbox_auth_method_ok(by_token)
        self._assert_user_notified_about_secure_phone_removed()

    def test_ok_without_track_by_session(self):
        self._test_without_phonenumber_alias()

    def test_ok_without_track_by_token(self):
        self._test_without_phonenumber_alias(by_token=True)

    def test_ok_with_existing_track(self):
        self._set_defaults()
        self._test_ok_with_existing_track()

    def test_error_operation_not_found(self):
        self._set_defaults()
        self._test_error_operation_not_found()

    def test_error_operation_invalid_type(self):
        self._build_account(**build_phone_being_bound(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164, TEST_OPERATION_ID))
        rv = self.make_request()
        self.assert_error_response(rv, ['operation.invalid_state'])

    def test_error_password_not_verified(self):
        self._set_defaults()
        self._test_error_password_not_verified()

    def test_ok_account_without_password(self):
        self._set_defaults()
        self._test_ok_account_without_password()

    def test_error_phone_not_confirmed(self):
        self._set_defaults()
        self.set_blackbox_response(operations=[dict(self.operation, code_confirmed=None)])

        rv = self.make_request()

        self.assert_error_response(rv, ['phone.not_confirmed', 'phone.not_confirmed(%d)' % TEST_PHONE_ID])

    def test_in_quarantine(self):
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        phone_operation_finished = datetime.now() + TEST_OPERATION_TTL / 2
        self._build_account(
            **deep_merge(
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164),
                build_remove_operation(
                    TEST_OPERATION_ID,
                    TEST_PHONE_ID,
                    code_last_sent=None,
                    code_send_count=0,
                    code_value=None,
                    password_verified=datetime.now(),
                    finished=phone_operation_finished,
                    flags=phone_operation_flags,
                ),
            )
        )

        rv = self.make_request()

        self.assert_response_ok(rv, track_id=self.track_id, number=TEST_PHONE_NUMBER)

        assert_secure_phone_being_removed.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID, 'number': TEST_PHONE_NUMBER.e164},
            {'finished': phone_operation_finished},
        )

        eq_(len(self.env.mailer.messages), 0)
        eq_(len(self.env.yasms.requests), 0)

    def test_ready_for_quarantine(self):
        self._build_account(
            **deep_merge(
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164),
                build_remove_operation(
                    TEST_OPERATION_ID,
                    TEST_PHONE_ID,
                    code_last_sent=None,
                    code_send_count=0,
                    code_value=None,
                    password_verified=datetime.now(),
                ),
            )
        )

        rv = self.make_request()

        self.assert_response_ok(rv, track_id=self.track_id, number=TEST_PHONE_NUMBER)

        quarantine_finished = DatetimeNow(timestamp=datetime.now() + TEST_OPERATION_TTL)
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        assert_secure_phone_being_removed.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID, 'number': TEST_PHONE_NUMBER.e164},
            {
                'finished': quarantine_finished,
                'flags': phone_operation_flags,
            },
        )

        email_notifications.assert_user_notified_about_secure_phone_removal_started(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_EMAIL,
            firstname=TEST_FIRSTNAME,
            login=TEST_LOGIN,
        )
        sms_notifications.assert_user_notified_about_secure_phone_removal_started(
            yasms_builder_faker=self.env.yasms,
            language='ru',
            phone_number=TEST_PHONE_NUMBER,
            uid=TEST_UID,
        )

    def test_start_quarantine(self):
        self._build_account(
            **deep_merge(
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164),
                build_remove_operation(
                    TEST_OPERATION_ID,
                    TEST_PHONE_ID,
                    code_last_sent=None,
                    code_send_count=0,
                    code_value=None,
                    password_verified=None,
                ),
            )
        )
        self._given_track(is_password_verified=True)

        rv = self.make_request()

        self.assert_response_ok(rv, track_id=self.track_id, number=TEST_PHONE_NUMBER)

        quarantine_finished = DatetimeNow(timestamp=datetime.now() + TEST_OPERATION_TTL)
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        assert_secure_phone_being_removed.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID, 'number': TEST_PHONE_NUMBER.e164},
            {
                'finished': quarantine_finished,
                'flags': phone_operation_flags,
            },
        )

        email_notifications.assert_user_notified_about_secure_phone_removal_started(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_EMAIL,
            firstname=TEST_FIRSTNAME,
            login=TEST_LOGIN,
        )
        sms_notifications.assert_user_notified_about_secure_phone_removal_started(
            yasms_builder_faker=self.env.yasms,
            language='ru',
            phone_number=TEST_PHONE_NUMBER,
            uid=TEST_UID,
        )

    def test_2fa_enabled(self):
        self._build_account(
            **deep_merge(
                dict(attributes={'account.2fa_on': True}),
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164),
                build_remove_operation(
                    TEST_OPERATION_ID,
                    TEST_PHONE_ID,
                    code_confirmed=datetime.now(),
                    password_verified=datetime.now(),
                ),
            )
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['account.2fa_enabled'])

    def test_sms_2fa_enabled(self):
        self._build_account(
            **deep_merge(
                dict(attributes={'account.sms_2fa_on': True}),
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164),
                build_remove_operation(
                    TEST_OPERATION_ID,
                    TEST_PHONE_ID,
                    code_confirmed=datetime.now(),
                    password_verified=datetime.now(),
                ),
            )
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['account.sms_2fa_enabled'], can_disable_sms_2fa=True)

    def test_error_account_disabled(self):
        self._set_defaults()
        self._test_error_account_disabled()

    def test_error_operation_expired(self):
        self._build_account(
            **deep_merge(
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164),
                build_remove_operation(TEST_OPERATION_ID, TEST_PHONE_ID, finished=datetime.now()),
            )
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['operation.expired'])

    def test_passwordless_account(self):
        self._build_account(
            **deep_merge(
                dict(
                    aliases=dict(social=TEST_SOCIAL_LOGIN),
                    crypt_password=None,
                    have_password=False,
                    firstname=TEST_FIRSTNAME,
                ),
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164),
                build_remove_operation(
                    TEST_OPERATION_ID,
                    TEST_PHONE_ID,
                    code_confirmed=datetime.now(),
                    password_verified=None,
                ),
            )
        )

        rv = self.make_request()

        self.assert_response_ok(rv, track_id=self.track_id)

        assert_no_phone_in_db(self.env.db, TEST_UID, TEST_PHONE_ID, TEST_PHONE_NUMBER.e164)

        self._assert_user_notified_about_secure_phone_removed_from_passwordless_account()

        self.assert_events_are_logged(
            self.env.handle_mock,
            merge_dicts(
                {
                    'action': self.action,
                },
                self._event_lines_secure_phone_removed(),
                self._event_lines_environment(),
            ),
        )

        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry('check_cookies'),
                self.env.statbox.entry('submitted'),
                self.env.statbox.entry('account_modification_secure_phone_removed'),
                self.env.statbox.entry('secure_phone_removed'),
                self.env.statbox.entry('completed'),
            ],
        )

    def test_passwordless_account_ready_for_quarantine(self):
        self._build_account(
            **deep_merge(
                dict(
                    aliases=dict(social=TEST_SOCIAL_LOGIN),
                    crypt_password=None,
                    have_password=False,
                    firstname=TEST_FIRSTNAME,
                ),
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164),
                build_remove_operation(
                    TEST_OPERATION_ID,
                    TEST_PHONE_ID,
                    code_last_sent=None,
                    code_send_count=0,
                    code_value=None,
                    password_verified=None,
                ),
            )
        )

        rv = self.make_request()

        self.assert_response_ok(rv, track_id=self.track_id, number=TEST_PHONE_NUMBER)

        quarantine_finished = DatetimeNow(timestamp=datetime.now() + TEST_OPERATION_TTL)
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        assert_secure_phone_being_removed.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID, 'number': TEST_PHONE_NUMBER.e164},
            {
                'finished': quarantine_finished,
                'flags': phone_operation_flags,
            },
        )

        assert_user_notified_about_secure_phone_removal_started_on_passwordless_account(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_EMAIL,
            firstname=TEST_FIRSTNAME,
            login=TEST_FIRSTNAME,
        )
        sms_notifications.assert_user_notified_about_secure_phone_removal_started(
            yasms_builder_faker=self.env.yasms,
            language='ru',
            phone_number=TEST_PHONE_NUMBER,
            uid=TEST_UID,
        )

    def test_no_email(self):
        self._build_account(
            **deep_merge(
                dict(
                    emails=list(),
                ),
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164),
                build_remove_operation(
                    TEST_OPERATION_ID,
                    TEST_PHONE_ID,
                    code_confirmed=datetime.now(),
                    password_verified=datetime.now(),
                ),
            )
        )

        rv = self.make_request()

        self.assert_response_ok(rv, track_id=self.track_id)

        eq_(len(self.env.mailer.messages), 0)

    def test_start_quarantine_no_email(self):
        self._build_account(
            **deep_merge(
                dict(
                    emails=list(),
                ),
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164),
                build_remove_operation(
                    TEST_OPERATION_ID,
                    TEST_PHONE_ID,
                    code_last_sent=None,
                    code_send_count=0,
                    code_value=None,
                    password_verified=None,
                ),
            )
        )
        self._given_track(is_password_verified=True)

        rv = self.make_request()

        self.assert_response_ok(rv, track_id=self.track_id, number=TEST_PHONE_NUMBER)

        assert_secure_phone_being_removed.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID, 'number': TEST_PHONE_NUMBER.e164},
        )

        eq_(len(self.env.mailer.messages), 0)

        sms_notifications.assert_user_notified_about_secure_phone_removal_started(
            yasms_builder_faker=self.env.yasms,
            language='ru',
            phone_number=TEST_PHONE_NUMBER,
            uid=TEST_UID,
        )

    def _event_lines_environment(self):
        return {
            'consumer': 'dev',
            'user_agent': TEST_USER_AGENT,
        }

    def _event_lines_secure_phone_removed(self):
        fmt = (TEST_PHONE_ID, TEST_OPERATION_ID)
        return {
            'phone.%d.number' % TEST_PHONE_ID: TEST_PHONE_NUMBER.e164,
            'phone.%d.action' % TEST_PHONE_ID: 'deleted',
            'phone.%d.operation.%d.action' % fmt: 'deleted',
            'phone.%d.operation.%d.type' % fmt: 'remove',
            'phone.%d.operation.%d.security_identity' % fmt: str(SECURITY_IDENTITY),
            'phones.secure': '0',
        }

    def _assert_phone_data_asked_from_blackbox(self, request, by_token=False):
        method = 'oauth' if by_token else 'sessionid'
        request.assert_query_contains({
            'method': method,
            'aliases': 'all_with_hidden',
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
        })
        request.assert_contains_attributes({
            'account.2fa_on',
            'phones.secure',
            'phones.default',
        })

    def assert_response_ok(self, rv, track_id=None, number=None):
        eq_(rv.status_code, 200)
        data = json.loads(rv.data)

        eq_(data['status'], 'ok')
        eq_(data['track_id'], track_id)

        if number is not None:
            number = {
                'id': TEST_PHONE_ID,
                'number': dump_number(number),
                'operation': {
                    'id': TEST_OPERATION_ID,
                    'security_identity': SECURITY_IDENTITY,
                    'in_quarantine': True,
                },
            }
        eq_(data['phone'], number)
        ok_('account' in data)

    def _set_defaults(self):
        account_data = build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164)
        self.phone = account_data['phones'][0]

        account_data = build_remove_operation(
            TEST_OPERATION_ID,
            TEST_PHONE_ID,
            code_confirmed=datetime.now(),
            password_verified=datetime.now(),
        )
        self.operation = account_data['phone_operations'][0]

        self._given_track()

    def setup_statbox_templates(self):
        super(TestRemoveSecurePhoneCommit, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='submitted',
            operation_id=str(TEST_OPERATION_ID),
        )


@with_settings_hosts(
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'phone_change'},
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:phone_change': 5,
        },
    )
)
@istest
class TestAliasifySecurePhoneCommit(CommitBaseTestCase, GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/aliasify/commit/'

    action = 'aliasify_secure_commit'
    mode = 'aliasify_secure'
    with_check_cookies = True

    def setUp(self):
        super(TestAliasifySecurePhoneCommit, self).setUp()

        args = build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164)
        self.phone = args['phones'][0]

        args = build_aliasify_secure_operation(TEST_OPERATION_ID, TEST_PHONE_ID, code_confirmed=datetime.now())
        self.operation = args['phone_operations'][0]

    def test_error_phone_not_confirmed(self):
        self._test_error_phone_not_confirmed()

    def test_error_operation_invalid_type(self):
        self._test_error_operation_invalid_type()

    def test_error_operation_not_found(self):
        self._test_error_operation_not_found()

    def test_error_account_disabled(self):
        self._test_error_account_disabled()

    def test_error_account_disabled_on_deletion(self):
        self._test_error_account_disabled_on_deletion()

    def test_error_has_phonenumber_alias(self):
        self.set_blackbox_response(phonenumber_alias=TEST_PHONE_NUMBER.digital)

        rv = self.make_request()

        self.assert_error_response(rv, ['phone_alias.exist'])

    def test_error_no_secure_phone(self):
        self._test_error_no_secure_phone()

    def test_ok_account_without_password(self):
        self._test_ok_account_without_password()

    def test_display_language__ru(self):
        self.set_blackbox_response()
        self._given_track(display_language='ru')

        rv = self.make_request()

        self.assert_response_ok(rv)

        self._assert_user_notified_about_aliasify(language='ru')

    def test_display_language__en(self):
        self.set_blackbox_response()
        self._given_track(display_language='en')

        rv = self.make_request()

        self.assert_response_ok(rv)

        self._assert_user_notified_about_aliasify(language='en')

    def test_other_account_has_phonenumber_alias(self):
        self.set_blackbox_response()
        self._build_other_account()

        rv = self.make_request()

        self.assert_response_ok(rv)

        assert_phonenumber_alias_missing(self.env.db, TEST_UID2)
        assert_phonenumber_alias_removed(self.env.db, TEST_UID2, TEST_PHONE_NUMBER.digital)
        self._assert_user_notified_about_realiasify()

        self.env.event_logger.assert_contains([
            {'uid': str(TEST_UID2), 'name': 'action', 'value': 'phone_alias_delete'},
            {'uid': str(TEST_UID2), 'name': 'alias.phonenumber.rm', 'value': TEST_PHONE_NUMBER.international},
            {'uid': str(TEST_UID2), 'name': 'consumer', 'value': 'dev'},
        ])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('submitted', operation_id=str(TEST_OPERATION_ID)),
            self.env.statbox.entry('phonenumber_alias_removed', uid=str(TEST_UID2)),
            self.env.statbox.entry('phonenumber_alias_subscription_removed', uid=str(TEST_UID2)),
            self.env.statbox.entry('phonenumber_alias_added'),
            self.env.statbox.entry('phonenumber_alias_subscription_added'),
            self.env.statbox.entry('phonenumber_alias_search_enabled'),
            self.env.statbox.entry('phone_operation_applied'),
            self.env.statbox.entry('completed'),
        ])

    def test_dont_dealiasify_other_account__code_not_confirmed(self):
        self.set_blackbox_response(operations=[dict(self.operation, code_confirmed=None)])
        self._build_other_account()

        rv = self.make_request()

        self.assert_error_response(rv, ['phone.not_confirmed', 'phone.not_confirmed(%d)' % TEST_PHONE_ID])
        assert_account_has_phonenumber_alias(self.env.db, TEST_UID2, TEST_PHONE_NUMBER.digital)

    def _test_ok(self, by_token=False):
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self.set_blackbox_response()

        rv = self.make_request(headers=headers)

        self.assert_response_ok(rv)
        self._assert_user_notified_about_aliasify()
        assert_account_has_phonenumber_alias(self.env.db, TEST_UID, TEST_PHONE_NUMBER.digital)

        phone_fmt = 'phone.%d.' % TEST_PHONE_ID
        op_fmt = phone_fmt + 'operation.%d.' % TEST_OPERATION_ID
        self.env.event_logger.assert_contains([
            {'uid': str(TEST_UID), 'name': 'action', 'value': 'aliasify_secure_commit'},
            {'uid': str(TEST_UID), 'name': 'alias.phonenumber.add', 'value': TEST_PHONE_NUMBER.international},
            {'uid': str(TEST_UID), 'name': op_fmt + 'action', 'value': 'deleted'},
            {'uid': str(TEST_UID), 'name': op_fmt + 'type', 'value': 'aliasify'},
            {'uid': str(TEST_UID), 'name': op_fmt + 'security_identity', 'value': str(SECURITY_IDENTITY)},
            {'uid': str(TEST_UID), 'name': phone_fmt + 'number', 'value': TEST_PHONE_NUMBER.e164},
            {'uid': str(TEST_UID), 'name': 'consumer', 'value': 'dev'},
            {'uid': str(TEST_UID), 'name': 'user_agent', 'value': TEST_USER_AGENT},
        ])
        entries = []
        if not by_token:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry('submitted', operation_id=str(TEST_OPERATION_ID)),
            self.env.statbox.entry('phonenumber_alias_added'),
            self.env.statbox.entry('phonenumber_alias_subscription_added'),
            self.env.statbox.entry('phonenumber_alias_search_enabled'),
            self.env.statbox.entry('phone_operation_applied'),
            self.env.statbox.entry('completed'),
        ])
        self.env.statbox.assert_has_written(entries)
        self.assert_blackbox_auth_method_ok(by_token)

    def test_ok_by_session(self):
        self._test_ok()

    def test_ok_by_token(self):
        self._test_ok(by_token=True)

    def test_blackbox_args(self):
        self.set_blackbox_response()

        rv = self.make_request()

        self.assert_response_ok(rv)

        requests = self.env.blackbox.requests
        eq_(len(requests), 2)

        requests[0].assert_query_contains({
            'method': 'sessionid',
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
            'emails': 'getall',
        })

        requests[0].assert_contains_attributes(
            {'account.is_disabled', 'person.language'} |
            set(settings.BLACKBOX_PHONE_ATTRIBUTES),
        )

        requests[1].assert_post_data_contains({
            'method': 'userinfo',
            'login': TEST_PHONE_NUMBER.digital,
            'aliases': 'all_with_hidden',
            'emails': 'getall',
        })

        requests[1].assert_contains_attributes({'person.language'})

    def test_passwordless_account(self):
        self.set_blackbox_response(
            password_is_set=False,
            alias_type='social',
            login=TEST_SOCIAL_LOGIN,
        )

        rv = self.make_request()

        self.assert_response_ok(rv)

        assert_account_has_phonenumber_alias(
            self.env.db,
            TEST_UID,
            TEST_PHONE_NUMBER.digital,
            enable_search=False,
        )

    def set_blackbox_response(self, *args, **kwargs):
        super(TestAliasifySecurePhoneCommit, self).set_blackbox_response(*args, **kwargs)
        # Ответ ЧЯ на поиск пользователя по телефонному алиасу.
        self.env.blackbox.set_response_value('userinfo', blackbox_userinfo_response_multiple([{'uid': None}]))

    def _build_other_account(self):
        emails = [
            self.env.email_toolkit.create_native_email(
                login=TEST_EMAIL2.split(u'@')[0],
                domain=TEST_EMAIL2.split(u'@')[1],
            ),
        ]

        build_account(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            **deep_merge(
                dict(
                    uid=TEST_UID2,
                    login=TEST_LOGIN2,
                    aliases={'portal': TEST_LOGIN2},
                    emails=emails,
                    firstname=TEST_FIRSTNAME2,
                    language='ru',
                ),
                build_phone_secured(
                    TEST_PHONE_ID_EXTRA,
                    TEST_PHONE_NUMBER.e164,
                    is_alias=True,
                ),
            )
        )


@with_settings_hosts(
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'phone_change'},
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:phone_change': 5,
        },
    )
)
@istest
class TestDealiasifySecurePhoneCommit(CommitBaseTestCase, GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/dealiasify/commit/'

    action = 'dealiasify_secure_commit'
    mode = 'dealiasify_secure'
    with_check_cookies = True

    def setUp(self):
        super(TestDealiasifySecurePhoneCommit, self).setUp()

        args = build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164, is_alias=True)
        self.phone = args['phones'][0]

        self.operation = self.build_dealiasify_secure_operation()

    def build_dealiasify_secure_operation(self, password_verified=Undefined):
        if password_verified is Undefined:
            password_verified = datetime.now()
        args = build_dealiasify_secure_operation(
            TEST_OPERATION_ID,
            TEST_PHONE_ID,
            password_verified=password_verified,
        )
        return args['phone_operations'][0]

    def set_blackbox_response(self, phonenumber_alias=TEST_PHONE_NUMBER.digital, **kwargs):
        super(TestDealiasifySecurePhoneCommit, self).set_blackbox_response(phonenumber_alias=phonenumber_alias, **kwargs)

    def test_error_operation_invalid_type(self):
        self._test_error_operation_invalid_type(submitted_first=True)

    def test_error_operation_not_found(self):
        self._test_error_operation_not_found(submitted_first=True)

    def test_error_account_disabled(self):
        self._test_error_account_disabled()

    def test_error_account_disabled_on_deletion(self):
        self._test_error_account_disabled_on_deletion()

    def test_error_no_phonenumber_alias(self):
        self.set_blackbox_response(phonenumber_alias=None)

        rv = self.make_request()

        self.assert_error_response(rv, ['phone_alias.not_found'])

    def test_error_password_not_verified(self):
        self._test_error_password_not_verified()

    def test_ok_account_without_password(self):
        self._test_ok_account_without_password()

    def test_display_language__ru(self):
        self.set_blackbox_response()
        self._given_track(display_language='ru')

        rv = self.make_request()

        self.assert_response_ok(rv)

        self._assert_user_notified_about_alias_as_login_and_email_disabled(language='ru')

    def test_display_language__en(self):
        self.set_blackbox_response()
        self._given_track(display_language='en')

        rv = self.make_request()

        self.assert_response_ok(rv)

        self._assert_user_notified_about_alias_as_login_and_email_disabled(language='en')

    def _test_ok(self, by_token=False, with_check_cookies=False):
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self.set_blackbox_response()

        rv = self.make_request(headers=headers)

        self.assert_response_ok(rv)
        self._assert_phonenumber_alias_removed(with_check_cookies=with_check_cookies)
        self.assert_blackbox_auth_method_ok(by_token)

    def test_ok_by_session(self):
        self._test_ok(with_check_cookies=True)

    def test_ok_by_token(self):
        self._test_ok(by_token=True)

    def test_blackbox_args(self):
        self.set_blackbox_response()

        rv = self.make_request()

        self.assert_response_ok(rv)

        requests = self.env.blackbox.requests
        eq_(len(requests), 1)

        requests[0].assert_query_contains({
            'method': 'sessionid',
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
            'emails': 'getall',
        })

        requests[0].assert_contains_attributes(
            {'account.is_disabled'} |
            set(settings.BLACKBOX_PHONE_ATTRIBUTES),
        )

    def test_password_confirmed_in_track(self):
        self.operation = self.build_dealiasify_secure_operation(password_verified=None)
        self.set_blackbox_response()
        self._given_track(is_password_verified=True)

        rv = self.make_request()

        self.assert_response_ok(rv)
        self._assert_phonenumber_alias_removed(with_check_cookies=True)
        self.assert_blackbox_auth_method_ok(by_token=False)

    def test_alias_as_email_disabled(self):
        self.set_blackbox_response(
            account_attributes={
                'account.enable_search_by_phone_alias': '0',
            },
        )

        rv = self.make_request()

        self.assert_response_ok(rv)

        self._assert_phonenumber_alias_removed(phonenumber_alias_as_email_enabled=False, with_check_cookies=True)

    def test_passwordless_account(self):
        self.operation = self.build_dealiasify_secure_operation(password_verified=None)
        self.set_blackbox_response(
            alias_type='social',
            login=TEST_SOCIAL_LOGIN,
            password_is_set=False,
            account_attributes={
                'account.enable_search_by_phone_alias': '0',
            },
        )

        rv = self.make_request()

        self.assert_response_ok(rv)
        self._assert_phonenumber_alias_removed(phonenumber_alias_as_email_enabled=False, with_check_cookies=True)

    def _assert_phonenumber_alias_removed(self, phonenumber_alias_as_email_enabled=True, with_check_cookies=False):
        if phonenumber_alias_as_email_enabled:
            self._assert_user_notified_about_alias_as_login_and_email_disabled()
        else:
            self._assert_user_notified_about_alias_as_login_disabled()

        assert_phonenumber_alias_missing(self.env.db, TEST_UID)
        assert_phonenumber_alias_removed(self.env.db, TEST_UID, TEST_PHONE_NUMBER.digital)

        phone_fmt = 'phone.%d.' % TEST_PHONE_ID
        op_fmt = phone_fmt + 'operation.%d.' % TEST_OPERATION_ID
        self.env.event_logger.assert_contains([
            {'uid': str(TEST_UID), 'name': 'action', 'value': self.action},
            {'uid': str(TEST_UID), 'name': 'alias.phonenumber.rm', 'value': TEST_PHONE_NUMBER.international},
            {'uid': str(TEST_UID), 'name': op_fmt + 'action', 'value': 'deleted'},
            {'uid': str(TEST_UID), 'name': op_fmt + 'type', 'value': 'dealiasify'},
            {'uid': str(TEST_UID), 'name': op_fmt + 'security_identity', 'value': str(SECURITY_IDENTITY)},
            {'uid': str(TEST_UID), 'name': phone_fmt + 'number', 'value': TEST_PHONE_NUMBER.e164},
            {'uid': str(TEST_UID), 'name': 'consumer', 'value': 'dev'},
            {'uid': str(TEST_UID), 'name': 'user_agent', 'value': TEST_USER_AGENT},
        ])

        entries = [self.env.statbox.entry('submitted', operation_id=str(TEST_OPERATION_ID))]
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry('phonenumber_alias_removed'),
            self.env.statbox.entry('phonenumber_alias_subscription_removed'),
            self.env.statbox.entry('phone_operation_applied'),
            self.env.statbox.entry('completed'),
        ])

        self.env.statbox.assert_has_written(entries)
