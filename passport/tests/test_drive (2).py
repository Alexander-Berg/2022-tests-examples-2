# -*- coding: utf-8 -*-

from passport.backend.core.crypto.signing import (
    get_signing_registry,
    SigningRegistry,
)
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.models.drive import DriveSession
from passport.backend.core.test.consts import (
    TEST_UID1,
    TEST_UID2,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.core.ydb.exceptions import YdbTemporaryError
from passport.backend.core.ydb.faker.ydb import FakeYdb
from passport.backend.core.ydb.faker.ydb_keyvalue import FakeYdbKeyValue
from passport.backend.core.ydb.processors.drive import (
    find_drive_session,
    save_drive_session,
)
from passport.backend.core.ydb.ydb import get_ydb_drive_session
import passport.backend.core.ydb_client as ydb


DRIVE_DEVICE_ID1 = 'drive_device_id1'
DRIVE_DEVICE_ID2 = 'drive_device_id2'
DRIVE_SANDBOX_DEVICE_ID1 = 'sandbox_device_id1'
DRIVE_SANDBOX_DEVICE_ID2 = 'sandbox_device_id2'
DRIVE_SESSION_ID1 = 'drive_session_id1'
DRIVE_SESSION_ID2 = 'drive_session_id2'
SECRET1 = b'1' * 32
SECRET2 = b'2' * 32


class BaseTestCase(PassportTestCase):
    def setup_signing_registry(self):
        signing_registry_config = {
            'default_version_id': b'1',
            'versions': [
                {
                    'id':   b'1',
                    'algorithm': 'SHA256',
                    'salt_length': 32,
                    'secret': SECRET1,
                },
            ],
        }
        signing_registry = SigningRegistry()
        signing_registry.add_from_dict(signing_registry_config)
        LazyLoader.register('SigningRegistry', lambda: signing_registry)

    def assert_database_drive_session_equal(self, session):
        sessions = get_ydb_drive_session().get(dict(drive_device_id=session.drive_device_id))
        sessions = list(sessions)
        self.assertEqual(len(sessions), 1)
        self.assertEqual(
            set(sessions[0].keys()),
            {
                'sandbox_device_id',
                'drive_session_id',
                'signature',
                'uid',
            },
        )
        self.assertEqual(sessions[0]['sandbox_device_id'], session.sandbox_device_id)
        self.assertEqual(sessions[0]['drive_session_id'], session.drive_session_id)
        self.assertEqual(sessions[0]['uid'], session.uid)

    def assert_drive_session_not_saved(self, device_id=DRIVE_DEVICE_ID1):
        sessions = get_ydb_drive_session().get(dict(drive_device_id=device_id))
        sessions = list(sessions)
        self.assertEqual(len(sessions), 0)

    def build_drive_session(
        self,
        drive_device_id=DRIVE_DEVICE_ID1,
        sandbox_device_id=DRIVE_SANDBOX_DEVICE_ID1,
        drive_session_id=DRIVE_SESSION_ID1,
        uid=TEST_UID1,
    ):
        return DriveSession(
            drive_device_id=drive_device_id,
            sandbox_device_id=sandbox_device_id,
            drive_session_id=drive_session_id,
            uid=uid,
        )


@with_settings_hosts(
    YDB_DRIVE_DATABASE='drive',
    YDB_DRIVE_ENABLED=True,
)
class TestSaveDriveSession(BaseTestCase):
    def setUp(self):
        super(TestSaveDriveSession, self).setUp()
        self.fake_ydb = FakeYdb()
        self.fake_ydb_key_value = FakeYdbKeyValue()
        self.fake_ydb.set_execute_return_value([])

        self.__patches = [
            self.fake_ydb,
            self.fake_ydb_key_value,
        ]
        for patch in self.__patches:
            patch.start()

        self.setup_signing_registry()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        del self.__patches
        del self.fake_ydb
        del self.fake_ydb_key_value
        super(TestSaveDriveSession, self).tearDown()

    def test_no_session(self):
        self.assert_drive_session_not_saved()

        session = self.build_drive_session()
        save_drive_session(session)

        self.assert_database_drive_session_equal(session)

    def test_session_exists(self):
        old_session = self.build_drive_session(
            drive_session_id=DRIVE_SESSION_ID1,
            uid=TEST_UID1,
        )
        new_session = self.build_drive_session(
            drive_session_id=DRIVE_SESSION_ID2,
            uid=TEST_UID2,
        )
        save_drive_session(old_session)
        save_drive_session(new_session)

        self.assert_database_drive_session_equal(new_session)

    def test_update_sandbox_device_id(self):
        session = self.build_drive_session()
        save_drive_session(session)
        session.sandbox_device_id = DRIVE_SANDBOX_DEVICE_ID2
        save_drive_session(session)

        self.assert_database_drive_session_equal(session)

    def test_timeout(self):
        self.fake_ydb_key_value.set_response_side_effect([ydb.Timeout('timeout')])

        session = self.build_drive_session()
        with self.assertRaises(YdbTemporaryError):
            save_drive_session(session)


@with_settings_hosts(
    YDB_DRIVE_DATABASE='drive',
    YDB_DRIVE_ENABLED=True,
)
class TestFindDriveSession(BaseTestCase):
    def setUp(self):
        super(TestFindDriveSession, self).setUp()
        self.fake_ydb = FakeYdb()
        self.fake_ydb_key_value = FakeYdbKeyValue()
        self.fake_ydb.set_execute_return_value([])

        self.__patches = [
            self.fake_ydb,
            self.fake_ydb_key_value,
        ]
        for patch in self.__patches:
            patch.start()

        self.setup_signing_registry()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        del self.__patches
        del self.fake_ydb
        del self.fake_ydb_key_value
        super(TestFindDriveSession, self).tearDown()

    def test_no_session(self):
        save_drive_session(
            self.build_drive_session(
                drive_device_id=DRIVE_DEVICE_ID2,
            ),
        )

        session = find_drive_session(DRIVE_DEVICE_ID1)

        self.assertIsNone(session)

    def test_session_exists(self):
        old_session = self.build_drive_session(
            drive_device_id=DRIVE_DEVICE_ID1,
        )
        save_drive_session(old_session)

        new_session = find_drive_session(DRIVE_DEVICE_ID1)

        self.assertEqual(new_session, old_session)

    def test_invalid_signature(self):
        save_drive_session(
            self.build_drive_session(drive_device_id=DRIVE_DEVICE_ID1),
        )

        signing_registry_config = {
            'versions': [
                {
                    'id':   b'1',
                    'algorithm': 'SHA256',
                    'salt_length': 32,
                    'secret': SECRET2,
                },
            ],
        }
        get_signing_registry().add_from_dict(signing_registry_config)

        session = find_drive_session(DRIVE_DEVICE_ID1)
        self.assertIsNone(session)
