import pytest

QUEUE_NAME = 'eats_nomenclature_brand_processing'


def settings(max_retries_on_error):
    return {
        '__default__': {
            'max_retries_on_error': max_retries_on_error,
            'insert_batch_size': 1000,
            'lookup_batch_size': 1000,
        },
    }


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=settings(max_retries_on_error=2),
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_stq_error_limit(task_enqueue_v2, pgsql, taxi_config):

    max_retries_on_error = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')[
        '__default__'
    ]['max_retries_on_error']
    task_id = '1'

    for i in range(max_retries_on_error):
        await task_enqueue_v2(
            QUEUE_NAME, task_id=task_id, expect_fail=True, exec_tries=i,
        )

    # should succeed because of the error limit
    await task_enqueue_v2(
        QUEUE_NAME,
        task_id=task_id,
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )
