# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)
import json
from time import time

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.emails import (
    assert_user_notified_about_alias_as_login_and_email_enabled,
    assert_user_notified_about_alias_as_login_and_email_owner_changed,
)
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.views.bundle.phone.controllers import CONFIRM_BOUND_SECURE_AND_ALIASIFY_STATE
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_SESSIONID_DISABLED_STATUS,
    BLACKBOX_SESSIONID_EXPIRED_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
    BLACKBOX_SESSIONID_NOAUTH_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.models.phones.faker import (
    assert_account_has_phonenumber_alias,
    assert_secure_phone_bound,
    build_phone_being_bound,
    build_phone_bound,
    build_phone_secured,
    build_remove_operation,
    event_lines_aliasify_operation_created,
    event_lines_aliasify_operation_deleted,
    event_lines_phonenumber_alias_given_out,
    event_lines_phonenumber_alias_removed,
)
from passport.backend.core.test.consts import (
    TEST_PASSWORD_HASH1,
    TEST_SOCIAL_LOGIN1,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)

from .base import (
    BaseConfirmCommitterTestCase,
    BaseConfirmSubmitterTestCase,
    blackbox_userinfo_mock,
    ConfirmCommitterSentCodeTestMixin,
    ConfirmCommitterTestMixin,
    ConfirmSubmitterChangePasswordNewSecureNumberTestMixin,
    ConfirmSubmitterSendSmsTestMixin,
    ConfirmSubmitterSpecificTestMixin,
    HEADERS_WITH_SESSIONID,
    LITE_ACCOUNT_KWARGS,
    MAILISH_ACCOUNT_KWARGS,
    PDD_ACCOUNT_KWARGS,
    PHONISH_ACCOUNT_KWARGS,
    SOCIAL_ACCOUNT_KWARGS,
    TEST_LOGIN,
    TEST_NOT_EXIST_PHONE_NUMBER,
    TEST_OPERATION_ID,
    TEST_OTHER_LOGIN,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_PHONE_NUMBER,
    TEST_SESSION_ID,
    TEST_TAXI_APPLICATION,
    TEST_UID,
)


