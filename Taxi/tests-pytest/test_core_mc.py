import cPickle
import hashlib
import uuid
import zlib

from twisted.internet import defer
import pytest

from taxi.core import async
from taxi.core import mc
from taxi.core import threads


@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_memcached_commands():
    key1 = uuid.uuid4().hex
    key2 = uuid.uuid4().hex
    key3 = uuid.uuid4().hex

    # set
    assert (yield mc.set(key1, 'value', expire_time=5))
    assert (yield mc.set(key2, 42, expire_time=5, pickle=True))
    assert (yield mc.set(key3, 42, expire_time=5, pickle=True, compress=True))

    # get
    pickled = yield mc._pickle_and_compress(42, True, False)
    pickled_and_compressed = yield mc._pickle_and_compress(42, True, True)
    assert (yield mc.get(key1)) == 'value'
    assert (yield mc.get(key2)) == pickled
    assert (yield mc.get(key3)) == pickled_and_compressed
    assert (yield mc.get(key2, unpickle=True)) == 42
    assert (yield mc.get(key3, unpickle=True, decompress=True)) == 42

    # get_multi
    response = yield mc.get_multi(
        key1, (key2, mc.PICKLED), (key3, mc.PICKLED, mc.COMPRESSED)
    )
    assert response == {key1: 'value', key2: 42, key3: 42}

    # delete
    for key in [key1, key2]:
        assert (yield mc.delete(key)) is None
        assert (yield mc.get(key)) is None

    # add
    assert (yield mc.add(key1, 'value1', expire_time=5))
    assert (yield mc.add(key2, 'value2', expire_time=5, pickle=True))
    assert not (yield mc.add(key3, 'value3', expire_time=5, compress=True))
    response = yield mc.get_multi(
        key1, (key2, mc.PICKLED), (key3, mc.PICKLED, mc.COMPRESSED)
    )
    assert response == {key1: 'value1', key2: 'value2', key3: 42}


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_soft_caching():
    key = uuid.uuid4().hex
    lock_key = mc.SOFT_LOCK_KEY_PATTERN % key
    data_key = mc.SOFT_DATA_KEY_PATTERN % key

    # Soft caching system is implemented with two keys. First key is a
    # marker which existence means cached data is fresh. And by second
    # one data is stored.

    # First of all, you should check if data exists and if data is fresh
    (fresh, data) = yield mc.soft_get(key)

    # Of course, we don't have any data by a key, so we must not set any
    # lock, we just need to recalculate data and set it (with lock)
    assert data is None
    assert (yield mc.soft_try_lock(key, fresh_time=5))
    assert (yield mc.soft_set(key, 'value1', fresh_time=5))

    # Data is set, and lock is set too
    assert bool((yield mc.get(lock_key)))
    assert (yield mc.get(data_key)) == 'value1'

    # Nobody should rewrite data while data is fresh
    (fresh, data) = yield mc.soft_get(key)
    assert fresh
    assert data == 'value1'

    # But when data isn't fresh some process must recalculate result
    # while others must go with old data
    yield mc.delete(lock_key)
    (fresh, data) = yield mc.soft_get(key)
    assert not fresh
    assert data == 'value1'

    # So, each process which takes unfresh data must try to set lock,
    # and if lock is successfully set data must be recalculated
    assert (yield mc.soft_try_lock(key, fresh_time=5))  # success
    assert not (yield mc.soft_try_lock(key, fresh_time=5))  # fail

    # If something during recalculation happened lock must be unset
    yield mc.soft_unset_lock(key)

    # Another process will set lock and will recalculate data
    assert (yield mc.soft_try_lock(key, fresh_time=5))
    assert (yield mc.soft_set(key, 'value2', fresh_time=5))
    assert (yield mc.soft_get(key)) == (True, 'value2')


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_soft_caching_pickling_and_compression():
    key = uuid.uuid4().hex
    data_key = mc.SOFT_DATA_KEY_PATTERN % key

    # Soft cache can be used with pickling and compression
    assert (yield mc.soft_try_lock(key, fresh_time=5))
    yield mc.soft_set(key, 'value', fresh_time=5, pickle=True, compress=True)
    (fresh, data) = yield mc.soft_get(key, unpickle=True, decompress=True)
    assert (fresh, data) == (True, 'value')

    # Stored value is pickled and compressed
    assert (yield mc.get(data_key, unpickle=True, decompress=True)) == 'value'


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('key,args,kwargs', [
    ('key', ('x', 'y'), {'z': 1}),
    ('anotherkey', (), {}),
])
def test_memoize_key(key, args, kwargs):
    expected = '%s%s' % (key, hashlib.sha1(repr((args, kwargs))).hexdigest())
    assert mc._memoize_key(
        key, mc._get_default_args_repr(args, kwargs)
    ) == expected


