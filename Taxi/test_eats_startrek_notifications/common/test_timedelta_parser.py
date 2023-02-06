import datetime

from eats_startrek_notifications.common import timedelta_parser


def test_parse():
    assert timedelta_parser.parse('1h') == datetime.timedelta(hours=1)
    assert timedelta_parser.parse('2d') == datetime.timedelta(days=2)
    assert timedelta_parser.parse('3m') == datetime.timedelta(minutes=3)

    assert timedelta_parser.parse('4d 5h') == datetime.timedelta(
        days=4, hours=5,
    )
    assert timedelta_parser.parse('4d5h') == datetime.timedelta(
        days=4, hours=5,
    )

    assert timedelta_parser.parse('6d 7h 8m') == datetime.timedelta(
        days=6, hours=7, minutes=8,
    )
    assert timedelta_parser.parse('6d7h  8m') == datetime.timedelta(
        days=6, hours=7, minutes=8,
    )
    assert timedelta_parser.parse('6d  7h8m') == datetime.timedelta(
        days=6, hours=7, minutes=8,
    )
