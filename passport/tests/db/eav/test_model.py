# -*- coding: utf-8 -*-
from copy import deepcopy

from django.test.utils import override_settings
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.oauth.core.common.crypto import (
    decrypt,
    encrypt,
)
from passport.backend.oauth.core.common.utils import make_hash
from passport.backend.oauth.core.db.eav.attributes import ATTRIBUTES_BY_NAME
from passport.backend.oauth.core.db.eav.context_managers import (
    CREATE,
    DELETE,
    UPDATE,
)
from passport.backend.oauth.core.db.eav.errors import (
    AttributeNotFoundError,
    EntityNotFoundError,
)
from passport.backend.oauth.core.db.eav.schemas import auto_id
from passport.backend.oauth.core.db.eav.utils import insert_on_duplicate_update
from passport.backend.oauth.core.db.schemas import (
    client_attributes_table,
    client_by_owner_table,
    client_by_params_table,
    client_by_uid_table,
    token_attributes_table,
    token_by_access_token_table,
    token_by_alias_table,
    token_by_params_table,
)
from passport.backend.oauth.core.test.fake_db import FakeDB
from passport.backend.oauth.core.test.framework import BaseTestCase
from passport.backend.oauth.core.test.utils import iter_eq
from passport.backend.oauth.tvm_api.tvm_keygen import decrypt as cpp_decrypt
from passport.backend.utils.time import unixtime_to_datetime
from sqlalchemy import (
    and_,
    select,
)
from sqlalchemy.dialects import mysql

from .base_test_data import (
    ClientForTest,
    SecretKeyForTest,
    TokenForTest,
)


TEST_CIPHER_KEYS = {
    1: b'*' * 32,
    2: b'*' * 32,
}


class BaseModelTestCase(BaseTestCase):
    def setUp(self):
        super(BaseModelTestCase, self).setUp()
        self.fake_db = FakeDB()
        self.fake_db.start()

        with CREATE(TokenForTest()) as token:
            token.uid = 1
            token.access_token = 'foo'
            token.scope_ids = [1, 2]
            token.client_id = 1
            token.device_id = 'apple'
            token.meta = 'meta'
        eq_(token.id, 1)
        self.token = token

        with CREATE(ClientForTest()) as client:
            client.uid = 1
            client.display_id = 'random_stuff'
            client.default_title = 'Тестовое приложение'
            client.secret = 'secret'
            client.is_blocked = False
            client.approval_status = 0
            client.services = ['test']
        eq_(client.id, 1)
        self.client = client

        with CREATE(ClientForTest()) as client:
            client.uid = 42
            client.display_id = 'random_stuff_2'
            client.default_title = 'Удалённое приложение'
            client.secret = 'secret'
            client.is_blocked = False
            client.approval_status = 0
            client.services = ['test']
            client.deleted = unixtime_to_datetime(1)
        eq_(client.id, 2)
        self.deleted_client = client

        self.fake_db.reset_mocks()

    def tearDown(self):
        self.fake_db.stop()
        super(BaseModelTestCase, self).tearDown()

    def eq_queries(self, executed, expected):
        eq_(len(executed), len(expected), [len(executed), len(expected), executed, expected])

        iter_eq(
            [str(q.compile(dialect=mysql.dialect())) for q in executed],
            [str(q.compile(dialect=mysql.dialect())) for q in expected],
        )

        iter_eq(
            [q.compile(dialect=mysql.dialect()).params for q in executed],
            [q.compile(dialect=mysql.dialect()).params for q in expected],
        )


