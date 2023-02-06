# -*- coding: utf-8 -*-

from itertools import chain
import unittest

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.db.faker.db_utils import (
    compile_query_with_dialect,
    eq_eav_queries,
)
from passport.backend.core.db.query import DbTransactionContainer
from passport.backend.core.db.schemas import (
    aliases_table as at,
    domains_events_table as det,
    pdd_domains_table as pdt,
    removed_aliases_table as rat,
)
from passport.backend.core.db.utils import encode_params_for_db
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE
from passport.backend.core.models.domain import Domain
from passport.backend.core.serializers.domain import (
    DeleteDomainAliasesAndSuid2Query,
    DeleteDomainAliasesFromSQLiteQuery,
    DomainSerializer,
    EVENT_NAME_TO_TYPE,
)
from passport.backend.core.test.test_utils import settings_context
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.utils.common import merge_dicts
from sqlalchemy.dialects import (
    mysql,
    sqlite,
)
from sqlalchemy.sql import (
    and_ as sql_and,
    or_ as sql_or,
    select as sql_select,
    text as sql_text,
)


ORIGINAL_DOMAIN = 'ya.ru'
MIXEDCASE_DOMAIN = 'MiXeD.rU'
SLAVE_DOMAIN = 'slave-domain.ru'
ANOTHER_DOMAIN = 'another-domain.ru'
CYRILLIC_DOMAIN = u'яндекс.рф'
IDNA_CYRILLIC_DOMAIN = CYRILLIC_DOMAIN.encode('idna').decode('utf8')

TEST_DOMAIN_ID = 42
TEST_ALIAS_ID = 43


def prepare_raw_data(domain, **kwargs):
    raw_data = {
        'mx': domain.is_yandex_mx,
        'admin_uid': domain.admin_uid,
        'default_uid': domain.default_uid,
        'enabled': domain.is_enabled,
        'name': domain.punycode_domain,
        'ts': domain.registration_datetime,
        'options': '{"can_users_change_password": 1, "display_master_id": 42}',
    }
    raw_data.update(**kwargs)
    return raw_data


