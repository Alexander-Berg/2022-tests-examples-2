# -*- coding: utf-8 -*-

import abc
from datetime import datetime
from time import time
from unittest import TestCase

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from nose_parameterized import parameterized
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_PWDHISTORY_REASON_COMPROMISED,
    BLACKBOX_PWDHISTORY_REASON_STRONG_POLICY,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    FakeBlackbox,
)
from passport.backend.core.db import schemas
from passport.backend.core.db.faker.db import (
    aliases_insert,
    attribute_table_insert_on_duplicate_update_key as at_insert_odk,
    extended_attribute_table_insert_on_duplicate_key as eat_insert_odk,
    FakeDB,
    IdGeneratorFaker,
    insert_ignore_into_removed_aliases,
    passman_recovery_key_insert,
    pdduid_table_insert,
    transaction,
    uid_table_insert,
)
from passport.backend.core.db.faker.db_utils import (
    compile_query_with_dialect,
    eq_eav_queries,
)
from passport.backend.core.db.schemas import (
    account_deletion_operations_table as adot,
    aliases_table as alt,
    attributes_table as at,
    email_bindings_table as ebt,
    extended_attributes_table as eat,
    family_members_table,
    passman_recovery_keys_table as prkt,
    password_history_eav_table as pht,
    phone_bindings_table as phone_bindings,
    phone_operations_table as phone_operations,
    reserved_logins_table as rlt,
    suid2_table,
    webauthn_credentials_table as wct,
)
from passport.backend.core.db.utils import insert_with_on_duplicate_key_update
from passport.backend.core.dbmanager.manager import safe_execute_queries
from passport.backend.core.dbmanager.sharder import get_db_name
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import (
    ALIAS_NAME_TO_TYPE as ALT,
    ATTRIBUTE_NAME_TO_TYPE as AT,
    EXTENDED_ATTRIBUTES_EMAIL_TYPE,
    EXTENDED_ATTRIBUTES_PHONE_NAME_TO_TYPE_MAPPING,
    EXTENDED_ATTRIBUTES_PHONE_TYPE,
    EXTENDED_ATTRIBUTES_WEBAUTHN_NAME_TO_TYPE_MAPPING,
    EXTENDED_ATTRIBUTES_WEBAUTHN_TYPE,
)
from passport.backend.core.env import Environment
from passport.backend.core.models.account import (
    Account,
    ACCOUNT_DISABLED,
    ACCOUNT_DISABLED_ON_DELETION,
    ACCOUNT_ENABLED,
    AccountDeletionOperation,
    MAIL_STATUS_ACTIVE,
    MAIL_STATUS_FROZEN,
    MAIL_STATUS_NONE,
    UnsubscriptionList,
)
from passport.backend.core.models.alias import (
    AltDomainAlias,
    PhonenumberAlias,
)
from passport.backend.core.models.domain import PartialPddDomain
from passport.backend.core.models.email import (
    Email,
    Emails,
)
from passport.backend.core.models.faker.account import default_account
from passport.backend.core.models.hint import Hint
from passport.backend.core.models.karma import Karma
from passport.backend.core.models.passman_recovery_key import PassManRecoveryKey
from passport.backend.core.models.person import Person
from passport.backend.core.models.phones.phones import (
    Operation as PhoneOperation,
    Phones,
)
from passport.backend.core.models.subscription import (
    subscribe,
    Subscription,
)
from passport.backend.core.models.webauthn import (
    WebauthnCredential,
    WebauthnCredentials,
)
from passport.backend.core.serializers.eav.account import (
    account_registration_datetime_processor,
    AccountEavSerializer,
)
from passport.backend.core.serializers.eav.query import EavInsertPasswordHistoryQuery
from passport.backend.core.services import Service
from passport.backend.core.test.consts import (
    TEST_BIRTHDATE1,
    TEST_CITY1,
    TEST_COUNTRY_CODE1,
    TEST_DATETIME1,
    TEST_DATETIME2,
    TEST_DEFAULT_AVATAR1,
    TEST_DISPLAY_NAME1,
    TEST_EMAIL1,
    TEST_EMAIL_ID1,
    TEST_FIRSTNAME1,
    TEST_LASTNAME1,
    TEST_LOGIN1,
    TEST_PDD_UID1,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER1,
    TEST_PHONE_OPERATION_ID1,
    TEST_PLUS_SUBSCRIBER_STATE1_BASE64,
    TEST_PLUS_SUBSCRIBER_STATE1_JSON,
    TEST_PLUS_SUBSCRIBER_STATE1_PROTO,
    TEST_TIMEZONE1,
    TEST_UID,
)
from passport.backend.core.test.data import TEST_PASSWORD
from passport.backend.core.test.test_utils import (
    settings_context,
    with_settings,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
    unixtime,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.types.account.account import KINOPOISK_UID_BOUNDARY
from passport.backend.core.types.gender import Gender
from passport.backend.core.types.question import Question
from passport.backend.core.types.totp_secret import TotpSecretType
from passport.backend.core.undefined import Undefined
from passport.backend.utils.string import smart_bytes
from passport.backend.utils.time import (
    datetime_to_unixtime,
    get_unixtime,
    unixtime_to_datetime,
)
from sqlalchemy.dialects import mysql
from sqlalchemy.schema import Table
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import (
    and_,
    or_,
)

from .test_query import (
    TEST_PASSMAN_KEY_ID,
    TEST_PASSMAN_RECOVERY_KEY,
)


TEST_KINOPOISK_ID = 1
TEST_KINOPOISK_UID = KINOPOISK_UID_BOUNDARY + TEST_KINOPOISK_ID

TEST_UBER_ID = '11'

TEST_PHONE_ATTR_CREATED = 1234567892
TEST_PHONE_ATTR_BOUND = 1234567893
TEST_PHONE_ATTR_CONFIRMED = 1234567894
TEST_PHONE_ATTR_ADMITTED = 1234567895
TEST_PHONE_ATTR_SECURED = 1234567896
TEST_PHONE_ATTR_BOUND2 = 9876543213

TEST_PHONE_ATTR_BOUND_DT = unixtime_to_datetime(TEST_PHONE_ATTR_BOUND)
TEST_PHONE_ATTR_BOUND2_DT = unixtime_to_datetime(TEST_PHONE_ATTR_BOUND2)

TEST_NEW_SECURED_DT = datetime(2000, 1, 2, 1, 2, 3)
TEST_NEW_SECURED = int(datetime_to_unixtime(TEST_NEW_SECURED_DT))

TEST_STARTED_DT = datetime(2000, 1, 22, 12, 34, 56)
TEST_STARTED_UT = int(datetime_to_unixtime(TEST_STARTED_DT))

TEST_PHONE_OPERATION = {
    'id': 1,
    'type': 'bind',
    'password_verified': unixtime(2000, 1, 23, 12, 34, 56),
    'started': unixtime(2000, 1, 22, 12, 34, 56),
}

TEST_PHONE_DICT = {
    'id': TEST_PHONE_ID1,
    'attributes': {
        'number': TEST_PHONE_NUMBER1.e164,
        'created': TEST_PHONE_ATTR_CREATED,
        'bound': TEST_PHONE_ATTR_BOUND,
        'confirmed': TEST_PHONE_ATTR_CONFIRMED,
        'admitted': TEST_PHONE_ATTR_ADMITTED,
        'secured': TEST_PHONE_ATTR_SECURED,
    },
    'binding': {
        'uid': TEST_UID,
        'type': 'current',
        'phone_number': TEST_PHONE_NUMBER1,
        'phone_id': TEST_PHONE_ID1,
        'binding_time': TEST_PHONE_ATTR_BOUND,
        'should_ignore_binding_limit': 0,
    },
    'operation': TEST_PHONE_OPERATION,
}


class TestCreateAccount(TestCase):
    def test_account_create(self):
        acc = default_account().parse({
            'person.firstname': 'fname',
            'person.firstname_global': 'fname',
            'subscriptions': {24: {'host_id': 1, 'sid': 24}},
            'userinfo.reg_date.uid': datetime.now(),
        })
        acc.global_logout_datetime = datetime.now()
        acc.password.set(TEST_PASSWORD.password, TEST_PASSWORD.quality, TEST_PASSWORD.salt)
        acc.person.contact_phone_number = '9261234567'
        acc.person.default_avatar = 'ava'
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))

        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                # subscriptions
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['subscription.24'], 'value': b'1'},
                ]),
                # contact_phone_number
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['person.contact_phone_number'], 'value': b'9261234567'},
                ]),
                # account
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['account.registration_datetime'], 'value': TimeNow()},
                    {'uid': TEST_UID, 'type': AT['account.global_logout_datetime'], 'value': TimeNow()},
                ]),
                # password
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['password.encrypted'], 'value': smart_bytes('1:%s' % TEST_PASSWORD.encrypted)},
                    {'uid': TEST_UID, 'type': AT['password.quality'], 'value': smart_bytes('3:%s' % TEST_PASSWORD.quality)},
                    {'uid': TEST_UID, 'type': AT['password.update_datetime'], 'value': TimeNow()},
                ]),
                # person
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['person.firstname'], 'value': b'fname'},
                    {'uid': TEST_UID, 'type': AT['person.firstname_global'], 'value': b'fname'},
                    {'uid': TEST_UID, 'type': AT['avatar.default'], 'value': b'ava'},
                ]),
                # portal alias
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['portal'],
                    value=b'login',
                    surrogate_type=str(ALT['portal']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_with_blackbox_password_hash(self):
        acc = default_account().parse({
            'person.firstname': 'fname',
            'subscriptions': {
                24: {'host_id': 1, 'sid': 24},
                8: {'login_rule': 2, 'sid': 8, 'login': 'login'},
            },
            'userinfo.reg_date.uid': datetime.now(),
        })
        acc.global_logout_datetime = datetime.now()

        with settings_context(BLACKBOX_URL='http://bb'), FakeBlackbox() as blackbox, FakeTvmCredentialsManager() as tvm:
            tvm.set_data(fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'blackbox',
                        'ticket': TEST_TICKET,
                    },
                },
            ))
            blackbox.set_blackbox_response_value(
                'create_pwd_hash',
                blackbox_create_pwd_hash_response(password_hash='5:%s' % 'newhash'),
            )
            acc.password.set(TEST_PASSWORD.password, TEST_PASSWORD.quality, version=5, get_hash_from_blackbox=True)
            acc.person.contact_phone_number = '9261234567'
            acc.person.default_avatar = 'ava'
            queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))

            eq_eav_queries(
                queries,
                [
                    uid_table_insert(),
                    # subscriptions
                    at_insert_odk().values([
                        {'uid': TEST_UID, 'type': AT['subscription.24'], 'value': b'1'},
                    ]),
                    # contact_phone_number
                    at_insert_odk().values([
                        {'uid': TEST_UID, 'type': AT['person.contact_phone_number'], 'value': b'9261234567'},
                    ]),
                    # account
                    at_insert_odk().values([
                        {'uid': TEST_UID, 'type': AT['account.registration_datetime'], 'value': TimeNow()},
                        {'uid': TEST_UID, 'type': AT['account.global_logout_datetime'], 'value': TimeNow()},
                    ]),
                    # password
                    at_insert_odk().values([
                        {'uid': TEST_UID, 'type': AT['password.encrypted'], 'value': b'5:newhash'},
                        {'uid': TEST_UID, 'type': AT['password.quality'], 'value': smart_bytes('3:%s' % TEST_PASSWORD.quality)},
                        {'uid': TEST_UID, 'type': AT['password.update_datetime'], 'value': TimeNow()},
                    ]),
                    # person
                    at_insert_odk().values([
                        {'uid': TEST_UID, 'type': AT['person.firstname'], 'value': b'fname'},
                        {'uid': TEST_UID, 'type': AT['avatar.default'], 'value': b'ava'},
                    ]),
                    # portal alias
                    aliases_insert().values(
                        uid=TEST_UID,
                        type=ALT['portal'],
                        value=b'login',
                        surrogate_type=str(ALT['portal']).encode('utf8'),
                    ),
                ],
                inserted_keys=[TEST_UID],
            )
            eq_(len(blackbox.requests), 1)

    def test_account_create_with_password_to_history(self):
        acc = default_account().parse({
            'subscriptions': {67: {'sid': 67}},
            'userinfo.reg_date.uid': datetime.now(),
        })
        acc.password.set(TEST_PASSWORD.password, TEST_PASSWORD.quality, TEST_PASSWORD.salt)

        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))

        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                # password
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['password.is_strong_policy_enabled'], 'value': b'1'},
                ]),
                # account
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['account.registration_datetime'], 'value': TimeNow()},
                ]),
                # password
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['password.encrypted'], 'value': smart_bytes('1:%s' % TEST_PASSWORD.encrypted)},
                    {'uid': TEST_UID, 'type': AT['password.quality'], 'value': smart_bytes('3:%s' % TEST_PASSWORD.quality)},
                    {'uid': TEST_UID, 'type': AT['password.update_datetime'], 'value': TimeNow()},
                ]),
                # portal alias
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['portal'],
                    value=b'login',
                    surrogate_type=str(ALT['portal']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_with_karma(self):
        acc = default_account()
        acc.registration_datetime = datetime.now()
        acc.karma = Karma(parent=acc, prefix=2, suffix=20, activation_datetime=datetime.now())

        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))

        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                # account
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['account.registration_datetime'], 'value': TimeNow()},
                ]),
                # karma
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['karma.value'], 'value': b'2020'},
                    {'uid': TEST_UID, 'type': AT['karma.activation_datetime'], 'value': TimeNow()},
                ]),
                # portal alias
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['portal'],
                    value=b'login',
                    surrogate_type=str(ALT['portal']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_login_normalization(self):
        acc = Account(uid=TEST_UID).parse({'userinfo.reg_date.uid': datetime.now()})
        acc.set_portal_alias('un.normalized.login')

        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))

        eq_eav_queries(queries, [
            # account
            at_insert_odk().values([
                {'uid': TEST_UID, 'type': AT['account.registration_datetime'], 'value': TimeNow()},
                {'uid': TEST_UID, 'type': AT['account.user_defined_login'], 'value': b'un.normalized.login'},
            ]),
            # portal alias
            aliases_insert().values(
                uid=TEST_UID,
                type=ALT['portal'],
                value=b'un-normalized-login',
                surrogate_type=str(ALT['portal']).encode('utf8'),
            ),
        ])

    def test_account_create_with_password_and_hint(self):
        acc = default_account().parse({
            'userinfo_safe.hintq.uid': u'99:Тестовый вопрос',
            'userinfo_safe.hinta.uid': u'Ответ',
        })
        acc.password.set(TEST_PASSWORD.password, TEST_PASSWORD.quality, TEST_PASSWORD.salt)
        acc.hint = Hint(acc, answer=u'Ответ', question=Question(u'Тестовый вопрос', 99))

        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))

        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                # hint
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['hint.question.serialized'], 'value': u'99:Тестовый вопрос'.encode('utf-8')},
                    {'uid': TEST_UID, 'type': AT['hint.answer.encrypted'], 'value': u'Ответ'.encode('utf-8')},
                ]),
                # password
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['password.encrypted'], 'value': smart_bytes('1:%s' % TEST_PASSWORD.encrypted)},
                    {'uid': TEST_UID, 'type': AT['password.quality'], 'value': smart_bytes('3:%s' % TEST_PASSWORD.quality)},
                    {'uid': TEST_UID, 'type': AT['password.update_datetime'], 'value': TimeNow()},
                ]),
                # portal alias
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['portal'],
                    value=b'login',
                    surrogate_type=str(ALT['portal']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_with_hint(self):
        acc = default_account()
        acc.hint = Hint(acc, answer=u'Ответ', question=Question(u'Тестовый вопрос', 99))

        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))

        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                # hint
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['hint.question.serialized'], 'value': u'99:Тестовый вопрос'.encode('utf-8')},
                    {'uid': TEST_UID, 'type': AT['hint.answer.encrypted'], 'value': u'Ответ'.encode('utf-8')},
                ]),
                # portal alias
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['portal'],
                    value=b'login',
                    surrogate_type=str(ALT['portal']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_without_password_and_hint(self):
        acc = default_account()
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))

        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['portal'],
                    value=b'login',
                    surrogate_type=str(ALT['portal']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_pdd(self):
        acc = default_account(alias='login@okna.ru', alias_type='pdd')
        acc.domain = PartialPddDomain(id=1, domain='okna.ru')
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))

        eq_eav_queries(
            queries,
            [
                pdduid_table_insert(),
                aliases_insert().values(
                    uid=TEST_PDD_UID1,
                    type=ALT['pdd'],
                    value=b'1/login',
                    surrogate_type=str(ALT['pdd']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_PDD_UID1],
        )

    def test_account_create_pdd_with_unnormalized_login_and_domain(self):
        acc = default_account(alias='Login@Okna.ru', alias_type='pdd')
        acc.domain = PartialPddDomain(id=1, domain='okna.RU')
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))

        eq_eav_queries(
            queries,
            [
                pdduid_table_insert(),
                at_insert_odk().values([
                    {'uid': TEST_PDD_UID1, 'type': AT['account.user_defined_login'], 'value': b'Login'},
                ]),
                aliases_insert().values(
                    uid=TEST_PDD_UID1,
                    type=ALT['pdd'],
                    value=b'1/login',
                    surrogate_type=str(ALT['pdd']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_PDD_UID1],
        )

    @raises(ValueError)
    def test_account_create_pdd_with_no_domain_fails(self):
        acc = default_account(alias='login@okna.ru', alias_type='pdd')
        list(AccountEavSerializer().serialize(None, acc, diff(None, acc)))

    @raises(ValueError)
    def test_account_create_pdd_with_no_domain_id_fails(self):
        acc = default_account(alias='login@okna.ru', alias_type='pdd')
        acc.domain = PartialPddDomain()
        list(AccountEavSerializer().serialize(None, acc, diff(None, acc)))

    @raises(ValueError)
    def test_account_create_pdd_with_bad_domain_fails(self):
        acc = default_account(alias='login@okna.ru', alias_type='pdd')
        acc.domain = PartialPddDomain(id=1, domain='dveri.com')
        list(AccountEavSerializer().serialize(None, acc, diff(None, acc)))

    def test_account_create_lite(self):
        acc = default_account(alias='username@okna.ru', alias_type='lite')
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                # lite alias
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['lite'],
                    value=b'username@okna.ru',
                    surrogate_type=str(ALT['lite']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_social(self):
        acc = default_account(alias='uid-login', alias_type='social')
        ok_(acc.is_social)
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                # social alias
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['social'],
                    value=b'uid-login',
                    surrogate_type=str(ALT['social']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_phonish(self):
        acc = default_account(alias='phne-login', alias_type='phonish')
        ok_(acc.is_phonish)
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                # phonish alias
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['phonish'],
                    value=b'phne-login',
                    surrogate_type=str(ALT['phonish']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_phonish_with_namespace(self):
        acc = default_account(alias='phne-login', alias_type='phonish')
        acc.phonish_namespace = 'rutaxi'
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['account.phonish_namespace'], 'value': b'rutaxi'},
                ]),
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['phonish'],
                    value=b'phne-login',
                    surrogate_type=str(ALT['phonish']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_neophonish(self):
        acc = default_account(alias='nphne-login', alias_type='neophonish')
        ok_(acc.is_neophonish)
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                # neophonish alias
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['neophonish'],
                    value=b'nphne-login',
                    surrogate_type=str(ALT['neophonish']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_mailish(self):
        acc = default_account(alias=u'вася@пупкин.рф', alias_type='mailish')
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                # mailish alias
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['mailish'],
                    value=u'вася@пупкин.рф'.encode('utf-8'),
                    surrogate_type=str(ALT['mailish']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_kinopoisk(self):
        acc = default_account(
            alias=str(TEST_KINOPOISK_ID),
            alias_type='kinopoisk',
            uid=TEST_KINOPOISK_UID,
        ).parse({})
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                # kinopoisk alias
                aliases_insert().values(
                    uid=TEST_KINOPOISK_UID,
                    type=ALT['kinopoisk'],
                    value=str(TEST_KINOPOISK_ID).encode('utf8'),
                    surrogate_type=str(ALT['kinopoisk']).encode('utf8'),
                ),
            ],
        )

    def test_account_create_uber(self):
        acc = default_account(
            alias=str(TEST_UBER_ID),
            alias_type='uber',
        )
        ok_(acc.is_uber)
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['uber'],
                    value=str(TEST_UBER_ID).encode('utf8'),
                    surrogate_type=str(ALT['uber']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_uber_not_normalized(self):
        acc = default_account(
            alias='11.11',
            alias_type='uber',
        )
        ok_(acc.is_uber)
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['uber'],
                    value=b'11.11',
                    surrogate_type=str(ALT['uber']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    @raises(ValueError)
    def test_account_create_uber_mixed_case(self):
        acc = default_account(
            alias='6HMjGgBfsUnVI2vz7R9AwQB7vb9Z55c0laYsDHzp',
            alias_type='uber',
        )
        ok_(acc.is_uber)
        list(AccountEavSerializer().serialize(None, acc, diff(None, acc)))

    def test_account_create_yambot(self):
        acc = default_account(
            alias='yambot-bot',
            alias_type='yambot',
        )
        ok_(acc.is_yambot)
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['yambot'],
                    value=b'yambot-bot',
                    surrogate_type=str(ALT['yambot']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_kolonkish(self):
        acc = default_account(
            alias='kolonkish-123',
            alias_type='kolonkish',
            creator_uid=TEST_UID * 2,
        )
        ok_(acc.is_kolonkish)
        eq_(acc.creator_uid, TEST_UID * 2)
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['account.creator_uid'], 'value': smart_bytes(TEST_UID * 2)},
                ]),
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['kolonkish'],
                    value=b'kolonkish-123',
                    surrogate_type=str(ALT['kolonkish']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_scholar(self):
        acc = default_account(alias='вовочка', alias_type='scholar')
        ok_(acc.is_scholar)
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['scholar'],
                    value=u'вовочка'.encode('utf-8'),
                    surrogate_type=str(ALT['scholar']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_federal(self):
        acc = default_account(alias='1/login', alias_type='federal')
        ok_(acc.is_federal)
        acc.domain = PartialPddDomain(id=1, domain='some-domain.com')
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                pdduid_table_insert(),
                aliases_insert().values(
                    uid=TEST_PDD_UID1,
                    type=ALT['federal'],
                    value=b'1/login',
                    surrogate_type=str(ALT['federal']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_PDD_UID1],
        )

    def test_account_create_with_public_id(self):
        acc = default_account().parse({
            'aliases': {str(ALT['public_id']): 'public_id-123'},
            'account.user_defined_public_id': 'PublicId',
        })
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['account.user_defined_public_id'], 'value': b'PublicId'},
                ]),
                # portal alias
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['portal'],
                    value=b'login',
                    surrogate_type=str(ALT['portal']).encode('utf8'),
                ),
                # public_id
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['public_id'],
                    value=b'public_id-123',
                    surrogate_type=str(ALT['public_id']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_with_phonenumber_alias(self):
        acc = default_account().parse({
            'aliases': {str(ALT['phonenumber']): '79096841646'},
            'account.enable_search_by_phone_alias': '1',
        })
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                # portal alias
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['portal'],
                    value=b'login',
                    surrogate_type=str(ALT['portal']).encode('utf8'),
                ),
                # создаем телефонный алиас
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['account.enable_search_by_phone_alias'], 'value': b'1'},
                ]),
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['phonenumber'],
                    value=b'79096841646',
                    surrogate_type=str(ALT['phonenumber']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_with_altdomain_alias(self):
        acc = default_account().parse({'aliases': {str(ALT['altdomain']): 'login@galatasaray.net'}})
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                # portal alias
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['portal'],
                    value=b'login',
                    surrogate_type=str(ALT['portal']).encode('utf8'),
                ),
                # создаем алиас
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['altdomain'],
                    value=b'1/login',
                    surrogate_type=str(ALT['altdomain']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_with_default_email(self):
        acc = default_account().parse({'default_email': u'василий@пупкин.рф'})
        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                uid_table_insert(),
                # default_email
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['account.default_email'], 'value': u'василий@пупкин.рф'.encode('utf-8')},
                ]),
                # portal alias
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['portal'],
                    value=b'login',
                    surrogate_type=str(ALT['portal']).encode('utf8'),
                ),
            ],
            inserted_keys=[TEST_UID],
        )

    def test_account_create_browser_key(self):
        acc = default_account(uid=TEST_UID)
        s1 = acc.snapshot()
        acc.browser_key.set('key')

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([{'uid': TEST_UID, 'type': AT['account.browser_key'], 'value': b'key'}]),
            ],
        )

    @parameterized.expand([
        ('1,2,3', {1, 2, 3}, False),
        ('all', None, True),
    ])
    def test_account_create_unsubscriptions_list(self, value, expected_set, expected_all):
        acc = default_account(uid=TEST_UID).parse(
            {'account.unsubscribed_from_maillists': value},
        )

        self.assertEqual(acc.unsubscribed_from_maillists.values, expected_set)
        self.assertEqual(acc.unsubscribed_from_maillists.all, expected_all)

        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values(
                    [{'uid': TEST_UID, 'type': AT['account.unsubscribed_from_maillists'], 'value': value.encode('utf8')}],
                ),
                aliases_insert().values(
                    uid=TEST_UID,
                    type=ALT['portal'],
                    value=b'login',
                    surrogate_type=str(ALT['portal']).encode('utf8'),
                ),
            ],
        )

    @parameterized.expand(
        [
            ('audience_on', 'account.audience_on', True),
            ('audience_on', 'account.audience_on', False),
            ('is_shared', 'account.is_shared', True),
            ('is_shared', 'account.is_shared', False),
            ('account.magic_link_login_forbidden', 'account.magic_link_login_forbidden', True),
            ('account.magic_link_login_forbidden', 'account.magic_link_login_forbidden', False),
            ('account.qr_code_login_forbidden', 'account.qr_code_login_forbidden', True),
            ('account.qr_code_login_forbidden', 'account.qr_code_login_forbidden', False),
            ('account.sms_code_login_forbidden', 'account.sms_code_login_forbidden', True),
            ('account.sms_code_login_forbidden', 'account.sms_code_login_forbidden', False),
            ('takeout.subscription', 'takeout.subscription', True),
            ('takeout.subscription', 'takeout.subscription', False),
            ('account.is_connect_admin', 'account.is_connect_admin', True),
            ('account.is_connect_admin', 'account.is_connect_admin', False),
            ('account.is_money_agreement_accepted', 'account.is_money_agreement_accepted', True),
            ('account.is_money_agreement_accepted', 'account.is_money_agreement_accepted', False),
            ('account.is_easily_hacked', 'account.is_easily_hacked', True),
            ('account.is_easily_hacked', 'account.is_easily_hacked', False),
            ('is_employee', 'account.is_employee', True),
            ('is_employee', 'account.is_employee', False),
            ('is_maillist', 'account.is_maillist', True),
            ('is_maillist', 'account.is_maillist', False),
            ('enable_app_password', 'account.enable_app_password', True),
            ('enable_app_password', 'account.enable_app_password', False),
            ('account.is_verified', 'account.is_verified', True),
            ('account.is_verified', 'account.is_verified', False),
            ('takeout.delete.subscription', 'takeout.delete.subscription', True),
            ('takeout.delete.subscription', 'takeout.delete.subscription', False),
        ],
    )
    def test_create_boolean_flag_attribute(self, model_field_name, blackbox_attribute_name, set_value):
        acc = default_account().parse({model_field_name: set_value})

        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        expected_queries = [uid_table_insert()]
        if set_value:
            expected_queries.append(
                at_insert_odk().values([{'uid': TEST_UID, 'type': AT[blackbox_attribute_name], 'value': b'1'}])
            )
        expected_queries.append(aliases_insert().values(
            uid=TEST_UID,
            type=ALT['portal'],
            value=b'login',
            surrogate_type=str(ALT['portal']).encode('utf8'),
        ))

        eq_eav_queries(
            queries,
            expected_queries,
            inserted_keys=[TEST_UID],
        )

    @parameterized.expand(
        [
            ('account.personal_data_public_access_allowed', 'account.personal_data_public_access_allowed', True),
            ('account.personal_data_public_access_allowed', 'account.personal_data_public_access_allowed', False),
            ('account.personal_data_third_party_processing_allowed', 'account.personal_data_third_party_processing_allowed', True),
            ('account.personal_data_third_party_processing_allowed', 'account.personal_data_third_party_processing_allowed', False),
        ],
    )
    def test_create_boolean_flag_attribute_with_both_values(self, model_field_name, blackbox_attribute_name, set_value):
        acc = default_account().parse({model_field_name: set_value})

        queries = AccountEavSerializer().serialize(None, acc, diff(None, acc))
        expected_queries = [uid_table_insert()]
        expected_queries.append(
            at_insert_odk().values([{'uid': TEST_UID, 'type': AT[blackbox_attribute_name], 'value': b'1' if set_value else b'0'}])
        )
        expected_queries.append(aliases_insert().values(
            uid=TEST_UID,
            type=ALT['portal'],
            value=b'login',
            surrogate_type=str(ALT['portal']).encode('utf8'),
        ))

        eq_eav_queries(
            queries,
            expected_queries,
            inserted_keys=[TEST_UID],
        )


