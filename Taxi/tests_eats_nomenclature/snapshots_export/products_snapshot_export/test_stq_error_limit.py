import pytest

BRAND_ID = 777


def settings(
        max_retries_on_error=3,
        max_retries_on_busy=3,
        max_busy_time_in_ms=100000,
        retry_on_busy_delay_ms=1000,
):
    return {
        '__default__': {
            'max_retries_on_error': max_retries_on_error,
            'max_retries_on_busy': max_retries_on_busy,
            'max_busy_time_in_ms': max_busy_time_in_ms,
            'retry_on_busy_delay_ms': retry_on_busy_delay_ms,
            'insert_batch_size': 1000,
            'lookup_batch_size': 1000,
        },
    }


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=settings(max_retries_on_error=2),
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_brand_data.sql',
        'fill_data_for_stq_error_limit.sql',
    ],
)
async def test_stq_error_limit(
        taxi_config, put_products_snapshot_task_into_stq, testpoint,
):
    @testpoint('export-products-snapshot-injected-error')
    def task_testpoint(param):
        return {'inject_failure': True}

    task_id = '1'
    max_retries_on_error = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')[
        '__default__'
    ]['max_retries_on_error']

    for i in range(max_retries_on_error):
        await put_products_snapshot_task_into_stq(
            brand_id=BRAND_ID, task_id=task_id, expect_fail=True, exec_tries=i,
        )

    # should succeed because of the error limit
    await put_products_snapshot_task_into_stq(
        brand_id=BRAND_ID,
        task_id=task_id,
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )

    assert task_testpoint.has_calls
