from libstall.model.vars import Vars
from .record import VarsRecord


async def test_save_load(tap):
    with tap.plan(15, 'Работа с vars'):
        item = VarsRecord({'vars': {'hello': 'world'}})

        tap.isa_ok(item, VarsRecord, 'Инстанцировано')
        tap.isa_ok(item.vars, Vars, 'поле vars')
        tap.eq(item.vars('hello'), 'world', 'доступ к элементам')

        tap.ok(await item.save(), 'Сохранено')
        tap.eq(item.vars, {'hello': 'world'}, 'значение')
        item.vars['abc'] = 'cde'
        tap.ok(
            item.rehashed('vars'),
            'rehashed проставился при изменении vars'
        )

#         item.rehashed('vars', True)
        tap.ok(await item.save(), 'Сохранены изменения vars')
        tap.eq(item.vars,
               {'hello': 'world', 'abc': 'cde'},
               'Изменения итого')


        item.vars['foo'] = []
        tap.ok(
            item.rehashed('vars'),
            'rehashed проставился при изменении vars'
        )
        tap.ok(await item.save(), 'сохранено')
        tap.eq(
            item.vars,
            {'abc': 'cde', 'foo': [], 'hello': 'world'},
            'Изменения итого'
        )


        del item.vars['hello']
#         item.rehashed('vars', True)
        tap.ok(await item.save(), 'Сохранены изменения vars')
        tap.eq(item.vars, {'abc': 'cde', 'foo': []}, 'Изменения итого')

        del item.vars['abc']
#         item.rehashed('vars', True)
        tap.ok(await item.save(), 'Сохранены изменения vars')
        tap.eq(item.vars, {'foo': []}, 'Изменения итого')

