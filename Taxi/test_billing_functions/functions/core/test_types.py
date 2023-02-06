from billing_functions.functions.core import types


def test_bool():
    assert types.TrueOrReason.make_value(True)
    assert not types.TrueOrReason.make_reason('abc')
