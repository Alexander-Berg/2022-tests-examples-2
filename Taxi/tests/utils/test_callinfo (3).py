import asyncio
import functools

import pytest

from taxi_tests.utils import callinfo

# pylint: disable=eval-used


def test_callinfo():
    def noargs():
        pass

    getter = callinfo.callinfo(noargs)
    assert getter((), {}) == {}

    def positional(arg_a, arg_b):
        pass

    getter = callinfo.callinfo(positional)
    assert getter((1, 2), {}) == {'arg_a': 1, 'arg_b': 2}
    assert getter((1,), {'arg_b': 2}) == {'arg_a': 1, 'arg_b': 2}
    assert getter((), {'arg_a': 1, 'arg_b': 2}) == {'arg_a': 1, 'arg_b': 2}

    def positional_keyword(arg_a, arg_b, arg_c=3):
        pass

    getter = callinfo.callinfo(positional_keyword)
    assert getter((1, 2), {}) == {'arg_a': 1, 'arg_b': 2, 'arg_c': 3}
    assert getter((1, 2, 4), {}) == {'arg_a': 1, 'arg_b': 2, 'arg_c': 4}
    assert getter((1,), {'arg_b': 2, 'arg_c': 4}) == {
        'arg_a': 1,
        'arg_b': 2,
        'arg_c': 4,
    }

    def starargs(*args, **kwargs):
        pass

    getter = callinfo.callinfo(starargs)
    assert getter((1, 2), {}) == {'args': (1, 2), 'kwargs': {}}
    assert getter((1, 2), {'k': 'v'}) == {'args': (1, 2), 'kwargs': {'k': 'v'}}

    def mixed(arg_a, arg_b, arg_c=3, **kwargs):
        pass

    getter = callinfo.callinfo(mixed)
    assert getter((1, 2), {}) == {
        'arg_a': 1,
        'arg_b': 2,
        'arg_c': 3,
        'kwargs': {},
    }
    assert getter((1,), {'arg_z': 3, 'arg_b': 2, 'arg_c': 4}) == {
        'arg_a': 1,
        'arg_b': 2,
        'arg_c': 4,
        'kwargs': {'arg_z': 3},
    }

    kwonlyargs = eval('lambda a, *args, b, c=3, **kwargs: None')
    getter = callinfo.callinfo(kwonlyargs)
    assert getter((4,), {'b': 5}) == {
        'a': 4,
        'args': (),
        'b': 5,
        'c': 3,
        'kwargs': {},
    }
    assert getter((4,), {'b': 5, 'c': 2}) == {
        'a': 4,
        'args': (),
        'b': 5,
        'c': 2,
        'kwargs': {},
    }
    assert getter((4, 5, 6), {'b': 5}) == {
        'a': 4,
        'args': (5, 6),
        'b': 5,
        'c': 3,
        'kwargs': {},
    }
    assert getter((4, 5, 6), {'b': 5, 'c': 6}) == {
        'a': 4,
        'args': (5, 6),
        'b': 5,
        'c': 6,
        'kwargs': {},
    }
    assert getter((4, 5, 6), {'b': 5, 'c': 6, 'd': 7}) == {
        'a': 4,
        'args': (5, 6),
        'b': 5,
        'c': 6,
        'kwargs': {'d': 7},
    }


async def test_callqueue_wait():
    @callinfo.acallqueue
    def method(arg):
        pass

    async def async_task():
        await method(1)
        await asyncio.sleep(0.1)
        await method(2)

    asyncio.create_task(async_task())

    assert await method.wait_call() == {'arg': 1}
    assert await method.wait_call() == {'arg': 2}


async def test_callqueue_wait_timeout():
    @callinfo.acallqueue
    def method(arg):
        pass

    with pytest.raises(callinfo.CallQueueTimeoutError):
        assert await method.wait_call(timeout=0.1)


async def test_callqueue_next_call():
    @callinfo.acallqueue
    def method(arg):
        pass

    assert not method.has_calls
    with pytest.raises(callinfo.CallQueueEmptyError):
        assert await method.next_call()

    await method(1)
    await method(2)

    assert method.has_calls
    assert method.times_called == 2

    assert method.next_call() == {'arg': 1}
    assert method.next_call() == {'arg': 2}

    assert not method.has_calls
    with pytest.raises(callinfo.CallQueueEmptyError):
        assert method.next_call()


async def test_acallqueue_next_call():
    @callinfo.acallqueue
    async def method(arg):
        pass

    assert not method.has_calls
    with pytest.raises(callinfo.CallQueueEmptyError):
        assert method.next_call()

    await method(1)
    await method(2)

    assert method.has_calls
    assert method.times_called == 2

    assert method.next_call() == {'arg': 1}
    assert method.next_call() == {'arg': 2}

    assert not method.has_calls
    with pytest.raises(callinfo.CallQueueEmptyError):
        assert method.next_call()


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