class TestModelCommon(BaseModelTestCase):
    def test_del_attribute(self):
        del self.token.uid
        ok_('uid' not in self.token._attributes)
        ok_(self.token.uid is None)

    def test_set_attribute_to_none(self):
        self.token.uid = None
        ok_('uid' not in self.token._attributes)
        ok_(self.token.uid is None)

    @raises(AttributeNotFoundError)
    def test_bad_attribute_get(self):
        getattr(self.token, 'bad_attr')

    @raises(AttributeNotFoundError)
    def test_bad_attribute_set(self):
        setattr(self.token, 'bad_attr', 'foo')

    @raises(AttributeNotFoundError)
    def test_bad_attribute_del(self):
        delattr(self.token, 'bad_attr')

    def test_magic_methods(self):
        eq_(self.token, deepcopy(self.token))
        ok_(not self.token != deepcopy(self.token))
        eq_(repr(self.token), '<TokenForTest id=1>: %s' % self.token._attributes)

    def test_ignore_unknown_attrs_on_parse(self):
        eq_(
            dict(TokenForTest._parse_rows_from_db([
                (1, 1, b'access_token*'),
                (1, 3, b'123'),
                (1, 100500, b'smth_weird'),
            ])),
            {
                1: {
                    'access_token': 'access_token*',
                    'uid': 123,
                },
            },
        )
        eq_(
            dict(TokenForTest._parse_attrs_from_bb(
                1,
                {
                    '1': 'access_token*',
                    '3': '123',
                    '100500': 'smth_weird',
                },
            )),
            {
                'access_token': 'access_token*',
                'uid': 123,
            },
        )

    @raises(ValueError)
    def test_error_on_parse(self):
        TokenForTest.parse({})


@override_settings(ATTRIBUTE_CIPHER_KEYS=TEST_CIPHER_KEYS)
class TestEncryptedAttrs(BaseModelTestCase):
    def test_ok(self):
        with CREATE(SecretKeyForTest()) as key:
            key.private_secret = 'foo'

        eq_(key.id, 1)

        encrypted = self.fake_db.get('oauthdbcentral', 'tvm_secret_key_attributes', 'private_secret', id=1)
        ok_(encrypted != b'foo')
        eq_(
            decrypt(keys=TEST_CIPHER_KEYS, encrypted_message=encrypted),
            (2, b'foo\x00\x00\x00\x00\x00\x00\x00\x01'),
        )

        key = SecretKeyForTest.by_id(1)
        eq_(key.private_secret, 'foo')

        assert 'foo' == cpp_decrypt(TEST_CIPHER_KEYS[1], encrypted, 1)

    def test_unicode_ok(self):
        # нужен id ключа, не кодирующийся ascii-символом
        self.fake_db.insert('oauthdbcentral', 'auto_id_tvm_secret_key', id=127)

        with CREATE(SecretKeyForTest()) as key:
            key.private_secret = 'foo'

        eq_(key.id, 128)

        encrypted = self.fake_db.get('oauthdbcentral', 'tvm_secret_key_attributes', 'private_secret', id=128)
        ok_(encrypted != b'foo')
        eq_(
            decrypt(keys=TEST_CIPHER_KEYS, encrypted_message=encrypted),
            (2, b'foo\x00\x00\x00\x00\x00\x00\x00\x80'),
        )

        key = SecretKeyForTest.by_id(128)
        eq_(key.private_secret, 'foo')

    def test_ok_old_version(self):
        with CREATE(SecretKeyForTest()) as key:
            pass

        eq_(key.id, 1)

        encrypted_value = encrypt(keys=TEST_CIPHER_KEYS, message='foo', version=1)
        self.fake_db.insert('oauthdbcentral', 'tvm_secret_key_attributes', id=1, type=2, value=encrypted_value)

        key = SecretKeyForTest.by_id(1)
        eq_(key.private_secret, 'foo')

    def test_unencrypted_ok(self):
        with CREATE(SecretKeyForTest()) as key:
            pass

        eq_(key.id, 1)

        self.fake_db.insert('oauthdbcentral', 'tvm_secret_key_attributes', id=1, type=2, value=b'not encrypted')

        key = SecretKeyForTest.by_id(1)
        eq_(key.private_secret, 'not encrypted')

    def test_corrupt_parent_id(self):
        with CREATE(SecretKeyForTest()) as key:
            pass

        eq_(key.id, 1)

        encrypted_value = encrypt(keys=TEST_CIPHER_KEYS, message='foo\x00\x00\x00\x00\x00\x00\x00\x02', version=2)
        self.fake_db.insert('oauthdbcentral', 'tvm_secret_key_attributes', id=1, type=2, value=encrypted_value)

        key = SecretKeyForTest.by_id(1)
        eq_(key.private_secret, 'foo')


