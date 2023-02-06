# -*- coding: utf-8 -*-
import unittest

from passport.backend.core.crypto.faker import FakeKeyStorage
from passport.backend.core.historydb.crypto import encrypt
from passport.backend.library.historydbloader.historydb.processors import (
    decrypt_processor,
    default_processor,
    int_processor,
    ip_processor,
    rfctime_processor,
    unhexify_processor,
)


class TestProcessors(unittest.TestCase):
    def setUp(self):
        self.fake_key_storage = FakeKeyStorage(1, b'1' * 24)
        self.fake_key_storage.start()

    def tearDown(self):
        self.fake_key_storage.stop()

    def test_default_processor(self):
        self.assertEqual(default_processor(None), None)
        self.assertEqual(default_processor('-'), None)
        self.assertEqual(default_processor('a'), 'a')
        self.assertEqual(default_processor(1), 1)

    def test_int_processor(self):
        self.assertEqual(int_processor(None), None)
        self.assertEqual(int_processor('-'), None)
        self.assertEqual(int_processor('1'), 1)
        self.assertEqual(int_processor('b'), None)

    def test_unhexify_processor(self):
        self.assertEqual(unhexify_processor(None), None)
        self.assertEqual(unhexify_processor('-'), None)
        self.assertEqual(unhexify_processor('ff'), 255)
        self.assertEqual(unhexify_processor('A'), 10)
        self.assertEqual(unhexify_processor('G'), None)

    def test_ip_processor(self):
        self.assertEqual(ip_processor(None), None)
        self.assertEqual(ip_processor('-'), None)
        self.assertEqual(ip_processor('::ffff:127.0.0.1'), '127.0.0.1')
        self.assertEqual(ip_processor('2001:0db8:11a3:09d7:1f34:8a2e:07a0:765d'), '2001:0db8:11a3:09d7:1f34:8a2e:07a0:765d')
        self.assertEqual(ip_processor('...'), '...')

    def test_rfctime_processor(self):
        self.assertEqual(rfctime_processor(None), None)
        self.assertEqual(rfctime_processor('-'), None)
        self.assertEqual(rfctime_processor('1970-01-01T04:00:00.000000+04'), 0)
        self.assertEqual(rfctime_processor('1970-01-01T05:01:30.000000+04'), 3690)
        self.assertEqual(rfctime_processor('1970-01-01T05:01:30.000sdf'), None)
        self.assertEqual(rfctime_processor('1970-01-01T05:01:30.000000+123'), None)

    def test_decrypt_processor(self):
        encrypted = encrypt(u'значение')
        self.assertEqual(decrypt_processor(encrypted), u'значение'.encode('utf-8'))
        self.assertEqual(decrypt_processor(b'abracadabra'), None)
        bad_utf8_value = u'значение'.encode('utf-8')[:-1] + b'tail'
        encrypted = encrypt(bad_utf8_value)
        self.assertEqual(decrypt_processor(encrypted), bad_utf8_value)
