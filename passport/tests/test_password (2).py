# -*- coding: utf-8 -*-

from datetime import datetime
import unittest

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_PWDHISTORY_REASON_COMPROMISED,
    BLACKBOX_PWDHISTORY_REASON_STRONG_POLICY,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    FakeBlackbox,
)
from passport.backend.core.db.faker.db import attribute_table_insert_on_duplicate_update_key as at_insert_odk
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import (
    attributes_table as at,
    password_history_eav_table as pht,
)
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE as AT
from passport.backend.core.models.account import Account
from passport.backend.core.models.password import (
    Password,
    PASSWORD_CHANGING_REASON_PWNED,
    ScholarPassword,
)
from passport.backend.core.serializers.eav.password import (
    PasswordEavSerializer,
    ScholarPasswordEavSerializer,
)
from passport.backend.core.test.consts import TEST_UID
from passport.backend.core.test.data import (
    TEST_PASSWORD,
    TEST_PASSWORD_HASH,
    TEST_PASSWORD_HASH_MD5_CRYPT_ARGON,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.undefined import Undefined
from passport.backend.utils.string import smart_bytes
from passport.backend.utils.time import datetime_to_unixtime
from sqlalchemy.sql.expression import and_


def serialize_dt(dt):
    return str(int(datetime_to_unixtime(dt))).encode('utf8')


@with_settings_hosts(
    BLACKBOX_URL='http://blackbox/',
)
class BasePasswordTestCase(PassportTestCase):
    def setUp(self):
        super(BasePasswordTestCase, self).setUp()

        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))

        self.blackbox = FakeBlackbox()

        self.__patches = [
            self.fake_tvm_credentials_manager,
            self.blackbox,
        ]
        for patch in self.__patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()

        del self.blackbox
        del self.fake_tvm_credentials_manager

        super(BasePasswordTestCase, self).tearDown()


