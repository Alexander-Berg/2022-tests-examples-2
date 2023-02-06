#pylint: disable=protected-access

import asyncio
import socket
import time

import pytest
from asyncpg.exceptions import (
    QueryCanceledError, ConnectionDoesNotExistError,
    InterfaceError,
)

from libstall.pg import shard
from libstall.pg.exception import PgErNoMaster


async def test_conn(tap, cfg):
    with tap.plan(16):
        pool = shard.PgShard(cfg('pg.databases.tlibstall.shards.0'))
        tap.ok(pool, 'Инстанцирован')

        async with pool(mode='master') as conn:
            tap.ok(conn, 'Коннекшен к мастеру получен')
            tap.eq(conn.shardno, 0, 'shardno дефолт')
            tap.eq(conn.mode, 'master', 'Режим мастер подтверждён')
            tap.eq(conn.name, 'tlibstall', 'name')

            row = await conn.fetchrow('SELECT 1 AS "col"')
            tap.eq(dict(row), {'col': 1}, 'fetchrow')

        async with pool(mode='slow') as conn:
            tap.ok(conn, 'Коннекшен к слейву получен')
            tap.eq(conn.shardno, 0, 'shardno дефолт')
            tap.ok(conn.mode in ('slave', 'slow'), 'Режим слейв подтверждён')
            tap.eq(conn.name, 'tlibstall', 'name')

            row = await conn.fetchrow('SELECT 1 AS "col"')
            tap.eq(dict(row), {'col': 1}, 'fetchrow')

        await pool.close()

        async with pool(mode='master') as conn:
            tap.ok(conn, 'Коннекшен к мастеру получен после закрытия')
            tap.eq(conn.shardno, 0, 'shardno дефолт')
            tap.eq(conn.mode, 'master', 'Режим мастер подтверждён')
            tap.eq(conn.name, 'tlibstall', 'name')

            row = await conn.fetchrow('SELECT 1 AS "col"')
            tap.eq(dict(row), {'col': 1}, 'fetchrow')

        await pool.close()


async def test_one_pg_down(tap, cfg):
    with tap.plan(7):
        dsnstr = cfg('pg.databases.tlibstall.shards.0')
        new_parts = []
        for part in dsnstr.split(' '):
            if part.startswith('host='):
                part = f'{part},pg-down:15431'
            new_parts.append(part)

        pool = shard.PgShard(' '.join(new_parts))

        tap.eq_ok(len(pool.stat), 3, '3 nodes in cluster')

        async with pool(mode='master') as conn:
            cur_modes = {i['mode'] for i in pool.stat.values()}
            tap.ok('master' in cur_modes, 'master in cluster')
            tap.ok(
                'slave' in cur_modes or 'slow' in cur_modes,
                'slave/slow in cluster'
            )
            tap.ok('not_connected' in cur_modes, 'not_connected in cluster')

            tap.ok(pool.is_connected, 'Connected to master')
            tap.ok(pool.check_last_time > 0, 'Recheck next time')

            row = await conn.fetchrow('SELECT 1 AS "col"')
            tap.eq(dict(row), {'col': 1}, 'fetchrow')

        await pool.close()


async def test_all_pg_down(tap):
    with tap:
        pool = shard.PgShard(
            'host=pg-down:15433,pg-down:15432,pg-down:15431 '
            'dbname=tlibstall '
            'user=test '
            'password=test',
            attempt_limit=3,
            attempt_sleep_unit=0,
        )

        tap.eq_ok(len(pool.stat), 3, '3 nodes in cluster')

        with tap.raises(shard.PgErNoMaster, 'Cluster is down'):
            async with pool(mode='master'):
                pass

        tap.eq_ok(
            {i['mode'] for i in pool.stat.values()},
            {'not_connected'},
            'All dead',
        )
        tap.ok(pool.is_connected is False, 'Connected flag')
        tap.eq_ok(pool.check_last_time, 0, 'Recheck next time')

        await pool.close()