class TestModelLoadFromShard(BaseModelTestCase):
    def test_load_by_id_ok(self):
        token = TokenForTest.by_id(1)
        eq_(token, self.token)

        eq_(self.fake_db.query_count('oauthdbshard1'), 1)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 0)

        self.eq_queries(
            self.fake_db.get_queries('oauthdbshard1'),
            [
                select([token_attributes_table]).where(token_attributes_table.c.id == 1),
            ]
        )

    @raises(EntityNotFoundError)
    def test_load_by_id_not_found(self):
        TokenForTest.by_id(2)

    def test_load_by_index_ok(self):
        tokens = TokenForTest.by_index('params', uid=1)
        eq_(tokens, [self.token])

        eq_(self.fake_db.query_count('oauthdbshard1'), 1)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 0)

        ids = select([
            token_by_params_table.c.id,
        ]).where(
            token_by_params_table.c.uid.in_([1]),
        ).order_by(
            token_by_params_table.c.id,
        ).alias()
        self.eq_queries(
            self.fake_db.get_queries('oauthdbshard1'),
            [
                select([
                    token_attributes_table.c.id,
                    token_attributes_table.c.type,
                    token_attributes_table.c.value,
                ]).select_from(
                    token_attributes_table.join(ids, token_attributes_table.c.id == ids.c.id),
                ).order_by(
                    token_attributes_table.c.id,
                ),
            ]
        )

    def test_load_by_index_with_value_lists(self):
        tokens = TokenForTest.by_index('params', uid=[1, 2], device_id=[b'apple', b'android', b'winmobile'])
        eq_(tokens, [self.token])

        eq_(self.fake_db.query_count('oauthdbshard1'), 1)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 0)

        ids = select([
            token_by_params_table.c.id,
        ]).where(and_(
            token_by_params_table.c.uid.in_([1, 2]),
            token_by_params_table.c.device_id.in_([b'apple', b'android', b'winmobile']),
        )).order_by(
            token_by_params_table.c.id,
        ).alias()
        self.eq_queries(
            self.fake_db.get_queries('oauthdbshard1'),
            [
                select([
                    token_attributes_table.c.id,
                    token_attributes_table.c.type,
                    token_attributes_table.c.value,
                ]).select_from(
                    token_attributes_table.join(ids, token_attributes_table.c.id == ids.c.id),
                ).order_by(
                    token_attributes_table.c.id,
                ),
            ]
        )

    def test_load_by_index_not_found(self):
        tokens = TokenForTest.by_index('params', uid=2)
        eq_(tokens, [])

        eq_(self.fake_db.query_count('oauthdbshard1'), 1)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 0)


