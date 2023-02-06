# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import (
    assert_is_none,
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.base_test_data import (
    TEST_COOKIE_AGE,
    TEST_COOKIE_TIMESTAMP,
    TEST_HOST,
    TEST_IP,
    TEST_LOGIN,
    TEST_OLD_AUTH_ID,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER1,
    TEST_PHONE_NUMBER_DUMPED_MASKED,
    TEST_RETPATH,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_WEAK_PASSWORD_HASH,
    TEST_YANDEXUID_VALUE,
)
from passport.backend.api.views.bundle.auth.forwarding.forms import AUTH_LINK_PLACEHOLDER
from passport.backend.core import authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.builders.yasms.exceptions import (
    YaSmsDeliveryError,
    YaSmsError,
    YaSmsLimitExceeded,
    YaSmsPermanentBlock,
    YaSmsTemporaryBlock,
    YaSmsUidLimitExceeded,
)
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.counters.sms_per_ip import get_auth_forwarding_by_sms_counter
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.core.tracks.utils import create_short_track_id


eq_ = iterdiff(eq_)

TEST_IP_COUNTER_LIMIT = 3
TEST_SHORT_TRACK_LINK_TEMPLATE = 'https://passport.%(tld)s/a/%(track_id)s/'
TEST_SMS_IDENTITY = 'morda'
TEST_AUTH_FORWARDING_TRACK_TTL = 120
TEST_SMS_TEMPLATE = u'Настройте тему: %s' % AUTH_LINK_PLACEHOLDER


class ForwardAuthBySmsCommonTests(object):
    def test_ip_counter_overflow(self):
        counter = get_auth_forwarding_by_sms_counter(TEST_IP)
        for _ in range(TEST_IP_COUNTER_LIMIT):
            counter.incr(TEST_IP)

        response = self.make_request()

        self.assert_error_response(
            response,
            ['rate.limit_exceeded'],
        )

        eq_(counter.get(TEST_IP), TEST_IP_COUNTER_LIMIT)
        self.env.statbox.assert_has_written([])
        self.assert_sms_not_sent()

    def test_invalid_session(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

        response = self.make_request()

        self.assert_error_response(
            response,
            ['sessionid.invalid'],
        )
        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])
        self.assert_sms_not_sent()


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    AUTH_FORWARDING_SMS_IDENTITY=TEST_SMS_IDENTITY,
    **mock_counters(AUTH_FORWARDING_SMS_PER_IP_LIMIT_COUNTER=(24, 3600, TEST_IP_COUNTER_LIMIT))
)
class BaseForwardAuthBySmsTestCase(BaseBundleTestViews):
    track_type = 'authorize'
    statbox_mode = 'auth_forwarding'
    http_method = 'POST'

    def setUp(self):
        super(BaseForwardAuthBySmsTestCase, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
                age=TEST_COOKIE_AGE,
                ttl=5,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
                dbfields={
                    'password_quality.quality.uid': 10,
                    'password_quality.version.uid': 3,
                },
                crypt_password=TEST_WEAK_PASSWORD_HASH,
                **build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER.e164,
                )
            ),
        )

        self.env.grants.set_grants_return_value(
            mock_grants(grants={'auth_forwarding': ['by_sms']}),
        )

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(self.track_type)
        self.track_id_generator = FakeTrackIdGenerator()
        self.track_id_generator.set_return_value(self.track_id)

        self.short_track_id = create_short_track_id()
        create_short_track_id_mock = mock.Mock(return_value=self.short_track_id)
        self.short_track_patch = mock.patch(
            'passport.backend.core.tracks.track_manager.create_short_track_id',
            create_short_track_id_mock,
        )

        self.patches = [
            self.track_id_generator,
            self.short_track_patch,
        ]
        for p in self.patches:
            p.start()

        self.setup_statbox_templates()

        self.http_headers = dict(
            user_ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
            host=TEST_HOST,
            cookie=TEST_USER_COOKIE,
        )

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator,
        del self.patches
        del self.short_track_patch
        super(BaseForwardAuthBySmsTestCase, self).tearDown()

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            yandexuid=TEST_YANDEXUID_VALUE,
            track_id=self.track_id,
            ip=TEST_IP,
            host=TEST_HOST,
            uid=str(TEST_UID),
            user_agent=TEST_USER_AGENT,
            consumer='dev',
            mode=self.statbox_mode,
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='local_base',
            action='submitted',
        )
        self.env.statbox.bind_entry(
            'finished_with_error',
            _inherit_from='local_base',
            action='finished_with_error',
        )
        self.env.statbox.bind_entry(
            'committed',
            _inherit_from='local_base',
            action='committed',
        )
        self.env.statbox.bind_entry(
            'sms_sent',
            _inherit_from='local_base',
            action='%s.notification_sent' % TEST_SMS_IDENTITY,
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
            sms_id='1',
        )

    def assert_sms_not_sent(self):
        requests = self.env.yasms.requests
        eq_(requests, [])