@with_settings_hosts(
    APP_ID_SPECIFIC_ROUTE_DENOMINATOR=1,
    APP_ID_TO_SMS_ROUTE={TEST_TAXI_APPLICATION: 'taxi'},
    SMS_VALIDATION_CODE_LENGTH=4,
    SMS_VALIDATION_MAX_SMS_COUNT=3,
    SMS_VALIDATION_RESEND_TIMEOUT=0,
    YASMS_URL='http://localhost',
    **mock_counters()
)
class TestConfirmSecureBoundAndAliasifySubmitter(
        BaseConfirmSubmitterTestCase,
        ConfirmSubmitterSendSmsTestMixin,
        ConfirmSubmitterChangePasswordNewSecureNumberTestMixin,
        ConfirmSubmitterSpecificTestMixin):

    track_state = CONFIRM_BOUND_SECURE_AND_ALIASIFY_STATE
    url = '/1/bundle/phone/confirm_secure_bound_and_aliasify/submit/?consumer=dev'

    def setUp(self):
        super(TestConfirmSecureBoundAndAliasifySubmitter, self).setUp()

        self.setup_account(setup_db=False)

        # Переопределяю базовый ответ, потому что в запросе нет телефона
        self.base_response = {u'status': u'ok'}

    def setup_account(
        self,
        alias_type='portal',
        crypt_password=TEST_PASSWORD_HASH1,
        login=TEST_LOGIN,
        setup_db=True,
    ):
        account_args = dict(
            aliases={alias_type: login},
            crypt_password=crypt_password,
            login=login,
            uid=TEST_UID,
        )

        phone_args = build_phone_secured(
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER.e164,
        )

        userinfo_args = deep_merge(account_args, phone_args)
        userinfo_response = blackbox_userinfo_response(**userinfo_args)
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo_response)

        if setup_db:
            self.env.db.serialize(userinfo_response)

    def query_params(self, exclude=None, **kwargs):
        base_params = {
            'display_language': 'ru',
            'track_id': self.track_id,
            'uid': TEST_UID,
        }
        if exclude is not None:
            for key in exclude:
                del base_params[key]
        return merge_dicts(base_params, kwargs)

    def check_ok_track(
        self,
        track,
        sms_text=None,
        used_gate_ids=None,
        phone_number=TEST_PHONE_NUMBER,
        enable_phonenumber_alias_as_email=True,
    ):
        super(TestConfirmSecureBoundAndAliasifySubmitter, self).check_ok_track(
            track=track,
            used_gate_ids=used_gate_ids,
            phone_number=phone_number,
        )
        self.assertIs(track.enable_phonenumber_alias_as_email, enable_phonenumber_alias_as_email)

    def make_request_with_sessionid(self):
        return self.make_request(
            self.query_params(sessionid=TEST_SESSION_ID, exclude=['uid']),
        )

    def test_ok(self):
        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            self.base_send_code_response,
        )

        eq_(self.env.blackbox._mock.request.call_count, 1)

        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm_secure_bound_and_aliasify',
        })

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)
        ok_(track.country is None)
        eq_(track.uid, str(TEST_UID))

        self.assert_statbox_ok()

    def test_ok_by_sessionid(self):
        account_args = dict(
            uid=TEST_UID,
            attributes={'password.encrypted': '1:testpassword'},
        )

        phone_args = build_phone_secured(
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER.e164,
        )

        sessionid_args = deep_merge(account_args, phone_args)

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**sessionid_args),
        )

        rv = self.make_request_with_sessionid()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            self.base_send_code_response,
        )

        eq_(self.env.blackbox._mock.request.call_count, 1)

        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm_secure_bound_and_aliasify',
        })

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)
        ok_(track.country is None)
        eq_(track.uid, str(TEST_UID))

        self.assert_statbox_ok(with_check_cookies=True)

    def test_account_not_found(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [u'account.not_found'],
                u'track_id': str(self.track_id),
            },
        )
        eq_(self.env.blackbox._mock.request.call_count, 1)

        self.env.statbox.assert_has_written([])

    def test_invalid_sessionid(self):
        for status in [BLACKBOX_SESSIONID_EXPIRED_STATUS,
                       BLACKBOX_SESSIONID_NOAUTH_STATUS,
                       BLACKBOX_SESSIONID_INVALID_STATUS]:
            self.env.blackbox.set_blackbox_response_value(
                'sessionid',
                blackbox_sessionid_multi_response(status=status),
            )

            rv = self.make_request_with_sessionid()

            eq_(rv.status_code, 200, rv.data)
            eq_(
                json.loads(rv.data),
                {
                    u'status': u'error',
                    u'errors': [u'sessionid.invalid'],
                    u'track_id': str(self.track_id),
                },
            )

        eq_(self.env.blackbox._mock.request.call_count, 3)

        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')] * 3)

    def test_disabled_account_on_deletion_by_uid(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                enabled=False,
            ),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [u'account.disabled'],
                u'track_id': str(self.track_id),
            },
        )

        eq_(self.env.blackbox._mock.request.call_count, 1)

        self.env.statbox.assert_has_written([])

    def test_disabled_account_by_sessionid(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_DISABLED_STATUS),
        )

        rv = self.make_request_with_sessionid()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [u'account.disabled'],
                u'track_id': str(self.track_id),
            },
        )

        eq_(self.env.blackbox._mock.request.call_count, 1)

        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])

    def test_disabled_account_by_uid(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [u'account.disabled_on_deletion'],
                u'track_id': str(self.track_id),
            },
        )

        eq_(self.env.blackbox._mock.request.call_count, 1)

        self.env.statbox.assert_has_written([])

    def test_disabled_on_deletion_account_by_sessionid(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_DISABLED_STATUS,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )

        rv = self.make_request_with_sessionid()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [u'account.disabled_on_deletion'],
                u'track_id': str(self.track_id),
            },
        )

        eq_(self.env.blackbox._mock.request.call_count, 1)

        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])

    def test_without_secure_phone(self):
        account_args = dict(
            uid=TEST_UID,
        )

        phone_args = build_phone_bound(
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER.e164,
        )

        userinfo_args = deep_merge(account_args, phone_args)

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**userinfo_args),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            {u'status': u'error', u'errors': [u'phone_secure.not_found'], u'track_id': str(self.track_id)},
        )
        eq_(self.env.blackbox._mock.request.call_count, 1)

        self.env.statbox.assert_has_written([])

    def test_with_alias_on_account(self):
        account_args = dict(
            uid=TEST_UID,
            aliases={
                'portal': TEST_LOGIN,
                'phonenumber': TEST_PHONE_NUMBER.digital,
            },
            attributes={'password.encrypted': '1:testpassword'},
        )

        phone_args = build_phone_secured(
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER.e164,
        )

        userinfo_args = deep_merge(account_args, phone_args)

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**userinfo_args),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'phone_alias.exist']},
            ),
        )

        self.env.statbox.assert_has_written([])

    def test_account_invalid_type_error(self):
        for account_kwargs in (
            PDD_ACCOUNT_KWARGS,
            LITE_ACCOUNT_KWARGS,
            PHONISH_ACCOUNT_KWARGS,
            SOCIAL_ACCOUNT_KWARGS,
            MAILISH_ACCOUNT_KWARGS,
        ):
            self.env.blackbox.set_blackbox_response_value(
                'userinfo',
                blackbox_userinfo_response(**account_kwargs),
            )

            rv = self.make_request()
            eq_(rv.status_code, 200, rv.data)
            eq_(
                json.loads(rv.data),
                {
                    u'status': u'error',
                    u'errors': [u'account.invalid_type'],
                    u'track_id': self.track_id,
                },
            )

            self.env.statbox.assert_has_written([])

    def test_enable_alias_as_email(self):
        rv = self.make_request(self.query_params(enable_alias_as_email='1'))

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            self.base_send_code_response,
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)

    def test_disable_alias_as_email(self):
        rv = self.make_request(self.query_params(enable_alias_as_email='0'))

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            self.base_send_code_response,
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track, enable_phonenumber_alias_as_email=False)

    def test_passwordless_account(self):
        self.setup_account(
            alias_type='social',
            crypt_password=None,
            login=TEST_SOCIAL_LOGIN1,
        )

        rv = self.make_request(self.query_params(enable_alias_as_email='0'))

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            self.base_send_code_response,
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track, enable_phonenumber_alias_as_email=False)


