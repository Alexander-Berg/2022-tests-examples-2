from mouse import Mouse, Has


def test_coerce(tap):
    with tap.plan(3):
        # pylint: disable=blacklisted-name
        class Foo(Mouse):
            value = Has(str,
                        coerce=lambda x: f'coerced: {x}',
                        always_coerce=True)

            v2 = Has(str, always_coerce=True)

        foo = Foo(value='abc')
        tap.isa_ok(foo, Foo, 'instance created')
        tap.eq(foo.value, 'coerced: abc', 'value')

        foo.value = 'cde'
        tap.eq(foo.value, 'coerced: cde', 'value')
