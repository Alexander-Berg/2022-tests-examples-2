# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

from django.test.utils import override_settings
import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.oauth.core.db.eav import (
    CREATE,
    EntityNotFoundError,
)
from passport.backend.oauth.core.test.base_test_data import TEST_CIPHER_KEYS
from passport.backend.oauth.core.test.framework.testcases import DBTestCase
from passport.backend.oauth.tvm_api.tvm_api.db.tvm_secret_key import (
    TVMSecretKey,
    TVMSecretKeyGenerationError,
)
from passport.backend.oauth.tvm_api.tvm_keygen import parse_key


@override_settings(ATTRIBUTE_CIPHER_KEYS=TEST_CIPHER_KEYS)
class TestTVMSecretKey(DBTestCase):
    def test_ok(self):
        with CREATE(TVMSecretKey.create()) as key:
            pass

        key = TVMSecretKey.by_id(key.id)
        eq_(key.created, DatetimeNow())

        size = len(key.private_secret)
        assert 1575 <= size <= 1600, size
        size = len(key.public_secret)
        assert 350 <= size <= 400, size

        parse_key(key.public_secret, key.private_secret)

    def test_fail(self):
        with mock.patch('passport.backend.oauth.tvm_api.tvm_api.db.tvm_secret_key.generate_rw_keys',
                        side_effect=RuntimeError):
            with assert_raises(TVMSecretKeyGenerationError):
                TVMSecretKey.create()

    def test_deleted(self):
        with CREATE(TVMSecretKey.create()) as key:
            key.deleted = datetime.now() - timedelta(seconds=10)
        with assert_raises(EntityNotFoundError):
            TVMSecretKey.by_id(key.id)
        ok_(TVMSecretKey.by_id(key.id, allow_deleted=True))
