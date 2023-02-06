import pytest

BRAND_ID = 777


@pytest.mark.parametrize(
    'exp_value, use_sku',
    [
        pytest.param({'enabled': True}, True, id='enabled'),
        pytest.param(
            {'enabled': True, 'excluded_brand_ids': [BRAND_ID]},
            False,
            id='enabled_with_excluded_brands',
        ),
        pytest.param({'enabled': False}, False, id='disabled'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_brand_data.sql',
        'fill_data_for_use_sku.sql',
    ],
)
async def test_use_sku(
        experiments3,
        generate_product_snapshot_from_row,
        load_json,
        put_products_snapshot_task_into_stq,
        sorted_logged_data,
        testpoint,
        # parametrize
        exp_value,
        use_sku,
):
    experiment_data = load_json('use_sku_experiment.json')
    experiment_data['experiments'][0]['clauses'][0]['value'] = exp_value
    experiments3.add_experiments_json(experiment_data)

    logged_data = []

    @testpoint('export-products-snapshot')
    def yt_logger(row):
        logged_data.append(generate_product_snapshot_from_row(row))

    await put_products_snapshot_task_into_stq(
        brand_id=BRAND_ID, task_id=str(BRAND_ID),
    )
    assert yt_logger.has_calls

    if use_sku:
        expected_data = load_json('logged_data_with_sku.json')
    else:
        expected_data = load_json('logged_data_without_sku.json')

    assert sorted_logged_data(logged_data) == sorted_logged_data(expected_data)
