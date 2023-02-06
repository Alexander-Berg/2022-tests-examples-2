# -*- coding: utf-8 -*-
from django.test.utils import override_settings
from nose.tools import (
    eq_,
    raises,
)
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import CREATE
from passport.backend.oauth.core.db.psuid import (
    make_psuid,
    parse_psuid,
    PsuidInvalidError,
)
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.test.base_test_data import (
    TEST_CIPHER_KEYS,
    TEST_UID,
)
from passport.backend.oauth.core.test.framework import DBTestCase


@override_settings(
    PSUID_DEFAULT_VERSION=1,
    PSUID_ENCRYPTION_KEYS=TEST_CIPHER_KEYS,
    PSUID_SIGNATURE_KEYS=TEST_CIPHER_KEYS,
)
class PsuidTestCase(DBTestCase):
    def setUp(self):
        super(PsuidTestCase, self).setUp()
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')],
            default_title='Test app',
        )) as client:
            client.display_id = 'a' * 32
            self.test_client = client

    def test_make_and_parse_ok(self):
        psuid = make_psuid(TEST_UID, self.test_client)
        eq_(psuid, '1.AAAAAQ.6evKhOrL2DLD0IVkUfIdzg.w35cnO4igIT6_iJdipaUgA')
        uid, seed, client = parse_psuid(psuid)
        eq_(uid, TEST_UID)
        eq_(seed, 0)
        eq_(client.display_id, self.test_client.display_id)

    def test_make_with_custom_seed_and_parse_ok(self):
        psuid = make_psuid(TEST_UID, self.test_client, seed=100500)
        eq_(psuid, '1.AAAAAQ.CysQ3Si_1ZcJ3CcH8ETInw.wzSeDxf3Rc9bAX4TQiLzqw')
        uid, seed, client = parse_psuid(psuid)
        eq_(uid, TEST_UID)
        eq_(seed, 100500)
        eq_(client.display_id, self.test_client.display_id)

    @raises(PsuidInvalidError)
    def test_parse_not_enough_parts_error(self):
        parse_psuid('1.foo.bar')

    @raises(PsuidInvalidError)
    def test_parse_invalid_version_error(self):
        parse_psuid('nan.foo.bar.zar')

    @raises(PsuidInvalidError)
    def test_parse_unknown_version_error(self):
        parse_psuid('100500.foo.bar.zar')

    @raises(PsuidInvalidError)
    def test_parse_client_not_found_error(self):
        parse_psuid('1.foo.bar.zar')

    @raises(PsuidInvalidError)
    def test_parse_failed_to_decrypt_error(self):
        parse_psuid('1.AAAAAQ.bar.zar')

    @raises(PsuidInvalidError)
    def test_parse_signature_not_matched_error(self):
        parse_psuid('1.AAAAAQ.CysQ3Si_1ZcJ3CcH8ETInw.zar')
