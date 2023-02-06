import pytest


@pytest.mark.parametrize(
    'task_name, is_enabled',
    [
        ('non-exists', True),
        ('service-stuff-some_task', True),
        ('py2_task', False),
        ('taxi_corp-stuff-send_csv_order_report', True),
    ],
)
async def test_is_enabled(web_app_client, task_name, is_enabled):
    response = await web_app_client.get(f'/v1/task/{task_name}/is-enabled/')
    assert response.status == 200
    result = await response.json()
    assert result['is_enabled'] == is_enabled, task_name
