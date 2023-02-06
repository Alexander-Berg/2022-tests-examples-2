# -*- coding: utf-8 -*-

import mock
from nose.tools import eq_
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_HOST,
    TEST_LOGIN,
    TEST_UID,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_multi_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.time import get_unixtime


@with_settings_hosts(
    TIME_FOR_ACCEPTING_EXTRACT=60,
)
class TestRequestExtract(BaseBundleTestViews, EmailTestMixin):
    default_url = '/1/bundle/takeout/extract/request/'
    http_method = 'post'
    http_query_args = {
        'uid': TEST_UID,
    }
    http_headers = {
        'host': TEST_HOST,
        'cookie': 'Session_id=foo;',
    }
    consumer = 'dev'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='dev',
                grants={'takeout': ['request_extract']},
            ),
        )
        self.setup_blackbox()

    def setup_blackbox(self, uid=TEST_UID, is_extract_in_progress=False, has_archive=True, has_native_email=True):
        attributes = {}
        if is_extract_in_progress:
            attributes['takeout.extract_in_progress_since'] = str(get_unixtime())
        if has_archive:
            attributes.update({
                'takeout.archive_s3_key': 'key',
                'takeout.archive_password': 'password',
                'takeout.archive_created_at': '123',
            })

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
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=uid,
                attributes=attributes,
                emails=emails,
            ),
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def assert_db_ok(self, uid=TEST_UID, dbshard='passportdbshard1'):
        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count(dbshard), 2)  # insert и delete атрибутов

        self.env.db.check('attributes', 'takeout.extract_in_progress_since', TimeNow(), uid=uid, db=dbshard)
        self.env.db.check_missing('attributes', 'takeout.archive_s3_key', uid=uid, db=dbshard)
        self.env.db.check_missing('attributes', 'takeout.archive_password', uid=uid, db=dbshard)
        self.env.db.check_missing('attributes', 'takeout.archive_created_at', uid=uid, db=dbshard)
        self.env.db.check('attributes', 'takeout.fail_extract_at', TimeNow(offset=60), uid=uid, db=dbshard)

    def assert_historydb_ok(self):
        expected_log_entries = {
            'action': 'request_takeout_extract',
            'consumer': 'dev',
            'takeout.extract_in_progress_since': TimeNow(),
            'takeout.archive_s3_key': '-',
            'takeout.archive_password': '-',
            'takeout.archive_created_at': '0',
            'takeout.fail_extract_at': TimeNow(offset=60),
        }
        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_log_entries,
        )

    def assert_logbroker_ok(self):
        self.env.lbw_takeout_tasks.assert_messages_sent(
            [
                dict(
                    extract=dict(),
                    task_base_message=dict(
                        extract_id=mock.ANY,
                        task_id=mock.ANY,
                        task_name='extract',
                        uid=str(TEST_UID),
                        unixtime=TimeNow(),
                        send_time=TimeNow(),
                        source='passport_api',
                    ),
                ),
            ],
            strict=True,
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
            'subject': 'takeout.extract_requested.subject',
            'tanker_keys': {
                'takeout.extract_requested.subject': {},
                'takeout.extract_requested.message': {},
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
        self.assert_logbroker_ok()

    def test_not_native_email_ok(self):
        self.setup_blackbox(has_native_email=False)

        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.check_emails_sent(native=False)

    def test_extract_already_in_progress(self):
        self.setup_blackbox(is_extract_in_progress=True)

        resp = self.make_request()
        self.assert_error_response(resp, ['action.not_required'])