class TestModelLoadFromCentral(BaseModelTestCase):
    def test_load_by_id_ok(self):
        client = ClientForTest.by_id(1)
        eq_(client, self.client)

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 1)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 0)

        self.eq_queries(
            self.fake_db.get_queries('oauthdbcentral'),
            [
                select([client_attributes_table]).where(client_attributes_table.c.id == 1),
            ]
        )

    @raises(EntityNotFoundError)
    def test_load_by_id_not_found(self):
        ClientForTest.by_id(100500)

    @raises(EntityNotFoundError)
    def test_load_by_id_deleted(self):
        ClientForTest.by_id(2)

    def test_load_by_id_deleted_ok(self):
        client = ClientForTest.by_id(2, allow_deleted=True)
        eq_(client, self.deleted_client)

    def test_load_by_index_ok(self):
        clients = ClientForTest.by_index('uid', uid=1)
        eq_(clients, [self.client])

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 1)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 0)

        ids = select([
            client_by_uid_table.c.id,
        ]).where(
            client_by_uid_table.c.uid.in_([1]),
        ).order_by(
            client_by_uid_table.c.id,
        ).alias()
        self.eq_queries(
            self.fake_db.get_queries('oauthdbcentral'),
            [
                select([
                    client_attributes_table.c.id,
                    client_attributes_table.c.type,
                    client_attributes_table.c.value,
                ]).select_from(
                    client_attributes_table.join(ids, client_attributes_table.c.id == ids.c.id),
                ).order_by(
                    client_attributes_table.c.id,
                ),
            ]
        )

    def test_load_by_index_with_value_lists(self):
        clients = ClientForTest.by_index('uid', uid=[1, 2])
        eq_(clients, [self.client])

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 1)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 0)

        ids = select([
            client_by_uid_table.c.id,
        ]).where(
            client_by_uid_table.c.uid.in_([1, 2]),
        ).order_by(
            client_by_uid_table.c.id,
        ).alias()
        self.eq_queries(
            self.fake_db.get_queries('oauthdbcentral'),
            [
                select([
                    client_attributes_table.c.id,
                    client_attributes_table.c.type,
                    client_attributes_table.c.value,
                ]).select_from(
                    client_attributes_table.join(ids, client_attributes_table.c.id == ids.c.id),
                ).order_by(
                    client_attributes_table.c.id,
                ),
            ]
        )

    def test_load_by_index_not_found(self):
        clients = ClientForTest.by_index('uid', uid=2)
        eq_(clients, [])

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 1)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 0)