class TestCreatePassword(BasePasswordTestCase):
    def test_empty(self):
        acc = Account(uid=123)
        pas = Password(acc)

        queries = PasswordEavSerializer().serialize(None, pas, diff(None, pas))
        eq_eav_queries(queries, [])

    def test_set_password(self):
        acc = Account(uid=123).parse({'login': 'login'})
        pas = Password(acc)
        pas.set(TEST_PASSWORD.password, TEST_PASSWORD.quality, TEST_PASSWORD.salt)

        queries = list(PasswordEavSerializer().serialize(None, pas, diff(None, pas)))

        eq_(pas.update_datetime, DatetimeNow())
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.encrypted'], 'value': smart_bytes('1:%s' % TEST_PASSWORD.encrypted)},
                    {'uid': 123, 'type': AT['password.quality'], 'value': smart_bytes('3:%s' % TEST_PASSWORD.quality)},
                    {'uid': 123, 'type': AT['password.update_datetime'], 'value':serialize_dt(pas.update_datetime)},
                ]),
            ],
        )

    def test_set_password_with_blackbox_hashing_with_uid_available(self):
        self.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash='1:%s' % TEST_PASSWORD.encrypted),
        )

        acc = Account(uid=123).parse({'login': 'login'})
        pas = Password(acc)
        pas.set(
            TEST_PASSWORD.password,
            TEST_PASSWORD.quality,
            salt=TEST_PASSWORD.salt,
            get_hash_from_blackbox=True,
        )

        # UID доступен, поэтому вызов происходит сразу при установке пароля
        self.blackbox.requests[0].assert_post_data_contains(
            {
                'method': 'create_pwd_hash',
                'password': TEST_PASSWORD.password,
                'ver': '1',
                'uid': '123',
            },
        )

        queries = list(PasswordEavSerializer().serialize(None, pas, diff(None, pas)))

        eq_(pas.update_datetime, DatetimeNow())
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.encrypted'], 'value': smart_bytes('1:%s' % TEST_PASSWORD.encrypted)},
                    {'uid': 123, 'type': AT['password.quality'], 'value': smart_bytes('3:%s' % TEST_PASSWORD.quality)},
                    {'uid': 123, 'type': AT['password.update_datetime'], 'value': serialize_dt(pas.update_datetime)},
                ]),
            ],
        )

        eq_(len(self.blackbox.requests), 1)

    def test_set_password_with_blackbox_hashing_without_uid(self):
        self.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash='6:%s' % TEST_PASSWORD_HASH_MD5_CRYPT_ARGON),
        )

        acc = Account().parse({'login': 'login'})
        pas = Password(acc)
        pas.set(
            TEST_PASSWORD.password,
            TEST_PASSWORD.quality,
            get_hash_from_blackbox=True,
            version=6,
        )

        # UID недоступен при установке, ЧЯ не вызывается
        eq_(len(self.blackbox.requests), 0)

        # Эмулируем побочный эффект вызова сериализатора аккаунта
        acc.uid = 123

        queries = list(PasswordEavSerializer().serialize(None, pas, diff(None, pas)))

        eq_(pas.update_datetime, DatetimeNow())
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.encrypted'], 'value': smart_bytes('6:%s' % TEST_PASSWORD_HASH_MD5_CRYPT_ARGON)},
                    {'uid': 123, 'type': AT['password.quality'], 'value': smart_bytes('3:%s' % TEST_PASSWORD.quality)},
                    {'uid': 123, 'type': AT['password.update_datetime'], 'value': serialize_dt(pas.update_datetime)},
                ]),
            ],
        )

        self.blackbox.requests[0].assert_post_data_contains(
            {
                'method': 'create_pwd_hash',
                'password': TEST_PASSWORD.password,
                'ver': '6',
                'uid': '123',
            },
        )

    def test_quality(self):
        acc = Account(uid=123)
        pas = Password(acc)
        pas.quality = 10
        pas.quality_version = 3

        queries = PasswordEavSerializer().serialize(None, pas, diff(None, pas))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.quality'], 'value': b'3:10'},
                ]),
            ],
        )

    def test_set_password_changing_requirement(self):
        acc = Account(uid=123)
        pas = Password(acc)
        pas.setup_password_changing_requirement(changing_reason='1234')

        queries = PasswordEavSerializer().serialize(None, pas, diff(None, pas))

        eq_(pas.forced_changing_time, DatetimeNow())
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.forced_changing_reason'], 'value': b'1234'},
                    {'uid': 123, 'type': AT['password.forced_changing_time'], 'value': serialize_dt(pas.forced_changing_time)},
                ]),
            ],
        )

    def test_clear_password_changing_requirement(self):
        acc = Account(uid=123)
        pas = Password(acc)
        pas.setup_password_changing_requirement(is_required=False)

        queries = PasswordEavSerializer().serialize(None, pas, diff(None, pas))

        eq_eav_queries(queries, [])

    def test_all_fields(self):
        acc = Account(uid=123)
        pas = Password(
            acc,
            encrypted_password='$1$salt$test',
            encoding_version=1,
            quality=10,
            quality_version=3,
            update_datetime=datetime.fromtimestamp(100),
            pwn_forced_changing_suspended_at=datetime.fromtimestamp(100),
        )
        pas.setup_password_changing_requirement()

        queries = list(PasswordEavSerializer().serialize(None, pas, diff(None, pas)))

        eq_(pas.update_datetime, datetime.fromtimestamp(100))
        eq_(pas.forced_changing_time, DatetimeNow())
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.encrypted'], 'value': b'1:$1$salt$test'},
                    {'uid': 123, 'type': AT['password.quality'], 'value': b'3:10'},
                    {'uid': 123, 'type': AT['password.forced_changing_reason'], 'value': b'1'},
                    {'uid': 123, 'type': AT['password.forced_changing_time'], 'value': serialize_dt(pas.forced_changing_time)},
                    {'uid': 123, 'type': AT['password.pwn_forced_changing_suspended_at'], 'value': b'100'},
                    {'uid': 123, 'type': AT['password.update_datetime'], 'value': b'100'},
                ]),
            ],
        )

    def test_all_fields_with_different_encoding_version(self):
        acc = Account(uid=123)
        pas = Password(
            acc,
            encrypted_password=TEST_PASSWORD_HASH,
            encoding_version=1000,
            update_datetime=datetime.fromtimestamp(100),
        )

        queries = list(PasswordEavSerializer().serialize(None, pas, diff(None, pas)))

        eq_(pas.update_datetime, datetime.fromtimestamp(100))
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.encrypted'], 'value': smart_bytes('1000:%s' % TEST_PASSWORD_HASH)},
                    {'uid': 123, 'type': AT['password.update_datetime'], 'value': b'100'},
                ]),
            ],
        )

    def test_all_fields_with_strong_policy(self):
        acc = Account(uid=123).parse({
            'subscriptions': {
                67: {'sid': 67},
            },
        })
        pas = Password(
            acc,
            encrypted_password='$1$salt$test',
            encoding_version=1,
            quality=10,
            quality_version=3,
            update_datetime=datetime.fromtimestamp(100),
        )
        pas.setup_password_changing_requirement()

        queries = list(PasswordEavSerializer().serialize(None, pas, diff(None, pas)))

        eq_(pas.update_datetime, datetime.fromtimestamp(100))
        eq_(pas.forced_changing_time, DatetimeNow())
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.encrypted'], 'value': b'1:$1$salt$test'},
                    {'uid': 123, 'type': AT['password.quality'], 'value': b'3:10'},
                    {'uid': 123, 'type': AT['password.forced_changing_reason'], 'value': b'1'},
                    {'uid': 123, 'type': AT['password.forced_changing_time'], 'value': serialize_dt(pas.forced_changing_time)},
                    {'uid': 123, 'type': AT['password.update_datetime'], 'value': b'100'},
                ]),
            ],
        )


