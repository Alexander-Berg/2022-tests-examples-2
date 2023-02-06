import pytest

from swaggen import exceptions
from swaggen import parsing_utils
from swaggen import tracing


def test_default_ignored_keys():
    assert (
        parsing_utils.validate_extensions_keys(
            tracing.Dict(
                {
                    'x-stall': 'aaa',
                    'x-stall-22': [],
                    'x-taxi-cpp-type': 'blabla_impl',
                    'x-taxi-cpp': {'x-something-else': []},
                    'x-taxi-handler-tag': ['logs1', 'logs2'],
                },
                filepath='',
            ),
        )
        is None
    )


def test_raise():
    with pytest.raises(exceptions.SwaggenError) as exc_info:
        parsing_utils.validate_extensions_keys(
            tracing.Dict({'x-taxi-py3': 'aaaa'}, filepath='a.yaml'),
        )
    assert exc_info.value.args == (
        'In file a.yaml at x-taxi-py3: unexpected key',
    )
