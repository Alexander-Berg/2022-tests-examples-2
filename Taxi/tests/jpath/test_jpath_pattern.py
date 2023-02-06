import pytest

from ymlcfg.jpath import JPath

@pytest.mark.parametrize('cache', [False, True])
@pytest.mark.parametrize('safe', [False, True])
def test_jpath(tap, safe, cache):
    with tap.plan(9):
        o = {
            'a3': 'b',
            'c': [1, 2, 3],
            33: 'abc',
            (-1): 'error',

            'nest1': {'abc': 'cde'},
            'nest2': {'aab': 'def'},
            'nest3': {'123': 345},
            'a66': {'12': '34'},
        }

        path = JPath(o, safe=safe, cache=cache)

        tap.ok(path, 'инстанцирован')

        tap.eq(path('*'), list(o.values()), 'звездочка в начале')
        tap.eq(path('*3'),
               ['b', 'abc', {'123': 345}],
               'звездочка в начале с символом')
        tap.eq(path('c.*'), [1, 2, 3], 'звездочка в элементе массива')
        tap.eq(path('*.*b*'), ['cde', 'def'], 'пара звездочек в пути')

        tap.eq(path('aa*.bb*.cc', [42]), [42], 'Не найденное - нет исключения')


        if cache:
            tap.in_ok('*3', path.cached, 'Закешировано')
        else:
            tap.ok('*3' not in path.cached, 'кеш не используется')

        if safe:
            tap.ne(id(path('*66')[0]), id(o['a66']), 'копии объектов')
        else:
            tap.eq(id(path('*66')[0]), id(o['a66']), 'сами объекты')

        with tap.raises(path.NotFound, 'Без default есть исключение'):
            path('aa*.bb*.cc')