class TestUpdateAccount(TestCase):
    def setUp(self):
        super(TestUpdateAccount, self).setUp()

        self.id_faker = IdGeneratorFaker()
        self.id_faker.set_list(range(1, 100))
        self.id_faker.start()

    def tearDown(self):
        self.id_faker.stop()

    def test_update_login_to_normal(self):
        acc = Account(uid=TEST_UID, is_enabled=True).parse({'aliases': {str(ALT['lite']): 'login@okna.ru'}})

        s1 = acc.snapshot()
        acc.set_portal_alias('login')

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(queries, [
            # delete user defined login
            at.delete().where(and_(
                at.c.uid == TEST_UID,
                at.c.type.in_([AT['account.user_defined_login']]),
            )),
            # portal alias
            aliases_insert().values(
                uid=TEST_UID,
                type=ALT['portal'],
                value=b'login',
                surrogate_type=str(ALT['portal']).encode('utf8'),
            ),
        ])

    def test_unset_ena_serialize(self):
        acc = default_account().parse({
            'uid': TEST_UID,
            'is_enabled': True,
        })

        s1 = acc.snapshot()
        acc.is_enabled = False

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(queries, [
            # account
            at_insert_odk().values([
                {'uid': TEST_UID, 'type': AT['account.is_disabled'], 'value': b'1'},
            ]),
        ])

    def test_set_ena_serialize(self):
        acc = default_account().parse({
            'uid': TEST_UID,
            'disabled_status': '1',
        })
        acc.domain = PartialPddDomain(id=1)

        s1 = acc.snapshot()
        acc.is_enabled = True

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(queries, [
            # account
            at.delete().where(and_(at.c.uid == TEST_UID, at.c.type.in_([AT['account.is_disabled']]))),
        ])

    def test_global_logout_datetime_serialize(self):
        acc = default_account(uid=TEST_UID)
        s1 = acc.snapshot()

        acc.global_logout_datetime = datetime.now()

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(queries, [
            # account
            at_insert_odk().values([
                {'uid': TEST_UID, 'type': AT['account.global_logout_datetime'], 'value': TimeNow()},
            ]),
        ])

    def test_unset_global_logout_datetime_serialize(self):
        acc = default_account(uid=TEST_UID)
        acc.global_logout_datetime = datetime.now()
        s1 = acc.snapshot()

        acc.global_logout_datetime = datetime.fromtimestamp(0)

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(queries, [
            # account
            at.delete().where(and_(at.c.uid == TEST_UID, at.c.type.in_([AT['account.global_logout_datetime']]))),
        ])

    def test_subscribe(self):
        acc = default_account().parse({
            'uid': TEST_UID,
            'subscriptions': {},
        })
        s1 = acc.snapshot()

        svc = Service.by_sid(76)
        acc.subscriptions[svc.sid] = Subscription(acc, service=svc)

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(queries, [
            at_insert_odk().values([{'uid': TEST_UID, 'type': AT['subscription.76'], 'value': b'1'}]),
        ])

    def test_unsubscribe(self):
        acc = default_account().parse({
            'uid': TEST_UID,
            'subscriptions': {76: {'sid': 76}},
        })
        s1 = acc.snapshot()

        del acc.subscriptions[76]
        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([AT['subscription.76']]),
                    ),
                ),
            ],
        )

    def test_karma_serialize(self):
        acc = default_account(uid=TEST_UID)
        acc.karma = Karma(parent=acc, prefix=1, suffix=10, activation_datetime=datetime.now())

        s1 = acc.snapshot()
        acc.is_enabled = False
        acc.karma.prefix = 3
        acc.karma.suffix = 30
        acc.karma.activation_datetime = datetime.now()

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(queries, [
            # account
            at_insert_odk().values([
                {'uid': TEST_UID, 'type': AT['account.is_disabled'], 'value': b'1'},
            ]),
            # karma
            at_insert_odk().values([
                {'uid': TEST_UID, 'type': AT['karma.activation_datetime'], 'value': TimeNow()},
                {'uid': TEST_UID, 'type': AT['karma.value'], 'value': b'3030'},
            ]),
        ])

    def test_zero_karma_serialize(self):
        acc = default_account(uid=TEST_UID)
        acc.karma = Karma(parent=acc, prefix=1, suffix=10)

        s1 = acc.snapshot()
        acc.is_enabled = False
        acc.karma.prefix = 0
        acc.karma.suffix = 0

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(queries, [
            # account
            at_insert_odk().values([
                {'uid': TEST_UID, 'type': AT['account.is_disabled'], 'value': b'1'},
            ]),
            # karma
            at.delete().where(and_(at.c.uid == TEST_UID, at.c.type.in_([AT['karma.value']]))),
        ])

    def test_unchanged_account_serialize(self):
        acc = default_account(uid=TEST_UID, is_enabled=True)

        s1 = acc.snapshot()
        acc.is_enabled = True

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(queries, [])

    def test_unchanged_account_model_attr_serialize(self):
        acc = default_account(uid=TEST_UID)

        s1 = acc.snapshot()

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(queries, [])

    def test_account_plus_enable(self):
        acc = default_account().parse({
            'uid': TEST_UID,
        })
        s1 = acc.snapshot()

        acc.plus.enabled = True
        acc.plus.subscription_stopped_ts = datetime.now()
        acc.plus.subscription_expire_ts = datetime.now()
        acc.plus.trial_used_ts = datetime.now()
        acc.plus.next_charge_ts = datetime.now()
        acc.plus.ott_subscription = 'ott-subscription'
        acc.plus.family_role = 'family-role'
        acc.plus.cashback_enabled = True
        acc.plus.subscriber_state = TEST_PLUS_SUBSCRIBER_STATE1_JSON

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['account.plus.enabled'], 'value': b'1'},
                    {'uid': TEST_UID, 'type': AT['account.plus.subscription_stopped_ts'], 'value': TimeNow()},
                    {'uid': TEST_UID, 'type': AT['account.plus.subscription_expire_ts'], 'value': TimeNow()},
                    {'uid': TEST_UID, 'type': AT['account.plus.trial_used_ts'], 'value': TimeNow()},
                    {'uid': TEST_UID, 'type': AT['account.plus.next_charge_ts'], 'value': TimeNow()},
                    {'uid': TEST_UID, 'type': AT['account.plus.ott_subscription'], 'value': b'ott-subscription'},
                    {'uid': TEST_UID, 'type': AT['account.plus.family_role'], 'value': b'family-role'},
                    {'uid': TEST_UID, 'type': AT['account.plus.cashback_enabled'], 'value': b'1'},
                    {'uid': TEST_UID, 'type': AT['account.plus.subscriber_state'], 'value': TEST_PLUS_SUBSCRIBER_STATE1_PROTO},
                ]),
            ],
        )

    def test_account_plus_subscriber_state_not_changed(self):
        acc = default_account().parse({
            'uid': TEST_UID,
        })

        acc.plus.enabled = True
        acc.plus.subscriber_state = TEST_PLUS_SUBSCRIBER_STATE1_JSON
        s1 = acc.snapshot()
        acc.plus.subscriber_state = TEST_PLUS_SUBSCRIBER_STATE1_JSON

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [],
        )

    def test_account_plus_subscriber_state_deleted(self):
        acc = default_account().parse({
            'uid': TEST_UID,
        })

        acc.plus.subscriber_state = TEST_PLUS_SUBSCRIBER_STATE1_JSON
        s1 = acc.snapshot()
        acc.plus.subscriber_state = ''

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([
                            AT['account.plus.subscriber_state'],
                        ]),
                        ),
                ),
            ],
        )

    def test_account_plus_empty_ott_subscription(self):
        acc = default_account().parse({
            'uid': TEST_UID,
            'account.plus.ott_subscription': 'ott-subscription',
        })
        eq_(acc.plus.ott_subscription, 'ott-subscription')

        s1 = acc.snapshot()

        acc.plus.ott_subscription = ''

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([
                            AT['account.plus.ott_subscription'],
                        ]),
                    ),
                ),
            ],
        )

    def test_account_plus_empty_family_role(self):
        acc = default_account().parse({
            'uid': TEST_UID,
            'account.plus.family_role': 'family-role',
        })
        eq_(acc.plus.family_role, 'family-role')

        s1 = acc.snapshot()

        acc.plus.family_role = ''

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([
                            AT['account.plus.family_role'],
                        ]),
                    ),
                ),
            ],
        )

    def test_account_plus_enable_zero_timestamp(self):
        acc = default_account().parse({
            'uid': TEST_UID,
        })
        s1 = acc.snapshot()

        acc.plus.enabled = True
        acc.plus.subscription_stopped_ts = datetime.fromtimestamp(0)
        acc.plus.subscription_expire_ts = datetime.fromtimestamp(0)
        acc.plus.trial_used_ts = datetime.fromtimestamp(0)
        acc.plus.next_charge_ts = datetime.fromtimestamp(0)

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['account.plus.enabled'], 'value': b'1'},
                ]),
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_(sorted([
                            AT['account.plus.subscription_stopped_ts'],
                            AT['account.plus.subscription_expire_ts'],
                            AT['account.plus.trial_used_ts'],
                            AT['account.plus.next_charge_ts'],
                        ])),
                    ),
                ),
            ],
        )

    def test_account_plus_disable(self):
        acc = default_account().parse({
            'uid': TEST_UID,
            'account.plus.enabled': True,
            'account.plus.subscription_stopped_ts': get_unixtime(),
            'account.plus.subscription_expire_ts': get_unixtime(),
            'account.plus.trial_used_ts': get_unixtime(),
            'account.plus.next_charge_ts': get_unixtime(),
            'account.plus.ott_subscription': 'ott-subscription',
            'account.plus.cashback_enabled': True,
            'account.plus.subscriber_state': TEST_PLUS_SUBSCRIBER_STATE1_BASE64,
        })
        s1 = acc.snapshot()

        eq_(s1.plus.enabled, True)
        eq_(s1.plus.subscription_stopped_ts, DatetimeNow())
        eq_(s1.plus.subscription_expire_ts, DatetimeNow())
        eq_(s1.plus.trial_used_ts, DatetimeNow())
        eq_(s1.plus.next_charge_ts, DatetimeNow())
        eq_(s1.plus.ott_subscription, 'ott-subscription')
        eq_(s1.plus.cashback_enabled, True)
        eq_(s1.plus.subscriber_state, TEST_PLUS_SUBSCRIBER_STATE1_JSON)

        acc.plus.enabled = False
        acc.plus.subscription_stopped_ts = None
        acc.plus.subscription_expire_ts = None
        acc.plus.trial_used_ts = None
        acc.plus.next_charge_ts = None
        acc.plus.ott_subscription = None
        acc.plus.subscriber_state = None

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_(sorted([
                            AT['account.plus.trial_used_ts'],
                            AT['account.plus.subscription_stopped_ts'],
                            AT['account.plus.ott_subscription'],
                            AT['account.plus.subscription_expire_ts'],
                            AT['account.plus.enabled'],
                            AT['account.plus.next_charge_ts'],
                            AT['account.plus.subscriber_state'],
                        ])),
                    ),
                ),
            ],
        )

    def test_account_plus_disable_cashback(self):
        acc = default_account().parse({
            'uid': TEST_UID,
            'account.plus.cashback_enabled': True,
        })
        s1 = acc.snapshot()

        eq_(s1.plus.cashback_enabled, True)

        acc.plus.cashback_enabled = False

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([
                            AT['account.plus.cashback_enabled'],
                        ]),
                    ),
                ),
            ],
        )

    def test_account_plus_freeze(self):
        acc = default_account().parse({
            'uid': TEST_UID,
        })
        s1 = acc.snapshot()

        acc.plus.is_frozen = True

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['account.plus.is_frozen'], 'value': b'1'},
                ]),
            ],
        )

    def test_account_plus_unfreeze(self):
        acc = default_account().parse(
            {'uid': TEST_UID, 'account.plus.is_frozen': True},
        )
        s1 = acc.snapshot()

        eq_(s1.plus.is_frozen, True)

        acc.plus.is_frozen = False

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([AT['account.plus.is_frozen']]),
                    ),
                ),
            ],
        )

    def test_account_plus_delete(self):
        acc = default_account().parse({
            'uid': TEST_UID,
            'account.plus.enabled': True,
            'account.plus.subscription_stopped_ts': get_unixtime(),
            'account.plus.subscription_expire_ts': get_unixtime(),
            'account.plus.trial_used_ts': get_unixtime(),
            'account.plus.next_charge_ts': get_unixtime(),
            'account.plus.ott_subscription': 'ott-subscription',
            'account.plus.family_role': 'family-role',
            'account.plus.cashback_enabled': True,
            'account.plus.subscription_level': 2,
            'account.plus.is_frozen': True,
            'account.plus.subscriber_state': TEST_PLUS_SUBSCRIBER_STATE1_JSON,
        })
        s1 = acc.snapshot()

        acc.plus = None

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_(sorted([
                            AT['account.plus.family_role'],
                            AT['account.plus.subscription_stopped_ts'],
                            AT['account.plus.enabled'],
                            AT['account.plus.subscription_expire_ts'],
                            AT['account.plus.trial_used_ts'],
                            AT['account.plus.next_charge_ts'],
                            AT['account.plus.ott_subscription'],
                            AT['account.plus.cashback_enabled'],
                            AT['account.plus.subscription_level'],
                            AT['account.plus.is_frozen'],
                            AT['account.plus.subscriber_state'],
                        ])),
                    ),
                ),
            ],
        )

    def test_account_add_phonenumber_alias(self):
        acc = default_account().parse({
            'uid': TEST_UID,
        })
        s1 = acc.snapshot()

        number = TEST_PHONE_NUMBER1
        acc.phonenumber_alias = PhonenumberAlias(parent=acc, number=number, enable_search=True)

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(queries, [
            # создаем телефонный алиас
            at_insert_odk().values([
                {'uid': TEST_UID, 'type': AT['account.enable_search_by_phone_alias'], 'value': b'1'},
            ]),
            aliases_insert().values(
                uid=TEST_UID,
                type=ALT['phonenumber'],
                value=TEST_PHONE_NUMBER1.digital.encode('utf8'),
                surrogate_type=str(ALT['phonenumber']).encode('utf8'),
            ),
        ])

    def test_account_add_altdomain_alias(self):
        acc = default_account().parse({
            'uid': TEST_UID,
        })
        s1 = acc.snapshot()

        acc.altdomain_alias = AltDomainAlias(parent=acc, login='login@galatasaray.net')

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(queries, [
            # создаем алиас
            aliases_insert().values(
                uid=TEST_UID,
                type=ALT['altdomain'],
                value=b'1/login',
                surrogate_type=str(ALT['altdomain']).encode('utf8'),
            ),
        ])

    def test_update_contact_phone_number(self):
        acc = default_account().parse({
            'uid': TEST_UID,
            'subscriptions': {89: {'sid': 89, 'login': '9261234567'}},
        })
        s1 = acc.snapshot()
        acc.person.contact_phone_number = '9260000000'
        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(queries, [
            at_insert_odk().values([{'uid': TEST_UID, 'type': AT['person.contact_phone_number'], 'value': b'9260000000'}]),
        ])

    def test_account_update_browser_key(self):
        acc = default_account(uid=TEST_UID).parse({
            'browser_key': 'key',
        })
        s1 = acc.snapshot()
        acc.browser_key.set('new key')

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(queries, [
            at_insert_odk().values([
                {
                    'uid': TEST_UID,
                    'type': AT['account.browser_key'],
                    'value': b'new key',
                },
            ]),
        ])

        s2 = acc.snapshot()
        acc.browser_key.set('another key')
        queries = AccountEavSerializer().serialize(s2, acc, diff(s2, acc))
        eq_eav_queries(queries, [
            at_insert_odk().values([
                {
                    'uid': TEST_UID,
                    'type': AT['account.browser_key'],
                    'value': b'another key',
                },
            ]),
        ])

    def test_change_passwd_and_update_datetime_serialize(self):
        acc = default_account(uid=TEST_UID).parse({
            'userinfo.reg_date.uid': datetime.now(),
            'password.encrypted': '1:secret',
        })
        s1 = acc.snapshot()

        acc.password.set(TEST_PASSWORD.password, TEST_PASSWORD.quality, TEST_PASSWORD.salt)

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(queries, [
            # password
            at_insert_odk().values([
                {'uid': TEST_UID, 'type': AT['password.encrypted'], 'value': smart_bytes('1:%s' % TEST_PASSWORD.encrypted)},
                {'uid': TEST_UID, 'type': AT['password.quality'], 'value': smart_bytes('3:%s' % TEST_PASSWORD.quality)},
                {'uid': TEST_UID, 'type': AT['password.update_datetime'], 'value': TimeNow()},
            ]),
        ])

    def test_change_passwd_and_update_datetime_serialize_with_blackbox_hash(self):
        acc = default_account(uid=TEST_UID).parse({
            'subscriptions': {
                8: {'login_rule': 2, 'sid': 8, 'login': 'login'},
            },
            'userinfo.reg_date.uid': datetime.now(),
        })
        s1 = acc.snapshot()

        with settings_context(BLACKBOX_URL='http://bb'), FakeBlackbox() as blackbox, FakeTvmCredentialsManager() as tvm:
            tvm.set_data(fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'blackbox',
                        'ticket': TEST_TICKET,
                    },
                },
            ))
            blackbox.set_blackbox_response_value(
                'create_pwd_hash',
                blackbox_create_pwd_hash_response(password_hash='5:%s' % 'newhash'),
            )

            acc.password.set(TEST_PASSWORD.password, TEST_PASSWORD.quality, get_hash_from_blackbox=True, version=5)

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(queries, [
            # password
            at_insert_odk().values([
                {'uid': TEST_UID, 'type': AT['password.encrypted'], 'value': b'5:newhash'},
                {'uid': TEST_UID, 'type': AT['password.quality'], 'value': smart_bytes('3:%s' % TEST_PASSWORD.quality)},
                {'uid': TEST_UID, 'type': AT['password.update_datetime'], 'value': TimeNow()},
            ]),
        ])

    def test_change_passwd_and_update_datetime_with_strong_policy_serialize(self):
        acc = default_account(uid=TEST_UID).parse({
            'subscriptions': {67: {'sid': 67}},
            'userinfo.reg_date.uid': datetime.now(),
            'password.encrypted': '1:secret',
        })
        s1 = acc.snapshot()

        acc.password.set(TEST_PASSWORD.password, TEST_PASSWORD.quality, TEST_PASSWORD.salt)

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(queries, [
            # password
            at_insert_odk().values([
                {'uid': TEST_UID, 'type': AT['password.encrypted'], 'value': smart_bytes('1:%s' % TEST_PASSWORD.encrypted)},
                {'uid': TEST_UID, 'type': AT['password.quality'], 'value': smart_bytes('3:%s' % TEST_PASSWORD.quality)},
                {'uid': TEST_UID, 'type': AT['password.update_datetime'], 'value': TimeNow()},
            ]),
            pht.insert().values(
                uid=TEST_UID,
                ts=acc.password.update_datetime,
                reason=BLACKBOX_PWDHISTORY_REASON_STRONG_POLICY,
                encrypted_password=b'1:secret',
            ),
        ])

    def test_change_passwd_and_update_datetime_with_is_changing_required_serialize(self):
        acc = default_account(uid=TEST_UID).parse({
            'password.forced_changing_reason': '1',
            'userinfo.reg_date.uid': datetime.now(),
            'password.encrypted': '1:secret',
        })
        s1 = acc.snapshot()

        acc.password.set(TEST_PASSWORD.password, TEST_PASSWORD.quality, TEST_PASSWORD.salt)
        acc.password.setup_password_changing_requirement(is_required=False)

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(queries, [
            at_insert_odk().values([
                {'uid': TEST_UID, 'type': AT['password.encrypted'], 'value': smart_bytes('1:%s' % TEST_PASSWORD.encrypted)},
                {'uid': TEST_UID, 'type': AT['password.quality'], 'value': smart_bytes('3:%s' % TEST_PASSWORD.quality)},
                {'uid': TEST_UID, 'type': AT['password.update_datetime'], 'value': TimeNow()},
            ]),
            at.delete().where(and_(at.c.uid == TEST_UID, at.c.type.in_([
                AT['password.forced_changing_reason'],
                AT['password.forced_changing_time'],
            ]))),
            pht.insert().values(
                uid=TEST_UID,
                ts=acc.password.update_datetime,
                reason=BLACKBOX_PWDHISTORY_REASON_COMPROMISED,
                encrypted_password=b'1:secret',
            ),
        ])

    def test_change_password_update_datetime_serialize(self):
        acc = default_account(uid=TEST_UID)
        s1 = acc.snapshot()

        acc.password.update_datetime = datetime.fromtimestamp(1000)

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(queries, [
            at_insert_odk().values([
                {'uid': TEST_UID, 'type': AT['password.update_datetime'], 'value': b'1000'},
            ]),
        ])

    def test_account_with_totp_secret_create(self):
        acc = default_account(uid=TEST_UID)
        s1 = acc.snapshot()
        acc.totp_secret.set(TotpSecretType('secret'))

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(queries, [
            at_insert_odk().values([
                {'uid': TEST_UID, 'type': AT['account.totp.secret'], 'value': b'secret'},
                {'uid': TEST_UID, 'type': AT['account.totp.update_datetime'], 'value': TimeNow()},
            ]),
        ])

    def test_account_with_totp_secret_delete(self):
        acc = default_account(uid=TEST_UID).parse({
            'password.update_datetime': 1000,
        })
        s1 = acc.snapshot()
        acc.totp_secret = None

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(queries, [
            at.delete().where(
                and_(
                    at.c.uid == TEST_UID,
                    at.c.type.in_([
                        AT['account.totp.secret'],
                        AT['account.totp.check_time'],
                        AT['account.totp.failed_pin_checks_count'],
                        AT['account.totp.update_datetime'],
                        AT['account.totp.yakey_device_ids'],
                    ]),
                ),
            ),
        ])

    def test_enable_app_password(self):
        SingleValueAttributeTest(
            account_field_name='enable_app_password',
            attribute_name='account.enable_app_password',
            attribute_type=UnaryAttributeValuespace(),
        ).run()

    def test_is_shared(self):
        SingleValueAttributeTest(
            account_field_name='is_shared',
            attribute_name='account.is_shared',
            attribute_type=UnaryAttributeValuespace(),
        ).run()

    def test_is_verified(self):
        SingleValueAttributeTest(
            account_field_name='is_verified',
            attribute_name='account.is_verified',
            attribute_type=UnaryAttributeValuespace(),
        ).run()

    def test_personal_data_third_party_processing_allowed(self):
        AttributeTest(
            account_field_name='personal_data_third_party_processing_allowed',
            attribute_name='account.personal_data_third_party_processing_allowed',
            attribute_type=BinaryAttributeValuespace(),
        ).run()

    def test_personal_data_public_access_allowed(self):
        AttributeTest(
            account_field_name='personal_data_public_access_allowed',
            attribute_name='account.personal_data_public_access_allowed',
            attribute_type=BinaryAttributeValuespace(),
        ).run()

    def test_is_connect_admin(self):
        SingleValueAttributeTest(
            account_field_name='is_connect_admin',
            attribute_name='account.is_connect_admin',
            attribute_type=UnaryAttributeValuespace(),
        ).run()

    def test_change_disabled_status(self):
        acc = default_account(uid=TEST_UID)
        acc.disabled_status = Undefined
        s1 = acc.snapshot()

        for status in [
            ACCOUNT_DISABLED,
            ACCOUNT_DISABLED_ON_DELETION,
        ]:
            acc.disabled_status = status
            queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
            eq_eav_queries(queries, [
                at_insert_odk().values([{
                    'uid': TEST_UID,
                    'type': AT['account.is_disabled'],
                    'value': smart_bytes(status),
                }]),
            ])

        # Так как значение ACCOUNT_ENABLED соответствует нулю, то мы не пишем
        # его в базу и вместо этого удаляем запись атрибута для этого UID'а.
        acc.disabled_status = ACCOUNT_ENABLED
        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([
                            AT['account.is_disabled'],
                        ]),
                    ),
                ),
            ],
        )

    def test_change_mail_status(self):
        acc = default_account(uid=TEST_UID)
        acc.mail_status = Undefined
        s1 = acc.snapshot()

        for status in [
            MAIL_STATUS_ACTIVE,
            MAIL_STATUS_FROZEN,
        ]:
            acc.mail_status = status
            queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
            eq_eav_queries(queries, [
                at_insert_odk().values([{
                    'uid': TEST_UID,
                    'type': AT['subscription.mail.status'],
                    'value': smart_bytes(status),
                }]),
            ])

        # Так как значение MAIL_STATUS_NONE соответствует нулю, то мы не пишем
        # его в базу и вместо этого удаляем запись атрибута для этого UID'а.
        acc.mail_status = MAIL_STATUS_NONE
        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([
                            AT['subscription.mail.status'],
                        ]),
                    ),
                ),
            ],
        )

    def test_is_auth_email_datetime(self):
        AttributeTest(
            account_field_name='auth_email_datetime',
            attribute_name='account.auth_email_datetime',
            attribute_type=DatetimeAttributeValuespace(),
        ).run()

    def test_change_failed_auth_challenge_checks_counter(self):
        with mock.patch('passport.backend.core.types.expirable_counter.expirable_counter.time') as time_mock:
            # изменяю время, чтобы быстро было понятно, отклеился мок или нет
            current_time = int(time() / 4)
            time_mock.return_value = current_time

            tm = int(current_time) + 100
            acc = default_account(uid=TEST_UID).parse({
                'failed_auth_challenge_checks_counter': '1:%s' % tm,
            })
            s1 = acc.snapshot()

            acc.failed_auth_challenge_checks_counter.incr(200)

            queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
            eq_eav_queries(queries, [
                at_insert_odk().values([{
                    'uid': TEST_UID,
                    'type': AT['account.failed_auth_challenge_checks_counter'],
                    'value': smart_bytes('2:%d' % (current_time + 200)),
                }]),
            ])

    def test_reset_failed_auth_challenge_checks_counter(self):
        tm = int(time()) + 100
        acc = default_account(uid=TEST_UID).parse({
            'failed_auth_challenge_checks_counter': '1:%s' % tm,
        })
        s1 = acc.snapshot()

        acc.failed_auth_challenge_checks_counter.reset()

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(queries, [
            at.delete().where(
                and_(
                    at.c.uid == TEST_UID,
                    at.c.type.in_([
                        AT['account.failed_auth_challenge_checks_counter'],
                    ]),
                ),
            ),
        ])

    def test_junk_secret(self):
        AttributeTest(
            account_field_name='totp_junk_secret',
            attribute_name='account.totp.junk_secret',
            attribute_type=StringAttributeValuespace(),
        ).run()

    def test_create_passman_recovery_key(self):
        acc = Account(uid=TEST_UID).parse({'login': 'login'})
        s1 = acc.snapshot()
        acc.passman_recovery_key = PassManRecoveryKey(
            acc,
            key_id=TEST_PASSMAN_KEY_ID,
            recovery_key=TEST_PASSMAN_RECOVERY_KEY,
        )

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [
                passman_recovery_key_insert().values(
                    [
                        {
                            'uid': TEST_UID,
                            'key_id': TEST_PASSMAN_KEY_ID,
                            'recovery_key': TEST_PASSMAN_RECOVERY_KEY,
                        },
                    ],
                ),
            ],
        )

    def test_add_webauthn_credential(self):
        acc = Account(uid=TEST_UID).parse({'login': 'login'})
        s1 = acc.snapshot()
        cred = WebauthnCredential(external_id='test-id')
        acc.webauthn_credentials.add(cred)

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [
                eat_insert_odk().values(
                    [
                        {
                            'uid': TEST_UID,
                            'entity_type': EXTENDED_ATTRIBUTES_WEBAUTHN_TYPE,
                            'entity_id': 1,
                            'type': EXTENDED_ATTRIBUTES_WEBAUTHN_NAME_TO_TYPE_MAPPING['external_id'],
                            'value': b'test-id',
                        },
                    ],
                ),
                wct.insert().values(uid=TEST_UID, credential_id=b'test-id'),
            ],
        )

    def test_additional_data_asked(self):
        AttributeTest(
            account_field_name='additional_data_asked',
            attribute_name='account.additional_data_asked',
            attribute_type=StringAttributeValuespace(),
        ).run()

    def test_additional_data_ask_next_datetime(self):
        AttributeTest(
            account_field_name='additional_data_ask_next_datetime',
            attribute_name='account.additional_data_ask_next_datetime',
            attribute_type=DatetimeAttributeValuespace(),
        ).run()

    def test_external_organization_ids_changed(self):
        acc = Account(uid=TEST_UID).parse({'login': 'login'})
        s1 = acc.snapshot()
        acc.external_organization_ids = [1, 3, 2]

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': TEST_UID, 'type': AT['account.external_organization_ids'], 'value': b'1,2,3'},
                ]),
            ],
        )

    def test_external_organization_ids_not_changed(self):
        acc = Account(uid=TEST_UID).parse({'login': 'login'})
        acc.external_organization_ids = {1, 2, 3}
        s1 = acc.snapshot()
        acc.external_organization_ids = [1, 3, 2]

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [],
        )

    def test_external_organization_ids_deleted(self):
        acc = Account(uid=TEST_UID).parse({'login': 'login'})
        acc.external_organization_ids = {1, 2, 3}
        s1 = acc.snapshot()
        acc.external_organization_ids = []

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([
                            AT['account.external_organization_ids'],
                        ]),
                    ),
                ),
            ],
        )

    def test_billing_features_changed(self):
        acc = Account(uid=TEST_UID).parse({'login': 'login'})
        s1 = acc.snapshot()
        acc.billing_features = {
            '100% cashback': {
                'in_trial': True,
                'paid_trial': False,
                'region_id': 0,
                'trial_duration': 0,
                'brand': 'brand',
            },
        }

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {u'type': 180, u'uid': 123, u'value': b'\n \n\r100% cashback\x12\x0f\x08\x01\x10\x00\x18\x00 \x00*\x05brand'},
                ]),
            ],
        )

    def test_billing_features_not_changed(self):
        acc = Account(uid=TEST_UID).parse({'login': 'login'})
        acc.billing_features = {
            '100% cashback': {
                'in_trial': True,
                'paid_trial': False,
                'region_id': 0,
                'trial_duration': 0,
                'brand': 'brand',
            },
        }
        s1 = acc.snapshot()
        acc.billing_features = {
            '100% cashback': {
                'in_trial': True,
                'paid_trial': False,
                'region_id': 0,
                'trial_duration': 0,
                'brand': 'brand',
            },
        }

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [],
        )

    def test_billing_features_deleted(self):
        acc = Account(uid=TEST_UID).parse({'login': 'login'})
        acc.billing_features = {
            '100% cashback': {
                'in_trial': True,
                'paid_trial': False,
                'region_id': 0,
                'trial_duration': 0,
                'brand': 'brand',
            },
        }
        s1 = acc.snapshot()
        acc.billing_features = {}

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))

        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([
                            AT['account.billing_features'],
                        ]),
                    ),
                ),
            ],
        )

    def test_content_rating_class(self):
        AttributeTest(
            account_field_name='content_rating_class',
            attribute_name='account.content_rating_class',
            attribute_type=IntegerAttributeValuespace(),
        ).run()

    def test_music_content_rating(self):
        AttributeTest(
            account_field_name='music_content_rating_class',
            attribute_name='account.music_content_rating_class',
            attribute_type=IntegerAttributeValuespace(),
        ).run()

    def test_video_content_rating(self):
        AttributeTest(
            account_field_name='video_content_rating_class',
            attribute_name='account.video_content_rating_class',
            attribute_type=IntegerAttributeValuespace(),
        ).run()

    def test_unsubscribed_from_maillists(self):
        AttributeTest(
            account_field_name='unsubscribed_from_maillists',
            attribute_name='account.unsubscribed_from_maillists',
            attribute_type=UnsubscribedFromMaillistsValuespace(),
        ).run()


