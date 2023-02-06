# -*- coding: utf-8 -*-

import json

from nose.tools import eq_
from passport.backend.api.common.phone import PhoneAntifraudFeatures
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.tests.views.bundle.restore.test.test_base import RestoreTestUtilsMixin
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_bindings_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.counters import login_restore_counter
from passport.backend.core.models.account import (
    ACCOUNT_DISABLED_ON_DELETION,
    ACCOUNT_ENABLED,
)
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import deep_merge


eq_ = iterdiff(eq_)


TEST_KOLMOGOR_KEYSPACE_COUNTERS = 'octopus-calls-counters'
TEST_KOLMOGOR_KEYSPACE_FLAG = 'octopus-calls-flag'
KOLMOGOR_COUNTER_SESSIONS_CREATED = 'sessions_created'
KOLMOGOR_COUNTER_CALLS_FAILED = 'calls_failed'
KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG = 'calls_shut_down'


@with_settings_hosts(
    ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD=TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD,
)
class LoginRestoreBaseTestCase(BaseBundleTestViews, RestoreTestUtilsMixin):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value(mock_grants(grants={'login_restore': ['base']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('restore')
        self.setup_statbox_templates()
        track = self.track_manager.read(self.track_id)
        self.orig_track = track.snapshot()

        self.env.kolmogor.set_response_value('inc', 'OK')
        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 0,
        }
        counters = {
            KOLMOGOR_COUNTER_SESSIONS_CREATED: 5,
            KOLMOGOR_COUNTER_CALLS_FAILED: 0,
        }
        self.env.kolmogor.set_response_side_effect('get', [flag, counters])

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager
        del self.orig_track

    def setup_statbox_templates(self, sms_retriever_kwargs=None):
        # записи, которые относятся к форматированию SMS под SmsRetriever в Андроиде
        sms_retriever_kwargs = sms_retriever_kwargs or {}

        self.env.statbox.bind_entry(
            'local_base',
            mode='login_restore',
            track_id=self.track_id,
            ip=TEST_IP,
            host=TEST_HOST,
            user_agent=TEST_USER_AGENT,
            consumer='dev',
            yandexuid=TEST_YANDEXUID_COOKIE,
            step=self.restore_step,
        )
        self.env.statbox.bind_entry(
            'finished_with_error',
            _inherit_from='local_base',
            action='finished_with_error',
        )
        self.env.statbox.bind_entry(
            'finished_with_error_with_sms',
            _inherit_from='finished_with_error',
        )
        self.env.statbox.bind_entry(
            'passed',
            _inherit_from='local_base',
            action='passed',
        )
        self.env.statbox.bind_entry(
            'code_sent',
            _inherit_from='local_base',
            action='send_confirmation_code.code_sent',
            number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            sms_count='1',
            sms_id='1',
            **sms_retriever_kwargs
        )
        self.env.statbox.bind_entry(
            'call_with_code',
            _inherit_from='local_base',
            action='call_with_code',
            number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            calls_count='1',
            call_session_id='123',
        )
        self.env.statbox.bind_entry(
            'flash_call',
            _inherit_from='local_base',
            action='flash_call',
            number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            calls_count='1',
            call_session_id='123',
        )
        self.env.statbox.bind_entry(
            'enter_code',
            _inherit_from='local_base',
            action='enter_code',
            operation='confirm',
        )
        self.env.statbox.bind_entry(
            'base_pharma',
            _inherit_from=['local_base'],
            action='send_confirmation_code',
            antifraud_reason='some-reason',
            antifraud_tags='',
            number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            scenario='restore',
        )
        self.env.statbox.bind_entry(
            'pharma_allowed',
            _inherit_from=['base_pharma'],
            antifraud_action='ALLOW',
        )
        self.env.statbox.bind_entry(
            'pharma_denied',
            _inherit_from=['base_pharma'],
            antifraud_action='DENY',
            error='antifraud_score_deny',
            mask_denial='0',
            status='error',
        )

    def build_account(self, registered_at=TEST_DEFAULT_REGISTRATION_DATETIME, disabled_status=ACCOUNT_ENABLED,
                      deletion_started_at=None, bound_at=TEST_PHONE_BOUND, confirmed_at=TEST_PHONE_CONFIRMED,
                      secured_at=TEST_PHONE_SECURED,
                      alias_type='portal', login=TEST_DEFAULT_LOGIN, uid=TEST_DEFAULT_UID,
                      phone_id=TEST_PHONE_ID, phone_number=TEST_PHONE_OBJECT,
                      firstname=TEST_DEFAULT_FIRSTNAME, lastname=TEST_DEFAULT_LASTNAME,
                      has_plus=False,has_family=False, is_child=False,
                      **kwargs):
        kwargs.update({
            'uid': uid,
            'login': login,
            'dbfields': {
                'userinfo.reg_date.uid': registered_at,
            },
            'attributes': {
                'person.firstname': firstname,
                'person.lastname': lastname,
                'account.is_disabled': str(disabled_status),
            },
            'aliases': {
                alias_type: login,
            },
            'default_avatar_key': TEST_AVATAR_KEY,
        })
        if has_plus:
            kwargs['attributes']['account.have_plus'] = '1'
        if is_child:
            kwargs['attributes']['account.is_child'] = '1'
        if has_family:
            kwargs['family_info'] = {
                'family_id': 'f1',
                'admin_uid': 42,
            }
        if deletion_started_at:
            kwargs['attributes']['account.deletion_operation_started_at'] = deletion_started_at
        if secured_at is not None:
            kwargs = deep_merge(
                kwargs,
                build_phone_secured(
                    phone_id=phone_id,
                    phone_number=phone_number.e164,
                    phone_created=bound_at,
                    phone_bound=bound_at,
                    phone_confirmed=confirmed_at,
                    phone_secured=secured_at,
                ),
            )
        elif bound_at is not None:
            kwargs = deep_merge(
                kwargs,
                build_phone_bound(
                    phone_id=phone_id,
                    phone_number=phone_number.e164,
                    phone_created=bound_at,
                    phone_bound=bound_at,
                    phone_confirmed=confirmed_at,
                ),
            )

        return kwargs

    def setup_accounts(self, accounts):
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple(accounts),
        )

    def setup_phone_bindings(self, accounts):
        phone_bindings = []
        for account in accounts:
            account_bindings = account.get('phone_bindings', [])
            for binding in account_bindings:
                if binding['number'] == TEST_PHONE_OBJECT.e164:
                    phone_bindings.append(
                        dict(
                            binding,
                            uid=account['uid'],
                        ),
                    )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response(phone_bindings),
        )

    def assert_blackbox_called(self, phone=TEST_PHONE_OBJECT.e164, uids=None, call_index=0):
        uids = uids or [TEST_DEFAULT_UID]

        self.env.blackbox.get_requests_by_method('phone_bindings')[call_index].assert_query_contains(
            {
                'method': 'phone_bindings',
                'type': 'current',
                'numbers': phone,
            },
        )
        self.env.blackbox.get_requests_by_method('userinfo')[call_index].assert_post_data_contains(
            {
                'method': 'userinfo',
                'uid': ','.join(map(str, uids)),
                'emails': 'getall',
                'getphones': 'all',
                'getphoneoperations': '1',
                'getphonebindings': 'all',
                'aliases': 'all_with_hidden',
            },
        )
        self.env.blackbox.get_requests_by_method('userinfo')[call_index].assert_contains_attributes({
            'phones.default',
            'phones.secure',
        })

    def assert_kolmogor_called(self, calls=1, with_inc=True, keys='sessions_created'):
        eq_(len(self.env.kolmogor.requests), calls)
        if with_inc:
            self.env.kolmogor.requests[-1].assert_properties_equal(
                method='POST',
                url='http://localhost/inc',
                post_args={'space': TEST_KOLMOGOR_KEYSPACE_COUNTERS, 'keys': keys},
            )

    def assert_ok_pharma_request(self, request, extra_features=None):
        request_data = json.loads(request.post_args)
        features = PhoneAntifraudFeatures.default(
            sub_channel='dev',
            user_phone_number=TEST_PHONE_OBJECT,
        )
        features.external_id = 'track-{}'.format(self.track_id)
        features.phone_confirmation_method = 'by_sms'
        features.t = TimeNow(as_milliseconds=True)
        features.request_path = self.default_url.split('?')[0]
        features.scenario = 'restore'
        features.add_headers_features(mock_headers(**self.http_headers))
        features.add_dict_features(extra_features)
        assert request_data == features.as_score_dict()


