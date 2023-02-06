import pytest
import mock

from datetime import datetime

from dmp_suite import datetime_utils as dtu
from dmp_suite.logfeller_utils import LogfellerScale
from dmp_suite.ext_source_proxy.logfeller import LogfelellerLastDttmGetter
from dmp_suite.ext_source_proxy.logfeller import LogfellerReactorArtifact


def _get_scale_func_name():
    import dmp_suite.ext_source_proxy.logfeller
    module = dmp_suite.ext_source_proxy.logfeller.__name__
    func = dmp_suite.ext_source_proxy.logfeller._get_scale.__name__
    return module + '.' + func


def _half_hours_in_day(day_one):
    p = dtu.period(day_one, day_one.replace(hour=23, minute=30))
    return [hh for hh in p.split_in_halfhours()]


def _hours_in_day(day_one):
    p = dtu.period(day_one, day_one.replace(hour=23, minute=0))
    return [h for h in p.split_in_hours()]


def _fivemins_in_day(day_one):
    p = dtu.period(day_one, day_one.replace(hour=23, minute=55))
    return [fm for fm in p.split_in_5mins()]


@pytest.mark.parametrize(
    'days, halfhours, expected', [
        (
            # ничего от реактора не пришло
            [],
            [],
            None,
        ),
        (
            # только перый день по msk
            [datetime(2020, 1, 1)],
            [],
            datetime(2020, 1, 1, 21),
        ),
        (
            # два дня по msk
            [datetime(2020, 1, 1), datetime(2020, 1, 2)],
            [],
             datetime(2020, 1, 2, 21),
        ),
        (
            # два дня с дыркой по msk
            [datetime(2020, 1, 1), datetime(2020, 1, 3)],
            [],
            datetime(2020, 1, 1, 21),
        ),
        (
            # только получас по msk
            [],
            [datetime(2020, 10, 10, 12, 30)],
            datetime(2020, 10, 10, 10),
        ),
        (
            # два последовательных получаса по мск
            [],
            [datetime(2020, 10, 10, 12, 30), datetime(2020, 10, 10, 13)],
            datetime(2020, 10, 10, 10, 30),
        ),
        (
            # два получаса с дыркой между ними
            [],
            [datetime(2020, 10, 10, 12, 30), datetime(2020, 10, 10, 13, 30)],
            datetime(2020, 10, 10, 10),
        ),
        (
            # день с дыркой, получас в конце
            [datetime(2020, 11, 2), datetime(2020, 11, 4)],
            [datetime(2020, 11, 4, 0, 30)],
            datetime(2020, 11, 2, 21),
        ),
        (
            # день с дыркой и с получасом рядом с перым днем
            [datetime(2020, 11, 2), datetime(2020, 11, 4)],
            [datetime(2020, 11, 3, 0, 0)],
            datetime(2020, 11, 2, 21, 30),
        ),
        (
            # день с дыркой и с получасом не рядом с перым днем
            [datetime(2020, 11, 2), datetime(2020, 11, 4)],
            [datetime(2020, 11, 3, 0, 30)],
            datetime(2020, 11, 2, 21),
        ),
        (
            # получасовые с дыркой, но она покрыта дневной
            [datetime(2020, 11, 2)],
            [datetime(2020, 11, 2, 0, 30), datetime(2020, 11, 3, 0, 0)],
            datetime(2020, 11, 2, 21, 30),
        ),
        (
            # регулярный случай № 1
            [datetime(2020, 11, 1), datetime(2020, 11, 2)],
            [
                datetime(2020, 11, 3, 0, 0),
                datetime(2020, 11, 3, 0, 30),
                datetime(2020, 11, 3, 1, 0),
                datetime(2020, 11, 3, 1, 30),
                datetime(2020, 11, 3, 2, 0),
                datetime(2020, 11, 3, 2, 30),
            ],
            datetime(2020, 11, 3, 0, 0),
        ),
        (
            # регулярный случай № 2
            [datetime(2020, 11, 1), datetime(2020, 11, 2)],
            [
                *_half_hours_in_day(datetime(2020, 11, 3)),
                datetime(2020, 11, 4, 0, 0),
                datetime(2020, 11, 4, 0, 30),
                datetime(2020, 11, 4, 1, 0),
                datetime(2020, 11, 4, 1, 30),
                datetime(2020, 11, 4, 2, 0),
            ],
            datetime(2020, 11, 3, 23, 30),
        ),

    ]
)
def test_user_time_only_from_daily_and_hh_scales(days, halfhours, expected):

    def side_effect(*args, **kwargs):
        if kwargs['scale'] is LogfellerScale.DAY:
            return days
        elif kwargs['scale'] is LogfellerScale.HALFHOUR:
            return halfhours

    _get_scale_patch = mock.patch(
        _get_scale_func_name(),
        side_effect=side_effect,
    )

    with _get_scale_patch:
        res = LogfelellerLastDttmGetter(
            'dummy',
            log_tz='msk',
            scale=LogfellerScale.DAY,
            prompt_scale=LogfellerScale.HALFHOUR,
        )()
    assert res == expected


