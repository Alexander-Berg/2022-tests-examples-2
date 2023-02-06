import pytest

from fleet_common.utils import helpers


@pytest.mark.parametrize(
    'chunk_size, chunk_count, chunk_real_size',
    [(1, 100, 1), (10, 10, 10), (100, 1, 100), (1000, 1, 100)],
)
def test_chunks(chunk_size, chunk_count, chunk_real_size):
    test_list = list(range(0, 100))

    iteration_count = 0
    for chunk in helpers.chunks(test_list, chunk_size):
        iteration_count += 1
        assert len(chunk) == chunk_real_size
    assert iteration_count == chunk_count


def test_parse_locale():
    assert helpers.parse_locale('ru,en') == 'ru'
    assert helpers.parse_locale('en,en') == 'en'
    assert helpers.parse_locale('ru,en;q=0.9,la;q=0.8') == 'ru'
    assert helpers.parse_locale('ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3') == 'ru'
    assert (
        helpers.parse_locale(
            'ru-RU, ru;q=0.9, en-US;q=0.8, en;q=0.7, fr;q=0.6',
        )
        == 'ru'
    )
    assert helpers.parse_locale('') == 'en'
    assert helpers.parse_locale('q') == 'en'
