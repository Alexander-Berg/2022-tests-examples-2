# -*- coding: utf-8 -*-
from passport.backend.core.s3.faker.fake_s3 import s3_ok_response
from passport.backend.takeout.logbroker_client.tasks.cleanup import cleanup_local
from passport.backend.takeout.test_utils.base import BaseTestCase


TEST_UID = 1
TEST_EXTRACT_ID = '123'


class CleanupLocalTestCase(BaseTestCase):
    def setUp(self):
        super(CleanupLocalTestCase, self).setUp()

        self.s3_faker.set_response_value(
            'delete_object',
            s3_ok_response(status=204),
        )
        self.s3_faker.set_response_side_effect(
            'list_objects',
            [
                s3_ok_response(
                    Contents=[
                        {
                            'Key': '%s/%s/passport/.takeout-touch/sync-started' % (TEST_UID, TEST_EXTRACT_ID),
                        },
                        {
                            'Key': '%s/%s/passport/1.jpg.kv1' % (TEST_UID, TEST_EXTRACT_ID),
                        },
                        {
                            'Key': '%s/%s/mail/2.jpg.kv1' % (TEST_UID, TEST_EXTRACT_ID),
                        },
                    ],
                ),
                s3_ok_response(
                    Contents=[
                        {
                            'Key': '%s/%s/disk/3.jpg.kv1' % (TEST_UID, TEST_EXTRACT_ID),
                        },
                    ],
                ),
                s3_ok_response(
                    Contents=[],
                ),
            ],
        )

    def test_ok(self):
        cleanup_local(uid=TEST_UID, extract_id=TEST_EXTRACT_ID)
        assert len(self.s3_faker.calls_by_method('list_objects')) == 3
        assert self.s3_faker.calls_by_method('delete_object') == [
            {'Bucket': 'takeout', 'Key': '1/123/passport/1.jpg.kv1'},
            {'Bucket': 'takeout', 'Key': '1/123/mail/2.jpg.kv1'},
            {'Bucket': 'takeout', 'Key': '1/123/disk/3.jpg.kv1'},
        ]
