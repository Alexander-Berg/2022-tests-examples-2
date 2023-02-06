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
    TEST_PDD_LOGIN,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER1,
    TEST_RECOVERY_EMAIL,
    TEST_REFERER,
    TEST_RETPATH,
    TEST_TR_HOST,
    TEST_TR_RECOVERY_EMAIL,
    TEST_UID,
    TEST_UID2,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SESSIONID_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_bindings_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.conf import settings
from passport.backend.core.mailer.faker.mail_utils import assert_email_message_sent
from passport.backend.core.models.phones.faker import (
    build_phone_being_bound,
    build_phone_bound,
    TEST_DATE,
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


class UserApproveBase(BaseBundleTestViews):
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
                },
            ),
        )

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        self.http_query_args.update(track_id=self.track_id)
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
        account_data.setdefault('karma', 10)

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

    def setup_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = False
            track.is_captcha_recognized = True
            track.is_captcha_checked = True

    @property
    def expected_response(self):
        return {'retpath': TEST_RETPATH}

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

    def assert_mail_not_sent(self):
        ok_(not self.env.mailer.message_count)

    def check_db(self, karma_value=TEST_DEFAULT_KARMA_VALUE):
        self.env.db.check_db_attr(TEST_UID, 'karma.value', karma_value)

    def check_db_karma_missing(self):
        self.env.db.check_db_attr_missing(TEST_UID, 'karma.value')

    def assert_historydb_ok(self):
        expected_entries = {
            'action': 'karma',
            'consumer': 'dev',
            'user_agent': 'curl',
            'info.karma_prefix': '6',
            'info.karma_full': '6010',
        }
        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_entries,
        )

    def assert_track_invalidated(self):
        track = self.track_manager.read(self.track_id)
        ok_(not track.is_captcha_checked)
        ok_(not track.is_captcha_recognized)
        ok_(track.is_captcha_required)


