import pytest


@pytest.mark.config(
    OPERATION_CALCULATIONS_DOXGETY_SETTINGS={
        'money_multiplier': 0.8,
        'algorithms': [
            {'name': 'DoXGetY', 'instance_id': 'a', 'workflow_id': 'b'},
        ],
    },
)
async def test_v2_operations_operation_params_get(web_app_client):
    response = await web_app_client.get(f'/v1/doxgety/algorithms/')
    assert response.status == 200
    res = await response.json()
    assert res == [{'name': 'DoXGetY'}]
