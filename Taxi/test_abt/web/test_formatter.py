import pytest

from abt.generated.service.swagger.models import api as api_models
from abt.logic import format as format_logic


@pytest.fixture(name='formatter')
def prepared_formatter(web_context):
    config = web_context.config.ABT_FORMATTING_RULES
    return format_logic.Formatter(
        api_models.FormattingConfig.deserialize(config),
    )


@pytest.mark.parametrize(
    'number,formatted',
    [
        (100_000_000.0, '100,0M'),
        (100_560_000.123, '100,6M'),
        (-100_000_000.0, '-100,0M'),
        (-100_560_000.123, '-100,6M'),
        (500_000.0, '500K'),
        (500_900.0, '501K'),
        (-500_000.0, '-500K'),
        (-500_900.0, '-501K'),
        (50_000.0, '50,0K'),
        (50_900.0, '50,9K'),
        (-50_000.0, '-50,0K'),
        (-50_900.0, '-50,9K'),
        (500.678, '500,68'),
        (500.0, '500,0'),
        (-500.678, '-500,68'),
        (-500.0, '-500,0'),
        (0.1236, '0,124'),
        (0.0, '0,0'),
        (+0.0, '0,0'),
        (-0.0, '0,0'),
        (-0.1236, '-0,124'),
        (0.00056, '0,0006'),
        (-0.00056, '-0,0006'),
        (None, '-'),
    ],
)
def test_format_metric_with_target_config(formatter, number, formatted):
    assert formatter.format_metric(number) == formatted, f'Number: {number}'


@pytest.mark.parametrize(
    'number,formatted',
    [
        (0.0056, '+0,01%'),
        (-0.0056, '-0,01%'),
        (100.45678, '+100,46%'),
        (-100.45678, '-100,46%'),
        (None, '-'),
    ],
)
def test_format_relativediff_with_target_config(formatter, number, formatted):
    assert (
        formatter.format_relative_diff(number) == formatted
    ), f'Number: {number}'


@pytest.mark.parametrize(
    'number,formatted',
    [
        (10_000_000, '+10,0M'),
        (-10_000_000, '-10,0M'),
        (500_000, '+500K'),
        (-500_000, '-500K'),
        (50_000, '+50,0K'),
        (-50_000, '-50,0K'),
        (500.128, '+500,13'),
        (-500.128, '-500,13'),
        (0.1236, '+0,124'),
        (-0.1236, '-0,124'),
        (0.00056, '+0,0006'),
        (-0.00056, '-0,0006'),
        (0.0, '0,0'),
        (-0.0, '0,0'),
        (0.0000001, '0,0'),
        (None, '-'),
    ],
)
def test_format_absdiff_with_target_config(formatter, number, formatted):
    assert formatter.format_abs_diff(number) == formatted, f'Number: {number}'


METRIC = format_logic.ValueType.Metric

ABSDIFF = format_logic.ValueType.AbsDiff

RELATIVEDIFF = format_logic.ValueType.RelativeDiff


@pytest.mark.parametrize(
    'condition,value,value_type,is_matched',
    [
        (format_logic.AlwaysTruePredicate(), '100500', METRIC, True),
        (format_logic.GtePredicate('100'), 100, METRIC, True),
        (format_logic.GtePredicate('100'), 99, METRIC, False),
        (format_logic.GtePredicate('100'), 120, METRIC, True),
        (format_logic.GtePredicate('100'), -100, METRIC, True),
        (format_logic.GtePredicate('100'), -99, METRIC, False),
        (format_logic.GtePredicate('100'), -120, METRIC, True),
        (format_logic.LtePredicate('100'), 100, METRIC, True),
        (format_logic.LtePredicate('100'), 99, METRIC, True),
        (format_logic.LtePredicate('100'), 120, METRIC, False),
        (format_logic.LtePredicate('100'), -100, METRIC, True),
        (format_logic.LtePredicate('100'), -99, METRIC, True),
        (format_logic.LtePredicate('100'), -120, METRIC, False),
        (format_logic.GtPredicate('100'), 120, METRIC, True),
        (format_logic.GtPredicate('100'), 100, METRIC, False),
        (format_logic.GtPredicate('100'), -100, METRIC, False),
        (format_logic.GtPredicate('100'), -120, METRIC, True),
        (format_logic.LtPredicate('100'), 100, METRIC, False),
        (format_logic.LtPredicate('100'), 99, METRIC, True),
        (format_logic.LtPredicate('100'), -100, METRIC, False),
        (format_logic.LtPredicate('100'), -99, METRIC, True),
        (format_logic.TypesPredicate([METRIC.value]), 100500, METRIC, True),
        (format_logic.TypesPredicate([METRIC.value]), 100500, ABSDIFF, False),
    ],
)
def test_simple_conditions(condition, value, value_type, is_matched):
    assert condition.match(value, value_type) == is_matched


def test_and_condition():
    condition_config = api_models.FormattingConfigCondition(
        gt='100', lt='1000',
    )
    condition = format_logic.AndPredicate(condition_config)

    assert not condition.match(50, METRIC)
    assert condition.match(500, METRIC)


def test_empty_and_condition():
    condition = format_logic.AndPredicate(
        api_models.FormattingConfigCondition(),
    )
    assert condition.match(50, METRIC)


@pytest.mark.parametrize(
    'params,value,value_type,expected',
    [
        (api_models.FormattingConfigParams(round=3), 1.12389, METRIC, '1,124'),
        (
            api_models.FormattingConfigParams(round=3, suffix='%'),
            1.12389,
            METRIC,
            '1,124%',
        ),
        (
            api_models.FormattingConfigParams(round=3, divide_by='10'),
            10.12389,
            METRIC,
            '1,012',
        ),
        (api_models.FormattingConfigParams(round=0), 10.12389, METRIC, '10'),
        (api_models.FormattingConfigParams(round=3), -0.0, METRIC, '0,0'),
        (
            api_models.FormattingConfigParams(round=3, sign=True),
            -0.0,
            METRIC,
            '0,0',
        ),
        (
            api_models.FormattingConfigParams(round=3, sign=True),
            -123.1239,
            METRIC,
            '-123,124',
        ),
        (
            api_models.FormattingConfigParams(round=3, sign=True),
            123.1239,
            METRIC,
            '+123,124',
        ),
    ],
)
def test_different_params(params, value, value_type, expected):
    rule = format_logic.Rule(None, params)
    assert rule.apply(value, value_type) == expected
