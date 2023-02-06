from mouse import Mouse, Has
from mouse.exception import ErUnknownField

def test_rehashed(tap):
    with tap.plan(21):
        # pylint: disable=blacklisted-name
        class FooBar(Mouse):
            foo = Has(str)

        foo = FooBar(foo='abc')
        tap.isa_ok(foo, FooBar, 'instance created')
        tap.ok(not foo.rehashed('foo'), 'not rehashed')

        foo.foo = 'abc'
        tap.ok(not foo.rehashed('foo'), 'not rehashed yet')

        foo.foo = 'cde'
        tap.ok(foo.rehashed('foo'), 'rehashed: new value')
        tap.eq(foo.rehashed(), {'foo'}, 'rehashed set')

        with tap.raises(ErUnknownField, 'Unknown field exception'):
            foo.rehashed('Unknown')

        tap.eq(foo.rehashed(foo=False), None, 'clear one rehashed field')
        tap.ok(not foo.rehashed('foo'), 'not rehashed')
        tap.eq(foo.rehashed(), set(), 'rehashed set')


        tap.eq(
            foo.rehashed({'bar': True}, foo=True),
            None,
            'set one rehashed field')
        tap.ok(foo.rehashed('foo'), 'not rehashed')
        tap.eq(foo.rehashed(), {'foo'}, 'rehashed set')


        tap.eq(foo.rehash({'foo': 'bar'}), None, 'foo=bar')
        tap.eq(foo.foo, 'bar', 'value')
        tap.ok(foo.rehashed('foo'), 'rehashed')

        tap.eq(foo.rehash(foo='baz'), None, 'foo=bar')
        tap.eq(foo.foo, 'baz', 'value')
        tap.ok(foo.rehashed('foo'), 'rehashed')

        tap.eq(foo.rehash('foo', 'baze'), None, 'foo=bar')
        tap.eq(foo.foo, 'baze', 'value')
        tap.ok(foo.rehashed('foo'), 'rehashed')
