import pytest

from taxi_devtools import commitstyle


@pytest.mark.parametrize(
    'line,expected',
    [
        ('feat foo: bar', True),
        ('bug foo: bar', True),
        ('feat  : bar', False),
        ('feat foo: ', False),
        ('Revert "foo bar" (#XXXX)', True),
        ('feat foo: /api/v1 handle', True),
        ('feat /foo: handle', False),
    ],
)
def test_check_title(line, expected):
    assert commitstyle.check_title(line) == expected


@pytest.mark.parametrize(
    'line,expected',
    [
        ('foo', []),
        ('Relates: TAXIBACKEND-123', ['TAXIBACKEND-123']),
        (
            'Relates: TAXIBACKEND-123,TAXIDATA-321',
            ['TAXIBACKEND-123', 'TAXIDATA-321'],
        ),
        (
            'Relates: TAXIBACKEND-123,TAXIDATA-321,TAXI-111',
            ['TAXIBACKEND-123', 'TAXIDATA-321', 'TAXI-111'],
        ),
    ],
)
def test_fetch_tickets(line, expected):
    assert commitstyle.fetch_tickets(line) == expected


@pytest.mark.parametrize(
    'description,expected',
    [
        (
            '* foo\n\nRelates: TAXI-1, TAXI-2\n',
            '* foo\n\nRelates: [TAXI-1](https://st.yandex-team.ru/TAXI-1), '
            '[TAXI-2](https://st.yandex-team.ru/TAXI-2)\n',
        ),
        (
            '* foo\n\nRelates: TAXI-1, FOO\n',
            '* foo\n\nRelates: [TAXI-1](https://st.yandex-team.ru/TAXI-1), '
            'FOO\n',
        ),
    ],
)
def test_markdown_description(description, expected):
    assert commitstyle.markdown_description(description) == expected
