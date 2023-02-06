# -*- coding: utf-8 -*-
import json
from time import time

from nose.tools import ok_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_HOST,
    TEST_UID,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_multi_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.time import get_unixtime


TEST_TTL = 3601


@with_settings_hosts(
    S3_ENDPOINT='https://mds.localhost/',
    S3_SECRET_KEY_ID='key_id',
    S3_SECRET_KEY='key',
    TAKEOUT_ARCHIVE_TTL=TEST_TTL,
)
class BaseGetExtractResultTestCase(BaseBundleTestViews):
    default_url = None
    http_method = 'get'
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
                grants={'takeout': ['get_extract_result']},
            ),
        )
        self.setup_blackbox()
        # Не мокаем S3, так как сетевых запросов не делается, урл подписывается локально

    def setup_blackbox(self, uid=TEST_UID, is_extract_in_progress=False, has_archive=True,
                       archive_has_password=True, archive_created_at=None):
        attributes = {}
        if is_extract_in_progress:
            attributes['takeout.extract_in_progress_since'] = str(get_unixtime())
        if has_archive:
            attributes.update({
                'takeout.archive_s3_key': 'key',
                'takeout.archive_created_at': str(int(archive_created_at or time())),
            })
            if archive_has_password:
                attributes.update({
                    'takeout.archive_password': 'password',
                })

        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=uid,
                attributes=attributes,
            ),
        )

    def tearDown(self):
        self.env.stop()
        del self.env


class GetExtractStatusView(BaseGetExtractResultTestCase):
    default_url = '/1/bundle/takeout/extract/get_status/'

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            is_extract_in_progress=False,
            archive=dict(
                created_at=TimeNow(),
                valid_until=TimeNow(offset=TEST_TTL),
                has_password=True,
            ),
        )

    def test_archive_without_password_ok(self):
        self.setup_blackbox(archive_has_password=False)

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            is_extract_in_progress=False,
            archive=dict(
                created_at=TimeNow(),
                valid_until=TimeNow(offset=TEST_TTL),
                has_password=False,
            ),
        )

    def test_extract_in_progress(self):
        self.setup_blackbox(is_extract_in_progress=True, has_archive=False)

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            is_extract_in_progress=True,
        )

    def test_no_extract_results(self):
        self.setup_blackbox(has_archive=False)

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            is_extract_in_progress=False,
        )

    def test_extract_results_expired(self):
        self.setup_blackbox(archive_created_at=time() - 2 * TEST_TTL)

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            is_extract_in_progress=False,
        )


class GetArchiveUrlView(BaseGetExtractResultTestCase):
    default_url = '/1/bundle/takeout/extract/get_archive_url/'

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            skip=['archive_url'],
        )
        rv = json.loads(resp.data)
        ok_(rv['archive_url'].startswith('https://takeout.mds.localhost/key'))
        ok_('Signature' in rv['archive_url'])

    def test_extract_in_progress(self):
        self.setup_blackbox(is_extract_in_progress=True)

        resp = self.make_request()
        self.assert_error_response(resp, ['extract.in_progress'])

    def test_no_extract_results(self):
        self.setup_blackbox(has_archive=False)

        resp = self.make_request()
        self.assert_error_response(resp, ['action.impossible'])

    def test_extract_results_expired(self):
        self.setup_blackbox(archive_created_at=time() - 2 * TEST_TTL)

        resp = self.make_request()
        self.assert_error_response(resp, ['action.impossible'])


class GetArchivePasswordView(BaseGetExtractResultTestCase):
    default_url = '/1/bundle/takeout/extract/get_archive_password/'

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            archive_password='password',
        )

    def test_archive_without_password_ok(self):
        self.setup_blackbox(archive_has_password=False)

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            archive_password=None,
        )

    def test_extract_in_progress(self):
        self.setup_blackbox(is_extract_in_progress=True)

        resp = self.make_request()
        self.assert_error_response(resp, ['extract.in_progress'])

    def test_no_extract_results(self):
        self.setup_blackbox(has_archive=False)

        resp = self.make_request()
        self.assert_error_response(resp, ['action.impossible'])

    def test_extract_results_expired(self):
        self.setup_blackbox(archive_created_at=time() - 2 * TEST_TTL)

        resp = self.make_request()
        self.assert_error_response(resp, ['action.impossible'])
