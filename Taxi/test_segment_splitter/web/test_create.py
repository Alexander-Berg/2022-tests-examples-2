import pytest

SEGMENT_SPLITTER_SETTINGS = {
    'instance_id': 'a12d39401bcd424b9a57b3b02762c493',
    'workflow_id': 'a12d39401bcd424b9a57b3b02762c493',
    'workflow_timeout_in_seconds': 86400,
    'workflow_retry_period_in_seconds': 60,
}


@pytest.mark.config(SEGMENT_SPLITTER_SETTINGS=SEGMENT_SPLITTER_SETTINGS)
async def test_create(web_app_client):
    id_ = 'a12d39401bcd424b9a57b3b02762c493'
    response = await web_app_client.post(
        '/v1/splitting/create',
        json={
            'id': id_,
            'segment_path': 'path',
            'output_path': 'path',
            'spark_cluster': 'cluster',
            'groups': {'1': 0.1, '0': 0.9},
            'split_col_name': 'splitter_col',
            'sub_segment_id': 'group_name',
            'unique_entity_attr': 'user_id',
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'id': id_, 'status': 'OK'}
