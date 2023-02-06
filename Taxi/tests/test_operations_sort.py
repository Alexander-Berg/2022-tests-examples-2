from typing import List

import pytest

from swaggen import parsing_utils
from swaggen import utils


def sorted_urls(operations: List[dict]) -> List[str]:
    return [
        operation['extra']['urls'].without_slash
        for operation in utils.sort_operations_by_url(operations)
    ]


def create_operation_from_url(url: str) -> dict:
    return {'extra': {'urls': parsing_utils.OperationUrls.from_string(url)}}


@pytest.mark.parametrize(
    'urls, expected_sort',
    (
        (['/ping', '/{prefix}'], ['/ping', '/{prefix}']),
        (['/{prefix}', '/ping/'], ['/ping', '/{prefix}']),
        (['/{prefix}/', '/ping/'], ['/ping', '/{prefix}']),
        (['/{prefix}/', '/ping'], ['/ping', '/{prefix}']),
        (['/a', '/b', '/c'], ['/c', '/b', '/a']),
        (['/x', '/aa/b', '/b/a', '/c/xx'], ['/x', '/c/xx', '/b/a', '/aa/b']),
        (
            ['/zzzzzzzz', '/{param}', '/pref/{zz}', '/pref/aa'],
            ['/zzzzzzzz', '/{param}', '/pref/aa', '/pref/{zz}'],
        ),
        (
            ['/pref/{zz}', '/{param}', '/zzzzzzzz', '/pref/aa'],
            ['/zzzzzzzz', '/{param}', '/pref/aa', '/pref/{zz}'],
        ),
        (
            ['/{aa}/{bb}', '/aa/bb', '/zz', '/{prefix}'],
            ['/zz', '/{prefix}', '/aa/bb', '/{aa}/{bb}'],
        ),
    ),
)
def test_sort(urls, expected_sort):
    operations = [create_operation_from_url(url) for url in urls]
    assert sorted_urls(operations) == expected_sort
