import typing as tp

import pytest

from supportai_lib.generated import models as api_module

from supportai.common import agent as agent_module


async def _call_agent(
        web_context,
        agent: agent_module.Agent,
        request: dict,
        api_flags: tp.Optional[agent_module.ApiFlags] = None,
) -> api_module.SupportResponse:
    data = api_module.SupportRequest.deserialize(request)
    state = await agent.init_state_from_db(
        context=web_context, request_data=data,
    )
    return await agent(
        context=web_context,
        request_data=data,
        state=state,
        api_flags=api_flags,
    )


@pytest.mark.parametrize(
    'config_path', ['configuration_graph_request_features.json'],
)
async def test_graph_requested_features(
        create_agent, web_context, mockserver, config_path,
):
    project_id = 'test_project'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': 'order_status',
            'probabilities': [
                {'topic_name': 'order_status', 'probability': 1.0},
            ],
        },
    )

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [
                    {
                        'author': 'user',
                        'text': 'Добрый день! Где мой заказ 9768576',
                    },
                ],
            },
            'features': [{'key': 'iteration_number', 'value': 1}],
            'chat_id': '123',
        },
        api_flags=agent_module.ApiFlags(ask_features=True),
    )

    assert response.features is not None
    assert response.features.most_probable_topic == 'order_status'
    assert response.reply is None
    assert response.close is None
    assert response.requested_features.features[0].feature == 'order_id'
    assert response.graph_positions_stack.positions_stack == ['XXXX1']

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [
                    {
                        'author': 'user',
                        'text': 'Добрый день! Где мой заказ 9768576',
                    },
                ],
            },
            'features': [
                {'key': 'iteration_number', 'value': 1},
                {'key': 'order_id', 'value': '9768576'},
            ],
            'chat_id': '123',
        },
        api_flags=agent_module.ApiFlags(ask_features=True),
    )

    assert response.reply is not None
    assert response.reply.texts[0] == 'Cтатус заказа ГОТОВ'
