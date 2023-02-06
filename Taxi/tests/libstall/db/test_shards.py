import pytest

from libstall.pg import shard


@pytest.mark.parametrize('test_shardno', [0, 1])
async def test_conn(tap, test_shardno, cfg):

    tap.plan(11)

    pool = shard.PgShards([cfg('pg.databases.tlibstall.shards.0')] * 2)

    async with pool(shard=test_shardno, mode='master') as conn:
        tap.ok(conn, 'Коннекшен к мастеру получен')
        tap.eq(conn.shardno, test_shardno, 'shardno')
        tap.eq(conn.mode, 'master', 'Режим мастер подтверждён')
        tap.eq(conn.name, 'tlibstall', 'name')

        row = await conn.fetchrow('SELECT 1 AS "col"')
        tap.eq(dict(row), {'col': 1}, 'fetchrow')

    async with pool(shard=test_shardno, mode='slow') as conn:
        tap.ok(conn, 'Коннекшен к слейву получен')
        tap.eq(conn.shardno, test_shardno, 'shardno')
        tap.ok(conn.mode in ('slave', 'slow'), 'Режим слейв подтверждён')
        tap.eq(conn.name, 'tlibstall', 'name')

        row = await conn.fetchrow('SELECT 1 AS "col"')
        tap.eq(dict(row), {'col': 1}, 'fetchrow')

    tap.ok(pool, 'Инстанцирован')


    await pool.close()
    tap()
