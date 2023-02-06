# -*- coding: utf-8 -*-

import unittest

import mock
from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.cookies import lrandoms
from passport.backend.core.cookies.cookie_l import (
    CookieL,
    CookieLPackError,
    CookieLUnpackError,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.utils.string import smart_text


TEST_L_RANDOM = {
    'body': '2dL9OKKqcKHbljKQI70PMaaB7R08VnEn3jo5iAI62gPeCQ5zgI5fjjczFOMRvvaQ',
    'created_timestamp': 1376769602,
    'id': '1002323',
}


@with_settings(
    BLACKBOX_URL='http://localhost/',
)
class TestCookieL(unittest.TestCase):
    def setUp(self):
        self._current_lrandom = mock.Mock()
        self._get_lrandom = mock.Mock()

        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))

        self.patches = [
            mock.patch.object(lrandoms._LRandomsManager,
                              'current_lrandom',
                              self._current_lrandom),
            mock.patch.object(lrandoms._LRandomsManager,
                              'get_lrandom',
                              self._get_lrandom),
            self.fake_tvm_credentials_manager,
        ]
        for patch in self.patches:
            patch.start()

        self.cookie_l = CookieL(lrandoms._LRandomsManager())
        self._current_lrandom.return_value = TEST_L_RANDOM
        self._get_lrandom.return_value = TEST_L_RANDOM

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        del self.patches
        del self._current_lrandom
        del self._get_lrandom
        del self.fake_tvm_credentials_manager

    def test_eq_simple_unpack(self):
        packed = self.cookie_l.pack(7654321, 'username')
        unpacked = self.cookie_l.unpack(packed)
        eq_(
            unpacked,
            {
                'uid': 7654321,
                'login': 'username',
            },
        )

    def test_eq_simple_unpack_unicode_login(self):
        bytes_packed = self.cookie_l.pack(7654321, u'плохой-логин')
        text_packed = smart_text(bytes_packed)
        for packed in [bytes_packed, text_packed]:
            unpacked = self.cookie_l.unpack(packed)
            eq_(
                unpacked,
                {
                    'uid': 7654321,
                    'login': u'плохой-логин',
                },
            )

    def test_known_cases(self):
        cases = [
            (
                'UVU9WnZ9f0hbeHlVWlh9YngGCGJ6WVl1XjNZXGFeNwZJHA0FDTszX1kBMRImKV4SUiRAFQ8YDRsrKmBjREJXYA==.1376939944.1002323.216145.e46392a735b0d198614ac9cb321d79b4',
                {'uid': 1, 'login': u'username-124'},
            ),
            (
                'AgN+Xn56eEFTe3hSXFp7YXkHAGV8VFdxBjVFSzMcKw9eDy9aAi8oGEASZFQ6J0AcFyJaXloMDxc2Nn9nEU9WZg==.1376939981.1002323.273612.eec41a4a89676bae03d50e35a27896b0',
                {'uid': 1130000000000005, 'login': 'username@okna.ru'},
            ),
            (
                'AAN/SHZ8ekBQe3hSXFp7YXkHAGB9VFhwTmNZ6Oi+/76Out91uMCZiOLWgNWT6+XKSZi1t+4TUhs1KnVgERgRJw==.1376939998.1002323.264175.e11678d6c6178f606d35324a78deea08',
                {'uid': 1130000000000005, 'login': u'окна@собака.рф'},
            ),
        ]

        # Распаковываем cookie L полученные из Perl
        for packed, unpacked in cases:
            eq_(self.cookie_l.unpack(packed), unpacked)

        # Проверяем, что эти же данные пакуются-распакуются
        for _, unpacked in cases:
            packed = self.cookie_l.pack(**unpacked)
            eq_(self.cookie_l.unpack(packed), unpacked)

    @raises(CookieLUnpackError)
    def test_unpack_bad_fields_count(self):
        packed = 'abc.cde'
        self.cookie_l.unpack(packed)

    @raises(CookieLUnpackError)
    def test_unpack_signature_mismatch(self):
        packed = self.cookie_l.pack(7654321, 'username')
        packed = packed[:-1] + 'x'
        self.cookie_l.unpack(packed)

    @raises(CookieLUnpackError)
    def test_unpack_bad_uid_value(self):
        packed = 'UVAqDHt5eUJRfHpRWFp9aHgFAyN9UFF3RDBZSW8cdVhVXgVAGihxWl0AOQs2MFkMAC9bFxlYW0I/PTs3EhMKJg==.1376941096.1002323.76558.3233cfa606cec5b84083e0fac875a27f'
        self.cookie_l.unpack(packed)

    @raises(CookieLUnpackError)
    def test_unpack_unknown_lrandom(self):
        packed = 'B1cgDX9zeENRenpRXlp+ZHoGBGh8U1lzQzhGADkYKRgKDABHBi8sR0gfIREtuJPj/nxTEgEOVxc8fywgBA4JPQ==.1376941436.1002323.4418.8761c439929bd529b8beb0c82f4a3e6b'
        self.cookie_l.unpack(packed)

    @raises(CookieLPackError)
    def test_pack_lrandoms_not_found(self):
        self._current_lrandom.return_value = None
        self.cookie_l.pack(123, 'login')

    @raises(CookieLUnpackError)
    def test_unpack_lrandom_not_found(self):
        packed = 'AgN+Xn56eEFTe3hSXFp7YXkHAGV8VFdxBjVFSzMcKw9eDy9aAi8oGEASZFQ6J0AcFyJaXloMDxc2Nn9nEU9WZg==.1376939981.1002323.273612.eec41a4a89676bae03d50e35a27896b0'
        self._get_lrandom.return_value = None
        self.cookie_l.unpack(packed)


