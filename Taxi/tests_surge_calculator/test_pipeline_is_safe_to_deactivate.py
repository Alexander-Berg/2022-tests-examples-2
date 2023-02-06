import pytest

INVALID_PIPELINE = 'invalid_pipeline'


@pytest.mark.config(SURGE_DEFAULT_PIPELINE='default')
@pytest.mark.parametrize(
    'pipeline_name, expected_reason',
    [
        ('default', '\'default\' is default pipeline'),
        (
            'used_in_zone',
            '\'used_in_zone\' is used in zones (experiments): '
            'active1 (test_production_experiment); '
            'active2 (test_production_experiment)',
        ),
        (
            'used_in_zone_alot',
            '\'used_in_zone_alot\' is used in zones (experiments): '
            'active1 (test_experimental_experiment_1); '
            'active1 (test_experimental_experiment_2); '
            'active2 (test_experimental_experiment_1); '
            'active2 (test_experimental_experiment_2); '
            'active3 (test_production_experiment) '
            'and more...',
        ),
        ('used_in_removed_zone', ''),
        ('used_in_disabled_experiment', ''),
    ],
)
async def test(taxi_surge_calculator, pipeline_name, expected_reason):
    response = await taxi_surge_calculator.post(
        '/v1/js/pipeline/is-safe-to-deactivate',
        params={'consumer': 'taxi-surge', 'name': pipeline_name},
    )

    assert response.json() == {'unsafe_reason': expected_reason}
