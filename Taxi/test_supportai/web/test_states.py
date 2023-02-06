import json

import pytest

from supportai import models as db_models
from supportai.common import state as state_module

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai', files=['states.sql']),
]


async def test_state_clone(web_app_client, web_context):

    response = await web_app_client.post(
        '/supportai/v1/states/clone?project_slug=sample_project',
        json={
            'chat_id': '1',
            'new_chat_id': '2',
            'iteration': 1,
            'graph_positions_stack': ['1', '2', '3'],
        },
    )

    assert response.status == 200

    async with web_context.pg.master_pool.acquire() as conn:
        state_data = await db_models.State.select_by_project_and_chat(
            web_context, conn, chat_id='2', project_id='sample_project',
        )

    state = state_module.State.from_dict(json.loads(state_data.state))

    assert len(state.get_feature_layers()) == 1
    assert state.get_positions() == []  # TODO: fix to new position way
