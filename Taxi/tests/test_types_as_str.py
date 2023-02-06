from mouse import Mouse, Has


def test_types(tap):
    with tap:
        class Foo(Mouse):
            next_value = Has('Foo')


        first = Foo()
        tap.isa_ok(first, Foo, 'first item')

        second = Foo(next_value=first)
        tap.isa_ok(second, Foo, 'second item')

        tap.eq(second.next_value, first, 'next_value')
