import datetime

import pytest

NOW = datetime.datetime(2020, 11, 10, 10, 3, 10)


@pytest.mark.now(NOW.isoformat())
async def test_etl_process_control_updated(web_app_client, db):
    entity_name = 'atlas.ods_order'
    increment_mark = NOW - datetime.timedelta(minutes=15, seconds=34)
    load_finished = NOW - datetime.timedelta(minutes=13, seconds=23)

    response = await web_app_client.post(
        '/v1/etl-process/increment/update-meta',
        json={
            'entity_name': entity_name,
            'last_load_increment_mark': increment_mark.isoformat(),
            'last_load_finished_at': load_finished.isoformat(),
        },
    )
    assert response.status == 201

    result = await db.atlas_etl_control.find_one({'entity_name': entity_name})
    assert result is not None
    assert result['last_load_increment_mark'] == increment_mark
    assert result['last_load_finished_at'] == load_finished
    assert result['updated_at'] == NOW

    result_hist = await db.atlas_etl_control_history.find_one(
        {'entity_name': entity_name, 'last_load_finished_at': load_finished},
    )
    assert result_hist is not None
    assert result_hist['last_load_increment_mark'] == increment_mark
    assert result_hist['created_at'] == NOW
