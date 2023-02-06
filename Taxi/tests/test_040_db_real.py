#!/usr/bin/env python3

import os
import sys

from easytap import Tap

import pytest

sys.path.insert(0, '.')
sys.path.insert(0, '..')

SQL_DIR = os.path.join(os.path.dirname(__file__), 'sql')

DSN = os.getenv('PG_DSN', '').replace('postgres://', 'pq://')
SKIP_COND = DSN == ''
SKIP_TEXT = 'Please export PG_DSN to run the test list'

# pylint: disable=redefined-outer-name,unused-import
try:
    import psycopg2
except ModuleNotFoundError:
    SKIP_COND = True
    SKIP_TEXT = 'Please install python3-postgresql first'


@pytest.mark.skipif(SKIP_COND, reason=SKIP_TEXT)
def test_perform():
    tap = Tap(5, 'perform')
    import dbtpl.pg

    db = dbtpl.pg.connect(DSN, 'tests/sql/dbtpl.pg')
    tap.ok(db, 'Присоеденились')

    tap.ok(db.perform('create_table.sql', {'name': 'tst'}),
           'perform: create table')
    tap.ok(db.perform('insert.sql', {'lst': ['a', 'b', 'c']}),
           'perform: insert')
    tap.ok(db.perform('delete.sql', {'lst': ['a', 'b', 'c']}),
           'perform: delete')
    tap.ok(db.perform('delete.sql', {'lst': ['a', 'b', 'c']}),
           'perform: repeat (no deleted rows)')
    assert tap.done_testing()


@pytest.mark.skipif(SKIP_COND, reason=SKIP_TEXT)
def test_single():
    tap = Tap(7, 'single')
    import dbtpl.pg
    import psycopg2.extras

    db = dbtpl.pg.connect(DSN, 'tests/sql/dbtpl.pg')
    tap.ok(db, 'Присоеденились')
    tap.ok(db.perform('delete.sql', {'lst': ['a', 'b', 'c']}),
           'perform: repeat (no deleted rows)')
    tap.ok(db.perform('insert.sql', {'lst': ['a', 'b', 'c']}),
           'perform: insert')

    res = db.single('select.sql', {'lst': ('a')})
    tap.ok(res, 'select returned one tuple')
    tap.isa_ok(res, psycopg2.extras.DictRow, 'is a row')

    tap.eq_ok(res['name'], 'a', 'name')
    tap.isa_ok(res['id'], int, 'id')
    assert tap.done_testing()


@pytest.mark.skipif(SKIP_COND, reason=SKIP_TEXT)
def test_select():
    tap = Tap(9, 'select')
    import dbtpl.pg
    import psycopg2.extras

    db = dbtpl.pg.connect(DSN, 'tests/sql/dbtpl.pg')
    tap.ok(db, 'Присоеденились')
    tap.ok(db.perform('delete.sql', {'lst': ['a', 'b', 'c']}),
           'perform: repeat (no deleted rows)')
    tap.ok(db.perform('insert.sql', {'lst': ['a', 'b', 'c']}),
           'perform: insert')

    res = db.select('select.sql', {'lst': ('a', 'b')})
    tap.ok(res, 'select returned several tuples')
    tap.isa_ok(res, list, 'returned list')

    tap.eq_ok(len(res), 2, '2 tuples')

    tap.isa_ok(res[0], psycopg2.extras.DictRow, 'is a row')
    tap.eq_ok(res[0]['name'], 'a', 'name')
    tap.isa_ok(res[0]['id'], int, 'id')
    assert tap.done_testing()


@pytest.mark.skipif(SKIP_COND, reason=SKIP_TEXT)
def test_txn():
    tap = Tap(11, 'transaction')
    import dbtpl.pg
    db = dbtpl.pg.connect(DSN, 'tests/sql/dbtpl.pg', autocommit=False)
    tap.ok(not db.db.autocommit, 'Автокоммит отключен')
    tap.ok(db, 'Присоеденились')
    tap.ok(db.perform('delete.sql', {'lst': ['a', 'b', 'c']}),
           'perform: repeat (no deleted rows)')

    tap.ok(not db.select('select.sql', {'lst': ('a', 'b')}), 'empty')
    with db.cursor() as x:
        tap.ok(x.perform('insert.sql', {'lst': ['a', 'b', 'c']}),
               'perform: insert/rollback')
        db.rollback()
    tap.ok(not db.select('select.sql', {'lst': ('a', 'b')}), 'empty')

    try:
        with db.cursor() as x:
            tap.ok(x.perform('insert.sql', {'lst': ['a', 'b', 'c']}),
                   'perform: insert/rollback')
            raise RuntimeError('tst')
    except RuntimeError as exc:
        tap.is_ok(str(exc), 'tst', 'Exception text')
    tap.ok(not db.select('select.sql', {'lst': ('a', 'b')}), 'empty')

    with db.cursor() as x:
        tap.ok(x.perform('insert.sql', {'lst': ['a', 'b', 'c']}),
               'perform: insert/rollback')

    res = db.select('select.sql', {'lst': ('a', 'b')})
    tap.is_ok(len(res), 2, '2 tuples')
    assert tap.done_testing()


@pytest.mark.skipif(SKIP_COND, reason=SKIP_TEXT)
def test_inline():
    tap = Tap(10, 'inline')
    import dbtpl.pg
    import psycopg2.extras
    db = dbtpl.pg.connect(DSN, 'tests/sql/dbtpl.pg')
    tap.ok(db, 'Присоеденились')
    tap.ok(db.inline.perform('DROP TABLE "{{ t |i }}"', {'t': 'tst'}),
           'drop test table')
    res = db.inline.single('SELECT {{ name }}::TEXT "name"', {'name': 'Vasya'})
    tap.isa_ok(res, psycopg2.extras.DictRow, 'is a row')
    tap.eq_ok(res['name'], 'Vasya', 'row .name')

    res = db.inline.select(
        'SELECT "column1" AS "name" FROM (VALUES ({{name1}}), ({{name2}})) t',
        {'name1': 'Vasya', 'name2': 'Petya'})
    tap.isa_ok(res, list, 'select result is list')
    tap.eq_ok(len(res), 2, 'count of elements')

    tap.isa_ok(res[0], psycopg2.extras.DictRow, 'is a row')
    tap.eq_ok(res[0]['name'], 'Vasya', 'name')
    tap.isa_ok(res[1], psycopg2.extras.DictRow, 'is a row')
    tap.eq_ok(res[1]['name'], 'Petya', 'name')

    assert tap.done_testing()