@pytest.mark.parametrize(
    'days, hours, expected', [
        (
            # ничего от реактора не пришло
            [],
            [],
            None,
        ),
        (
            # только перый день по msk
            [datetime(2020, 1, 1)],
            [],
            datetime(2020, 1, 1, 21),
        ),
        (
            # два дня по msk
            [datetime(2020, 1, 1), datetime(2020, 1, 2)],
            [],
             datetime(2020, 1, 2, 21),
        ),
        (
            # два дня с дыркой по msk
            [datetime(2020, 1, 1), datetime(2020, 1, 3)],
            [],
            datetime(2020, 1, 1, 21),
        ),
        (
            # только час по msk
            [],
            [datetime(2020, 10, 10, 12)],
            datetime(2020, 10, 10, 10),
        ),
        (
            # два последовательных часа по мск
            [],
            [datetime(2020, 10, 10, 12), datetime(2020, 10, 10, 13)],
            datetime(2020, 10, 10, 11),
        ),
        (
            # два часа с дыркой между ними
            [],
            [datetime(2020, 10, 10, 12), datetime(2020, 10, 10, 14)],
            datetime(2020, 10, 10, 10),
        ),
        (
            # день с дыркой, час в конце
            [datetime(2020, 11, 2), datetime(2020, 11, 4)],
            [datetime(2020, 11, 4, 0)],
            datetime(2020, 11, 2, 21),
        ),
        (
            # день с дыркой и с часом рядом с перым днем
            [datetime(2020, 11, 2), datetime(2020, 11, 4)],
            [datetime(2020, 11, 3, 0, 0)],
            datetime(2020, 11, 2, 22),
        ),
        (
            # день с дыркой и с часом не рядом с перым днем
            [datetime(2020, 11, 2), datetime(2020, 11, 4)],
            [datetime(2020, 11, 3, 1)],
            datetime(2020, 11, 2, 21),
        ),
        (
            # часовые с дыркой, но она покрыта дневной
            [datetime(2020, 11, 2)],
            [datetime(2020, 11, 2, 0), datetime(2020, 11, 3, 0, 0)],
            datetime(2020, 11, 2, 22),
        ),
        (
            # регулярный случай № 1
            [datetime(2020, 11, 1), datetime(2020, 11, 2)],
            [
                datetime(2020, 11, 3, 0, 0),
                datetime(2020, 11, 3, 1, 0),
                datetime(2020, 11, 3, 2, 0),
            ],
            datetime(2020, 11, 3, 0, 0),
        ),
        (
            # регулярный случай № 2
            [datetime(2020, 11, 1), datetime(2020, 11, 2)],
            [
                *_hours_in_day(datetime(2020, 11, 3)),
                datetime(2020, 11, 4, 0, 0),
                datetime(2020, 11, 4, 1, 0),
            ],
            datetime(2020, 11, 3, 23),
        ),
    ]
)
def test_user_time_only_from_daily_and_hour_scales(days, hours, expected):

    def side_effect(*args, **kwargs):
        if kwargs['scale'] is LogfellerScale.DAY:
            return days
        elif kwargs['scale'] is LogfellerScale.HOUR:
            return hours

    _get_scale_patch = mock.patch(
        _get_scale_func_name(),
        side_effect=side_effect,
    )

    with _get_scale_patch:
        res = LogfelellerLastDttmGetter(
            'dummy',
            log_tz='msk',
            scale=LogfellerScale.DAY,
            prompt_scale=LogfellerScale.HOUR,
        )()
    assert res == expected


