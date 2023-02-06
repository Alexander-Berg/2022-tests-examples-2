import asyncio
from unittest.mock import patch
from multiprocessing import Process
import pytest

from libstall.util import now
from stall.model.lock import ProlongLock


async def test_lock(tap, uuid):
    """Блокировка"""
    with tap.plan(12):

        lock_id = uuid()

        lock = ProlongLock(lock_id, rm=True, timeout=1.5)
        tap.ok(not lock.is_active(), 'Лок не активный')
        async with lock as ll:
            tap.ok(lock.is_active(), 'Блокировка активна')
            tap.eq(ll.prolongs, 0, 'количество пролонгов пока нулевое')
            tap.passed('блокировка взята')
            tap.ok(ll.task, 'задача создана')

            started = now()

            with tap.raises(ProlongLock.TimeoutError, 'повтор - ошибка'):
                async with ProlongLock(lock_id, lock_timeout=1):
                    tap.failed('Повторно не взята')

            prolong_lock = ProlongLock(
                lock_id,
                lock_timeout=2,
                noraise=True
            )
            async with prolong_lock as pl:
                tap.eq(pl, None, 'с флагом noraise не бросает исключение')
                tap.ok(not prolong_lock.is_active(), 'Неактивная блокировка')
            tap.ok(ll.prolongs, 'количество пролонгов не нулевое')
            tap.ok(lock.is_active(), 'Все еще лок активный')

            ttl = now().timestamp() - started.timestamp()
            tap.ok(ttl >= 2, 'время ожидание не нулевое')
        tap.ok(not lock.is_active(), 'Лок не активный')


async def test_lock_err(tap, uuid):
    """Блокировка"""
    with tap.plan(3):

        lock_id = uuid()

        started = now()
        with tap.raises(RuntimeError, 'тест исключений'):
            async with ProlongLock(lock_id, lock_timeout=12):
                raise RuntimeError('привет')

        async with ProlongLock(lock_id, rm=True, timeout=2):
            tap.passed('Зашли повторно')

        ttl = now().timestamp() - started.timestamp()
        tap.ok(ttl < 1, 'менее одной секунды на всё')


@pytest.mark.filterwarnings('ignore:coroutine')
async def test_prolong_process_kill(tap, uuid, cfg):
    with tap.plan(2, 'Завершение процесса'):
        cfg.set('lock.prolong_retries', 1)

        async def target():
            async with ProlongLock(
                    name=f'test-{uuid()}',
                    timeout=2,
                    rm=True,
                    exit_on_failure=True
            ):
                with patch('stall.model.lock.Lock.__base__.save') as mock:
                    mock.side_effect = RuntimeError
                    await asyncio.sleep(3)

        process = Process(target=asyncio.run, args=(target(),))
        process.start()
        process.join(timeout=4)
        tap.ok(not process.is_alive(), 'Процесс не живой')
        tap.eq(process.exitcode, 255, 'Правильный код выхода')
        process.close()


async def test_prolong_few_failures(tap, uuid, cfg):
    with tap.plan(5, 'Несколько неудач пролонгации'):
        cfg.set('lock.prolong_retries', 5)
        async with ProlongLock(
                name=f'test-{uuid()}', timeout=2, rm=True) as lock:
            tap.ok(lock, 'Взяли блокировку')
            tap.ok(lock.is_active(), 'Активна до')
            patcher = patch('stall.model.lock.Lock.__base__.save')
            mock = patcher.start()
            mock.side_effect = RuntimeError
            await asyncio.sleep(1)
            tap.ok(lock.is_active(), 'Активна после неудач')
            patcher.stop()
            await asyncio.sleep(1)
            tap.ok(lock.is_active(), 'Активна после захвата')
            tap.ok(not lock.task.done(), 'Корутина жива после неудачи')


async def test_prolong_retries(tap, uuid, cfg):
    with tap.plan(5, 'Число пролонгаций верное'):
        cfg.set('lock.prolong_retries', 4)
        async with ProlongLock(
                name=f'test-{uuid()}', timeout=2, rm=True) as lock:
            tap.ok(lock, 'Взяли блокировку')
            patcher = patch('stall.model.lock.Lock.__base__.save')
            mock = patcher.start()
            mock.side_effect = RuntimeError
            tap.ok(lock.is_active(), 'Активна блокировка')
            await asyncio.sleep(3)
            tap.ok(not lock.is_active(), 'Блокировка неактивна')
            tap.ok(lock.task.done(), 'Корутина остановлена')
            tap.eq(mock.call_count, 4, 'Правильное число пролонгаций')
            patcher.stop()
