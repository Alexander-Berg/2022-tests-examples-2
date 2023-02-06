from twisted.internet import defer
import pytest

from taxi.core import memstorage


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_memoize_usage(sleep):
    function_calls = []

    @memstorage.memoize(fresh_time=10)
    def function(*args, **kwargs):
        function_calls.append((args, kwargs))
        return (args, kwargs)

    result1 = yield function(1, y=2)
    result2 = yield function(1, y=2)
    assert len(function_calls) == 1
    assert result1 == result2 == function_calls[0] == ((1,), {'y': 2})

    result3 = yield function(3)
    assert len(function_calls) == 2
    assert result3 == function_calls[1] == ((3,), {})

    yield sleep(21)

    yield function(1, y=2)
    yield function(3)
    assert len(function_calls) == 4


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_memoize_blocking(sleep):
    calls = []

    @memstorage.memoize(fresh_time=10)
    def foo(*args, **kwargs):
        calls.append((args, kwargs))
        return (args, kwargs)

    assert foo(1) == foo(1) == ((1,), {})
    assert len(calls) == 1

    # No soft caching
    yield sleep(15)
    assert foo(1) == foo(1) == ((1,), {})
    assert len(calls) == 2


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_memoize_async_soft_cache(sleep):
    deferreds = []

    @memstorage.memoize(fresh_time=10)
    def foo(*args, **kwargs):
        deferred = defer.Deferred()
        deferreds.append(deferred)
        return deferred

    # Calculate for the first time
    deferred = foo()
    assert len(deferreds) == 1
    deferreds[-1].callback('result')
    assert (yield deferred) == 'result'

    # Take result from cache
    assert (yield foo()) == 'result'
    assert len(deferreds) == 1

    # Soft caching: return result and start recalculation
    yield sleep(15)
    assert (yield foo()) == 'result'
    assert (yield foo()) == 'result'
    assert len(deferreds) == 2

    # Fresh result after recalculation
    deferreds[-1].callback('another_result')
    assert (yield foo()) == 'another_result'

    # In a 20 seconds cache will be empty
    yield sleep(10)
    yield sleep(10)
    deferred = foo()
    assert len(deferreds) == 3
    assert not deferred.called
    deferreds[-1].callback('third_result')
    assert (yield deferred) == 'third_result'


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_memoize_multiple_functions():
    @memstorage.memoize(fresh_time=10)
    def foo(*args, **kwargs):
        return 'foo_result'

    @memstorage.memoize(fresh_time=10)
    def bar(*args, **kwargs):
        return 'bar_result'

    assert (yield foo()) == 'foo_result'
    assert (yield bar()) == 'bar_result'


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_memoize_simultaneous_calls(sleep):
    deferreds = []

    @memstorage.memoize(fresh_time=10)
    def foo(*args, **kwargs):
        deferred = defer.Deferred()
        deferreds.append(deferred)
        return deferred

    deferred1 = foo()
    deferred2 = foo()
    assert len(deferreds) == 1
    assert deferred1 != deferred2
    deferreds[-1].callback('hello')
    print 'same orig', deferreds[-1]
    print 'd1', deferred1
    print 'd2', deferred2
    assert deferred1.result == 'hello'
    assert deferred2.result == 'hello'

    # Start recalculation before full invalidation
    yield sleep(19)
    assert (yield foo()) == 'hello'

    # Recalculation is not finished, old result is returned
    yield sleep(5)
    assert (yield foo()) == 'hello'

    # No it is finished
    deferreds[-1].callback('bye')
    assert (yield foo()) == 'bye'


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_memoize_error_handling():
    calls = []

    @memstorage.memoize()
    def foo():
        calls.append('something')
        raise ValueError

    for i in range(3):
        with pytest.raises(ValueError):
            yield foo()

    # Exception is not memoized
    assert len(calls) == 3


@pytest.mark.filldb(_fill=False)
def test_put_and_get_and_rm():
    assert memstorage.get('key') is None
    memstorage.put('key', 'value')
    assert memstorage.get('key') == 'value'
    memstorage.remove('key')
    assert memstorage.get('key') is None


@pytest.mark.asyncenv('async')
@pytest.mark.filldb(_fill=False)
def test_inmemory_async_succeed():
    calls = []

    @memstorage.memoize(fresh_time=10)
    def function():
        calls.append(1)
        return defer.succeed('result')

    first = function()
    second = function()
    assert len(calls) == 1
    assert first.called
    assert first.result == 'result'
    assert second.called
    assert second.result == 'result'


@pytest.mark.asyncenv('async')
@pytest.mark.filldb(_fill=False)
def test_inmemory_async_fail():
    calls = []
    exception = ValueError('error description')

    @memstorage.memoize(fresh_time=10)
    def function():
        calls.append(1)
        return defer.fail(exception)

    first = function()
    second = function()
    assert len(calls) == 2
    assert first.called
    assert second.called


@pytest.mark.asyncenv('async')
@pytest.mark.filldb(_fill=False)
def test_inmemory_async_delayed_fail():
    deferred = defer.Deferred()
    calls = []

    @memstorage.memoize(fresh_time=10)
    def function():
        calls.append(1)
        return deferred

    first = function()
    second = function()
    third = function()
    assert len(calls) == 1

    deferred.errback(ValueError('error description'))
    assert first.called
    assert second.called
    assert third.called