@with_settings(LOGIN_QUARANTINE_PERIOD=1)
class TestDeleteAccount(TestCase):
    def setUp(self):
        self.alias_types = sorted(ALT.values())
        super(TestDeleteAccount, self).setUp()

    def query_insert_related_aliases_to_removed_aliases_table(self, uid=TEST_UID):
        """
        SQL-запрос добавляющий алиасы связанные с uid'ом в таблицу removed_aliases
        """
        return insert_ignore_into_removed_aliases(
            select([alt.c.uid, alt.c.type, alt.c.value]).where(
                and_(
                    alt.c.uid == uid,
                    alt.c.type.in_(sorted(set(self.alias_types) - {ALT['pdd'], ALT['pddalias']})),
                ),
            ),
        )

    def test_delete_account(self):
        acc = default_account().parse({
            'uid': TEST_UID,
            'subscriptions': {2: {'sid': 2}},
        })

        queries = AccountEavSerializer().serialize(acc, None, diff(acc, None))

        eq_eav_queries(
            queries,
            [
                insert_with_on_duplicate_key_update(rlt, ['free_ts']).values({
                    'login': TEST_LOGIN1.encode('utf8'),
                    'free_ts': DatetimeNow(),
                }),
                self.query_insert_related_aliases_to_removed_aliases_table(TEST_UID),
                alt.delete().where(
                    and_(
                        alt.c.uid == TEST_UID,
                        alt.c.type.in_(self.alias_types),
                    ),
                ),
                suid2_table.delete().where(
                    suid2_table.c.uid == TEST_UID,
                ),
                at.delete().where(at.c.uid == TEST_UID),
                eat.delete().where(eat.c.uid == TEST_UID),
                pht.delete().where(pht.c.uid == TEST_UID),
                prkt.delete().where(prkt.c.uid == TEST_UID),
            ],
        )

    def test_with_public_id(self):
        acc = default_account().parse({
            'uid': TEST_UID,
            'account.user_defined_public_id': 'Public.Id',
            'aliases': {
                str(ALT['public_id']): 'public-id',
                str(ALT['old_public_id']): ['old-public-id-1', 'old-public-id-2'],
            }
        })

        queries = AccountEavSerializer().serialize(acc, None, diff(acc, None))
        eq_eav_queries(
            queries,
            [
                insert_with_on_duplicate_key_update(rlt, ['free_ts']).values({
                    'login': TEST_LOGIN1.encode('utf8'),
                    'free_ts': DatetimeNow(),
                }),
                insert_with_on_duplicate_key_update(rlt, ['free_ts']).values({
                    'login': b'public-id',
                    'free_ts': DatetimeNow(),
                }),
                insert_with_on_duplicate_key_update(rlt, ['free_ts']).values({
                    'login': b'old-public-id-1',
                    'free_ts': DatetimeNow(),
                }),
                insert_with_on_duplicate_key_update(rlt, ['free_ts']).values({
                    'login': b'old-public-id-2',
                    'free_ts': DatetimeNow(),
                }),
                self.query_insert_related_aliases_to_removed_aliases_table(TEST_UID),
                alt.delete().where(
                    and_(
                        alt.c.uid == TEST_UID,
                        alt.c.type.in_(self.alias_types),
                    ),
                ),
                at.delete().where(at.c.uid == TEST_UID),
                eat.delete().where(eat.c.uid == TEST_UID),
                pht.delete().where(pht.c.uid == TEST_UID),
                prkt.delete().where(prkt.c.uid == TEST_UID),
            ],
        )

    def test_delete_account_with_plus(self):
        acc = default_account().parse({
            'uid': TEST_UID,
            'plus_enabled': True,
            'plus_subscription_stopped_ts': datetime.now(),
            'plus_trial_used_ts': datetime.now(),
            'plus_next_charge_ts': datetime.now(),
        })

        queries = AccountEavSerializer().serialize(acc, None, diff(acc, None))

        eq_eav_queries(
            queries,
            [
                insert_with_on_duplicate_key_update(rlt, ['free_ts']).values({
                    'login': TEST_LOGIN1.encode('utf8'),
                    'free_ts': DatetimeNow(),
                }),
                self.query_insert_related_aliases_to_removed_aliases_table(TEST_UID),
                alt.delete().where(
                    and_(
                        alt.c.uid == TEST_UID,
                        alt.c.type.in_(self.alias_types),
                    ),
                ),
                at.delete().where(at.c.uid == TEST_UID),
                eat.delete().where(eat.c.uid == TEST_UID),
                pht.delete().where(pht.c.uid == TEST_UID),
                prkt.delete().where(prkt.c.uid == TEST_UID),
            ],
            row_count=[1],
        )

    def test_delete_account_with_phones(self):
        acc = default_account().parse({
            'uid': TEST_UID,
            'phones': {TEST_PHONE_DICT['id']: TEST_PHONE_DICT},
        })

        phone_attr_filters = [
            and_(
                eat.c.entity_type == EXTENDED_ATTRIBUTES_PHONE_TYPE,
                eat.c.entity_id == TEST_PHONE_ID1,
                eat.c.type == EXTENDED_ATTRIBUTES_PHONE_NAME_TO_TYPE_MAPPING[field],
            )
            for field in ['number', 'created', 'bound', 'confirmed', 'secured', 'admitted']
        ]

        queries = AccountEavSerializer().serialize(acc, None, diff(acc, None))
        eq_eav_queries(
            queries,
            [
                insert_with_on_duplicate_key_update(rlt, ['free_ts']).values({
                    'login': TEST_LOGIN1.encode('utf8'),
                    'free_ts': DatetimeNow(),
                }),
                self.query_insert_related_aliases_to_removed_aliases_table(TEST_UID),
                alt.delete().where(
                    and_(
                        alt.c.uid == TEST_UID,
                        alt.c.type.in_(self.alias_types),
                    ),
                ),
                phone_operations.delete().where(
                    and_(
                        phone_operations.c.uid == TEST_UID,
                        phone_operations.c.id == TEST_PHONE_OPERATION['id'],
                    ),
                ),
                phone_bindings.delete().where(
                    and_(
                        phone_bindings.c.uid == TEST_UID,
                        phone_bindings.c.phone_id == TEST_PHONE_ID1,
                    ),
                ),
                eat.delete().where(
                    and_(
                        eat.c.uid == TEST_UID,
                        or_(*phone_attr_filters),
                    ),
                ),
                at.delete().where(at.c.uid == TEST_UID),
                eat.delete().where(eat.c.uid == TEST_UID),
                pht.delete().where(pht.c.uid == TEST_UID),
                prkt.delete().where(prkt.c.uid == TEST_UID),
            ],
            row_count=[1],
        )

    def test_with_emails(self):
        account = default_account(uid=TEST_UID)
        account.emails = Emails(account)
        email = Email(address=TEST_EMAIL1, id=TEST_EMAIL_ID1)
        account.emails.add(email)

        queries = list(AccountEavSerializer().serialize(account, None, diff(account, None)))

        eq_eav_queries(
            queries,
            [
                insert_with_on_duplicate_key_update(rlt, ['free_ts']).values({'login': TEST_LOGIN1.encode('utf8'), 'free_ts': DatetimeNow()}),
                self.query_insert_related_aliases_to_removed_aliases_table(TEST_UID),
                alt.delete().where(and_(alt.c.uid == TEST_UID, alt.c.type.in_(self.alias_types))),
                ebt.delete().where(ebt.c.uid == TEST_UID),
                eat.delete().where(and_(eat.c.uid == TEST_UID, eat.c.entity_type == EXTENDED_ATTRIBUTES_EMAIL_TYPE)),
                at.delete().where(at.c.uid == TEST_UID),
                eat.delete().where(eat.c.uid == TEST_UID),
                pht.delete().where(pht.c.uid == TEST_UID),
                prkt.delete().where(prkt.c.uid == TEST_UID),
            ],
        )

    def test_with_webauthn_credentials(self):
        account = default_account(uid=TEST_UID)
        cred = WebauthnCredential(external_id='test-id')
        account.webauthn_credentials.add(cred)

        queries = list(AccountEavSerializer().serialize(account, None, diff(account, None)))

        eq_eav_queries(
            queries,
            [
                insert_with_on_duplicate_key_update(rlt, ['free_ts']).values({'login': TEST_LOGIN1.encode('utf8'), 'free_ts': DatetimeNow()}),
                self.query_insert_related_aliases_to_removed_aliases_table(TEST_UID),
                alt.delete().where(and_(alt.c.uid == TEST_UID, alt.c.type.in_(self.alias_types))),
                wct.delete().where(wct.c.uid == TEST_UID),
                eat.delete().where(and_(eat.c.uid == TEST_UID, eat.c.entity_type == EXTENDED_ATTRIBUTES_WEBAUTHN_TYPE)),
                at.delete().where(at.c.uid == TEST_UID),
                eat.delete().where(eat.c.uid == TEST_UID),
                pht.delete().where(pht.c.uid == TEST_UID),
                prkt.delete().where(prkt.c.uid == TEST_UID),
            ],
        )

    def test_delete_pdd_account(self):
        acc = default_account(
            alias_type='pdd',
            uid=TEST_PDD_UID1,
            alias='test@okna.ru',
        ).parse({
            'domain': 'okna.ru',
            'domid': 1,
            'hosted': True,
        })

        queries = list(AccountEavSerializer().serialize(acc, None, diff(acc, None)))
        # Здесь мы руками "формируем" сырой SQL, поэтому стандартный метод проверки
        # не подходит.
        eq_(
            str(compile_query_with_dialect(queries[0].to_query(), mysql.dialect())),
            'INSERT IGNORE INTO removed_aliases (uid, type, value) SELECT aliases.uid, aliases.type, '
            'concat(\'okna.ru\', SUBSTR(aliases.value, LOCATE(\'/\', aliases.value))) \n'
            'FROM aliases \nWHERE aliases.uid = %s AND aliases.type IN (%s, %s)',
        )
        eq_eav_queries(
            queries[1:],
            [
                self.query_insert_related_aliases_to_removed_aliases_table(TEST_PDD_UID1),
                alt.delete().where(
                    and_(
                        alt.c.uid == TEST_PDD_UID1,
                        alt.c.type.in_(self.alias_types),
                    ),
                ),
                at.delete().where(at.c.uid == TEST_PDD_UID1),
                eat.delete().where(eat.c.uid == TEST_PDD_UID1),
                pht.delete().where(pht.c.uid == TEST_PDD_UID1),
                prkt.delete().where(prkt.c.uid == TEST_PDD_UID1),
            ],
        )

    def test_delete_kinopoisk_account(self):
        acc = default_account(
            alias_type='kinopoisk',
            uid=TEST_KINOPOISK_UID,
            alias=str(TEST_KINOPOISK_ID),
        )

        queries = list(AccountEavSerializer().serialize(acc, None, diff(acc, None)))

        eq_eav_queries(
            queries,
            [
                self.query_insert_related_aliases_to_removed_aliases_table(TEST_KINOPOISK_UID),
                alt.delete().where(
                    and_(
                        alt.c.uid == TEST_KINOPOISK_UID,
                        alt.c.type.in_(self.alias_types),
                    ),
                ),
                at.delete().where(at.c.uid == TEST_KINOPOISK_UID),
                eat.delete().where(eat.c.uid == TEST_KINOPOISK_UID),
                pht.delete().where(pht.c.uid == TEST_KINOPOISK_UID),
                prkt.delete().where(prkt.c.uid == TEST_KINOPOISK_UID),
            ],
        )

    def test_delete_kiddish_account(self):
        acc = default_account(
            alias_type='kiddish',
            uid=TEST_UID,
            alias=str(TEST_LOGIN1),
        )

        queries = list(AccountEavSerializer().serialize(acc, None, diff(acc, None)))

        eq_eav_queries(
            queries,
            [
                insert_with_on_duplicate_key_update(rlt, ['free_ts']).values(
                    {
                        'login': TEST_LOGIN1.encode('utf8'),
                        'free_ts': DatetimeNow(),
                    },
                ),
                self.query_insert_related_aliases_to_removed_aliases_table(TEST_UID),
                transaction.begin(),
                alt.delete().where(
                    and_(
                        alt.c.uid == TEST_UID,
                        alt.c.type.in_(self.alias_types),
                    ),
                ),
                family_members_table.delete().where(family_members_table.c.uid == TEST_UID),
                transaction.commit(),
                at.delete().where(at.c.uid == TEST_UID),
                eat.delete().where(eat.c.uid == TEST_UID),
                pht.delete().where(pht.c.uid == TEST_UID),
                prkt.delete().where(prkt.c.uid == TEST_UID),
            ],
        )


