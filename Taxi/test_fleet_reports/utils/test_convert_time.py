import pytest

from fleet_reports.utils.convert_time import convert_time

KEYSET = 'opteum_page_report_parks'


@pytest.mark.translations(
    opteum_page_report_parks={
        'hours': {'ru': 'ч.', 'en': 'h.'},
        'minutes': {'ru': 'мин.', 'en': 'm.'},
    },
)
@pytest.mark.parametrize(
    'seconds, locale, expected_result',
    [
        (0, 'ru', '–'),
        (0, 'en', '–'),
        (0.3, 'ru', '–'),
        (0.3, 'en', '–'),
        (0.5, 'ru', '–'),
        (0.5, 'en', '–'),
        (0.9, 'ru', '–'),
        (0.9, 'en', '–'),
        (1, 'ru', '1 мин.'),
        (1, 'en', '1 m.'),
        (50, 'ru', '1 мин.'),
        (50, 'en', '1 m.'),
        (59, 'ru', '1 мин.'),
        (59, 'en', '1 m.'),
        (60, 'ru', '1 мин.'),
        (60, 'en', '1 m.'),
        (61, 'ru', '2 мин.'),
        (61, 'en', '2 m.'),
        (110, 'ru', '2 мин.'),
        (110, 'en', '2 m.'),
        (3599, 'ru', '1 ч.'),
        (3599, 'en', '1 h.'),
        (3600, 'ru', '1 ч.'),
        (3600, 'en', '1 h.'),
        (3601, 'ru', '1 ч. 1 мин.'),
        (3601, 'en', '1 h. 1 m.'),
        (4000, 'ru', '1 ч. 7 мин.'),
        (4000, 'en', '1 h. 7 m.'),
        (140000, 'ru', '38 ч. 54 мин.'),
        (140000, 'en', '38 h. 54 m.'),
    ],
)
def test_convert_time(seconds, locale, expected_result):
    result = convert_time(seconds=seconds, locale=locale, keyset=KEYSET)
    assert result == expected_result
