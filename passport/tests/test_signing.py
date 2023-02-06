# -*- coding: utf-8 -*-

from base64 import (
    b64decode,
    standard_b64encode,
)
import json

import mock
from nose_parameterized import parameterized
from passport.backend.core.crypto.signing import (
    ByteSequence,
    ConfigurationFailedSigningError,
    DefaultVersionNotFoundSigningError,
    get_signing_registry,
    is_correct_signature,
    pack,
    RotatingSigningRegistry,
    sign,
    SigningRegistry,
    simple_is_correct_signature,
    simple_sign,
    unpack,
    Version,
    VersionNotFoundSigningError,
)
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
import six


EPOCH_LENGTH1 = 5
EPOCH_LENGTH2 = 10
SECRET1 = b'1' * 32
SECRET2 = b'2' * 32
SECRET3 = b''.join(map(six.int2byte, range(256)))
DATA1 = b'foofoofoo'
DATA2 = b'barbarbar'
DATA3 = b''.join(map(six.int2byte, range(256)))
SIGNING_VERSION1 = b'1'
SIGNING_VERSION2 = b'2'
SIGNING_VERSION3 = b'2'


class SignTestMixin(object):
    def test_sign_sample(self):
        signature = sign(DATA1, SECRET1, self.algorithm)
        self.assertEqual(signature, self.sample)

    def test_sign_idempotence(self):
        signature1 = sign(DATA1, SECRET1, self.algorithm)
        signature2 = sign(DATA1, SECRET1, self.algorithm)
        self.assertEqual(signature1, signature2)

    def test_sign_data_matters(self):
        signature1 = sign(DATA1, SECRET1, self.algorithm)
        signature2 = sign(DATA2, SECRET1, self.algorithm)
        self.assertNotEqual(signature1, signature2)

    def test_sign_secret_matters(self):
        signature1 = sign(DATA1, SECRET1, self.algorithm)
        signature2 = sign(DATA1, SECRET2, self.algorithm)
        self.assertNotEqual(signature1, signature2)

    def test_check_correct_signature(self):
        signature = sign(DATA1, SECRET1, self.algorithm)
        correct = is_correct_signature(signature, DATA1, SECRET1, self.algorithm)
        self.assertTrue(correct)

    def test_check_invalid_signature(self):
        signature = sign(DATA2, SECRET1, self.algorithm)
        correct = is_correct_signature(signature, DATA1, SECRET1, self.algorithm)
        self.assertFalse(correct)

    def test_sign_all_bytes(self):
        signature = sign(DATA3, SECRET3, self.algorithm)
        correct = is_correct_signature(signature, DATA3, SECRET3, self.algorithm)
        assert correct


@with_settings_hosts()
class TestSign(PassportTestCase):
    def test_sign_unknown_algorithm(self):
        with self.assertRaises(NotImplementedError):
            sign(DATA1, SECRET1, 'unknown')

    def test_check_unknown_algorithm(self):
        with self.assertRaises(NotImplementedError):
            is_correct_signature(DATA1, DATA1, SECRET1, 'unknown')

    def test_sign_unicode_data(self):
        with self.assertRaises(TypeError) as assertion:
            sign(u'hello', SECRET1, 'SHA256')

        self.assertEqual(str(assertion.exception), 'data must be bytes-like')

    def test_sign_unicode_secret(self):
        with self.assertRaises(TypeError):
            sign(DATA1, u'hello', 'SHA256')


@with_settings_hosts()
class TestSignSha256(PassportTestCase, SignTestMixin):
    algorithm = 'SHA256'
    sample = b64decode(b'P4Ei1NYOHTvb82qkuvLjQT4rsfEAFLK3P5vXT8IQw3A=')


