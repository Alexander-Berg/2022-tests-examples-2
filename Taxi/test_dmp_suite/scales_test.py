# coding: utf-8
import pytest

from dmp_suite import datetime_utils as dtu, scales


def test_scale_for_name():
    # get by name
    assert 'm' == scales.get_scale_by_name('m').name
    # get by alias
    assert 'd' == scales.get_scale_by_name('1d').name

    with pytest.raises(scales.UnknownScaleError):
        scales.get_scale_by_name('asd')


def test_all_scales():
    all_scales = scales.all_scales()
    assert scales.day in all_scales
    assert scales.week in all_scales
    assert scales.month in all_scales
    assert scales.year in all_scales
    assert scales.hour in all_scales
    assert scales.half_hour in all_scales


def test_all_scale_names():
    names = list(scales.all_scale_names())

    # name
    assert 'm' in names
    # alias
    assert '1d' in names
    # non usual name
    assert '30min' in names

    assert len(names) == len(set(names))


@pytest.mark.parametrize('period', [
    dtu.Period('2017-03-01', '2017-03-11'),
    dtu.Period('2017-03-01', '2017-03-01'),
    dtu.Period('2017-03-01 13:00:00', '2017-03-01 16:59:59.999999'),
    dtu.Period('2017-03-01 00:00:00', '2017-03-07 23:59:59.999999'),
    dtu.Period('2017-01-01 00:00:00.000000', '2018-12-31 23:59:59.999999')
])
def test_is_entire__false(period):
    for scale in scales.all_scales():
        assert scale.is_entire(period) is False


@pytest.mark.parametrize('scale, period', [
    (scales.half_hour, dtu.period('2018-07-01 14:30:00',
                                  '2018-07-01 14:59:59.999999')),
    (scales.hour, dtu.period('2018-07-01 14:00:00',
                             '2018-07-01 14:59:59.999999')),
    (scales.day, dtu.Period('2018-07-01', '2018-07-01 23:59:59.999999')),
    (scales.week, dtu.Period('2018-07-02', '2018-07-08 23:59:59.999999')),
    (scales.month, dtu.Period('2018-07-01', '2018-07-31 23:59:59.999999')),
    (scales.year, dtu.Period('2018-01-01', '2018-12-31 23:59:59.999999')),
])
def test_is_entire__true(scale, period):
    assert scale.is_entire(period)


@pytest.mark.parametrize('scale, period, expect_extended_period', [
    (
        scales.hour,
        dtu.period('2018-07-01 14:10:00', '2018-07-03 16:30:00'),
        dtu.period('2018-07-01 14:00:00', '2018-07-03 16:59:59.999999'),
    ),
    (
        scales.hour,
        dtu.period('2018-07-01 14:00:00', '2018-07-03 16:59:59.999999'),
        dtu.period('2018-07-01 14:00:00', '2018-07-03 16:59:59.999999'),
    ),
    (
        scales.day,
        dtu.period('2018-07-01 14:10:00', '2018-07-03 16:30:00'),
        dtu.period('2018-07-01 00:00:00', '2018-07-03 23:59:59.999999'),
    ),
    (
        scales.day,
        dtu.period('2018-07-01 00:00:00', '2018-07-03 23:59:59.999999'),
        dtu.period('2018-07-01 00:00:00', '2018-07-03 23:59:59.999999'),
    ),
])
def test_extend_period(scale, period, expect_extended_period):
    assert scale.extend_period(period) == expect_extended_period


def test_scale_eq():
    scale_classes = [scale.__class__ for scale in scales.all_scales()]

    for cls1 in scale_classes:
        for cls2 in scale_classes:
            if cls1 == cls2:
                assert cls1() == cls2()
            else:
                assert cls1() != cls2()