class TestChangePassword(BasePasswordTestCase):
    def build_password(self, account, encrypted_password='$1$salt$test',
                       quality=10, quality_version=3,
                       is_changing_required=False,
                       update_datetime=datetime.fromtimestamp(1000)):
        pas = Password(
            account,
            encrypted_password=encrypted_password,
            quality=quality,
            quality_version=quality_version,
            update_datetime=update_datetime,
        )
        if is_changing_required:
            pas.setup_password_changing_requirement()
        return pas

    def test_unchanged(self):
        acc = Account(uid=123)
        pas = self.build_password(acc)

        s1 = pas.snapshot()
        queries = PasswordEavSerializer().serialize(s1, pas, diff(s1, pas))
        eq_eav_queries(queries, [])

    def test_quality_change(self):
        acc = Account(uid=123)
        pas = self.build_password(acc, quality=10, quality_version=2)

        s1 = pas.snapshot()
        pas.quality = 15
        pas.quality_version = 3

        queries = PasswordEavSerializer().serialize(s1, pas, diff(s1, pas))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.quality'], 'value': b'3:15'},
                ]),
            ],
        )

    def test_error_invalid_attributes(self):
        acc = Account(uid=123)

        for invalid_value in ('Hello', None, Undefined, bool):
            with assert_raises(ValueError):
                pas = self.build_password(acc, quality=invalid_value, quality_version=3)
                PasswordEavSerializer().serialize(None, pas, diff(None, pas))

                pas = self.build_password(acc, quality=0, quality_version=invalid_value)
                PasswordEavSerializer().serialize(None, pas, diff(None, pas))

    def test_set_password_changing_requirement(self):
        acc = Account(uid=123)
        pas = self.build_password(acc)

        s1 = pas.snapshot()
        pas.setup_password_changing_requirement()

        queries = PasswordEavSerializer().serialize(s1, pas, diff(s1, pas))

        eq_(pas.forced_changing_time, DatetimeNow())
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.forced_changing_reason'], 'value': b'1'},
                    {'uid': 123, 'type': AT['password.forced_changing_time'], 'value': serialize_dt(pas.forced_changing_time)},
                ]),
            ],
        )

    def test_clear_password_changing_requirement(self):
        acc = Account(uid=123)
        pas = self.build_password(acc, is_changing_required=True)

        s1 = pas.snapshot()
        pas.setup_password_changing_requirement(is_required=False)

        queries = PasswordEavSerializer().serialize(s1, pas, diff(s1, pas))

        eq_eav_queries(
            queries,
            [
                at.delete().where(and_(at.c.uid == 123, at.c.type.in_([
                    AT['password.forced_changing_reason'],
                    AT['password.forced_changing_time'],
                ]))),
            ],
        )

    def test_clear_password_changing_requirement_with_suspend(self):
        acc = Account(uid=123)
        pas = Password(
            acc,
            forced_changing_time=datetime.fromtimestamp(1000),
            forced_changing_reason=PASSWORD_CHANGING_REASON_PWNED,
        )

        s1 = pas.snapshot()
        pas.setup_password_changing_requirement(is_required=False)

        queries = PasswordEavSerializer().serialize(s1, pas, diff(s1, pas))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {
                        'uid': 123,
                        'type': AT['password.pwn_forced_changing_suspended_at'],
                        'value': serialize_dt(pas.pwn_forced_changing_suspended_at),
                    },
                ]),
                at.delete().where(and_(at.c.uid == 123, at.c.type.in_([
                    AT['password.forced_changing_reason'],
                    AT['password.forced_changing_time'],
                ]))),
            ],
        )

    def test_change_all_fields(self):
        acc = Account(uid=123).parse({'login': 'login'})
        pas = self.build_password(
            acc,
            encrypted_password='$1$salt$test_old',
            quality=10,
            quality_version=2,
            update_datetime=datetime.fromtimestamp(1000),
        )
        s1 = pas.snapshot()

        pas.set(TEST_PASSWORD.password, TEST_PASSWORD.quality, TEST_PASSWORD.salt)
        pas.setup_password_changing_requirement()

        queries = list(PasswordEavSerializer().serialize(s1, pas, diff(s1, pas)))

        eq_(pas.update_datetime, DatetimeNow())
        eq_(pas.forced_changing_time, DatetimeNow())
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.encrypted'], 'value': smart_bytes('1:%s' % TEST_PASSWORD.encrypted)},
                    {'uid': 123, 'type': AT['password.forced_changing_reason'], 'value': b'1'},
                    {'uid': 123, 'type': AT['password.forced_changing_time'], 'value': serialize_dt(pas.forced_changing_time)},
                    {'uid': 123, 'type': AT['password.quality'], 'value': smart_bytes('3:%s' % TEST_PASSWORD.quality)},
                    {'uid': 123, 'type': AT['password.update_datetime'], 'value': serialize_dt(pas.update_datetime)},
                ]),
            ],
        )

    def test_change_all_field_except_password_without_history(self):
        acc = Account(uid=123).parse({
            'login': 'login',
            'subscriptions': {
                67: {'sid': 67},
            },
        })
        pas = self.build_password(acc)
        s1 = pas.snapshot()

        pas.setup_password_changing_requirement()
        pas.quality = 66
        pas.quality_version = 3
        pas.update_datetime = datetime.now()

        queries = list(PasswordEavSerializer().serialize(s1, pas, diff(s1, pas)))
        eq_(pas.update_datetime, DatetimeNow())
        eq_(pas.forced_changing_time, DatetimeNow())
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.forced_changing_reason'], 'value': b'1'},
                    {'uid': 123, 'type': AT['password.forced_changing_time'], 'value': serialize_dt(pas.forced_changing_time)},
                    {'uid': 123, 'type': AT['password.quality'], 'value': b'3:66'},
                    {'uid': 123, 'type': AT['password.update_datetime'], 'value': serialize_dt(pas.update_datetime)},
                ]),
            ],
        )

    def test_change_all_fields_with_strong_policy(self):
        acc = Account(uid=123).parse({
            'login': 'login',
            'subscriptions': {
                67: {'sid': 67},
            },
        })
        pas = Password(
            acc,
            encrypted_password='$1$salt$test_old',
            encoding_version=1,
            quality=10,
            quality_version=2,
            update_datetime=datetime.fromtimestamp(1000),
        )
        s1 = pas.snapshot()

        pas.set(TEST_PASSWORD.password, TEST_PASSWORD.quality, TEST_PASSWORD.salt)
        pas.setup_password_changing_requirement()

        queries = list(PasswordEavSerializer().serialize(s1, pas, diff(s1, pas)))

        eq_(pas.update_datetime, DatetimeNow())
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.encrypted'], 'value': smart_bytes('1:%s' % TEST_PASSWORD.encrypted)},
                    {'uid': 123, 'type': AT['password.forced_changing_reason'], 'value': b'1'},
                    {'uid': 123, 'type': AT['password.forced_changing_time'], 'value': serialize_dt(pas.forced_changing_time)},
                    {'uid': 123, 'type': AT['password.quality'], 'value': smart_bytes('3:%s' % TEST_PASSWORD.quality)},
                    {'uid': 123, 'type': AT['password.update_datetime'], 'value': serialize_dt(pas.update_datetime)},
                ]),
                pht.insert().values(
                    uid=123,
                    ts=pas.update_datetime,
                    reason=BLACKBOX_PWDHISTORY_REASON_STRONG_POLICY,
                    encrypted_password=b'1:$1$salt$test_old',
                ),
            ],
        )

    def test_change_all_fields_with_password_changing_required(self):
        acc = Account(uid=123)
        pas = Password(
            acc,
            encrypted_password='$1$salt$test_old',
            encoding_version=1,
            quality=10,
            quality_version=2,
            update_datetime=datetime.fromtimestamp(1000),
        )
        pas.setup_password_changing_requirement()
        s1 = pas.snapshot()

        pas.set(TEST_PASSWORD.password, TEST_PASSWORD.quality, TEST_PASSWORD.salt)
        pas.setup_password_changing_requirement(is_required=False)

        queries = list(PasswordEavSerializer().serialize(s1, pas, diff(s1, pas)))

        eq_(pas.update_datetime, DatetimeNow())
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.encrypted'], 'value': smart_bytes('1:%s' % TEST_PASSWORD.encrypted)},
                    {'uid': 123, 'type': AT['password.quality'], 'value': smart_bytes('3:%s' % TEST_PASSWORD.quality)},
                    {'uid': 123, 'type': AT['password.update_datetime'], 'value': serialize_dt(pas.update_datetime)},
                ]),
                at.delete().where(and_(at.c.uid == 123, at.c.type.in_([
                    AT['password.forced_changing_reason'],
                    AT['password.forced_changing_time'],
                ]))),
                pht.insert().values(
                    uid=123,
                    ts=pas.update_datetime,
                    reason=BLACKBOX_PWDHISTORY_REASON_COMPROMISED,
                    encrypted_password=b'1:$1$salt$test_old',
                ),
            ],
        )

    def test_change_all_fields_with_password_changing_required_and_strong_policy(self):
        """При одновременном наличии требования сильного пароля и принудительной смены, в историю паролей
        пишем флаг принудительной смены"""
        acc = Account(uid=123).parse({
            'subscriptions': {
                67: {'sid': 67},
            },
        })
        pas = Password(
            acc,
            encrypted_password='$1$salt$test_old',
            encoding_version=1,
            quality=10,
            quality_version=2,
            update_datetime=datetime.fromtimestamp(1000),
        )
        pas.setup_password_changing_requirement()
        s1 = pas.snapshot()

        pas.set(TEST_PASSWORD.password, TEST_PASSWORD.quality, TEST_PASSWORD.salt)
        pas.setup_password_changing_requirement(is_required=False)

        queries = list(PasswordEavSerializer().serialize(s1, pas, diff(s1, pas)))

        eq_(pas.update_datetime, DatetimeNow())
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.encrypted'], 'value': smart_bytes('1:%s' % TEST_PASSWORD.encrypted)},
                    {'uid': 123, 'type': AT['password.quality'], 'value': smart_bytes('3:%s' % TEST_PASSWORD.quality)},
                    {'uid': 123, 'type': AT['password.update_datetime'], 'value': serialize_dt(pas.update_datetime)},
                ]),
                at.delete().where(and_(at.c.uid == 123, at.c.type.in_([
                    AT['password.forced_changing_reason'],
                    AT['password.forced_changing_time'],
                ]))),
                pht.insert().values(
                    uid=123,
                    ts=pas.update_datetime,
                    reason=BLACKBOX_PWDHISTORY_REASON_COMPROMISED,
                    encrypted_password=b'1:$1$salt$test_old',
                ),
            ],
        )

    def test_change_all_fields_with_different_encoding_and_password_changing_required_and_strong_policy(self):
        """При одновременном наличии требования сильного пароля и принудительной смены, в историю паролей
        пишем флаг принудительной смены; версия кодирования нового пароля отлична от стандартной"""
        acc = Account(uid=123).parse({
            'subscriptions': {
                67: {'sid': 67},
            },
        })
        pas = Password(
            acc,
            encrypted_password='$1$salt$test_old',
            encoding_version=1,
            quality=10,
            quality_version=2,
            update_datetime=datetime.fromtimestamp(1000),
        )
        pas.setup_password_changing_requirement()
        s1 = pas.snapshot()

        pas.set_hash(TEST_PASSWORD_HASH, version=1000)
        pas.setup_password_changing_requirement(is_required=False)

        queries = list(PasswordEavSerializer().serialize(s1, pas, diff(s1, pas)))

        eq_(pas.update_datetime, DatetimeNow())
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.encrypted'], 'value': smart_bytes('1000:%s' % TEST_PASSWORD_HASH)},
                    {'uid': 123, 'type': AT['password.update_datetime'], 'value': serialize_dt(pas.update_datetime)},
                ]),
                at.delete().where(and_(at.c.uid == 123, at.c.type.in_([
                    AT['password.forced_changing_reason'],
                    AT['password.forced_changing_time'],
                ]))),
                pht.insert().values(
                    uid=123,
                    ts=pas.update_datetime,
                    reason=BLACKBOX_PWDHISTORY_REASON_COMPROMISED,
                    encrypted_password=b'1:$1$salt$test_old',
                ),
            ],
        )

    def test_change_only_password_with_blackbox_hashing(self):
        self.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash='5:newhash'),
        )

        acc = Account(uid=123)
        pas = self.build_password(acc)

        s1 = pas.snapshot()

        pas.set(
            'newpassword',
            TEST_PASSWORD.quality,
            get_hash_from_blackbox=True,
            version=5,
        )

        self.blackbox.requests[0].assert_post_data_contains(
            {
                'method': 'create_pwd_hash',
                'password': 'newpassword',
                'ver': '5',
                'uid': '123',
            },
        )

        queries = list(PasswordEavSerializer().serialize(s1, pas, diff(s1, pas)))

        eq_(pas.update_datetime, DatetimeNow())
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.encrypted'], 'value': b'5:newhash'},
                    {'uid': 123, 'type': AT['password.quality'], 'value': smart_bytes('3:%s' % TEST_PASSWORD.quality)},
                    {'uid': 123, 'type': AT['password.update_datetime'], 'value': serialize_dt(pas.update_datetime)},
                ]),
            ],
        )

    def test_change_all_fields_with_blackbox_hashing(self):
        self.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash='5:newhash'),
        )

        acc = Account(uid=123)
        pas = Password(
            acc,
            encrypted_password='$1$salt$test_old',
            encoding_version=1,
            quality=10,
            quality_version=2,
            update_datetime=datetime.fromtimestamp(1000),
        )
        pas.setup_password_changing_requirement()
        s1 = pas.snapshot()

        pas.set(
            'newpassword',
            TEST_PASSWORD.quality,
            get_hash_from_blackbox=True,
            version=5,
        )
        pas.setup_password_changing_requirement(is_required=False)

        self.blackbox.requests[0].assert_post_data_contains(
            {
                'method': 'create_pwd_hash',
                'password': 'newpassword',
                'ver': '5',
                'uid': '123',
            },
        )

        queries = list(PasswordEavSerializer().serialize(s1, pas, diff(s1, pas)))

        eq_(pas.update_datetime, DatetimeNow())
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['password.encrypted'], 'value': b'5:newhash'},
                    {'uid': 123, 'type': AT['password.quality'], 'value': smart_bytes('3:%s' % TEST_PASSWORD.quality)},
                    {'uid': 123, 'type': AT['password.update_datetime'], 'value': serialize_dt(pas.update_datetime)},
                ]),
                at.delete().where(and_(at.c.uid == 123, at.c.type.in_([
                    AT['password.forced_changing_reason'],
                    AT['password.forced_changing_time'],
                ]))),
                pht.insert().values(
                    uid=123,
                    ts=pas.update_datetime,
                    reason=BLACKBOX_PWDHISTORY_REASON_COMPROMISED,
                    encrypted_password=b'1:$1$salt$test_old',
                ),
            ],
        )


