# -*- coding: utf-8 -*-
from collections import defaultdict

import mock
from passport.backend.oauth.core.db.eav.attributes import serialize_attribute
from passport.backend.oauth.core.db.eav.dbmanager import (
    _DBManager,
    get_dbm,
)
from passport.backend.oauth.core.db.eav.schemas import (
    central_metadata,
    shard_metadata,
)
from passport.backend.oauth.core.db.eav.sharder import (
    _Sharder,
    build_range_shard_function,
    get_sharder,
)


class FakeDB(object):
    schemes_metadata = (
        (central_metadata, 'oauthdbcentral'),
        (shard_metadata, 'oauthdbshard1'),
        (shard_metadata, 'oauthdbshard2'),
    )

    default_db_config = {
        'master': {
            'driver': 'sqlite',
            'database': ':memory:',
        },
    }

    default_sharding_config = {
        'token': {1: 'oauthdbshard1', 2: 'oauthdbshard2'},
    }
    default_shard_ranges = [(1, 0), (2, 20000000)]

    def __init__(self, db_config=None, sharding_config=None):
        self.config = db_config or self.default_db_config
        self.sharding_config = sharding_config or self.default_sharding_config
        self._dbms_patch = mock.patch(
            'passport.backend.oauth.core.db.eav.dbmanager._dbms',
            defaultdict(lambda: mock.Mock(wraps=_DBManager())),
        )
        self._sharders_patch = mock.patch(
            'passport.backend.oauth.core.db.eav.sharder._sharders',
            defaultdict(lambda: mock.Mock(wraps=_Sharder())),
        )
        self.shard_function = build_range_shard_function(self.default_shard_ranges)

    def start(self):
        self._dbms_patch.start()
        self._sharders_patch.start()

        for metadata, dbname in self.schemes_metadata:
            dbm = get_dbm(dbname)
            dbm.configure(self.config)
            metadata.create_all(dbm._master.select_engine())
        for table_name, config in self.sharding_config.items():
            sharder = get_sharder(table_name)
            sharder.configure(config, shard_function=self.shard_function)

    def stop(self):
        for metadata, dbname in self.schemes_metadata:
            metadata.drop_all(get_dbm(dbname)._master.select_engine())
        self._sharders_patch.stop()
        self._dbms_patch.stop()

    def reset_mocks(self):
        get_dbm('oauthdbcentral').reset_mock()
        get_dbm('oauthdbshard1').reset_mock()
        get_dbm('oauthdbshard2').reset_mock()

    def query_count(self, db):
        return get_dbm(db).execute.call_count

    def transaction_count(self, db):
        return get_dbm(db).transaction.call_count

    def get_queries(self, db):
        return [
            q.to_sql()
            for q in get_dbm(db).execute.call_args_list[0][0]
        ]

    def get_transaction_queries(self, db, transaction_index=-1):
        return [
            q.to_sql()
            for q in get_dbm(db).transaction.call_args_list[transaction_index][0][0]._queries
        ]

    def get_table(self, table_name, dbname):
        for metadata, name in self.schemes_metadata:
            if dbname == name:
                return metadata.tables[table_name]
        raise KeyError('No such table "%s" in db "%s"' % (table_name, dbname))  # pragma: no cover

    def _make_query(self, table, query, field):
        if table.name.endswith('attributes'):
            entity = table.name.rsplit('_', 1)[0]
            attr_type, _ = serialize_attribute(entity, 0, field, '')
            query = query.where(table.c.type == attr_type)
        return query

    def select(self, db_name, table_name, field=None, limit=None, **kwargs):
        table = self.get_table(table_name, db_name)
        query = self._make_query(table, table.select(), field)
        for key, val in kwargs.items():
            query = query.where(table.c[key] == val)
        if limit:
            query = query.limit(limit)
        return get_dbm(db_name)._master.select_engine().execute(query).fetchall()

    def get(self, db_name, table_name, field, **kwargs):
        result = self.select(db_name, table_name, field=field, limit=1, **kwargs)
        if not result:
            return None
        result = result[0]

        if table_name.endswith('attributes'):
            return result['value']
        return result[field]

    def insert(self, db_name, table_name, **kwargs):
        table = self.get_table(table_name, db_name)
        query = table.insert().values(**kwargs)
        get_dbm(db_name)._master.select_engine().execute(query)

    def check(self, db_name, table_name, field, expected_value, **kwargs):
        """Проверим, что в БД записано ожидаемое значение в указанной таблице и столбце"""
        value = self.get(db_name, table_name, field, **kwargs)
        if value != expected_value:
            raise AssertionError('%r not equals %r' % (value, expected_value))  # pragma: no cover

    def check_missing(self, db_name, table_name, field=None, **kwargs):
        """Проверим отсутствие записи в БД"""
        value = self.get(db_name, table_name, field=field, **kwargs)
        if value is not None:
            raise AssertionError('%r is not None' % value)  # pragma: no cover
