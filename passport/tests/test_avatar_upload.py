# -*- coding: utf-8 -*-
import mock
from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.avatars import (
    upload_avatar,
    upload_avatar_async,
)
from passport.backend.core.builders.avatars_mds_api import (
    AvatarsMdsApiImageNotFoundError,
    AvatarsMdsApiInvalidFileSizeError,
    AvatarsMdsApiInvalidImageSizeError,
    AvatarsMdsApiPermanentError,
    AvatarsMdsApiTemporaryError,
)
from passport.backend.core.builders.avatars_mds_api.faker import (
    avatars_mds_api_upload_ok_response,
    FakeAvatarsMdsApi,
)
from passport.backend.core.logging_utils.faker.fake_tskv_logger import AvatarsLoggerFaker
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from six import BytesIO


TEST_UID = 123456789
TEST_IP = '1.2.3.4'
TEST_URL = 'http://smth'
TEST_GROUP_ID = '1234'
TEST_AVATAR_KEY = '567890'
TEST_AVATAR_ID = '%s/%s' % (TEST_GROUP_ID, TEST_AVATAR_KEY)
TEST_IMAGE_DATA = b'some-cool-image'


class TestUploadAsync(PassportTestCase):
    def setUp(self):
        self._log_faker = AvatarsLoggerFaker()
        self._log_faker.start()

    def tearDown(self):
        self._log_faker.stop()

    def test_ok(self):
        upload_avatar_async(TEST_UID, avatar_url=TEST_URL, user_ip=TEST_IP)
        self._log_faker.assert_has_written([
            self._log_faker.entry(
                'base',
                uid=str(TEST_UID),
                avatar_to_upload=TEST_URL,
                mode='upload_by_url',
                unixtime=TimeNow(),
                user_ip=TEST_IP,
                skip_if_set='0',
            ),
        ])

    def test_ok_with_skip_if_set(self):
        upload_avatar_async(TEST_UID, avatar_url=TEST_URL, user_ip=TEST_IP, skip_if_set=True)
        self._log_faker.assert_has_written([
            self._log_faker.entry(
                'base',
                uid=str(TEST_UID),
                avatar_to_upload=TEST_URL,
                mode='upload_by_url',
                unixtime=TimeNow(),
                user_ip=TEST_IP,
                skip_if_set='1',
            ),
        ])


@with_settings(
    AVATARS_WRITE_URL='mds.localhost',
    AVATARS_READ_URL='-',
    AVATARS_TIMEOUT=1,
    AVATARS_RETRIES=2,
)
class TestUpload(PassportTestCase):
    def setUp(self):
        super(TestUpload, self).setUp()

        self.fake_avatars_mds_api = FakeAvatarsMdsApi()
        self.fake_avatars_mds_api.set_response_value('upload_from_url', avatars_mds_api_upload_ok_response(TEST_GROUP_ID))
        self.fake_avatars_mds_api.set_response_value('upload_from_file', avatars_mds_api_upload_ok_response(TEST_GROUP_ID))

        patch_get_key = mock.patch(
            'passport.backend.core.avatars.avatars.get_avatar_mds_key',
            mock.Mock(return_value=TEST_AVATAR_KEY),
        )

        self.patches = [
            patch_get_key,
            self.fake_avatars_mds_api,
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        super(TestUpload, self).tearDown()

    def assert_upload_ok(self, from_url):
        eq_(len(self.fake_avatars_mds_api.requests), 1)

    def test_upload_from_url_ok(self):
        eq_(
            upload_avatar(TEST_UID, avatar_url=TEST_URL),
            TEST_AVATAR_ID,
        )
        self.assert_upload_ok(from_url=True)

    def test_upload_from_file_ok(self):
        eq_(
            upload_avatar(TEST_UID, avatar_file=BytesIO(TEST_IMAGE_DATA)),
            TEST_AVATAR_ID,
        )
        self.assert_upload_ok(from_url=False)

    @raises(ValueError)
    def test_too_few_params_error(self):
        upload_avatar(TEST_UID)

    @raises(ValueError)
    def test_too_many_params_error(self):
        upload_avatar(TEST_UID, avatar_url=TEST_URL, avatar_file=BytesIO(TEST_IMAGE_DATA))

    @raises(AvatarsMdsApiTemporaryError)
    def test_mds_temporary_error(self):
        self.fake_avatars_mds_api.set_response_side_effect('upload_from_url', AvatarsMdsApiTemporaryError)
        upload_avatar(TEST_UID, avatar_url=TEST_URL)

    @raises(AvatarsMdsApiPermanentError)
    def test_mds_permanent_error(self):
        self.fake_avatars_mds_api.set_response_side_effect('upload_from_url', AvatarsMdsApiPermanentError)
        upload_avatar(TEST_UID, avatar_url=TEST_URL)

    @raises(AvatarsMdsApiImageNotFoundError)
    def test_invalid_url_error(self):
        self.fake_avatars_mds_api.set_response_side_effect('upload_from_url', AvatarsMdsApiImageNotFoundError)
        upload_avatar(TEST_UID, avatar_url=TEST_URL)

    @raises(AvatarsMdsApiInvalidFileSizeError)
    def test_invalid_file_size_error(self):
        self.fake_avatars_mds_api.set_response_side_effect('upload_from_file', AvatarsMdsApiInvalidFileSizeError)
        upload_avatar(TEST_UID, avatar_file=BytesIO(TEST_IMAGE_DATA))

    @raises(AvatarsMdsApiInvalidImageSizeError)
    def test_invalid_avatar_size_error(self):
        self.fake_avatars_mds_api.set_response_side_effect('upload_from_file', AvatarsMdsApiInvalidImageSizeError)
        upload_avatar(TEST_UID, avatar_file=BytesIO(TEST_IMAGE_DATA))
