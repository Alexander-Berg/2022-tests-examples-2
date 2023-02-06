# -*- coding: utf-8 -*-
import mock
from passport.backend.takeout.api.grants import GRANT_DEBUG_GET_STATUS
from passport.backend.takeout.common.conf.services import ServiceConfig
from passport.backend.takeout.test_utils.base import BaseTestCase


TEST_UID = 1
TEST_EXTRACT_ID = 'extract-id'
TEST_SERVICE_NAME = 'test-service'
TEST_OTHER_SERVICE_NAME = 'other'
TEST_ONE_MORE_SERVICE_NAME = 'one-more'

TEST_SERVICES_CONFIG = {
    TEST_SERVICE_NAME: ServiceConfig.from_dict({
        'enabled': True,
        'type': 'sync',
        'tvm_dst_alias': 'fake_sync',
        'urls': {'base': ''},
        'run_integration_test_consumers': ['dev'],
    }),
    TEST_OTHER_SERVICE_NAME: ServiceConfig.from_dict({
        'enabled': True,
        'type': 'async',
        'tvm_dst_alias': 'fake_async',
        'urls': {'base': ''},
        'run_integration_test_consumers': [],
    }),
    TEST_ONE_MORE_SERVICE_NAME: ServiceConfig.from_dict({
        'enabled': True,
        'type': 'async_upload',
        'tvm_dst_alias': 'fake_async_upload',
        'urls': {'base': ''},
        'run_integration_test_consumers': [],
    }),
}


class DebugGetStatusTestCase(BaseTestCase):
    def setUp(self):
        super(DebugGetStatusTestCase, self).setUp()

        self.grants_faker.set_grant_list([GRANT_DEBUG_GET_STATUS])
        self.services_patch = mock.patch(
            'passport.backend.takeout.api.views.get_status.get_service_configs',
            mock.Mock(return_value=TEST_SERVICES_CONFIG)
        )
        self.services_patch.start()

    def tearDown(self):
        self.services_patch.stop()
        super(DebugGetStatusTestCase, self).tearDown()

    def test_no_grants(self):
        self.grants_faker.set_grant_list([])

        rv = self.client.post(
            '/1/debug/get_status/?consumer=dev',
            data={
                'uid': TEST_UID,
                'extract_id': TEST_EXTRACT_ID,
                'service_name': TEST_SERVICE_NAME,
            },
        )
        assert rv.status_code == 403

    def test_get_one_service_ok(self):
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.UNSET,  # DONE
            self.touch_faker.State.SET,  # STARTED
        ])

        rv = self.client.post(
            '/1/debug/get_status/?consumer=dev',
            data={
                'uid': TEST_UID,
                'extract_id': TEST_EXTRACT_ID,
                'service_name': TEST_SERVICE_NAME,
            },
        )
        assert rv.status_code == 200, rv.data
        assert rv.json == {
            'status': 'ok',
            'services': {
                TEST_SERVICE_NAME: {'status': 'started'},
            },
        }

    def test_get_several_services_ok(self):
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.SET,  # DONE
            self.touch_faker.State.SET,  # DONE
        ])

        rv = self.client.post(
            '/1/debug/get_status/?consumer=dev',
            data={
                'uid': TEST_UID,
                'extract_id': TEST_EXTRACT_ID,
                'service_name': [TEST_SERVICE_NAME, TEST_OTHER_SERVICE_NAME],
            },
        )
        assert rv.status_code == 200, rv.data
        assert rv.json == {
            'status': 'ok',
            'services': {
                TEST_SERVICE_NAME: {'status': 'done'},
                TEST_OTHER_SERVICE_NAME: {'status': 'done'},
            },
        }

    def test_get_all_services_ok(self):
        self.touch_faker.setup_set_mask([
            self.touch_faker.State.SET,  # DONE
            self.touch_faker.State.SET,  # DONE
            self.touch_faker.State.SET,  # DONE
        ])

        rv = self.client.post(
            '/1/debug/get_status/?consumer=dev',
            data={
                'uid': TEST_UID,
                'extract_id': TEST_EXTRACT_ID,
            },
        )
        assert rv.status_code == 200, rv.data
        assert rv.json == {
            'status': 'ok',
            'services': {
                TEST_SERVICE_NAME: {'status': 'done'},
                TEST_OTHER_SERVICE_NAME: {'status': 'done'},
                TEST_ONE_MORE_SERVICE_NAME: {'status': 'done'},
            },
        }
