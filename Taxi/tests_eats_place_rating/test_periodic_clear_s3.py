import pytest


@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_feedback_reports.sql',),
)
async def test_check_deleting_files(
        taxi_eats_place_rating, taxi_eats_place_rating_monitor,
):

    await taxi_eats_place_rating.run_periodic_task('clear-s3-periodic')
    metrics = await taxi_eats_place_rating_monitor.get_metrics()
    assert metrics['clear-s3']['try_delete_jsons'] == 2
    assert metrics['clear-s3']['try_delete_tables'] == 2

    # файлы удалены


#    s3_data = mds_s3_storage.get_object('partner_1/uuid1.json').data
#    assert not s3_data
#    s3_data = mds_s3_storage.get_object('partner_1/uuid1.csv').data
#    assert not s3_data
#    s3_data = mds_s3_storage.get_object('partner_4/uuid4.json').data
#    assert not s3_data

#    # файл задачи с статусом new не удален
#    s3_data = mds_s3_storage.get_object('partner_2/uuid2.json').data
#    assert s3_data
#    # файл таблицы задачи с статусом table_created не удален
#    s3_data = mds_s3_storage.get_object('partner_4/uuid4.csv').data
#    assert s3_data