@pytest.mark.parametrize(
    'variant',
    [
        (
            {
                0: {'mode': 'not_connected'},
                1: {'mode': 'not_connected'},
            },
            False,
        ),
        (
            {
                0: {'mode': 'not_connected'},
                1: {'mode': 'slow'},
            },
            False,
        ),
        (
            {
                0: {'mode': 'not_connected'},
                1: {'mode': 'slave'},
            },
            False,
        ),
        (
            {
                0: {'mode': 'slow'},
                1: {'mode': 'slave'},
            },
            False,
        ),
        (
            {
                0: {'mode': 'master'},
                1: {'mode': 'not_connected'},
            },
            True,
        ),
        (
            {
                0: {'mode': 'master'},
                1: {'mode': 'slow'},
            },
            True,
        ),
        (
            {
                0: {'mode': 'master'},
                1: {'mode': 'slave'},
            },
            True,
        ),
    ]
)
async def test_is_connected(tap, cfg, variant):
    stat, is_connected = variant

    with tap.plan(1, 'если мастер жив, то считаем шард жив'):
        pgshard = shard.PgShard(
            cfg('pg.databases.tlibstall.shards.0'),
            pool_min_size=2,
            pool_max_size=2,
        )

        pgshard.stat = stat

        tap.is_ok(pgshard.is_connected, is_connected, 'состояние подключения')


@pytest.mark.parametrize('mode', ('master', 'slave', 'slow'))
async def test_run_check(tap, cfg, mode):
    with tap.plan(5, 'запуск чека после первого запроса к шарду'):
        pgshard = shard.PgShard(
            cfg('pg.databases.tlibstall.shards.0'),
            pool_min_size=2,
            pool_max_size=2,
        )

        # выставляем настройки чекера

        pgshard.check_interval = 5
        pgshard.check_sleep = 5

        tap.ok(pgshard.check_is_running is False, 'чекер не крутится')
        tap.eq(
            pgshard.check_last_time, 0, 'время последнего чека не выставлено',
        )

        async with pgshard(mode=mode) as conn:
            await conn.fetchrow('SELECT 1')

        tap.ok(
            pgshard.check_is_running, 'чекер запустился после первого запроса',
        )
        tap.ok(pgshard.check_task, 'чек таска пошла крутить проверки')
        tap.ok(pgshard.check_last_time > 0, 'выставили время последнего чека')

        await pgshard.close()


async def test_check_revive(tap, cfg):
    with tap.plan(6, 'Воскрешение чека'):
        pgshard = shard.PgShard(
            cfg('pg.databases.tlibstall.shards.0'),
            pool_min_size=2,
            pool_max_size=2,
        )

        # выставляем настройки чекера

        pgshard.check_interval = 5
        pgshard.check_sleep = 5

        tap.ok(pgshard.check_is_running is False, 'чекер не крутится')
        tap.eq(
            pgshard.check_last_time, 0, 'время последнего чека не выставлено',
        )
        async with pgshard(mode='master') as conn:
            await conn.fetchrow('SELECT 1')

        tap.ok(pgshard.check_task, 'чек таска пошла крутить проверки')
        pgshard.check_task.cancel()
        with tap.raises(asyncio.CancelledError):
            await pgshard.check_task

        async with pgshard(mode='master') as conn:
            await conn.fetchrow('SELECT 1')

        tap.ok(pgshard.check_task, 'Таска на месте')
        tap.ne_ok(pgshard.check_task.done(), True, 'Таска работает')

        await pgshard.close()


async def test_check_last_time(tap, cfg):
    with tap.plan(5, 'делаем чек раз в эн секунд'):
        pgshard = shard.PgShard(
            cfg('pg.databases.tlibstall.shards.0'),
            pool_min_size=2,
            pool_max_size=2,
        )

        pgshard.check_interval = 5
        pgshard.check_sleep = 0

        tap.ok(pgshard.check_last_time == 0, 'не было чеков')

        async with pgshard(mode='master') as conn:
            await conn.fetchrow('SELECT 1')

        tap.ok(pgshard.is_connected is True, 'пациент здоров')
        tap.ok(pgshard.check_last_time > 0, 'сделали чек')

        check_last_time = pgshard.check_last_time

        await pgshard._check()

        tap.ok(
            pgshard.check_last_time == check_last_time,
            'время последней проверки не сдвинулось',
        )

        pgshard.check_last_time -= 5.5

        await pgshard._check()

        tap.ok(
            pgshard.check_last_time > check_last_time,
            'время последней проверки сдвинулось',
        )

        await pgshard.close()


