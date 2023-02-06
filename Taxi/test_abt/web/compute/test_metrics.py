import typing as tp

import numpy as np
import pytest

from abt import models
from abt.generated.service.swagger.models import api as api_models
from abt.models import metric as metrics_models
from abt.utils import exceptions
from test_abt import consts


def create_group_measures(
        measures_data: tp.Dict[str, tp.List[float]],
) -> models.RevisionGroupMeasures:
    measures = models.RevisionGroupMeasures()
    for measure_name, measure_values in measures_data.items():
        measures.extend(measure_name, measure_values)
    measures.lock()
    return measures


@pytest.mark.parametrize(
    'metric_type',
    [metrics_models.MetricType.Value, metrics_models.MetricType.Ratio],
)
def test_parse_config(abt, metric_type):
    builder = abt.builders.get_mg_config_builder().add_precomputes()

    if metric_type == metrics_models.MetricType.Value:
        builder.add_value_metric()
    elif metric_type == metrics_models.MetricType.Ratio:
        builder.add_ratio_metric()

    config = builder.build_apply(api_models.MetricsGroupConfig.deserialize)

    assert len(config.metrics) == 1

    metric_config = config.metrics[0]

    metric = metrics_models.from_config(metric_config)

    assert metric.type == metric_type
    assert metric.name == metric_config.name
    assert metric.title == metric_config.title
    assert metric.greater_is_better == metric_config.greater_is_better

    if metric_type == metrics_models.MetricType.Value:
        assert metric.fields == {metric_config.params.value}
    elif metric_type == metrics_models.MetricType.Ratio:
        assert metric.fields == {
            metric_config.params.numerator,
            metric_config.params.denominator,
        }


@pytest.mark.parametrize('value', [True, False, None])
def test_greater_is_better(abt, value):
    config = (
        abt.builders.get_mg_config_builder()
        .add_precomputes()
        .add_value_metric(greater_is_better=value)
        .add_ratio_metric(greater_is_better=value)
        .build_apply(api_models.MetricsGroupConfig.deserialize)
    )

    assert len(config.metrics) == 2
    assert all(
        metrics_models.from_config(metric_config).greater_is_better == value
        for metric_config in config.metrics
    )


@pytest.mark.parametrize(
    'measures,expecting_error,expected_value',
    [
        pytest.param(
            create_group_measures({consts.DEFAULT_VALUE_COLUMN: [1, 2, 3]}),
            False,
            6.0,
            id='Successful evaluation',
        ),
        pytest.param(
            create_group_measures({consts.DEFAULT_VALUE_COLUMN: [1, 2, -6]}),
            False,
            -3.0,
            id='Successful evaluation with negative value',
        ),
        pytest.param(
            create_group_measures({}), True, None, id='No column -> error',
        ),
        pytest.param(
            create_group_measures({consts.DEFAULT_VALUE_COLUMN: []}),
            True,
            None,
            id='Empty list -> error',
        ),
    ],
)
def test_value_metric_eval(abt, measures, expecting_error, expected_value):
    metric = metrics_models.from_config(
        abt.builders.get_mg_config_builder()
        .add_precomputes()
        .add_value_metric()
        .build_apply(api_models.MetricsGroupConfig.deserialize)
        .metrics[0],
    )

    if expecting_error:
        with pytest.raises(exceptions.MetricEvaluationError):
            metric.eval(measures)
    else:
        evaluated = metric.eval(measures)
        assert isinstance(evaluated, float), (
            f'Incorrect type of evaluated value. '
            f'Expected float, but {type(evaluated).__name__} received'
        )
        assert evaluated == expected_value