@with_settings_hosts()
class TestPack(PassportTestCase):
    @parameterized.expand(
        [
            (b'foo', b'spam'),
            (b'', b''),
            (b'foo', b''),
            (b'', b'bar'),
            (b'1.foo', b'2.bar'),
            (b'1.foo', b''),
            (b'', b'1.bar'),
        ],
    )
    def test_pack_unpack(self, first, second):
        result = unpack(pack(first, second))
        self.assertEqual(result, (first, second))

    def test_multi_packing(self):
        result = pack(b'foo', b'bar')
        result = pack(result, b'spam')
        result, spam = unpack(result)
        foo, bar = unpack(result)
        self.assertEqual(foo, b'foo')
        self.assertEqual(bar, b'bar')
        self.assertEqual(spam, b'spam')

    def test_pack_first_unicode(self):
        with self.assertRaises(TypeError) as assertion:
            pack(u'foo', 'bar')

        self.assertEqual(str(assertion.exception), 'data must be bytes-like')

    def test_pack_second_unicode(self):
        with self.assertRaises(TypeError) as assertion:
            pack('foo', u'bar')

        self.assertEqual(str(assertion.exception), 'data must be bytes-like')

    @parameterized.expand(
        [
            (b'',),
            (b'foo',),
            (b'.',),
            (b'.foo',),
            (b'-2.foo',),
            (b'x.foo',),
        ],
    )
    def test_unpack_invalid_data(self, data):
        with self.assertRaises(ValueError):
            unpack(data)


