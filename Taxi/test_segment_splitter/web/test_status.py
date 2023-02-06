import pytest

from segment_splitter import storage


SEGMENT_SPLITTER_SETTINGS = {
    'instance_id': 'a12d39401bcd424b9a57b3b02762c493',
    'workflow_id': 'a12d39401bcd424b9a57b3b02762c493',
    'workflow_timeout_in_seconds': 86400,
    'workflow_retry_period_in_seconds': 60,
}


@pytest.mark.config(SEGMENT_SPLITTER_SETTINGS=SEGMENT_SPLITTER_SETTINGS)
async def test_status(web_context, web_app_client):
    id_ = 'a12d3940-1bcd-424b-9a57-b3b02762c493'
    await web_app_client.post(
        '/v1/splitting/create',
        json={
            'id': id_,
            'segment_path': 'segment_path',
            'output_path': 'output_path',
            'spark_cluster': 'spark_cluster',
            'groups': {'1': 0.1, '0': 0.9},
            'split_col_name': 'splitter_col',
            'sub_segment_id': 'group_name',
            'unique_entity_attr': 'user_id',
        },
    )

    nirvana_db = storage.DbTask(web_context)
    task = await nirvana_db.fetch_by_task(id_)
    task.result = {
        '1': {
            'metric': {
                'is_sign': True,
                'ci_width': 0.1,
                'hash_string': '__campaign_5999__',
            },
        },
    }
    await nirvana_db.update(task)

    response = await web_app_client.get(
        '/v1/splitting/status', params={'id': id_},
    )
    assert response.status == 200
    content = await response.json()

    metrics_result = {
        '1': {
            'metric': {
                'is_colored': True,
                'ci_width': 0.1,
                'salt': '__campaign_5999__',
            },
        },
    }

    assert content == {
        'id': id_.replace('-', ''),
        'segment_path': 'segment_path',
        'output_path': 'output_path',
        'status': 'NEW',
        'metrics_result': metrics_result,
    }
