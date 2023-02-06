import pytest

BRAND_ID = 777


@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_brand_data.sql',
        'fill_data_for_full_schema.sql',
    ],
)
async def test_full_schema(
        generate_product_snapshot_from_row,
        load_json,
        put_products_snapshot_task_into_stq,
        sorted_logged_data,
        testpoint,
):
    """
    Test a schema with all posible fields filled
    (and multiple values where possible)
    """

    logged_data = []

    @testpoint('export-products-snapshot')
    def yt_logger(row):
        logged_data.append(generate_product_snapshot_from_row(row))

    await put_products_snapshot_task_into_stq(
        brand_id=BRAND_ID, task_id=str(BRAND_ID),
    )
    assert yt_logger.has_calls

    expected_data = load_json('full_logged_data.json')
    assert sorted_logged_data(logged_data) == sorted_logged_data(expected_data)


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_brand_data.sql',
        'fill_data_for_minimal_schema.sql',
    ],
)
async def test_minimal_schema(
        generate_product_snapshot_from_row,
        load_json,
        put_products_snapshot_task_into_stq,
        sorted_logged_data,
        testpoint,
):
    """
    Test a schema with minimal posible fields filled
    """

    logged_data = []

    @testpoint('export-products-snapshot')
    def yt_logger(row):
        logged_data.append(generate_product_snapshot_from_row(row))

    await put_products_snapshot_task_into_stq(
        brand_id=BRAND_ID, task_id=str(BRAND_ID),
    )
    assert yt_logger.has_calls

    expected_data = load_json('minimal_logged_data.json')
    assert sorted_logged_data(logged_data) == sorted_logged_data(expected_data)


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_brand_data.sql'],
)
async def test_empty_schema(
        generate_product_snapshot_from_row,
        put_products_snapshot_task_into_stq,
        sorted_logged_data,
        testpoint,
):
    """
    Test a schema with empty data
    """

    logged_data = []

    @testpoint('export-products-snapshot')
    def yt_logger(row):
        logged_data.append(generate_product_snapshot_from_row(row))

    await put_products_snapshot_task_into_stq(
        brand_id=BRAND_ID, task_id=str(BRAND_ID),
    )
    assert not yt_logger.has_calls

    assert sorted_logged_data(logged_data) == []
