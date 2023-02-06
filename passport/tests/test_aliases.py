# -*- coding: utf-8 -*-

import unittest

import mock
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.read_api.aliases import (
    find_removed_aliases_by_uid,
    find_uids_by_removed_aliases,
    RemovedAliasesByUidQuery,
    UidsByRemovedAliasesQuery,
)
from passport.backend.core.db.read_api.exceptions import UidsByRemovedAliasesLoginError
from passport.backend.core.db.schemas import removed_aliases_table as rat
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ATT
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import (
    and_,
    or_,
)


TEST_UID = 123
TEST_UID_2 = 1234
TEST_NORMAL_LOGIN = 'yandex_login'
TEST_NORMAL_LOGIN_WITH_DOMAIN = 'yandex_login@ya.ru'
TEST_LITE_ALIAS_1 = 'lite@lite.ru'
TEST_LITE_ALIAS_2_ENCODED = 'vasia@xn--80ad7c2a.xn--p1ai'
TEST_LITE_ALIAS_2_DECODED = u'vasia@фыва.рф'
TEST_LITE_ALIAS_2_ENCODED_AS_PDD_ALIAS = 'xn--80ad7c2a.xn--p1ai/vasia'
TEST_PDD_ENCODED = 'pdddomain.ru/pddlogin'
TEST_PDD_DECODED = 'pddlogin@pdddomain.ru'
TEST_PDD_ENCODED_AS_LITE_ALIAS = 'pddlogin@pdddomain.ru'
TEST_PDDALIAS_ENCODED = 'xn--80ad7c2a.xn--p1ai/pddlogin'
TEST_PDDALIAS_DECODED = u'pddlogin@фыва.рф'
TEST_SOCIAL_ALIAS = 'uid-abcdefgh'
TEST_PHONISH_ALIAS = 'phne-abcdefgh'
TEST_PHONENUMBER_ALIAS = '78121234567'
TEST_PHONENUMBER_ALIAS_NATURAL = u'+7(812)123-45-67'
TEST_GALATASARAY_ALIAS_ENCODED = '1/vasia'
TEST_GALATASARAY_ALIAS_DECODED = 'vasia@galatasaray.net'
TEST_KP_ALIAS_ENCODED = '2/vasia'
TEST_KP_ALIAS_DECODED = 'vasia@kinopoisk.ru'
TEST_LIMIT = 100500


def _raw_query_result(rows):
    result_proxy = mock.Mock()
    result_proxy.fetchall = mock.Mock(return_value=rows)
    return result_proxy


class TestRemovedAliasesByUidQuery(unittest.TestCase):
    """
    Тесты RemovedAliasesByUidQuery - формирование запроса, парсинг ответа БД в словарь алиасов.
    """
    def test_select_query(self):
        q = RemovedAliasesByUidQuery(TEST_UID)
        eq_eav_queries(
            [q],
            [
                select([rat.c.value, rat.c.type]).distinct().where(rat.c.uid == TEST_UID),
            ],
        )

    def test_repr(self):
        eq_(repr(RemovedAliasesByUidQuery(1)),
            "<RemovedAliasesByUidQuery: uid: 1>")

    def test_eq(self):
        eq_(RemovedAliasesByUidQuery(TEST_UID), RemovedAliasesByUidQuery(TEST_UID))
        ok_(RemovedAliasesByUidQuery(TEST_UID) != RemovedAliasesByUidQuery(TEST_UID_2))

    def test_parse_query_result_empty_result(self):
        parsed_rows = RemovedAliasesByUidQuery(TEST_UID).parse_query_result(_raw_query_result([]))
        eq_(parsed_rows, {})

    def test_parse_query_result_simple_aliases(self):
        aliases = RemovedAliasesByUidQuery(TEST_UID).parse_query_result(_raw_query_result([
            (TEST_NORMAL_LOGIN.encode('utf8'), ATT['portal']),
            (b'mail_alias_1', ATT['mail']),
            (b'mail_alias_2', ATT['mail']),
            (b'narodmail_alias', ATT['narodmail']),
            (TEST_SOCIAL_ALIAS.encode('utf8'), ATT['social']),
            (TEST_PHONISH_ALIAS.encode('utf8'), ATT['phonish']),
            (TEST_PHONENUMBER_ALIAS.encode('utf8'), ATT['phonenumber']),
            (b'yandexoid_alias', ATT['yandexoid']),
        ]))
        eq_(
            aliases,
            {
                'portal': [TEST_NORMAL_LOGIN],
                'mail': ['mail_alias_1', 'mail_alias_2'],
                'narodmail': ['narodmail_alias'],
                'social': [TEST_SOCIAL_ALIAS],
                'phonish': [TEST_PHONISH_ALIAS],
                'phonenumber': [TEST_PHONENUMBER_ALIAS],
                'yandexoid': ['yandexoid_alias'],
            },
        )

    def test_parse_query_result_altdomain_galatasaray_alias(self):
        aliases = RemovedAliasesByUidQuery(TEST_UID).parse_query_result(_raw_query_result(
            [(TEST_GALATASARAY_ALIAS_ENCODED.encode('utf8'), ATT['altdomain'])],
        ))
        eq_(aliases, {'altdomain': [TEST_GALATASARAY_ALIAS_DECODED]})

    def test_parse_query_result_altdomain_kinopoisk_alias(self):
        aliases = RemovedAliasesByUidQuery(TEST_UID).parse_query_result(_raw_query_result(
            [(TEST_KP_ALIAS_ENCODED.encode('utf8'), ATT['altdomain'])],
        ))
        eq_(aliases, {'altdomain': [TEST_KP_ALIAS_DECODED]})

    def test_parse_query_result_lite_alias(self):
        aliases = RemovedAliasesByUidQuery(TEST_UID).parse_query_result(_raw_query_result(
            [
                (TEST_LITE_ALIAS_1.encode('utf8'), ATT['lite']),
                (TEST_LITE_ALIAS_2_ENCODED.encode('utf8'), ATT['lite']),
            ],
        ))
        eq_(
            aliases,
            {
                'lite': [
                    TEST_LITE_ALIAS_1,
                    TEST_LITE_ALIAS_2_DECODED,
                ],
            },
        )

    def test_parse_query_result_pdd_pddalias_aliases(self):
        aliases = RemovedAliasesByUidQuery(TEST_UID).parse_query_result(_raw_query_result(
            [
                (TEST_PDD_ENCODED.encode('utf8'), ATT['pdd']),
                (TEST_PDDALIAS_ENCODED.encode('utf8'), ATT['pddalias']),
            ],
        ))
        eq_(
            aliases,
            {
                'pdd': [TEST_PDD_DECODED],
                'pddalias': [TEST_PDDALIAS_DECODED],
            },
        )

    def test_parse_query_result_public_id_aliases(self):
        aliases = RemovedAliasesByUidQuery(TEST_UID).parse_query_result(_raw_query_result(
            [
                (b'p_id', ATT['public_id']),
                (b'old_p_id', ATT['old_public_id']),
            ],
        ))
        eq_(
            aliases,
            {
                'public_id': ['p_id'],
                'old_public_id': ['old_p_id'],
            },
        )