@with_settings_hosts()
class TestSigningRegistry(PassportTestCase):
    def setUp(self):
        super(TestSigningRegistry, self).setUp()
        self.registry = SigningRegistry()

    def tearDown(self):
        del self.registry
        super(TestSigningRegistry, self).tearDown()

    def build_version_dict(
        self,
        algorithm='SHA256',
        id=SIGNING_VERSION1,
        salt_length=8,
        secret=b'secret',
    ):
        return dict(
            algorithm=algorithm,
            id=id,
            salt_length=salt_length,
            secret=secret,
        )

    def build_version(self, **kwargs):
        return Version(**self.build_version_dict(**kwargs))

    def test_get_default(self):
        version1 = self.build_version(id=SIGNING_VERSION1)
        self.registry.add(version1)
        version2 = self.build_version(id=SIGNING_VERSION2)
        self.registry.add(version2)

        with self.assertRaises(DefaultVersionNotFoundSigningError):
            self.registry.get()

        self.registry.set_default_version_id(SIGNING_VERSION1)
        self.assertEqual(self.registry.get(), version1)

        self.registry.set_default_version_id(SIGNING_VERSION2)
        self.assertEqual(self.registry.get(), version2)

    def test_get(self):
        version1 = self.build_version(id=SIGNING_VERSION1)
        self.registry.add(version1)

        with self.assertRaises(VersionNotFoundSigningError):
            self.registry.get(SIGNING_VERSION2)

        self.assertEqual(self.registry.get(SIGNING_VERSION1), version1)

        version2 = self.build_version(id=SIGNING_VERSION2)
        self.registry.add(version2)
        self.registry.remove(SIGNING_VERSION1)

        with self.assertRaises(VersionNotFoundSigningError):
            self.registry.get(SIGNING_VERSION1)

        self.assertEqual(self.registry.get(SIGNING_VERSION2), version2)

    def test_get_default_version_id_no_default(self):
        self.assertIsNone(self.registry.get_default_version_id())

    def test_set_default_version_id_not_existent_version(self):
        self.registry.add(self.build_version(id=SIGNING_VERSION1))
        with self.assertRaises(VersionNotFoundSigningError):
            self.registry.set_default_version_id(SIGNING_VERSION2)

    def test_remove_not_existent_version(self):
        self.registry.add(self.build_version(id=SIGNING_VERSION1))
        self.registry.remove(SIGNING_VERSION2)
        self.assertIsNotNone(self.registry.get(SIGNING_VERSION1))

    def test_remove_default(self):
        self.registry.add(self.build_version(id=SIGNING_VERSION1))
        self.registry.set_default_version_id(SIGNING_VERSION1)

        self.assertIsNotNone(self.registry.get_default_version_id())

        self.registry.remove(SIGNING_VERSION1)

        self.assertIsNone(self.registry.get_default_version_id())

    def test_version(self):
        kwargs = dict(
            algorithm='SHA256',
            salt_length=42,
            secret=SECRET1,
            id=SIGNING_VERSION1,
        )
        version1 = Version(**kwargs)
        self.assertEqual(version1.algorithm, 'SHA256')
        self.assertEqual(version1.salt_length, 42)
        self.assertEqual(version1.secret, SECRET1)
        self.assertEqual(version1.id, SIGNING_VERSION1)

        version2 = Version.from_dict(kwargs)
        self.assertEqual(version1, version2)

    @parameterized.expand(
        [
            ('unknown',),
            (0,),
            ('',),
            (None,),
        ],
    )
    def test_version_invalid_algorithm(self, algorithm):
        with self.assertRaises(ConfigurationFailedSigningError):
            Version.from_dict(self.build_version_dict(algorithm=algorithm))

    @parameterized.expand(
        [
            (-1,),
            (0,),
            ('foo',),
            ('',),
            (None,),
        ],
    )
    def test_version_invalid_salt_length(self, salt_length):
        with self.assertRaises(ConfigurationFailedSigningError):
            Version.from_dict(self.build_version_dict(salt_length=salt_length))

    @parameterized.expand(
        [
            (b'',),
            (None,),
        ],
    )
    def test_version_invalid_secret(self, secret):
        with self.assertRaises(ConfigurationFailedSigningError):
            Version.from_dict(self.build_version_dict(secret=secret))

    def test_add_from_dict(self):
        version_dict = self.build_version_dict(id=SIGNING_VERSION1)
        self.registry.add_from_dict(
            {
                'default_version_id': SIGNING_VERSION1,
                'versions': [version_dict],
            },
        )

        self.assertEqual(
            self.registry.get(SIGNING_VERSION1),
            self.build_version(**version_dict),
        )
        self.assertEqual(self.registry.get_default_version_id(), SIGNING_VERSION1)

    def test_add_from_dict_no_default(self):
        version_dict = self.build_version_dict(id=SIGNING_VERSION1)
        self.registry.add_from_dict(
            {
                'versions': [version_dict],
            },
        )
        self.assertIsNone(self.registry.get_default_version_id())

    def test_add_from_dict_update(self):
        version_dict1 = self.build_version_dict(id=SIGNING_VERSION1)
        self.registry.add_from_dict(
            {
                'default_version_id': SIGNING_VERSION1,
                'versions': [version_dict1],
            },
        )

        version_dict2 = self.build_version_dict(id=SIGNING_VERSION2)
        version_dict3 = self.build_version_dict(id=SIGNING_VERSION3)
        self.registry.add_from_dict(
            {
                'versions': [
                    version_dict2,
                    version_dict3,
                ],
            },
        )

        self.assertEqual(self.registry.get_default_version_id(), SIGNING_VERSION1)
        self.assertEqual(
            self.registry.get(SIGNING_VERSION1),
            self.build_version(**version_dict1),
        )
        self.assertEqual(
            self.registry.get(SIGNING_VERSION2),
            self.build_version(**version_dict2),
        )
        self.assertEqual(
            self.registry.get(SIGNING_VERSION3),
            self.build_version(**version_dict3),
        )

    def test_add_from_dict_update_default(self):
        version_dict1 = self.build_version_dict(id=SIGNING_VERSION1)
        version_dict2 = self.build_version_dict(id=SIGNING_VERSION2)
        self.registry.add_from_dict(
            {
                'default_version_id': SIGNING_VERSION1,
                'versions': [
                    version_dict1,
                    version_dict2,
                ],
            },
        )
        self.registry.add_from_dict(
            {
                'default_version_id': SIGNING_VERSION2,
            },
        )

        self.assertEqual(self.registry.get_default_version_id(), SIGNING_VERSION2)

    def test_add_from_dict_invalid_default_version(self):
        with self.assertRaises(ConfigurationFailedSigningError):
            self.registry.add_from_dict(
                {
                    'default_version_id': '',
                    'versions': [
                        self.build_version_dict(),
                    ],
                },
            )

    def test_add_from_dict_unknown_default_version(self):
        with self.assertRaises(ConfigurationFailedSigningError):
            self.registry.add_from_dict(
                {
                    'default_version_id': SIGNING_VERSION1,
                    'versions': [
                        self.build_version_dict(id=SIGNING_VERSION2),
                    ],
                },
            )

    def test_add_from_dict_invalid_version(self):
        with self.assertRaises(ConfigurationFailedSigningError):
            self.registry.add_from_dict(
                {
                    'versions': [
                        self.build_version_dict(algorithm='unknown'),
                    ],
                },
            )


