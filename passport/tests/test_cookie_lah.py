# -*- coding: utf-8 -*-

import datetime

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from nose_parameterized import parameterized
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_check_sign_response,
    blackbox_sign_response,
    FakeBlackbox,
)
from passport.backend.core.cookies import lrandoms
from passport.backend.core.cookies.cookie_lah import (
    CookieLAH,
    CookieLAHPackError,
    CookieLAHUnpackError,
    try_parse_cookie_lah,
)
from passport.backend.core.cookies.cookie_lah.container import AuthHistoryContainer
from passport.backend.core.cookies.cookie_lah.wrapper.base import string_xor
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.test.test_utils.utils import PassportTestCase
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.utils.string import smart_bytes
import six


TEST_UID = 123
TEST_LOGIN = 'some-login'
TEST_TS = 1234567
TEST_METHOD = 1
TEST_OTHER_UID = 246
TEST_OTHER_TS = 1234568
TEST_OTHER_METHOD = 42
TEST_UNKNOWN_METHOD = 0
TEST_L_RANDOM = {
    'body': '2dL9OKKqcKHbljKQI70PMaaB7R08VnEn3jo5iAI62gPeCQ5zgI5fjjczFOMRvvaQ',
    'created_timestamp': 1376769602,
    'id': '1002323',
}
TEST_TTL1 = datetime.timedelta(hours=1)


@with_settings(
    BLACKBOX_URL='http://localhost/',
    COOKIE_LAH_MAX_SIZE=3,
    LAH_SIGN_VERSION=1,
)
class TestCookieLAHWrapperV1(PassportTestCase):
    def setUp(self):
        self._current_lrandom = mock.Mock()
        self._get_lrandom = mock.Mock()
        self._load = mock.Mock(return_value=None)

        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))

        LazyLoader.flush('LRandomsManager')
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
            mock.patch.object(
                lrandoms._LRandomsManager,
                'load',
                self._load,
            ),
            self.fake_tvm_credentials_manager,
        ]
        for patch in self.patches:
            patch.start()

        self._current_lrandom.return_value = TEST_L_RANDOM
        self._get_lrandom.return_value = TEST_L_RANDOM

        self.cookie_lah = CookieLAH()
        self.local_auth_history_container = AuthHistoryContainer()
        self.local_auth_history_container.add(TEST_UID, TEST_TS, TEST_METHOD)

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        del self.patches
        del self._current_lrandom
        del self._get_lrandom
        del self._load
        del self.fake_tvm_credentials_manager,

    def test_string_xor(self):
        for src, key, dst in (
            (b'\x00\x00\x00', b'\x01\x01\x01', b'\x01\x01\x01'),
            (b'\x00\x00\x00', b'\x01', b'\x01\x01\x01'),
            (b'\x10\x10\x10', b'\x01', b'\x11\x11\x11'),
            (b'\x10\x10', b'\x01\x01\x01', b'\x11\x11'),
            (smart_bytes('привет, мир'), b'secret_key', b'\xa3\xda\xb2\xf2\xb5\xcc\x8f\xd9\xb5\xcc\xa2\xe7OR\xb5\xc8\x8f\xd3\xb4\xf9'),
        ):
            eq_(
                string_xor(src, key),
                dst,
            )
            eq_(
                string_xor(dst, key),
                src,
            )

    def test_eq_simple_unpack(self):
        packed = self.cookie_lah.pack(self.local_auth_history_container)
        unpacked = self.cookie_lah.unpack(packed)
        eq_(
            unpacked,
            self.local_auth_history_container,
        )

    def test_pack_empty_container(self):
        packed = self.cookie_lah.pack(AuthHistoryContainer())
        eq_(packed, '')

    @parameterized.expand([
        ('a.b.c.d.e',),
        ('abc.de',),
        ('a.b.c.100.e',),
    ])
    def test_unpack_bad_data(self, packed):
        with self.assertRaises(CookieLAHUnpackError):
            self.cookie_lah.unpack(packed)

    def test_unpack_signature_mismatch(self):
        packed = self.cookie_lah.pack(self.local_auth_history_container)
        packed = packed[:-1] + 'x'
        with assert_raises(CookieLAHUnpackError):
            self.cookie_lah.unpack(packed)

    @raises(CookieLAHPackError)
    def test_pack_no_lrandom(self):
        self._current_lrandom.return_value = None
        self.cookie_lah.pack(self.local_auth_history_container)

    def test_unpack_no_lrandom(self):
        packed = self.cookie_lah.pack(self.local_auth_history_container)
        self._get_lrandom.return_value = None
        with assert_raises(CookieLAHUnpackError):
            self.cookie_lah.unpack(packed)

    def test_try_parse_ok(self):
        packed = self.cookie_lah.pack(self.local_auth_history_container)
        container = try_parse_cookie_lah(packed)
        eq_(
            container,
            self.local_auth_history_container,
        )


