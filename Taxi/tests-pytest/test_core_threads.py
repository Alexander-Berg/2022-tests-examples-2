from twisted.internet import defer

from taxi.core import async
from taxi.core import threads


def test_api(monkeypatch, stub, asyncenv):
    calls = []

    def deferToThread(target, *args, **kwargs):
        d = defer.Deferred()
        calls.append((d, target, args, kwargs))
        return d

    monkeypatch.setattr(
        threads, 'twisted_threads', stub(deferToThread=deferToThread)
    )

    target = lambda x, y=3: x + y
    args = (20,)
    kwargs = {'y': 22}
    result = 42

    # When reactor is not running target will be executed immediately
    # and no `deferToThread()` calls will be done
    if asyncenv == 'blocking':
        d = threads.defer_to_thread(target, *args, **kwargs)
        assert isinstance(d, async.DeferredMimic)
        assert d.result == result
        assert not calls

    # When reactor is running `twisted.internet.defer.deferToThread`
    # will be called
    elif asyncenv == 'async':
        d = threads.defer_to_thread(target, *args, **kwargs)
        assert isinstance(d, defer.Deferred)
        assert len(calls) == 1
        assert calls.pop(0) == (d, target, args, kwargs)
