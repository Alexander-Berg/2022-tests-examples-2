import pytest

from abt import consts as app_consts
from abt import models
from abt.generated.service.swagger.models import api as api_models
from abt.logic import highlight as highlight_logic
from abt.models import metric as metrics_models
from test_abt import consts


def create_metric(abt, greater_is_better):
    return metrics_models.from_config(
        abt.builders.get_mg_config_builder()
        .add_precomputes()
        .add_value_metric(greater_is_better=greater_is_better)
        .build_apply(api_models.MetricsGroupConfig.deserialize)
        .metrics[0],
    )


@pytest.mark.parametrize(
    'diff,greater_is_better,expected_characterization',
    [
        pytest.param(
            0,
            None,
            highlight_logic.Characterization.Unknown,
            id='greater_is_better is None',
        ),
        pytest.param(
            100,
            True,
            highlight_logic.Characterization.Positive,
            id='greater is better and positive',
        ),
        pytest.param(
            -100,
            True,
            highlight_logic.Characterization.Negative,
            id='greater is better and negative',
        ),
        pytest.param(
            100,
            False,
            highlight_logic.Characterization.Negative,
            id='greater is worse and positive',
        ),
        pytest.param(
            -100,
            False,
            highlight_logic.Characterization.Positive,
            id='greater is worse and negative',
        ),
        pytest.param(
            0,
            True,
            highlight_logic.Characterization.Unknown,
            id='diff is zero',
        ),
        pytest.param(
            None,
            True,
            highlight_logic.Characterization.Unknown,
            id='diff is None',
        ),
    ],
)
def test_metric_characterization(
        abt, diff, greater_is_better, expected_characterization,
):
    assert (
        highlight_logic.compute_metric_characterization(
            models.MetricDiff(abs=diff), create_metric(abt, greater_is_better),
        )
        == expected_characterization
    )


CONFIDENCE_THRESHOLDS_CONFIG = {
    app_consts.SHAPIRO_TEST_NAME: api_models.Thresholds(
        weak='0.2', strong='0.6',
    ),
    app_consts.MANNWHITNEYU_TEST_NAME: api_models.Thresholds(
        weak='0.3', strong='0.1',
    ),
    app_consts.TTEST_TEST_NAME: api_models.Thresholds(
        weak='0.3', strong='0.1',
    ),
}

POSITIVE_DIFF = 100

STRONG_PVALUES = models.MetricPValues(
    ttest=0.01, mannwhitneyu=0.01, shapiro=0.99,
)


@pytest.mark.parametrize(
    'colors_config,thresholds_config,diff,'
    'greater_is_better,pvalues,expected_colors',
    [
        pytest.param(
            {
                'strong/positive': api_models.MetricColorsConfig(
                    background='background', font='font', wiki='wiki',
                ),
            },
            CONFIDENCE_THRESHOLDS_CONFIG,
            POSITIVE_DIFF,
            True,
            STRONG_PVALUES,
            highlight_logic.ColorsSettings(
                background='background',
                font='font',
                alias='strong/positive',
                wiki='wiki',
            ),
            id='select color from config',
        ),
        pytest.param(
            {
                '__default__': api_models.MetricColorsConfig(
                    background=consts.DEFAULT_BACKGROUND_COLOR,
                    font=consts.DEFAULT_FONT_COLOR,
                    wiki='wiki',
                ),
            },
            CONFIDENCE_THRESHOLDS_CONFIG,
            POSITIVE_DIFF,
            True,
            STRONG_PVALUES,
            highlight_logic.ColorsSettings(
                background=consts.DEFAULT_BACKGROUND_COLOR,
                font=consts.DEFAULT_FONT_COLOR,
                alias='strong/positive',
                wiki='wiki',
            ),
            id='fallback to __default__',
        ),
    ],
)
def test_highlighter_select_color(
        abt,
        colors_config,
        thresholds_config,
        diff,
        greater_is_better,
        pvalues,
        expected_colors,
):
    highlight_colors_config = api_models.HighlightColorsConfig(
        extra=colors_config,
    )
    thresholds_config = api_models.ConfidenceThresholdsConfig(
        extra=thresholds_config,
    )

    highlighter = highlight_logic.Highlighter(
        highlight_colors_config, thresholds_config,
    )

    assert (
        highlighter.select_colors(
            models.MetricDiff(abs=diff),
            pvalues,
            create_metric(abt, greater_is_better),
        )
        == expected_colors
    )