@with_settings_hosts(
    SMS_VALIDATION_MAX_CHECKS_COUNT=5,
    YASMS_URL='http://localhost/',
)
class TestConfirmSecureBoundAndAliasifyCommitter(BaseConfirmCommitterTestCase,
                                                 ConfirmCommitterTestMixin,
                                                 ConfirmCommitterSentCodeTestMixin,
                                                 EmailTestMixin):

    track_state = CONFIRM_BOUND_SECURE_AND_ALIASIFY_STATE
    url = '/1/bundle/phone/confirm_secure_bound_and_aliasify/commit/?consumer=dev'

    def setUp(self):
        super(TestConfirmSecureBoundAndAliasifyCommitter, self).setUp()
        self.env.statbox.bind_entry(
            'phone_confirmed',
            _inherit_from=['phone_confirmed', 'local_base'],
        )
        self.env.statbox.bind_entry(
            'phone_operation_applied',
            _inherit_from=['phone_operation_applied', 'local_base'],
        )

    def query_params(self, **kwargs):
        base_params = {
            'code': self.confirmation_code,
            'password': 'testpassword',
            'track_id': self.track_id,
        }

        return merge_dicts(base_params, kwargs)

    def assert_track_ok(self):
        track = self.track_manager.read(self.track_id)

        ok_(track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_confirms_count.get(), 1)
        ok_(not track.phone_confirmation_confirms_count_limit_reached)
        eq_(track.phone_confirmation_first_checked, TimeNow())
        eq_(track.phone_confirmation_last_checked, TimeNow())

    def setup_account_with_phone(self, userinfo=None, additional_userinfo=None):
        userinfo_response = userinfo or blackbox_userinfo_response(
            **deep_merge(
                dict(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                    emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')],
                ),
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER.e164,
                    phone_confirmed=datetime.now(),
                ),
            )
        )

        self.env.db.serialize(userinfo_response)

        if additional_userinfo is None:
            additional_userinfo = blackbox_userinfo_response(uid=None)
        else:
            self.env.db.serialize(additional_userinfo)

        side_effect = [userinfo_response, additional_userinfo]

        self.env.blackbox.set_blackbox_response_side_effect('userinfo', side_effect)

        return userinfo_response

    def setup_track_for_commit(
        self,
        exclude=None,
        _defaults=None,
        **kwargs
    ):
        defaults = dict(
            enable_phonenumber_alias_as_email='1',
        )
        if _defaults:
            defaults.update(_defaults)

        super(TestConfirmSecureBoundAndAliasifyCommitter, self).setup_track_for_commit(
            exclude=exclude,
            _defaults=defaults,
            **kwargs
        )

    def assert_account_has_phonenumber_alias(self, enable_search=True):
        assert_account_has_phonenumber_alias(
            db_faker=self.env.db,
            uid=TEST_UID,
            alias=TEST_PHONE_NUMBER.digital,
            enable_search=enable_search,
        )

    def test_ok(self):
        self.setup_account_with_phone()

        self.setup_track_for_commit()
        self.env.db.check_missing('aliases', 'phonenumber', uid=TEST_UID, db='passportdbcentral')

        rv = self.make_request()

        self.assert_ok_response(rv, **self.number_response)

        eq_(len(self.env.blackbox.requests), 2)

        self.assert_account_has_phonenumber_alias()
        self.env.db.check('aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=TEST_UID, db='passportdbcentral')
        assert_secure_phone_bound.check_db(
            db_faker=self.env.db,
            uid=TEST_UID,
            phone_attributes={'id': TEST_PHONE_ID1},
        )
        self.env.db.check_missing(
            'phone_operations',
            phone_id=TEST_PHONE_ID1,
            uid=TEST_UID,
            db='passportdbshard1',
        )

        self.env.event_logger.assert_contains(
            event_lines_aliasify_operation_created(
                uid=TEST_UID,
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER,
                operation_id=1,
                operation_ttl=timedelta(seconds=60),
            ) +
            event_lines_aliasify_operation_deleted(
                action='confirm_secure_bound_and_aliasify',
                uid=TEST_UID,
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER,
                operation_id=1,
            ) +
            event_lines_phonenumber_alias_given_out(
                action='confirm_secure_bound_and_aliasify',
                uid=TEST_UID,
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER,
            ),
        )

        self.assert_track_ok()

        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry('enter_code'),
                self.env.statbox.entry('aliasify_secure_operation_created'),
            ] +
            self.aliasify_statbox_values(login=TEST_LOGIN) +
            [
                self.env.statbox.entry('phone_confirmed'),
                self.env.statbox.entry('phone_operation_applied'),
                self.env.statbox.entry('update_phone'),
                self.env.statbox.entry('success'),
            ],
        )

    def test_ok_with_delete_alias(self):
        self.setup_track_for_commit()

        blackbox_response_with_alias = blackbox_userinfo_response(
            **deep_merge(
                dict(
                    uid=2,
                    login=TEST_OTHER_LOGIN,
                    aliases={'portal': TEST_OTHER_LOGIN},
                ),
                build_phone_secured(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER.e164,
                    phone_confirmed=datetime.now(),
                    is_alias=True,
                ),
            )
        )
        self.setup_account_with_phone(additional_userinfo=blackbox_response_with_alias)

        self.env.db.check_missing('aliases', 'phonenumber', uid=TEST_UID, db='passportdbcentral')
        self.env.db.check('aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=2, db='passportdbcentral')

        rv = self.make_request()

        self.assert_ok_response(rv, **self.number_response)

        eq_(self.env.blackbox._mock.request.call_count, 2)

        self.env.db.check_missing('aliases', 'phonenumber', uid=2, db='passportdbcentral')
        self.env.db.check('removed_aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=2, db='passportdbcentral')
        self.env.db.check('aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=TEST_UID, db='passportdbcentral')
        assert_secure_phone_bound.check_db(
            db_faker=self.env.db,
            uid=TEST_UID,
            phone_attributes={'id': TEST_PHONE_ID1},
        )
        self.env.db.check_missing(
            'phone_operations',
            phone_id=TEST_PHONE_ID2,
            uid=TEST_UID,
            db='passportdbshard1',
        )

        self.env.event_logger.assert_contains(
            event_lines_aliasify_operation_created(
                uid=TEST_UID,
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER,
                operation_id=1,
                operation_ttl=timedelta(seconds=60),
            ) +
            event_lines_aliasify_operation_deleted(
                action='confirm_secure_bound_and_aliasify',
                uid=TEST_UID,
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER,
                operation_id=1,
            ) +
            event_lines_phonenumber_alias_given_out(
                action='confirm_secure_bound_and_aliasify',
                uid=TEST_UID,
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER,
            ) +
            event_lines_phonenumber_alias_removed(
                uid=2,
                phone_number=TEST_PHONE_NUMBER,
            ),
        )

        self.assert_track_ok()

        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry('enter_code'),
                self.env.statbox.entry('aliasify_secure_operation_created'),
            ] +
            self.dealiasify_statbox_values() +
            self.aliasify_statbox_values(dealiasify=True, login=TEST_LOGIN) +
            [
                self.env.statbox.entry('phone_confirmed'),
                self.env.statbox.entry('phone_operation_applied'),
                self.env.statbox.entry('update_phone'),
                self.env.statbox.entry('success'),
            ],
        )

    def _test_ok_with_delete_alias_and_emails(self, submit_language=None):
        self.setup_track_for_commit()

        userinfo1 = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            emails=[
                self.create_native_email('user1', 'yandex.ru'),
            ],
            **build_phone_secured(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER.e164,
                phone_confirmed=datetime.now(),
            )
        )
        userinfo2 = blackbox_userinfo_response(
            **deep_merge(
                dict(
                    uid='2',
                    login=TEST_OTHER_LOGIN,
                    aliases={
                        'portal': TEST_OTHER_LOGIN,
                        'phonenumber': TEST_PHONE_NUMBER.digital,
                    },
                    emails=[
                        self.create_native_email('user2', 'yandex.ru'),
                        self.create_validated_external_email('user2', 'gmail.com'),
                    ],
                ),
                build_phone_secured(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER.e164,
                    phone_confirmed=datetime.now(),
                    is_alias=True,
                ),
            )
        )
        self.setup_account_with_phone(
            userinfo=userinfo1,
            additional_userinfo=userinfo2,
        )

        language = 'ru'
        if submit_language:
            with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
                track.display_language = submit_language
            language = submit_language

        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data), self.base_response)

        eq_(len(self.env.mailer.messages), 3)
        assert_user_notified_about_alias_as_login_and_email_owner_changed(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address='user2@gmail.com',
            firstname='\u0414',
            login=TEST_OTHER_LOGIN,
            portal_email=TEST_OTHER_LOGIN + '@yandex.ru',
            phonenumber_alias=TEST_PHONE_NUMBER.digital,
        )
        assert_user_notified_about_alias_as_login_and_email_owner_changed(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address='user2@yandex.ru',
            firstname='\u0414',
            login=TEST_OTHER_LOGIN,
            portal_email=TEST_OTHER_LOGIN + '@yandex.ru',
            phonenumber_alias=TEST_PHONE_NUMBER.digital,
        )
        assert_user_notified_about_alias_as_login_and_email_enabled(
            mailer_faker=self.env.mailer,
            language=language,
            email_address='user1@yandex.ru',
            firstname='\u0414',
            login=TEST_LOGIN,
            portal_email=TEST_LOGIN + '@yandex.ru',
            phonenumber_alias=TEST_PHONE_NUMBER.digital,
        )

        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry('enter_code'),
                self.env.statbox.entry('aliasify_secure_operation_created'),
            ] +
            self.dealiasify_statbox_values() +
            self.aliasify_statbox_values(dealiasify=True, login=TEST_LOGIN) +
            [
                self.env.statbox.entry('phone_confirmed'),
                self.env.statbox.entry('phone_operation_applied'),
                self.env.statbox.entry('update_phone'),
                self.env.statbox.entry('success'),
            ],
        )

    def test_ok_with_delete_alias_and_emails(self):
        self._test_ok_with_delete_alias_and_emails()

    def test_ok_with_delete_alias_and_emails_in_custom_display_language(self):
        self._test_ok_with_delete_alias_and_emails(submit_language='en')

    def test_operation_exists_error(self):
        self.setup_track_for_commit()

        userinfo = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            emails=[self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru')],
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER.e164,
                    phone_confirmed=datetime.now(),
                ),
                build_remove_operation(
                    operation_id=TEST_OPERATION_ID,
                    phone_id=TEST_PHONE_ID1,
                ),
            )
        )
        self.setup_account_with_phone(userinfo=userinfo)

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'operation.secure_operation_exists']},
            ),
        )

    def test_without_secure_phone(self):
        self.setup_track_for_commit()

        userinfo = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            **build_phone_bound(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER.e164,
                phone_confirmed=datetime.now(),
            )
        )
        self.setup_account_with_phone(userinfo=userinfo)

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'phone_secure.not_found']},
            ),
        )
        eq_(self.env.blackbox._mock.request.call_count, 1)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code'),
        ])

    def test_with_secure_unconfirmed_phone(self):
        self.setup_track_for_commit()

        userinfo = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            **build_phone_being_bound(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER.e164,
                operation_id=TEST_OPERATION_ID,
            )
        )
        self.setup_account_with_phone(userinfo=userinfo)

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'phone_secure.not_found']},
            ),
        )
        eq_(self.env.blackbox._mock.request.call_count, 1)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code'),
        ])

    def test_with_changed_secure_phone(self):
        self.setup_track_for_commit()

        userinfo = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            **build_phone_secured(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_NOT_EXIST_PHONE_NUMBER.e164,
            )
        )
        self.setup_account_with_phone(userinfo=userinfo)

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'phone_secure.not_found']},
            ),
        )
        eq_(self.env.blackbox._mock.request.call_count, 1)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code'),
        ])

    def test_alias_already_exists(self):
        self.setup_track_for_commit()

        userinfo = blackbox_userinfo_response(
            **deep_merge(
                dict(
                    uid=TEST_UID,
                    login=TEST_OTHER_LOGIN,
                    aliases={
                        'portal': TEST_OTHER_LOGIN,
                        'phonenumber': TEST_PHONE_NUMBER.digital,
                    },
                    attributes={'account.enable_search_by_phone_alias': '1'},
                ),
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER.e164,
                ),
            )
        )
        self.setup_account_with_phone(userinfo=userinfo)

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'phone_alias.exist']},
            ),
        )

        eq_(self.env.blackbox._mock.request.call_count, 1)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code'),
        ])

    def test_already_confirmed_and_validation_period(self):
        userinfo = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            emails=[self.create_native_email(TEST_LOGIN, 'yandex.ru')],
            **build_phone_secured(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER.e164,
                phone_confirmed=datetime.fromtimestamp(time() - 20),
            )
        )
        self.setup_account_with_phone(userinfo=userinfo)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_confirms_count.incr()
            track.uid = TEST_UID

        self.setup_track_for_commit(
            phone_confirmation_is_confirmed='1',
            phone_confirmation_confirms_count='1',
        )

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), self.base_response)
        eq_(self.env.blackbox._mock.request.call_count, 2)

        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry('enter_code'),
                self.env.statbox.entry('aliasify_secure_operation_created'),
            ] +
            self.aliasify_statbox_values(validation_period=20, login=TEST_LOGIN) +
            [
                self.env.statbox.entry('phone_confirmed'),
                self.env.statbox.entry('phone_operation_applied'),
                self.env.statbox.entry('update_phone'),
                self.env.statbox.entry('success'),
            ],
        )

    def test_account_not_found(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            blackbox_userinfo_mock(found_by_login=False, not_found=True),
        )

        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'account.not_found']},
            ),
        )

        eq_(self.env.blackbox._mock.request.call_count, 1)
        eq_(len(self.env.yasms.requests), 0)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code'),
        ])

    def test_dberror_on_delete_alias(self):
        userinfo2 = blackbox_userinfo_response(
            **deep_merge(
                dict(
                    uid='2',
                    login=TEST_OTHER_LOGIN,
                    aliases={
                        'portal': TEST_OTHER_LOGIN,
                        'phonenumber': TEST_PHONE_NUMBER.digital,
                    },
                    attributes={'account.enable_search_by_phone_alias': '1'},
                ),
                build_phone_secured(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER.e164,
                ),
            )
        )
        self.setup_account_with_phone(additional_userinfo=userinfo2)

        self.env.db.check('aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=2, db='passportdbcentral')

        self.setup_track_for_commit()

        self.env.db.set_side_effect_for_db('passportdbcentral', DBError)
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError)

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {
                    'status': 'error',
                    'errors': ['backend.database_failed'],
                },
            ),
        )

        eq_(self.env.blackbox._mock.request.call_count, 1)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code'),
        ])

    def test_dberror_on_create_alias(self):
        self.setup_account_with_phone()

        self.env.db.check_missing('aliases', 'phonenumber', uid=TEST_UID, db='passportdbcentral')

        self.setup_track_for_commit()

        self.env.db.set_side_effect_for_db('passportdbcentral', DBError)
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError)

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {
                    'status': 'error',
                    'errors': ['backend.database_failed'],
                },
            ),
        )

        eq_(self.env.blackbox._mock.request.call_count, 1)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code'),
        ])

    def test_account_invalid_type_error(self):
        for account_kwargs in (
            PDD_ACCOUNT_KWARGS,
            LITE_ACCOUNT_KWARGS,
            PHONISH_ACCOUNT_KWARGS,
            SOCIAL_ACCOUNT_KWARGS,
            MAILISH_ACCOUNT_KWARGS,
        ):
            self.env.blackbox.set_blackbox_response_side_effect(
                'userinfo',
                [blackbox_userinfo_response(**account_kwargs)],
            )

            self.setup_track_for_commit()
            rv = self.make_request()
            eq_(rv.status_code, 200, rv.data)
            eq_(
                json.loads(rv.data),
                merge_dicts(
                    self.base_response,
                    {
                        u'status': u'error',
                        u'errors': [u'account.invalid_type'],
                    },
                ),
            )

    def test_alias_as_email_disabled(self):
        self.setup_account_with_phone()
        self.setup_track_for_commit(enable_phonenumber_alias_as_email='0')

        rv = self.make_request()

        self.assert_ok_response(rv, **self.number_response)

        self.assert_account_has_phonenumber_alias(enable_search=False)
        self.assert_track_ok()

    def test_passwordless_account(self):
        userinfo = blackbox_userinfo_response(
            **deep_merge(
                dict(
                    uid=TEST_UID,
                    login=TEST_SOCIAL_LOGIN1,
                    aliases={'social': TEST_SOCIAL_LOGIN1},
                ),
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER.e164,
                    phone_confirmed=datetime.now(),
                ),
            )
        )
        self.setup_account_with_phone(userinfo=userinfo)

        self.setup_track_for_commit(enable_phonenumber_alias_as_email='0')

        rv = self.make_request()

        self.assert_ok_response(rv, **self.number_response)

        self.assert_account_has_phonenumber_alias(enable_search=False)
        self.assert_track_ok()


class TestConfirmSecureBoundAndAliasifySubmitterV2(TestConfirmSecureBoundAndAliasifySubmitter):
    url = '/2/bundle/phone/confirm_secure_bound_and_aliasify/submit/?consumer=dev'

    def make_request_with_sessionid(self):
        return self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.build_headers(HEADERS_WITH_SESSIONID),
        )


class TestConfirmSecureBoundAndAliasifyCommitterV2(TestConfirmSecureBoundAndAliasifyCommitter):
    url = '/2/bundle/phone/confirm_secure_bound_and_aliasify/commit/?consumer=dev'
