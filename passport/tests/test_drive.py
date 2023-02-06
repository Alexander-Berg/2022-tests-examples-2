# -*- coding: utf-8 -*-

from nose_parameterized import parameterized
from passport.backend.core.models.drive import DriveSession
from passport.backend.core.test.consts import (
    TEST_UID1,
    TEST_UID2,
)
from passport.backend.core.test.test_utils import PassportTestCase


DEVICE_ID1 = 'device_id1'
DEVICE_ID2 = 'device_id2'
DRIVE_SESSION_ID1 = 'drive_session_id1'
DRIVE_SESSION_ID2 = 'drive_session_id2'


class TestDriveSession(PassportTestCase):
    def test_parse(self):
        session = DriveSession()
        session.parse(
            dict(
                drive_device_id=DEVICE_ID1,
                drive_session_id=DRIVE_SESSION_ID1,
                uid=TEST_UID1,
            ),
        )
        self.assertEqual(session.drive_device_id, DEVICE_ID1)
        self.assertEqual(session.drive_session_id, DRIVE_SESSION_ID1)
        self.assertEqual(session.uid, TEST_UID1)

    def test_is_same(self):
        sessions = list()
        for _ in range(2):
            sessions.append(
                DriveSession(
                    drive_device_id=DEVICE_ID1,
                    drive_session_id=DRIVE_SESSION_ID1,
                    uid=TEST_UID1,
                ),
            )

        self.assertTrue(
            sessions[0].is_same(sessions[1]),
        )

    @parameterized.expand(
        [
            ('drive_device_id', DEVICE_ID2),
            ('drive_session_id', DRIVE_SESSION_ID2),
            ('uid', TEST_UID2),
        ],
    )
    def test_not_is_same(self, attr, value):
        sessions = list()
        for _ in range(2):
            sessions.append(
                DriveSession(
                    drive_device_id=DEVICE_ID1,
                    drive_session_id=DRIVE_SESSION_ID1,
                    uid=TEST_UID1,
                ),
            )
        setattr(sessions[0], attr, value)
        self.assertFalse(
            sessions[0].is_same(sessions[1]),
        )

    def test_not_is_same_other_type(self):
        session = DriveSession(
            drive_device_id=DEVICE_ID1,
            drive_session_id=DRIVE_SESSION_ID1,
            uid=TEST_UID1,
        )
        self.assertFalse(
            session.is_same(DRIVE_SESSION_ID1),
        )

    def test_to_bytes(self):
        session = DriveSession(
            drive_device_id=DEVICE_ID1,
            drive_session_id=DRIVE_SESSION_ID1,
            uid=TEST_UID1,
        )
        self.assertEqual(
            session.to_bytes(),
            DEVICE_ID1.encode() + DRIVE_SESSION_ID1.encode() + str(TEST_UID1).encode(),
        )