class TestDeleteFieldAccount(TestCase):
    def test_account_delete_phonenumber_alias(self):
        acc = default_account(uid=TEST_UID).parse({
            'aliases': {str(ALT['phonenumber']): TEST_PHONE_NUMBER1.digital},
            'account.enable_search_by_phone_alias': '1',
        })
        s1 = acc.snapshot()

        acc.phonenumber_alias = None

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(queries, [
            insert_ignore_into_removed_aliases(
                select([alt.c.uid, alt.c.type, alt.c.value]).where(
                    and_(alt.c.uid == TEST_UID, alt.c.type.in_([ALT['phonenumber']])),
                ),
            ),
            alt.delete().where(
                and_(alt.c.uid == TEST_UID, alt.c.type.in_([ALT['phonenumber']])),
            ),
            at.delete().where(and_(at.c.uid == TEST_UID, at.c.type.in_([AT['account.enable_search_by_phone_alias']]))),
        ])

    def test_account_delete_altdomain_alias(self):
        acc = default_account(uid=TEST_UID).parse({
            'aliases': {
                str(ALT['altdomain']): 'login@galatasaray.net',
            },
        })
        s1 = acc.snapshot()

        acc.altdomain_alias = None

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(queries, [
            insert_ignore_into_removed_aliases(
                select([alt.c.uid, alt.c.type, alt.c.value]).where(
                    and_(alt.c.uid == TEST_UID, alt.c.type.in_([ALT['altdomain']])),
                ),
            ),
            alt.delete().where(
                and_(alt.c.uid == TEST_UID, alt.c.type.in_([ALT['altdomain']])),
            ),
        ])

    def test_account_delete_browser_key(self):
        acc = default_account(uid=TEST_UID).parse({
            'browser_key': 'key',
        })
        s1 = acc.snapshot()
        acc.browser_key = None

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == 123,
                        at.c.type.in_([AT['account.browser_key']]),
                    ),
                ),
            ],
        )

    def test_account_set_browser_key_to_none(self):
        acc = default_account(uid=TEST_UID).parse({
            'browser_key': 'key',
        })
        s1 = acc.snapshot()
        acc.browser_key.set(None)

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([AT['account.browser_key']]),
                    ),
                ),
            ],
        )

    def test_account_delete_password(self):
        acc = default_account(uid=TEST_UID)
        acc.password.set(TEST_PASSWORD.password, TEST_PASSWORD.quality, TEST_PASSWORD.salt)
        s1 = acc.snapshot()
        acc.password = None

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_(
                            sorted([
                                AT['password.forced_changing_reason'],
                                AT['password.forced_changing_time'],
                                AT['password.pwn_forced_changing_suspended_at'],
                                AT['password.encrypted'],
                                AT['password.quality'],
                                AT['password.update_datetime'],
                            ]),
                        ),
                    ),
                ),
            ],
        )

    def test_delete_enable_app_password(self):
        acc = default_account(uid=TEST_UID).parse({
            'enable_app_password': True,
        })
        s1 = acc.snapshot()

        acc.enable_app_password = None

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([
                            AT['account.enable_app_password'],
                        ]),
                    ),
                ),
            ],
        )

    def test_delete_is_shared(self):
        acc = default_account(uid=TEST_UID).parse({
            'is_shared': True,
        })
        s1 = acc.snapshot()

        acc.is_shared = None

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([
                            AT['account.is_shared'],
                        ]),
                    ),
                ),
            ],
        )

    def test_delete_is_verified(self):
        acc = default_account(uid=TEST_UID).parse({
            'is_verified': True,
        })
        s1 = acc.snapshot()

        acc.is_verified = None

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([
                            AT['account.is_verified'],
                        ]),
                    ),
                ),
            ],
        )

    def test_delete_is_connect_admin(self):
        acc = default_account(uid=TEST_UID).parse({
            'account.is_connect_admin': True,
        })
        s1 = acc.snapshot()

        acc.is_connect_admin = None

        queries = AccountEavSerializer().serialize(s1, acc, diff(s1, acc))
        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([
                            AT['account.is_connect_admin'],
                        ]),
                    ),
                ),
            ],
        )


