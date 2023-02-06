# -*- coding: utf-8 -*-

import io
import os
import shutil
import tempfile

from botocore.exceptions import ClientError
from hamcrest import (
    all_of,
    assert_that,
    has_entries,
    has_property,
    instance_of,
)
import mock
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    FakeBlackbox,
)
from passport.backend.core.builders.passport import (
    PassportAccountNotFoundError,
    PassportActionNotRequiredError,
)
from passport.backend.core.builders.passport.faker.fake_passport import (
    FakePassport,
    passport_ok_response,
)
from passport.backend.core.s3.faker.fake_s3 import s3_ok_response
from passport.backend.core.test.test_utils.utils import with_settings
from passport.backend.takeout.common.conf import get_config
from passport.backend.takeout.common.conf.crypto import get_keys_for_encrypting
from passport.backend.takeout.common.crypto import encrypt_stream
from passport.backend.takeout.common.utils import maybe_make_dirs
from passport.backend.takeout.logbroker_client.tasks.make_archive import make_archive
from passport.backend.takeout.test_utils.base import BaseTestCase


TEST_UID = 1
TEST_EXTRACT_ID = '123afecdefa123456'
TEST_ANOTHER_EXTRACT_ID = '456afedecedf1424'
TEST_UNIXTIME = 123456789

TEST_PASSWORD = 'pass'
TEST_ANOTHER_PASSWORD = 'pass2'

TEST_BUCKET = 'takeout'
TEST_FILE_CONTENT = b'test_content'


def encrypt_bytes(bytes_sequence):
    keys = get_keys_for_encrypting()
    key_version = get_config()['s3']['encryption_key_version']

    input_stream = io.BytesIO(bytes_sequence)
    output_file = encrypt_stream(
        input_stream,
        keys,
        key_version,
    )
    return output_file.read()


