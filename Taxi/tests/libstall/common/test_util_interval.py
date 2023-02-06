from datetime import datetime, timezone

from libstall.util import split_interval


def test_one_day(tap):
    with tap.plan(1, 'Один день не сплитится'):

        begin = datetime(2020, 1, 1, 13, 45, 0, tzinfo=timezone.utc)
        end   = datetime(2020, 1, 1, 22, 30, 0, tzinfo=timezone.utc)

        tap.eq(
            split_interval(begin, end),
            [[begin, end]],
            'Нечего сплитить'
        )


def test_splited(tap):
    with tap.plan(1, 'Разделили'):

        begin = datetime(2020, 1, 1, 13, 45, 0, tzinfo=timezone.utc)
        end   = datetime(2020, 1, 3, 22, 30, 0, tzinfo=timezone.utc)

        tap.eq(
            split_interval(begin, end),
            [
                [
                    begin,
                    datetime(2020, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
                ],
                [
                    datetime(2020, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
                    datetime(2020, 1, 3, 0, 0, 0, tzinfo=timezone.utc),
                ],
                [
                    datetime(2020, 1, 3, 0, 0, 0, tzinfo=timezone.utc),
                    end,
                ]
            ],
            'Разсплитили на 3 части'
        )


def test_begin_0(tap):
    with tap.plan(1, 'С начала дня'):

        begin = datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end   = datetime(2020, 1, 2, 22, 30, 0, tzinfo=timezone.utc)

        tap.eq(
            split_interval(begin, end),
            [
                [
                    begin,
                    datetime(2020, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
                ],
                [
                    datetime(2020, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
                    end,
                ]
            ],
            'Разсплитили на 2 части'
        )


def test_end_0(tap):
    with tap.plan(1, 'До конца дня'):

        begin = datetime(2020, 1, 1, 13, 45, 0, tzinfo=timezone.utc)
        end   = datetime(2020, 1, 3, 0, 0, 0, tzinfo=timezone.utc)

        tap.eq(
            split_interval(begin, end),
            [
                [
                    begin,
                    datetime(2020, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
                ],
                [
                    datetime(2020, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
                    end,
                ]
            ],
            'Разсплитили на 2 части'
        )


def test_alldays(tap):
    with tap.plan(1, 'Все дни'):

        begin = datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end   = datetime(2020, 1, 3, 0, 0, 0, tzinfo=timezone.utc)

        tap.eq(
            split_interval(begin, end),
            [
                [
                    begin,
                    datetime(2020, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
                ],
                [
                    datetime(2020, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
                    end,
                ]
            ],
            'Разсплитили на 2 части'
        )


def test_allday(tap):
    with tap.plan(1, 'Весь день'):

        begin = datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end   = datetime(2020, 1, 2, 0, 0, 0, tzinfo=timezone.utc)

        tap.eq(
            split_interval(begin, end),
            [
                [
                    begin,
                    end,
                ]
            ],
            'Не сплитили'
        )