class TestDomainSerializer(unittest.TestCase):
    def setUp(self):
        self.db = FakeDB()
        self.db.start()

        self.serializer = DomainSerializer()
        self.domain_data = {
            'domid': str(TEST_DOMAIN_ID),
            'admin': u'2',
            'mx': u'1',
            'default_uid': u'1',
            'master_domain': u'yandex.ru',
            'domain': ORIGINAL_DOMAIN,
            'domain_ena': u'1',
            'born_date': '2015-01-21 12:16:31',
            'options': '{"can_users_change_password": 1, "display_master_id": 42}',
        }

    def tearDown(self):
        self.db.stop()
        del self.db

    def _insert_all_pdd_aliases_from_domain_into_removed_aliases_query(self, domain_id, domain_name):
        query = rat.insert().from_select(
            rat.c.keys(),
            sql_select([
                at.c.uid,
                at.c.type,
                sql_text("concat('%s', SUBSTR(aliases.value, LOCATE('/', aliases.value)))" % domain_name),
            ])
            .where(
                sql_and(
                    at.c.value.like(b'%d/%%' % domain_id),
                    at.c.type.in_([
                        ALIAS_NAME_TO_TYPE['pdd'],
                        ALIAS_NAME_TO_TYPE['pddalias'],
                    ]),
                ),
            ),
        )

        return query.prefix_with('IGNORE')

    def test_delete_alias_queries(self):
        query = DeleteDomainAliasesAndSuid2Query(1).to_query()
        eq_(
            str(compile_query_with_dialect(query, mysql.dialect())),
            'DELETE a, s FROM aliases a LEFT JOIN '
            'suid2 s USING(uid) WHERE a.type IN (%d, %d) '
            'AND a.value LIKE "%d/%%%%"' % (
                ALIAS_NAME_TO_TYPE['pdd'],
                ALIAS_NAME_TO_TYPE['pddalias'],
                1,
            ),
        )
        eq_(
            str(compile_query_with_dialect(query, sqlite.dialect())),
            'DELETE FROM suid2 WHERE uid IN '
            '(SELECT uid FROM aliases WHERE type IN (%d, %d) '
            'AND cast(value AS TEXT) LIKE "%d/%%")' % (
                ALIAS_NAME_TO_TYPE['pdd'],
                ALIAS_NAME_TO_TYPE['pddalias'],
                1,
            ),
        )

        query = DeleteDomainAliasesFromSQLiteQuery(1).to_query()
        eq_(
            str(compile_query_with_dialect(query, mysql.dialect())),
            'SELECT 1',
        )
        query = DeleteDomainAliasesFromSQLiteQuery(1).to_query()
        eq_(
            str(compile_query_with_dialect(query, sqlite.dialect())),
            'DELETE FROM aliases WHERE type IN (%d, %d) '
            'AND cast(value AS TEXT) LIKE "%d/%%"' % (
                ALIAS_NAME_TO_TYPE['pdd'],
                ALIAS_NAME_TO_TYPE['pddalias'],
                1,
            ),
        )

    def test_no_action_required(self):
        """
        Проверяем, что при отсутствии изменений в объекте
        сериализатор не порождает запросов.
        """
        domain = Domain().parse(self.domain_data)
        s1 = domain.snapshot()
        queries = self.serializer.serialize(
            s1,
            domain,
            diff(s1, domain),
        )
        eq_eav_queries(queries, [])

    def test_insert(self):
        """
        Проверяем, что сериализатор корректно порождает
        запрос на помещение объекта в БД.
        """
        self.domain_data.pop('domid', None)

        domain = Domain().parse(self.domain_data)
        queries = self.serializer.serialize(
            None,
            domain,
            diff(None, domain),
        )

        raw_data = prepare_raw_data(domain)
        eq_eav_queries(
            queries,
            [
                'BEGIN',
                pdt.insert().values(**encode_params_for_db(raw_data)),
                det.insert().values({
                    'domain_id': TEST_DOMAIN_ID,
                    'type': EVENT_NAME_TO_TYPE['add'],
                    'ts': DatetimeNow(),
                }),
                'COMMIT',
            ],
            inserted_keys=[TEST_DOMAIN_ID],
        )

        raw_data.update({
            'domain_id': TEST_DOMAIN_ID,
            'master_domain_id': 0,
        })
        self.db._serialize_to_eav(domain)
        self.db.check_line(
            'domains',
            raw_data,
            name=domain.domain,
            db='passportdbcentral',
        )
        self.db.check_line(
            'domains_events',
            {
                'type': EVENT_NAME_TO_TYPE['add'],
                'domain_id': TEST_DOMAIN_ID,
                'meta': None,
                'id': 1,
                'ts': DatetimeNow(),
            },
            type=EVENT_NAME_TO_TYPE['add'],
            db='passportdbcentral',
        )

    def test_insert_cyrillic(self):
        """
        Проверяем, что сериализатор корректно порождает
        запрос на помещение объекта в БД.
        """
        self.domain_data.pop('domid', None)
        self.domain_data['domain'] = CYRILLIC_DOMAIN

        domain = Domain().parse(self.domain_data)
        queries = self.serializer.serialize(
            None,
            domain,
            diff(None, domain),
        )

        raw_data = prepare_raw_data(domain)
        eq_eav_queries(
            queries,
            [
                'BEGIN',
                pdt.insert().values(**encode_params_for_db(raw_data)),
                det.insert().values({
                    'domain_id': TEST_DOMAIN_ID,
                    'type': EVENT_NAME_TO_TYPE['add'],
                    'ts': DatetimeNow(),
                }),
                'COMMIT',
            ],
            inserted_keys=[TEST_DOMAIN_ID],
        )

        raw_data.update({
            'domain_id': TEST_DOMAIN_ID,
            'master_domain_id': 0,
        })
        self.db._serialize_to_eav(domain)
        self.db.check_line(
            'domains',
            raw_data,
            name=domain.punycode_domain,
            db='passportdbcentral',
        )
        self.db.check_line(
            'domains_events',
            {
                'type': EVENT_NAME_TO_TYPE['add'],
                'domain_id': TEST_DOMAIN_ID,
                'meta': None,
                'id': 1,
                'ts': DatetimeNow(),
            },
            type=EVENT_NAME_TO_TYPE['add'],
            db='passportdbcentral',
        )

    def test_insert_mixed_case_convert_to_lowercase(self):
        domain = Domain().parse(
            merge_dicts(
                self.domain_data,
                dict(domain=MIXEDCASE_DOMAIN),
            ),
        )
        raw_data = merge_dicts(
            prepare_raw_data(domain),
            {
                'name': domain.domain.lower(),
                'domain_id': TEST_DOMAIN_ID,
                'master_domain_id': 0,
            },
        )

        self.db._serialize_to_eav(domain)
        self.db.check_line(
            'domains',
            raw_data,
            name=MIXEDCASE_DOMAIN.lower(),
            db='passportdbcentral',
        )

    def test_insert_without_options(self):
        """
        Проверяем, что сериализатор корректно порождает
        запрос на помещение объекта в БД, даже если
        поле options на модели не заполнено.
        """
        self.domain_data.pop('domid', None)
        self.domain_data.pop('options', None)

        domain = Domain().parse(self.domain_data)
        domain.can_users_change_password = None

        queries = self.serializer.serialize(
            None,
            domain,
            diff(None, domain),
        )

        raw_data = prepare_raw_data(
            domain,
            options='{}',
        )
        eq_eav_queries(
            queries,
            [
                'BEGIN',
                pdt.insert().values(**encode_params_for_db(raw_data)),
                det.insert().values({
                    'domain_id': TEST_DOMAIN_ID,
                    'type': EVENT_NAME_TO_TYPE['add'],
                    'ts': DatetimeNow(),
                }),
                'COMMIT',
            ],
            inserted_keys=[TEST_DOMAIN_ID],
        )

        self.db._serialize_to_eav(domain)

        raw_data.update({
            'domain_id': TEST_DOMAIN_ID,
            'master_domain_id': 0,
        })
        self.db.check_line(
            'domains',
            raw_data,
            name=domain.domain,
            db='passportdbcentral',
        )
        self.db.check_line(
            'domains_events',
            {
                'type': EVENT_NAME_TO_TYPE['add'],
                'domain_id': TEST_DOMAIN_ID,
                'meta': None,
                'id': 1,
                'ts': DatetimeNow(),
            },
            type=EVENT_NAME_TO_TYPE['add'],
            db='passportdbcentral',
        )

    def test_insert_with_options(self):
        self.domain_data.pop('domid', None)

        domain = Domain().parse(self.domain_data)
        domain.organization_name = 'Organization'
        domain.can_users_change_password = False
        domain.display_master_id = TEST_DOMAIN_ID
        queries = self.serializer.serialize(
            None,
            domain,
            diff(None, domain),
        )

        raw_data = prepare_raw_data(
            domain,
            options='{"can_users_change_password": 0, "display_master_id": 42, "organization_name": "Organization"}',
        )

        eq_eav_queries(
            queries,
            [
                'BEGIN',
                pdt.insert().values(**encode_params_for_db(raw_data)),
                det.insert().values({
                    'domain_id': TEST_DOMAIN_ID,
                    'type': EVENT_NAME_TO_TYPE['add'],
                    'ts': DatetimeNow(),
                }),
                'COMMIT',
            ],
            inserted_keys=[TEST_DOMAIN_ID],
        )

        raw_data.update({
            'domain_id': TEST_DOMAIN_ID,
            'master_domain_id': 0,
        })
        self.db._serialize_to_eav(domain)
        self.db.check_line(
            'domains',
            raw_data,
            name=domain.domain,
            db='passportdbcentral',
        )
        self.db.check_line(
            'domains_events',
            {
                'type': EVENT_NAME_TO_TYPE['add'],
                'domain_id': TEST_DOMAIN_ID,
                'meta': None,
                'id': 1,
                'ts': DatetimeNow(),
            },
            type=EVENT_NAME_TO_TYPE['add'],
            db='passportdbcentral',
        )

    def test_insert_with_options_new_scheme(self):
        self.domain_data.pop('domid', None)

        domain = Domain().parse(self.domain_data)
        domain.organization_name = 'Organization'
        domain.can_users_change_password = False
        domain.display_master_id = TEST_DOMAIN_ID
        queries = self.serializer.serialize(
            None,
            domain,
            diff(None, domain),
        )

        raw_data = prepare_raw_data(
            domain,
            options='{"1": 0, "2": "Organization", "3": 42}',
        )

        with settings_context(OPTIONS_USE_NEW_SERIALIZATION_SCHEME=True):
            eq_eav_queries(
                queries,
                [
                    'BEGIN',
                    pdt.insert().values(**encode_params_for_db(raw_data)),
                    det.insert().values({
                        'domain_id': TEST_DOMAIN_ID,
                        'type': EVENT_NAME_TO_TYPE['add'],
                        'ts': DatetimeNow(),
                    }),
                    'COMMIT',
                ],
                inserted_keys=[TEST_DOMAIN_ID],
            )
            self.db._serialize_to_eav(domain)
            raw_data.update({
                'domain_id': TEST_DOMAIN_ID,
                'master_domain_id': 0,
            })

        self.db.check_line(
            'domains',
            raw_data,
            name=domain.domain,
            db='passportdbcentral',
        )
        self.db.check_line(
            'domains_events',
            {
                'type': EVENT_NAME_TO_TYPE['add'],
                'domain_id': TEST_DOMAIN_ID,
                'meta': None,
                'id': 1,
                'ts': DatetimeNow(),
            },
            type=EVENT_NAME_TO_TYPE['add'],
            db='passportdbcentral',
        )

    def test_insert_with_aliases(self):
        """
        Проверяем, что сериализатор корректно порождает
        запрос на помещение объекта в БД.
        """
        self.domain_data.pop('domid', None)
        domain = Domain().parse(self.domain_data)
        domain.aliases = [SLAVE_DOMAIN]
        queries = self.serializer.serialize(
            None,
            domain,
            diff(None, domain),
        )

        raw_data = prepare_raw_data(domain)
        alias_data = {
            'enabled': domain.is_enabled,
            'name': SLAVE_DOMAIN,
            'master_domain_id': TEST_DOMAIN_ID,
            'options': '{"can_users_change_password": 1}',
            'ts': DatetimeNow(),
        }

        eq_eav_queries(
            queries,
            [
                'BEGIN',
                pdt.insert().values(**encode_params_for_db(raw_data)),
                det.insert().values({
                    'domain_id': TEST_DOMAIN_ID,
                    'type': EVENT_NAME_TO_TYPE['add'],
                    'ts': DatetimeNow(),
                }),
                pdt.insert().values(**encode_params_for_db(alias_data)),
                det.insert().values({
                    'domain_id': TEST_ALIAS_ID,
                    'type': EVENT_NAME_TO_TYPE['add'],
                    'ts': DatetimeNow(),
                }),
                'COMMIT',
            ],
            inserted_keys=[TEST_DOMAIN_ID, TEST_ALIAS_ID],
        )

        self.db._serialize_to_eav(domain)
        raw_data.update({
            'domain_id': TEST_DOMAIN_ID,
            'master_domain_id': 0,
        })
        alias_data.update({
            'domain_id': TEST_ALIAS_ID,
            'admin_uid': 0,
            'default_uid': 0,
            'mx': False,
            'master_domain_id': TEST_DOMAIN_ID,
            'ts': DatetimeNow(),
        })

        self.db.check_line(
            'domains',
            raw_data,
            name=domain.domain,
            db='passportdbcentral',
        )
        self.db.check_line(
            'domains',
            alias_data,
            name=SLAVE_DOMAIN,
            db='passportdbcentral',
        )
        self.db.check_line(
            'domains_events',
            {
                'type': EVENT_NAME_TO_TYPE['add'],
                'domain_id': TEST_DOMAIN_ID,
                'meta': None,
                'id': 1,
                'ts': DatetimeNow(),
            },
            type=EVENT_NAME_TO_TYPE['add'],
            db='passportdbcentral',
        )

    def test_insert_with_mixedcase_alias(self):
        self.domain_data.pop('domid', None)
        domain = Domain().parse(self.domain_data)
        domain.aliases = [MIXEDCASE_DOMAIN]
        lowercase_domain = MIXEDCASE_DOMAIN.lower()

        raw_data = prepare_raw_data(domain)
        alias_data = {
            'enabled': domain.is_enabled,
            'name': lowercase_domain,
            'master_domain_id': TEST_DOMAIN_ID,
            'options': '{"can_users_change_password": 1}',
            'ts': DatetimeNow(),
        }

        queries = self.serializer.serialize(
            None,
            domain,
            diff(None, domain),
        )
        eq_eav_queries(
            queries,
            [
                'BEGIN',
                pdt.insert().values(**encode_params_for_db(raw_data)),
                det.insert().values({
                    'domain_id': TEST_DOMAIN_ID,
                    'type': EVENT_NAME_TO_TYPE['add'],
                    'ts': DatetimeNow(),
                }),
                pdt.insert().values(**encode_params_for_db(alias_data)),
                det.insert().values({
                    'domain_id': TEST_ALIAS_ID,
                    'type': EVENT_NAME_TO_TYPE['add'],
                    'ts': DatetimeNow(),
                }),
                'COMMIT',
            ],
            inserted_keys=[TEST_DOMAIN_ID, TEST_ALIAS_ID],
        )

        self.db._serialize_to_eav(domain)
        self.db.check(
            'domains',
            'admin_uid',
            0,
            name=lowercase_domain,
            db='passportdbcentral',
        )

    def test_delete(self):
        """
        Проверяем, что удаление домена порождает специфические
        SQL-запросы:
        1) Перенос алиасов аккаунтов домена в список удаленных
        2) Удаление домена и всех его подчиненных
        """
        domain = Domain().parse(self.domain_data)
        self.db._serialize_to_eav(domain)

        queries = self.serializer.serialize(
            domain,
            None,
            diff(domain, None),
        )

        eq_eav_queries(
            queries,
            [
                'BEGIN',
                self._insert_all_pdd_aliases_from_domain_into_removed_aliases_query(domain.id, domain.domain),
                (
                    'DELETE a, s '
                    'FROM aliases a LEFT JOIN suid2 s USING(uid) '
                    'WHERE a.type IN (%s, %s) AND a.value LIKE "42/%%%%"'
                ) % (ALIAS_NAME_TO_TYPE['pdd'], ALIAS_NAME_TO_TYPE['pddalias']),
                'SELECT 1',
                pdt.delete().where(
                    sql_or(
                        pdt.c.domain_id == domain.id,
                        pdt.c.master_domain_id == domain.id,
                    )
                ),
                det.insert().values(
                    type=3,
                    domain_id=domain.id,
                    ts=DatetimeNow(),
                ),
                'COMMIT',
            ],
        )

        self.db._serialize_to_eav(None, old_instance=domain)

        self.db.check_missing(
            'domains',
            name=domain.domain,
            db='passportdbcentral',
        )
        self.db.check_line(
            'domains_events',
            {
                'type': EVENT_NAME_TO_TYPE['add'],
                'domain_id': domain.id,
                'meta': None,
                'id': 1,
                'ts': DatetimeNow(),
            },
            type=EVENT_NAME_TO_TYPE['add'],
            db='passportdbcentral',
        )
        self.db.check_line(
            'domains_events',
            {
                'type': EVENT_NAME_TO_TYPE['delete'],
                'domain_id': domain.id,
                'meta': None,
                'id': 2,
                'ts': DatetimeNow(),
            },
            type=EVENT_NAME_TO_TYPE['delete'],
            db='passportdbcentral',
        )

    def test_simple_update(self):
        """
        Проверяем, что простое обновление одного из полей
        без изменения списка алиасов порождает только один
        запрос UPDATE.
        """
        domain = Domain().parse(self.domain_data)
        s1 = domain.snapshot()
        domain.domain = ANOTHER_DOMAIN
        queries = self.serializer.serialize(
            s1,
            domain,
            diff(s1, domain),
        )
        eq_eav_queries(
            queries,
            [
                'BEGIN',
                pdt.update().values(
                    name=ANOTHER_DOMAIN.encode('utf8'),
                ).where(pdt.c.domain_id == domain.id),
                'COMMIT',
            ],
        )

        self.db._serialize_to_eav(s1)
        self.db._serialize_to_eav(domain, old_instance=s1)
        self.db.check(
            'domains',
            'name',
            ANOTHER_DOMAIN,
            db='passportdbcentral',
        )

    def test_update_with_options_modified(self):
        """
        Проверяем, что изменение любого из установленного списка
        полей вызывает запись соответствующего события в БД.
        """
        domain = Domain().parse(self.domain_data)
        s1 = domain.snapshot()
        domain.organization_name = u'Яндекс'

        queries = self.serializer.serialize(
            s1,
            domain,
            diff(s1, domain),
        )

        events_queries = [
            det.insert().values(
                type=EVENT_NAME_TO_TYPE['options'],
                domain_id=domain.id,
                ts=DatetimeNow(),
            ),
        ]

        eq_eav_queries(
            queries,
            list(chain(
                [
                    'BEGIN',
                    pdt.update().values(
                        options=u'{"can_users_change_password": 1, "display_master_id": 42,'
                                u' "organization_name": "\\u042f\\u043d\\u0434\\u0435\\u043a\\u0441"}'.encode('utf8'),
                    ).where(pdt.c.domain_id == domain.id),
                ],
                events_queries,
                ['COMMIT'],
            )),
        )

        self.db._serialize_to_eav(s1)
        self.db._serialize_to_eav(domain, old_instance=s1)

        for field, value in (
            ('mx', domain.is_yandex_mx),
            ('enabled', domain.is_enabled),
            ('default_uid', domain.default_uid),
        ):
            self.db.check(
                'domains',
                field,
                value,
                db='passportdbcentral',
            )

    def test_update_with_options_removed(self):
        """
        Проверяем, что удаление любого из установленного списка
        полей вызывает запись соответствующего события в БД.
        """
        domain = Domain().parse(self.domain_data)
        s1 = domain.snapshot()
        domain.display_master_id = None

        queries = self.serializer.serialize(
            s1,
            domain,
            diff(s1, domain),
        )

        events_queries = [
            det.insert().values(
                type=EVENT_NAME_TO_TYPE['options'],
                domain_id=domain.id,
                ts=DatetimeNow(),
            ),
        ]

        eq_eav_queries(
            queries,
            list(chain(
                [
                    'BEGIN',
                    pdt.update().values(
                        options=b'{"can_users_change_password": 1}',
                    ).where(pdt.c.domain_id == domain.id),
                ],
                events_queries,
                ['COMMIT'],
            )),
        )

        self.db._serialize_to_eav(s1)
        self.db._serialize_to_eav(domain, old_instance=s1)

        for field, value in (
            ('mx', domain.is_yandex_mx),
            ('enabled', domain.is_enabled),
            ('default_uid', domain.default_uid),
        ):
            self.db.check(
                'domains',
                field,
                value,
                db='passportdbcentral',
            )

    def test_update_with_all_options_removed(self):
        """
        Проверяем, что удаление всех опций запишет в БД пустую строку в поле options.
        """
        self.domain_data['options'] = '{"organization_name": "foo", "display_master_id": 42}'
        domain = Domain().parse(self.domain_data)
        s1 = domain.snapshot()
        domain.organization_name = None
        domain.display_master_id = None

        queries = self.serializer.serialize(
            s1,
            domain,
            diff(s1, domain),
        )

        events_queries = [
            det.insert().values(
                type=EVENT_NAME_TO_TYPE['options'],
                domain_id=domain.id,
                ts=DatetimeNow(),
            ),
        ]

        eq_eav_queries(
            queries,
            list(chain(
                [
                    'BEGIN',
                    pdt.update().values(
                        options=b'',
                    ).where(pdt.c.domain_id == domain.id),
                ],
                events_queries,
                ['COMMIT'],
            )),
        )

        self.db._serialize_to_eav(s1)
        self.db._serialize_to_eav(domain, old_instance=s1)

        for field, value in (
            ('mx', domain.is_yandex_mx),
            ('enabled', domain.is_enabled),
            ('default_uid', domain.default_uid),
        ):
            self.db.check(
                'domains',
                field,
                value,
                db='passportdbcentral',
            )

    def test_update_with_events_generated(self):
        """
        Проверяем, что изменение любого из установленного списка
        полей вызывает запись соответствующего события в БД.
        """
        domain = Domain().parse(self.domain_data)
        s1 = domain.snapshot()
        domain.is_yandex_mx = not domain.is_yandex_mx
        domain.is_enabled = not domain.is_enabled
        domain.default_uid += + 1
        domain.display_master_id += 1

        queries = self.serializer.serialize(
            s1,
            domain,
            diff(s1, domain),
        )

        events_queries = [
            det.insert().values(
                type=EVENT_NAME_TO_TYPE[event_type],
                domain_id=domain.id,
                ts=DatetimeNow(),
            )
            for event_type in ('ena', 'default_uid', 'mx', 'options')
        ]

        eq_eav_queries(
            queries,
            list(chain(
                [
                    'BEGIN',
                    pdt.update().values(
                        mx=domain.is_yandex_mx,
                        enabled=domain.is_enabled,
                        default_uid=domain.default_uid,
                        options=b'{"can_users_change_password": 1, "display_master_id": 43}',
                    ).where(pdt.c.domain_id == domain.id),
                ],
                events_queries,
                ['COMMIT'],
            )),
        )

        self.db._serialize_to_eav(s1)
        self.db._serialize_to_eav(domain, old_instance=s1)

        for field, value in (
            ('mx', domain.is_yandex_mx),
            ('enabled', domain.is_enabled),
            ('default_uid', domain.default_uid),
        ):
            self.db.check(
                'domains',
                field,
                value,
                db='passportdbcentral',
            )

    def test_update_with_additional_alias(self):
        """
        Проверяем, что изменение содержимого объекта
        вместе с модификацией списка алиасов приводит
        к порождению дополнительного запроса на изменение
        головного домена у затронутых алиасов, а также
        обертыванию всех запросов в транзакцию.
        """
        domain = Domain().parse(self.domain_data)
        s1 = domain.snapshot()
        domain.domain = ANOTHER_DOMAIN
        domain.aliases.append(SLAVE_DOMAIN)
        queries = self.serializer.serialize(
            s1,
            domain,
            diff(s1, domain),
        )

        alias_data = {
            'master_domain_id': TEST_DOMAIN_ID,
            'name': SLAVE_DOMAIN,
            'enabled': True,
            'options': '{"can_users_change_password": 1}',
            'ts': DatetimeNow(),
        }
        eq_eav_queries(
            queries,
            [
                'BEGIN',
                pdt.update().values(
                    name=ANOTHER_DOMAIN.encode('utf8'),
                ).where(pdt.c.domain_id == domain.id),
                pdt.insert().values(**encode_params_for_db(alias_data)),
                det.insert().values({
                    'domain_id': TEST_DOMAIN_ID,
                    'type': EVENT_NAME_TO_TYPE['add'],
                    'ts': DatetimeNow(),
                }),
                'COMMIT',
            ],
            inserted_keys=[TEST_DOMAIN_ID],
        )
        raw_data = prepare_raw_data(domain)

        self.db._serialize_to_eav(s1)
        self.db._serialize_to_eav(domain, old_instance=s1)
        self.db.check_table_contents(
            'domains',
            'passportdbcentral',
            [
                merge_dicts(
                    raw_data,
                    dict(
                        name=ANOTHER_DOMAIN,
                        domain_id=TEST_DOMAIN_ID,
                        master_domain_id=0,
                    ),
                ),
                merge_dicts(
                    alias_data,
                    dict(
                        domain_id=TEST_ALIAS_ID,
                        admin_uid=0,
                        default_uid=0,
                        mx=False,
                    ),
                ),
            ]
        )

    def test_update_with_removed_alias(self):
        """
        Проверяем, что изменение содержимого объекта
        вместе с удалением алиаса из списка приводит
        к порождению дополнительного запроса на удаление
        записи об алиасе из БД, а также обертыванию всех
        запросов в транзакцию.
        """
        modified_domain = dict(self.domain_data)
        modified_domain['slaves'] = SLAVE_DOMAIN
        domain = Domain().parse(modified_domain)
        domain.alias_to_id_mapping = {SLAVE_DOMAIN: TEST_ALIAS_ID}
        s1 = domain.snapshot()

        domain.domain = ANOTHER_DOMAIN
        domain.aliases = [ORIGINAL_DOMAIN]
        queries = self.serializer.serialize(
            s1,
            domain,
            diff(s1, domain),
        )

        raw_data = prepare_raw_data(domain)
        alias_data = {
            'master_domain_id': TEST_DOMAIN_ID,
            'name': ORIGINAL_DOMAIN,
            'enabled': True,
            'options': '{"can_users_change_password": 1}',
            'ts': DatetimeNow(),
        }

        eq_eav_queries(
            queries,
            [
                'BEGIN',
                pdt.update().values(
                    name=ANOTHER_DOMAIN.encode('utf8'),
                ).where(pdt.c.domain_id == domain.id),
                pdt.delete().where(
                    pdt.c.name.in_([SLAVE_DOMAIN.encode('utf8')]),
                ),
                det.insert().values({
                    'domain_id': TEST_ALIAS_ID,
                    'type': EVENT_NAME_TO_TYPE['delete'],
                    'ts': DatetimeNow(),
                }),
                pdt.insert().values(**encode_params_for_db(alias_data)),
                det.insert().values({
                    'domain_id': TEST_DOMAIN_ID,
                    'type': EVENT_NAME_TO_TYPE['add'],
                    'ts': DatetimeNow(),
                }),
                'COMMIT',
            ],
            inserted_keys=[TEST_DOMAIN_ID],
        )

        self.db._serialize_to_eav(s1)
        self.db._serialize_to_eav(domain, old_instance=s1)
        self.db.check_table_contents(
            'domains',
            'passportdbcentral',
            [
                merge_dicts(
                    raw_data,
                    dict(
                        name=ANOTHER_DOMAIN,
                        domain_id=TEST_DOMAIN_ID,
                        master_domain_id=0,
                    ),
                ),
                merge_dicts(
                    alias_data,
                    dict(
                        domain_id=TEST_ALIAS_ID,
                        admin_uid=0,
                        default_uid=0,
                        mx=False,
                    ),
                ),
            ]
        )

    def test_update_with_all_aliases_removed(self):
        """
        Проверяем, что удаление всех алиасов из списка приводит
        к порождению запроса в БД.
        """
        modified_domain = dict(self.domain_data)
        modified_domain['slaves'] = SLAVE_DOMAIN
        domain = Domain().parse(modified_domain)
        domain.alias_to_id_mapping = {SLAVE_DOMAIN: TEST_ALIAS_ID}
        s1 = domain.snapshot()

        domain.aliases = []
        queries = self.serializer.serialize(
            s1,
            domain,
            diff(s1, domain),
        )

        raw_data = prepare_raw_data(domain)
        eq_eav_queries(
            queries,
            [
                'BEGIN',
                pdt.delete().where(
                    pdt.c.name.in_([SLAVE_DOMAIN.encode('utf8')]),
                ),
                det.insert().values({
                    'domain_id': TEST_ALIAS_ID,
                    'type': EVENT_NAME_TO_TYPE['delete'],
                    'ts': DatetimeNow(),
                }),
                'COMMIT',
            ],
        )

        self.db._serialize_to_eav(s1)
        self.db._serialize_to_eav(domain, old_instance=s1)
        self.db.check_table_contents(
            'domains',
            'passportdbcentral',
            [
                merge_dicts(
                    raw_data,
                    dict(
                        name=ORIGINAL_DOMAIN,
                        domain_id=TEST_DOMAIN_ID,
                        master_domain_id=0,
                    ),
                ),
            ]
        )

    @raises(ValueError)
    def test_error_idna_domain_not_encodable(self):
        self.domain_data['domain'] = u'б' * 128

        domain = Domain().parse(self.domain_data)
        queries = self.serializer.serialize(
            None,
            domain,
            diff(None, domain),
        )
        for query in queries:
            if isinstance(query, DbTransactionContainer):
                list(query.get_queries())