class TestUidsByRemovedAliasesQuery(unittest.TestCase):
    """
    Тесты UidsByRemovedAliasesQuery - формирование запроса в зависимости от передаваемого логина.
    """
    def test_select_query_normal_login(self):
        q = UidsByRemovedAliasesQuery(TEST_NORMAL_LOGIN, TEST_LIMIT)
        eq_eav_queries(
            [q],
            [
                select([rat.c.uid]).distinct().where(and_(
                    rat.c.type.in_(ATT[alias] for alias in ['portal', 'mail', 'narodmail']),
                    rat.c.value == TEST_NORMAL_LOGIN.encode('utf8'),
                )).limit(TEST_LIMIT),
            ],
        )

    def test_select_query_normal_login_with_yandex_domain(self):
        q = UidsByRemovedAliasesQuery(TEST_NORMAL_LOGIN_WITH_DOMAIN, TEST_LIMIT)
        eq_eav_queries(
            [q],
            [
                select([rat.c.uid]).distinct().where(and_(
                    rat.c.type.in_(ATT[alias] for alias in ['portal', 'mail', 'narodmail']),
                    rat.c.value == TEST_NORMAL_LOGIN.encode('utf8'),
                )).limit(TEST_LIMIT),
            ],
        )

    @raises(UidsByRemovedAliasesLoginError)
    def test_select_query_no_login_part(self):
        UidsByRemovedAliasesQuery('@yandex.ru', TEST_LIMIT).to_query()

    def test_select_query_lite_login(self):
        q = UidsByRemovedAliasesQuery(TEST_LITE_ALIAS_2_DECODED, TEST_LIMIT)
        eq_eav_queries(
            [q],
            [
                select([rat.c.uid]).distinct().where(or_(
                    and_(
                        rat.c.type.in_(ATT[alias] for alias in ['pdd', 'pddalias']),
                        rat.c.value == TEST_LITE_ALIAS_2_ENCODED_AS_PDD_ALIAS.encode('utf8'),
                    ),
                    and_(
                        rat.c.type == ATT['lite'],
                        rat.c.value == TEST_LITE_ALIAS_2_ENCODED.encode('utf8'),
                    ),
                )).limit(TEST_LIMIT),
            ],
        )

    def test_select_query_pdd_login(self):
        q = UidsByRemovedAliasesQuery(TEST_PDD_DECODED, TEST_LIMIT)
        eq_eav_queries(
            [q],
            [
                select([rat.c.uid]).distinct().where(or_(
                    and_(
                        rat.c.type.in_(ATT[alias] for alias in ['pdd', 'pddalias']),
                        rat.c.value == TEST_PDD_ENCODED.encode('utf8'),
                    ),
                    and_(
                        rat.c.type == ATT['lite'],
                        rat.c.value == TEST_PDD_ENCODED_AS_LITE_ALIAS.encode('utf8'),
                    ),
                )).limit(TEST_LIMIT),
            ],
        )

    def test_select_query_altdomain_alias(self):
        q = UidsByRemovedAliasesQuery(TEST_GALATASARAY_ALIAS_DECODED, TEST_LIMIT)
        eq_eav_queries(
            [q],
            [
                select([rat.c.uid]).distinct().where(and_(
                    rat.c.type == ATT['altdomain'],
                    rat.c.value == TEST_GALATASARAY_ALIAS_ENCODED.encode('utf8'),
                )).limit(TEST_LIMIT),
            ],
        )

    def test_select_query_social_alias(self):
        q = UidsByRemovedAliasesQuery(TEST_SOCIAL_ALIAS, TEST_LIMIT)
        eq_eav_queries(
            [q],
            [
                select([rat.c.uid]).distinct().where(and_(
                    rat.c.type == ATT['social'],
                    rat.c.value == TEST_SOCIAL_ALIAS.encode('utf8'),
                )).limit(TEST_LIMIT),
            ],
        )

    def test_select_query_phonish_alias(self):
        q = UidsByRemovedAliasesQuery(TEST_PHONISH_ALIAS, TEST_LIMIT)
        eq_eav_queries(
            [q],
            [
                select([rat.c.uid]).distinct().where(and_(
                    rat.c.type == ATT['phonish'],
                    rat.c.value == TEST_PHONISH_ALIAS.encode('utf8'),
                )).limit(TEST_LIMIT),
            ],
        )

    def test_select_query_phonenumber_alias(self):
        q = UidsByRemovedAliasesQuery(TEST_PHONENUMBER_ALIAS_NATURAL, TEST_LIMIT)
        eq_eav_queries(
            [q],
            [
                select([rat.c.uid]).distinct().where(and_(
                    rat.c.type == ATT['phonenumber'],
                    rat.c.value == TEST_PHONENUMBER_ALIAS.encode('utf8'),
                )).limit(TEST_LIMIT),
            ],
        )

    def test_parse_query_result(self):
        uids = UidsByRemovedAliasesQuery(TEST_NORMAL_LOGIN).parse_query_result(_raw_query_result(
            [(TEST_UID,), (TEST_UID_2,)],
        ))
        eq_(uids, [TEST_UID, TEST_UID_2])

    def test_repr(self):
        eq_(repr(UidsByRemovedAliasesQuery(TEST_NORMAL_LOGIN)),
            "<UidsByRemovedAliasesQuery: login: yandex_login | limit: 5000>")

    def test_query_params(self):
        eq_(
            UidsByRemovedAliasesQuery(TEST_NORMAL_LOGIN, TEST_LIMIT).query_params(),
            (TEST_NORMAL_LOGIN, TEST_LIMIT),
        )