class TestModelSerializeToShard(BaseModelTestCase):
    def test_create(self):
        self.fake_db.check_missing('oauthdbcentral', 'auto_id_token', id=0)
        self.fake_db.check('oauthdbcentral', 'auto_id_token', 'id', 1)

        with CREATE(TokenForTest()) as token:
            token.uid = 3
            token.access_token = 'bar'
            token.scope_ids = [3, 4]
            token.client_id = 2
            token.device_id = 'android'

        eq_(token.id, 2)

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 1)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)

        self.eq_queries(
            self.fake_db.get_transaction_queries('oauthdbcentral'),
            [
                auto_id['token'].insert().values({}),
            ],
        )
        self.eq_queries(
            self.fake_db.get_transaction_queries('oauthdbshard1'),
            [
                insert_on_duplicate_update(token_attributes_table, ['value']).values([
                    {
                        'id': 2,
                        'type': ATTRIBUTES_BY_NAME['token']['access_token'][0],
                        'value': b'bar',
                    },
                    {
                        'id': 2,
                        'type': ATTRIBUTES_BY_NAME['token']['scope_ids'][0],
                        'value': b'|3|4|',
                    },
                    {
                        'id': 2,
                        'type': ATTRIBUTES_BY_NAME['token']['uid'][0],
                        'value': b'3',
                    },
                    {
                        'id': 2,
                        'type': ATTRIBUTES_BY_NAME['token']['client_id'][0],
                        'value': b'2',
                    },
                    {
                        'id': 2,
                        'type': ATTRIBUTES_BY_NAME['token']['device_id'][0],
                        'value': b'android',
                    },
                ]),
                token_by_access_token_table.insert().values({
                    'access_token': make_hash('bar'),
                    'id': 2,
                }),
                token_by_params_table.insert().values({
                    'client_id': 2,
                    'device_id': b'android',
                    'id': 2,
                    'scope_ids': b'|3|4|',
                    'uid': 3,
                }),
            ],
        )
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'uid', b'3', id=2)
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'access_token', b'bar', id=2)
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'scope_ids', b'|3|4|', id=2)
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'client_id', b'2', id=2)
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'device_id', b'android', id=2)
        self.fake_db.check_missing('oauthdbshard1', 'token_attributes', 'meta', id=2)

        self.fake_db.check('oauthdbshard1', 'token_by_params', 'id', 2, uid=3)

        self.fake_db.check('oauthdbcentral', 'auto_id_token', 'id', 2, id=2)

    def test_create_with_nullable_index_fields(self):
        self.fake_db.check_missing('oauthdbcentral', 'auto_id_token', id=0)
        self.fake_db.check('oauthdbcentral', 'auto_id_token', 'id', 1)

        with CREATE(TokenForTest()) as token:
            token.uid = 3
            token.access_token = 'bar'
            token.scope_ids = [3, 4]
            token.client_id = 2
            token.device_id = 'android'
            token.alias = 'alias'

        eq_(token.id, 2)

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 1)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)

        self.eq_queries(
            self.fake_db.get_transaction_queries('oauthdbcentral'),
            [
                auto_id['token'].insert().values({}),
            ],
        )
        self.eq_queries(
            self.fake_db.get_transaction_queries('oauthdbshard1'),
            [
                insert_on_duplicate_update(token_attributes_table, ['value']).values([
                    {
                        'id': 2,
                        'type': ATTRIBUTES_BY_NAME['token']['access_token'][0],
                        'value': b'bar',
                    },
                    {
                        'id': 2,
                        'type': ATTRIBUTES_BY_NAME['token']['scope_ids'][0],
                        'value': b'|3|4|',
                    },
                    {
                        'id': 2,
                        'type': ATTRIBUTES_BY_NAME['token']['uid'][0],
                        'value': b'3',
                    },
                    {
                        'id': 2,
                        'type': ATTRIBUTES_BY_NAME['token']['client_id'][0],
                        'value': b'2',
                    },
                    {
                        'id': 2,
                        'type': ATTRIBUTES_BY_NAME['token']['device_id'][0],
                        'value': b'android',
                    },
                    {
                        'id': 2,
                        'type': ATTRIBUTES_BY_NAME['token']['alias'][0],
                        'value': b'alias',
                    },
                ]),
                token_by_access_token_table.insert().values({
                    'access_token': make_hash('bar'),
                    'id': 2,
                }),
                token_by_alias_table.insert().values({
                    'alias': make_hash('alias'),
                    'id': 2,
                    'uid': 3,
                }),
                token_by_params_table.insert().values({
                    'client_id': 2,
                    'device_id': b'android',
                    'id': 2,
                    'scope_ids': b'|3|4|',
                    'uid': 3,
                }),
            ],
        )
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'uid', b'3', id=2)
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'access_token', b'bar', id=2)
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'scope_ids', b'|3|4|', id=2)
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'client_id', b'2', id=2)
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'device_id', b'android', id=2)
        self.fake_db.check_missing('oauthdbshard1', 'token_attributes', 'meta', id=2)

        self.fake_db.check('oauthdbshard1', 'token_by_params', 'id', 2, uid=3)

        self.fake_db.check('oauthdbcentral', 'auto_id_token', 'id', 2, id=2)

    def test_update(self):
        with UPDATE(self.token) as token:
            del token.meta
            token.scope_ids = [2, 3]
            token.client_id = 2

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 1)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 0)

        self.eq_queries(
            self.fake_db.get_transaction_queries('oauthdbshard1'),
            [
                insert_on_duplicate_update(token_attributes_table, ['value']).values([
                    {
                        'id': 1,
                        'type': ATTRIBUTES_BY_NAME['token']['scope_ids'][0],
                        'value': b'|2|3|',
                    },
                    {
                        'id': 1,
                        'type': ATTRIBUTES_BY_NAME['token']['client_id'][0],
                        'value': b'2',
                    },
                ]),
                token_attributes_table.delete().where(and_(
                    token_attributes_table.c.id == 1,
                    token_attributes_table.c.type == ATTRIBUTES_BY_NAME['token']['meta'][0],
                )),
                token_by_params_table.update().where(and_(
                    token_by_params_table.c.client_id == 1,
                    token_by_params_table.c.device_id == b'apple',
                    token_by_params_table.c.id == 1,
                    token_by_params_table.c.scope_ids == b'|1|2|',
                    token_by_params_table.c.uid == 1,
                )).values({
                    'client_id': 2,
                    'device_id': b'apple',
                    'id': 1,
                    'scope_ids': b'|2|3|',
                    'uid': 1,
                }),
            ],
        )
        self.fake_db.check_missing('oauthdbshard1', 'token_attributes', 'meta', id=1)
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'scope_ids', b'|2|3|', id=1)
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'client_id', b'2', id=1)
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'uid', b'1', id=1)
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'access_token', b'foo', id=1)

        self.fake_db.check('oauthdbshard1', 'token_by_params', 'id', 1, uid=1)

    def test_update_nothing_changed(self):
        with UPDATE(self.token):
            pass

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 0)

        self.fake_db.check('oauthdbshard1', 'token_attributes', 'access_token', b'foo', id=1)
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'scope_ids', b'|1|2|', id=1)
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'client_id', b'1', id=1)

        self.fake_db.check('oauthdbshard1', 'token_by_params', 'id', 1, uid=1)

    def test_update_index_changed(self):
        with UPDATE(self.token) as token:
            token.uid = 2

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 1)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 0)

        self.eq_queries(
            self.fake_db.get_transaction_queries('oauthdbshard1'),
            [
                insert_on_duplicate_update(token_attributes_table, ['value']).values([
                    {
                        'id': 1,
                        'type': ATTRIBUTES_BY_NAME['token']['uid'][0],
                        'value': b'2',
                    },
                ]),
                token_by_params_table.update().where(and_(
                    token_by_params_table.c.client_id == 1,
                    token_by_params_table.c.device_id == b'apple',
                    token_by_params_table.c.id == 1,
                    token_by_params_table.c.scope_ids == b'|1|2|',
                    token_by_params_table.c.uid == 1,
                )).values({
                    'client_id': 1,
                    'device_id': b'apple',
                    'id': 1,
                    'scope_ids': b'|1|2|',
                    'uid': 2,
                }),
            ],
        )
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'uid', b'2', id=1)
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'access_token', b'foo', id=1)
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'scope_ids', b'|1|2|', id=1)
        self.fake_db.check('oauthdbshard1', 'token_attributes', 'client_id', b'1', id=1)

        self.fake_db.check('oauthdbshard1', 'token_by_params', 'id', 1, uid=2)
        self.fake_db.check_missing('oauthdbshard1', 'token_by_params', uid=1)

    def test_delete(self):
        with DELETE(self.token):
            pass

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 1)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 0)

        self.eq_queries(
            self.fake_db.get_transaction_queries('oauthdbshard1'),
            [
                token_attributes_table.delete().where(
                    token_attributes_table.c.id == 1,
                ),
                token_by_access_token_table.delete().where(and_(
                    token_by_access_token_table.c.access_token == make_hash('foo'),
                    token_by_access_token_table.c.id == 1,
                )),
                token_by_params_table.delete().where(and_(
                    token_by_params_table.c.client_id == 1,
                    token_by_params_table.c.device_id == b'apple',
                    token_by_params_table.c.id == 1,
                    token_by_params_table.c.scope_ids == b'|1|2|',
                    token_by_params_table.c.uid == 1,
                )),
            ],
        )

        self.fake_db.check_missing('oauthdbshard1', 'token_attributes', 'uid', id=1)
        self.fake_db.check_missing('oauthdbshard1', 'token_attributes', 'access_token', id=1)
        self.fake_db.check_missing('oauthdbshard1', 'token_attributes', 'scope_ids', id=1)
        self.fake_db.check_missing('oauthdbshard1', 'token_attributes', 'client_id', id=1)
        self.fake_db.check_missing('oauthdbshard1', 'token_attributes', 'device_id', id=1)

        self.fake_db.check_missing('oauthdbshard1', 'token_by_params', 'id', uid=1)


