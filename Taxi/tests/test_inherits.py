from mouse import Has, Mouse

def test_inherit(tap):
    # pylint: disable=blacklisted-name
    with tap.plan(4):
        class Foo(Mouse):
            foo = Has(types=str, coerce=str)

        class Bar(Foo):
            bar = Has(types=str, coerce=str)

        bar = Bar(foo='foo', bar='bar')
        tap.isa_ok(bar, Bar, 'created')
        tap.eq(set(bar.meta.fields.keys()), {'foo', 'bar'}, 'fields')
        tap.eq(bar.foo, 'foo', 'bar.foo')
        tap.eq(bar.bar, 'bar', 'bar.bar')


def test_inherit_attr(tap):
    # pylint: disable=blacklisted-name
    with tap.plan(7):
        class Foo(Mouse, foo='BAR'):
            foo = Has(types=str, coerce=str)

        class Bar(Foo):
            bar = Has(types=str, coerce=str)

        foo = Foo(foo='foo')
        tap.isa_ok(foo, Foo, 'instance created')
        tap.eq(foo.meta.foo, 'BAR', 'meta.foo')


        bar = Bar(foo='foo', bar='bar')
        tap.isa_ok(bar, Bar, 'created')
        tap.eq(set(bar.meta.fields.keys()), {'foo', 'bar'}, 'fields')
        tap.eq(bar.foo, 'foo', 'bar.foo')
        tap.eq(bar.bar, 'bar', 'bar.bar')

        tap.eq(bar.meta.foo, 'BAR', 'meta.foo')