async def test_query_last_time(tap, cfg):
    with tap:
        pgshard = shard.PgShard(
            cfg('pg.databases.tlibstall.shards.0'),
            pool_min_size=2,
            pool_max_size=2,
        )

        pgshard.check_interval = 5
        pgshard.check_sleep = 0

        tap.ok(pgshard.query_last_time == 0, 'не было запросов')
        tap.ok(pgshard.check_last_time == 0, 'не было чеков')

        async with pgshard(mode='master') as conn:
            await conn.fetchrow('SELECT 1')

        tap.ok(pgshard.is_connected is True, 'пациент здоров')
        tap.ok(pgshard.query_last_time > 0, 'сделали запрос')
        tap.ok(pgshard.check_last_time > 0, 'сделали чек')

        pgshard.query_last_time -= 5.5

        pgshard.check_last_time -= 5.5
        check_last_time = pgshard.check_last_time

        await pgshard._check()

        tap.ok(
            pgshard.check_last_time == check_last_time,
            'время последней проверки не сдвинулось',
        )

        pgshard.query_last_time += 5.5

        await pgshard._check()

        tap.ok(
            pgshard.check_last_time > check_last_time,
            'время последней проверки сдвинулось',
        )

        await pgshard.close()


async def test_check_pool(tap, cfg):
    with tap.plan(9, 'переподключение пула'):
        pgshard = shard.PgShard(
            cfg('pg.databases.tlibstall.shards.0'),
            pool_min_size=2,
            pool_max_size=2,
        )

        pgshard.check_interval = 5
        pgshard.check_sleep = 0

        tap.eq(len(pgshard.stat), 2, 'два хоста')

        tap.ok(
            pgshard.stat[0]['mode'] == 'not_connected',
            'начальное состояние',
        )

        await pgshard._check_pool(0)

        mode = pgshard.stat[0]['mode']
        pool = pgshard.stat[0]['pool']

        tap.ok(mode in {'master', 'slave', 'slow'}, 'первый хост включили')
        tap.ok(pool, 'есть пул')

        await pgshard._close_pool(0, force=True)

        mode1 = pgshard.stat[0]['mode']
        pool1 = pgshard.stat[0]['pool']

        tap.ok(mode1 == 'not_connected', 'первый хост вырубили')
        tap.ok(pool1 is None, 'нет пула')

        await pgshard._check_pool(0)

        mode2 = pgshard.stat[0]['mode']
        pool2 = pgshard.stat[0]['pool']

        tap.ok(mode2 in {'master', 'slave', 'slow'}, 'первый хост включен')
        tap.ok(id(pool2) != id(pool1), 'создали новый пул')

        pgshard.stat[1]['mode'] = 'not_connected'

        async with pgshard(mode='slow') as conn:
            tap.ok(await conn.fetchrow('SELECT 1'), 'запросы проходят')
        await pool.close()


async def test_close(tap, cfg):
    with tap.plan(6, 'корректное закрытие шарда'):
        pool = shard.PgShard(
            cfg('pg.databases.tlibstall.shards.0'),
            pool_min_size=2,
            pool_max_size=2,
        )

        async with pool(mode='master') as conn:
            row = await conn.fetchrow('SELECT 1 AS "col"')

            tap.eq(dict(row), {'col': 1}, 'fetchrow')

        async with pool(mode='slow') as conn:
            row = await conn.fetchrow('SELECT 1 AS "col"')

            tap.eq(dict(row), {'col': 1}, 'fetchrow')

        tap.ok(await pool.close() is None, 'закрываемся')
        tap.ok(pool.is_connected is False, 'пул без мастера')
        tap.eq(
            {i['mode'] for i in pool.stat.values()},
            {'not_connected'},
            'все статусы отметили как неактивыне',
        )
        tap.eq(
            {i['pool'] for i in pool.stat.values()},
            {None},
            'все пулы закрыли',
        )


