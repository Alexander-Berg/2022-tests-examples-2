import pytest


@pytest.mark.parametrize('batch_size', [1, 1000])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_marking_type_merging(
        taxi_config,
        pgsql,
        brand_task_enqueue,
        # parametrize params
        batch_size,
):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_PROCESSING': {
                '__default__': {
                    'insert_batch_size': 1000,
                    'lookup_batch_size': 1000,
                },
                'marking_type_merger': {
                    'insert_batch_size': batch_size,
                    'lookup_batch_size': batch_size,
                },
            },
        },
    )
    # check current data
    assert _get_marking_types(pgsql) == ['default', 'tobacco']
    # upload new nomenclature
    await brand_task_enqueue()
    # check merged data
    assert _get_marking_types(pgsql) == ['default', 'tobacco', 'wine']


def _get_marking_types(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """select value
        from eats_nomenclature.marking_types
        order by value""",
    )
    return [value[0] for value in list(cursor)]
