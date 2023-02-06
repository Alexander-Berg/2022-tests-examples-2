import pytest

from ymlcfg.jpath import JPath

@pytest.mark.parametrize('cache', [True, False])
@pytest.mark.parametrize('safe', [True, False])
def test_jpath(tap, safe, cache):
    with tap.plan(22):
        o = {
            'a': 'b',
            'c': [1, 2, 3],
            33: 'abc',
            (-1): 'error'
        }

        path = JPath(o, safe=safe, cache=cache)

        tap.ok(path, 'инстанцирован')
        tap.eq(path(), o, 'полный объект')
        tap.eq(path(''), o, 'на пустой строке тоже полный объект')
        tap.eq(path(None), o, 'на None тоже полный объект')

        tap.eq(path('a'), 'b', 'взятие ключа')
        tap.eq(path('c'), [1, 2, 3], 'взятие ключа')
        tap.eq(path('33'), 'abc', 'взятие ключа с чисельным значением')
        tap.eq(path('-1'), 'error', 'взятие ключа с чисельным значением')


        tap.eq(path('c.0'), 1, 'взятие элемента массива')
        tap.eq(path('c.2'), 3, 'взятие элемента массива')
        tap.eq(path('c.-1'), 3, 'взятие элемента массива')
        tap.eq(path('c.-2'), 2, 'взятие элемента массива')
        tap.eq(path('c.-3'), 1, 'взятие элемента массива')


        with tap.raises(path.NotFound, 'ключ не существует'):
            path('abc')
        with tap.raises(path.NotFound, 'чисельный ключ не существует'):
            path('333')
        with tap.raises(path.NotFound, 'чисельный ключ не существует'):
            path('-333')
        with tap.raises(path.NotFound, 'за границей массива'):
            path('c.4')
        with tap.raises(path.NotFound, 'за границей массива отр'):
            path('c.-4')

        with tap.raises(path.NotFound, 'непонятно что'):
            path('aanhjj')

        tap.eq(path('c.4', 27), 27, 'Значение по умолчанию')

        if cache:
            tap.in_ok('c.-3', path.cached, 'кеширование есть')
        else:
            tap.ok('c.-3' not in path.cached, 'кеширования нет')

        if safe:
            tap.ne(id(path('c')), id(o['c']), 'копирование работает')
        else:
            tap.eq(id(path('c')), id(o['c']), 'копирование не работает')
