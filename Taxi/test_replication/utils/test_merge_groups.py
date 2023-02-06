import pytest

from replication.utils import merge_groups


@pytest.mark.parametrize(
    'list_of_groups, expected_result',
    [
        (
            [
                [
                    frozenset({'a', 'b'}),
                    frozenset({'c', 'd'}),
                    frozenset({'e'}),
                ],
                [frozenset({'a', 'b', 'c', 'd'}), frozenset({'e'})],
                [frozenset({'a', 'b', 'c', 'd', 'e'})],
            ],
            frozenset(
                {
                    frozenset({'a', 'b'}),
                    frozenset({'c', 'd'}),
                    frozenset({'e'}),
                },
            ),
        ),
        (
            [
                [frozenset({'a', 'b'}), frozenset({'c', 'd', 'e'})],
                [frozenset({'a', 'b', 'c', 'd'}), frozenset({'e'})],
                [frozenset({'a', 'b', 'c', 'd', 'e'})],
            ],
            frozenset(
                {
                    frozenset({'a', 'b'}),
                    frozenset({'c', 'd'}),
                    frozenset({'e'}),
                },
            ),
        ),
        (
            [
                [frozenset({'a', 'b'}), frozenset({'c', 'd', 'e'})],
                [frozenset({'a', 'c', 'd'}), frozenset({'e'})],
            ],
            frozenset(
                {
                    frozenset({'a'}),
                    frozenset({'b'}),
                    frozenset({'c', 'd'}),
                    frozenset({'e'}),
                },
            ),
        ),
        (
            [
                [frozenset({'a', 'b'}), frozenset({'d'})],
                [frozenset({'a', 'c', 'd'}), frozenset({'e'})],
            ],
            frozenset(
                {  # bad case because of skips
                    frozenset({'c'}),
                    frozenset({'e'}),
                    frozenset({'a'}),
                    frozenset({'b'}),
                    frozenset({'d'}),
                },
            ),
        ),
        (
            [
                [frozenset({'a'}), frozenset({'b'}), frozenset({'d'})],
                [frozenset({'a', 'c', 'd'}), frozenset({'e'})],
            ],
            frozenset(
                {
                    frozenset({'a'}),
                    frozenset({'b'}),
                    frozenset({'c'}),
                    frozenset({'d'}),
                    frozenset({'e'}),
                },
            ),
        ),
        (
            [
                [frozenset({'a', 'b', 'c', 'd'}), frozenset({'e', 'f', 'g'})],
                [frozenset({'a', 'c', 'd'}), frozenset({'b', 'e', 'f', 'g'})],
                [frozenset({'a', 'e'}), frozenset({'b', 'c', 'd', 'f', 'g'})],
            ],
            frozenset(
                {
                    frozenset({'a'}),
                    frozenset({'b'}),
                    frozenset({'c', 'd'}),
                    frozenset({'e'}),
                    frozenset({'f', 'g'}),
                },
            ),
        ),
    ],
)
@pytest.mark.nofilldb()
def test_merge_groups(list_of_groups, expected_result):
    assert merge_groups.merge_groups(list_of_groups) == expected_result