@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_memoizing(sleep):
    data_key = lambda key, *args, **kwargs: (
        mc.SOFT_DATA_KEY_PATTERN % mc._memoize_key(
            key, mc._get_default_args_repr(args, kwargs)
        )
    )

    key1 = uuid.uuid4().hex
    key3 = uuid.uuid4().hex

    calls = list()

    @mc.memoize(key1, fresh_time=5)
    def foo(str1, str2):
        calls.append(('foo', str1, str2))
        return str1 + str2

    @mc.memoize(fresh_time=5)
    @async.inline_callbacks
    def foo_deferred(str1, str2):
        calls.append(('foo_deferred', str1, str2))
        target = lambda x, y: x + y
        response = yield threads.defer_to_thread(target, str1, str2)
        async.return_value(response)

    @mc.memoize(key3, fresh_time=5, pickle=True, compress=True)
    def product(x, y):
        calls.append(('product', x, y))
        return x * y

    # First time function is called and data is calculated
    assert (yield foo('s1', 's2')) == 's1s2'
    assert (yield foo_deferred('s1', 's2')) == 's1s2'
    assert (yield product(5, 10)) == 50
    yield sleep(0)
    assert calls.pop(0) == ('foo', 's1', 's2')
    assert calls.pop(0) == ('foo_deferred', 's1', 's2')
    assert calls.pop(0) == ('product', 5, 10)
    assert not calls

    # Second time data from cache will be returned
    assert (yield foo('s1', 's2')) == 's1s2'
    assert (yield foo_deferred('s1', 's2')) == 's1s2'
    assert (yield product(5, 10)) == 50
    yield sleep(0)
    assert not calls

    # Note, `memoize` is based on `soft_*` functions, so if data is not
    # fresh anymore it will be recalculated
    hash_key1 = mc._memoize_key(
        key1, mc._get_default_args_repr(('s1', 's2'), {})
    )
    yield mc.soft_unset_lock(hash_key1)
    assert (yield foo('s1', 's2')) == 's1s2'
    assert (yield foo_deferred('s1', 's2')) == 's1s2'
    assert (yield product(5, 10)) == 50
    yield sleep(0)
    assert calls.pop(0) == ('foo', 's1', 's2')
    assert not calls

    # Also note, `product` cache is pickled and compressed
    data = yield mc.get(data_key(key3, 5, 10), unpickle=True, decompress=True)
    assert data == 50


@pytest.mark.filldb(_fill=False)
def test_key_validation():
    # Key must be a string
    with pytest.raises(mc.InvalidKeyError) as excinfo:
        mc._validate_key(42)
    assert 'key must be a str, got int' in excinfo.value

    # Key length is restored with `mc.MAX_KEY_LENGTH` characters
    with pytest.raises(mc.InvalidKeyError) as excinfo:
        mc._validate_key('k' * (mc.MAX_KEY_LENGTH + 1))
    msg = 'key length is %d, must be <= %d' % (
        mc.MAX_KEY_LENGTH + 1,
        mc.MAX_KEY_LENGTH
    )
    assert msg in excinfo.value

    # If key is valid `_validate_key` returns nothing
    assert mc._validate_key('k' * mc.MAX_KEY_LENGTH) is None


