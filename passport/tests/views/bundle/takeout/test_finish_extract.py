# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_LOGIN,
    TEST_UID,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.time import get_unixtime


TEST_ARCHIVE_KEY = 'key'
TEST_ARCHIVE_PASSWORD = 'password'


@with_settings_hosts()
class TestFinishExtract(BaseBundleTestViews, EmailTestMixin):
    default_url = '/1/bundle/takeout/extract/finish/'
    http_method = 'post'
    http_query_args = {
        'uid': TEST_UID,
        'archive_s3_key': TEST_ARCHIVE_KEY,
        'archive_password': TEST_ARCHIVE_PASSWORD,
    }
    consumer = 'dev'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='dev',
                grants={'takeout': ['finish_extract']},
            ),
        )
        self.setup_blackbox()

    def setup_blackbox(self, uid=TEST_UID, is_extract_in_progress=True, has_native_email=True):
        attributes = {
            'takeout.fail_extract_at': '42',
        }
        if is_extract_in_progress:
            attributes['takeout.extract_in_progress_since'] = str(get_unixtime())

        emails = [
            self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
            self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
            self.create_validated_external_email(TEST_LOGIN, 'silent.ru', silent=True),
        ]
        if has_native_email:
            emails.append(
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            )

        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=uid,
                attributes=attributes,
                emails=emails,
            ),
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def assert_db_ok(self, uid=TEST_UID, with_password=True, dbshard='passportdbshard1'):
        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count(dbshard), 2)  # insert и delete атрибутов

        self.env.db.check_missing('attributes', 'takeout.extract_in_progress_since', uid=uid, db=dbshard)
        self.env.db.check('attributes', 'takeout.archive_created_at', TimeNow(), uid=uid, db=dbshard)
        self.env.db.check('attributes', 'takeout.archive_s3_key', TEST_ARCHIVE_KEY, uid=uid, db=dbshard)
        if with_password:
            self.env.db.check('attributes', 'takeout.archive_password', TEST_ARCHIVE_PASSWORD, uid=uid, db=dbshard)
        else:
            self.env.db.check_missing('attributes', 'takeout.archive_password', uid=uid, db=dbshard)
        self.env.db.check_missing('attributes', 'takeout.fail_extract_at', uid=uid, db=dbshard)

    def assert_historydb_ok(self, with_password=True):
        expected_log_entries = {
            'action': 'finish_takeout_extract',
            'consumer': 'dev',
            'takeout.extract_in_progress_since': '0',
            'takeout.archive_s3_key': '***',
            'takeout.archive_created_at': TimeNow(),
            'takeout.fail_extract_at': '0',
        }
        if with_password:
            expected_log_entries['takeout.archive_password'] = '***'
        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_log_entries,
        )

    def check_emails_sent(self, native=True):
        self.assert_emails_sent([
            self.build_email(
                address='%s@%s' % (TEST_LOGIN, 'yandex.ru' if native else 'gmail.com'),
            ),
        ])

    def build_email(self, address):
        return {
            'language': 'ru',
            'addresses': [address],
            'subject': 'takeout.extract_complete.subject',
            'tanker_keys': {
                'takeout.extract_complete.subject': {},
                'takeout.extract_complete.message': {},
                'takeout.extract_complete.download': {},
                'takeout.extract_complete.download_url': {'UID': TEST_UID},
                'signature.secure': {},
                'takeout.feedback': {
                    'FEEDBACK_URL_BEGIN': '<a href=\'https://yandex.ru/support/passport/data.html#faq__feedback\'>',
                    'FEEDBACK_URL_END': '</a>',
                },
            },
        }

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.check_emails_sent()

    def test_ok_without_password(self):
        resp = self.make_request(exclude_args=['archive_password'])
        self.assert_ok_response(resp)
        self.assert_db_ok(with_password=False)
        self.assert_historydb_ok(with_password=False)
        self.check_emails_sent()

    def test_not_native_email_ok(self):
        self.setup_blackbox(has_native_email=False)

        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.check_emails_sent(native=False)

    def test_extract_already_finished(self):
        self.setup_blackbox(is_extract_in_progress=False)

        resp = self.make_request(exclude_args=['archive_password'])
        self.assert_error_response(resp, ['action.not_required'])
