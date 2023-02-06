import pytest

from taxi.internal.notifications import order


DATE = '2015-12-08T16:34:00+0300'


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'min_mins, max_mins, pattern, expected_result',
    [
        (None, 5, '{} - {}', '5'),
        (3, 5, '{} - {}', '3 - 5'),
        (3, 5, u'{}\u00a0\u2014 {}', u'3\u00a0\u2014 5'),
    ]
)
def test_format_arrival_interval(min_mins, max_mins, pattern, expected_result):
    result = order.text_formatter.format_arrival_interval(min_mins, max_mins,
                                                          pattern)
    assert result == expected_result