@with_settings(
    BLACKBOX_URL='http://localhost/',
    COOKIE_LAH_MAX_SIZE=3,
    LAH_SIGN_TTL=TEST_TTL1,
)
class TestCookieLAHWrapperV2(PassportTestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'blackbox',
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )

        self.fake_blackbox = FakeBlackbox()
        self.fake_blackbox.set_response_side_effect('sign', [blackbox_sign_response()])
        self.fake_blackbox.set_response_side_effect('check_sign', [blackbox_check_sign_response()])

        self.__patches = [
            self.fake_tvm_credentials_manager,
            self.fake_blackbox,
        ]
        for patch in self.__patches:
            patch.start()

        self.cookie_lah = CookieLAH()
        self.local_auth_history_container = AuthHistoryContainer()
        self.local_auth_history_container.add(TEST_UID, TEST_TS, TEST_METHOD)

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()

    def get_signed_value(self, lah_container):
        self.cookie_lah.pack(lah_container)
        return self.fake_blackbox.requests[0].get_query_params()['value'][0]

    def test_pack(self):
        self.fake_blackbox.set_response_side_effect('sign', [blackbox_sign_response(signed_value='signed_lah')])

        packed = self.cookie_lah.pack(self.local_auth_history_container)

        assert packed == '2:signed_lah'

    def test_unpack(self):
        self.fake_blackbox.set_response_side_effect(
            'check_sign',
            [
                blackbox_check_sign_response(value=self.get_signed_value(self.local_auth_history_container)),
            ],
        )

        unpacked = self.cookie_lah.unpack('2:signed_lah')

        assert unpacked == self.local_auth_history_container

    def test_pack_empty_container(self):
        packed = self.cookie_lah.pack(AuthHistoryContainer())
        eq_(packed, '')

    def test_unpack_empty_cookie(self):
        unpacked = self.cookie_lah.unpack('')
        eq_(unpacked, AuthHistoryContainer())

    def test_try_parse_failure(self):
        container = try_parse_cookie_lah('foo')
        eq_(
            container,
            AuthHistoryContainer(),
        )

    @parameterized.expand([
        ('3:x',),
        ('1:x',),
        ('2',),
    ])
    def test_unpack_bad_data(self, packed):
        with self.assertRaises(CookieLAHUnpackError):
            self.cookie_lah.unpack(packed)

    @parameterized.expand([
        ('INVALID',),
        ('EXPIRED',),
        ('NO_KEY',),
    ])
    def test_unpack_invalid_signature(self, status):
        self.fake_blackbox.set_response_side_effect('check_sign', [blackbox_check_sign_response(status=status)])

        with self.assertRaises(CookieLAHUnpackError):
            self.cookie_lah.unpack('2:signed_lah')

        assert len(self.fake_blackbox.requests) == 1

    def test_try_parse_ok(self):
        self.fake_blackbox.set_response_side_effect(
            'check_sign',
            [
                blackbox_check_sign_response(value=self.get_signed_value(self.local_auth_history_container)),
            ],
        )

        container = try_parse_cookie_lah('2:signed_lah')

        assert container == self.local_auth_history_container

    def test_pack_blackbox_request(self):
        self.cookie_lah.pack(self.local_auth_history_container)

        self.fake_blackbox.requests[0].assert_query_equals(dict(
            format='json',
            method='sign',
            sign_space='lah',
            ttl=str(int(TEST_TTL1.total_seconds())),
            value=mock.ANY,
        ))

    def test_unpack_blackbox_request(self):
        self.cookie_lah.unpack('2:signed_lah')

        self.fake_blackbox.requests[0].assert_query_equals(dict(
            format='json',
            method='check_sign',
            sign_space='lah',
            signed_value='signed_lah',
        ))


