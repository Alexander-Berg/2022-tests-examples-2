# -*- coding: utf-8 -*-
from passport.backend.takeout.common.job_id import make_job_id_v1
from passport.backend.takeout.common.touch import TouchFiles
from passport.backend.takeout.test_utils.base import BaseTestCase


TEST_UID = 123
TEST_UNIXTIME = 123456789


class FakeServicesTestCase(BaseTestCase):
    def test_get_file(self):
        rv = self.client.get('/1/test/fake_services/get_file/?file_name=test')
        assert rv.data == b'test content'
        assert rv.headers['Content-Disposition'] == 'attachment; filename="test"'

    def test_sync_user_info(self):
        rv = self.client.post('/1/test/fake_services/sync/user_info/')
        assert rv.json == {
            'status': 'ok',
            'data': {
                '1.txt': 'Content 1',
                '2.txt': 'Content 2',
            },
            'file_links': [
                'http://localhost/1/test/fake_services/get_file/?file_name=3.txt',
                'http://localhost/1/test/fake_services/get_file/?file_name=4.txt'
            ],
        }

    def test_async_start(self):
        rv = self.client.post('/1/test/fake_services/async/start/')
        assert rv.json == {
            'status': 'ok',
            'job_id': 'job-id',
        }

    def test_async_user_info(self):
        rv = self.client.post('/1/test/fake_services/async/user_info/')
        assert rv.json == {
            'status': 'ok',
            'data': {
                '1.txt': 'Content 1',
                '2.txt': 'Content 2',
            },
            'file_links': [
                'http://localhost/1/test/fake_services/get_file/?file_name=3.txt',
                'http://localhost/1/test/fake_services/get_file/?file_name=4.txt'
            ],
        }

    def test_async_upload_start(self):
        job_id = make_job_id_v1(str(TEST_UID), 'fake_async_upload', 'test-extract-id')
        rv = self.client.post(
            '/1/test/fake_services/async_upload/start/',
            data={
                'uid': TEST_UID,
                'unixtime': TEST_UNIXTIME,
                'job_id': job_id,
            },
        )
        assert rv.json == {
            'status': 'ok',
        }
        assert len(self.s3_faker.calls_by_method('put_object')) == 1
        assert '5.txt' in self.s3_faker.calls_by_method('put_object')[0]['Key']

        assert len(self.fake_redis.redis_calls_by_method('setex')) == 1
        self.touch_faker.assert_is_set([
            TouchFiles.AsyncUpload.DONE,
        ])
