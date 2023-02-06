#!/usr/bin/env python3

import json
import os
import sys

from easytap import Tap

import pytest

sys.path.insert(0, '.')
sys.path.insert(0, '..')

SQL_DIR = os.path.join(os.path.dirname(__file__), 'sql/dbtpl.asyncpg')


SKIP_COND = False
SKIP_TEXT = None

# pylint: disable=unused-import
try:
    import asyncpg      # noqa
except ModuleNotFoundError:
    SKIP_COND = True
    SKIP_TEXT = 'asyncpg is not installed'

if not os.getenv('PG_DSN', ''):
    SKIP_COND = True
    SKIP_TEXT = 'PG_DSN is not defined'
else:
    DSN = os.getenv('PG_DSN', '').replace('pq://', 'postgresql://')


@pytest.mark.skipif(SKIP_COND, reason=SKIP_TEXT)
async def test_main():

    tap = Tap(62, 'async tests')
    tap.passed('Inside async')

    import dbtpl.asyncpg

    db = await dbtpl.asyncpg.connect(
        DSN,
        sql_dir=SQL_DIR,
        json_encoder=lambda x: json.dumps({'js': x}))
    tap.ok(db, 'Connection established')

    tap.isa_ok(db.last_sql, tuple, 'last request is tuple')
    tap.ok(not db.last_sql, 'last request is empty tuple')

    async def file_tests(db):
        tap.note('run file tests')
        res = await db.single('single-select.sql', {'a': 'b'})
        tap.eq_ok(dict(res), {'a': 'b'}, 'select single')
        tap.isa_ok(db.last_sql, tuple, 'last request is tuple')
        tap.ok(db.last_sql, 'last request is nonempty tuple')
        tap.like(db.last_sql[0], r'SELECT \$1::TEXT AS "a"', 'SQL text')
        tap.eq_ok(db.last_sql[1], ['b'], 'bind vars')

        res = await db.select('multi-select.sql', {'a': 'A!', 'b': 'B!'})
        tap.eq_ok(tuple(map(dict, res)),
                  ({'a': 'a', 'b': 'b'},
                   {'a': 'A!', 'b': 'B!'}), 'results')

        tap.isa_ok(db.last_sql, tuple, 'last request is tuple')
        tap.ok(db.last_sql, 'last request is nonempty tuple')
        tap.unlike(db.last_sql[0], r'SELECT \$1::TEXT AS "a"', 'SQL text')
        tap.like(db.last_sql[0], r'SELECT', 'SQL text')
        tap.eq_ok(db.last_sql[1], ['a', 'b', 'A!', 'B!'], 'bind vars')

        res = await db.perform('nothing-select.sql')
        tap.is_ok(res, True, 'perform')

        tap.ok(db.last_sql, 'last request is nonempty tuple')
        tap.like(db.last_sql[0], r'WITH', 'SQL text')
        tap.eq_ok(db.last_sql[1], ['a', 'b'], 'bind vars')

    async def inline_tests(db):
        tap.note('run inline tests')
        res = await db.inline.single('SELECT {{ a }}::TEXT as a', {'a': 'A!'})
        tap.eq_ok(dict(res), {'a': 'A!'}, 'inline single result')
        tap.ok(db.last_sql, 'last request is nonempty tuple')
        tap.like(db.last_sql[0], r'SELECT\s\$1::TEXT as a', 'SQL text')
        tap.eq_ok(db.last_sql[1], ['A!'], 'bind vars')

        res = await db.inline.select(
            'select generate_series(1,2) AS id, {{a}}::TEXT AS a;',
            {'a': 'A!'})
        tap.eq_ok(tuple(map(dict, res)),
                  ({'id': 1, 'a': 'A!'},
                   {'id': 2, 'a': 'A!'}), 'results')
        tap.ok(db.last_sql, 'last request is nonempty tuple')
        tap.like(db.last_sql[0], r'generate_series', 'SQL text')
        tap.eq_ok(db.last_sql[1], ['A!'], 'bind vars')

        res = await db.inline.perform(
            "SELECT 1 FROM (VALUES({{'a'}}, {{'b'}})) AS t WHERE FALSE")
        tap.is_ok(res, True, 'perform')

        tap.ok(db.last_sql, 'last request is nonempty tuple')
        tap.like(db.last_sql[0], r'SELECT.*VALUES', 'SQL text')
        tap.eq_ok(db.last_sql[1], ['a', 'b'], 'bind vars')

        res = await db.inline.single(
            'SELECT {{ jsv |j }}::JSON AS a', {'jsv': {'a': 'b'}})
        tap.eq(dict(res),
               {'a': json.dumps({'js': {'a': 'b'}})}, 'json_encoder')

    await file_tests(db)
    await inline_tests(db)

    pool = await dbtpl.asyncpg.create_pool(
        DSN,
        sql_dir=SQL_DIR,
        json_encoder=lambda x: json.dumps({'js': x}))
    tap.ok(pool, 'pool created')

    async with pool.acquire() as dbh:
        tap.ok(dbh, 'connection from pool')
        await file_tests(dbh)
        await inline_tests(dbh)

    assert tap.done_testing()
