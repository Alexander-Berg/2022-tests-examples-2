from taxi.core import scheduler


def test_call_later(monkeypatch, stub, mock, asyncenv):
    @mock
    def foo(*args, **kwargs):
        return 42

    @mock
    def callLater(*args, **kwargs):
        return 'DelayedCall'

    # In blocking environment function passed to `call_later` is
    # executed immediately and nothing is returned.
    if asyncenv == 'blocking':
        result = scheduler.call_later(10, foo, 'x', y=1)
        assert result is None
        assert foo.calls == [dict(args=('x',), kwargs={'y': 1})]
        assert not callLater.calls

    # In asynchronous environment `twisted.internet.reactor.callLater`
    # is called and its result is returned.
    elif asyncenv == 'async':
        monkeypatch.setattr(scheduler, 'callLater', callLater)
        result = scheduler.call_later(10, foo, 'x', y=1)
        assert result == 'DelayedCall'
        assert callLater.calls == [dict(args=(10, foo, 'x'), kwargs={'y': 1})]
        assert not foo.calls
