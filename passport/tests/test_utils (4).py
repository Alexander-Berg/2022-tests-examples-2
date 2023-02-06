# -*- coding: utf-8 -*-

from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.db.faker.db_utils import compile_query_with_dialect
from passport.backend.core.db.schemas import (
    aliases_table,
    attributes_table,
    passman_recovery_keys_table,
    tracks_table,
)
from passport.backend.core.db.utils import (
    delete_with_limit,
    insert_with_on_duplicate_key_append,
    insert_with_on_duplicate_key_increment,
    insert_with_on_duplicate_key_update,
    insert_with_on_duplicate_key_update_if_equals,
    is_on_duplicate_key_append_insert,
    is_on_duplicate_key_update_insert,
    with_ignore_prefix,
)
from sqlalchemy.dialects import (
    mysql,
    sqlite,
)


def test_insert_binary():
    insert = attributes_table.insert(mysql_binary_value_ids=[-1]).values(
        uid=1,
        type=2,
        value='value',
    )
    eq_(
        str(compile_query_with_dialect(insert, mysql.dialect())),
        'INSERT INTO attributes (uid, type, value) VALUES (%s, %s, _binary %s)',
    )


def test_insert_several_binary_values():
    insert = passman_recovery_keys_table.insert(mysql_binary_value_ids=[1, 2]).values(
        uid=1,
        key_id='foo',
        recovery_key='bar',
    )
    eq_(
        str(compile_query_with_dialect(insert, mysql.dialect())),
        'INSERT INTO passman_recovery_keys (uid, key_id, recovery_key) VALUES (%s, _binary %s, _binary %s)',
    )


def test_with_ignore_prefix():
    expression = with_ignore_prefix(aliases_table.insert()).values(uid=1, type=1, value='value', surrogate_type='value')
    ok_(str(compile_query_with_dialect(expression, mysql.dialect())).startswith('INSERT IGNORE'))
    ok_(str(compile_query_with_dialect(expression, sqlite.dialect())).startswith('INSERT OR IGNORE'))


def test_insert_with_on_duplicate_key_update():
    insert = insert_with_on_duplicate_key_update(aliases_table, ['value']).values(
        uid=1,
        type=1,
        value='value',
        surrogate_type='value',
    )
    ok_(
        str(compile_query_with_dialect(insert, mysql.dialect())).endswith(
            'ON DUPLICATE KEY UPDATE value = VALUES(value)',
        ),
    )

    sqlite_query = str(compile_query_with_dialect(insert, sqlite.dialect())).upper()
    ok_('ON DUPLICATE KEY UPDATE value = VALUES(value)' not in sqlite_query)
    ok_(sqlite_query.startswith('INSERT OR REPLACE'))


def test_insert_with_on_duplicate_key_update_binary():
    insert = insert_with_on_duplicate_key_update(attributes_table, ['value'], binary_value_ids=[-1]).values(
        uid=1,
        type=2,
        value='value',
    )
    eq_(
        str(compile_query_with_dialect(insert, mysql.dialect())),
        'INSERT INTO attributes (uid, type, value) VALUES (%s, %s, _binary %s) '
        'ON DUPLICATE KEY UPDATE value = VALUES(value)',
    )
    eq_(
        str(compile_query_with_dialect(insert, sqlite.dialect())),
        'INSERT OR REPLACE INTO attributes (uid, type, value) VALUES (?, ?, ?)',
    )


def test_insert_with_on_duplicate_key_update_if_equals():
    key, old_value, new_value = 'value', 'old-value', 'new-value'
    insert = insert_with_on_duplicate_key_update_if_equals(attributes_table, [key], key, old_value).values(
        uid=1,
        type=13,
        value=new_value,
    )
    q = str(compile_query_with_dialect(insert, mysql.dialect()))
    expected = 'ON DUPLICATE KEY UPDATE %(key)s = IF(%(key)s = "%(expected)s", VALUES(%(key)s), %(key)s)' % {
        'key': key,
        'expected': old_value,
    }
    ok_(
        q.endswith(expected),
        [q, expected]
    )

    sqlite_query = str(compile_query_with_dialect(insert, sqlite.dialect())).upper()
    ok_('ON DUPLICATE KEY UPDATE %s = ' % key not in sqlite_query)
    ok_(sqlite_query.startswith('INSERT OR REPLACE'))


