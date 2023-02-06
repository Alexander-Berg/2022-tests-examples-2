import pytest


class BaseDatabase:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __call__(self, **kwargs):
        _dict = self.__dict__.copy()
        _dict.update(kwargs)
        return pytest.mark.pgsql(
            'eats_integration_offline_orders', files=list(_dict.values()),
        )


def partial_matcher(expected, actual):

    assert isinstance(
        expected, type(actual),
    ), f'{type(expected)} != {type(actual)}'

    if isinstance(expected, dict):
        for key, val in expected.items():
            assert key in actual, f'{key} is not in actual'
            try:
                partial_matcher(val, actual[key])
            except AssertionError as exc:
                exc.args = (f'{key}',) + exc.args
                raise

    elif isinstance(expected, list):
        assert len(expected) == len(
            actual,
        ), f'len expected ({len(expected)}) != len actual ({len(actual)})'
        for i, val in enumerate(expected):
            partial_matcher(val, actual[i])
    else:
        assert expected == actual, f'{expected} != {actual}'
