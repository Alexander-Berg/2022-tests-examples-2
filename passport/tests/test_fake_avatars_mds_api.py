# -*- coding: utf-8 -*-
from unittest import TestCase

from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.avatars_mds_api import (
    AvatarsMdsApi,
    AvatarsMdsApiPermanentError,
    AvatarsMdsApiTemporaryError,
    BaseAvatarsMdsApiError,
)
from passport.backend.core.builders.avatars_mds_api.faker import (
    avatars_mds_api_download_response,
    avatars_mds_api_upload_ok_response,
    FakeAvatarsMdsApi,
)
from passport.backend.core.test.test_utils import with_settings
from six import BytesIO


TEST_GROUP_ID = '123'
TEST_KEY = 'key-1'
TEST_FILE = BytesIO(b'data')
TEST_URL = 'http://localhost/i.png'
TEST_NAMESPACE = 'test'


@with_settings(
    AVATARS_WRITE_URL='http://localhost-write/',
    AVATARS_READ_URL='http://localhost-read/',
    AVATARS_TIMEOUT=1,
    AVATARS_RETRIES=2,
)
class FakeAvatarsMdsApiTestCase(TestCase):
    def setUp(self):
        self.faker = FakeAvatarsMdsApi()
        self.faker.start()
        self.avatars = AvatarsMdsApi(TEST_NAMESPACE)

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_upload_from_file(self):
        self.faker.set_response_value('upload_from_file', avatars_mds_api_upload_ok_response(group_id=123))
        eq_(self.avatars.upload_from_file(TEST_KEY, TEST_FILE), 123)
        self.faker.requests[-1].assert_url_starts_with('http://localhost-write/put-test/%s' % TEST_KEY)

    @raises(AvatarsMdsApiPermanentError)
    def test_upload_from_file_error(self):
        self.faker.set_response_side_effect('upload_from_file', AvatarsMdsApiPermanentError)
        self.avatars.upload_from_file(TEST_KEY, TEST_FILE)

    def test_upload_from_url(self):
        self.faker.set_response_value('upload_from_url', avatars_mds_api_upload_ok_response(group_id=123))
        eq_(self.avatars.upload_from_url(TEST_KEY, TEST_URL), 123)
        self.faker.requests[-1].assert_url_starts_with('http://localhost-write/put-test/%s' % TEST_KEY)

    def test_download(self):
        self.faker.set_response_value('download', avatars_mds_api_download_response())
        self.avatars.download(url='http://localhost/get-space/test')
        self.faker.requests[-1].assert_url_starts_with('http://localhost/get-space/test')

    def test_delete(self):
        self.faker.set_response_side_effect('delete', 'OK')
        ok_(not self.avatars.delete(TEST_GROUP_ID, TEST_KEY))
        self.faker.requests[-1].assert_url_starts_with(
            'http://localhost-write/delete-test/%s/%s' % (TEST_GROUP_ID, TEST_KEY)
        )

    @raises(BaseAvatarsMdsApiError)
    def test_delete_error(self):
        self.faker.set_response_side_effect('delete', AvatarsMdsApiTemporaryError)
        self.avatars.delete(TEST_GROUP_ID, TEST_KEY)
