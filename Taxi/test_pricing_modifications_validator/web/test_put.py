# flake8: noqa
# pylint: disable=redefined-outer-name
import pytest

from test_pricing_modifications_validator.plugins.mock_pricing_admin import (
    mock_pricing_admin,
)


@pytest.fixture
def stq_client_patched(patch):
    @patch('taxi.stq.client.put')
    async def stq_client_put(
            queue, eta=None, task_id=None, args=None, kwargs=None, loop=None,
    ):
        return

    return stq_client_put


async def test_put(web_app_client, select_named, stq):
    body = {'script': 'some_ast', 'constraints': []}
    response = await web_app_client.post('/v1/add_task', json=body)
    assert response.status == 200
    response_data = await response.json()
    data = select_named(
        f'SELECT script_body FROM db.script_tasks WHERE id={response_data["id"]}',
    )
    assert data[0]['script_body'] == 'some_ast'
