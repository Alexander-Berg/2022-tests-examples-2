import pytest

PERIODIC_NAME = 'eats_nomenclature-autodisabled-items-metrics'
METRICS_NAME = 'autodisabled-items-metrics'


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_data.sql'],
)
@pytest.mark.parametrize('batch_size', [1, 1000])
async def test_autodisabled_items_metrics(
        taxi_eats_nomenclature,
        taxi_eats_nomenclature_monitor,
        testpoint,
        taxi_config,
        # parametrize params
        batch_size,
):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_PERIODICS': {
                '__default__': {'is_enabled': True, 'period_in_sec': 600},
            },
            'EATS_NOMENCLATURE_PROCESSING': {
                'periodic_autodisabled_items': {
                    'insert_batch_size': batch_size,
                    'lookup_batch_size': batch_size,
                },
            },
        },
    )

    @testpoint(f'eats_nomenclature::{METRICS_NAME}')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature.run_periodic_task(PERIODIC_NAME)
    handle_finished.next_call()

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    metric_values = metrics[METRICS_NAME]['autodisabled_products_count']

    expected_metrics_values = {
        '$meta': {'solomon_children_labels': 'brand_slug'},
        'brand777': 1,
        'brand888': 2,
    }

    assert expected_metrics_values == metric_values


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=False)
