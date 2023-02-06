# pylint: disable=redefined-outer-name
import uuid

from aiohttp import test_utils
import pytest

from taxi.billing import util


@pytest.fixture
def mock_uuid(monkeypatch):
    class _DummyUuid:
        hex = 'uuid'

    monkeypatch.setattr(uuid, 'uuid4', _DummyUuid)


def test_log_extra_from(mock_uuid):
    request = test_utils.make_mocked_request('GET', '/')
    request['log_extra'] = {'foo': 'bar'}
    assert util.log_extra_from(request) == {'foo': 'bar'}

    request = test_utils.make_mocked_request('GET', '/')
    assert util.log_extra_from(request) == {'_link': 'uuid', 'extdict': {}}


@pytest.mark.parametrize(
    'sequence, expected',
    [
        ([], []),
        ([[], []], []),
        ([[1], []], [1]),
        ([[], [2]], [2]),
        ([[1], [2]], [1, 2]),
        ([[1, 2], [3]], [1, 2, 3]),
        ([[1, 2], [3], [], [4, 5, 6]], [1, 2, 3, 4, 5, 6]),
        # nested lists
        ([[[1, 2]], [3], [[]], [4, 5, 6]], [[1, 2], 3, [], 4, 5, 6]),
    ],
)
def test_flatten(sequence, expected):
    assert expected == util.flatten(sequence)


@pytest.mark.parametrize(
    'sequence, key, expected',
    [
        ([], lambda _: _, {}),
        ([1, 1, 1], lambda _: _, {1: [1, 1, 1]}),
        ([1, 1, 1, 3], lambda _: _, {1: [1, 1, 1], 3: [3]}),
        (
            ['1', '1', '1', '3', ' 3'],
            int,
            {1: ['1', '1', '1'], 3: ['3', ' 3']},
        ),
        (
            [['1', '1', '1'], ['3', ' 3']],
            len,
            {3: [['1', '1', '1']], 2: [['3', ' 3']]},
        ),
        (
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            lambda _: _ % 2 == 0,
            {True: [2, 4, 6, 8, 10], False: [1, 3, 5, 7, 9]},
        ),
        (
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            lambda _: 1 if _ % 2 == 0 else None,
            {1: [2, 4, 6, 8, 10], None: [1, 3, 5, 7, 9]},
        ),
    ],
)
def test_group_by(sequence, key, expected):
    assert expected == util.group_by(sequence, key)
