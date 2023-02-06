import pytest

METRICS_NAME = 'product-types-metrics'
PERIODIC_NAME = 'eats_nomenclature-product-types-metrics'


@pytest.mark.parametrize('products_usage_threshold', [12, 48, 96])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_product_types_metrics(
        taxi_eats_nomenclature,
        taxi_eats_nomenclature_monitor,
        testpoint,
        taxi_config,
        products_usage_threshold,
):
    set_config(taxi_config, products_usage_threshold)

    @testpoint(f'eats_nomenclature::{METRICS_NAME}')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature.run_periodic_task(PERIODIC_NAME)
    handle_finished.next_call()

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    metric_values = metrics[METRICS_NAME]

    expected_metrics = get_expected_metrics(products_usage_threshold)

    per_brand_metrics = dict(sorted(metric_values.items()))
    per_brand_metrics_expected = dict(sorted(expected_metrics.items()))

    assert expected_metrics['total'] == metric_values['total']
    assert per_brand_metrics_expected == per_brand_metrics


def set_config(taxi_config, products_usage_threshold):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_DB_CLEANUP': {
                'products_usage': {'interval-hours': products_usage_threshold},
            },
            'EATS_NOMENCLATURE_MASTER_TREE': {
                'master_tree_settings': {
                    '1': {'assortment_name': 'assortment_name_1'},
                    '2': {'assortment_name': 'assortment_name_3'},
                },
            },
            'EATS_NOMENCLATURE_PERIODICS': {
                '__default__': {'is_enabled': False, 'period_in_sec': 600},
                METRICS_NAME: {'is_enabled': True, 'period_in_sec': 600},
            },
        },
    )


def get_expected_metrics(products_usage_threshold):
    brand1_old_products_count = 0
    brand2_old_products_count = 0
    if products_usage_threshold == 12:
        brand1_old_products_count = 2
        brand2_old_products_count = 1
    elif products_usage_threshold == 48:
        brand1_old_products_count = 1
    total_old_products_count = (
        brand1_old_products_count + brand2_old_products_count
    )
    return {
        'total': {
            'products_count': 12 - total_old_products_count,
            'untyped_products_count': 3 - brand2_old_products_count,
            'product_types_out_of_tree_count': 1,
            'products_out_of_tree_count': 3,
        },
        'per_brand': {
            '$meta': {'solomon_children_labels': 'brand_slug'},
            'brand1': {
                'products_count': 9 - brand1_old_products_count,
                'untyped_products_count': 2,
                'product_types_out_of_tree_count': 2,
                'products_out_of_tree_count': 2,
            },
            'brand2': {
                'products_count': 3 - brand2_old_products_count,
                'untyped_products_count': 1 - brand2_old_products_count,
                'product_types_out_of_tree_count': 1,
                'products_out_of_tree_count': 1,
            },
        },
    }


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=False)
