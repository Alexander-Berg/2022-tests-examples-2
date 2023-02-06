import pytest


@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS={
        'algorithm1': {
            'description': 'test description',
            'metric_name': 'test_metric_name',
        },
        'kt2_smart_script': {
            'description': 'kt2_smart_script desc',
            'metric_name': 'kt2_smart_script metric_name',
        },
    },
)
async def test_get_algorithms(web_app_client):
    response = await web_app_client.get('/v1/algorithms')
    assert response.status == 200
    content = await response.json()
    assert content == [
        {
            'name': 'algorithm1',
            'ignore_companies': False,
            'metric_name': 'test_metric_name',
            'description': 'test description',
        },
        {
            'name': 'kt2_smart_script',
            'ignore_companies': True,
            'metric_name': 'kt2_smart_script metric_name',
            'description': 'kt2_smart_script desc',
        },
    ]
