import pytest

CRM_EFFICIENCY_SETTINGS = {
    'NirvanaSettings': {
        'instance_id': 'a12d3940-1bcd-424b-9a57-b3b02762c493',
        'workflow_id': '1363da95-a6cc-45bb-ae7b-643ed902812f',
        'workflow_timeout_in_seconds': 86400,
        'workflow_retry_period_in_seconds': 60,
    },
}


@pytest.mark.config(CRM_EFFICIENCY_SETTINGS=CRM_EFFICIENCY_SETTINGS)
async def test_nirvana_run(web_app_client, stq):
    response = await web_app_client.post(
        '/v1/internal/nirvana/run',
        json={
            'task_id': 'task_id',
            'instance_id': 'inst_id1',
            'target_workflow_id': 'target_id1',
            'global_params': [
                {'parameter': 'param1', 'value': 'value1'},
                {'parameter': 'param_to_erase'},
            ],
        },
    )
    assert response.status == 200
    data = await response.json()
    assert data == {'task_id': 'task_id'}

    assert stq.crm_efficiency_run_spark.times_called == 1
