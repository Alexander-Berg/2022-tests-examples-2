import pytest


TEST_ACTIONS = ['set_actual_commit_hash', 'save_value']


@pytest.mark.config(AUDIT_RELEVANT_ACTIONS={'relevant_actions': TEST_ACTIONS})
async def test_relevant_actions(web_app_client):

    response = await web_app_client.get('/v1/client/relevant_actions/')
    assert response.status == 200
    content = await response.json()
    assert content['actions'] == TEST_ACTIONS