async def test_master_down(tap, cfg):
    with tap.plan(7, 'отрыв мастера пересоздает пул на следующий запрос'):
        pgshard = shard.PgShard(
            cfg('pg.databases.tlibstall.shards.0'),
            pool_min_size=2,
            pool_max_size=2,
        )

        # выставляем настройки чекера

        pgshard.check_interval = 5
        pgshard.check_sleep = 0

        async with pgshard(mode='master') as conn:
            await conn.fetchrow('SELECT 1')
            tap.ok(conn.mode == 'master', 'читаем из мастера')

        async with pgshard(mode='slow') as conn:
            await conn.fetchrow('SELECT 1')
            tap.ok(conn.mode in ('slow', 'slave'), 'читаем из реплики')

        # убираем из пула мастера

        master = await pgshard._seek_pool('master')
        master['mode'] = 'not_connected'

        with tap.raises(PgErNoMaster, 'мастер оторвался'):
            async with pgshard(mode='master') as _:
                pass

        tap.eq(pgshard.is_connected, False, 'сработало закрытие')
        tap.eq(pgshard.check_last_time, 0, 'форсим чек')

        await pgshard._check()

        async with pgshard(mode='master') as conn:
            await conn.fetchrow('SELECT 1')
            tap.ok(conn.mode == 'master', 'мастер вернулся в пул')

        async with pgshard(mode='slow') as conn:
            await conn.fetchrow('SELECT 1')
            tap.ok(conn.mode in ('slow', 'slave'), 'реплика жива')

        await pgshard.close()


async def test_master_acquire_timeout(tap, cfg):
    with tap.plan(5, 'таймаут при получении коннекта для мастера'):
        pgshard = shard.PgShard(
            cfg('pg.databases.tlibstall.shards.0'),
            pool_min_size=1,
            pool_max_size=1,
            pool_acquire_timeout=0.1,
        )

        pgshard.check_interval = 5
        pgshard.check_sleep = 0

        pool, conn = await pgshard.acquire(mode='master')

        tap.ok(conn, 'взяли коннект и не вернули')
        tap.ok(
            'not_connected' not in {i['mode'] for i in pgshard.stat.values()},
            'все подключено',
        )

        with tap.raises(asyncio.TimeoutError, 'не хватает коннектов'):
            async with pgshard(mode='master') as _:
                pass

        tap.eq(pgshard.check_last_time, 0, 'форсим чек')

        await pool.release(conn)

        async with pgshard(mode='master') as conn:
            await conn.fetchrow('SELECT 1')
            tap.ok(conn.mode == 'master', 'мастер переподключен')

        await pgshard.close()


async def test_replica_down(tap, cfg):
    with tap.plan(4, 'отрыв реплики переключает все запросы на мастер'):
        pgshard = shard.PgShard(
            cfg('pg.databases.tlibstall.shards.0'),
            pool_min_size=2,
            pool_max_size=3,
        )

        # выставляем настройки чекера

        pgshard.check_interval = 5
        pgshard.check_sleep = 0

        async with pgshard(mode='master') as conn:
            await conn.fetchrow('SELECT 1')
            tap.ok(conn.mode == 'master', 'читаем из мастера')

        async with pgshard(mode='slow') as conn:
            await conn.fetchrow('SELECT 1')

            tap.ok(conn.mode in ('slow', 'slave'), 'читаем из реплики')

        # убраем из пула слейв

        slow = await pgshard._seek_pool('slow')
        slow['mode'] = 'not_connected'

        async with pgshard(mode='slow') as conn:
            await conn.fetchrow('SELECT 1 AS result')
            tap.eq(conn.mode, 'master', 'запросы переключились на мастер')

        # ждем следующего чека

        pgshard.check_interval = 0.1
        check_last_time = pgshard.check_last_time

        handbrake = 0

        while check_last_time == pgshard.check_last_time:
            await asyncio.sleep(0.1)

            if handbrake >= 1:
                break

            handbrake += 0.1

        async with pgshard(mode='slow') as conn:
            await conn.fetchrow('SELECT 1')
            tap.ok(conn.mode in ('slow', 'slave'), 'слейв вернулся в пул')

        await pgshard.close()