class TestDeletePassword(unittest.TestCase):
    def test_delete(self):
        acc = Account(uid=123)
        pas = Password(acc)

        s1 = pas.snapshot()
        queries = PasswordEavSerializer().serialize(s1, None, diff(s1, None))
        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == 123,
                        at.c.type.in_(
                            sorted([
                                AT['password.forced_changing_reason'],
                                AT['password.forced_changing_time'],
                                AT['password.pwn_forced_changing_suspended_at'],
                                AT['password.encrypted'],
                                AT['password.update_datetime'],
                                AT['password.quality'],
                            ]),
                        ),
                    ),
                ),
            ],
        )

    def test_strong_policy_delete(self):
        acc = Account(uid=123).parse({
            'subscriptions': {
                67: {'sid': 67},
            },
        })
        pas = Password(
            acc,
            encrypted_password='$1$salt$test_old',
            encoding_version=1,
            update_datetime=datetime.fromtimestamp(1000),
        )

        s1 = pas.snapshot()
        queries = PasswordEavSerializer().serialize(s1, None, diff(s1, None))
        eq_eav_queries(
            queries,
            [
                pht.insert().values(
                    uid=123,
                    ts=pas.update_datetime,
                    reason=BLACKBOX_PWDHISTORY_REASON_STRONG_POLICY,
                    encrypted_password=b'1:$1$salt$test_old',
                ),
                at.delete().where(
                    and_(
                        at.c.uid == 123,
                        at.c.type.in_(
                            sorted([
                                AT['password.forced_changing_reason'],
                                AT['password.forced_changing_time'],
                                AT['password.pwn_forced_changing_suspended_at'],
                                AT['password.quality'],
                                AT['password.encrypted'],
                                AT['password.update_datetime'],
                            ]),
                        ),
                    ),
                ),
            ],
        )