@pytest.mark.parametrize(
    'days, fivemins, expected', [
        (
            # ничего от реактора не пришло
            [],
            [],
            None,
        ),
        (
            # только перый день по msk
            [datetime(2020, 1, 1)],
            [],
            datetime(2020, 1, 1, 21),
        ),
        (
            # два дня по msk
            [datetime(2020, 1, 1), datetime(2020, 1, 2)],
            [],
             datetime(2020, 1, 2, 21),
        ),
        (
            # два дня с дыркой по msk
            [datetime(2020, 1, 1), datetime(2020, 1, 3)],
            [],
            datetime(2020, 1, 1, 21),
        ),
        (
            # только 5 мин по msk
            [],
            [datetime(2020, 10, 10, 12, 0)],
            datetime(2020, 10, 10, 9, 5),
        ),
        (
            # два последовательных 5 мин по мск
            [],
            [datetime(2020, 10, 10, 12, 5), datetime(2020, 10, 10, 12, 10)],
            datetime(2020, 10, 10, 9, 15),
        ),
        (
            # две пятимянутки с дыркой между ними
            [],
            [datetime(2020, 10, 10, 12, 0), datetime(2020, 10, 10, 12, 10)],
            datetime(2020, 10, 10, 9, 5),
        ),
        (
            # день с дыркой, пятимянутка в конце
            [datetime(2020, 11, 2), datetime(2020, 11, 4)],
            [datetime(2020, 11, 4, 0)],
            datetime(2020, 11, 2, 21),
        ),
        (
            # день с дыркой и с пятимятуткой рядом с перым днем
            [datetime(2020, 11, 2), datetime(2020, 11, 4)],
            [datetime(2020, 11, 3, 0, 0)],
            datetime(2020, 11, 2, 21, 5),
        ),
        (
            # день с дыркой и с пятимянуткой не рядом с перым днем
            [datetime(2020, 11, 2), datetime(2020, 11, 4)],
            [datetime(2020, 11, 3, 1)],
            datetime(2020, 11, 2, 21),
        ),
        (
            # пятимятутки с дыркой, но она покрыта дневной
            [datetime(2020, 11, 2)],
            [datetime(2020, 11, 2, 0), datetime(2020, 11, 3, 0)],
            datetime(2020, 11, 2, 21, 5),
        ),
        (
            # регулярный случай № 1
            [datetime(2020, 11, 1), datetime(2020, 11, 2)],
            [
                *dtu.period(
                    datetime(2020, 11, 3),
                    datetime(2020, 11, 3, 2, 55)
                ).split_in_5mins()
            ],
            datetime(2020, 11, 3, 0),
        ),
        (
            # регулярный случай № 2
            [datetime(2020, 11, 1), datetime(2020, 11, 2)],
            [
                *_fivemins_in_day(datetime(2020, 11, 3)),
                datetime(2020, 11, 4, 0),
                datetime(2020, 11, 4, 0, 5),
            ],
            datetime(2020, 11, 3, 21, 10),
        ),
    ]
)
def test_user_time_only_from_daily_and_5m_scales(days, fivemins, expected):

    def side_effect(*args, **kwargs):
        if kwargs['scale'] is LogfellerScale.DAY:
            return days
        elif kwargs['scale'] is LogfellerScale.FIVEMIN:
            return fivemins

    _get_scale_patch = mock.patch(
        _get_scale_func_name(),
        side_effect=side_effect,
    )

    with _get_scale_patch:
        res = LogfelellerLastDttmGetter(
            'dummy',
            log_tz='msk',
            scale=LogfellerScale.DAY,
            prompt_scale=LogfellerScale.FIVEMIN,
        )()
    assert res == expected


