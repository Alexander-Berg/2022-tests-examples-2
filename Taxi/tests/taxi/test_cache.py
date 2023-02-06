from taxi import cache


def test_in_mem_ttl_cache(patch):
    # Test default behaviour
    cache1: cache.InMemSizedTTLCache[int, str] = (
        cache.InMemSizedTTLCache('cache1', default_ttl=10000.0)
    )  # lags happen
    assert cache1.get(0) is None
    cache1.set(0, 'HI0')
    assert cache1.get(0) == 'HI0'
    assert cache1.get(1) is None
    assert cache1.get_or_set(1, lambda i: 'HI' + str(i)) == 'HI1'
    assert cache1.pop(1) == 'HI1'
    assert cache1.pop(1) is None
    del cache1
    # Test instant timeout
    # The clock inside is monotonic, so there is no point in moving time
    cache2: cache.InMemSizedTTLCache[int, str] = (
        cache.InMemSizedTTLCache('cache2', default_ttl=0.0)
    )
    assert cache2.get(0) is None
    cache2.set(0, 'HI0')
    assert cache2.get(0) is None
    assert cache2.get(1) is None
    assert cache2.get_or_set(1, lambda i: 'HI' + str(i)) == 'HI1'
    assert cache2.pop(1) is None
    del cache2
    # Test not enough space
    cache3: cache.InMemSizedTTLCache[int, str] = (
        cache.InMemSizedTTLCache('cache3', default_ttl=10000.0, max_size=2)
    )
    cache3.set(0, 'HI0')
    assert cache3.get(0) == 'HI0'
    cache3.set(1, 'HI1')
    assert cache3.get(0) == 'HI0'
    assert cache3.get(1) == 'HI1'
    cache3.set(2, 'HI2')
    assert cache3.get(0) is None
    assert cache3.get(1) == 'HI1'
    assert cache3.get(2) == 'HI2'

    # Test reset after expire
    @patch('time.monotonic')  # noqa: F811
    def _time():
        return 1.0

    cache4: cache.InMemSizedTTLCache[int, str] = (
        cache.InMemSizedTTLCache('cache4')
    )
    cache4.set_ttl(0, 'HI0', ttl=2)
    cache4.set_ttl(0, 'HI1', ttl=2)
    assert cache4.get(0) == 'HI0'

    @patch('time.monotonic')  # noqa: F811
    def _time():
        return 4.0

    cache4.set_ttl(0, 'HI1', ttl=2)
    assert cache4.get(0) == 'HI1'