@with_settings(
    S3_ENDPOINT='http://s3.localhost/',
    S3_SECRET_KEY_ID='key-id',
    S3_SECRET_KEY='key',
    S3_CONNECT_TIMEOUT=1,
    S3_READ_TIMEOUT=1,
    S3_RETRIES=2,
    S3_TAKEOUT_BUCKET_NAME=TEST_BUCKET,

    PASSPORT_URL='http://passport.localhost/',
    PASSPORT_TIMEOUT=1,
    PASSPORT_RETRIES=2,
    PASSPORT_CONSUMER='takeout',

    BLACKBOX_URL='http://blackbox.localhost',
    BLACKBOX_TIMEOUT=1,
    BLACKBOX_RETRIES=2,
    BLACKBOX_USE_TVM=True,
    BLACKBOX_GET_HIDDEN_ALIASES=False,
)
class MakeArchiveTestCase(BaseTestCase):
    def setUp(self):
        super(MakeArchiveTestCase, self).setUp()

        encrypted_file_content = encrypt_bytes(TEST_FILE_CONTENT)

        self.s3_faker.set_response_side_effect(
            'list_objects',
            [
                s3_ok_response(
                    Contents=[
                        {
                            'Key': 'test_folder/1.jpg.kv1',
                            'Size': len(encrypted_file_content),
                        },
                        {
                            'Key': 'fake_async/2.jpg.kv1',
                            'Size': len(encrypted_file_content),
                        },
                        {
                            'Key': 'fake_async_upload/3.jpg.kv1',
                            'Size': len(encrypted_file_content),
                        },
                    ],
                ),
                s3_ok_response(
                    Contents=[],
                ),
            ],
        )
        self.s3_faker.set_response_side_effect(
            'download_fileobj',
            lambda Bucket, Key, Fileobj: (
                Fileobj.write(encrypted_file_content),
                Fileobj.seek(0),
            ),
        )
        self.s3_faker.set_response_side_effect('head_object', ClientError({'Error': {'Code': '404'}}, ''))
        self.s3_faker.set_response_value('put_object', s3_ok_response())

        self.passport_faker = FakePassport()
        self.passport_faker.start()
        self.passport_faker.set_response_value('takeout_finish_extract', passport_ok_response())

        self.test_dir = tempfile.mkdtemp()
        self.expected_archive_name = 'archive_%(extract_id)s_%(uid)s_%(ts)s.7z' % {
            'uid': TEST_UID,
            'extract_id': TEST_EXTRACT_ID,
            'ts': TEST_UNIXTIME,
        }
        self.expected_archive_filepath = '%(uid)s/%(extract_id)s/%(archive_name)s' % {
            'uid': TEST_UID,
            'extract_id': TEST_EXTRACT_ID,
            'archive_name': self.expected_archive_name,
        }

        def run_7z():
            with open(os.path.join(self.test_dir, self.expected_archive_filepath), 'w') as f:
                f.write('archive_content')
            return 'output', 'errors'

        self.random_patch = mock.patch('random.sample', mock.Mock(return_value=TEST_PASSWORD))
        self.random_patch.start()

        subprocess_mock = mock.MagicMock()
        subprocess_mock.poll.return_value = 0  # returncode
        subprocess_mock.communicate.side_effect = lambda *args, **kwargs: run_7z()
        subprocess_mock.__enter__.return_value = subprocess_mock
        self.popen_mock = mock.Mock(return_value=subprocess_mock)
        self.popen_patch = mock.patch('subprocess.Popen', self.popen_mock)
        self.popen_patch.start()

        self.shutil_move_mock = mock.Mock()
        self.shutil_move_patch = mock.patch('shutil.move', self.shutil_move_mock)
        self.shutil_move_patch.start()

        self.blackbox_faker = FakeBlackbox()
        self.blackbox_faker.start()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

        self.blackbox_faker.stop()
        self.shutil_move_patch.stop()
        self.popen_patch.stop()
        self.random_patch.stop()
        self.passport_faker.stop()

        super(MakeArchiveTestCase, self).tearDown()

    def setup_blackbox_userinfo_response(self, archive_key_suffix=None, account_exists=True):
        attributes = {}
        if archive_key_suffix:
            attributes['takeout.archive_s3_key'] = 'some_archive_{}_smth.7z'.format(archive_key_suffix)
        if account_exists:
            self.blackbox_faker.set_blackbox_response_value(
                method='userinfo',
                value=blackbox_userinfo_response(uid=TEST_UID, id=TEST_UID, attributes=attributes),
            )
        else:
            self.blackbox_faker.set_blackbox_response_value(
                method='userinfo',
                value=blackbox_userinfo_response(uid=None, id=TEST_UID),
            )

    def _test_ok(self):
        make_archive(uid=TEST_UID, extract_id=TEST_EXTRACT_ID, unixtime=TEST_UNIXTIME, cooking_directory=self.test_dir)

        assert self.s3_faker.calls_by_method('list_objects') == [
            {
                'Bucket': TEST_BUCKET,
                'Prefix': '%s/%s/' % (TEST_UID, TEST_EXTRACT_ID),
                'Marker': '',
                'MaxKeys': 1000,
            },
            {
                'Bucket': TEST_BUCKET,
                'Prefix': '%s/%s/' % (TEST_UID, TEST_EXTRACT_ID),
                'Marker': 'fake_async_upload/3.jpg.kv1',
                'MaxKeys': 1000,
            },
        ]
        assert self.s3_faker.calls_by_method('download_fileobj') == [
            {
                'Bucket': TEST_BUCKET,
                'Key': 'test_folder/1.jpg.kv1',
                'Fileobj': mock.ANY,
            },
            {
                'Bucket': TEST_BUCKET,
                'Key': 'fake_async/2.jpg.kv1',
                'Fileobj': mock.ANY,
            },
            {
                'Bucket': TEST_BUCKET,
                'Key': 'fake_async_upload/3.jpg.kv1',
                'Fileobj': mock.ANY,
            },
        ]
        assert_that(
            self.s3_faker.calls_by_method('put_object'),
            [
                has_entries(dict(
                    Body=all_of(
                        instance_of(io.IOBase),
                        has_property('name', '%s/%s' % (self.test_dir, self.expected_archive_filepath)),
                    ),
                    Bucket=TEST_BUCKET,
                    Key='res/%s' % self.expected_archive_filepath,
                )),
            ],
        )

        assert self.popen_mock.call_count == 1
        assert self.popen_mock.call_args[0] == (
            [
                '7z', 'a', '-mx=1', '-mem=AES128', '-mtc=off',
                '-p%s' % TEST_PASSWORD,
                self.expected_archive_name + '.zip',
                '%s/%s/%s/_data/*' % (self.test_dir, TEST_UID, TEST_EXTRACT_ID),
            ],
        )

        # перенос папки со всеми данными архива + один перенос при переименовании папки сервиса
        assert self.shutil_move_mock.call_count == 2

        assert len(self.passport_faker.requests) == 1
        self.passport_faker.requests[0].assert_properties_equal(
            method='POST',
            url='http://passport.localhost/1/bundle/takeout/extract/finish/?consumer=takeout',
            post_args={
                'uid': TEST_UID,
                'archive_s3_key': 'res/%s' % self.expected_archive_filepath,
                'archive_password': TEST_PASSWORD,
            },
        )

        userinfo_requests = self.blackbox_faker.get_requests_by_method('userinfo')
        assert len(userinfo_requests) == 1
        userinfo_requests[0].assert_post_data_contains(dict(
            attributes='170',
        ))
        assert 'get_public_name' not in userinfo_requests[0].post_args

        assert not os.path.exists(os.path.join(self.test_dir, '_data'))

    def test_ok__with_another_existing_archive(self):
        self.setup_blackbox_userinfo_response(archive_key_suffix=TEST_ANOTHER_EXTRACT_ID)
        self._test_ok()

    def test_ok__without_existing_archive(self):
        self.setup_blackbox_userinfo_response()
        self._test_ok()

    def _test_skip_passport_errors(self, passport_exception):
        self.setup_blackbox_userinfo_response()
        self.s3_faker.set_response_side_effect(
            'list_objects',
            [
                s3_ok_response(
                    Contents=[],
                ),
            ],
        )
        self.s3_faker.set_response_side_effect('head_object', s3_ok_response())

        maybe_make_dirs(os.path.join(self.test_dir, str(TEST_UID), str(TEST_EXTRACT_ID)))
        with open(os.path.join(self.test_dir, self.expected_archive_filepath), 'w') as f:
            f.write('empty')

        with open(os.path.join(self.test_dir, self.expected_archive_filepath + '.pwd'), 'w') as f:
            f.write(TEST_ANOTHER_PASSWORD + '\n')

        self.passport_faker.set_response_side_effect('takeout_finish_extract', passport_exception)

        make_archive(uid=TEST_UID, extract_id=TEST_EXTRACT_ID, unixtime=TEST_UNIXTIME, cooking_directory=self.test_dir)

        assert len(self.s3_faker.calls_by_method('list_objects')) == 1
        assert not self.s3_faker.calls_by_method('download_fileobj')  # новых файлов в S3 не нашлось, скачивать нечего
        assert_that(
            self.s3_faker.calls_by_method('put_object'),
            [
                has_entries(dict(
                    Body=all_of(
                        instance_of(io.IOBase),
                        has_property('name', '%s/%s' % (
                        self.test_dir, self.expected_archive_filepath)),
                    ),
                    Bucket=TEST_BUCKET,
                    Key='res/%s' % self.expected_archive_filepath,
                )),
            ],
        )

        # архив уже есть на диске, не пересобираем
        assert not self.popen_mock.called
        assert not self.shutil_move_mock.called

        assert len(self.passport_faker.requests) == 1
        self.passport_faker.requests[0].assert_properties_equal(
            method='POST',
            url='http://passport.localhost/1/bundle/takeout/extract/finish/?consumer=takeout',
            post_args={
                'uid': TEST_UID,
                'archive_s3_key': 'res/%s' % self.expected_archive_filepath,
                'archive_password': TEST_ANOTHER_PASSWORD,  # пароль прочитан с диска, а не сгенерён заново
            },
        )

        assert not os.path.exists(os.path.join(self.test_dir, '_data'))

    def test_all_already_done(self):
        self._test_skip_passport_errors(PassportActionNotRequiredError)

    def test_account_not_found(self):
        self._test_skip_passport_errors(PassportAccountNotFoundError)

    def test_blackbox_archive_exists(self):
        self.setup_blackbox_userinfo_response(archive_key_suffix=TEST_EXTRACT_ID)
        make_archive(uid=TEST_UID, extract_id=TEST_EXTRACT_ID, unixtime=TEST_UNIXTIME, cooking_directory=self.test_dir)

        assert not self.s3_faker.calls_by_method('list_objects')
        assert not self.s3_faker.calls_by_method('download_fileobj')
        assert not self.s3_faker.calls_by_method('put_object')

        assert self.popen_mock.call_count == 0
        assert self.shutil_move_mock.call_count == 0
        assert len(self.passport_faker.requests) == 0
        assert not os.path.exists(os.path.join(self.test_dir, '_data'))

    def test_non_existing_account(self):
        self.setup_blackbox_userinfo_response(account_exists=False)
        make_archive(uid=TEST_UID, extract_id=TEST_EXTRACT_ID, unixtime=TEST_UNIXTIME, cooking_directory=self.test_dir)

        assert not self.s3_faker.calls_by_method('list_objects')
        assert not self.s3_faker.calls_by_method('download_fileobj')
        assert not self.s3_faker.calls_by_method('put_object')

        assert self.popen_mock.call_count == 0
        assert self.shutil_move_mock.call_count == 0
        assert len(self.passport_faker.requests) == 0
        assert not os.path.exists(os.path.join(self.test_dir, '_data'))
