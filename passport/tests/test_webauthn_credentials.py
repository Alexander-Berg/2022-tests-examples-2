# -*- coding: utf-8 -*-
from datetime import datetime
import unittest

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.models.webauthn import (
    WebauthnCredential,
    WebauthnCredentials,
)


TEST_CREDENTIAL_EXTERNAL_ID = 'some-long-credential-id'
TEST_PUBLIC_KEY = 'some-long-public-key'
TEST_DEVICE_NAME = 'device-name'
TEST_RP_ID = 'rp-id'


class TestWebauthnCredentialModel(unittest.TestCase):
    def test_parse_basic(self):
        cred = WebauthnCredential().parse(
            {
                'id': 1,
                'external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                'public_key': '1:%s' % TEST_PUBLIC_KEY,
                'relying_party_id': TEST_RP_ID,
            },
        )

        eq_(cred.id, 1)
        eq_(cred.external_id, TEST_CREDENTIAL_EXTERNAL_ID)
        eq_(cred.public_key, TEST_PUBLIC_KEY)
        eq_(cred.relying_party_id, TEST_RP_ID)
        ok_(not cred.sign_count)
        ok_(not cred.device_name)
        ok_(not cred.is_device_mobile)
        ok_(not cred.is_device_tablet)
        ok_(not cred.created_at)

    def test_parse_full(self):
        cred = WebauthnCredential().parse(
            {
                'id': 1,
                'external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                'public_key': '1:%s' % TEST_PUBLIC_KEY,
                'relying_party_id': TEST_RP_ID,
                'sign_count': 2,
                'device_name': TEST_DEVICE_NAME,
                'os_family_id': '3',
                'browser_id': '4',
                'is_device_mobile': '1',
                'is_device_tablet': '1',
                'created': '42',
            },
        )

        eq_(cred.id, 1)
        eq_(cred.external_id, TEST_CREDENTIAL_EXTERNAL_ID)
        eq_(cred.public_key, TEST_PUBLIC_KEY)
        eq_(cred.relying_party_id, TEST_RP_ID)
        eq_(cred.sign_count, 2)
        eq_(cred.device_name, TEST_DEVICE_NAME)
        eq_(cred.os_family_id, 3)
        eq_(cred.browser_id, 4)
        ok_(cred.is_device_mobile)
        ok_(cred.is_device_tablet)
        eq_(cred.created_at, datetime.fromtimestamp(42))

    def test_repr(self):
        cred = WebauthnCredential().parse(
            {
                'id': 1,
                'external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                'relying_party_id': TEST_RP_ID,
                'device_name': TEST_DEVICE_NAME,
            },
        )
        eq_(
            repr(cred),
            '<WebauthnCredential: id=1, external_id=%s, rp_id=%s, device_name=%s>' % (
                TEST_CREDENTIAL_EXTERNAL_ID,
                TEST_RP_ID,
                TEST_DEVICE_NAME,
            ),
        )

    def test_is_suitable_for_host(self):
        cred = WebauthnCredential().parse(
            {
                'id': 1,
                'external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                'relying_party_id': 'passport.yandex.ru',
            },
        )
        ok_(cred.is_suitable_for_host('passport.yandex.ru'))
        ok_(cred.is_suitable_for_host('smth.passport.yandex.ru'))
        ok_(not cred.is_suitable_for_host('yandex.ru'))
        ok_(not cred.is_suitable_for_host('passport.yandex.com'))
        ok_(not cred.is_suitable_for_host('passport.yandex.ru.narod.ru'))


class TestWebauthnCredentialsModel(unittest.TestCase):
    def test_parse(self):
        creds = WebauthnCredentials().parse({
            'webauthn_credentials': [
                {
                    'id': 1,
                    'external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                },
                {
                    'id': 2,
                },
            ],
        })

        eq_(len(creds.all()), 2)
        ok_(TEST_CREDENTIAL_EXTERNAL_ID in creds)
        eq_(
            creds.by_external_id(TEST_CREDENTIAL_EXTERNAL_ID).id,
            1,
        )

    def test_modify(self):
        creds = WebauthnCredentials().parse({})
        eq_(len(creds.all()), 0)

        creds.add(WebauthnCredential().parse({'id': 1, 'external_id': TEST_CREDENTIAL_EXTERNAL_ID}))
        eq_(len(creds.all()), 1)

        creds.remove(TEST_CREDENTIAL_EXTERNAL_ID)
        eq_(len(creds.all()), 0)

    def test_remove_unexistent(self):
        creds = WebauthnCredentials().parse({})
        with assert_raises(KeyError):
            creds.remove(TEST_CREDENTIAL_EXTERNAL_ID)

    def test_repr(self):
        creds = WebauthnCredentials().parse({})

        creds.add(
            WebauthnCredential().parse({
                'id': 1,
                'external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                'relying_party_id': TEST_RP_ID,
                'device_name': TEST_DEVICE_NAME,
            }),
        )

        eq_(
            repr(creds),
            '<WebauthnCredentials: [<WebauthnCredential: id=1, external_id=%s, rp_id=%s, device_name=%s>]>' % (
                TEST_CREDENTIAL_EXTERNAL_ID,
                TEST_RP_ID,
                TEST_DEVICE_NAME,
            )
        )
