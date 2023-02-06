import datetime as dt

import pytest

MOCK_NOW = dt.datetime(2021, 3, 2, 12)


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize('should_call_edadeal_stq', [True, False])
@pytest.mark.parametrize('should_call_fts_stq', [True, False])
@pytest.mark.parametrize('should_call_cc_stq', [True, False])
@pytest.mark.parametrize('should_log_to_lb', [True, False])
@pytest.mark.parametrize('delay', [0, 100])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'fill_additional_data.sql',
    ],
)
async def test_stq(
        testpoint,
        stq_runner,
        stq,
        update_taxi_config,
        should_call_edadeal_stq,
        should_call_fts_stq,
        should_call_cc_stq,
        should_log_to_lb,
        delay,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_ASSORTMENT_ACTIVATION_NOTIFICATION_SETTINGS',
        {
            'per_component_additional_settings': {
                'yt_new_assortment': {
                    'is_enabled': should_log_to_lb,
                    'additional_delay_in_seconds': delay,
                },
                'stq_edadeal_s3_uploader': {
                    'is_enabled': should_call_edadeal_stq,
                    'additional_delay_in_seconds': delay,
                },
                'stq_eats_full_text_search_indexer_update_retail_place': {
                    'is_enabled': should_call_fts_stq,
                    'additional_delay_in_seconds': delay,
                },
                'stq_update_custom_categories_history': {
                    'is_enabled': should_call_cc_stq,
                    'additional_delay_in_seconds': delay,
                },
            },
        },
    )
    place_ids = [1, 2, 3]
    brand_id = 777

    logged_place_ids = []

    @testpoint('yt-logger-new-assortment')
    def yt_logger(data):
        del data['timestamp_raw']
        assert data['timestamp'] == MOCK_NOW.strftime('%Y-%m-%dT%H:%M:%S')
        logged_place_ids.append(int(data['place_id']))

    await stq_runner.eats_nomenclature_assortment_activation_notifier.call(
        task_id=str(brand_id),
        args=[],
        kwargs={'place_ids': place_ids, 'brand_id': brand_id},
        expect_fail=False,
    )

    assert yt_logger.times_called == (
        len(place_ids) if should_log_to_lb else 0
    )
    assert sorted(logged_place_ids) == (place_ids if should_log_to_lb else [])

    now = dt.datetime.fromisoformat(MOCK_NOW.isoformat())
    if should_call_edadeal_stq:
        assert stq.eats_nomenclature_edadeal_s3_uploader.times_called == 1

        task_info = stq.eats_nomenclature_edadeal_s3_uploader.next_call()
        assert (task_info['eta'] - now).total_seconds() == delay
    else:
        assert stq.eats_nomenclature_edadeal_s3_uploader.times_called == 0

    if should_call_cc_stq:
        assert (
            stq.eats_nomenclature_update_custom_categories_history.times_called
            == len(place_ids)
        )

        task_info = (
            stq.eats_nomenclature_update_custom_categories_history.next_call()
        )
        assert (task_info['eta'] - now).total_seconds() == delay
    else:
        assert (
            stq.eats_nomenclature_update_custom_categories_history.times_called
            == 0
        )

    if should_call_fts_stq:
        assert (
            stq.eats_full_text_search_indexer_update_retail_place.times_called
            == len(place_ids)
        )

        task_info = (
            stq.eats_full_text_search_indexer_update_retail_place.next_call()
        )
        assert (task_info['eta'] - now).total_seconds() == delay
    else:
        assert (
            stq.eats_full_text_search_indexer_update_retail_place.times_called
            == 0
        )
