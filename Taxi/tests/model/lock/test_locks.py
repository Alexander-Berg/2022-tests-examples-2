from stall.model.lock import Lock


async def test_lock(tap, uuid):
    """Блокировка"""

    with tap.plan(21):
        lock = Lock({'name': f'test-cron-{uuid()}'})
        tap.ok(lock, 'Лок')
        tap.ok(lock.name, 'Имя')
        tap.eq(lock.status, 'processing', 'Статус в работе')

        tap.eq(await lock.lock(), True, 'Блокировка установлена')
        tap.ok(lock.locked, 'Время блокировки')
        tap.eq(lock.unlocked, None, 'Время разблокировки снято')
        tap.eq(lock.status, 'processing', 'Статус в работе')
        tap.ok(lock.host,   'Хост')
        tap.ok(lock.pid,    'PID')

        tap.eq(await lock.lock(), False, 'Уже заблокировано')
        tap.ok(lock.locked, 'Время блокировки')
        tap.eq(lock.unlocked, None, 'Время разблокировки снято')
        tap.eq(lock.status, 'processing', 'Статус в работе')

        tap.eq(await lock.unlock(), True, 'Блокировка снята')
        tap.ok(lock.locked, 'Время блокировки')
        tap.ok(lock.unlocked, 'Время разблокировки')
        tap.eq(lock.status, 'complete', 'Статус завершено')

        tap.eq(await lock.unlock(), True, 'Блокировки нет')
        tap.ok(lock.locked, 'Время блокировки')
        tap.ok(lock.unlocked, 'Время разблокировки')
        tap.eq(lock.status, 'complete', 'Статус завершено')

async def test_complete_timeout(tap, uuid):
    """После коорректной разблокировки таймаут все равно блокирует"""

    with tap.plan(4):
        lock = Lock({'name': f'test-cron-{uuid()}'})

        tap.eq(await lock.lock(), True, 'Блокировка установлена')
        tap.eq(await lock.unlock(), True, 'Блокировка снята')

        tap.eq(await lock.lock(after_success_timeout=15),
               False,
               'Ждем таймаут')

        tap.eq(await lock.lock(after_success_timeout=0),
               True,
               'Без таймаута работает сразу')

async def test_failed_no_timeout(tap, uuid):
    """Если выполнение падает, то повторно запускать можно сразу"""

    with tap.plan(3):
        lock = Lock({'name': f'test-cron-{uuid()}'})

        tap.eq(await lock.lock(), True, 'Блокировка установлена')
        tap.eq(await lock.unlock(status='failed'), True, 'Блокировка снята')

        tap.eq(await lock.lock(), True, 'Запускать можно сразу')

async def test_lock_repeat(tap, uuid):
    """Блокировка"""
    with tap.plan(8):
        lock = Lock({'name': f'test-cron-{uuid()}'})
        tap.ok(lock, 'Лок')
        tap.ok(lock.name, 'Имя')
        tap.eq(lock.status, 'processing', 'Статус в работе')

        tap.eq(await lock.lock(), True, 'Блокировка установлена')
        tap.eq(await lock.unlock(), True, 'Блокировка снята')


        lock2 = Lock({'name': lock.name})
        tap.ok(lock2, 'Лок2 инстанцирован')
        tap.eq(lock2.name, lock.name, 'имя')

        tap.eq(await lock.lock(after_success_timeout=0),
               True,
               'Блокировка повторно не установлена')