async def test_replica_acquire_timeout(tap, cfg):
    with tap.plan(5, 'таймаут при получении коннекта для реплики'):
        pgshard = shard.PgShard(
            cfg('pg.databases.tlibstall.shards.0'),
            pool_min_size=1,
            pool_max_size=1,
            pool_acquire_timeout=0.2,
        )

        pgshard.check_interval = 5
        pgshard.check_sleep = 0

        pool, conn = await pgshard.acquire(mode='slow')

        tap.ok(
            'not_connected' not in {i['mode'] for i in pgshard.stat.values()},
            'все подключено',
        )

        with tap.raises(asyncio.TimeoutError, 'не хватает коннектов'):
            async with pgshard(mode='slow') as _:
                pass

        tap.eq(pgshard.check_last_time, 0, 'форсим чек')

        async with pgshard(mode='slow') as second_conn:
            await second_conn.fetchrow('SELECT 1')
            tap.ok(
                second_conn.mode == 'master',
                'все запросы переключились на мастер',
            )

        await pool.release(conn)

        pgshard.check_interval = 0.1
        check_last_time = pgshard.check_last_time

        handbrake = 0

        while check_last_time == pgshard.check_last_time:
            await asyncio.sleep(0.1)

            if handbrake >= 1:
                break

            handbrake += 0.1

        async with pgshard(mode='slow') as conn:
            await conn.fetchrow('SELECT 1')
            tap.ok(conn.mode in ('slow', 'slave'), 'реплика вернулась в строй')

        await pgshard.close()


@pytest.mark.parametrize('mode', ['master', 'slave', 'slow'])
async def test_statement_timeout(tap, cfg, mode):
    with tap.plan(3, 'Таймаут запроса'):
        timeout = 0.5

        pgshard = shard.PgShard(
            cfg('pg.databases.tlibstall.shards.0'),
            pool_min_size=2,
            pool_max_size=3,
        )

        pgshard.pool_query_timeout = timeout

        pool, conn = await pgshard.acquire(mode=mode)
        tap.ok(
            'not_connected' not in {i['mode'] for i in pgshard.stat.values()},
            'все подключено',
        )

        try:
            await conn.fetchrow('SELECT pg_sleep($1::INTEGER)', timeout + 1)
        except asyncio.TimeoutError:
            tap.passed('Таймаут сработал')
        else:
            tap.failed('Таймаут сработал')

        await pool.release(conn)

        pool, conn = await pgshard.acquire(mode=mode)

        tap.ok(await conn.fetchrow('SELECT TRUE'), 'Пул функционирует')

        await pool.release(conn)

        await pgshard.close()


@pytest.mark.parametrize('mode', ['master', 'slave', 'slow'])
async def test_pg_cancel(tap, cfg, mode, uuid):
    with tap.plan(5, 'Корректно дропаем запрос'):
        timeout = 3

        pgshard = shard.PgShard(
            cfg('pg.databases.tlibstall.shards.0'),
            pool_min_size=2,
            pool_max_size=3,
        )

        pgshard.pool_query_timeout = timeout

        pool, conn1 = await pgshard.acquire(mode=mode)
        pool, conn2 = await pgshard.acquire(mode=mode)

        tap.ok(
            'not_connected' not in {i['mode'] for i in pgshard.stat.values()},
            'все подключено',
        )
        tap.eq(conn1.shardno, conn2.shardno, 'На том же шарде')

        marker = uuid()

        background = asyncio.create_task(
            # UGLY: да, да иньекции и все такое. это тест, так удобней
            conn1.fetchrow(
                f"SELECT"
                f" pg_sleep({timeout}::INTEGER),"
                f" '{marker}'::TEXT"
            )
        )
        tap.ok(background, 'Запрос в фоне запущен')

        # Ожидаем запрос слипа и убиваем его
        for _ in range(timeout):
            await asyncio.sleep(1)

            ps = await conn2.fetchrow(
                f"SELECT pg_cancel_backend(pid)"
                f" FROM pg_stat_activity"
                f" WHERE query ILIKE '%{marker}%'",
            )
            if ps:
                break

        try:
            await background
        except QueryCanceledError:
            tap.passed('Запрос убит')
        else:
            tap.failed('Запрос убит')

        await pool.release(conn1)
        await pool.release(conn2)

        pool, conn = await pgshard.acquire(mode=mode)

        tap.ok(await conn.fetchrow('SELECT TRUE'), 'Пул функционирует')

        await pool.release(conn)

        await pgshard.close()


