# -*- coding: utf-8 -*-

import json

from passport.backend.core.builders.drive_api.drive_api import (
    DriveApiPermanentError,
    DriveApiTemporaryError,
    get_drive_api,
)
from passport.backend.core.builders.drive_api.faker import (
    drive_api_find_drive_session_id_access_denied_response,
    drive_api_find_drive_session_id_found_response,
    drive_api_find_drive_session_id_not_found_response,
    drive_api_find_drive_session_id_unknown_device_response,
    FakeDriveApi,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


DRIVE_DEVICE_ID1 = 'device_id1'
DRIVE_SESSION_ID1 = 'drive_session_id1'


class BaseDriveApiTestCase(PassportTestCase):
    def setUp(self):
        super(BaseDriveApiTestCase, self).setUp()
        self.fake_drive_api = FakeDriveApi()
        self.fake_drive_api.start()
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.start()

        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'drive_api',
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )

        self.drive_api = get_drive_api()

    def tearDown(self):
        del self.drive_api
        self.fake_drive_api.stop()
        del self.fake_drive_api
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager
        super(BaseDriveApiTestCase, self).tearDown()


@with_settings_hosts(
    DRIVE_API_RETRIES=1,
    DRIVE_API_TIMEOUT=1,
    DRIVE_API_URL='https://drive_api',
)
class TestFindDriveSessionIdRequest(BaseDriveApiTestCase):
    def setUp(self):
        super(TestFindDriveSessionIdRequest, self).setUp()
        self.fake_drive_api.set_response_side_effect(
            'find_drive_session_id',
            [
                drive_api_find_drive_session_id_found_response(DRIVE_SESSION_ID1),
            ],
        )

    def test(self):
        self.drive_api.find_drive_session_id(DRIVE_DEVICE_ID1)

        self.assertEqual(len(self.fake_drive_api.requests), 1)
        self.fake_drive_api.requests[0].assert_url_starts_with('https://drive_api/api/staff/head/session?')
        self.fake_drive_api.requests[0].assert_properties_equal(
            method='GET',
            headers={'X-Ya-Service-Ticket': TEST_TICKET},
        )
        self.fake_drive_api.requests[0].assert_query_equals(
            {
                'device_id': DRIVE_DEVICE_ID1,
            },
        )


@with_settings_hosts(
    DRIVE_API_RETRIES=1,
    DRIVE_API_TIMEOUT=1,
    DRIVE_API_URL='https://drive_api',
)
class TestFindDriveSessionIdResponse(BaseDriveApiTestCase):
    def test_found(self):
        self.fake_drive_api.set_response_side_effect(
            'find_drive_session_id',
            [
                drive_api_find_drive_session_id_found_response(DRIVE_SESSION_ID1),
            ],
        )

        drive_session_id = self.drive_api.find_drive_session_id(DRIVE_DEVICE_ID1)

        self.assertEqual(drive_session_id, DRIVE_SESSION_ID1)

    def test_not_found(self):
        self.fake_drive_api.set_response_side_effect(
            'find_drive_session_id',
            [
                drive_api_find_drive_session_id_not_found_response(),
            ],
        )

        drive_session_id = self.drive_api.find_drive_session_id(DRIVE_DEVICE_ID1)

        self.assertIsNone(drive_session_id)

    def test_unknown_device(self):
        self.fake_drive_api.set_response_side_effect(
            'find_drive_session_id',
            [
                drive_api_find_drive_session_id_unknown_device_response(),
            ],
        )

        drive_session_id = self.drive_api.find_drive_session_id(DRIVE_DEVICE_ID1)

        self.assertIsNone(drive_session_id)

    def test_access_denied(self):
        self.fake_drive_api.set_response_side_effect(
            'find_drive_session_id',
            [
                drive_api_find_drive_session_id_access_denied_response(),
            ],
        )

        with self.assertRaises(DriveApiPermanentError):
            self.drive_api.find_drive_session_id(DRIVE_DEVICE_ID1)

    def test_500(self):
        self.fake_drive_api.set_response_value('find_drive_session_id', 'Internal Server Error', 500)

        with self.assertRaises(DriveApiTemporaryError):
            self.drive_api.find_drive_session_id(DRIVE_DEVICE_ID1)

    def test_invalid_json(self):
        self.fake_drive_api.set_response_side_effect('find_drive_session_id', ['invalid json'])

        with self.assertRaises(DriveApiTemporaryError):
            self.drive_api.find_drive_session_id(DRIVE_DEVICE_ID1)

    def test_not_dict(self):
        self.fake_drive_api.set_response_side_effect('find_drive_session_id', [json.dumps(1)])

        with self.assertRaises(DriveApiTemporaryError):
            self.drive_api.find_drive_session_id(DRIVE_DEVICE_ID1)

    def test_no_session_id(self):
        self.fake_drive_api.set_response_side_effect('find_drive_session_id', [json.dumps(dict())])

        with self.assertRaises(DriveApiTemporaryError):
            self.drive_api.find_drive_session_id(DRIVE_DEVICE_ID1)