class TestAliasesExecute(unittest.TestCase):
    """
    Проверяем результат выполнения запросов UidsByRemovedAliasesQuery и RemovedAliasesByUidQuery.
    """
    TABLE = 'removed_aliases'
    DB = 'passportdbcentral'

    def setUp(self):
        self.fake_db = FakeDB()
        self.fake_db.start()

    def tearDown(self):
        self.fake_db.stop()
        del self.fake_db

    def test_find_uids_by_removed_aliases_empty(self):
        uids = find_uids_by_removed_aliases(TEST_PDD_DECODED)
        eq_(uids, [])

    def test_find_uids_by_removed_aliases_pdd_to_lite(self):
        self.fake_db.insert('removed_aliases', db='passportdbcentral', uid=TEST_UID, type=ATT['lite'], value=TEST_PDD_ENCODED_AS_LITE_ALIAS)
        aliases = find_uids_by_removed_aliases(TEST_PDD_DECODED)
        eq_(aliases, [TEST_UID])

    def test_find_uids_by_removed_aliases_same_uids(self):
        self.fake_db.insert(self.TABLE, db=self.DB, uid=TEST_UID, type=ATT['lite'], value=TEST_LITE_ALIAS_2_ENCODED)
        self.fake_db.insert(self.TABLE, db=self.DB, uid=TEST_UID, type=ATT['pdd'], value=TEST_LITE_ALIAS_2_ENCODED_AS_PDD_ALIAS)
        uids = find_uids_by_removed_aliases(TEST_LITE_ALIAS_2_DECODED)
        eq_(uids, [TEST_UID])

    def test_find_removed_aliases_by_uid_empty(self):
        aliases = find_removed_aliases_by_uid(TEST_UID)
        eq_(aliases, {})

    def test_find_removed_aliases_by_uid(self):
        self.fake_db.insert(self.TABLE, db=self.DB, uid=TEST_UID_2, type=ATT['portal'], value=TEST_NORMAL_LOGIN)
        self.fake_db.insert(self.TABLE, db=self.DB, uid=TEST_UID, type=ATT['lite'], value=TEST_LITE_ALIAS_2_ENCODED)
        self.fake_db.insert(self.TABLE, db=self.DB, uid=TEST_UID, type=ATT['pdd'], value=TEST_PDD_ENCODED)
        aliases = find_removed_aliases_by_uid(TEST_UID)
        eq_(
            aliases,
            {
                'lite': [TEST_LITE_ALIAS_2_DECODED],
                'pdd': [TEST_PDD_DECODED],
            },
        )
