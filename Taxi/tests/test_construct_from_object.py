from mouse import Mouse, Has


def test_construct(tap):
    with tap.plan(3):
        # pylint: disable=blacklisted-name
        class Foo(Mouse):
            bar = Has(str)

        foo = Foo(bar='123')
        tap.eq(foo.bar, '123', 'foo.bar')

        obj = Foo(foo)
        tap.eq(obj.bar, '123', 'obj.bar')

        foo.bar = '345'

        tap.eq((foo.bar, obj.bar), ('345', '123'), 'result')