@with_settings(
    BLACKBOX_URL='http://localhost/',
)
class TestCookieLWithVersion3Algorythm(unittest.TestCase):
    def setUp(self):
        self._current_lrandom = mock.Mock()
        self._get_lrandom = mock.Mock()

        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))

        self.lrandoms_map = {
            '1': {
                'body': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
                'created_timestamp': 1376769602,
                'id': '1',
            },
            '2': {
                'body': 'bbb',
                'created_timestamp': 1376769602,
                'id': '2',
            },
            '1002323': TEST_L_RANDOM,
        }

        self.patches = [
            mock.patch.object(
                lrandoms._LRandomsManager,
                'current_lrandom',
                self._current_lrandom,
            ),
            mock.patch.object(
                lrandoms._LRandomsManager,
                'get_lrandom',
                self._get_lrandom,
            ),
            self.fake_tvm_credentials_manager,
        ]
        for patch in self.patches:
            patch.start()

        self._current_lrandom.return_value = TEST_L_RANDOM
        self._get_lrandom.side_effect = lambda key: self.lrandoms_map[key]

        self.cookie_l = CookieL(lrandoms._LRandomsManager())

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        del self.patches
        del self._current_lrandom
        del self._get_lrandom
        del self.fake_tvm_credentials_manager

    def test_unpack_version_2(self):
        """
        Проверим распаковку кук 2ей версии, по кукам,
        созданным в перле. Убедимся, что ничего не сломали
        """
        eq_(
            self.cookie_l.unpack(
                'UlgKAllTVFBQUFBQUFBQUFBQWVZZWFdYDgoNUwcLBBYXUg4HAlAbBQVYCgYYAA8FBBlMDQ4GCA8MDVQVEQkZGw==.1400761800.1.221453.39035f3f91da75c8a56b4c1d0165970c',
            ),
            {
                'uid': 111111111,
                'login': 'yandex-login',
            },
        )

    def test_known_cases(self):
        """
        Проверим распаковку кук 3ей версии, по кукам,
        созданным в перле
        """
        for cookie, uid, login in (
            (
                'UVhRK1NTU1NTU1NTU1ZTUVRZWFdVWVRSEhQRBBNMERQRBBNMBBkVEwBMFwQTGEwXBBMYTA0ODwZMGAAPBQQZTA0OBggP.1400761964.1.391225.bec7457ed3a1f3ab51746c9fe8004dab',
                222222222,
                'super-puper-extra-very-very-long-yandex-login',
            ),
            (
                'UQZRA1BQUlFRUVFRUVFRUVFRUVBYVlRTEQUFIQ4KDwBPExQ=.1400763784.1.397116.6eef25a754eb752dd8de4c2cabdba1ef',
                1130000000000001,
                u'pdd@okna.ru',
            ),
            (
                'UQZRCVBQUlFRUVFRUVFRUVFRUVNXUFdSEQUFIbHfsdux3LHRT7DhsOU=.1400763929.1.361033.3f9a2f2551a8da2a2c7ce7e0cf1d4b33',
                1130000000000002,
                u'pdd@окна.рф',
            ),
        ):
            eq_(
                self.cookie_l.unpack(cookie),
                {
                    'uid': uid,
                    'login': login,
                },
            )

    def test_known_cases_short_key(self):
        """
        Проверим распаковку кук 3ей версии, по кукам,
        созданным в перле с коротким ключем lrandom
        """
        eq_(
            self.cookie_l.unpack(
                'UltSKFBQUFBQUFBQUFpRWltUW1ZXVVNbERcSBxBPEhcSBxBPBxoWEANPFAcQG08UBxAbTw4NDAVPGwMMBgcaTw4NBQsM.1400762446.2.338823.f2e243723a1e610e4f3291e44447bbe3',
            ),
            {
                'uid': 222222222,
                'login': 'super-puper-extra-very-very-long-yandex-login',
            },
        )

    def test_eq_simple_unpack(self):
        """
        Удостоверимся, что можем запаковать и распаковать новым алгоритмом
        """
        for uid, login in (
            (7654321, 'username'),
            (1130000000000001, u'pdd-very-loooooong-login@окна.рф'),
            (1130000000000001, u'robbitter-1778770790@закодированный.домен'),
            (1130000000000001, u'mega-long-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'),
        ):
            packed = self.cookie_l.pack(uid, login)
            unpacked = self.cookie_l.unpack(packed)
            eq_(
                unpacked,
                {
                    'uid': uid,
                    'login': login,
                },
            )

    @raises(CookieLUnpackError)
    def test_bad_version(self):
        self.cookie_l.unpack(
            'UQZRCVBQUlFRUVFRUVFRUVFRUVNXUFdSEQUFIbHfsdux3LHRT7DhsOU=.1400763929.1.a61033.3f9a2f2551a8da2a2c7ce7e0cf1d4b33',
        )
