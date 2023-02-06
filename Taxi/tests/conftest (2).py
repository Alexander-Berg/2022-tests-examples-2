import pytest


@pytest.fixture
def patch(monkeypatch):
    """Monkey patch helper.

    Usage:

        @patch('full.path.to.func')
        def func(*args, **kwargs):
            return (args, kwargs)

        assert foo(1, x=2) == ((1,), {'x': 2})
        assert foo.calls == [{'args': (1,), 'kwargs': {'x': 2}}]

    """

    def dec_generator(full_func_path):
        def dec(func):
            monkeypatch.setattr(full_func_path, func)
            return func

        return dec

    return dec_generator