class TestScholarPassword(BasePasswordTestCase):
    def setUp(self):
        super(TestScholarPassword, self).setUp()
        self.account = Account(uid=TEST_UID)
        self.password = self.build_password()

        self.blackbox = FakeBlackbox()
        self.blackbox.start()

    def tearDown(self):
        self.blackbox.stop()
        super(TestScholarPassword, self).tearDown()

    def build_password(self):
        return ScholarPassword(
            encoding_version='1',
            encrypted_password='pwd',
            parent=self.account,
        )

    def serialize(self, old, new):
        return ScholarPasswordEavSerializer().serialize(old, new, diff(old, new))

    def test_create(self):
        eq_eav_queries(
            self.serialize(None, self.password),
            [
                at_insert_odk().values([dict(type=AT['account.scholar_password'], uid=TEST_UID, value=b'1:pwd')]),
            ],
        )

    def test_create_account(self):
        # В момент создания аккаунт UID неизвестен, поэтому вычисление хеша
        # пароля происходить в момент сериализации.
        self.account.uid = Undefined

        self.blackbox.set_response_side_effect(
            'create_pwd_hash',
            [
                blackbox_create_pwd_hash_response(password_hash='1:pwd'),
            ],
        )

        password = self.account.scholar_password = ScholarPassword(parent=self.account)
        password.set('pwd', get_hash_from_blackbox=True)

        assert password.encoding_version is Undefined
        assert password.encrypted_password is Undefined

        self.account.uid = TEST_UID

        eq_eav_queries(
            self.serialize(None, password),
            [
                at_insert_odk().values([dict(type=AT['account.scholar_password'], uid=TEST_UID, value=b'1:pwd')]),
            ],
        )

        assert password.encoding_version == 1
        assert password.encrypted_password == 'pwd'

    def test_change(self):
        new = self.password.snapshot()
        new.encrypted_password = 'pwd1'

        eq_eav_queries(
            self.serialize(self.password, new),
            [
                at_insert_odk().values([dict(type=AT['account.scholar_password'], uid=TEST_UID, value=b'1:pwd1')]),
            ],
        )

        new = self.password.snapshot()
        new.encoding_version = '2'

        eq_eav_queries(
            self.serialize(self.password, new),
            [
                at_insert_odk().values([dict(type=AT['account.scholar_password'], uid=TEST_UID, value=b'2:pwd')]),
            ],
        )

    def test_delete(self):
        eq_eav_queries(
            self.serialize(self.password, None),
            [
                at.delete().where(and_(at.c.uid == TEST_UID, at.c.type.in_([AT['account.scholar_password']]))),
            ],
        )
