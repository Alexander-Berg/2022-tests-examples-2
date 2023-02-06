from mouse import Mouse, Has


def test_kwargs(tap):
    with tap.plan(8):
        # pylint: disable=blacklisted-name
        class Foo(Mouse):
            bar = Has(str)

            mode: str = None

        foo = Foo(bar='abc', mode='cde', unknown='def')
        tap.isa_ok(foo, Foo, 'instance created')
        tap.eq(foo.bar, 'abc', 'foo.bar')
        tap.eq(foo.mode, None, 'foo mode is not set')
        tap.ok(not hasattr(foo, 'unknown'), 'foo.unknown do not exists')

        foo = Foo({'bar': 'abc'}, mode='cde', unknown='def')
        tap.isa_ok(foo, Foo, 'instance created')
        tap.eq(foo.bar, 'abc', 'foo.bar')
        tap.eq(foo.mode, 'cde', 'foo mode is set')
        tap.ok(not hasattr(foo, 'unknown'), 'foo.unknown do not exists')