@with_settings_hosts()
class TestSimpleSign(PassportTestCase):
    def setUp(self):
        super(TestSimpleSign, self).setUp()
        LazyLoader.register('SigningRegistry', SigningRegistry)

    def patch_sign(self):
        fake_sign = mock.Mock(name='fake_sign', return_value=b'signature')
        return mock.patch('passport.backend.core.crypto.signing.sign', fake_sign)

    def build_registry(self, **kwargs):
        registry = SigningRegistry()
        registry.add(self.build_version(**kwargs))
        return registry

    def unpack_signature(self, signature):
        signature, version_id = unpack(signature)
        signature, salt = unpack(signature)
        return dict(
            version_id=version_id,
            salt=salt,
            signature=signature,
        )

    def build_version(
        self,
        algorithm='SHA256',
        id=SIGNING_VERSION1,
        salt_length=8,
        secret=b'secret',
    ):
        return Version(
            algorithm=algorithm,
            id=id,
            salt_length=salt_length,
            secret=secret,
        )

    def test_use_sign_result(self):
        registry = self.build_registry()

        with self.patch_sign() as fake_sign:
            fake_sign.side_effect = [b'signature1', b'signature2']
            signature1 = simple_sign(DATA1, SIGNING_VERSION1, registry)
            signature2 = simple_sign(DATA1, SIGNING_VERSION1, registry)

        signature1 = self.unpack_signature(signature1)
        signature2 = self.unpack_signature(signature2)
        self.assertEqual(signature1['signature'], b'signature1')
        self.assertEqual(signature2['signature'], b'signature2')

    def test_data_and_salt_matter(self):
        registry = self.build_registry()

        with self.patch_sign() as fake_sign1:
            signature1 = simple_sign(DATA1, SIGNING_VERSION1, registry)
        with self.patch_sign() as fake_sign2:
            signature2 = simple_sign(DATA2, SIGNING_VERSION1, registry)

        signature1 = self.unpack_signature(signature1)
        signature2 = self.unpack_signature(signature2)
        fake_sign1.assert_called_once_with(pack(DATA1, signature1['salt']), mock.ANY, mock.ANY)
        fake_sign2.assert_called_once_with(pack(DATA2, signature2['salt']), mock.ANY, mock.ANY)

    def test_salt_length_matters(self):
        registry1 = self.build_registry(salt_length=8)
        registry2 = self.build_registry(salt_length=32)

        signature1 = simple_sign(DATA1, SIGNING_VERSION1, registry1)
        signature2 = simple_sign(DATA1, SIGNING_VERSION1, registry2)

        signature1 = self.unpack_signature(signature1)
        signature2 = self.unpack_signature(signature2)
        self.assertEqual(len(signature1['salt']), 8)
        self.assertEqual(len(signature2['salt']), 32)

    def test_salt_random(self):
        registry = self.build_registry()

        signature1 = simple_sign(DATA1, SIGNING_VERSION1, registry)
        signature2 = simple_sign(DATA1, SIGNING_VERSION1, registry)

        signature1 = self.unpack_signature(signature1)
        signature2 = self.unpack_signature(signature2)
        self.assertNotEqual(signature1['salt'], signature2['salt'])

    def test_secret_matters(self):
        registry1 = self.build_registry(secret=SECRET1)
        registry2 = self.build_registry(secret=SECRET2)

        with self.patch_sign() as fake_sign1:
            simple_sign(DATA1, SIGNING_VERSION1, registry1)
        with self.patch_sign() as fake_sign2:
            simple_sign(DATA1, SIGNING_VERSION1, registry2)

        fake_sign1.assert_called_once_with(mock.ANY, SECRET1, mock.ANY)
        fake_sign2.assert_called_once_with(mock.ANY, SECRET2, mock.ANY)

    def test_algorithm_matters(self):
        registry1 = self.build_registry(algorithm='foo')
        registry2 = self.build_registry(algorithm='bar')

        with self.patch_sign() as fake_sign1:
            simple_sign(DATA1, SIGNING_VERSION1, registry1)
        with self.patch_sign() as fake_sign2:
            simple_sign(DATA1, SIGNING_VERSION1, registry2)

        fake_sign1.assert_called_once_with(mock.ANY, mock.ANY, 'foo')
        fake_sign2.assert_called_once_with(mock.ANY, mock.ANY, 'bar')

    def test_version_matters(self):
        registry = SigningRegistry()
        registry.add(
            Version(
                id=SIGNING_VERSION1,
                algorithm='foo',
                salt_length=7,
                secret=SECRET1,
            ),
        )
        registry.add(
            Version(
                id=SIGNING_VERSION2,
                algorithm='bar',
                salt_length=13,
                secret=SECRET2,
            ),
        )

        with self.patch_sign() as fake_sign1:
            signature1 = simple_sign(DATA1, SIGNING_VERSION1, registry)
        with self.patch_sign() as fake_sign2:
            signature2 = simple_sign(DATA1, SIGNING_VERSION2, registry)

        signature1 = self.unpack_signature(signature1)
        self.assertEqual(signature1['version_id'], SIGNING_VERSION1)
        self.assertEqual(len(signature1['salt']), 7)
        fake_sign1.assert_called_once_with(pack(DATA1, signature1['salt']), SECRET1, 'foo')

        signature2 = self.unpack_signature(signature2)
        self.assertEqual(signature2['version_id'], SIGNING_VERSION2)
        self.assertEqual(len(signature2['salt']), 13)
        fake_sign2.assert_called_once_with(pack(DATA1, signature2['salt']), SECRET2, 'bar')

    def test_default_version(self):
        registry = SigningRegistry()
        registry.add(self.build_version(id=SIGNING_VERSION1))
        registry.add(self.build_version(id=SIGNING_VERSION2))

        with self.assertRaises(DefaultVersionNotFoundSigningError):
            simple_sign(DATA1, registry=registry)

        registry.set_default_version_id(SIGNING_VERSION2)

        signature = simple_sign(DATA1, registry=registry)

        signature = self.unpack_signature(signature)
        self.assertEqual(signature['version_id'], SIGNING_VERSION2)

    def test_ignore_default_version(self):
        registry = SigningRegistry()
        registry.add(self.build_version(id=SIGNING_VERSION1))
        registry.add(self.build_version(id=SIGNING_VERSION2))
        registry.set_default_version_id(SIGNING_VERSION2)

        signature = simple_sign(DATA1, SIGNING_VERSION1, registry)

        signature = self.unpack_signature(signature)
        self.assertEqual(signature['version_id'], SIGNING_VERSION1)

    def test_sign_with_unknown_version(self):
        registry = self.build_registry(id=SIGNING_VERSION1)

        with self.assertRaises(VersionNotFoundSigningError):
            simple_sign(DATA1, SIGNING_VERSION2, registry)

    def test_default_registry(self):
        registry = get_signing_registry()
        registry.add(self.build_version(id=SIGNING_VERSION3, algorithm='yello'))
        registry.set_default_version_id(SIGNING_VERSION3)

        with self.patch_sign() as fake_sign:
            signature = simple_sign(DATA1)

        signature = self.unpack_signature(signature)
        self.assertEqual(signature['version_id'], SIGNING_VERSION3)
        fake_sign.assert_called_once_with(mock.ANY, mock.ANY, 'yello')

    def test_valid_signature(self):
        registry = SigningRegistry()
        registry.add(self.build_version(id=SIGNING_VERSION1))
        registry.add(self.build_version(id=SIGNING_VERSION2))
        registry.set_default_version_id(SIGNING_VERSION2)

        signature = simple_sign(DATA1, SIGNING_VERSION1, registry)

        self.assertTrue(simple_is_correct_signature(signature, DATA1, registry))

    def test_invalid_signature(self):
        registry = self.build_registry(id=SIGNING_VERSION1)
        signature = simple_sign(DATA1, SIGNING_VERSION1, registry)
        self.assertFalse(simple_is_correct_signature(signature, DATA2, registry))

    def test_check_unknown_version(self):
        registry = SigningRegistry()
        registry.add(self.build_version(id=SIGNING_VERSION1))
        registry.add(self.build_version(id=SIGNING_VERSION2))

        signature = simple_sign(DATA1, SIGNING_VERSION2, registry)
        registry.remove(SIGNING_VERSION2)

        self.assertFalse(simple_is_correct_signature(signature, DATA1, registry))

    def test_malformed_signature(self):
        registry = self.build_registry()
        self.assertFalse(simple_is_correct_signature(b'malformed', DATA1, registry))

    def test_check_with_default_registry(self):
        registry = get_signing_registry()
        registry.add(self.build_version(id=SIGNING_VERSION1))

        signature = simple_sign(DATA1, SIGNING_VERSION1, registry)

        self.assertTrue(simple_is_correct_signature(signature, DATA1))


