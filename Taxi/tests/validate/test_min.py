from mouse import Mouse, Has
from mouse.exception import ErValidate

def test_enum(tap):
    with tap.plan(5):
        # pylint: disable=blacklisted-name
        class Foo(Mouse):
            key = Has(int, min=10)

        foo = Foo(key=11)
        tap.isa_ok(foo, Foo, 'instance created')
        tap.eq(foo.key, 11, 'foo.key')

        foo.key = 10
        tap.eq(foo.key, 10, 'foo.key changed')

        with tap.raises(ErValidate, 'validate exception'):
            foo.key = 9

        with tap.raises(ErValidate, 'validate exception'):
            Foo(key=9)