@pytest.mark.filldb(_fill=False)
def test_value_validation():
    # If value is valid `_validate_value` returns nothing
    assert mc._validate_value('valid value', False) is None

    # Value must be a string
    with pytest.raises(mc.InvalidDataError) as excinfo:
        mc._validate_value(42, False)
    msg = 'value must be str, got int; may be you forgot pickle option?'
    assert msg in excinfo.value

    # Until value will be pickled
    assert mc._validate_value(42, True) is None


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_pickling_and_compression(mock):
    # Both pickling and compression are performed in thread

    @mock('taxi.core.threads.defer_to_thread')
    def d2t(target, *args, **kwargs):
        return target(*args, **kwargs)

    # By default, value won't be pickled or comressed
    value = yield mc._pickle_and_compress('value', False, False)
    assert value == 'value'
    assert not d2t.calls

    # Value is pickled in thread with `cPickle.HIGHEST_PROTOCOL`
    value = yield mc._pickle_and_compress(42, True, False)
    assert value == cPickle.dumps(42, protocol=cPickle.HIGHEST_PROTOCOL)
    assert not d2t.calls

    # Compression is made in thread via zlib with `mc.COMPRESS_LEVEL`
    # level
    value = yield mc._pickle_and_compress('value', False, True)
    assert value == zlib.compress('value', mc.COMPRESS_LEVEL)
    assert d2t.calls == [{
        'target': mc._pickle_and_compress_sync,
        'args': ('value', False, True),
        'kwargs': {}
    }]

    # String also can be explicitly pickled
    value = yield mc._pickle_and_compress('value', True, True)
    pickled = cPickle.dumps('value', protocol=cPickle.HIGHEST_PROTOCOL)
    assert value == zlib.compress(pickled, mc.COMPRESS_LEVEL)
    assert d2t.calls == [{
        'target': mc._pickle_and_compress_sync,
        'args': ('value', True, True),
        'kwargs': {}
    }]


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_unpickling_and_decompression(mock):
    # Both unpickling and decompression are performed in thread

    @mock('taxi.core.threads.defer_to_thread')
    def d2t(target, *args, **kwargs):
        return target(*args, **kwargs)

    pickled = cPickle.dumps(42, protocol=cPickle.HIGHEST_PROTOCOL)
    compressed = zlib.compress(pickled, mc.COMPRESS_LEVEL)

    # By default, value won't be unpickled or uncomressed
    response = yield mc._unpickle_and_decompress(pickled, False, False)
    assert response == pickled

    # Unpickling is done explicitly
    response = yield mc._unpickle_and_decompress(pickled, True, False)
    assert response == 42
    assert not d2t.calls

    # The same with decompression
    response = yield mc._unpickle_and_decompress(compressed, False, True)
    assert response == pickled
    assert d2t.calls == [dict(
        target=mc._unpickle_and_decompress_sync, args=(compressed, False, True),
        kwargs={}),
    ]

    # If a value has been pickled and compressed you must explicitly
    # unpickle and decompress
    response = yield mc._unpickle_and_decompress(compressed, True, True)
    assert response == 42
    assert d2t.calls == [dict(
        target=mc._unpickle_and_decompress_sync, args=(compressed, True, True),
        kwargs={}),
    ]


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_sync_calls(monkeypatch, stub):
    # Test that all blocking calls are made via lymc
    calls = []

    def func(name, args, kwargs):
        calls.append((name, args, kwargs))
        if name == 'get_multi':
            return {}
        else:
            return 'result'

    client = stub(
        set=lambda *args, **kwargs: func('set', args, kwargs),
        add=lambda *args, **kwargs: func('add', args, kwargs),
        delete=lambda *args, **kwargs: func('delete', args, kwargs),
        get=lambda *args, **kwargs: func('get', args, kwargs),
        get_multi=lambda *args, **kwargs: func('get_multi', args, kwargs),
    )
    monkeypatch.setattr(mc, 'memcache_client', client)

    assert mc._sync_set('key', 'value', 30) == 'result'
    assert mc._sync_add('key', 'value', 30) == 'result'
    assert mc._sync_delete('key') is None
    assert mc._sync_get('key') == 'result'
    assert mc._sync_get_multi(['key1', 'key2']) == {'key1': None, 'key2': None}
    assert calls == [
        ('set', ('key', 'value'), {'time': 30}),
        ('add', ('key', 'value'), {'time': 30}),
        ('delete', ('key',), {}),
        ('get', ('key',), {}),
        ('get_multi', (['key1', 'key2'],), {}),
    ]


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_async_calls(monkeypatch, stub):
    # Test that all async calls are made via txyam
    calls = []

    def func(name, args, kwargs):
        calls.append((name, args, kwargs))
        if name == 'get':
            return defer.succeed((0, 'result'))
        elif name == 'getMultiple':
            return defer.succeed({'key1': (0, 1), 'key2': (0, 2)})
        else:
            return defer.succeed(True)

    client = mc.YamClient([])
    client.set = lambda *args, **kwargs: func('set', args, kwargs)
    client.add = lambda *args, **kwargs: func('add', args, kwargs)
    client.delete = lambda *args, **kwargs: func('delete', args, kwargs)
    client.get = lambda *args, **kwargs: func('get', args, kwargs)
    client.getMultiple = lambda *args, **kwargs: func(
        'getMultiple', args, kwargs
    )
    monkeypatch.setattr(mc, 'txyam_client', client)

    assert (yield mc._async_set('key', 'value', 30)) is True
    assert (yield mc._async_add('key', 'value', 30)) is True
    assert (yield mc._async_delete('key')) is None
    assert (yield mc._async_get('key')) == 'result'
    response = yield mc._async_get_multi(['key1', 'key2'])
    assert response == {'key1': 1, 'key2': 2}
    assert calls == [
        ('set', ('key', 'value'), {'expireTime': 30}),
        ('add', ('key', 'value'), {'expireTime': 30}),
        ('delete', ('key',), {}),
        ('get', ('key',), {}),
        ('getMultiple', (['key1', 'key2'],), {}),
    ]
