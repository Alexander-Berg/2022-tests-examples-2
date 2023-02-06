# -*- coding: utf-8 -*-

import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.views.bundle.phone.controllers import CONFIRM_BOUND_STATE
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
from passport.backend.core.models.phones.faker import (
    assert_secure_phone_bound,
    assert_simple_phone_bound,
    build_account,
    build_phone_being_bound,
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_invalid_user_ticket,
    fake_user_ticket,
)
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)

from .base import (
    BaseConfirmCommitterTestCase,
    BaseConfirmSubmitterTestCase,
    ConfirmCommitterLocalPhonenumberTestMixin,
    ConfirmCommitterSentCodeTestMixin,
    ConfirmCommitterTestMixin,
    ConfirmSubmitterAccountTestMixin,
    ConfirmSubmitterChangePasswordNewSecureNumberTestMixin,
    ConfirmSubmitterLocalPhonenumberMixin,
    ConfirmSubmitterSendSmsTestMixin,
    ConfirmSubmitterSpecificTestMixin,
    LITE_ACCOUNT_KWARGS,
    PDD_ACCOUNT_KWARGS,
    PHONISH_ACCOUNT_KWARGS,
    SOCIAL_ACCOUNT_KWARGS,
    TEST_DATE1,
    TEST_OPERATION_ID,
    TEST_OTHER_EXIST_PHONE_NUMBER,
    TEST_OTHER_EXIST_PHONE_NUMBER_DUMPED,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_PHONE_NUMBER,
    TEST_SESSION_ID,
    TEST_TAXI_APPLICATION,
    TEST_UID,
    TEST_USER_TICKET1,
)


