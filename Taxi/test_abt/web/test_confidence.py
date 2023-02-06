import pytest

from abt import consts as app_consts
from abt import models
from abt.generated.service.swagger.models import api as api_models
from abt.logic import confidence as confidence_logic
from test_abt import consts


@pytest.mark.parametrize(
    'pvalues,thresholds,expected_confidence',
    [
        pytest.param(
            models.MetricPValues(
                ttest=consts.SOME_FLOAT_VALUE,
                mannwhitneyu=consts.SOME_FLOAT_VALUE,
                shapiro=None,
            ),
            consts.UNIMPORTANT_VALUE,
            confidence_logic.ConfidenceLevel.Unknown,
            id='incompete pvalues',
        ),
        pytest.param(
            models.MetricPValues(
                ttest=consts.SOME_FLOAT_VALUE,
                mannwhitneyu=consts.SOME_FLOAT_VALUE,
                shapiro=consts.SOME_FLOAT_VALUE,
            ),
            {
                app_consts.SHAPIRO_TEST_NAME: api_models.Thresholds(
                    weak='0.1', strong='0.2',
                ),
            },
            confidence_logic.ConfidenceLevel.Unknown,
            id='not all fields in config',
        ),
        pytest.param(
            models.MetricPValues(ttest=0.01, mannwhitneyu=0.01, shapiro=0.7),
            {
                app_consts.SHAPIRO_TEST_NAME: api_models.Thresholds(
                    weak='0.2', strong='0.6',
                ),
                app_consts.MANNWHITNEYU_TEST_NAME: api_models.Thresholds(
                    weak='0.3', strong='0.1',
                ),
                app_consts.TTEST_TEST_NAME: api_models.Thresholds(
                    weak='0.3', strong='0.1',
                ),
            },
            confidence_logic.ConfidenceLevel.Strong,
            id='shapiro > strong && others < strong -> strong',
        ),
        pytest.param(
            models.MetricPValues(ttest=0.01, mannwhitneyu=0.01, shapiro=0.4),
            {
                app_consts.SHAPIRO_TEST_NAME: api_models.Thresholds(
                    weak='0.2', strong='0.6',
                ),
                app_consts.MANNWHITNEYU_TEST_NAME: api_models.Thresholds(
                    weak='0.3', strong='0.1',
                ),
                app_consts.TTEST_TEST_NAME: api_models.Thresholds(
                    weak='0.3', strong='0.1',
                ),
            },
            confidence_logic.ConfidenceLevel.Weak,
            id='strong > shapiro > weak && others < strong -> weak',
        ),
        pytest.param(
            models.MetricPValues(ttest=0.2, mannwhitneyu=0.2, shapiro=0.9),
            {
                app_consts.SHAPIRO_TEST_NAME: api_models.Thresholds(
                    weak='0.2', strong='0.6',
                ),
                app_consts.MANNWHITNEYU_TEST_NAME: api_models.Thresholds(
                    weak='0.3', strong='0.1',
                ),
                app_consts.TTEST_TEST_NAME: api_models.Thresholds(
                    weak='0.3', strong='0.1',
                ),
            },
            confidence_logic.ConfidenceLevel.Weak,
            id='shapiro > strong && weak > others > strong -> weak',
        ),
        pytest.param(
            models.MetricPValues(ttest=0.01, mannwhitneyu=0.01, shapiro=0.1),
            {
                app_consts.SHAPIRO_TEST_NAME: api_models.Thresholds(
                    weak='0.2', strong='0.6',
                ),
                app_consts.MANNWHITNEYU_TEST_NAME: api_models.Thresholds(
                    weak='0.3', strong='0.1',
                ),
                app_consts.TTEST_TEST_NAME: api_models.Thresholds(
                    weak='0.3', strong='0.1',
                ),
            },
            confidence_logic.ConfidenceLevel.Unknown,
            id='shapiro < weak && others < strong -> unknown',
        ),
        pytest.param(
            models.MetricPValues(ttest=0.5, mannwhitneyu=0.5, shapiro=0.9),
            {
                app_consts.SHAPIRO_TEST_NAME: api_models.Thresholds(
                    weak='0.2', strong='0.6',
                ),
                app_consts.MANNWHITNEYU_TEST_NAME: api_models.Thresholds(
                    weak='0.3', strong='0.1',
                ),
                app_consts.TTEST_TEST_NAME: api_models.Thresholds(
                    weak='0.3', strong='0.1',
                ),
            },
            confidence_logic.ConfidenceLevel.Unknown,
            id='shapiro < strong && others > weak -> unknown',
        ),
    ],
)
def test_compute_confidence(pvalues, thresholds, expected_confidence):
    thresholds_config = api_models.ConfidenceThresholdsConfig(extra=thresholds)
    assert (
        confidence_logic.compute_confidence(pvalues, thresholds_config)
        == expected_confidence
    )
