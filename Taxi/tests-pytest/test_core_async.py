from twisted.internet import defer
from twisted.python import failure
import pytest

from taxi.core import async


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_deferred_mimic(mock):
    @mock
    def callback(result, *args, **kwargs):
        return (result, 42)

    @mock
    def errback(result, *args, **kwargs):
        raise RuntimeError('never occurs')

    # Following Deferred methods are supported
    d = async.DeferredMimic()
    d.addCallbacks(
        callback, errback=errback,
        callbackArgs=('foo',), callbackKeywords={'bar': 3},
        errbackArgs=('no', 'matter'), errbackKeywords={'never': 'occurs'}
    )
    d.addCallback(callback, 'baz', ban=4)
    d.addErrback(errback, 'never-never', occurs='never')
    d.addBoth(callback, 'x', y=5)

    # Result must be explicitly returned by `d.callback(..)` call
    assert not hasattr(d, 'result')

    # Errors should be handled (and possibly raised) in a function that
    # returns DeferredMimic instance. We don't want to implement all
    # `twisted.internet.defer.Deferred` logic, we just want to write
    # blocking and asynchronous code along avoiding to get too much
    # copy-n-paste.
    with pytest.raises(AttributeError) as excinfo:
        d.errback(ValueError('some error'))
    msg = 'errback was called but errors should be handled before callback'
    assert msg in excinfo.value

    # `callback` method run the chain of calls
    assert d.callback('the result') is None

    # Final result will be produced by last callback
    assert d.result == ((('the result', 42), 42), 42)

    # Totally we have 3 called callbacks, each call has been made with
    # respect to passed args and kwargs
    assert callback.calls == [
        {
            'result': 'the result',
            'args': ('foo',),
            'kwargs': {'bar': 3},
        },
        {
            'result': ('the result', 42),
            'args': ('baz',),
            'kwargs': {'ban': 4},
        },
        {
            'result': (('the result', 42), 42),
            'args': ('x',),
            'kwargs': {'y': 5},
        },
    ]


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_deferred_mimic_exception(mock):
    # This test shows that DeferredMimic won't catch any exception
    # raised inside some callback

    @mock
    def callback(result, *args, **kwargs):
        return (result, 42)

    def callback_with_error(result):
        raise RuntimeError('runtime error description')

    d = async.DeferredMimic()
    d.addCallback(callback, 'first')
    d.addCallback(callback_with_error)
    d.addCallback(callback, 'second')

    with pytest.raises(RuntimeError) as excinfo:
        d.callback('some result')
    assert 'runtime error description' in excinfo.value

    callback.calls == [
        {'result': 'some result', 'args': ('first', ), 'kwargs': {}}
    ]

    # Now we have undetermined result (and something left in callbacks)
    assert len(d.callbacks) == 1


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_deferred_mimic_already_called(mock):
    # Test that fired DeferredMimic run callbacks immediately

    @mock
    def callback(result, *args, **kwargs):
        return (result, 'plus')

    @mock
    def errback(result, *args, **kwargs):
        return (result, 'error')

    # You can fire without callbacks
    d = async.DeferredMimic()
    d.callback('result')
    d.callback('new result')
    assert d.result == 'new result'
    assert not callback.calls
    assert not errback.calls

    # But when you add new callback it will be fired immediately
    d.addCallback(callback, 'x', y=1)
    d.addErrback(errback, 'will be skipped')
    d.addCallback(callback, 'foo', bar=2)
    assert d.result == (('new result', 'plus'), 'plus')
    assert callback.calls == [
        {
            'result': 'new result',
            'args': ('x',),
            'kwargs': {'y': 1}
        },
        {
            'result': ('new result', 'plus'),
            'args': ('foo',),
            'kwargs': {'bar': 2}
        },
    ]
    assert not errback.calls

    # Last result will be saved, no new callback calls
    d.callback('very new result')
    assert d.result == 'very new result'
    assert not callback.calls


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_defer_or_result(mock):
    args = ('foo', 'bar', 'baz')
    kwargs = {'x': 1, 'y': 2, 'z': 3}

    @mock
    def callback(result, *args, **kwargs):
        return (result, 'plus')

    # Function must return Deferred or DeferredMimic instance
    @mock
    @async.defer_or_result
    def wrong_usage(*args, **kwargs):
        return 42

    with pytest.raises(AssertionError) as excinfo:
        wrong_usage(*args, **kwargs)
    msg = 'Deferred or DeferredMimic expected, got %s' % repr(42)
    assert msg in excinfo.value
    assert wrong_usage.calls == [{'args': args, 'kwargs': kwargs}]

    # DeferredMimic must be fired
    @mock
    @async.defer_or_result
    def unfired_mimic(*args, **kwargs):
        d = async.DeferredMimic()
        d.addCallback(callback, 'unfired')
        return d

    with pytest.raises(AssertionError) as excinfo:
        unfired_mimic(*args, **kwargs)
    assert 'DeferredMimic must be fired' in excinfo.value
    assert unfired_mimic.calls == [{'args': args, 'kwargs': kwargs}]

    # Blocking call just return result immediately
    @mock
    @async.defer_or_result
    def blocking_call(*args, **kwargs):
        d = async.DeferredMimic()
        d.callback('result')
        d.addCallback(callback, 'blocking')
        return d

    assert blocking_call(*args, **kwargs) == ('result', 'plus')
    assert blocking_call.calls == [{'args': args, 'kwargs': kwargs}]
    assert callback.calls == [
        {'result': 'result', 'args': ('blocking',), 'kwargs': {}}
    ]

    # Async call return deferred without any changes
    @mock
    @async.defer_or_result
    def async_call(*args, **kwargs):
        d = defer.Deferred()
        d.addCallback(callback, 'async')
        deferreds.append(d)
        return d

    deferreds = []
    d = async_call(*args, **kwargs)
    assert async_call.calls == [{'args': args, 'kwargs': kwargs}]
    assert deferreds == [d]

    # Exceptions won't be catched
    @mock
    @async.defer_or_result
    def call_with_error(*args, **kwargs):
        raise ValueError('error description')
        return 42

    with pytest.raises(ValueError) as excinfo:
        call_with_error(*args, **kwargs)
    assert 'error description' in excinfo.value
    assert call_with_error.calls == [{'args': args, 'kwargs': kwargs}]


