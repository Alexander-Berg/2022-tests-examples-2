import pytest

from ymlcfg.jpath import JPath

@pytest.mark.parametrize('cache', [True, False])
@pytest.mark.parametrize('safe', [True, False])
def test_jmodify_set(tap, safe, cache):
    with tap.plan(13):
        o = {
            'a': 'b',
            'c': [1, 2, 3],
            33: 'abc',
            'c3': 356,
            (-1): 'error'
        }

        path = JPath(o, safe=safe, cache=cache)

        tap.ok(path, 'инстанцирован')
        tap.eq(path(), o, 'полный объект')

        tap.eq(path.set('aaaaaaaaa', 'Hel'), 0, 'нет измененных объектов')

        tap.eq(path('a'), 'b', 'Начальное значение объекта')
        tap.eq(path.set('a', 11), 1, 'один объект изменен')
        tap.eq(path('a'), 11, 'Объект реально поменялся')

        tap.eq(path('c'), [1, 2, 3], 'Начальное значение родителя')
        tap.eq(path('c.1'), 2, 'Начальное значение объекта')
        tap.eq(path.set('c.1', 31), 1, 'еще один объект изменен')
        tap.eq(path('c'), [1, 31, 3], 'Объект реально поменялся')


        tap.eq(path.set('c*', 'c'), 2, 'заменили два раза')
        tap.eq(path('c'), 'c', 'одно значение')
        tap.eq(path('c3'), 'c', 'второе')


@pytest.mark.parametrize('cache', [True, False])
@pytest.mark.parametrize('safe', [True, False])
def test_jmodify_append(tap, safe, cache):
    with tap.plan(14):
        o = {
            'a': 'b',
            'c': [1, 2, 3],
            'c1': [2, 3, 4],
            33: 'abc',
            (-1): 'error'
        }

        path = JPath(o, safe=safe, cache=cache)

        tap.ok(path, 'инстанцирован')
        tap.eq(path(), o, 'полный объект')

        tap.eq(path.append('aaaaaaaaa', 'Hel'), 0, 'нет измененных объектов')

        tap.eq(path('a'), 'b', 'Начальное значение объекта')
        tap.eq(path.append('a', '11'), 1, 'один объект изменен')
        tap.eq(path('a'), 'b11', 'Новое значение объекта')

        tap.eq(path('c'), [1, 2, 3], 'Начальное значение объекта родителя')
        tap.eq(path('c.1'), 2, 'Начальное значение объекта')
        tap.eq(path.append('c.1', 11), 1, 'один объект изменен')
        tap.eq(path('c.1'), 2 + 11, 'Новое значение объекта')
        tap.eq(path('c'), [1, 2 + 11, 3], 'конечное значение объекта родителя')


        tap.eq(path('c*'), [[1, 2 + 11, 3], [2, 3, 4]], 'Начальное значение')
        tap.eq(path.append('c*', [11]), 2, 'Два элемента дополнено')
        tap.eq(path('c*'), [[1, 2 + 11, 3, 11], [2, 3, 4, 11]], 'Итого')


@pytest.mark.parametrize('cache', [True, False])
@pytest.mark.parametrize('safe', [True, False])
def test_jmodify_prepend(tap, safe, cache):
    with tap.plan(14):
        o = {
            'a': 'b',
            'c': [1, 2, 3],
            'c1': [2, 3, 4],
            33: 'abc',
            (-1): 'error'
        }

        path = JPath(o, safe=safe, cache=cache)

        tap.ok(path, 'инстанцирован')
        tap.eq(path(), o, 'полный объект')

        tap.eq(path.prepend('aaaaaaaaa', 'Hel'), 0, 'нет измененных объектов')

        tap.eq(path('a'), 'b', 'Начальное значение объекта')
        tap.eq(path.prepend('a', '11'), 1, 'один объект изменен')
        tap.eq(path('a'), '11b', 'Новое значение объекта')

        tap.eq(path('c'), [1, 2, 3], 'Начальное значение объекта родителя')
        tap.eq(path('c.1'), 2, 'Начальное значение объекта')
        tap.eq(path.prepend('c.1', 11), 1, 'один объект изменен')
        tap.eq(path('c.1'), 2 + 11, 'Новое значение объекта')
        tap.eq(path('c'), [1, 2 + 11, 3], 'конечное значение объекта родителя')


        tap.eq(path('c*'), [[1, 2 + 11, 3], [2, 3, 4]], 'Начальное значение')
        tap.eq(path.prepend('c*', [11]), 2, 'Два элемента дополнено')
        tap.eq(path('c*'), [[11, 1, 2 + 11, 3], [11, 2, 3, 4]], 'Итого')