class ReminderTestDeleteAccount(TestCase):
    """
    Тест должен напомнить разработчику, добавляющему новую таблицу, о возможной
    необходимости удалить из неё данные вместе с аккаунтом.

    Если новую таблицу не требуется чистить в момент удаления аккаунта, то
    нужно её добавить в множество EXCLUDE_TABLES.
    """

    # Эти таблицы либо не связаны непосредственно с аккаунтом, либо их не
    # следует чистить, удаляя аккаунт.
    EXCLUDE_TABLES = {
        'removed_aliases',
        'uid',
        'pdduid',
        'suid',
        'pddsuid',
        'totp_secret_id',
        'phone_id',
        'email_id',
        'phone_bindings_history',
        'domains',
        'reserved_logins',
        'hosts',
        'domains_events',
        'domains_hosts',
        'tracks',
        'yakey_backups',
        'device_public_key',
        'family_info',
        'family_members',
        'phone_bindings_history_delete_tasks',
        'webauthn_credential_id',
    }

    def setUp(self):
        super(ReminderTestDeleteAccount, self).setUp()
        self._env = Environment()
        self._db_faker = FakeDB()
        self._db_faker.start()

    def tearDown(self):
        self._db_faker.stop()
        del self._db_faker
        super(ReminderTestDeleteAccount, self).tearDown()

    def _populate_tables(self, uid):
        account = Account(uid=uid)
        for populator in self._get_populators():
            populator(account)
        queries = AccountEavSerializer().serialize(None, account, diff(None, account))
        safe_execute_queries(queries)
        return account

    def _get_populators(self):
        populators = []
        for attr_name in dir(self):
            if attr_name.startswith('_populator__'):
                attr = getattr(self, attr_name)
                if callable(attr):
                    populators.append(attr)
        return populators

    def _assert_tables_are_full(self, uid):
        for table in self._get_account_tables():
            db = self._get_db_name(table, uid)
            records = self._db_faker.select(table.name, uid=uid, db=db)
            ok_(records, 'Table %s should not be empty. Populate the table or exclude it.' % table.name)

    def _assert_tables_are_empty(self, uid):
        for table in self._get_account_tables():
            db = self._get_db_name(table, uid)
            records = self._db_faker.select(table.name, uid=uid, db=db)
            eq_(records, [])

    def _get_account_tables(self):
        tables = []
        for name in dir(schemas):
            obj = getattr(schemas, name)
            if isinstance(obj, Table):
                tables.append(obj)
        return [t for t in tables if t.name not in self.EXCLUDE_TABLES]

    def _get_db_name(self, table, uid):
        if table.metadata is schemas.central_metadata:
            return 'passportdbcentral'
        else:
            return get_db_name(table.name, uid)

    def _populator__basic(self, account):
        account.uid = TEST_UID
        account.set_portal_alias(TEST_LOGIN1)

    def _populator__subcriptions(self, account):
        account.subscriptions = {}
        subscribe(account, Subscription(account, service=Service.by_slug('fotki')))
        subscribe(account, Subscription(account, service=Service.by_slug('cards')))
        subscribe(account, Subscription(account, service=Service.by_slug('mail')))

    def _populator__account_deletion_operations(self, account):
        account.deletion_operation = AccountDeletionOperation(account, started_at=datetime.now())
        account.disabled_status = ACCOUNT_DISABLED_ON_DELETION

    def _populator__password_history(self, account):
        safe_execute_queries([
            EavInsertPasswordHistoryQuery(account.uid, [(datetime.now(), b'hello', 'reason')]),
        ])

    def _populator__personal_data(self, account):
        account.person = Person(
            account,
            firstname=TEST_FIRSTNAME1,
            lastname=TEST_LASTNAME1,
            display_name=TEST_DISPLAY_NAME1,
            default_avatar=TEST_DEFAULT_AVATAR1,
            birthday=TEST_BIRTHDATE1,
            country=TEST_COUNTRY_CODE1,
            city=TEST_CITY1,
            timezone=TEST_TIMEZONE1,
            gender=Gender.Male,
        )

    def _populator__emails(self, account):
        account.emails = Emails(account)
        account.emails.add(
            Email(
                account.emails,
                id=TEST_EMAIL_ID1,
                address=TEST_EMAIL1,
                created_at=datetime.now(),
                confirmed_at=datetime.now(),
                bound_at=datetime.now(),
            ),
        )

    def _populator__phones(self, account):
        account.phones = Phones(account)

        phone = account.phones.create(existing_phone_id=TEST_PHONE_ID1, number=TEST_PHONE_NUMBER1)
        phone.confirmed = datetime.now()
        phone.bound = datetime.now()
        phone.secured = datetime.now()
        account.phones.secure = phone

        phone.operation = PhoneOperation(
            phone,
            id=TEST_PHONE_OPERATION_ID1,
            type='remove',
        )

    def _populator__webauthn_credentials(self, account):
        account.webauthn_credentials = WebauthnCredentials(account)
        account.webauthn_credentials.add(
            WebauthnCredential(external_id='test-id'),
        )

    def _populator__passman_recovery_key(self, account):
        account.passman_recovery_key = PassManRecoveryKey(
            account,
            key_id=TEST_PASSMAN_KEY_ID,
            recovery_key=TEST_PASSMAN_RECOVERY_KEY,
        )

    def test(self):
        account = self._populate_tables(TEST_UID)
        self._assert_tables_are_full(TEST_UID)

        queries = AccountEavSerializer().serialize(account, None, diff(account, None))
        safe_execute_queries(queries)

        self._assert_tables_are_empty(TEST_UID)