@pytest.mark.filldb(_fill=False)
def test_async_call(asyncenv, mock):
    deferreds = []
    args = ('foo', 'bar')
    kwargs = {'x': 1, 'y': 2}

    @mock
    def async_func(*args, **kwargs):
        d = async.Deferred()
        deferreds.append(d)
        return d

    @mock
    def blocking_func(*args, **kwargs):
        return 'result'

    # If twisted is installed and reactor is running call async function
    if asyncenv == 'async':
        d = async.call(async_func, blocking_func, *args, **kwargs)
        assert async_func.calls == [{'args': args, 'kwargs': kwargs}]
        assert isinstance(d, defer.Deferred)
        assert deferreds == [d]
        assert not blocking_func.calls

    # If twisted is not installed or reactor is not running fired
    # DeferredMimic will be returned
    if asyncenv == 'blocking':
        d = async.call(async_func, blocking_func, *args, **kwargs)
        assert blocking_func.calls == [{'args': args, 'kwargs': kwargs}]
        assert isinstance(d, async.DeferredMimic)
        assert d.result == 'result'
        assert not async_func.calls
        assert not deferreds


@pytest.mark.filldb(_fill=False)
def test_async_call_error(asyncenv):
    def async_func():
        return 'not a deferred'

    def blocking_func():
        return async.DeferredMimic()

    if asyncenv == 'async':
        with pytest.raises(AssertionError) as excinfo:
            async.call(async_func, lambda: None)
        msg = 'Deferred expected, got %s' % repr(async_func())
        assert msg in excinfo.value
    elif asyncenv == 'blocking':
        with pytest.raises(AssertionError) as excinfo:
            async.call(lambda: None, blocking_func)
        msg = 'expected immediately returned result, not DeferredMimic'
        assert msg in excinfo.value


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_async_inline_callbacks_sync(mock):
    # Test inlineCallbacks like behaviour

    after_return = []
    args = ('foo', 'bar')
    kwargs = {'x': 1, 'y': 2}

    @mock
    @async.inline_callbacks
    def foo(*args, **kwargs):
        d = async.DeferredMimic()
        d.callback('result')
        result = yield d
        async.return_value(result)
        after_return.append('won\'t be executed')

    assert foo(*args, **kwargs) == 'result'
    assert foo.calls == [{'args': args, 'kwargs': kwargs}]
    assert not after_return


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_async_inline_callbacks_sync_return_points():

    @async.inline_callbacks
    def return_first():
        async.return_value('first')
        yield None

    @async.inline_callbacks
    def without_return():
        yield 42

    assert return_first() == 'first'
    assert without_return() is None


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_async_inline_callbacks_sync_exception():
    rows = []

    @async.inline_callbacks
    def foo():
        rows.append('called')
        raise ValueError('error description')
        rows.append('never')
        d = async.DeferredMimic()
        d.callback('result')
        result = yield d
        async.return_value(result)

    with pytest.raises(ValueError) as excinfo:
        foo()
    assert 'error description' in excinfo.value
    assert rows == ['called']


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('async')
def test_async_inline_callbacks_async():
    calls = []
    deferreds = []
    errors = []

    def errback(fail):
        errors.append(fail)

    @async.inline_callbacks
    def foo(*args, **kwargs):
        calls.append((args, kwargs))
        d = defer.Deferred()
        deferreds.append(d)
        result = yield d
        async.return_value(result)

    # It not just works like inlineCallbacks, it is inlineCallbacks
    r = foo('x', y=1)
    assert isinstance(r, defer.Deferred)
    assert calls.pop(0) == (('x',), {'y': 1})
    assert len(deferreds) == 1

    d = deferreds.pop(0)
    d.callback('result')
    assert d.called and r.called
    assert r.result == 'result'

    assert not calls
    assert not deferreds

    # Exceptions will be handled in the same manner
    r = foo('bar', baz=1)
    assert isinstance(r, defer.Deferred)
    assert calls.pop(0) == (('bar',), {'baz': 1})
    assert len(deferreds) == 1

    r.addErrback(errback)
    d = deferreds.pop(0)
    d.errback(ValueError('an error'))
    assert d.called and r.called
    assert r.result is None  # due to handled exception
    fail = errors.pop(0)
    assert isinstance(fail, failure.Failure)
    assert fail.type == ValueError
    assert fail.value.message == 'an error'

    assert not calls
    assert not deferreds
    assert not errors


@pytest.mark.filldb(_fill=False)
def test_is_async_env(asyncenv):
    result = True if asyncenv == 'async' else False
    assert async.is_async_env() == result


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_log_errors():
    records = []

    class TestLogger(object):
        def error(self, *args, **kwargs):
            records.append((args, kwargs))

    logger = async.logger
    async.logger = TestLogger()

    @async.log_errors
    @async.inline_callbacks
    def uut(raise_error, log_extra=None):
        yield
        if raise_error:
            raise RuntimeError('hello')

    yield uut(False)
    with pytest.raises(RuntimeError):
        yield uut(True)

    yield uut(False, log_extra=1)
    with pytest.raises(RuntimeError):
        yield uut(True, log_extra=1)

    assert records == [
        (('Cannot execute function %s: Error %s', 'uut', 'hello'),
         {'exc_info': True, 'extra': None}),
        (('Cannot execute function %s: Error %s', 'uut', 'hello'),
         {'exc_info': True, 'extra': 1}),
    ]
    async.logger = logger
