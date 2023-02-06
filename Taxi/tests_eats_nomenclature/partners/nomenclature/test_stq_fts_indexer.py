import pytest


@pytest.mark.parametrize(
    'stq_is_enabled, delay_in_min',
    [
        pytest.param(True, 10, id='enabled'),
        pytest.param(False, 10, id='disabled'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_stq_fts_indexer_task_created(
        stq,
        taxi_config,
        stq_runner,
        update_taxi_config,
        stq_is_enabled,
        delay_in_min,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_ASSORTMENT_ACTIVATION_NOTIFICATION_SETTINGS',
        {
            'per_component_additional_settings': {
                '__default__': {
                    'is_enabled': True,
                    'additional_delay_in_seconds': 0,
                },
                'stq_eats_full_text_search_indexer_update_retail_place': {
                    'is_enabled': stq_is_enabled,
                    'additional_delay_in_seconds': delay_in_min,
                },
            },
        },
    )

    place_id = 1
    brand_id = 777

    await stq_runner.eats_nomenclature_assortment_activation_notifier.call(
        task_id=str(brand_id),
        args=[],
        kwargs={'place_ids': [place_id], 'brand_id': brand_id},
        expect_fail=False,
    )

    if stq_is_enabled:
        assert (
            stq.eats_full_text_search_indexer_update_retail_place.times_called
            == 1
        )
        task_info = (
            stq.eats_full_text_search_indexer_update_retail_place.next_call()
        )
        assert task_info['kwargs']['place_slug'] == str(place_id)
    else:
        assert (
            stq.eats_full_text_search_indexer_update_retail_place.times_called
            == 0
        )
