# flake8: noqa
import pytest

from test_pricing_modifications_validator.plugins.mock_pricing_admin import (
    mock_pricing_admin,
)


async def test_unexistent_task(web_app_client):
    query = {'id': 1}
    response = await web_app_client.post('/v1/cancel_task', json=query)
    assert response.status == 404


@pytest.mark.pgsql('pricing_modifications_validator', files=['state.sql'])
@pytest.mark.parametrize('task_id, expected_code', [(1, 200), (3, 409)])
async def test_cancel_task(
        web_app_client, task_id, expected_code, select_named,
):
    query = {'id': task_id}
    response = await web_app_client.post('/v1/cancel_task', json=query)
    assert response.status == expected_code
    if expected_code == 200:
        task_state = select_named(
            f'SELECT task_state FROM db.script_tasks WHERE id={task_id}',
        )[0]['task_state']
        assert task_state == 'Terminated'
        checks = select_named(
            f'SELECT task_state FROM db.checks WHERE script_id={task_id}',
        )
        assert checks
        assert all(check['task_state'] == 'Terminated' for check in checks)