class CommonTestMixin(object):
    def test_invalid_cookie__error(self):
        self.setup_bb_response({'status': BLACKBOX_SESSIONID_INVALID_STATUS})
        resp = self.make_request(query_args={'text': TEST_TEXT})
        self.assert_error_response(resp, ['sessionid.invalid'], **self.expected_response)
        self.assert_mail_not_sent()

    def test_account_disabled__error(self):
        account_data = {
            'attributes': {
                'account.is_disabled': '1',
            },
        }
        self.setup_bb_response(account_data)
        resp = self.make_request(query_args={'text': TEST_TEXT})
        self.assert_error_response(resp, ['account.disabled'], **self.expected_response)
        self.assert_mail_not_sent()

    def test_account_disabled_on_deletion__error(self):
        account_data = {
            'attributes': {
                'account.is_disabled': '2',
            },
        }
        self.setup_bb_response(account_data)
        resp = self.make_request(query_args={'text': TEST_TEXT})
        self.assert_error_response(resp, ['account.disabled_on_deletion'], **self.expected_response)
        self.assert_mail_not_sent()

    def test_karma_already_washed__error(self):
        karma_value = '2100'
        self.setup_bb_response({'karma': karma_value})
        self.check_db(karma_value=karma_value)
        resp = self.make_request(query_args={'text': TEST_TEXT})
        self.assert_error_response(resp, ['action.not_required'], **self.expected_response)
        self.assert_mail_not_sent()
        self.check_db(karma_value=karma_value)

    def test_perfect_karma(self):
        karma_value = '0'
        self.setup_bb_response({'karma': karma_value})
        self.check_db_karma_missing()
        resp = self.make_request(query_args={'text': TEST_TEXT})
        self.assert_error_response(resp, ['action.not_required'], **self.expected_response)
        self.assert_mail_not_sent()


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
)
class TestUserApproveSubmit(UserApproveBase, CommonTestMixin):
    default_url = '/1/bundle/account/userapprove/submit/?consumer=dev'

    def test_single_valid_bound_phone__karma_washed(self):
        account_data = build_phone_bound(
            TEST_PHONE_ID1,
            TEST_PHONE_NUMBER.e164,
        )
        self.setup_bb_response(account_data)

        binding_history = [
            {
                'id': TEST_PHONE_ID1,
                'obj': TEST_PHONE_NUMBER,
                'uid': TEST_UID,
                'bound': TEST_DATE,
            },
        ]
        self.setup_phone_bindings_history(binding_history)

        self.check_db()
        resp = self.make_request(exclude_args=['track_id'])
        expected_response = merge_dicts(
            self.expected_response,
            {'state': KARMA_WASHED_STATE},
        )
        self.assert_ok_response(resp, **expected_response)
        self.check_db('6010')
        self.assert_historydb_ok()
        self.assert_mail_not_sent()

    def test_no_valid_bound_phones(self):
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

        resp = self.make_request()
        expected_response = merge_dicts(
            self.expected_response,
            {'track_id': self.track_id},
        )
        self.assert_ok_response(resp, **expected_response)
        self.check_db()
        self.assert_track_invalidated()

    def test_multiple_phones_bound_one_valid__karma_washed(self):
        account_data = deep_merge(
            build_phone_bound(
                TEST_PHONE_ID1,
                TEST_PHONE_NUMBER.e164,
            ),
            build_phone_bound(
                TEST_PHONE_ID2,
                TEST_PHONE_NUMBER1.e164,
            ),
        )
        self.setup_bb_response(account_data=account_data)
        binding_history = [
            {
                'id': TEST_PHONE_ID1,
                'obj': TEST_PHONE_NUMBER,
                'bound': TEST_DATE,
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
        resp = self.make_request()
        expected_response = merge_dicts(
            self.expected_response,
            {'state': KARMA_WASHED_STATE},
        )
        self.assert_ok_response(resp, **expected_response)
        self.check_db('6010')
        self.assert_historydb_ok()
        self.assert_mail_not_sent()


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    RECOVERY_EMAIL_BY_TLD={
        'default': TEST_RECOVERY_EMAIL,
        'com.tr': TEST_TR_RECOVERY_EMAIL,
    },
)
class TestUserApproveCommit(UserApproveBase, CommonTestMixin):
    default_url = '/1/bundle/account/userapprove/commit/?consumer=dev'

    def test_no_track__error(self):
        resp = self.make_request(exclude_args=['track_id'])
        self.assert_error_response(resp, ['track_id.empty'])
        self.assert_mail_not_sent()

    def test_text_invalid__error(self):
        karma_value = '7100'
        self.setup_bb_response({'karma': karma_value})
        self.check_db(karma_value=karma_value)
        self.setup_track()

        resp = self.make_request(query_args={'text': 'abcd'})
        self.assert_error_response(resp, ['text.short'])
        self.assert_mail_not_sent()
        self.check_db(karma_value=karma_value)

    def test_email_sent(self):
        account_data = {
            'emails': [
                self.env.email_toolkit.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        }
        self.setup_bb_response(account_data)
        self.check_db()
        self.setup_track()
        resp = self.make_request(query_args={'text': TEST_TEXT})
        expected_response = merge_dicts(
            self.expected_response,
            {'state': EMAIL_SENT_STATE},
        )
        self.assert_ok_response(resp, **expected_response)
        self.assert_mail_sent()
        self.check_db()
        self.assert_track_invalidated()

    def test_captcha_not_passed__error(self):
        karma_value = '100'
        self.setup_bb_response({'karma': karma_value})
        self.check_db(karma_value=karma_value)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
        resp = self.make_request(query_args={'text': TEST_TEXT})
        self.assert_error_response(resp, ['captcha.required'], **self.expected_response)
        self.assert_mail_not_sent()
        self.check_db(karma_value=karma_value)
        self.assert_track_invalidated()

    def test_pdd_email_sent(self):
        account_data = {
            'aliases': {
                'pdd': TEST_PDD_LOGIN,
            },
        }
        self.setup_bb_response(account_data, serialize=False)
        self.setup_track()
        resp = self.make_request(query_args={'text': TEST_TEXT})
        expected_response = merge_dicts(
            self.expected_response,
            {'state': EMAIL_SENT_STATE},
        )
        self.assert_ok_response(resp, **expected_response)
        self.assert_mail_sent(email=TEST_PDD_LOGIN, login=TEST_PDD_LOGIN)
        self.assert_track_invalidated()

    def test_email_sent_with_referer_no_emails(self):
        account_data = {'login': 'abc'}
        self.setup_bb_response(account_data)
        self.setup_track()
        resp = self.make_request(query_args={'text': TEST_TEXT}, headers={'referer': TEST_REFERER})
        expected_response = merge_dicts(
            self.expected_response,
            {'state': EMAIL_SENT_STATE},
        )
        self.assert_ok_response(resp, **expected_response)
        self.assert_mail_sent(login='abc', referer='referer = %s' % TEST_REFERER)
        self.check_db()
        self.assert_track_invalidated()

    def test_external_emails_ok(self):
        # No default emails
        account_data = {
            'emails': [
                self.env.email_toolkit.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
            ],
        }
        self.setup_bb_response(account_data)
        self.check_db()
        self.setup_track()
        resp = self.make_request(query_args={'text': TEST_TEXT})
        expected_response = merge_dicts(
            self.expected_response,
            {'state': EMAIL_SENT_STATE},
        )
        self.assert_ok_response(resp, **expected_response)
        self.assert_mail_sent()
        self.check_db()
        self.assert_track_invalidated()

    def test_tr_host(self):
        headers = {
            'host': TEST_TR_HOST,
        }
        account_data = {
            'emails': [
                self.env.email_toolkit.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        }
        self.setup_bb_response(account_data)
        self.check_db()
        self.setup_track()
        resp = self.make_request(query_args={'text': TEST_TEXT}, headers=headers)
        expected_response = merge_dicts(
            self.expected_response,
            {'state': EMAIL_SENT_STATE},
        )
        self.assert_ok_response(resp, **expected_response)
        self.assert_mail_sent(recipient=TEST_TR_RECOVERY_EMAIL)
        self.check_db()
        self.assert_track_invalidated()
