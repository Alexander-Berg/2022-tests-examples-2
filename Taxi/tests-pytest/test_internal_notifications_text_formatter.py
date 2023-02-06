# coding: utf-8
from __future__ import unicode_literals

import pytest

from taxi.internal.notifications.order import text_formatter


# Russian car numbers
RUS_REGEXPS = [
    u'^(\\D)(\\d{3})(\\D{2})(\\d{2,3})$',
    u'^(\\D{2})(\\d{3})(\\d{2,3})$'
]


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'car_number, regexps, delimeter, to_lower_case, expected',
    [
        # TAXIBACKEND-14544
        (u'С606ВЕ199', [], ' ', True, u'с606ве199'),

        # TAXIBACKEND-9136
        # rus
        (u'А108СЕ152', RUS_REGEXPS, ' ', False, u'А 108 СЕ 152'),
        (u'АВ78977', RUS_REGEXPS, ' ', False, u'АВ 789 77'),
        # unknown
        (u'ABCDEF123', RUS_REGEXPS, ' ', False, u'ABCDEF123'),

        # Test delimeter='_' + regexp + to_lower_case
        (u'С606ВЕ199', RUS_REGEXPS, '_', True, u'с_606_ве_199'),
    ]
)
def test_format_car_number(
    car_number, regexps, delimeter, to_lower_case, expected
):
    result = text_formatter.format_car_number_with_regexps(
        car_number, regexps=regexps, delimiter=delimeter,
        to_lower_case=to_lower_case
    )
    assert result == expected