@pytest.mark.parametrize('cache', [True, False])
@pytest.mark.parametrize('safe', [True, False])
def test_jmodify_lreplace(tap, safe, cache):
    with tap.plan(9):
        o = {
            'a': 'Hello, world',
            'c': [1, 2, 3],
            'c1': [2, 3, 4],
            33: 'abc',
            (-1): 'error'
        }

        path = JPath(o, safe=safe, cache=cache)

        tap.ok(path, 'инстанцирован')
        tap.eq(path(), o, 'полный объект')

        tap.eq(path.lreplace('aaaaaaaaa', 'Hel'), 0, 'нет измененных объектов')

        tap.eq(path('a'), 'Hello, world', 'Начальное значение объекта')
        tap.eq(path.lreplace('a', 'Hel'), 1, 'один объект изменен')
        tap.eq(path('a'), 'lo, world', 'Новое значение объекта')

        tap.eq(path('c'), [1, 2, 3], 'Начальное значение объекта')
        tap.eq(path.lreplace('c', [1], [22, 33]), 1, 'один объект изменен')
        tap.eq(path('c'), [22, 33, 2, 3], 'конечное значение объекта')


@pytest.mark.parametrize('cache', [True, False])
@pytest.mark.parametrize('safe', [True, False])
def test_jmodify_rreplace(tap, safe, cache):
    with tap.plan(10):
        o = {
            'a': 'Hello, world',
            'c': [1, 2, 3],
            'c1': [2, 3, 4],
            33: 'abc',
            (-1): 'error'
        }

        path = JPath(o, safe=safe, cache=cache)

        tap.ok(path, 'инстанцирован')
        tap.eq(path(), o, 'полный объект')

        tap.eq(path.rreplace('aaaaaaaaa', 'Hel'), 0, 'нет измененных объектов')

        tap.eq(path('a'), 'Hello, world', 'Начальное значение объекта')
        tap.eq(path.rreplace('a', 'rld'), 1, 'один объект изменен')
        tap.eq(path('a'), 'Hello, wo', 'Новое значение объекта')

        tap.eq(path('c'), [1, 2, 3], 'Начальное значение объекта')
        tap.eq(path.rreplace('c', [3], [22, 33]), 1, 'один объект изменен')
        tap.eq(path('c'), [1, 2, 22, 33], 'конечное значение объекта')

        with tap.subtest(None, 'пустые суффиксы') as taps:
            taps.eq(path.rreplace('*', ', wo', 'cde'), 1, 'одно изменение')
            taps.eq(path('a'), 'Hellocde', 'Новое значение')