class TestAccountProcessors(TestCase):
    def test_registration_datetime(self):
        eq_(account_registration_datetime_processor(None), None)
        eq_(account_registration_datetime_processor(''), None)
        eq_(account_registration_datetime_processor(datetime.now()), TimeNow())
        eq_(account_registration_datetime_processor(datetime.fromtimestamp(0)), None)


class TestAccountDeletionOperation(TestCase):
    def _assert_queries_change_disable_status(self, queries):
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {
                        'uid': TEST_UID,
                        'type': AT['account.is_disabled'],
                        'value': smart_bytes(ACCOUNT_DISABLED),
                    },
                ]),
                adot.delete().where(adot.c.uid == TEST_UID),
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([AT['account.deletion_operation_started_at']]),
                    ),
                ),
            ],
        )

    def test_create(self):
        account = Account()
        account.uid = TEST_UID
        snapshot = account.snapshot()

        account.disabled_status = ACCOUNT_DISABLED_ON_DELETION
        account.deletion_operation = AccountDeletionOperation(account, started_at=TEST_STARTED_DT)
        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {
                        'uid': TEST_UID,
                        'type': AT['account.is_disabled'],
                        'value': smart_bytes(ACCOUNT_DISABLED_ON_DELETION),
                    },
                ]),
                at_insert_odk().values([
                    {
                        'uid': TEST_UID,
                        'type': AT['account.deletion_operation_started_at'],
                        'value': smart_bytes(TEST_STARTED_UT),
                    },
                ]),
                insert_with_on_duplicate_key_update(adot, ['started_at']).values([
                    {
                        'uid': TEST_UID,
                        'started_at': TEST_STARTED_DT,
                    },
                ]),
            ],
        )

    def test_delete(self):
        account = Account()
        account.uid = TEST_UID
        account.disabled_status = ACCOUNT_DISABLED_ON_DELETION
        account.deletion_operation = AccountDeletionOperation(account, started_at=TEST_STARTED_DT)
        snapshot = account.snapshot()

        account.deletion_operation = None
        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        eq_eav_queries(
            queries,
            [
                adot.delete().where(adot.c.uid == TEST_UID),
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([AT['account.deletion_operation_started_at']]),
                    ),
                ),
            ],
        )

    def test_change_disable_status(self):
        account = Account()
        account.uid = TEST_UID
        # Наличие операции на аккаунте не имеет значения, т.к. её могли забыть
        # запросить из ЧЯ.
        account.disabled_status = ACCOUNT_DISABLED_ON_DELETION
        snapshot = account.snapshot()

        account.disabled_status = ACCOUNT_DISABLED

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        self._assert_queries_change_disable_status(queries)

    def test_change_disable_status__with_operation(self):
        account = Account()
        account.uid = TEST_UID
        account.disabled_status = ACCOUNT_DISABLED_ON_DELETION
        account.deletion_operation = AccountDeletionOperation(account, started_at=TEST_DATETIME1)
        snapshot = account.snapshot()

        account.disabled_status = ACCOUNT_DISABLED

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        self._assert_queries_change_disable_status(queries)

    def test_change_disable_status_and_started_at(self):
        account = Account()
        account.uid = TEST_UID
        account.disabled_status = ACCOUNT_DISABLED_ON_DELETION
        account.deletion_operation = AccountDeletionOperation(account, started_at=TEST_DATETIME1)
        snapshot = account.snapshot()

        account.disabled_status = ACCOUNT_DISABLED
        account.deletion_operation.started_at = TEST_DATETIME2

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        self._assert_queries_change_disable_status(queries)

    def test_change_started_at(self):
        account = Account()
        account.uid = TEST_UID
        account.disabled_status = ACCOUNT_DISABLED_ON_DELETION
        account.deletion_operation = AccountDeletionOperation(account, started_at=TEST_DATETIME1)
        snapshot = account.snapshot()

        account.deletion_operation.started_at = TEST_DATETIME2

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {
                        'uid': TEST_UID,
                        'type': AT['account.deletion_operation_started_at'],
                        'value': smart_bytes(int(datetime_to_unixtime(TEST_DATETIME2))),
                    },
                ]),
                insert_with_on_duplicate_key_update(adot, ['started_at']).values([
                    {
                        'uid': TEST_UID,
                        'started_at': TEST_DATETIME2,
                    },
                ]),
            ],
        )

    def test_not_changed(self):
        account = Account()
        account.uid = TEST_UID
        account.disabled_status = ACCOUNT_DISABLED_ON_DELETION
        account.deletion_operation = AccountDeletionOperation(account, started_at=TEST_DATETIME1)
        queries = AccountEavSerializer().serialize(account, account, diff(account, account))

        eq_eav_queries(queries, [])

    def test_create_operation__account_enabled(self):
        account = Account()
        account.uid = TEST_UID
        snapshot = account.snapshot()

        account.disabled_status = ACCOUNT_ENABLED
        account.deletion_operation = AccountDeletionOperation(account, started_at=TEST_STARTED_DT)

        with assert_raises(ValueError):
            list(AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account)))

    def test_create_operation__account_disabled(self):
        account = Account()
        account.uid = TEST_UID
        snapshot = account.snapshot()

        account.disabled_status = ACCOUNT_DISABLED
        account.deletion_operation = AccountDeletionOperation(account, started_at=TEST_STARTED_DT)

        with assert_raises(ValueError):
            list(AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account)))


