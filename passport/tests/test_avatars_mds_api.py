# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.avatars_mds_api import (
    AvatarsMdsApiBadImageFormatError,
    AvatarsMdsApiImageNotFoundError,
    AvatarsMdsApiInvalidFileSizeError,
    AvatarsMdsApiInvalidImageSizeError,
    AvatarsMdsApiPermanentError,
    AvatarsMdsApiTemporaryError,
    get_avatars_mds_api,
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
TEST_SIZE = 'retina-5120'
TEST_FILE = BytesIO(b'data')
TEST_URL = 'http://localhost-read/get-space/smth'


@with_settings(
    AVATARS_WRITE_URL='http://localhost-write/',
    AVATARS_READ_URL='http://localhost-read/',
    AVATARS_TIMEOUT=1,
    AVATARS_RETRIES=2,
)
class TestAvatarsMdsApi(unittest.TestCase):
    def setUp(self):
        self.faker = FakeAvatarsMdsApi()
        self.builder = get_avatars_mds_api('test')
        self.faker.start()

    def tearDown(self):
        self.faker.stop()
        del self.faker
        del self.builder

    def test_read_url(self):
        read_url = self.builder.get_read_url(group_id=TEST_GROUP_ID, key=TEST_KEY, size=TEST_SIZE)
        ok_(read_url.startswith('http://localhost-read/'))
        ok_('get-' in read_url)

    def test_download_by_params_ok(self):
        self.faker.set_response_value(
            'download',
            avatars_mds_api_download_response('content'),
        )
        file_object = self.builder.download(group_id=TEST_GROUP_ID, key=TEST_KEY, size=TEST_SIZE)
        eq_(file_object.read(), b'content')
        self.faker.requests[-1].assert_properties_equal(
            method='GET',
            url=self.builder.get_read_url(group_id=TEST_GROUP_ID, key=TEST_KEY, size=TEST_SIZE),
        )

    def test_download_by_url_ok(self):
        self.faker.set_response_value(
            'download',
            avatars_mds_api_download_response('content'),
        )
        file_object = self.builder.download(url=TEST_URL)
        eq_(file_object.read(), b'content')
        self.faker.requests[-1].assert_properties_equal(
            method='GET',
            url=TEST_URL,
        )

    def test_download_not_enough_params(self):
        with assert_raises(ValueError):
            self.builder.download()
        ok_(not self.faker.requests)

    def test_download_server_error(self):
        self.faker.set_response_value(
            'download',
            avatars_mds_api_download_response(status_code=503),
        )
        with assert_raises(AvatarsMdsApiTemporaryError):
            self.builder.download(url=TEST_URL)

    def test_download_image_not_found(self):
        self.faker.set_response_value(
            'download',
            avatars_mds_api_download_response(status_code=404),
        )
        with assert_raises(AvatarsMdsApiImageNotFoundError):
            self.builder.download(url=TEST_URL)

    def test_upload_from_file_ok(self):
        self.faker.set_response_value(
            'upload_from_file',
            avatars_mds_api_upload_ok_response(TEST_GROUP_ID),
        )
        group_id = self.builder.upload_from_file(key=TEST_KEY, file_=TEST_FILE)
        eq_(group_id, TEST_GROUP_ID)

    def test_upload_from_file_collision(self):
        self.faker.set_response_value(
            'upload_from_file',
            '{"attrs":{"group-id": "%s"},"status": "error","description":"update is prohibited"}' % TEST_GROUP_ID,
            status=403,
        )
        group_id = self.builder.upload_from_file(key=TEST_KEY, file_=TEST_FILE)
        eq_(group_id, TEST_GROUP_ID)

    def test_upload_from_file_server_error(self):
        self.faker.set_response_value(
            'upload_from_file',
            '{}',
            status=500,
        )
        with assert_raises(AvatarsMdsApiTemporaryError):
            self.builder.upload_from_file(key=TEST_KEY, file_=TEST_FILE)

    def test_upload_from_file_error(self):
        self.faker.set_response_value(
            'upload_from_file',
            '{"description": "bad_request"}',
            status=400,
        )
        with assert_raises(AvatarsMdsApiPermanentError):
            self.builder.upload_from_file(key=TEST_KEY, file_=TEST_FILE)

    def test_upload_from_file_bad_file_type(self):
        self.faker.set_response_value(
            'upload_from_file',
            '{"description": "cannot process image: no kittens in it"}',
            status=400,
        )
        with assert_raises(AvatarsMdsApiBadImageFormatError):
            self.builder.upload_from_file(key=TEST_KEY, file_=TEST_FILE)

    def test_upload_from_file_bad_file_info(self):
        self.faker.set_response_value(
            'upload_from_file',
            '{"description": "cannot process image: no kitten names in it"}',
            status=400,
        )
        with assert_raises(AvatarsMdsApiBadImageFormatError):
            self.builder.upload_from_file(key=TEST_KEY, file_=TEST_FILE)

    def test_upload_from_file_image_too_small(self):
        self.faker.set_response_value(
            'upload_from_file',
            '{"description": "Image is too small"}',
            status=415,
        )
        with assert_raises(AvatarsMdsApiInvalidImageSizeError):
            self.builder.upload_from_file(key=TEST_KEY, file_=TEST_FILE)

    def test_upload_from_file_file_too_large(self):
        self.faker.set_response_value(
            'upload_from_file',
            '{"description": "Image size 11 bytes more than maximum allowed 10 bytes"}',
            status=415,
        )
        with assert_raises(AvatarsMdsApiInvalidFileSizeError):
            self.builder.upload_from_file(key=TEST_KEY, file_=TEST_FILE)

    def test_upload_from_file_bad_json(self):
        self.faker.set_response_value(
            'upload_from_file',
            'foo',
        )
        with assert_raises(AvatarsMdsApiPermanentError):
            self.builder.upload_from_file(key=TEST_KEY, file_=TEST_FILE)

    def test_upload_from_url_ok(self):
        self.faker.set_response_value(
            'upload_from_url',
            avatars_mds_api_upload_ok_response(TEST_GROUP_ID),
        )
        group_id = self.builder.upload_from_url(key=TEST_KEY, url=TEST_URL)
        eq_(group_id, TEST_GROUP_ID)

    def test_upload_from_url_file_not_found(self):
        self.faker.set_response_value(
            'upload_from_url',
            '{}',
            status=434,
        )
        with assert_raises(AvatarsMdsApiImageNotFoundError):
            self.builder.upload_from_url(key=TEST_KEY, url=TEST_URL)

    def test_delete_ok(self):
        self.faker.set_response_value(
            'delete',
            'ok',
        )
        self.builder.delete(group_id=TEST_GROUP_ID, key=TEST_KEY)
        eq_(len(self.faker.requests), 1)

    def test_delete_error(self):
        self.faker.set_response_value(
            'delete',
            'error',
            status=500,
        )
        with assert_raises(AvatarsMdsApiTemporaryError):
            self.builder.delete(group_id=TEST_GROUP_ID, key=TEST_KEY)