@pytest.mark.parametrize(
    'hours, halfhours, expected', [
        (
            # ничего от реактора не пришло
            [],
            [],
            None,
        ),
        (
            # только перый час по msk
            [datetime(2020, 1, 2)],
            [],
            datetime(2020, 1, 1, 22),
        ),
        (
            # два часа по msk
            [datetime(2020, 1, 2), datetime(2020, 1, 2, 1)],
            [],
             datetime(2020, 1, 1, 23),
        ),
        (
            # два дня с дыркой по msk
            [datetime(2020, 1, 2), datetime(2020, 1, 2, 2)],
            [],
            datetime(2020, 1, 1, 22),
        ),
        (
            # только полчаса msk
            [],
            [datetime(2020, 10, 10, 12, 0)],
            datetime(2020, 10, 10, 9, 30),
        ),
        (
            # два последовательных полуаса по мск
            [],
            [datetime(2020, 10, 10, 12, 0), datetime(2020, 10, 10, 12, 30)],
            datetime(2020, 10, 10, 10),
        ),
        (
            # два получаса с дыркой между ними
            [],
            [datetime(2020, 10, 10, 12, 0), datetime(2020, 10, 10, 13, 0)],
            datetime(2020, 10, 10, 9, 30),
        ),
        (
            # час с дыркой, получас в конце
            [datetime(2020, 11, 2, 0), datetime(2020, 11, 2, 2)],
            [datetime(2020, 11, 2, 3)],
            datetime(2020, 11, 1, 22),
        ),
        (
            # час с дыркой и с получас рядом с перым часом
            [datetime(2020, 11, 2), datetime(2020, 11, 2, 2)],
            [datetime(2020, 11, 2, 1, 0)],
            datetime(2020, 11, 1, 22, 30),
        ),
        (
            # час с дыркой и с полчасом не рядом с перым днем
            [datetime(2020, 11, 2), datetime(2020, 11, 2, 2)],
            [datetime(2020, 11, 2, 1, 30)],
            datetime(2020, 11, 1, 22),
        ),
        (
            # получасы с дыркой, но она покрыта часом
            [datetime(2020, 11, 2)],
            [datetime(2020, 11, 2, 0), datetime(2020, 11, 2, 1)],
            datetime(2020, 11, 1, 22, 30),
        ),
        (
            # регулярный случай № 1
            _hours_in_day(datetime(2020, 11, 2)),
            [
                datetime(2020, 11, 3, 0),
                datetime(2020, 11, 3, 0, 30),
                datetime(2020, 11, 3, 1),
                datetime(2020, 11, 3, 1, 30),
                datetime(2020, 11, 3, 2),
                datetime(2020, 11, 3, 2, 30),
            ],
            datetime(2020, 11, 3, 0),
        ),
        (
            # регулярный случай № 2
            _hours_in_day(datetime(2020, 11, 2)),
            [
                datetime(2020, 11, 3, 0),
                datetime(2020, 11, 3, 0, 30),
                datetime(2020, 11, 3, 1),
                datetime(2020, 11, 3, 1, 30),
            ],
            datetime(2020, 11, 2, 23),
        ),
    ]
)
def test_user_time_from_hour_and_hh_scales(hours, halfhours, expected):

    def side_effect(*args, **kwargs):
        if kwargs['scale'] is LogfellerScale.HOUR:
            return hours
        elif kwargs['scale'] is LogfellerScale.HALFHOUR:
            return halfhours

    _get_scale_patch = mock.patch(
        _get_scale_func_name(),
        side_effect=side_effect,
    )

    with _get_scale_patch:
        res = LogfelellerLastDttmGetter(
            'dummy',
            log_tz='msk',
            scale=LogfellerScale.HOUR,
            prompt_scale=LogfellerScale.HALFHOUR,
        )()
    assert res == expected


@pytest.mark.parametrize(
    'hours, fivemins, expected', [
        (
            # ничего от реактора не пришло
            [],
            [],
            None,
        ),
        (
            # только перый час
            [datetime(2020, 1, 2)],
            [],
            datetime(2020, 1, 2, 1),
        ),
        (
            # два часа
            [datetime(2020, 1, 2), datetime(2020, 1, 2, 1)],
            [],
             datetime(2020, 1, 2, 2),
        ),
        (
            # два дня с дыркой
            [datetime(2020, 1, 2), datetime(2020, 1, 2, 2)],
            [],
            datetime(2020, 1, 2, 1),
        ),
        (
            # только пятимянутка
            [],
            [datetime(2020, 10, 10, 12, 0)],
            datetime(2020, 10, 10, 12, 5),
        ),
        (
            # две последовательных пятимянутки
            [],
            [datetime(2020, 10, 10, 12, 0), datetime(2020, 10, 10, 12, 5)],
            datetime(2020, 10, 10, 12, 10),
        ),
        (
            # две пятимянутки с дыркой между ними
            [],
            [datetime(2020, 10, 10, 12, 0), datetime(2020, 10, 10, 13, 0)],
            datetime(2020, 10, 10, 12, 5),
        ),
        (
            # час с дыркой, пятимянутка в конце
            [datetime(2020, 11, 2, 0), datetime(2020, 11, 2, 2)],
            [datetime(2020, 11, 2, 3)],
            datetime(2020, 11, 2, 1),
        ),
        (
            # час с дыркой и с пятимянуткой рядом с перым часом
            [datetime(2020, 11, 2), datetime(2020, 11, 2, 2)],
            [datetime(2020, 11, 2, 1, 0)],
            datetime(2020, 11, 2, 1, 5),
        ),
        (
            # час с дыркой и с пятимянуткой не рядом с перым часом
            [datetime(2020, 11, 2), datetime(2020, 11, 2, 2)],
            [datetime(2020, 11, 2, 1, 30)],
            datetime(2020, 11, 2, 1),
        ),
        (
            # пятимянутки с дыркой, но она покрыта часом
            [datetime(2020, 11, 2)],
            [datetime(2020, 11, 2, 0), datetime(2020, 11, 2, 1)],
            datetime(2020, 11, 2, 1, 5),
        ),
        (
            # регулярный случай № 1
            _hours_in_day(datetime(2020, 11, 2))[:-3],
            [
                *dtu.period(
                    datetime(2020, 11, 2, 21),
                    datetime(2020, 11, 2, 23, 55)
                ).split_in_5mins()
            ],
            datetime(2020, 11, 3, 0),
        ),
    ]
)
def test_user_time_from_hour_and_hh_scales(hours, fivemins, expected):

    def side_effect(*args, **kwargs):
        if kwargs['scale'] is LogfellerScale.HOUR:
            return hours
        elif kwargs['scale'] is LogfellerScale.FIVEMIN:
            return fivemins

    _get_scale_patch = mock.patch(
        _get_scale_func_name(),
        side_effect=side_effect,
    )

    with _get_scale_patch:
        res = LogfelellerLastDttmGetter(
            'dummy',
            log_tz='utc',
            scale=LogfellerScale.HOUR,
            prompt_scale=LogfellerScale.FIVEMIN,
        )()
    assert res == expected


