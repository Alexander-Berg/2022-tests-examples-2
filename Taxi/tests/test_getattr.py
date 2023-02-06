from mouse import Mouse, Has
from mouse.exception import ErNoAttribute


def test_getattr(tap):
    with tap.plan(4):
        # pylint: disable=blacklisted-name
        class Foo(Mouse):
            bar = Has(str)

        foo = Foo(bar='abc')
        tap.isa_ok(foo, Foo, 'instance created')
        tap.eq(foo.bar, 'abc', 'foo.bar')
        tap.eq(foo['bar'], 'abc', 'foo["bar"]')

        with tap.raises(ErNoAttribute, 'foo["unknown"] throw exception'):
            foo['unknown']  # pylint: disable=pointless-statement