class CommonTestsMixin(object):
    test_invalid_track_state_options = {}

    def test_invalid_track_state(self):
        """Невалидное для данной ручки состояние в треке"""
        self.set_track_values(**self.test_invalid_track_state_options)

        resp = self.make_request()

        self.assert_error_response(resp, ['track.invalid_state'])
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([])

    test_action_not_required_options = {}

    def test_action_not_required(self):
        """Действие уже выполнено"""
        if self.test_action_not_required_options is None:
            return

        self.set_track_values(**self.test_action_not_required_options)

        resp = self.make_request()

        self.assert_error_response(resp, ['action.not_required'])
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([])

    def test_phone_limit_exceeded(self):
        """Счетчик по данному телефону перегрет"""
        self.set_track_values()
        buckets = login_restore_counter.get_per_phone_buckets()
        for _ in range(buckets.limit):
            buckets.incr(TEST_PHONE_OBJECT.digital)

        resp = self.make_request()

        self.assert_error_response(resp, ['rate.limit_exceeded'])
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='rate.limit_exceeded',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                rate_limited_by='phone',
            ),
        ])

    def test_ip_limit_exceeded(self):
        """Счетчик по IP перегрет"""
        self.set_track_values()
        buckets = login_restore_counter.get_per_ip_buckets()
        for _ in range(buckets.limit):
            buckets.incr(TEST_IP)

        resp = self.make_request()

        self.assert_error_response(resp, ['rate.limit_exceeded'])
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='rate.limit_exceeded',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                rate_limited_by='ip',
            ),
        ])

    invalid_phone_increases_ip_counter = False

    def test_no_phone_bindings_found(self):
        """По номеру не найдены привязки"""
        self.set_track_values()
        self.setup_phone_bindings([])

        resp = self.make_request()

        self.assert_error_response(resp, ['phone_secure.not_found'])
        self.assert_track_updated(is_captcha_checked=False, is_captcha_recognized=False)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='phone_secure.not_found',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])

        ip_buckets = login_restore_counter.get_per_ip_buckets()
        eq_(ip_buckets.get(TEST_IP), 1 if self.invalid_phone_increases_ip_counter else 0)
        phone_buckets = login_restore_counter.get_per_phone_buckets()
        eq_(phone_buckets.get(TEST_PHONE_OBJECT.digital), 0)

    def test_no_suitable_accounts_found(self):
        """По номеру не найдены подходящие аккаунты"""
        self.set_track_values()
        deletion_started_at = time.time() - TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD.total_seconds()
        accounts = [
            self.build_account(uid=1, alias_type='phonish'),
            self.build_account(uid=2, firstname=None),
            self.build_account(uid=3, lastname=None),
            self.build_account(uid=4, disabled_status=ACCOUNT_DISABLED_ON_DELETION),  # времени удаления нет
            self.build_account(uid=5, disabled_status=ACCOUNT_DISABLED_ON_DELETION, deletion_started_at=deletion_started_at),
            self.build_account(uid=6, confirmed_at=None, bound_at=None, secured_at=None),
            self.build_account(uid=7, secured_at=None),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request()

        self.assert_error_response(resp, ['phone_secure.not_found'])
        self.assert_track_updated(is_captcha_checked=False, is_captcha_recognized=False)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='phone_secure.not_found',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])
        self.assert_blackbox_called(uids=[1, 2, 3, 4, 5, 7])

        ip_buckets = login_restore_counter.get_per_ip_buckets()
        eq_(ip_buckets.get(TEST_IP), 1 if self.invalid_phone_increases_ip_counter else 0)
        phone_buckets = login_restore_counter.get_per_phone_buckets()
        eq_(phone_buckets.get(TEST_PHONE_OBJECT.digital), 0)
