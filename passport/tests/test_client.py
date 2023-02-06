# -*- coding: utf-8 -*-

import io
from unittest import TestCase

from boto3.exceptions import S3UploadFailedError
from botocore.exceptions import ClientError
from hamcrest import (
    all_of,
    assert_that,
    has_entries,
    has_property,
    instance_of,
)
from nose.tools import (
    assert_is_none,
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.s3 import (
    get_s3_client,
    S3PermanentError,
)
from passport.backend.core.s3.exceptions import FileNotFoundError
from passport.backend.core.s3.faker.fake_s3 import (
    FakeS3Client,
    s3_ok_response,
)
from passport.backend.core.test.test_utils import with_settings
from six.moves import StringIO


TEST_BUCKET_NAME = 'test_bucket'


@with_settings(
    S3_ENDPOINT='http://localhost/s3',
    S3_SECRET_KEY_ID='key_id',
    S3_SECRET_KEY='key',
    S3_CONNECT_TIMEOUT=1,
    S3_READ_TIMEOUT=1,
    S3_RETRIES=2,
    S3_PRESIGNED_URL_TTL=10,
    S3_TAKEOUT_BUCKET_NAME=TEST_BUCKET_NAME,
)
class TestS3Client(TestCase):
    def setUp(self):
        super(TestS3Client, self).setUp()
        self.faker = FakeS3Client()
        self.faker.start()

        self.s3 = get_s3_client()

    def tearDown(self):
        self.faker.stop()
        del self.faker
        del self.s3
        super(TestS3Client, self).tearDown()

    def test_file_exists_ok(self):
        self.faker.set_response_value(
            'head_object',
            s3_ok_response(),
        )
        rv = self.s3.file_exists('test_folder/kitten.jpg')
        ok_(rv)
        eq_(
            self.faker.calls_by_method('head_object'),
            [
                dict(Bucket=TEST_BUCKET_NAME, Key='test_folder/kitten.jpg'),
            ],
        )

    def test_file_exists_not_found(self):
        self.faker.set_response_side_effect(
            'head_object',
            ClientError({'Error': {'Code': '404'}}, 'test-arg'),
        )
        ok_(not self.s3.file_exists('test_folder/kitten.jpg'))

    def test_read_file_ok(self):
        self.faker.set_response_value(
            'get_object',
            s3_ok_response(Body=StringIO('test data')),
        )
        rv = self.s3.read_file('test_folder/kitten.jpg')
        eq_(rv, 'test data')
        eq_(
            self.faker.calls_by_method('get_object'),
            [
                dict(Bucket=TEST_BUCKET_NAME, Key='test_folder/kitten.jpg'),
            ],
        )

    def test_read_file_not_found(self):
        self.faker.set_response_side_effect(
            'get_object',
            ClientError({'Error': {'Code': 'NoSuchKey'}}, 'test-arg'),
        )
        with assert_raises(FileNotFoundError):
            self.s3.read_file('test_folder/kitten.jpg')

    def test_download_fileobj_ok(self):
        self.faker.set_response_value(
            'download_fileobj',
            None,
        )
        out = StringIO()
        rv = self.s3.download_fileobj('test_folder/kitten.jpg', out)
        eq_(rv, None)
        eq_(
            self.faker.calls_by_method('download_fileobj'),
            [
                dict(
                    Bucket=TEST_BUCKET_NAME,
                    Key='test_folder/kitten.jpg',
                    Fileobj=out,
                ),
            ],
        )

    def test_download_fileobj_not_found(self):
        self.faker.set_response_side_effect(
            'download_fileobj',
            ClientError({'Error': {'Code': '404'}}, 'test-arg'),
        )
        with assert_raises(S3PermanentError):
            self.s3.download_fileobj('test_folder/kitten.jpg', StringIO())

    def test_upload_file_ok(self):
        rv = self.s3.upload_file('/etc/passwd', 'test_folder', 'kitten.jpg')
        eq_(rv, 'test_folder/kitten.jpg')

        assert_that(
            self.faker.calls_by_method('put_object'),
            [
                has_entries(dict(
                    Body=all_of(
                        instance_of(io.IOBase),
                        has_property('name', '/etc/passwd'),
                    ),
                    Bucket=TEST_BUCKET_NAME,
                    Key='test_folder/kitten.jpg',
                )),
            ],
        )

    def test_upload_file_error(self):
        self.faker.set_response_side_effect('put_object', S3UploadFailedError())
        with assert_raises(S3PermanentError):
            self.s3.upload_file('/etc/passwd', 'test_folder', 'kitten.jpg')

    def test_upload_fileobj_ok(self):
        fileobj = StringIO('my password')
        rv = self.s3.upload_fileobj(fileobj, 'test_folder', 'kitten.jpg')
        eq_(rv, 'test_folder/kitten.jpg')
        eq_(
            self.faker.calls_by_method('put_object'),
            [
                dict(Bucket=TEST_BUCKET_NAME, Key='test_folder/kitten.jpg', Body=fileobj),
            ],
        )

    def test_upload_fileobj_error(self):
        self.faker.set_response_side_effect('put_object', S3UploadFailedError())
        with assert_raises(S3PermanentError):
            self.s3.upload_fileobj(StringIO('my password'), 'test_folder', 'kitten.jpg')

    def test_upload_fileobj_client_error(self):
        self.faker.set_response_side_effect('put_object', ClientError({'Error': {'Code': '500'}}, 'test-arg'))
        with assert_raises(S3PermanentError):
            self.s3.upload_fileobj(StringIO('my password'), 'test_folder', 'kitten.jpg')

    def test_list_files_ok(self):
        self.faker.set_response_value('list_objects', s3_ok_response(Contents=[{'Key': 'test_folder/puppy.jpg'}]))
        rv = self.s3.list_files(folder='test_folder', limit=2, last_seen_key='test_folder/kitten.jpg')
        eq_(rv, [{'Key': 'test_folder/puppy.jpg'}])
        eq_(
            self.faker.calls_by_method('list_objects'),
            [
                dict(Bucket=TEST_BUCKET_NAME, Prefix='test_folder/', MaxKeys=2, Marker='test_folder/kitten.jpg'),
            ],
        )

    def test_list_files_error(self):
        self.faker.set_response_value('list_objects', s3_ok_response(status=500))
        with assert_raises(S3PermanentError):
            self.s3.list_files(folder='', limit=100)

    def test_iterate_files_by_chunks_ok(self):
        self.faker.set_response_side_effect(
            'list_objects',
            [
                s3_ok_response(
                    Contents=[
                        {'Key': 'test_folder/1.jpg'},
                        {'Key': 'test_folder/2.jpg'},
                    ],
                ),
                s3_ok_response(
                    Contents=[
                        {'Key': 'test_folder/3.jpg'},
                    ],
                ),
                s3_ok_response(
                    Contents=[],
                ),
            ],
        )
        iterator = self.s3.iterate_files_by_chunks(folder='test_folder', chunk_size=2)
        eq_(
            next(iterator),
            [
                {'Key': 'test_folder/1.jpg'},
                {'Key': 'test_folder/2.jpg'},
            ],
        )
        eq_(
            next(iterator),
            [
                {'Key': 'test_folder/3.jpg'},
            ],
        )
        with assert_raises(StopIteration):
            next(iterator)

        eq_(len(self.faker.calls_by_method('list_objects')), 3)

    def test_delete_file_ok(self):
        self.faker.set_response_value('delete_object', s3_ok_response(status=204))
        rv = self.s3.delete_file(key='test_folder/kitten.jpg')
        assert_is_none(rv)
        eq_(
            self.faker.calls_by_method('delete_object'),
            [
                dict(Bucket=TEST_BUCKET_NAME, Key='test_folder/kitten.jpg'),
            ],
        )

    def test_delete_file_error(self):
        self.faker.set_response_value('delete_object', s3_ok_response(status=500))
        with assert_raises(S3PermanentError):
            self.s3.delete_file(key='test_folder/kitten.jpg')

    def test_generate_presigned_url_for_file_ok(self):
        self.faker.set_response_value('generate_presigned_url', 'https://some.url')
        rv = self.s3.generate_presigned_url_for_file(key='test_folder/kitten.jpg', expires_in=5)
        eq_(rv, 'https://some.url')
        eq_(
            self.faker.calls_by_method('generate_presigned_url'),
            [
                dict(
                    ClientMethod='get_object',
                    Params=dict(
                        Bucket=TEST_BUCKET_NAME,
                        Key='test_folder/kitten.jpg',
                        ResponseContentType='application/x-gzip',
                    ),
                    ExpiresIn=5,
                ),
            ],
        )
