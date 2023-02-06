import pytest


@pytest.mark.parametrize(
    'default_pipeline', ['regular_throw', 'explicit_throw'],
)
async def test_get_stats(
        mock_admin_pipelines,
        taxi_config,
        taxi_surge_calculator,
        taxi_surge_calculator_monitor,
        default_pipeline,
):
    taxi_config.set_values({'SURGE_DEFAULT_PIPELINE': default_pipeline})

    request = {'point_a': [38.1, 51]}

    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 500

    metrics = await taxi_surge_calculator_monitor.get_metric('js_metrics')

    if default_pipeline == 'regular_throw':
        assert (
            metrics['by_script'][default_pipeline]['statuses'][
                'runtime_error'
            ]['1min']
            == 1
        )
    else:
        assert (
            'runtime_error'
            not in metrics['by_script'][default_pipeline]['statuses']
        )
