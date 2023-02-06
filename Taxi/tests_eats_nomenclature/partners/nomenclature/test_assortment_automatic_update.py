import datetime as dt

import pytest

TEST_DATETIME = '2021-06-02T14:35:44+03:00'


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_process_nomenclature_from_s3(
        taxi_config,
        upload_verified_nomenclature_to_s3,
        insert_enrichment_status,
        get_in_progress_assortment,
        stq_runner,
        stq,
        mocked_time,
        get_uploaded_file_path,
):
    assortment_enrichment_timeout = 90
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_PROCESSOR_TIMEOUTS': {
                'assortment_enrichment_timeout_in_min': (
                    assortment_enrichment_timeout
                ),
            },
        },
    )

    place_id = '1'

    await upload_verified_nomenclature_to_s3(
        place_id, file_datetime=TEST_DATETIME,
    )

    s3_file_path = get_uploaded_file_path(place_id)
    await stq_runner.eats_nomenclature_transform_assortment.call(
        task_id='test_task',
        args=[],
        kwargs={'assortment_s3_url': s3_file_path, 'brand_id': 777},
    )
    assert stq.eats_nomenclature_add_custom_assortment.times_called == 1

    in_progress_assortment_id = get_in_progress_assortment(place_id)
    insert_enrichment_status(in_progress_assortment_id, dt.datetime.now())
    outdated_assortment_id = get_in_progress_assortment(place_id)
    insert_enrichment_status(
        outdated_assortment_id,
        mocked_time.now()
        - dt.timedelta(minutes=assortment_enrichment_timeout + 1),
    )

    await stq_runner.eats_nomenclature_transform_assortment.call(
        task_id='tests_task_2',
        args=[],
        kwargs={'assortment_s3_url': s3_file_path, 'brand_id': 777},
    )
    assert stq.eats_nomenclature_add_custom_assortment.times_called == 2


@pytest.mark.parametrize('merge_non_assortment_entities', [True, False])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_update_brand_assortments(
        taxi_config,
        brand_task_enqueue,
        load_json,
        insert_enrichment_status,
        get_in_progress_assortment,
        stq_runner,
        stq,
        mocked_time,
        # parametrize
        merge_non_assortment_entities,
):
    assortment_enrichment_timeout = 90
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_PROCESSOR_TIMEOUTS': {
                'assortment_enrichment_timeout_in_min': (
                    assortment_enrichment_timeout
                ),
            },
            'EATS_NOMENCLATURE_TEMPORARY_CONFIGS': {
                'should_merge_nmn_on_brand_sync': (
                    merge_non_assortment_entities
                ),
            },
        },
    )

    data_to_upload = load_json('s3_brand_nomenclature.json')

    place_id = '1'

    await brand_task_enqueue(
        '1', brand_nomenclature=data_to_upload, file_datetime=TEST_DATETIME,
    )

    trait_id = 1
    in_progress_assortment_id = get_in_progress_assortment(
        place_id, trait_id=trait_id,
    )
    insert_enrichment_status(in_progress_assortment_id, dt.datetime.now())
    outdated_assortment_id = get_in_progress_assortment(
        place_id, trait_id=trait_id,
    )
    insert_enrichment_status(
        outdated_assortment_id,
        mocked_time.now()
        - dt.timedelta(minutes=assortment_enrichment_timeout + 1),
    )

    await stq_runner.eats_nomenclature_update_brand_assortments.call(
        task_id='test_task',
        args=[],
        kwargs={'brand_id': 777, 'trait_id': trait_id},
    )
    assert stq.eats_nomenclature_transform_assortment.times_called == 1

    file_path = 'old_nomenclature/brand_nomenclature.json'
    task_info = stq.eats_nomenclature_transform_assortment.next_call()
    assert task_info['kwargs']['brand_id'] == 777
    assert task_info['kwargs']['trait_id'] == trait_id
    assert (
        task_info['kwargs']['should_merge_non_assortment_entities']
        == merge_non_assortment_entities
    )
    assert task_info['id'] == f'{file_path}_{trait_id}'


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_in_progress_assortments(
        brand_task_enqueue,
        load_json,
        insert_enrichment_status,
        get_in_progress_assortment,
        stq_runner,
        stq,
):

    data_to_upload = load_json('s3_brand_nomenclature.json')

    place_id = '1'

    data_to_upload['place_ids'] = [place_id]

    await brand_task_enqueue(
        '1', brand_nomenclature=data_to_upload, file_datetime=TEST_DATETIME,
    )

    trait_id = 1
    in_progress_assortment_id = get_in_progress_assortment(
        place_id, trait_id=trait_id,
    )
    insert_enrichment_status(in_progress_assortment_id, dt.datetime.now())

    await stq_runner.eats_nomenclature_update_brand_assortments.call(
        task_id='test_task',
        args=[],
        kwargs={'brand_id': 777, 'trait_id': trait_id},
    )
    assert stq.eats_nomenclature_transform_assortment.times_called == 0
    assert stq.eats_nomenclature_update_brand_assortments.times_called == 1