@pytest.mark.parametrize(
    'halfhours, fivemins, expected', [
        (
            # ничего от реактора не пришло
            [],
            [],
            None,
        ),
        (
            # только перый получас
            [datetime(2020, 1, 2)],
            [],
            datetime(2020, 1, 2, 0, 30),
        ),
        (
            # два получаса
            [datetime(2020, 1, 2), datetime(2020, 1, 2, 0, 30)],
            [],
             datetime(2020, 1, 2, 1),
        ),
        (
            # два получаса с дыркой
            [datetime(2020, 1, 2), datetime(2020, 1, 2, 1)],
            [],
            datetime(2020, 1, 2, 0, 30),
        ),
        (
            # только пятимянутка
            [],
            [datetime(2020, 10, 10, 12, 0)],
            datetime(2020, 10, 10, 12, 5),
        ),
        (
            # две последовательных пятимянутки
            [],
            [datetime(2020, 10, 10, 12, 0), datetime(2020, 10, 10, 12, 5)],
            datetime(2020, 10, 10, 12, 10),
        ),
        (
            # две пятимянутки с дыркой между ними
            [],
            [datetime(2020, 10, 10, 12, 0), datetime(2020, 10, 10, 13, 0)],
            datetime(2020, 10, 10, 12, 5),
        ),
        (
            # получас с дыркой, пятимянутка в конце
            [datetime(2020, 11, 2, 0), datetime(2020, 11, 2, 2)],
            [datetime(2020, 11, 2, 3)],
            datetime(2020, 11, 2, 0, 30),
        ),
        (
            # получас с дыркой и с пятимянуткой рядом с перым получасом
            [datetime(2020, 11, 2), datetime(2020, 11, 2, 2)],
            [datetime(2020, 11, 2, 0, 30)],
            datetime(2020, 11, 2, 0, 35),
        ),
        (
            # получас с дыркой и с пятимянуткой не рядом с перым получасом
            [datetime(2020, 11, 2), datetime(2020, 11, 2, 2)],
            [datetime(2020, 11, 2, 1, 30)],
            datetime(2020, 11, 2, 0, 30),
        ),
        (
            # пятимянутки с дыркой, но она покрыта получасом
            [datetime(2020, 11, 2)],
            [datetime(2020, 11, 2, 0), datetime(2020, 11, 2, 0, 30)],
            datetime(2020, 11, 2, 0, 35),
        ),
    ]
)
def test_user_time_from_hh_and_5min_scales(halfhours, fivemins, expected):

    def side_effect(*args, **kwargs):
        if kwargs['scale'] is LogfellerScale.HALFHOUR:
            return halfhours
        elif kwargs['scale'] is LogfellerScale.FIVEMIN:
            return fivemins

    _get_scale_patch = mock.patch(
        _get_scale_func_name(),
        side_effect=side_effect,
    )

    with _get_scale_patch:
        res = LogfelellerLastDttmGetter(
            'dummy',
            log_tz='utc',
            scale=LogfellerScale.HALFHOUR,
            prompt_scale=LogfellerScale.FIVEMIN,
        )()
    assert res == expected


