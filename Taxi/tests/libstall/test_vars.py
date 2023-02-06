import copy
from ymlcfg.jpath import JPath
from libstall.model.vars import Vars

def test_vars(tap):
    with tap.plan(22, 'Тесты vars'):
        tvars = Vars(a='123', b=32)

        tap.isa_ok(tvars, Vars, 'создан')
        tap.eq(tvars, {'a': '123', 'b': 32}, 'Равенство dict')

        tap.eq(tvars.result_dict, {'a': '123', 'b': 32}, 'результирующий dict')
        tap.isa_ok(tvars.result_dict, dict, 'result_dict - dict')
        tap.eq(tvars('a'), '123', 'jpath')
        tap.eq(tvars.deleted_keys, [], 'удалённые элементы')
        tap.eq(tvars.updated_dict, {}, 'изменённые элементы')

        with tap.raises(JPath.NotFound, 'неизвестный ключ'):
            tap.eq(tvars('a.abc'), 'ошибка')
        tap.eq(tvars('a.abc', 32), 32, 'значение по умолчанию jpath')

        tvars['a'] = {'abc': 27}
        tap.eq(tvars, {'a': {'abc': 27}, 'b': 32}, 'vars поменяли')
        tap.eq(tvars.result_dict, {'a': {'abc': 27}, 'b': 32}, 'vars поменяли')
        tap.eq(tvars('a.abc'), 27, 'значение по jpath')
        tap.eq(tvars.deleted_keys, [], 'удалённые элементы')
        tap.eq(tvars.updated_dict, {'a': {'abc': 27}}, 'словарь изменений')

        del tvars['b']
        tap.eq(tvars, {'a': {'abc': 27}}, 'vars поменяли')
        tap.eq(tvars.result_dict, {'a': {'abc': 27}}, 'vars поменяли')
        tap.eq(tvars('a.abc'), 27, 'значение по jpath')
        tap.eq(tvars.deleted_keys, ['b'], 'удалённые элементы')
        tap.eq(tvars.updated_dict, {'a': {'abc': 27}}, 'словарь изменений')

        c = copy.deepcopy(tvars)
        tap.ok(c, 'копия')
        tap.isa_ok(c, dict, 'в копии словарь')
        tap.eq(c, {'a': {'abc': 27}}, 'содержимое копии')
