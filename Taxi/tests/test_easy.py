from mouse import Mouse, Has


def test_easy(tap):
    # pylint: disable=blacklisted-name
    with tap.plan(3):
        class Foo(Mouse):
            key = Has(types=str, required=False)


        foo = Foo({'key': 'abc'})
        tap.isa_ok(foo, Foo, 'instance created')
        tap.eq(foo.key, 'abc', 'value')
        tap.isa_ok(foo.key, str, 'type foo.key')


def test_set(tap):
    # pylint: disable=blacklisted-name
    with tap.plan(7):
        class Foo(Mouse, foo='bar'):
            key = Has(types=str, required=False)


        foo = Foo(key='abc')
        tap.isa_ok(foo, Foo, 'instance created')
        tap.eq(foo.key, 'abc', 'value')
        tap.isa_ok(foo.key, str, 'type foo.key')

        bar = Foo(key='cde')
        tap.isa_ok(bar, Foo, 'instance created')
        tap.eq(bar.key, 'cde', 'value')
        tap.isa_ok(bar.key, str, 'type bar.key')

        tap.ne(foo.key, bar.key, 'foo != bar')


def test_twice(tap):
    # pylint: disable=blacklisted-name
    with tap.plan(8):
        class Foo(Mouse):
            key = Has(types=str, required=False)

        class Bar(Mouse):
            value = Has(types=str, required=False)


        foo = Foo(key='abc')
        tap.isa_ok(foo, Foo, 'instance created')

        bar = Bar(value='cde')
        tap.isa_ok(bar, Bar, 'instance created')


        tap.ok(hasattr(foo, 'key'), 'exists foo.key')
        tap.ok(not hasattr(foo, 'value'), 'not exists foo.value')

        tap.ok(not hasattr(bar, 'key'), 'not exists bar.key')
        tap.ok(hasattr(bar, 'value'), 'exists bar.value')

        tap.eq(foo.key, 'abc', 'foo.key')
        tap.eq(bar.value, 'cde', 'bar.value')
