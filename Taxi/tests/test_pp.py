from mouse import Mouse, Has


def test_pure_python(tap):
    with tap.plan(5):
        # pylint: disable=blacklisted-name
        class Foo(Mouse):
            bar = Has(str)
            baz = Has(int)

        obj = Foo(bar='abc', baz=123)
        tap.isa_ok(obj, Foo, 'instance created')

        tap.eq(
            obj.pure_python(),
            {
                'bar': 'abc',
                'baz': 123,
            },
            'pure_python'
        )

        class Fee(Mouse):
            uvw = Has('int')
            foo = Has(Foo, coerce=Foo)

        obj = Fee(foo={'bar': 'cde', 'baz': 345}, uvw=721)
        tap.isa_ok(obj, Fee, 'instance created (inherits)')

        tap.eq(
            obj.pure_python(),
            {
                'foo': {
                    'bar': 'cde',
                    'baz': 345,
                },
                'uvw': 721,
            },
            'pure_python'
        )

        tap.eq(
            obj.pure_python(hello='world'),
            {
                'foo': {
                    'bar': 'cde',
                    'baz': 345,
                },
                'uvw': 721,
                'hello': 'world',
            },
            'pure_python(kwargs)'
        )

        print(obj.foo.meta.fields)
