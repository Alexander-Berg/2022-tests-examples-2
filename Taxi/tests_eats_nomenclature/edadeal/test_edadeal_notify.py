import datetime as dt

import pytest

TEST_EXPORT_TASK_ID = 1
TEST_YT_PATH = '//edadeal_yt/proccessed/bystronom/2019-12-06'


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_data.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data.yaml'],
)
async def test_stq_added(
        taxi_eats_nomenclature,
        testpoint,
        stq,
        yt_apply,
        get_edadeal_export_task,
        get_edadeal_import_task,
):
    export_task = get_edadeal_export_task(export_task_id=TEST_EXPORT_TASK_ID)
    assert export_task['processed'] is False

    request = {
        'brand_id': export_task['brand_id'],
        'retailer_id': f'eda_{export_task["export_retailer_name"]}',
        'timestamp': f'{dt.datetime.utcnow().isoformat("T")}Z',
        's3_path': export_task['s3_export_path'],
        'yt_path': TEST_YT_PATH,
    }
    response = await taxi_eats_nomenclature.post(
        '/v1/edadeal/products/notify_new_data', json=request,
    )
    assert response.status == 204

    export_task = get_edadeal_export_task(export_task_id=TEST_EXPORT_TASK_ID)
    assert export_task['processed'] is True

    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['id']
    assert tag_import_task['yt_path'] == TEST_YT_PATH
    sku_import_task = get_edadeal_import_task(
        task_type='sku', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert sku_import_task['id']
    assert sku_import_task['yt_path'] == TEST_YT_PATH

    assert stq.eats_nomenclature_edadeal_tags_processing.times_called == 1
    tag_queue_next_call = (
        stq.eats_nomenclature_edadeal_tags_processing.next_call()
    )
    assert (
        tag_queue_next_call['queue']
        == 'eats_nomenclature_edadeal_tags_processing'
    )
    assert (
        tag_queue_next_call['id'] == f'tags_processing_{tag_import_task["id"]}'
    )
    assert (
        tag_queue_next_call['kwargs']['import_task_id']
        == tag_import_task['id']
    )

    assert stq.eats_nomenclature_edadeal_skus_processing.times_called == 1
    sku_queue_next_call = (
        stq.eats_nomenclature_edadeal_skus_processing.next_call()
    )
    assert (
        sku_queue_next_call['queue']
        == 'eats_nomenclature_edadeal_skus_processing'
    )
    assert (
        sku_queue_next_call['id'] == f'skus_processing_{sku_import_task["id"]}'
    )
    assert (
        sku_queue_next_call['kwargs']['import_task_id']
        == sku_import_task['id']
    )
