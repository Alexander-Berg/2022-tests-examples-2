from libstall.model import storable


class TstModel(storable.Base):
    id=storable.Attribute(types=(str,), required=True)
    name=storable.Attribute(
        types=(str,),
        required=False,
        coerce=lambda x: x + 'a',
        always_coerce=True
    )


def test_rehashed(tap):

    with tap.plan(9):
        item = TstModel({'id': '123', 'name': 'vasya'})

        tap.ok(item, 'инстанцирован')

        tap.eq(
            dict(item.items('rehashed')),
            {},
            'после конструктора список чист'
        )
        tap.eq(item.name, 'vasyaa', 'в конструкторе coerce отработал')


        item.name = 'vasya'
        tap.eq(dict(item.items('rehashed')), {}, 'поле не изменилось')
        tap.ok(not item.rehashed('name'), 'rehashed -> False')
        tap.eq(item.name, 'vasyaa', 'coerce отработал')


        item.name = 'petya'
        tap.eq(
            dict(item.items('rehashed')),
            {'name': 'petyaa'},
            'поле изменилось'
        )
        tap.ok(item.rehashed('name'), 'rehashed -> True')
        tap.eq(item.name, 'petyaa', 'coerce отработал')

