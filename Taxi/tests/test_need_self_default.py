from mouse import Mouse, Has
from mouse.exception import ErNeedSelf

def test_need_self(tap):
    # pylint: disable=blacklisted-name
    with tap.plan(3):
        def _default(self=None, field=None):
            if not self:
                raise ErNeedSelf()
            return self.key + ' default ' + field.name

        class Foo(Mouse):
            key = Has(types=str)
            value = Has(types=str, default=_default)

        foo = Foo(key='abc')
        tap.isa_ok(foo, Foo, 'instance created')
        tap.eq(foo.key, 'abc', 'key')
        tap.eq(foo.value, 'abc default value', 'value')
