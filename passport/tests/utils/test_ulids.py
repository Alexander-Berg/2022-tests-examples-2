# -*- coding: utf-8 -*-

import time
import unittest
import uuid

import mock
from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api.utils.errors import (
    InvalidUUIDPrefix,
    InvalidUUIDValue,
)
from passport.backend.vault.api.utils.ulid import (
    bytes_to_int,
    CrockfordBase32ULIDCodec,
    int_to_bytes,
    ULID,
)


class TestCreateULID(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        self.time_mock = TimeMock(base_value=12345678.1235)
        self.time_mock.start()

        self.urandom_mock = mock.patch('os.urandom', side_effect=lambda x: b'\x10' * (x - 1) + b'\x05')
        self.urandom_mock.start()

    def tearDown(self):
        self.urandom_mock.stop()
        self.time_mock.stop()

    def test_create_monotonic_ulids(self):
        ulid1 = ULID()
        ulid2 = ULID()
        ulid3 = ULID()
        self.assertEqual(
            [ulid1, ulid2, ulid3],
            ['000bfxr69b2081040g20810405', '000bfxr69b2081040g20810406', '000bfxr69b2081040g20810407'],
        )

    def test_create_ulid_from_string(self):
        ulid1 = ULID('01cbyhwne2b4w542mbwz70eb4e')
        self.assertEqual(ulid1, '01cbyhwne2b4w542mbwz70eb4e')
        self.assertEqual(str(ulid1), '01cbyhwne2b4w542mbwz70eb4e')
        self.assertEqual(repr(ulid1), 'ULID(\'01cbyhwne2b4w542mbwz70eb4e\')')
        self.assertEqual(ulid1.uuid, '0162fd1e-55c2-5938-520a-8be7ce072c8e')

        ulid2 = ULID('01CBYHWNE2B4W542MBWZ70EB4E')
        self.assertEqual(ulid2, '01cbyhwne2b4w542mbwz70eb4e')

    def test_create_ulid_from_ulid(self):
        ulid1 = ULID()
        ulid2 = ULID(ulid1)
        self.assertEqual(ulid1, ulid2)

    def test_parse_uuid(self):
        ulid1 = ULID('0162fd1e-55c2-5938-520a-8be7ce072c8e')
        self.assertEqual(ulid1, '01cbyhwne2b4w542mbwz70eb4e')

    def test_create_ulid_from_bytes(self):
        ulid1 = ULID(bytes_=b'\x01b\xfd\x1eU\xc2Y8R\n\x8b\xe7\xce\x07,\x8e')
        self.assertEqual(ulid1, '01cbyhwne2b4w542mbwz70eb4e')
        self.assertEqual(str(ulid1), '01cbyhwne2b4w542mbwz70eb4e')
        self.assertEqual(repr(ulid1), 'ULID(\'01cbyhwne2b4w542mbwz70eb4e\')')
        self.assertEqual(ulid1.uuid, '0162fd1e-55c2-5938-520a-8be7ce072c8e')

        with self.assertRaises(InvalidUUIDValue):
            ULID(bytes_='')

    def test_create_ulid_with_prefix(self):
        ulid1 = ULID('sec-01cbyhwne2b4w542mbwz70eb4e', prefix='sec')
        self.assertEqual(ulid1, 'sec-01cbyhwne2b4w542mbwz70eb4e')
        self.assertEqual(repr(ulid1), 'ULID(\'sec-01cbyhwne2b4w542mbwz70eb4e\', prefix=\'sec\')')

        ulid2 = ULID('01cbyhwne2b4w542mbwz70eb4e', prefix='sec')
        self.assertEqual(ulid2, 'sec-01cbyhwne2b4w542mbwz70eb4e')
        self.assertEqual(repr(ulid2), 'ULID(\'sec-01cbyhwne2b4w542mbwz70eb4e\', prefix=\'sec\')')

        ulid3 = ULID('sec-01cbyhwne2b4w542mbwz70eb4e', ignore_prefix=True)
        self.assertEqual(ulid3, ulid2)
        self.assertEqual(repr(ulid3), 'ULID(\'01cbyhwne2b4w542mbwz70eb4e\', ignore_prefix=True)')

        ulid4 = ULID('SeC-01cbyhwne2b4w542mbwz70eb4e', prefix='sec')
        self.assertEqual(ulid4, 'sec-01cbyhwne2b4w542mbwz70eb4e')
        self.assertEqual(repr(ulid4), 'ULID(\'sec-01cbyhwne2b4w542mbwz70eb4e\', prefix=\'sec\')')

    def test_invalid_ulids(self):
        invalid_ulids = [
            '',
            '12345',
            '0162fd1k-mmmm-5938-520a-8be7ce072c8e',
            '01cbyhwne2b4w542mbwz70eb4ew4',
            'sec-01cbyhwne2b4w542mbwz70eb4e',
            uuid.uuid4(),
        ]
        for s in invalid_ulids:
            with self.assertRaises(InvalidUUIDValue):
                ULID(s)

    def test_invalid_prefixed_ulids(self):
        invalid_ulids = [
            ('sec-01cbyhwne2b4w542mbwz70eb4e', 'unknown'),
        ]
        for s in invalid_ulids:
            with self.assertRaises(InvalidUUIDPrefix):
                ULID(s[0], prefix=s[1])


class TestULID(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_ulids_ok(self):
        lst = []
        for _ in range(15):
            lst.append(ULID())
            time.sleep(0.01)
        # Улиды должны быть уникальными
        self.assertEqual(len(set(lst)), len(lst))
        # Улиды должны быть возрастающими
        self.assertListEqual(lst, sorted(lst))
        # Улиды должны быть с возрастающими значениями в int
        int_lst = [int(u) for u in lst]
        self.assertListEqual(int_lst, sorted(int_lst))

    def test_ulid_as_uuid_ok(self):
        lst = []
        for _ in range(15):
            lst.append(ULID().uuid)
            time.sleep(0.01)
        self.assertEqual(len(set(lst)), len(lst))
        self.assertListEqual(lst, sorted(lst))


class TestFunctions(unittest.TestCase):
    def test_codec_errors(self):
        codec = CrockfordBase32ULIDCodec()
        with self.assertRaises(ValueError):
            codec.encode(b'\x01b\xfd\x1eU')

        with self.assertRaises(ValueError):
            codec.decode('123')

        with self.assertRaises(ValueError):
            codec._encode_timestamp(b'\x01b\xfd\x1eU')

        with self.assertRaises(ValueError):
            codec._encode_randomness(b'\x01b\xfd\x1eU')

        with self.assertRaises(ValueError):
            codec._decode_timestamp('123')

        with self.assertRaises(ValueError):
            codec._decode_randomness('123')

        with self.assertRaises(ValueError):
            codec._decode_randomness(b'\xff' * 16)

    def test_bytes_functions_errors(self):
        with self.assertRaises(TypeError):
            int_to_bytes(float(13.5), 15)

        with self.assertRaises(TypeError):
            bytes_to_int(int(100))

    def test_bytes_to_int_byteorder(self):
        value = 12345
        self.assertEqual(value, bytes_to_int(int_to_bytes(value, 26, 'little'), byteorder='little'))
        self.assertEqual(value, bytes_to_int(int_to_bytes(value, 26, 'big'), byteorder='big'))