class TestModelSerializeToCentral(BaseModelTestCase):
    def test_create(self):
        self.fake_db.check_missing('oauthdbcentral', 'auto_id_client', id=0)
        self.fake_db.check('oauthdbcentral', 'auto_id_client', 'id', 1)

        with CREATE(ClientForTest()) as client:
            client.uid = 3
            client.display_id = 'random_stuff_2'
            client.secret = 'non-secret'
            client.scope_ids = [3, 4]
            client.approval_status = 0
            client.services = ['test']

        eq_(client.id, 3)

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 2)

        self.eq_queries(
            self.fake_db.get_transaction_queries('oauthdbcentral', transaction_index=0),
            [
                auto_id['client'].insert().values({}),
            ]
        )

        self.eq_queries(
            self.fake_db.get_transaction_queries('oauthdbcentral', transaction_index=1),
            [
                insert_on_duplicate_update(client_attributes_table, ['value']).values([
                    {
                        'id': 3,
                        'type': ATTRIBUTES_BY_NAME['client']['uid'][0],
                        'value': b'3',
                    },
                    {
                        'id': 3,
                        'type': ATTRIBUTES_BY_NAME['client']['scope_ids'][0],
                        'value': b'|3|4|',
                    },
                    {
                        'id': 3,
                        'type': ATTRIBUTES_BY_NAME['client']['secret'][0],
                        'value': b'non-secret',
                    },
                    {
                        'id': 3,
                        'type': ATTRIBUTES_BY_NAME['client']['approval_status'][0],
                        'value': b'0',
                    },
                    {
                        'id': 3,
                        'type': ATTRIBUTES_BY_NAME['client']['display_id'][0],
                        'value': b'random_stuff_2',
                    },
                    {
                        'id': 3,
                        'type': ATTRIBUTES_BY_NAME['client']['services'][0],
                        'value': b'|test|',
                    },
                ]),
                client_by_params_table.insert().values({
                    'approval_status': 0,
                    'display_id': b'random_stuff_2',
                    'id': 3,
                    'is_yandex': 0,
                    'services': b'|test|',
                    'uid': 3,
                }),
                client_by_uid_table.insert().values({
                    'id': 3,
                    'uid': 3,
                }),
            ],
        )
        self.fake_db.check('oauthdbcentral', 'client_attributes', 'uid', b'3', id=3)
        self.fake_db.check('oauthdbcentral', 'client_attributes', 'secret', b'non-secret', id=3)
        self.fake_db.check('oauthdbcentral', 'client_attributes', 'scope_ids', b'|3|4|', id=3)
        self.fake_db.check_missing('oauthdbcentral', 'client_attributes', 'is_blocked', id=3)

        self.fake_db.check('oauthdbcentral', 'client_by_uid', 'id', 3, uid=3)

        self.fake_db.check('oauthdbcentral', 'auto_id_client', 'id', 3, id=3)

    def test_update(self):
        with UPDATE(self.client) as client:
            client.secret = None
            client.scope_ids = [2, 3]
            client.is_blocked = True

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)

        self.eq_queries(
            self.fake_db.get_transaction_queries('oauthdbcentral'),
            [
                insert_on_duplicate_update(client_attributes_table, ['value']).values([
                    {
                        'id': 1,
                        'type': ATTRIBUTES_BY_NAME['client']['scope_ids'][0],
                        'value': b'|2|3|',
                    },
                    {
                        'id': 1,
                        'type': ATTRIBUTES_BY_NAME['client']['is_blocked'][0],
                        'value': b'1',
                    },
                ]),
                client_attributes_table.delete().where(and_(
                    client_attributes_table.c.id == 1,
                    client_attributes_table.c.type == ATTRIBUTES_BY_NAME['client']['secret'][0],
                )),
            ],
        )
        self.fake_db.check('oauthdbcentral', 'client_attributes', 'uid', b'1', id=1)
        self.fake_db.check_missing('oauthdbcentral', 'client_attributes', 'secret', id=1)
        self.fake_db.check('oauthdbcentral', 'client_attributes', 'scope_ids', b'|2|3|', id=1)
        self.fake_db.check('oauthdbcentral', 'client_attributes', 'is_blocked', b'1', id=1)

        self.fake_db.check('oauthdbcentral', 'client_by_uid', 'id', 1, uid=1)

    def test_update_with_empty_values(self):
        with UPDATE(self.client) as client:
            client.secret = ''
            client.is_blocked = False

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)

        self.fake_db.check_missing('oauthdbcentral', 'client_attributes', 'secret', id=1)
        self.fake_db.check_missing('oauthdbcentral', 'client_attributes', 'is_blocked', id=1)

    def test_update_with_nullable_fields(self):
        with UPDATE(self.client) as client:
            client.owner_uids = [1]

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)

        self.eq_queries(
            self.fake_db.get_transaction_queries('oauthdbcentral'),
            [
                insert_on_duplicate_update(client_attributes_table, ['value']).values([
                    {
                        'id': 1,
                        'type': ATTRIBUTES_BY_NAME['client']['owner_uids'][0],
                        'value': b'|1|',
                    },
                ]),
                client_by_owner_table.insert().values({
                    'id': 1,
                    'owner_groups': b'||',
                    'owner_uids': b'|1|',
                    'uids': b'|fake_value|',
                }),
            ],
        )

    def test_update_nothing_changed(self):
        with UPDATE(self.client):
            pass

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 0)

        self.fake_db.check('oauthdbcentral', 'client_attributes', 'secret', b'secret', id=1)
        self.fake_db.check_missing('oauthdbcentral', 'client_attributes', 'is_blocked', id=1)

        self.fake_db.check('oauthdbcentral', 'client_by_uid', 'id', 1, uid=1)

    def test_update_index_changed(self):
        with UPDATE(self.client) as client:
            client.uid = 2

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)

        self.eq_queries(
            self.fake_db.get_transaction_queries('oauthdbcentral'),
            [
                insert_on_duplicate_update(client_attributes_table, ['value']).values([
                    {
                        'id': 1,
                        'type': ATTRIBUTES_BY_NAME['client']['uid'][0],
                        'value': b'2',
                    },
                ]),
                client_by_params_table.update().where(and_(
                    client_by_params_table.c.approval_status == 0,
                    client_by_params_table.c.display_id == b'random_stuff',
                    client_by_params_table.c.id == 1,
                    client_by_params_table.c.is_yandex == 0,
                    client_by_params_table.c.services == b'|test|',
                    client_by_params_table.c.uid == 1,
                )).values({
                    'approval_status': 0,
                    'display_id': b'random_stuff',
                    'id': 1,
                    'is_yandex': 0,
                    'services': b'|test|',
                    'uid': 2,
                }),
                client_by_uid_table.update().where(and_(
                    client_by_uid_table.c.id == 1,
                    client_by_uid_table.c.uid == 1,
                )).values({
                    'id': 1,
                    'uid': 2,
                }),
            ],
        )
        self.fake_db.check('oauthdbcentral', 'client_attributes', 'uid', b'2', id=1)
        self.fake_db.check('oauthdbcentral', 'client_attributes', 'secret', b'secret', id=1)

        self.fake_db.check('oauthdbcentral', 'client_by_uid', 'id', 1, uid=2)
        self.fake_db.check_missing('oauthdbcentral', 'client_by_uid', uid=1)

    def test_delete(self):
        with DELETE(self.client):
            pass

        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.query_count('oauthdbcentral'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)

        self.eq_queries(
            self.fake_db.get_transaction_queries('oauthdbcentral'),
            [
                client_attributes_table.delete().where(
                    client_attributes_table.c.id == 1,
                ),
                client_by_params_table.delete().where(and_(
                    client_by_params_table.c.approval_status == 0,
                    client_by_params_table.c.display_id == b'random_stuff',
                    client_by_params_table.c.id == 1,
                    client_by_params_table.c.is_yandex == 0,
                    client_by_params_table.c.services == b'|test|',
                    client_by_params_table.c.uid == 1,
                )),
                client_by_uid_table.delete().where(and_(
                    client_by_uid_table.c.id == 1,
                    client_by_uid_table.c.uid == 1,
                )),
            ],
        )

        self.fake_db.check_missing('oauthdbcentral', 'client_attributes', 'uid', id=1)
        self.fake_db.check_missing('oauthdbcentral', 'client_attributes', 'secret', id=1)
        self.fake_db.check_missing('oauthdbcentral', 'client_attributes', 'scope_ids', id=1)
        self.fake_db.check_missing('oauthdbcentral', 'client_attributes', 'is_blocked', id=1)

        self.fake_db.check_missing('oauthdbcentral', 'client_by_uid', 'id', uid=1)