@pytest.mark.parametrize(
    'measures,expecting_error,expected_value',
    [
        pytest.param(
            create_group_measures(
                {
                    consts.DEFAULT_NUMERATOR_COLUMN: [1, 2, 3],
                    consts.DEFAULT_DENOMINATOR_COLUMN: [5, 6, 8],
                },
            ),
            False,
            0.316,
            id='Successful evaluation',
        ),
        pytest.param(
            create_group_measures(
                {
                    consts.DEFAULT_NUMERATOR_COLUMN: [1, 2, 3],
                    consts.DEFAULT_DENOMINATOR_COLUMN: [7, -6, -8],
                },
            ),
            False,
            -0.857,
            id='Successful evaluation with negative value',
        ),
        pytest.param(
            create_group_measures(
                {
                    consts.DEFAULT_NUMERATOR_COLUMN: [1, 2, 3],
                    consts.DEFAULT_DENOMINATOR_COLUMN: [5, -5, 0],
                },
            ),
            True,
            None,
            id='Divided by zero',
        ),
        pytest.param(
            create_group_measures({}), True, None, id='No columns -> error',
        ),
        pytest.param(
            create_group_measures(
                {
                    consts.DEFAULT_NUMERATOR_COLUMN: [1, 2, 3],
                    consts.DEFAULT_DENOMINATOR_COLUMN: [],
                },
            ),
            True,
            None,
            id='Empty list -> error',
        ),
    ],
)
def test_ratio_metric_eval(abt, measures, expecting_error, expected_value):
    metric = metrics_models.from_config(
        abt.builders.get_mg_config_builder()
        .add_precomputes()
        .add_ratio_metric()
        .build_apply(api_models.MetricsGroupConfig.deserialize)
        .metrics[0],
    )

    if expecting_error:
        with pytest.raises(exceptions.MetricEvaluationError):
            metric.eval(measures)
    else:
        evaluated = metric.eval(measures)
        assert isinstance(evaluated, float), (
            f'Incorrect type of evaluated value. '
            f'Expected float, but {type(evaluated).__name__} received'
        )
        assert round(evaluated, 3) == expected_value


@pytest.mark.parametrize(
    'measures,expected',
    [
        pytest.param(
            create_group_measures({consts.DEFAULT_VALUE_COLUMN: [1, 2, 3]}),
            np.array([1, 2, 3]),
            id='Successful evaluation',
        ),
    ],
)
def test_value_metric_eval_values(abt, measures, expected):
    metric = metrics_models.from_config(
        abt.builders.get_mg_config_builder()
        .add_precomputes()
        .add_value_metric()
        .build_apply(api_models.MetricsGroupConfig.deserialize)
        .metrics[0],
    )

    np.testing.assert_array_equal(metric.eval_values(measures), expected)


@pytest.mark.parametrize(
    'measures,expected',
    [
        pytest.param(
            create_group_measures(
                {
                    consts.DEFAULT_NUMERATOR_COLUMN: np.array([1, 2, 3]),
                    consts.DEFAULT_DENOMINATOR_COLUMN: np.array([5, 6, 8]),
                },
            ),
            np.array([1 / 5, 2 / 6, 3 / 8]),
            id='Successful evaluation',
        ),
    ],
)
def test_ratio_metric_eval_values(abt, measures, expected):
    metric = metrics_models.from_config(
        abt.builders.get_mg_config_builder()
        .add_precomputes()
        .add_ratio_metric()
        .build_apply(api_models.MetricsGroupConfig.deserialize)
        .metrics[0],
    )

    np.testing.assert_array_equal(metric.eval_values(measures), expected)


@pytest.mark.parametrize(
    'pvalues,is_available',
    [
        pytest.param(
            metrics_models.MetricPValues(
                ttest=consts.SOME_FLOAT_VALUE,
                mannwhitneyu=consts.SOME_FLOAT_VALUE,
                shapiro=consts.SOME_FLOAT_VALUE,
            ),
            True,
            id='all pvalues available',
        ),
        pytest.param(
            metrics_models.MetricPValues(
                ttest=consts.SOME_FLOAT_VALUE,
                mannwhitneyu=None,
                shapiro=consts.SOME_FLOAT_VALUE,
            ),
            False,
            id='one pvalue is none',
        ),
        pytest.param(
            metrics_models.MetricPValues(
                ttest=consts.SOME_FLOAT_VALUE,
                mannwhitneyu=None,
                shapiro=consts.SOME_FLOAT_VALUE,
            ),
            False,
            id='all pvalues are none',
        ),
    ],
)
def test_pvalues_all_available(pvalues, is_available):
    assert pvalues.all_available == is_available
