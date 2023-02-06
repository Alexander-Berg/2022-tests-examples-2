from random import randrange

from stall.model.event import Event


async def test_cache_seek(tap):
    # pylint: disable=protected-access

    key = lambda x: x

    with tap.plan(22, 'Двоичный поиск по массиву'):
        tap.eq(Event._cache_seek([], 1, key), None, 'Пустой массив')
        tap.eq(Event._cache_seek([0, -1], 1, key), None, 'Не найдено')

        tap.eq(Event._cache_seek([2], 1, key), 2, 'найдено массив из 1')
        tap.eq(Event._cache_seek([2], 10, key), None, 'не найдено массив из 1')

        for i in range(1, 7):
            tap.eq(Event._cache_seek([1,2,3,4,5,6,7], i, key),
                   i + 1,
                   'обычный вариант')

        for i in range(1, 8):
            tap.eq(Event._cache_seek([1,2,3,4,5,6,7,8], i, key),
                   i + 1,
                   'обычный вариант')

        tap.eq(Event._cache_seek(list(range(500)), 5, key),
               6,
               'обычный вариант')

        for _ in (1, 2, 3):
            seek = randrange(1, 999)
            tap.eq(Event._cache_seek(list(range(1024)), seek, key),
                   seek + 1,
                   'обычный вариант')

        tap.eq(Event._cache_seek([3, 4, 5], 3, key), 4, 'обычный вариант')
