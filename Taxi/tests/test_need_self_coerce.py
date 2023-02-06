from mouse import Mouse, Has
from mouse.exception import ErNeedSelf

def test_coerce_runtime(tap):
    with tap.plan(4):
        # pylint: disable=blacklisted-name
        def _coerce(value, self=None, field=None):
            if not self:
                raise ErNeedSelf()
            return f'{self.foo} {value} {field.name}'

        class Foo(Mouse):
            foo = Has(types=str)
            bar = Has(str, coerce=_coerce)

        obj = Foo(foo='foo', bar='bar')
        tap.isa_ok(obj, Foo, 'instance created')
        tap.eq(obj.foo, 'foo', 'foo')
        tap.eq(obj.bar, 'bar', 'bar')

        obj.bar = 345
        tap.eq(obj.bar, 'foo 345 bar', 'coerced with self')


def test_coerce_init(tap):
    with tap.plan(3):
        # pylint: disable=blacklisted-name
        def _coerce(value, self=None, field=None):
            if not self:
                raise ErNeedSelf()
            return f'{self.foo} {value} {field.name}'

        class Foo(Mouse):
            foo = Has(types=str)
            bar = Has(str, coerce=_coerce)

        obj = Foo(foo='foo', bar=345)
        tap.isa_ok(obj, Foo, 'instance created')
        tap.eq(obj.foo, 'foo', 'foo')
        tap.eq(obj.bar, 'foo 345 bar', 'coerced with self')


def test_coerce_init_depends(tap):
    with tap.plan(4):
        # pylint: disable=blacklisted-name
        def _coerce(value, self=None, field=None):
            if not self:
                raise ErNeedSelf()
            return (
                f'foo={self.foo} '
                f'bar={self.bar is not None} '
                f'baz={self.baz is not None} '
                f'{value} '
                f'field={field.name}'
            )

        class Foo(Mouse):
            foo = Has(types=str)
            bar = Has(str, coerce=_coerce, depends='baz')
            baz = Has(str, coerce=_coerce)

        obj = Foo(foo='foo', bar=345, baz=567)
        tap.isa_ok(obj, Foo, 'instance created')
        tap.eq(obj.foo, 'foo', 'foo')
        tap.eq(
            obj.baz,
            'foo=foo bar=False baz=False 567 field=baz',
            'baz coerced first'
        )
        tap.eq(
            obj.bar,
            'foo=foo bar=False baz=True 345 field=bar',
            'bar coerced with self'
        )


def test_coerce_init_depends2(tap):
    with tap.plan(4):
        # pylint: disable=blacklisted-name
        def _coerce(value, self=None, field=None):
            if not self:
                raise ErNeedSelf()
            return (
                f'foo={self.foo} '
                f'bar={self.bar is not None} '
                f'baz={self.baz is not None} '
                f'{value} '
                f'field={field.name}'
            )

        class Foo(Mouse):
            foo = Has(types=str)
            bar = Has(str, coerce=_coerce)
            baz = Has(str, coerce=_coerce, depends=['bar'])

        obj = Foo(foo='foo', bar=345, baz=567)
        tap.isa_ok(obj, Foo, 'instance created')
        tap.eq(obj.foo, 'foo', 'foo')
        tap.eq(
            obj.baz,
            'foo=foo bar=True baz=False 567 field=baz',
            'baz coerced first'
        )
        tap.eq(
            obj.bar,
            'foo=foo bar=False baz=False 345 field=bar',
            'bar coerced with self'
        )