@raises(RuntimeError)
def test_insert_with_on_duplicate_key_update_if_equals_params_error():
    uid_key, key, old_value, new_value = 'uid', 'value', 'old-value', 'new-value'
    insert_with_on_duplicate_key_update_if_equals(attributes_table, [key, uid_key], key, old_value).values(
        uid=1,
        type=13,
        value=new_value,
    )


def test_insert_with_on_duplicate_key_update_if_equals_else_null():
    key, old_value, new_value = u'value', u'old-value', u'new-value'
    insert = insert_with_on_duplicate_key_update_if_equals(attributes_table, [key], key, old_value, True).values(
        uid=1,
        type=13,
        value=new_value,
    )
    q = str(compile_query_with_dialect(insert, mysql.dialect()))
    expected = 'ON DUPLICATE KEY UPDATE %(key)s = IF(%(key)s = "%(expected)s", VALUES(%(key)s), NULL)' % {
        'key': key,
        'expected': old_value,
    }
    ok_(
        q.endswith(expected),
        [q, expected]
    )

    sqlite_query = str(compile_query_with_dialect(insert, sqlite.dialect())).upper()
    ok_('ON DUPLICATE KEY UPDATE %s = ' % key not in sqlite_query)
    ok_(sqlite_query.startswith('INSERT OR REPLACE'))


def test_is_on_duplicate_key_update_insert():
    insert = insert_with_on_duplicate_key_update(aliases_table, ['value']).values(
        uid=1,
        type=1,
        value='value',
        surrogate_type='value',
    )
    eq_(is_on_duplicate_key_update_insert(insert), ['value'])

    insert = aliases_table.insert().values(uid=1, type=1, value='value', surrogate_type='value')
    eq_(is_on_duplicate_key_update_insert(insert), None)


def test_insert_with_on_duplicate_key_append():
    insert = insert_with_on_duplicate_key_append(aliases_table, ['value']).values(
        uid=1,
        type=1,
        value='value',
        surrogate_type='value',
    )
    ok_(
        str(compile_query_with_dialect(insert, mysql.dialect())).endswith(
            'ON DUPLICATE KEY UPDATE value = CONCAT(value, \';\', VALUES(value))',
        ),
    )

    sqlite_query = str(compile_query_with_dialect(insert, sqlite.dialect())).upper()
    ok_('ON DUPLICATE KEY UPDATE value = CONCAT(value, \';\', VALUES(value))' not in sqlite_query)
    ok_(sqlite_query.startswith('INSERT OR REPLACE'))


def test_is_on_duplicate_key_append_insert():
    insert = insert_with_on_duplicate_key_append(aliases_table, ['value']).values(
        uid=1,
        type=1,
        value='value',
        surrogate_type='value',
    )
    eq_(is_on_duplicate_key_append_insert(insert), ['value'])

    insert = aliases_table.insert().values(uid=1, type=1, value='value', surrogate_type='value')
    eq_(is_on_duplicate_key_append_insert(insert), None)


def test_insert_with_on_duplicate_key_increment():
    insert = insert_with_on_duplicate_key_increment(attributes_table, 'value').values(
        uid=1,
        type=1,
        value='value',
    )
    expected_odk_increment_statement = 'ON DUPLICATE KEY UPDATE value = value + 1'
    ok_(
        str(compile_query_with_dialect(insert, mysql.dialect())).endswith(
            expected_odk_increment_statement,
        ),
    )

    sqlite_query = str(compile_query_with_dialect(insert, sqlite.dialect())).upper()
    ok_(expected_odk_increment_statement not in sqlite_query)
    ok_(sqlite_query.startswith('INSERT OR REPLACE'))


def test_delete_with_limit():
    delete = delete_with_limit(tracks_table, 100)

    for dialect in (mysql.dialect(), sqlite.dialect()):
        eq_(
            str(compile_query_with_dialect(delete, dialect)),
            'DELETE FROM tracks LIMIT 100',
        )
