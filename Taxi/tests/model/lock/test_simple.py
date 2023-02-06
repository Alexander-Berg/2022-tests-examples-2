from stall.model.lock import lock, unlock


async def test_simple(tap, uuid):
    """Функциональный интерфейс к библиотеке"""

    with tap.plan(4):
        name = f'test-cron-{uuid()}'

        tap.eq(await lock(name=name), True, 'Блокировка установлена')
        tap.eq(await unlock(name=name, status='failed'), True, (
            'Блокировка снята'))

        tap.eq(await lock(name=name), True, 'Блокировка установлена')
        tap.eq(await unlock(name=name), True, 'Блокировка снята')
