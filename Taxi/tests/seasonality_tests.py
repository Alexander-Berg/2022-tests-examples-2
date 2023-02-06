#  coding: utf-8

import pytest

from business_models.models.seasonality import RotationSeasonality
from business_models.accuracy.seasonality_scoring import SeasonalityScore


@pytest.mark.parametrize(
    "scale, base_scale",
    [
        ['day', 'week'],
        ['day', 'month'],
        ['day', 'year'],
        ['month', 'year'],
        ['week', 'year']
    ]
)
def rotation_seasonality_tests(scale, base_scale, return_score=False):
    """Проверяем, что для комбинации scale, base_scale расчет сезонности:
        - не падает
        - почти идеально предсказывает синус
        - почти идеально предсказывает sin(x) + x
    """
    score = SeasonalityScore()
    score.score(RotationSeasonality(), parameters={'base_scale': base_scale},
                scale=scale, base_scale=base_scale,
                sample=['SinusAddTrendSample', 'SinusSample'])

    if return_score:
        return score

    errors = score.describe(metrics=['mape', 'mpe'])
    if not (errors < 0.001).all().all():
        raise ValueError('Errors in predictions: {}'.format(errors))


