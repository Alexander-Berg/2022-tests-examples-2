# -*- coding: utf-8 -*-
from io import BytesIO

from botocore.exceptions import ClientError
from passport.backend.core.s3 import S3PermanentError
from passport.backend.takeout.api.grants import GRANT_UPLOAD_FILE
from passport.backend.takeout.api.views.forms import UploadForm
from passport.backend.takeout.common.job_id import make_job_id_v1
from passport.backend.takeout.common.touch import TouchFiles
from passport.backend.takeout.test_utils.base import BaseTestCase
from passport.backend.takeout.test_utils.forms import assert_form_errors
import pytest
from werkzeug.datastructures import (
    FileStorage,
    MultiDict,
)
import yenv


TEST_UID = 123


@pytest.mark.parametrize(
    'input_form',
    [
        MultiDict({
            'consumer': 'dev',
            'job_id': make_job_id_v1(
                str(TEST_UID),
                'test-service',
                'test-extract-id',
            ),
            'file': FileStorage(
                stream=BytesIO(),
                filename='test-file-name',
            ),
        }),
    ],
)
def test_form_valid(input_form):
    form = UploadForm(formdata=input_form)
    assert form.validate()


@pytest.mark.parametrize(
    'input_form',
    [
        MultiDict({}),
        MultiDict({'consumer': 'dev'}),
        MultiDict({'job_id': '123'}),
        MultiDict({'file': '123'}),
        MultiDict({
            'file': FileStorage(
                stream=BytesIO(),
                filename='bad/filename',
            ),
        }),
        MultiDict({
            'file': FileStorage(
                stream=BytesIO(),
                filename='bad/filename',
            ),
            'job_id': make_job_id_v1(
                str(TEST_UID),
                'test-service',
                'test-extract-id',
            ),
        }),
        MultiDict({
            'file': FileStorage(
                stream=BytesIO(),
                filename='BAD_FILENAME',
            ),
            'job_id': make_job_id_v1(
                str(TEST_UID),
                'test-service',
                'test-extract-id',
            ),
        }),
        MultiDict({'job_id': '123', 'file': '123'}),
    ],
)
def test_form_invalid(input_form):
    form = UploadForm(formdata=input_form)
    assert not form.validate()


class UploadFileTestCase(BaseTestCase):
    def setUp(self):
        super(UploadFileTestCase, self).setUp()
        self.job_id = make_job_id_v1(str(TEST_UID), 'fake_async_upload', 'test-extract-id')

    def test_upload_missing_job_id_and_filename(self):
        self.grants_faker.set_grant_list([GRANT_UPLOAD_FILE])

        rv = self.client.post(
            '/1/upload/?consumer=dev',
        )
        assert_form_errors(rv, status='job_id.invalid')

    def test_upload_no_grants(self):
        self.grants_faker.set_grant_list([])

        rv = self.client.post(
            '/1/upload/?consumer=dev',
            data={
                'job_id': 'foo',
                'file': (BytesIO(b'Hello'), 'hello.txt'),
            },
        )
        assert_form_errors(rv, status='job_id.invalid')

    def test_upload_invalid_job_id(self):
        self.grants_faker.set_grant_list([GRANT_UPLOAD_FILE])

        rv = self.client.post(
            '/1/upload/?consumer=dev',
            data={
                'job_id': 'foo',
                'file': (BytesIO(b'Hello'), 'hello.txt'),
            },
        )
        assert_form_errors(rv, status='job_id.invalid')

    def test_upload_process_not_started(self):
        self.grants_faker.set_grant_list([GRANT_UPLOAD_FILE])

        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # STARTED
        ])

        rv = self.client.post(
            '/1/upload/?consumer=dev',
            data={
                'job_id': self.job_id,
                'file': (BytesIO(b'hello'), 'hello.txt'),
            },
        )

        assert rv.status_code == 200
        assert rv.json == {
            'status': 'job_id.invalid',
            'error': 'Not ready to receive files',
        }

        # была проверка на начало процесса
        self.touch_faker.assert_was_checked([
            TouchFiles.AsyncUpload.STARTED,
        ])

    def test_upload_process_already_done(self):
        self.grants_faker.set_grant_list([GRANT_UPLOAD_FILE])

        self.touch_faker.setup_set_mask([
            self.touch_faker.State.SET,  # STARTED
            self.touch_faker.State.SET,  # DONE
        ])

        rv = self.client.post(
            '/1/upload/?consumer=dev',
            data={
                'job_id': self.job_id,
                'file': (BytesIO(b'hello'), 'hello.txt'),
            },
        )

        assert rv.status_code == 200
        assert rv.json == {
            'status': 'job_id.invalid',
            'error': 'Task is complete',
        }

        # была проверка на начало и завершение процесса
        self.touch_faker.assert_was_checked([
            TouchFiles.AsyncUpload.STARTED,
            TouchFiles.AsyncUpload.DONE,
        ])

    def test_upload_ok(self):
        self.grants_faker.set_grant_list([GRANT_UPLOAD_FILE])

        self.touch_faker.setup_set_mask([
            self.touch_faker.State.SET,  # STARTED
            self.touch_faker.State.UNSET,  # DONE
        ])

        self.s3_faker.set_response_side_effect(
            'head_object',
            [
                None,
                ClientError({'Error': {'Code': '404'}}, 'test-arg'),
            ],
        )

        rv = self.client.post(
            '/1/upload/?consumer=dev',
            data={
                'job_id': self.job_id,
                'file': (BytesIO(b'hello'), 'hello.txt'),
            }
        )
        assert rv.status_code == 200
        assert rv.json == {'status': 'ok'}

        # была проверка на начало и завершение процесса
        self.touch_faker.assert_was_checked([
            TouchFiles.AsyncUpload.STARTED,
            TouchFiles.AsyncUpload.DONE,
        ])

        # был залит файл
        assert len(self.s3_faker.calls_by_method('put_object')) == 1
        assert 'hello.txt' in self.s3_faker.calls_by_method('put_object')[0]['Key']

    def test_s3_error(self):
        self.grants_faker.set_grant_list([GRANT_UPLOAD_FILE])

        self.s3_faker.set_response_side_effect(
            'head_object',
            S3PermanentError('S3 crashed'),
        )

        rv = self.client.post(
            '/1/upload/?consumer=dev',
            data={
                'job_id': self.job_id,
                'file': (BytesIO(b'hello'), 'hello.txt'),
            }
        )
        assert rv.status_code == 200
        assert rv.json == {
            'status': 'error',
            'error': 's3.unavailable',
            'description': 'S3PermanentError: S3 crashed',
            'env': yenv.type,
        }