@pytest.mark.parametrize('mode', ['master', 'slave', 'slow'])
async def test_disconnect(tap, cfg, mode):
    with tap.plan(7, 'Разрыв соединения во время запроса'):
        timeout = 1.5

        pgshard = shard.PgShard(
            cfg('pg.databases.tlibstall.shards.0'),
            pool_min_size=1,
            pool_max_size=1,
        )

        pgshard.pool_query_timeout = timeout

        pool, conn = await pgshard.acquire(mode=mode)
        tap.ok(
            'not_connected' not in {i['mode'] for i in pgshard.stat.values()},
            'все подключено',
        )

        start = time.time()

        background = asyncio.create_task(
            # UGLY: да, да иньекции и все такое. это тест, так удобней
            conn.fetchrow(f'SELECT pg_sleep({timeout}::INTEGER)')
        )
        tap.ok(background, 'Запрос в фоне запущен')

        await asyncio.sleep(1)

        # UGLY: здесь залезли во внутренности драйвера.
        # Возможно можно получить сокет более правильно.
        socket.close(conn._transport._sock.fileno())

        try:
            await background
        except asyncio.TimeoutError:
            tap.passed('Сокет закрыт')
        else:
            tap.failed('Сокет закрыт')

        tap.ok(time.time() - start >= timeout, 'Вышел по таймауту')

        try:
            await pool.release(conn, timeout=0.5)
        except Exception as exc:
            tap.ok(exc, 'Не смогли отдать коннект')

        pool, conn = await pgshard.acquire(mode=mode)
        tap.ok(
            'not_connected' not in {i['mode'] for i in pgshard.stat.values()},
            'все подключено',
        )

        tap.ok(await conn.fetchrow('SELECT TRUE'), 'Запрос выполнен')

        await pool.release(conn)

        await pgshard.close()


@pytest.mark.parametrize('mode', ['master'])
async def test_disconnect_before(tap, cfg, mode):
    with tap.plan(6, 'Разрыв соединения во время запроса'):
        timeout = 3

        pgshard = shard.PgShard(
            cfg('pg.databases.tlibstall.shards.0'),
            pool_min_size=1,
            pool_max_size=1,
        )

        pgshard.pool_query_timeout = timeout

        pool, conn = await pgshard.acquire(mode=mode)
        tap.ok(
            'not_connected' not in {i['mode'] for i in pgshard.stat.values()},
            'все подключено',
        )

        # UGLY: здесь залезли во внутренности драйвера.
        # Возможно можно получить сокет более правильно.
        socket.close(conn._transport._sock.fileno())

        start = time.time()
        try:
            # UGLY: да, да иньекции и все такое. это тест, так удобней
            tap.ok(await conn.fetchrow('SELECT TRUE'), 'Запрос выполнен')
        except ConnectionDoesNotExistError:
            tap.passed('Запрос отвалился')
        else:
            tap.failed('Запрос отвалился')

        tap.ok(time.time() - start < timeout, 'Вышел сам, а не по таймауту')

        await asyncio.sleep(timeout + 1)

        try:
            await conn.fetchrow('SELECT TRUE')
        except InterfaceError:
            tap.passed('Коннект сломан')
        else:
            tap.failed('Коннект сломан')

        await pool.release(conn)

        pool, conn = await pgshard.acquire(mode=mode)
        tap.ok(
            'not_connected' not in {i['mode'] for i in pgshard.stat.values()},
            'все подключено',
        )

        tap.ok(await conn.fetchrow('SELECT TRUE'), 'Запрос выполнен')

        await pool.release(conn)

        await pgshard.close()
