# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_BLACKBOX_RESPONSE_ACCOUNT_DATA,
    TEST_HOST,
    TEST_LOGIN,
    TEST_OPERATION_ID,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER1,
    TEST_RECOVERY_EMAIL,
    TEST_RETPATH,
    TEST_TR_RECOVERY_EMAIL,
    TEST_UID,
    TEST_UID2,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_bindings_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.builders.captcha.faker import captcha_response_check
from passport.backend.core.conf import settings
from passport.backend.core.mailer.faker.mail_utils import assert_email_message_sent
from passport.backend.core.models.phones.faker import (
    build_phone_being_bound,
    build_phone_bound,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)


TEST_DEFAULT_KARMA_VALUE = '10'

KARMA_WASHED_STATE = 'karma_washed'
EMAIL_SENT_STATE = 'email_sent'

TEST_TEXT = 'Пустите, я хороший кот'

TEST_EMAIL_BODY = """
%(text)s

----

uid = %(uid)s
login = %(login)s
email = %(email)s
karma = %(karma)s
ip = %(user_ip)s http://adm-test.yandex-team.ru/users/?ip_from=%(user_ip)s
adm: http://adm-test.yandex-team.ru/users/?uid=%(uid)s
%(referer)s
"""


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    RECOVERY_EMAIL_BY_TLD={
        'default': TEST_RECOVERY_EMAIL,
        'com.tr': TEST_TR_RECOVERY_EMAIL,
    },
)
class TestUserApproveIntegrational(BaseBundleTestViews):
    default_url = None
    http_method = 'post'
    http_query_args = dict(
        retpath=TEST_RETPATH,
    )
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIE,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'account': ['userapprove'],
                    'captcha': ['*'],
                },
            ),
        )

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        self.env.captcha_mock.set_response_value(
            'check',
            captcha_response_check(),
        )
        self.setup_bb_response(serialize=False)

    def tearDown(self):
        self.track_id_generator.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator

    def setup_bb_response(self, account_data=None, serialize=True):
        account_data = merge_dicts(
            TEST_BLACKBOX_RESPONSE_ACCOUNT_DATA,
            account_data or {},
        )
        account_data.setdefault('karma', TEST_DEFAULT_KARMA_VALUE)

        sessionid_data = blackbox_sessionid_multi_response(
            **account_data
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_data,
        )
        if serialize:
            self.env.db.serialize_sessionid(sessionid_data)

    def setup_phone_bindings_history(self, phones):
        bindings = []
        for phone in phones:
            bindings.append(
                {
                    'type': 'history',
                    'number': phone['obj'].e164,
                    'phone_id': phone['id'],
                    'uid': phone['uid'],
                    'bound': phone['bound'],
                },
            )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response(bindings),
        )

    def check_db(self, karma_value=TEST_DEFAULT_KARMA_VALUE):
        self.env.db.check_db_attr(TEST_UID, 'karma.value', karma_value)

    @property
    def expected_response(self):
        return {'retpath': TEST_RETPATH}

    def assert_track(self, validated):
        track = self.track_manager.read(self.track_id)
        ok_(validated == bool(track.is_captcha_checked))
        ok_(validated == bool(track.is_captcha_recognized))
        ok_(track.is_captcha_required)

    def assert_mail_sent(self, email=None, login=TEST_LOGIN, text=TEST_TEXT, uid=TEST_UID,
                         user_ip=TEST_USER_IP, karma=TEST_DEFAULT_KARMA_VALUE,
                         recipient=TEST_RECOVERY_EMAIL, referer=''):
        eq_(self.env.mailer.message_count, 1)

        if email is None:
            email = '%s@yandex.ru' % login
        assert_email_message_sent(
            self.env.mailer,
            recipient,
            settings.translations.NOTIFICATIONS['ru']['userapprove.subject'],
            TEST_EMAIL_BODY % dict(
                text=text,
                uid=uid,
                login=login,
                email=email,
                karma=karma,
                user_ip=user_ip,
                referer=referer,
            ),
        )

    def make_submit_request(self):
        return self.make_request(
            url='/1/bundle/account/userapprove/submit/?consumer=dev',
            query_args=dict(retpath=TEST_RETPATH),
        )

    def make_captcha_check_request(self):
        return self.make_request(
            url='/1/captcha/check/?consumer=dev',
            query_args=dict(
                answer='a',
                key='b',
                track_id=self.track_id,
            ),
        )

    def make_commit_request(self):
        return self.make_request(
            url='/1/bundle/account/userapprove/commit/?consumer=dev',
            query_args=dict(
                retpath=TEST_RETPATH,
                track_id=self.track_id,
                text=TEST_TEXT,
            ),
        )

    def test_email_sent(self):
        # Телефоны не подходят для автоматического обеления
        account_data = deep_merge(
            build_phone_bound(
                TEST_PHONE_ID1,
                TEST_PHONE_NUMBER.e164,
            ),
            build_phone_being_bound(
                TEST_PHONE_ID2,
                TEST_PHONE_NUMBER1.e164,
                TEST_OPERATION_ID,
            ),
        )
        self.setup_bb_response(account_data=account_data)
        binding_history = [
            {
                'id': TEST_PHONE_ID1,
                'obj': TEST_PHONE_NUMBER,
                'bound': datetime.now() - timedelta(seconds=100),
                'uid': TEST_UID,
            },
            {
                'id': TEST_PHONE_ID1,
                'obj': TEST_PHONE_NUMBER,
                'bound': datetime.now() - timedelta(seconds=50),
                'uid': TEST_UID2,
            },
        ]
        self.setup_phone_bindings_history(binding_history)

        self.check_db()

        resp = self.make_submit_request()
        expected_response = merge_dicts(
            self.expected_response,
            {'track_id': self.track_id},
        )
        self.assert_ok_response(resp, **expected_response)
        self.assert_track(validated=False)

        captcha_resp = self.make_captcha_check_request()
        self.assert_ok_response(captcha_resp, correct=True)

        self.assert_track(validated=True)

        resp = self.make_commit_request()
        expected_response = merge_dicts(
            self.expected_response,
            {'state': EMAIL_SENT_STATE},
        )
        self.assert_ok_response(resp, **expected_response)

        self.assert_track(validated=False)

        self.assert_mail_sent()
        self.check_db()
