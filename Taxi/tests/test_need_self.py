from mouse import Mouse, Has
from mouse.exception import ErNeedSelf


# pylint: disable=unused-argument
def _test_coerce(value, self=None, field=None):
    if not self:
        raise ErNeedSelf()

    if value is None:
        return None

    return str(value)


def test_default_no_need_self(tap):
    with tap.plan(2):
        class Cls(Mouse):
            key = Has(str, default=lambda: 4, coerce=_test_coerce)
        # pylint: disable=blacklisted-name
        foo = Cls()
        tap.isa_ok(foo, Cls, 'instance')
        tap.eq(foo.key, '4', 'coerced')
