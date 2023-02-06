# -*- coding: utf-8 -*-
from passport.backend.core.s3.faker.fake_s3 import s3_ok_response
from passport.backend.takeout.api.grants import GRANT_UPLOAD_DONE
from passport.backend.takeout.api.views.forms import DoneForm
from passport.backend.takeout.common.job_id import make_job_id_v1
from passport.backend.takeout.common.touch import TouchFiles
from passport.backend.takeout.common.utils import s3_path
from passport.backend.takeout.test_utils.base import BaseTestCase
from passport.backend.takeout.test_utils.forms import assert_form_errors
import pytest
from werkzeug.datastructures import MultiDict


TEST_UID = 123


@pytest.mark.parametrize(
    'input_form',
    [
        MultiDict([
            ('consumer', 'dev'),
            ('job_id', make_job_id_v1(
                str(TEST_UID),
                'test-service',
                'test-extract-id',
            )),
            ('filename', 'filename-1'),
            ('filename', 'filename-2'),
            ('filename', 'a' * 255),
        ]),
        MultiDict({
            'job_id': make_job_id_v1(str(TEST_UID), 'test-service', 'test-extract-id'),
            'consumer': 'dev',
        }),
    ],
)
def test_form_valid(input_form):
    form = DoneForm(formdata=input_form)
    assert form.validate()


@pytest.mark.parametrize(
    'input_form',
    [
        MultiDict({}),
        MultiDict({'consumer': 'dev'}),
        MultiDict({'job_id': '123'}),
        MultiDict({'filename': '123'}),
        MultiDict({
            'filename': '',
            'job_id': make_job_id_v1(str(TEST_UID), 'test-service', 'test-extract-id'),
        }),
        MultiDict({
            'filename': 'bad/filename',
            'job_id': make_job_id_v1(str(TEST_UID), 'test-service', 'test-extract-id'),
        }),
        MultiDict({
            'filename': 'FILENAME',
            'job_id': make_job_id_v1(str(TEST_UID), 'test-service', 'test-extract-id'),
        }),
        MultiDict({
            'filename': 'a' * 256,
            'job_id': make_job_id_v1(str(TEST_UID), 'test-service', 'test-extract-id'),
        }),
    ],
)
def test_form_invalid(input_form):
    form = DoneForm(formdata=input_form)
    assert not form.validate()


class UploadDoneTestCase(BaseTestCase):
    def setUp(self):
        super(UploadDoneTestCase, self).setUp()
        self.job_id = make_job_id_v1(str(TEST_UID), 'fake_async_upload', 'test-extract-id')

    def test_upload_done_signature_mismatch(self):
        self.grants_faker.set_grant_list([GRANT_UPLOAD_DONE])

        another_job_id = self.job_id.replace('test-extract-id', 'another-extract-id')

        rv = self.client.post(
            '/1/upload/done/?consumer=dev',
            data={
                'job_id': another_job_id,
            },
        )
        assert rv.status_code == 400
        assert rv.json == {'status': 'job_id.invalid', 'error': 'SignatureMismatch'}

    def test_upload_done_missing_job_id_and_filename(self):
        rv = self.client.post(
            '/1/upload/done/?consumer=dev',
        )
        assert_form_errors(rv, status='job_id.invalid')

    def test_upload_done_invalid_job_id(self):
        rv = self.client.post(
            '/1/upload/done/?consumer=dev',
            data={
                'job_id': 'foo',
            },
        )
        assert_form_errors(rv, status='job_id.invalid')

    def test_upload_done_no_grants(self):
        self.grants_faker.set_grant_list([])
        rv = self.client.post(
            '/1/upload/done/?consumer=dev',
            data={
                'job_id': self.job_id,
            },
        )
        assert rv.status_code == 403

    def test_upload_done_already_done(self):
        self.grants_faker.set_grant_list([GRANT_UPLOAD_DONE])

        self.touch_faker.setup_set_mask([
            self.touch_faker.State.SET,  # DONE
        ])

        rv = self.client.post(
            '/1/upload/done/?consumer=dev',
            data=MultiDict([
                ('job_id', self.job_id),
                ('filename', 'file1'),
                ('filename', 'file2'),
                ('filename', 'file3'),
            ]),
        )
        assert rv.status_code == 200
        assert rv.json == {'status': 'ok'}

        self.touch_faker.assert_was_checked([
            TouchFiles.AsyncUpload.DONE,
        ])
        self.touch_faker.assert_is_set([])

    def test_upload_done_missing_files(self):
        self.grants_faker.set_grant_list([GRANT_UPLOAD_DONE])

        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # DONE
            self.touch_faker.State.SET,  # STARTED
        ])

        touch_file_key = TouchFiles(TEST_UID, 'test-extract-id', 'fake_async_upload').get_s3_key('touch-file')

        self.s3_faker.set_response_side_effect(
            'list_objects',
            [
                s3_ok_response(
                    Contents=[
                        {'Key': s3_path(TEST_UID, 'test-extract-id', 'fake_async_upload', 'file1')},
                        {'Key': s3_path(TEST_UID, 'test-extract-id', 'fake_async_upload', 'file2')},
                        {'Key': s3_path(TEST_UID, 'test-extract-id', 'fake_async_upload', 'file4')},
                        {'Key': touch_file_key},
                    ],
                ),
                s3_ok_response(
                    Contents=[],
                ),
            ]
        )

        rv = self.client.post(
            '/1/upload/done/?consumer=dev',
            data=MultiDict([
                ('job_id', self.job_id),
                ('filename', 'file1'),
                ('filename', 'file2'),
                ('filename', 'file3'),
            ]),
        )
        assert rv.status_code == 200
        assert rv.json == {
            'status': 'missing',
            'missing_files': [
                'file3',
            ],
            'extra_files': [
                'file4',
            ],
        }

        self.touch_faker.assert_was_checked([
            TouchFiles.AsyncUpload.DONE,
            TouchFiles.AsyncUpload.STARTED,
        ])
        self.touch_faker.assert_is_set([])

    def test_upload_done_ok(self):
        self.grants_faker.set_grant_list([GRANT_UPLOAD_DONE])

        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # DONE
            self.touch_faker.State.SET,  # STARTED
        ])

        touch_file_key = TouchFiles(TEST_UID, 'test-extract-id', 'fake_async_upload').get_s3_key('touch-file')

        self.s3_faker.set_response_side_effect(
            'list_objects',
            [
                s3_ok_response(
                    Contents=[
                        {'Key': s3_path(TEST_UID, 'test-extract-id', 'fake_async_upload', 'file1')},
                        {'Key': s3_path(TEST_UID, 'test-extract-id', 'fake_async_upload', 'file2')},
                        {'Key': s3_path(TEST_UID, 'test-extract-id', 'fake_async_upload', 'file3')},
                        {'Key': touch_file_key},
                    ],
                ),
                s3_ok_response(
                    Contents=[],
                ),
            ],
        )

        rv = self.client.post(
            '/1/upload/done/?consumer=dev',
            data=MultiDict([
                ('job_id', self.job_id),
                ('filename', 'file1'),
                ('filename', 'file2'),
                ('filename', 'file3'),
            ]),
        )
        assert rv.status_code == 200
        assert rv.json == {'status': 'ok'}

        self.touch_faker.assert_is_set([
            TouchFiles.AsyncUpload.DONE,
        ])
