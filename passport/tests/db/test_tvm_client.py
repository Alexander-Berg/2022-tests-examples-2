# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

from django.test.utils import override_settings
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.oauth.core.db.eav import (
    CREATE,
    DELETE,
    EntityNotFoundError,
    UPDATE,
)
from passport.backend.oauth.core.test.base_test_data import TEST_CIPHER_KEYS
from passport.backend.oauth.core.test.framework.testcases import DBTestCase
from passport.backend.oauth.tvm_api.tvm_api.db.tvm_client import TVMClient
from passport.backend.oauth.tvm_api.tvm_api.db.tvm_secret_key import TVMSecretKey


TEST_UID = 1
TEST_OTHER_UID = 2


@override_settings(ATTRIBUTE_CIPHER_KEYS=TEST_CIPHER_KEYS)
class TestTVMClient(DBTestCase):
    def setUp(self):
        super(TestTVMClient, self).setUp()
        with CREATE(TVMClient.create(
            creator_uid=TEST_UID,
            name='Test client',
        )) as client:
            client.add_new_secret_key()
            self.test_tvm_client = client

    def test_can_be_edited(self):
        ok_(self.test_tvm_client.can_be_edited(uid=TEST_UID))
        ok_(not self.test_tvm_client.can_be_edited(uid=TEST_OTHER_UID))

    def test_secret(self):
        secret = self.test_tvm_client.client_secret

        with UPDATE(self.test_tvm_client) as client:
            client.generate_client_secret()

        new_secret = self.test_tvm_client.client_secret
        ok_(new_secret != secret)

        client = TVMClient.by_id(self.test_tvm_client.id)
        eq_(client.old_client_secret, secret)
        eq_(client.client_secret, new_secret)

        with UPDATE(self.test_tvm_client) as client:
            client.restore_old_client_secret()

        client = TVMClient.by_id(self.test_tvm_client.id)
        eq_(client.old_client_secret, new_secret)
        eq_(client.client_secret, secret)

    @raises(ValueError)
    def test_unable_to_restore_old_secret(self):
        self.test_tvm_client.restore_old_client_secret()

    def test_generate_key(self):
        eq_(list(self.test_tvm_client.secret_keys.keys()), [1])

        with UPDATE(self.test_tvm_client) as client:
            client.add_new_secret_key()

        client = TVMClient.by_id(self.test_tvm_client.id)
        eq_(list(client.secret_keys.keys()), [1, 2])

        key = TVMSecretKey.by_id(2)
        eq_(key.created, DatetimeNow())

    def test_invalidate_key(self):
        with UPDATE(self.test_tvm_client) as client:
            client.delete_secret_key(1)

        client = TVMClient.by_id(self.test_tvm_client.id)
        ok_(not client.secret_keys)

        with assert_raises(EntityNotFoundError):
            TVMSecretKey.by_id(1)

    def test_deleted(self):
        with UPDATE(self.test_tvm_client) as client:
            client.deleted = datetime.now() - timedelta(seconds=10)
        with assert_raises(EntityNotFoundError):
            TVMClient.by_id(self.test_tvm_client.id)
        ok_(TVMClient.by_id(self.test_tvm_client.id, allow_deleted=True))

    def test_corrupt_secret_key(self):
        with UPDATE(self.test_tvm_client) as client:
            client.add_new_secret_key()

        # Имитируем нарушение целостности: удаление ключа из БД без удаления из списка ключей приложения
        deleted_key = self.test_tvm_client.secret_keys[2]
        with DELETE(deleted_key):
            pass

        client = TVMClient.by_id(self.test_tvm_client.id)
        eq_(client.secret_key_ids, [1, 2])
        eq_(list(client.secret_keys.keys()), [1])

        with UPDATE(self.test_tvm_client) as client:
            client.delete_secret_key(2)

        client = TVMClient.by_id(self.test_tvm_client.id)
        eq_(client.secret_key_ids, [1])
        eq_(list(client.secret_keys.keys()), [1])
