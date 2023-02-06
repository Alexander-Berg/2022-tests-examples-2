import six
from six.moves import cPickle

import pytest


class Foo(object):
    @classmethod
    def class_method(cls):
        pass

    def instance_method(self):
        pass


some_lambda = lambda x: x * x


@pytest.mark.skipif(six.PY3, reason="py2 test only")
@pytest.mark.parametrize("obj", [Foo.class_method, Foo().instance_method, some_lambda])
def test__custom_pickler(obj):
    # Sandbox legacy server relies on custom picklers defined in `kernel.util.pickle`, e.g. for class methods.
    # Check if they are still in place.

    # noinspection PyUnresolvedReferences
    import kernel.util.pickle  # noqa

    # noinspection PyBroadException
    try:
        cPickle.dumps(obj, -1)
    except Exception:
        pytest.fail(
            "Looks like `kernel.util.pickle` is now missing custom pickler for `{}`. Sandbox depends on it."
            .format(type(obj).__name__)
        )
