import pytest


@pytest.mark.pgsql('operation_calculations', files=['pg_doxgety.sql'])
async def test_v2_operations_operation_params_get(web_app_client):
    response = await web_app_client.get(
        f'/v1/doxgety/status/', params={'task_id': 'a'},
    )
    assert response.status == 200
