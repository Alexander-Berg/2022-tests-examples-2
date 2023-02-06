# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import json
import logging

from passport.backend.qa.test_user_service.tus_api.db_schema import user_table
from passport.backend.qa.test_user_service.tus_api.exceptions import TemporarilyUnavailableError
from passport.backend.qa.test_user_service.tus_api.settings import TUS_ENV
from passport.backend.qa.test_user_service.tus_api.utils import (
    rename_exception_decorator,
    retry_decorator,
)
from sqlalchemy import (
    create_engine,
    text,
)
from sqlalchemy.exc import (
    InterfaceError,
    OperationalError,
)
from sqlalchemy.sql import (
    delete,
    expression,
    literal_column,
    select,
)


log = logging.getLogger(__name__)


def _apply_whereclause(clause, **kwargs):
    for key in kwargs:
        clause = clause.where(literal_column(key) == kwargs[key])
    return clause


class DB(object):
    def __init__(self, db_config):
        db_string = ('postgres+psycopg2://'
                     '%(user)s:%(password)s@%(host)s:%(port)s/%(db_name)s'
                     '?target_session_attrs=read-write' % db_config[TUS_ENV])
        self.engine = create_engine(db_string)

    @rename_exception_decorator((OperationalError, InterfaceError), TemporarilyUnavailableError)
    @retry_decorator(exception=(OperationalError, InterfaceError))
    def run_queries(self, *queries):
        """
        Query should be function with only one parameter - connection
        Function returns list with results for each query
        """
        result = []
        with self.engine.begin() as connection:
            for query in queries:
                result.append(query(connection))
        return result

    def make_add_query(self, table, **kwargs):
        """
        Inserts to table
        Returns dict with entity data
        """

        def _query(connection):
            log.debug('Inserting %s to %s' % (str(kwargs), table.name))
            connection.execute(table.insert().values(**kwargs))
            return kwargs

        return _query

    def make_remove_query(self, table, **kwargs):
        """
        Returns True if something was removed, False if nothing was removed
        """

        def _query(connection):
            rowcount = connection.execute(_apply_whereclause(delete(table), **kwargs)).rowcount
            log.debug('Removing %s from %s. Removed %d' % (str(kwargs), table.name, rowcount))
            return rowcount > 0

        return _query

    def update_account_lock(self, uid, new_lock_ts, ignore_current_lock, env):
        """
        Returns True if lock was updated, False if lock was not changed
        """
        clause = user_table.update().where(
            expression.and_(
                user_table.c.uid == uid,
                user_table.c.env == env,
            )
        ).values(locked_until=new_lock_ts)

        if not ignore_current_lock:
            clause = clause.where(user_table.c.locked_until < datetime.now())

        def _query(connection):
            rowcount = connection.execute(clause).rowcount
            log.debug('Updating lock for uid %s env %s until %s. Updated %d' % (uid, env, new_lock_ts, rowcount))
            return rowcount > 0

        return _query

    def get_user_by_uid(self, uid, env):
        sql = text('''
                    SELECT uid, login, password, locked_until, delete_at
                        FROM user_table
                        WHERE user_table.uid = :uid
                        AND user_table.env = :env
                        AND (user_table.delete_at IS NULL OR user_table.delete_at > :time_now)
                ''')

        def _query(connection):
            return connection.execute(sql, uid=uid, env=env, time_now=datetime.now()).fetchall()

        return _query

    def get_user_by_login(self, login, env):
        sql = text('''
                    SELECT uid, login, password, locked_until, delete_at
                        FROM user_table
                        WHERE user_table.login = :login
                        AND user_table.env = :env
                        AND (user_table.delete_at IS NULL OR user_table.delete_at > :time_now)
                ''')

        def _query(connection):
            return connection.execute(sql, login=login, env=env, time_now=datetime.now()).fetchall()

        return _query

    def get_uids_with_tags(self, consumer_name, client_login, offset, env):
        sql = text('''
            SELECT user_table.uid
            FROM user_table
                JOIN consumer_test_accounts_table
                    ON user_table.uid = consumer_test_accounts_table.uid
            WHERE consumer_test_accounts_table.consumer_name = :consumer_name
                AND user_table.env = :env
                AND consumer_test_accounts_table.consumer_name IN (
                    SELECT consumer_name FROM consumer_clients_table WHERE login = :client_login
                )
            ORDER BY user_table.uid ASC
            OFFSET :offset
            LIMIT 100;
        ''')

        def _query(connection):
            return connection.execute(
                sql, consumer_name=consumer_name, client_login=client_login, env=env, offset=offset,
            ).fetchall()

        return _query

    def get_tag_ids(self, tag_list):
        sql = text('SELECT tag_id FROM tag_table WHERE tag IN :tags;')

        def _query(connection):
            return connection.execute(sql, tags=tuple(tag_list)).fetchall()

        return _query

    def get_tag_list_for_uid(self, uid, env):
        sql = text('''
            SELECT tag_table.tag FROM tag_table JOIN user_tags_table USING (tag_id) WHERE user_tags_table.uid = :uid
            AND user_tags_table.env = :env;
        ''')

        def _query(connection):
            return connection.execute(sql, uid=uid, env=env).fetchall()

        return _query

    def get_consumer_list_for_uid_query(self, uid, env):
        sql = text('''
            SELECT RIGHT(tag_table.tag, -LENGTH('tus_consumer_value=')) FROM tag_table JOIN user_tags_table USING (tag_id)
            WHERE user_tags_table.uid = :uid AND tag_table.tag LIKE 'tus_consumer_value=%' AND user_tags_table.env = :env;
        ''')

        def _query(connection):
            return connection.execute(sql, uid=uid, env=env).fetchall()

        return _query

    def get_account_with_uid(self, consumer_name, uid, client_login, env):
        sql = text('''
        SELECT user_table.uid, user_table.login, user_table.password, user_table.locked_until, user_table.delete_at
        FROM user_table
            JOIN consumer_test_accounts_table
                ON user_table.uid = consumer_test_accounts_table.uid
                AND user_table.env = consumer_test_accounts_table.env
        WHERE user_table.uid = :uid
            AND consumer_test_accounts_table.consumer_name = :consumer_name
            AND consumer_test_accounts_table.consumer_name IN (
                SELECT consumer_name
                FROM consumer_clients_table
                WHERE login = :client_login
            )
            AND user_table.env = :env
            AND (user_table.delete_at IS NULL OR user_table.delete_at > :time_now);
        ''')

        def _query(connection):
            return connection.execute(
                sql, consumer_name=consumer_name, uid=uid, client_login=client_login, env=env, time_now=datetime.now()
            ).fetchall()

        return _query

    def get_account_with_login(self, consumer_name, login, client_login, env):
        sql = text('''
        SELECT user_table.uid, user_table.login, user_table.password, user_table.locked_until, user_table.delete_at
        FROM user_table
            JOIN consumer_test_accounts_table
                ON user_table.uid = consumer_test_accounts_table.uid
                AND user_table.env = consumer_test_accounts_table.env
        WHERE user_table.login = :login
            AND consumer_test_accounts_table.consumer_name = :consumer_name
            AND consumer_test_accounts_table.consumer_name IN (
                SELECT consumer_name
                FROM consumer_clients_table
                WHERE login = :client_login
            )
            AND user_table.env = :env
            AND (user_table.delete_at IS NULL OR user_table.delete_at > :time_now);
        ''')

        def _query(connection):
            return connection.execute(
                sql, consumer_name=consumer_name, login=login, client_login=client_login, env=env,
                time_now=datetime.now()
            ).fetchall()

        return _query

    def get_accounts_with_tags(self, consumer_name, tags, ignore_locks, client_login, env):
        if not ignore_locks:
            expiration_time = datetime.now()
        else:
            expiration_time = datetime.now() + timedelta(weeks=52)  # year

        sql = text('''
        SELECT user_table.uid, user_table.login, user_table.password, user_table.locked_until, user_table.delete_at
        FROM user_table
            JOIN consumer_test_accounts_table
                ON user_table.uid = consumer_test_accounts_table.uid
        WHERE consumer_test_accounts_table.consumer_name = :consumer_name
            AND consumer_test_accounts_table.consumer_name IN (
                SELECT consumer_name FROM consumer_clients_table WHERE login = :client_login
            )
            AND user_table.uid IN (
                SELECT user_tags_table.uid
                FROM user_tags_table
                    JOIN tag_table
                        ON user_tags_table.tag_id = tag_table.tag_id
                WHERE tag_table.tag in :tags
                GROUP BY user_tags_table.uid
                HAVING count(DISTINCT user_tags_table.tag_id) = :tags_length
            )
            AND user_table.env = :env
            AND (user_table.delete_at IS NULL OR user_table.delete_at > :time_now)
            AND user_table.locked_until < :expiration_time
        LIMIT 100;
        ''')

        def _query(connection):
            return connection.execute(
                sql, consumer_name=consumer_name, tags=tuple(tags), tags_length=len(tags),
                expiration_time=expiration_time, client_login=client_login, env=env, time_now=datetime.now()
            ).fetchall()

        return _query

    def add(self, table, **kwargs):
        return self.run_queries(self.make_add_query(table, **kwargs))[0]

    def remove(self, table, **kwargs):
        return self.run_queries(self.make_remove_query(table, **kwargs))[0]

    def get(self, table, **kwargs):
        """
        Returns list
        """
        return self.run_queries(lambda connection: [dict(row) for row in connection.execute(
            _apply_whereclause(select([table]), **kwargs)).fetchall()])[0]


_db = None


def get_db():
    global _db
    if _db is None:
        db_config = load_db_config()
        _db = DB(db_config)
    return _db


def load_db_config():
    with open('db.conf') as db_json:
        return json.load(db_json)