@with_settings_hosts()
class TestRotatingSigningRegistry(PassportTestCase):
    def setUp(self):
        super(TestRotatingSigningRegistry, self).setUp()
        self.fake_time = mock.Mock(name='fake_time', return_value=0)

    def tearDown(self):
        del self.fake_time
        super(TestRotatingSigningRegistry, self).tearDown()

    def build_key_storage(self, signing_versions):
        key_storage = dict()

        class FakeKeyStorage(dict):
            def get_key(self, key_number):
                return self[key_number], key_number

            def is_key_available(self, key_number):
                return key_number in self

        key_storage = FakeKeyStorage()
        for version in signing_versions:
            version = version._asdict()
            version['id'] = version['id'].decode('latin1')
            version['secret'] = standard_b64encode(version['secret']).decode('latin1')
            key_storage[int(version['id'])] = json.dumps(version)
        return key_storage

    def build_signing_version(self, id=SIGNING_VERSION1):
        return Version(
            id=id,
            algorithm='SHA256',
            salt_length=8,
            secret=SECRET3,
        )

    def build_signing_registry(
        self,
        key_storage,
        epoch_length,
        foresight=0,
        foresight_cache_ttl=0,
    ):
        return RotatingSigningRegistry(
            key_storage=key_storage,
            epoch_length=epoch_length,
            foresight=foresight,
            foresight_cache_ttl=foresight_cache_ttl,
            timer=self.fake_time,
        )

    def test_time_determines_signing_version(self):
        version0 = self.build_signing_version(id=b'0')
        version1 = self.build_signing_version(id=b'1')
        key_storage = self.build_key_storage([version0, version1])
        signing_registry = self.build_signing_registry(
            key_storage=key_storage,
            epoch_length=EPOCH_LENGTH1,
        )

        self.fake_time.return_value = 0
        secret = signing_registry.get()
        self.assertEqual(secret, version0)

        self.fake_time.return_value = EPOCH_LENGTH1 - 1
        secret = signing_registry.get()
        self.assertEqual(secret, version0)

        self.fake_time.return_value = EPOCH_LENGTH1
        secret = signing_registry.get()
        self.assertEqual(secret, version1)

    def test_epoch_determines_signing_version(self):
        version0 = self.build_signing_version(id=b'0')
        version1 = self.build_signing_version(id=b'1')
        key_storage = self.build_key_storage([version0, version1])
        self.fake_time.return_value = EPOCH_LENGTH1

        signing_registry = self.build_signing_registry(
            key_storage=key_storage,
            epoch_length=EPOCH_LENGTH1,
        )
        secret = signing_registry.get()
        self.assertEqual(secret, version1)

        signing_registry = self.build_signing_registry(
            key_storage=key_storage,
            epoch_length=EPOCH_LENGTH2,
        )
        secret = signing_registry.get()
        self.assertEqual(secret, version0)

    def get_specified_signing_version(self):
        version0 = self.build_signing_version(id=b'0')
        version1 = self.build_signing_version(id=b'1')
        key_storage = self.build_key_storage([version0, version1])
        signing_registry = self.build_signing_registry(
            key_storage=key_storage,
            epoch_length=EPOCH_LENGTH1,
        )

        self.fake_time.return_value = 0
        secret = signing_registry.get('1')
        self.assertEqual(secret, version1)

    def test_dont_cache_broken_keys(self):
        version = self.build_signing_version(id=b'0')
        key_storage = self.build_key_storage([version])
        key_storage.get_key = mock.Mock(
            wraps=key_storage.get_key,
            side_effect=[
                ('', 0),
                mock.DEFAULT,
            ],
        )
        key_storage.delete_key_from_cache = mock.Mock()
        signing_registry = self.build_signing_registry(
            key_storage=key_storage,
            epoch_length=EPOCH_LENGTH1,
        )

        with self.assertRaises(ValueError):
            signing_registry.get()

        key_storage.delete_key_from_cache.assert_called_once_with(0)

        secret = signing_registry.get()

        self.assertEqual(secret, version)
        key_storage.delete_key_from_cache.assert_called_once()

    def test_get_prev_version_id(self):
        key_storage = self.build_key_storage(list())
        signing_registry = self.build_signing_registry(
            key_storage=key_storage,
            epoch_length=EPOCH_LENGTH1,
        )

        self.assertEqual(signing_registry.get_prev_version_id('2'), '1')
        self.assertEqual(signing_registry.get_prev_version_id('1'), '0')

    def test_foresight_ok(self):
        self.fake_time.return_value = 0
        key_storage = self.build_key_storage(
            [
                self.build_signing_version(id=b'0'),
                self.build_signing_version(id=b'1'),
                self.build_signing_version(id=b'2'),
            ],
        )
        signing_registry = self.build_signing_registry(
            key_storage=key_storage,
            epoch_length=EPOCH_LENGTH1,
            foresight=2 * EPOCH_LENGTH1,
        )

        self.assertIsNone(signing_registry.get_timestamp_when_secrets_run_out())

    def test_foresight_run_out(self):
        self.fake_time.return_value = EPOCH_LENGTH1
        key_storage = self.build_key_storage(
            [
                self.build_signing_version(id=b'0'),
                self.build_signing_version(id=b'1'),
                self.build_signing_version(id=b'2'),
            ],
        )
        signing_registry = self.build_signing_registry(
            key_storage=key_storage,
            epoch_length=EPOCH_LENGTH1,
            foresight=2 * EPOCH_LENGTH1,
        )

        self.assertEqual(
            signing_registry.get_timestamp_when_secrets_run_out(),
            3 * EPOCH_LENGTH1,
        )

    def test_foresight_hole(self):
        self.fake_time.return_value = 0
        key_storage = self.build_key_storage(
            [
                self.build_signing_version(id=b'0'),
                self.build_signing_version(id=b'2'),
            ],
        )
        signing_registry = self.build_signing_registry(
            key_storage=key_storage,
            epoch_length=EPOCH_LENGTH1,
            foresight=2 * EPOCH_LENGTH1,
        )

        self.assertEqual(
            signing_registry.get_timestamp_when_secrets_run_out(),
            EPOCH_LENGTH1,
        )


class ByteSequenceTestCase(PassportTestCase):
    def test_all_bytes(self):
        for i in range(256):
            b = bytes([i])
            assert b == ByteSequence().to_python(b)
