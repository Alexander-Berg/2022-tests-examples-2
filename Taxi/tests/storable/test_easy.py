from mouse import Has
from libstall.model.storable import Base


class TstModel(Base):
    id      = Has(types=(str,), required=True)
    name    = Has(types=(str,), required=True)
    value   = Has(types=int, default=10)
    cvalue  = Has(types=int,
                  coerce=lambda x: x+1,
                  default=10,
                  always_coerce=True)
    var = 112
    var2 = 115


def test_instance(tap):
    with tap.plan(7):
        t = TstModel({'var': 'b', 'id': '1123', 'name': 'hello'}, var2=188)
        tap.ok(t, 'инстанцировано')
        tap.eq(t.var, 112, 'rehash на поля не Has не работает')
        tap.eq(t.var2, 188, 'конструктор ставит объявленные атрибуты')

        tap.eq(t.pure_python(),
               {
                   'id': '1123',
                   'name': 'hello',
                   'value': 10,
                   'cvalue': 11,
               },
               'сериализация')

        tap.eq(t.id, '1123', 'значение атрибута')
        # pylint: disable=no-member
        tap.eq(
            t.name,
            'hello',
            'значение атрибута не упомянутого в конструкторе'
        )
        tap.eq(t.value, 10, 'значение по умолчанию')