class SingleValueAttributeTest(object):
    def __init__(
        self,
        account_field_name,
        attribute_name,
        attribute_type,
    ):
        self.account_field_name = account_field_name
        self.attribute_name = attribute_name
        self.attribute_type = attribute_type

    def run(self):
        self.assert_change_undefined_ok()
        self.assert_change_default_value_ok()
        self.assert_change_to_default_value_ok()

    def assert_change_undefined_ok(self):
        account = default_account(uid=TEST_UID)
        old_account = account.snapshot()
        setattr(account, self.account_field_name, self.attribute_type.non_default_field_value)

        queries = AccountEavSerializer().serialize(old_account, account, diff(old_account, account))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values(
                    [
                        dict(
                            uid=TEST_UID,
                            type=AT[self.attribute_name],
                            value=smart_bytes(self.attribute_type.non_default_attribute_value),
                        ),
                    ]
                ),
            ],
        )

    def assert_change_default_value_ok(self):
        account = default_account(uid=TEST_UID)
        setattr(account, self.account_field_name, self.attribute_type.default_field_value)
        old_account = account.snapshot()
        setattr(account, self.account_field_name, self.attribute_type.non_default_field_value)

        queries = AccountEavSerializer().serialize(old_account, account, diff(old_account, account))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values(
                    [
                        dict(
                            uid=TEST_UID,
                            type=AT[self.attribute_name],
                            value=smart_bytes(self.attribute_type.non_default_attribute_value),
                        ),
                    ]
                ),
            ],
        )

    def assert_change_to_default_value_ok(self):
        account = default_account(uid=TEST_UID)
        setattr(account, self.account_field_name, self.attribute_type.non_default_field_value)
        old_account = account.snapshot()
        setattr(account, self.account_field_name, self.attribute_type.default_field_value)

        queries = AccountEavSerializer().serialize(old_account, account, diff(old_account, account))

        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([AT[self.attribute_name]]),
                    ),
                ),
            ],
        )