@with_settings_hosts(
    YASMS_URL='http://localhost',
    SMS_VALIDATION_CODE_LENGTH=4,
    SMS_VALIDATION_RESEND_TIMEOUT=0,
    SMS_VALIDATION_MAX_SMS_COUNT=3,
    APP_ID_SPECIFIC_ROUTE_DENOMINATOR=1,
    APP_ID_TO_SMS_ROUTE={TEST_TAXI_APPLICATION: 'taxi'},
    **mock_counters()
)
class TestConfirmBoundSubmitter(BaseConfirmSubmitterTestCase,
                                ConfirmSubmitterAccountTestMixin,
                                ConfirmSubmitterSendSmsTestMixin,
                                ConfirmSubmitterSpecificTestMixin,
                                ConfirmSubmitterChangePasswordNewSecureNumberTestMixin,
                                ConfirmSubmitterLocalPhonenumberMixin):
    track_state = CONFIRM_BOUND_STATE
    url = '/1/bundle/phone/confirm_bound/submit/?consumer=dev'

    def setUp(self):
        super(TestConfirmBoundSubmitter, self).setUp()
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                **build_phone_bound(TEST_PHONE_ID1, TEST_PHONE_NUMBER.e164)
            ),
        )

    def query_params(self, exclude=None, **kwargs):
        base_params = {
            'number': TEST_PHONE_NUMBER.e164,
            'display_language': 'ru',
            'track_id': self.track_id,
            'uid': TEST_UID,
        }
        if exclude is not None:
            for key in exclude:
                del base_params[key]
        return merge_dicts(base_params, kwargs)

    def test_ok(self):
        self._test_ok({'uid': TEST_UID})

    def test_ok_user_ticket(self):
        ticket = fake_user_ticket(
            default_uid=TEST_UID,
            scopes=['passport:bind_phone'],
            uids=[TEST_UID],
        )
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([ticket])
        rv = self.make_request(
            self.query_params(exclude=['uid']),
            headers=merge_dicts(
                self.build_headers(),
                {'X-Ya-User-Ticket': TEST_USER_TICKET1},
            )
        )
        self.assert_ok_response(
            rv,
            **self.base_send_code_response
        )

        eq_(len(self.env.blackbox.requests), 1)
        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm_bound',
        })

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)
        ok_(track.country is None)
        eq_(track.uid, str(TEST_UID))

        self.assert_statbox_ok()

    def test_invalid_user_ticket(self):
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([fake_invalid_user_ticket(uids=[100500])])
        rv = self.make_request(
            self.query_params(exclude=['uid']),
            headers=merge_dicts(
                self.build_headers(),
                {'X-Ya-User-Ticket': TEST_USER_TICKET1},
            )
        )
        self.assert_error_response(rv, ['tvm_user_ticket.invalid'])

    def test_ok_with_pdd(self):
        self._test_ok(PDD_ACCOUNT_KWARGS)

    def test_ok_with_lite(self):
        self._test_ok(LITE_ACCOUNT_KWARGS)

    def test_ok_with_social(self):
        self._test_ok(SOCIAL_ACCOUNT_KWARGS)

    def test_ok_with_phonish(self):
        self._test_ok(PHONISH_ACCOUNT_KWARGS)

    def _test_ok(self, account_kwargs):
        account_kwargs = deep_merge(
            account_kwargs,
            build_phone_bound(TEST_PHONE_ID1, TEST_PHONE_NUMBER.e164),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**account_kwargs),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            self.base_send_code_response,
        )

        eq_(len(self.env.blackbox.requests), 1)
        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm_bound',
        })

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)
        ok_(track.country is None)
        eq_(track.uid, str(account_kwargs['uid']))

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('send_code', uid=str(account_kwargs['uid'])),
            self.env.statbox.entry('success', uid=str(account_kwargs['uid'])),
        ])

    def test_ok_by_sessionid(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login_id='login-id',
                **build_phone_bound(TEST_PHONE_ID1, TEST_PHONE_NUMBER.e164)
            ),
        )

        with settings_context(PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True):
            rv = self.make_request(self.query_params(sessionid=TEST_SESSION_ID, exclude=['uid']))

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            self.base_send_code_response,
        )

        eq_(len(self.env.blackbox.requests), 1)

        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm_bound',
        })

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)
        ok_(track.country is None)
        eq_(track.uid, str(TEST_UID))

        self.assert_statbox_ok(with_antifraud_score=True, with_check_cookies=True)
        self.assert_antifraud_score_called(login_id='login-id')

    def test_sessionid_expired(self):
        self._test_invalid_sessionid(BLACKBOX_SESSIONID_EXPIRED_STATUS)

    def test_sessionid_noauth(self):
        self._test_invalid_sessionid(BLACKBOX_SESSIONID_NOAUTH_STATUS)

    def test_sessionid_invalid(self):
        self._test_invalid_sessionid(BLACKBOX_SESSIONID_INVALID_STATUS)

    def _test_invalid_sessionid(self, status):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=status),
        )

        rv = self.make_request(
            self.query_params(sessionid=TEST_SESSION_ID, exclude=['uid']),
        )

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'sessionid.invalid']},
            ),
        )

        eq_(len(self.env.blackbox.requests), 1)
        eq_(len(self.env.yasms.requests), 0)

        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])

    def test_disabled_account_by_uid(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID, enabled=False),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'account.disabled']},
            ),
        )

        eq_(len(self.env.blackbox.requests), 1)
        eq_(len(self.env.yasms.requests), 0)

        self.env.statbox.assert_has_written([])

    def test_disabled_account_by_sessionid_with_account_info(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_DISABLED_STATUS),
        )

        rv = self.make_request(
            self.query_params(sessionid=TEST_SESSION_ID, exclude=['uid']),
        )

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'account.disabled']},
            ),
        )

        eq_(len(self.env.blackbox.requests), 1)
        eq_(len(self.env.yasms.requests), 0)

        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])

    def test_disabled_on_deletion_account_by_uid(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                enabled=False,
                attributes={'account.is_disabled': '2'},
            ),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'account.disabled_on_deletion']},
            ),
        )

        eq_(len(self.env.blackbox.requests), 1)
        eq_(len(self.env.yasms.requests), 0)

        self.env.statbox.assert_has_written([])

    def test_disabled_on_deletion_account_by_sessionid_with_account_info(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_DISABLED_STATUS,
                attributes={'account.is_disabled': '2'},
            ),
        )

        rv = self.make_request(
            self.query_params(sessionid=TEST_SESSION_ID, exclude=['uid']),
        )

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'account.disabled_on_deletion']},
            ),
        )

        eq_(len(self.env.blackbox.requests), 1)
        eq_(len(self.env.yasms.requests), 0)

        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])

    def test_without_phone(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'phone.not_found']},
            ),
        )

        eq_(len(self.env.blackbox.requests), 1)

        self.env.statbox.assert_has_written([])
        self.env.antifraud_logger.assert_has_written([])

    def test_with_unconfirmed_phone(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                **build_phone_being_bound(TEST_PHONE_ID1, TEST_PHONE_NUMBER.e164, TEST_OPERATION_ID)
            ),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'phone.not_found']},
            ),
        )

        eq_(len(self.env.blackbox.requests), 1)

        self.env.statbox.assert_has_written([])

    def test_change_password_send_sms_only_on_secure_phone_number(self):
        kwargs = deep_merge(
            build_phone_secured(TEST_PHONE_ID1, TEST_PHONE_NUMBER.e164),
            build_phone_bound(TEST_PHONE_ID2, TEST_OTHER_EXIST_PHONE_NUMBER.e164),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID, **kwargs),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_password_change = True
            track.has_secure_phone_number = True
            track.secure_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request(
            self.query_params(number=TEST_OTHER_EXIST_PHONE_NUMBER.e164),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        rv = json.loads(rv.data)
        eq_(rv['status'], 'error')
        eq_(rv['errors'], ['number.invalid'])

        self.env.statbox.assert_has_written([])

    def test_force_change_password_send_sms_only_on_secure_phone_number_and_hint_not_passed(self):
        kwargs = deep_merge(
            build_phone_secured(TEST_PHONE_ID1, TEST_PHONE_NUMBER.e164),
            build_phone_bound(TEST_PHONE_ID2, TEST_OTHER_EXIST_PHONE_NUMBER.e164),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID, **kwargs),
        )

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_password_change = True
            track.is_force_change_password = True
            track.has_secure_phone_number = True
            track.secure_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request(
            self.query_params(number=TEST_OTHER_EXIST_PHONE_NUMBER.e164),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        rv = json.loads(rv.data)
        eq_(rv['status'], 'error')
        eq_(rv['errors'], ['number.invalid'])

        self.env.statbox.assert_has_written([])

    def test_force_change_password_send_sms_only_on_secure_phone_number_and_hint_passed(self):
        kwargs = deep_merge(
            build_phone_secured(TEST_PHONE_ID1, TEST_PHONE_NUMBER.e164),
            build_phone_bound(TEST_PHONE_ID2, TEST_OTHER_EXIST_PHONE_NUMBER.e164),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID, **kwargs),
        )

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_password_change = True
            track.is_force_change_password = True
            track.is_fuzzy_hint_answer_checked = True
            track.has_secure_phone_number = True
            track.secure_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request(
            self.query_params(number=TEST_OTHER_EXIST_PHONE_NUMBER.e164),
        )

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_send_code_response,
                {
                    'track_id': self.track_id,
                    'number': TEST_OTHER_EXIST_PHONE_NUMBER_DUMPED,
                },
            ),
        )

        eq_(len(self.env.yasms.requests), 1)
        self.env.yasms.requests[0].assert_query_contains({
            'phone': TEST_OTHER_EXIST_PHONE_NUMBER.e164,
            'from_uid': str(TEST_UID),
            'identity': 'confirm_bound',
        })

    def test_force_change_password_send_sms_only_on_secure_phone_number_and_short_form_passed(self):
        kwargs = deep_merge(
            build_phone_secured(TEST_PHONE_ID1, TEST_PHONE_NUMBER.e164),
            build_phone_bound(TEST_PHONE_ID2, TEST_OTHER_EXIST_PHONE_NUMBER.e164),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID, **kwargs),
        )

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_password_change = True
            track.is_force_change_password = True
            track.is_short_form_factors_checked = True
            track.has_secure_phone_number = True
            track.secure_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request(
            self.query_params(number=TEST_OTHER_EXIST_PHONE_NUMBER.e164),
        )

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_send_code_response,
                {
                    'track_id': self.track_id,
                    'number': TEST_OTHER_EXIST_PHONE_NUMBER_DUMPED,
                },
            ),
        )

        eq_(len(self.env.yasms.requests), 1)
        self.env.yasms.requests[0].assert_query_contains({
            'phone': TEST_OTHER_EXIST_PHONE_NUMBER.e164,
            'from_uid': str(TEST_UID),
            'identity': 'confirm_bound',
        })


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    SMS_VALIDATION_MAX_CHECKS_COUNT=3,
)
class TestConfirmBoundCommitter(BaseConfirmCommitterTestCase,
                                ConfirmCommitterTestMixin,
                                ConfirmCommitterSentCodeTestMixin,
                                ConfirmCommitterLocalPhonenumberTestMixin):
    track_state = CONFIRM_BOUND_STATE
    url = '/1/bundle/phone/confirm_bound/commit/?consumer=dev'

    def setUp(self):
        super(TestConfirmBoundCommitter, self).setUp()
        self._given_account(use_db=False)

    def query_params(self, **kwargs):
        base_params = {
            'code': self.confirmation_code,
            'track_id': self.track_id,
        }

        return merge_dicts(base_params, kwargs)

    def test_ok(self):
        self._given_account()
        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data), self.base_response)

        self._assert_phone_confirmed(is_secure=False)

        eq_(len(self.env.blackbox.requests), 1)

        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_confirms_count.get(), 1)
        ok_(not track.phone_confirmation_confirms_count_limit_reached)
        eq_(track.phone_confirmation_first_checked, TimeNow())
        eq_(track.phone_confirmation_last_checked, TimeNow())

    def test_ok_with_secure_phone(self):
        self._given_account(is_phone_secure=True)
        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data), self.base_response)

        self._assert_phone_confirmed(is_secure=True)

        eq_(len(self.env.blackbox.requests), 1)

        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_confirms_count.get(), 1)
        ok_(not track.phone_confirmation_confirms_count_limit_reached)
        eq_(track.phone_confirmation_first_checked, TimeNow())
        eq_(track.phone_confirmation_last_checked, TimeNow())

    def test_without_phone(self):
        self._given_account(has_phone=False)
        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'phone.not_found']},
            ),
        )

        eq_(len(self.env.blackbox.requests), 1)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code'),
        ])
        self._assert_antifraud_log_ok()

    def test_with_not_bound_phone(self):
        self._given_account(is_phone_bound=False)
        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'phone.not_found']},
            ),
        )

        eq_(len(self.env.blackbox.requests), 1)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code'),
        ])
        self._assert_antifraud_log_ok()

    def test_already_confirmed(self):
        self._given_account()
        self.setup_track_for_commit(phone_confirmation_is_confirmed='1')

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), self.base_response)

        self._assert_phone_confirmed()
        eq_(len(self.env.blackbox.requests), 1)

    def test_account_not_found(self):
        self.env.blackbox.set_response_value('userinfo', blackbox_userinfo_response(uid=None))
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

        eq_(len(self.env.blackbox.requests), 1)
        self.env.statbox.assert_has_written([])
        self.env.antifraud_logger.assert_has_written([])

    def _assert_phone_confirmed(self, is_secure=False):
        if is_secure:
            assert_secure_phone_bound.check_db(
                self.env.db,
                uid=TEST_UID,
                phone_attributes={
                    'id': 1,
                    'created': TEST_DATE1,
                    'bound': TEST_DATE1,
                    'secured': TEST_DATE1,
                    'confirmed': DatetimeNow(),
                },
            )
        else:
            assert_simple_phone_bound.check_db(
                self.env.db,
                TEST_UID,
                {'id': TEST_PHONE_ID1, 'confirmed': DatetimeNow()},
            )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code'),
            self.env.statbox.entry('update_phone'),
            self.env.statbox.entry('success'),
        ])
        self._assert_antifraud_log_ok(is_secure)

        self.env.event_logger.assert_contains([
            {'uid': str(TEST_UID), 'name': 'action', 'value': 'confirm_bound'},
            {'uid': str(TEST_UID), 'name': 'phone.%d.action' % TEST_PHONE_ID1, 'value': 'changed'},
            {'uid': str(TEST_UID), 'name': 'phone.%d.number' % TEST_PHONE_ID1, 'value': TEST_PHONE_NUMBER.e164},
            {'uid': str(TEST_UID), 'name': 'phone.%d.confirmed' % TEST_PHONE_ID1, 'value': TimeNow()},
            {'uid': str(TEST_UID), 'name': 'consumer', 'value': 'dev'},
        ])

    def _given_account(self, use_db=True, has_phone=True, is_phone_bound=True, is_phone_secure=False):
        kwargs = {}
        if has_phone and is_phone_bound and is_phone_secure:
            kwargs = deep_merge(
                kwargs,
                build_phone_secured(
                    TEST_PHONE_ID1,
                    TEST_PHONE_NUMBER.e164,
                    phone_created=TEST_DATE1,
                    phone_bound=TEST_DATE1,
                    phone_confirmed=TEST_DATE1,
                    phone_secured=TEST_DATE1,
                ),
            )
        elif has_phone and is_phone_bound and not is_phone_secure:
            kwargs = deep_merge(
                kwargs,
                build_phone_bound(
                    TEST_PHONE_ID1,
                    TEST_PHONE_NUMBER.e164,
                    phone_created=TEST_DATE1,
                    phone_bound=TEST_DATE1,
                    phone_confirmed=TEST_DATE1,
                ),
            )
        elif has_phone and not is_phone_bound:
            kwargs = deep_merge(
                kwargs,
                build_phone_being_bound(
                    TEST_PHONE_ID1,
                    TEST_PHONE_NUMBER.e164,
                    TEST_OPERATION_ID,
                    phone_created=TEST_DATE1,
                ),
            )

        if use_db:
            db_faker = self.env.db
        else:
            db_faker = None

        build_account(
            db_faker=db_faker,
            blackbox_faker=self.env.blackbox,
            uid=TEST_UID,
            **kwargs
        )

    def _assert_antifraud_log_ok(self, is_secure_phone=False):
        self.env.antifraud_logger.assert_has_written(
            [
                self.env.antifraud_logger.entry(
                    'base',
                    channel='pharma',
                    sub_channel='dev',
                    status='OK',
                    is_secure_phone=is_secure_phone,
                    uid=str(TEST_UID),
                    external_id='track-{}'.format(self.track_id),
                    phone_confirmation_method='by_sms',
                    scenario='register',
                    request_path='/1/bundle/phone/confirm_bound/commit/',
                    request='auth',
                    user_phone=TEST_PHONE_NUMBER.e164,
                ),
            ],
        )
