from mouse import Has, Mouse
from mouse.exception import ErReadOnlyAttribute

def test_ro(tap):
    with tap.plan(4):
        # pylint: disable=blacklisted-name
        class Foo(Mouse):
            foo = Has(str, mode='ro')

        foo = Foo(foo='hello')
        tap.isa_ok(foo, Foo, 'instance created')
        tap.eq(foo.foo, 'hello', 'attribute value')

        with tap.raises(ErReadOnlyAttribute, 'read only exception'):
            foo.foo = 'abc'

        tap.eq(foo.foo, 'hello', 'attribute value')
