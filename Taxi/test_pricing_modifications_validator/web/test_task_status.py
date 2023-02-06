# flake8: noqa
import pytest

from test_pricing_modifications_validator.plugins.mock_pricing_admin import (
    mock_pricing_admin,
)


@pytest.mark.parametrize(
    'task_id, expected_finished, expected_total',
    [(1, 0, 2), (2, 2, 3), (3, 2, 2)],
)
@pytest.mark.pgsql('pricing_modifications_validator', files=['state.sql'])
async def test_task_status(
        web_app_client, task_id, expected_finished, expected_total,
):
    query = {'id': task_id}
    response = await web_app_client.get('/v1/task_status', params=query)
    assert response.status == 200
    result = await response.json()
    assert result['finished'] == expected_finished
    assert result['total'] == expected_total