@with_settings(
    COOKIE_LAH_MAX_SIZE=3,
)
class TestCookieLAHContainer(PassportTestCase):
    def setUp(self):
        self.local_auth_history_container = AuthHistoryContainer()
        self.local_auth_history_container.add(TEST_UID, TEST_TS, TEST_METHOD)

    def test_repr(self):
        if six.PY2:
            dict_repr = '{\'input_login\': u\'\', \'version\': 1, \'method\': 1, \'timestamp\': 1234567, \'uid\': 123}'
        else:
            dict_repr = '{\'version\': 1, \'uid\': 123, \'timestamp\': 1234567, \'method\': 1, \'input_login\': \'\'}'
        eq_(
            repr(self.local_auth_history_container),
            '<AuthHistoryContainer: [<AuthHistoryItem: %s>]>' % dict_repr,
        )

    def test_nonzero(self):
        ok_(self.local_auth_history_container)
        ok_(not AuthHistoryContainer())

    def test_add_new(self):
        self.local_auth_history_container.add(TEST_OTHER_UID, TEST_OTHER_TS, TEST_OTHER_METHOD)
        eq_(
            len(list(self.local_auth_history_container)),
            2,
        )
        eq_(
            len(self.local_auth_history_container),
            2,
        )
        items = self.local_auth_history_container
        eq_(items[0].uid, TEST_UID)
        eq_(items[1].uid, TEST_OTHER_UID)
        ok_(not items[0].input_login)

    def test_add_new_as_string(self):
        self.local_auth_history_container.add(str(TEST_OTHER_UID), str(TEST_OTHER_TS), TEST_OTHER_METHOD)
        eq_(
            len(list(self.local_auth_history_container)),
            2,
        )
        eq_(
            len(self.local_auth_history_container),
            2,
        )
        items = self.local_auth_history_container
        eq_(items[0].uid, TEST_UID)
        eq_(items[1].uid, TEST_OTHER_UID)
        ok_(not items[0].input_login)

    def test_add_new_with_unknown_method(self):
        self.local_auth_history_container.add(TEST_OTHER_UID, TEST_OTHER_TS, TEST_UNKNOWN_METHOD)
        eq_(
            len(list(self.local_auth_history_container)),
            2,
        )
        eq_(
            len(self.local_auth_history_container),
            2,
        )
        items = self.local_auth_history_container
        eq_(items[0].uid, TEST_UID)
        eq_(items[1].uid, TEST_OTHER_UID)
        eq_(items[1].method, TEST_UNKNOWN_METHOD)
        ok_(not items[0].input_login)

    def test_add_new_with_input_login(self):
        self.local_auth_history_container.add(TEST_OTHER_UID, TEST_OTHER_TS, TEST_METHOD, TEST_LOGIN)
        eq_(
            len(self.local_auth_history_container),
            2,
        )
        items = self.local_auth_history_container
        eq_(items[0].uid, TEST_UID)
        eq_(items[1].uid, TEST_OTHER_UID)
        eq_(items[1].method, TEST_METHOD)
        eq_(items[1].input_login, TEST_LOGIN)

    def test_update_existing(self):
        self.local_auth_history_container.add(TEST_UID, TEST_OTHER_TS, TEST_OTHER_METHOD)
        eq_(
            len(self.local_auth_history_container),
            1,
        )
        items = self.local_auth_history_container
        eq_(items[0].uid, TEST_UID)
        eq_(items[0].timestamp, TEST_OTHER_TS)
        eq_(items[0].method, TEST_OTHER_METHOD)
        ok_(not items[0].input_login)

    def test_update_existing_with_unknown_method(self):
        self.local_auth_history_container.add(TEST_UID, TEST_OTHER_TS, TEST_UNKNOWN_METHOD)
        eq_(
            len(self.local_auth_history_container),
            1,
        )
        items = self.local_auth_history_container
        eq_(items[0].uid, TEST_UID)
        eq_(items[0].timestamp, TEST_OTHER_TS)
        eq_(items[0].method, TEST_METHOD)
        ok_(not items[0].input_login)

    def test_update_existing_with_input_login(self):
        self.local_auth_history_container.add(TEST_UID, TEST_OTHER_TS, TEST_METHOD, TEST_LOGIN)
        eq_(
            len(self.local_auth_history_container),
            1,
        )
        items = self.local_auth_history_container
        eq_(items[0].uid, TEST_UID)
        eq_(items[0].timestamp, TEST_OTHER_TS)
        eq_(items[0].method, TEST_METHOD)
        eq_(items[0].input_login, TEST_LOGIN)

    def test_remove(self):
        self.local_auth_history_container.add(TEST_OTHER_UID, TEST_OTHER_TS, TEST_OTHER_METHOD)
        self.local_auth_history_container.remove(TEST_UID)
        eq_(
            len(self.local_auth_history_container),
            1,
        )
        items = self.local_auth_history_container
        eq_(items[0].uid, TEST_OTHER_UID)
        eq_(items[0].timestamp, TEST_OTHER_TS)
        eq_(items[0].method, TEST_OTHER_METHOD)

    def test_remove_nonexistent(self):
        self.local_auth_history_container.remove(TEST_OTHER_UID)
        eq_(
            len(self.local_auth_history_container),
            1,
        )
        items = self.local_auth_history_container
        eq_(items[0].uid, TEST_UID)
        eq_(items[0].timestamp, TEST_TS)
        eq_(items[0].method, TEST_METHOD)

    def test_overflow(self):
        for i in range(10):
            self.local_auth_history_container.add(100500 + i, TEST_TS, TEST_METHOD)
        eq_(
            len(self.local_auth_history_container),
            3,
        )
        items = self.local_auth_history_container
        eq_(items[0].uid, 100507)
        eq_(items[1].uid, 100508)
        eq_(items[2].uid, 100509)