class AttributeTest(SingleValueAttributeTest):
    def run(self):
        super(AttributeTest, self).run()
        self.assert_change_non_default_values_ok()

    def assert_change_non_default_values_ok(self):
        account = default_account(uid=TEST_UID)
        setattr(account, self.account_field_name, self.attribute_type.non_default_field_value)
        old_account = account.snapshot()
        setattr(account, self.account_field_name, self.attribute_type.non_default_field_value2)

        queries = AccountEavSerializer().serialize(old_account, account, diff(old_account, account))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values(
                    [
                        dict(
                            uid=TEST_UID,
                            type=AT[self.attribute_name],
                            value=smart_bytes(self.attribute_type.non_default_attribute_value2),
                        ),
                    ]
                ),
            ],
        )


class BaseAttributeValuespace(object):
    __metaclass__ = abc.ABCMeta

    @property
    @abc.abstractmethod
    def non_default_field_value(self):
        pass

    @property
    @abc.abstractmethod
    def non_default_attribute_value(self):
        pass

    @property
    @abc.abstractmethod
    def default_field_value(self):
        pass

    @property
    @abc.abstractmethod
    def non_default_field_value2(self):
        return self.non_default_field_value

    @property
    @abc.abstractmethod
    def non_default_attribute_value2(self):
        return self.non_default_attribute_value


class UnaryAttributeValuespace(BaseAttributeValuespace):
    default_field_value = False
    non_default_field_value = True
    non_default_attribute_value = '1'
    non_default_field_value2 = None
    non_default_attribute_value2 = None


class BinaryAttributeValuespace(BaseAttributeValuespace):
    default_field_value = None
    non_default_field_value = True
    non_default_attribute_value = '1'
    non_default_field_value2 = False
    non_default_attribute_value2 = '0'


class StringAttributeValuespace(BaseAttributeValuespace):
    default_field_value = ''
    non_default_field_value = 'привет'
    non_default_attribute_value = 'привет'
    non_default_field_value2 = 'пока'
    non_default_attribute_value2 = 'пока'


class DatetimeAttributeValuespace(BaseAttributeValuespace):
    default_field_value = datetime.fromtimestamp(0)
    non_default_field_value = datetime.fromtimestamp(100)
    non_default_attribute_value = '100'
    non_default_field_value2 = datetime.fromtimestamp(200)
    non_default_attribute_value2 = '200'


class IntegerAttributeValuespace(BaseAttributeValuespace):
    default_field_value = None
    non_default_field_value = 1
    non_default_attribute_value = '1'
    non_default_field_value2 = 2
    non_default_attribute_value2 = '2'


class UnsubscribedFromMaillistsValuespace(BaseAttributeValuespace):
    default_field_value = UnsubscriptionList(None)
    non_default_field_value = UnsubscriptionList('all')
    non_default_attribute_value = 'all'
    non_default_field_value2 = UnsubscriptionList('1,2,3')
    non_default_attribute_value2 = '1,2,3'
