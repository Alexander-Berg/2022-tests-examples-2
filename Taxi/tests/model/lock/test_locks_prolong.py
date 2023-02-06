import asyncio
import datetime
import pytz

from stall.model.lock import Lock


async def test_lock(tap, uuid):
    """Блокировка"""

    with tap.plan(11):
        lock = Lock({'name': f'test-cron-{uuid()}'})
        tap.ok(lock, 'Лок')
        tap.ok(lock.name, 'Имя')
        tap.eq(lock.status, 'processing', 'Статус в работе')

        tap.ok(not await lock.prolong(), 'не пролонгируется пока не взята')

        tap.eq(await lock.lock(), True, 'Блокировка установлена')
        tap.ok(lock.locked, 'Время блокировки')
        tap.eq(lock.unlocked, None, 'Время разблокировки снято')
        tap.eq(lock.status, 'processing', 'Статус в работе')
        tap.ok(lock.host,   'Хост')
        tap.ok(lock.pid,    'PID')


        locked = int(lock.locked.timestamp())
        while locked == int(lock.locked.timestamp()):
            await lock.prolong()

        tap.ne(int(lock.locked.timestamp()), locked, 'изменилось время')


async def test_lock_error(tap, uuid):
    with tap.plan(5, 'Любая ошибка'):

        lock = Lock({'name': f'test-cron-{uuid()}', 'rm': False})
        tap.ok(await lock.lock(), 'Создали первый лок')

        second_lock = Lock({'name': f'test-cron-{uuid()}'})
        second_lock.lock_id = lock.lock_id
        tap.ok(second_lock, 'Лок')
        await asyncio.sleep(1)
        previous_locked = second_lock.locked

        tap.ok(
            not await second_lock.prolong(),
            'не пролонгируется без ошибки'
        )
        tap.eq(second_lock.locked, previous_locked, 'Время не поменялось')
        tap.ok(not second_lock.rehashed('locked'), 'Не рехешнуто')


async def test_lock_error_rehashed(tap, uuid):
    with tap.plan(5, 'Рехэш после неудачи'):

        lock = Lock({'name': f'test-cron-{uuid()}', 'rm': False})
        tap.ok(await lock.lock(), 'Создали первый лок')

        second_lock = Lock({'name': f'test-cron-{uuid()}'})
        tap.ok(second_lock, 'Лок')
        second_lock.lock_id = lock.lock_id
        new_locked = datetime.datetime(2007, 10, 10, tzinfo=pytz.UTC)
        second_lock.locked = new_locked
        await asyncio.sleep(1)
        previous_locked = second_lock.locked

        tap.ok(
            not await second_lock.prolong(),
            'не пролонгируется без ошибки'
        )
        tap.eq(second_lock.locked, previous_locked, 'Время не поменялось')
        tap.ok(second_lock.rehashed('locked'), 'Рехэш остался')