class ForwardAuthBySmsSubmitViewTestCase(BaseForwardAuthBySmsTestCase, ForwardAuthBySmsCommonTests):
    default_url = '/1/bundle/auth/forward_by_sms/submit/?consumer=dev'

    def test_no_secure_phone(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **build_phone_bound(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER.e164,
                )
            ),
        )

        response = self.make_request()

        self.assert_error_response(
            response,
            ['phone_secure.not_found'],
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('finished_with_error', error='phone_secure.not_found'),
        ])
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            eq_(track.track_type, 'authorize')
            assert_is_none(track.secure_phone_number)

    def test_submit_ok(self):

        response = self.make_request()

        self.assert_ok_response(
            response,
            track_id=self.track_id,
            number=TEST_PHONE_NUMBER_DUMPED_MASKED,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('submitted'),
        ])
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            eq_(track.track_type, 'authorize')
            eq_(track.secure_phone_number, TEST_PHONE_NUMBER.e164)

    def test_submit_non_default_uid_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_PDD_UID,  # дефолт
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=TEST_UID,
                **build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER.e164,
                )
            ),
        )

        response = self.make_request(query_args=dict(uid=TEST_UID))

        self.assert_ok_response(
            response,
            track_id=self.track_id,
            number=TEST_PHONE_NUMBER_DUMPED_MASKED,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('submitted'),
        ])
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            eq_(track.track_type, 'authorize')
            eq_(track.secure_phone_number, TEST_PHONE_NUMBER.e164)


