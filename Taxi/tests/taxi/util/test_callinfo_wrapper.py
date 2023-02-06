import functools

from taxi.util import callinfo


def test_calls_info_wrapper():
    def simple_func(arg_a, arg_b):
        pass

    wrap_func = functools.wraps(simple_func)(
        callinfo.CallsInfoWrapper(simple_func),
    )
    wrap_func(1, 2)
    wrap_func(1, 2)
    assert wrap_func.calls == [
        {'arg_a': 1, 'arg_b': 2},
        {'arg_a': 1, 'arg_b': 2},
    ]
    assert wrap_func.call is None
    assert wrap_func.calls == []

    wrap_func(1, 1)
    wrap_func(2, 2)
    wrap_func(3, 3)
    assert wrap_func.call == {'arg_a': 1, 'arg_b': 1}
    assert wrap_func.call == {'arg_a': 2, 'arg_b': 2}
    assert wrap_func.call == {'arg_a': 3, 'arg_b': 3}
    assert wrap_func.call is None
    assert wrap_func.calls == []

    wrap_func(1, 1)
    wrap_func(2, 2)
    wrap_func(3, 3)
    assert wrap_func.call == {'arg_a': 1, 'arg_b': 1}
    assert wrap_func.calls == [
        {'arg_a': 2, 'arg_b': 2},
        {'arg_a': 3, 'arg_b': 3},
    ]
    assert wrap_func.call is None
    assert wrap_func.calls == []
