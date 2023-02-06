from mouse import Has, Mouse
# pylint: disable=blacklisted-name
from mouse.exception import ErCoerce


def test_coerce_str(tap):
    with tap.plan(3):
        class Foo(Mouse):
            # pylint: disable=unnecessary-lambda
            key = Has(types=str, coerce=lambda x: str(x))

        foo = Foo(key=123)
        tap.isa_ok(foo, Foo, 'instance created')
        tap.isa_ok(foo.key, str, 'type(foo.key)')
        tap.eq(foo.key, '123', 'key.value')

def test_coerce_none(tap):
    with tap.plan(3):
        class Foo(Mouse):
            # pylint: disable=unnecessary-lambda
            key = Has(types=str, coerce=lambda x: x)

        foo = Foo(key=None)
        tap.isa_ok(foo, Foo, 'instance created')
        tap.isa_ok(foo.key, type(None), 'type(foo.key)')
        tap.eq(foo.key, None, 'key.value')


def test_coerce_str_none_nolambda(tap):
    with tap.plan(3):
        class Foo(Mouse):
            # pylint: disable=unnecessary-lambda
            key = Has(types=str, coerce=str)

        foo = Foo(key=None)
        tap.isa_ok(foo, Foo, 'instance created')
        tap.isa_ok(foo.key, type(None), 'type(foo.key)')
        tap.eq(foo.key, None, 'key.value')

def test_coerce_error(tap):
    with tap.plan(2):
        class Foo(Mouse):
            # pylint: disable=unnecessary-lambda
            key1 = Has(types=int, coerce=int, raise_er_coerce=True)
            key2 = Has(types=int, coerce=int)

        with tap.raises(ErCoerce, 'Coerce exception'):
            Foo(key1='', key2='2')

        with tap.raises(ValueError, 'Default exception'):
            Foo(key1='2', key2='')
