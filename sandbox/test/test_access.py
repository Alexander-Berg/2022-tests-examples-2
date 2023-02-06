import pytest

from sandbox.projects.yabs.qa.performance.stats.access import update_dict


@pytest.mark.parametrize(['dict', 'update', 'expected_dict'], [
    (
        {},
        {},
        {}
    ),
    (
        {
            'key': 'value',
        },
        {},
        {
            'key': 'value',
        }
    ),
    (
        {},
        {
            'key': 'value',
        },
        {
            'key': 'value',
        }
    ),
    (
        {
            'int': 1,
            'list': [
                0.1,
                0.2,
                0.3
            ],
            'dict': {
                'list': [
                    0.1,
                    0.2,
                    0.3
                ],
                'dict': {
                    1: 2,
                    2: 4,
                }
            }
        },
        {
            'int': 3,
            'list': [
                0.12,
                0.22,
                0.13
            ],
            'dict': {
                'list': [
                    0.1111,
                    0.21,
                    0.3
                ],
                'dict': {
                    3: 2,
                    2: 6,
                }
            }
        },
        {
            'int': 4,
            'list': [
                0.1,
                0.2,
                0.3,
                0.12,
                0.22,
                0.13
            ],
            'dict': {
                'list': [
                    0.1,
                    0.2,
                    0.3,
                    0.1111,
                    0.21,
                    0.3
                ],
                'dict': {
                    1: 2,
                    2: 10,
                    3: 2
                }
            }
        }
    )
])
def test_update_dict(dict, update, expected_dict):
    update_dict(dict, update)
    assert dict == expected_dict