@with_settings_hosts(
    SHORT_TRACK_LINK_TEMPLATE=TEST_SHORT_TRACK_LINK_TEMPLATE,
    AUTH_FORWARDING_TRACK_TTL=TEST_AUTH_FORWARDING_TRACK_TTL,
)
class ForwardAuthBySmsCommitViewTestCase(BaseForwardAuthBySmsTestCase, ForwardAuthBySmsCommonTests):
    default_url = '/1/bundle/auth/forward_by_sms/commit/?consumer=dev'

    def setUp(self):
        super(ForwardAuthBySmsCommitViewTestCase, self).setUp()
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.track_type = 'authorize'
            track.secure_phone_number = TEST_PHONE_NUMBER.e164
            track.uid = TEST_UID

        self.http_query_args = {
            'track_id': self.track_id,
            'template': TEST_SMS_TEMPLATE,
        }

        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

    def assert_sms_sent(self, tld='ru', uid=TEST_UID, template=TEST_SMS_TEMPLATE):
        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        link = (TEST_SHORT_TRACK_LINK_TEMPLATE % dict(tld=tld, track_id=self.short_track_id))
        requests[-1].assert_query_contains({
            'from_uid': str(uid),
            'text': template.replace(AUTH_LINK_PLACEHOLDER, link),
            'identity': TEST_SMS_IDENTITY + '.notify',
        })

    def test_commit_ok(self):

        counter = get_auth_forwarding_by_sms_counter(TEST_IP)
        # оставляем одну попытку счетчика
        for _ in range(TEST_IP_COUNTER_LIMIT - 1):
            counter.incr(TEST_IP)

        response = self.make_request()

        self.assert_ok_response(
            response,
            track_id=self.track_id,
            number=TEST_PHONE_NUMBER_DUMPED_MASKED,
        )

        self.assert_sms_sent()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('sms_sent'),
            self.env.statbox.entry('committed'),
        ])
        with self.track_manager.transaction(self.short_track_id).commit_on_error() as track:
            ok_(0 < track.ttl <= TEST_AUTH_FORWARDING_TRACK_TTL)
            eq_(track.track_type, 'authorize')
            eq_(track.auth_source, authtypes.AUTH_SOURCE_FOREIGN_COOKIE)
            eq_(track.source_authid, TEST_OLD_AUTH_ID)
            ok_(track.allow_authorization)
            ok_(not track.allow_oauth_authorization)
            eq_(track.uid, str(TEST_UID))
            eq_(track.login, TEST_LOGIN)
            ok_(not track.is_password_passed)
            ok_(track.have_password)
            ok_(not track.is_otp_restore_passed)

        with self.track_manager.transaction(self.track_id).commit_on_error() as orig_track:
            eq_(orig_track.next_track_id, self.short_track_id)

        # убеждаемся, что счетчик увеличился
        eq_(counter.get(TEST_IP), TEST_IP_COUNTER_LIMIT)

    def test_commit_with_retpath_ok(self):
        self.http_query_args['retpath'] = TEST_RETPATH

        response = self.make_request()

        self.assert_ok_response(
            response,
            track_id=self.track_id,
            number=TEST_PHONE_NUMBER_DUMPED_MASKED,
        )

        self.assert_sms_sent()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('sms_sent'),
            self.env.statbox.entry('committed'),
        ])
        with self.track_manager.transaction(self.short_track_id).commit_on_error() as track:
            eq_(track.track_type, 'authorize')
            eq_(track.source_authid, TEST_OLD_AUTH_ID)
            ok_(track.allow_authorization)
            eq_(track.retpath, TEST_RETPATH)

    def test_commit_pdd_ok(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.uid = TEST_PDD_UID
        self.http_headers['host'] = 'yandex.com.tr'
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={'pdd': TEST_PDD_LOGIN},
                authid=TEST_OLD_AUTH_ID,
                age=TEST_COOKIE_AGE,
                ttl=5,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
                **build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER.e164,
                )
            ),
        )

        response = self.make_request()

        self.assert_ok_response(
            response,
            track_id=self.track_id,
            number=TEST_PHONE_NUMBER_DUMPED_MASKED,
        )

        self.assert_sms_sent(tld='com.tr', uid=TEST_PDD_UID)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='yandex.com.tr'),
            self.env.statbox.entry('sms_sent', host='yandex.com.tr', uid=str(TEST_PDD_UID)),
            self.env.statbox.entry('committed', host='yandex.com.tr', uid=str(TEST_PDD_UID)),
        ])
        with self.track_manager.transaction(self.short_track_id).commit_on_error() as track:
            eq_(track.track_type, 'authorize')
            eq_(track.source_authid, TEST_OLD_AUTH_ID)
            ok_(track.allow_authorization)
            eq_(track.uid, str(TEST_PDD_UID))
            eq_(track.login, TEST_PDD_LOGIN)

    def test_commit_with_short_sms_template_ok(self):
        self.http_query_args['template'] = AUTH_LINK_PLACEHOLDER

        response = self.make_request()

        self.assert_ok_response(
            response,
            track_id=self.track_id,
            number=TEST_PHONE_NUMBER_DUMPED_MASKED,
        )

        self.assert_sms_sent(template=AUTH_LINK_PLACEHOLDER)

    def test_retpath_not_within_auth_domain(self):
        for retpath in (
            'https://ya.ru',
            'https://passport.yandex.com',
        ):
            self.http_query_args['retpath'] = retpath

            response = self.make_request()

            self.assert_error_response(
                response,
                ['retpath.invalid'],
            )

        self.assert_sms_not_sent()

    def test_invalid_track_state(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.secure_phone_number = None

        response = self.make_request()

        self.assert_error_response(
            response,
            ['track.invalid_state'],
        )
        self.assert_sms_not_sent()

    def test_no_secure_phone_on_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(),
        )

        response = self.make_request()

        self.assert_error_response(
            response,
            ['phone.changed'],
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('finished_with_error', error='phone.changed'),
        ])
        self.assert_sms_not_sent()

    def test_secure_phone_changed(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.secure_phone_number = TEST_PHONE_NUMBER1.e164

        response = self.make_request()

        self.assert_error_response(
            response,
            ['phone.changed'],
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('finished_with_error', error='phone.changed'),
        ])
        self.assert_sms_not_sent()

    def test_yasms_send_sms_failed_with_unhandled_error(self):
        self.env.yasms.set_response_side_effect('send_sms', YaSmsError('error message'))

        response = self.make_request()

        self.assert_error_response(
            response,
            ['exception.unhandled'],
        )

    @parameterized.expand([
        (YaSmsLimitExceeded, 'sms_limit.exceeded'),
        (YaSmsUidLimitExceeded, 'sms_limit.exceeded'),
        (YaSmsPermanentBlock, 'phone.blocked'),
        (YaSmsTemporaryBlock, 'sms_limit.exceeded'),
        (YaSmsDeliveryError, 'backend.yasms_failed'),
    ])
    def test_yasms_send_sms_failed_with_handled_error(self, error, code):
        self.env.yasms.set_response_side_effect('send_sms', error())

        response = self.make_request()

        self.assert_error_response(
            response,
            [code],
        )
