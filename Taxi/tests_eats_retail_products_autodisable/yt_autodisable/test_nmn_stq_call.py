# pylint: disable=import-only-modules
from math import ceil

import pytest

from tests_eats_retail_products_autodisable.yt_autodisable import consts


PERIODIC_NAME = 'yt-disabled-products-sync'
MOCK_NOW = '2021-09-20T15:00:00+03:00'
UNAVAILABLE_UNTIL_IN_FUTURE_1_UTC = '2021-09-20T13:00:00+00:00'
UNAVAILABLE_UNTIL_IN_FUTURE_2_UTC = '2021-09-20T14:00:00+00:00'
ORIGIN_ID_1 = 'item_origin_1'
ORIGIN_ID_2 = 'item_origin_2'
ORIGIN_ID_3 = 'item_origin_3'
ALGORITHM_NAME_ML = 'ml'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.yt(
    schemas=['yt_disable_schema.yaml'],
    static_table_data=['yt_disable_data.yaml'],
)
async def test_put_disable_info_into_nmn_stq(
        set_periodic_config,
        taxi_eats_retail_products_autodisable,
        testpoint,
        yt_apply,
        stq,
):
    set_periodic_config(
        enabled_place_ids=[consts.PLACE_ID_1],
        enabled_algorithms=[
            consts.ALGORITHM_NAME_THRESHOLD,
            ALGORITHM_NAME_ML,
        ],
    )

    @testpoint('yt-disabled-products-sync-finished')
    def periodic_end_run(param):
        pass

    await taxi_eats_retail_products_autodisable.run_distlock_task(
        PERIODIC_NAME,
    )
    assert periodic_end_run.times_called == 1

    assert stq.eats_nomenclature_autodisable_info_update.times_called == 1

    task_info = stq.eats_nomenclature_autodisable_info_update.next_call()
    assert task_info['kwargs']['place_id'] == consts.PLACE_ID_1

    disable_info_kwargs = task_info['kwargs']['products_info']
    expected_disable_info_kwargs = [
        # 1st item has info only from threshold algorithm
        {
            'force_unavailable_until': UNAVAILABLE_UNTIL_IN_FUTURE_1_UTC,
            'origin_id': ORIGIN_ID_1,
        },
        # 2nd item has info only from ml algorithm
        {
            'force_unavailable_until': UNAVAILABLE_UNTIL_IN_FUTURE_2_UTC,
            'origin_id': ORIGIN_ID_2,
        },
        # 3rd item has info from both algorithms
        # force_unavailable_until will be chosen as max from two algorithms
        {
            'force_unavailable_until': UNAVAILABLE_UNTIL_IN_FUTURE_2_UTC,
            'origin_id': ORIGIN_ID_3,
        },
    ]

    assert (
        sorted(disable_info_kwargs, key=lambda k: k['origin_id'])
        == expected_disable_info_kwargs
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.yt(
    schemas=['yt_disable_schema.yaml'],
    static_table_data=['yt_disable_data_for_batching.yaml'],
)
@pytest.mark.parametrize('stq_info_batch_size', [1, 2, 3])
async def test_batching(
        set_periodic_config,
        taxi_eats_retail_products_autodisable,
        testpoint,
        yt_apply,
        stq,
        # parametrize
        stq_info_batch_size,
):
    set_periodic_config(
        enabled_place_ids=[consts.PLACE_ID_1],
        enabled_algorithms=[
            consts.ALGORITHM_NAME_THRESHOLD,
            ALGORITHM_NAME_ML,
        ],
        nomenclature_update_info_batch_size=stq_info_batch_size,
    )

    @testpoint('yt-disabled-products-sync-finished')
    def periodic_end_run(param):
        pass

    await taxi_eats_retail_products_autodisable.run_distlock_task(
        PERIODIC_NAME,
    )
    assert periodic_end_run.times_called == 1

    expected_batches_number = ceil(3 / stq_info_batch_size)
    assert (
        stq.eats_nomenclature_autodisable_info_update.times_called
        == expected_batches_number
    )

    expected_kwargs_flattened = [
        {
            'force_unavailable_until': UNAVAILABLE_UNTIL_IN_FUTURE_1_UTC,
            'origin_id': ORIGIN_ID_1,
        },
        {
            'force_unavailable_until': UNAVAILABLE_UNTIL_IN_FUTURE_1_UTC,
            'origin_id': ORIGIN_ID_2,
        },
        {
            'force_unavailable_until': UNAVAILABLE_UNTIL_IN_FUTURE_1_UTC,
            'origin_id': ORIGIN_ID_3,
        },
    ]

    actual_kwargs = []
    expected_kwargs = []
    for batch_number in range(1, expected_batches_number + 1):
        task_info = stq.eats_nomenclature_autodisable_info_update.next_call()

        assert task_info['kwargs']['place_id'] == consts.PLACE_ID_1
        assert task_info['id'] == str(consts.PLACE_ID_1) + '_' + str(
            batch_number,
        )

        disable_info_kwargs = task_info['kwargs']['products_info']
        actual_kwargs.append(
            sorted(disable_info_kwargs, key=lambda k: k['origin_id']),
        )

        expected_kwargs_first_index = (batch_number - 1) * stq_info_batch_size
        expected_kwargs_last_index = min(
            len(expected_kwargs_flattened), batch_number * stq_info_batch_size,
        )
        expected_kwargs.append(
            expected_kwargs_flattened[
                expected_kwargs_first_index:expected_kwargs_last_index
            ],
        )

    assert actual_kwargs == expected_kwargs