@pytest.mark.parametrize(
    'scale, dttms, expected', [
        (
            LogfellerScale.DAY,
            [],
            None,
        ),
        (
            LogfellerScale.HOUR,
            [],
            None,
        ),
        (
            LogfellerScale.HALFHOUR,
            [],
            None,
        ),
        (
            LogfellerScale.FIVEMIN,
            [],
            None,
        ),
        (
            LogfellerScale.DAY,
            [datetime(2020, 1, 2), datetime(2020, 1, 3)],
            datetime(2020, 1, 4),
        ),
        (
            LogfellerScale.HOUR,
            [datetime(2020, 1, 2), datetime(2020, 1, 2, 1)],
            datetime(2020, 1, 2, 2),
        ),
        (
            LogfellerScale.HALFHOUR,
            [datetime(2020, 1, 2), datetime(2020, 1, 2, 0, 30)],
            datetime(2020, 1, 2, 1),
        ),
        (
            LogfellerScale.FIVEMIN,
            [datetime(2020, 1, 2), datetime(2020, 1, 2, 0, 5)],
            datetime(2020, 1, 2, 0, 10),
        ),
        (
            LogfellerScale.DAY,
            [datetime(2020, 1, 2), datetime(2020, 1, 4)],
            datetime(2020, 1, 3),
        ),
        (
            LogfellerScale.HOUR,
            [datetime(2020, 1, 2), datetime(2020, 1, 2, 2)],
            datetime(2020, 1, 2, 1),
        ),
        (
            LogfellerScale.HALFHOUR,
            [datetime(2020, 1, 2), datetime(2020, 1, 2, 1, 30)],
            datetime(2020, 1, 2, 0, 30),
        ),
        (
            LogfellerScale.FIVEMIN,
            [datetime(2020, 1, 2), datetime(2020, 1, 2, 10, 5)],
            datetime(2020, 1, 2, 0, 5),
        ),
    ]
)
def test_no_prompt_scale(scale, dttms, expected):

    def side_effect(*args, **kwargs):
        if kwargs['scale'] is scale:
            return dttms

    _get_scale_patch = mock.patch(
        _get_scale_func_name(),
        side_effect=side_effect,
    )

    with _get_scale_patch:
        res = LogfelellerLastDttmGetter(
            'dummy',
            log_tz='utc',
            scale=scale,
        )()

    assert res == expected


@pytest.mark.parametrize(
    'scale, prompt_scale, expected', [
        (
            LogfellerScale.DAY,
            LogfellerScale.HALFHOUR,
            'reactor#dummy/1d&30min',
        ),
        (
            LogfellerScale.DAY,
            LogfellerScale.HOUR,
            'reactor#dummy/1d&1h',
        ),
        (
            LogfellerScale.DAY,
            LogfellerScale.FIVEMIN,
            'reactor#dummy/1d&5min',
        ),
        (
            LogfellerScale.HOUR,
            LogfellerScale.HALFHOUR,
            'reactor#dummy/1h&30min',
        ),
        (
            LogfellerScale.HOUR,
            LogfellerScale.FIVEMIN,
            'reactor#dummy/1h&5min',
        ),
        (
            LogfellerScale.HALFHOUR,
            LogfellerScale.FIVEMIN,
            'reactor#dummy/30min&5min',
        ),
        (
            LogfellerScale.DAY,
            None,
            'reactor#dummy/1d',
        ),
        (
            LogfellerScale.HOUR,
            None,
            'reactor#dummy/1h',
        ),
        (
            LogfellerScale.HALFHOUR,
            None,
            'reactor#dummy/30min',
        ),
        (
            LogfellerScale.FIVEMIN,
            None,
            'reactor#dummy/5min',
        ),
    ]
)
def test_ctl_entity_algorithm_persistent(scale, prompt_scale, expected):
    # если этот тест падает, значит ты меняешь ctl.entity ключ для всех
    # внешних артефактов. Подумай, точно ли оно надо.
    proxy = LogfellerReactorArtifact(
        'dummy',
        scale=scale,
        prompt_scale=prompt_scale,
    )
    assert proxy.ctl_entity == expected