@pytest.mark.parametrize('cache', [True, False])
@pytest.mark.parametrize('safe', [True, False])
def test_jmodify_lreplace_keys(tap, safe, cache):
    with tap.plan(12):
        o = {
            'aa': 'Hello, world',
            'c': [1, 2, 3],
            'c1': [2, 3, 4],
            33: 'abc',
            (-1): 'error'
        }

        path = JPath(o, safe=safe, cache=cache)

        tap.ok(path, 'инстанцирован')
        tap.eq(path(), o, 'полный объект')

        tap.eq(path.lreplace_keys('aaaaaaaaa', 'Hel'),
               0,
               'нет измененных объектов')

        tap.eq(path('aa'), 'Hello, world', 'Начальное значение объекта')
        with tap.raises(path.NotFound, 'нет ключа cdea'):
            path('cdea')

        tap.eq(path.lreplace_keys('aa', 'a', 'cde'), 1, 'один объект изменен')
        tap.eq(path('c1'), [2,3,4], 'c1 не поменялся')

        with tap.raises(path.NotFound, 'теперь нет ключа aa'):
            path('aa')
        tap.eq(path('cdea'), 'Hello, world', 'Новое значение объекта')


        with tap.subtest(2, 'тесты не зацикливается ли') as taps:
            taps.eq(path.lreplace_keys('cde*', 'cde', 'cde'), 1, 'одна замена')
            taps.eq(path('cdea'), 'Hello, world', 'Новое значение объекта')

        with tap.subtest(3, 'тотальное переименование') as taps:
            taps.eq(path.lreplace_keys('*', '', 'cde'),
                    5, 'все корневые элементы заменены')
            taps.eq(path('cdecdea'), 'Hello, world', 'Новое значение объекта')
            taps.eq(path('cde-1'), 'error', 'числовое стало символьным')

        with tap.subtest(3, 'переименование с непустым префиксом') as taps:
            taps.eq(path.lreplace_keys('*', 'cde-1', 'cde--1'),
                    1, 'Один элемент имел префикс')
            taps.eq(path('cdecdea'), 'Hello, world', 'Новое значение объекта')
            taps.eq(path('cde--1'), 'error', 'переименованный ключ')


@pytest.mark.parametrize('cache', [True, False])
@pytest.mark.parametrize('safe', [True, False])
def test_jmodify_rreplace_keys(tap, safe, cache):
    with tap.plan(12):
        o = {
            'aa': 'Hello, world',
            'c': [1, 2, 3],
            'c1': [2, 3, 4],
            33: 'abc',
            (-1): 'error'
        }

        path = JPath(o, safe=safe, cache=cache)

        tap.ok(path, 'инстанцирован')
        tap.eq(path(), o, 'полный объект')

        tap.eq(path.rreplace_keys('aaaaaaaaa', 'Hel'),
               0,
               'нет измененных объектов')

        tap.eq(path('aa'), 'Hello, world', 'Начальное значение объекта')
        with tap.raises(path.NotFound, 'нет ключа acde'):
            path('acde')

        tap.eq(path.rreplace_keys('aa', 'a', 'cde'), 1, 'один объект изменен')
        tap.eq(path('c1'), [2,3,4], 'c1 не поменялся')

        with tap.raises(path.NotFound, 'теперь нет ключа aa'):
            path('aa')
        tap.eq(path('acde'), 'Hello, world', 'Новое значение объекта')


        with tap.subtest(2, 'тесты не зацикливается ли') as taps:
            taps.eq(path.rreplace_keys('acde', 'cde', 'cde'), 1, 'одна замена')
            taps.eq(path('acde'), 'Hello, world', 'Новое значение объекта')

        with tap.subtest(3, 'тотальное переименование') as taps:
            taps.eq(path.rreplace_keys('*', '', 'cde'),
                    5, 'все корневые элементы заменены')
            taps.eq(path('acdecde'), 'Hello, world', 'Новое значение объекта')
            taps.eq(path('-1cde'), 'error', 'числовое стало символьным')

        with tap.subtest(3, 'переименование с непустым суффиксом') as taps:
            taps.eq(path.rreplace_keys('*', '-1cde', '--1cde'),
                    1, 'Один элемент имел префикс')
            taps.eq(path('acdecde'), 'Hello, world', 'Новое значение объекта')
            taps.eq(path('--1cde'), 'error', 'переименованный ключ')
