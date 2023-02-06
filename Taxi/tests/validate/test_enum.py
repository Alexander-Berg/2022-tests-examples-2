from mouse import Mouse, Has
from mouse.exception import ErValidate

def test_enum(tap):
    with tap.plan(3):
        # pylint: disable=blacklisted-name
        class Foo(Mouse):
            key = Has(str, enum=('a', 'b'))

        foo = Foo(key='a')
        tap.isa_ok(foo, Foo, 'instance created')
        tap.eq(foo.key, 'a', 'foo.key')

        with tap.raises(ErValidate, 'enum validate exception'):
            foo.key = 'c'


def test_enum_list(tap):
    with tap.plan(4):
        # pylint: disable=blacklisted-name
        class Foo(Mouse):
            key = Has(list, enum=('a', 'b'))

        foo = Foo(key=['a'])
        tap.isa_ok(foo, Foo, 'instance created')
        tap.eq(foo.key, ['a'], 'foo.key')

        with tap.raises(ErValidate, 'enum validate exception'):
            foo.key = ['c']

        with tap.raises(ErValidate, 'enum validate exception'):
            Foo(key=['a', 'b', 'c'])
