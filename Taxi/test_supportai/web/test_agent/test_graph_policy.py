from typing import Callable

import pytest

from supportai.common import configuration
from supportai.common import feature as feature_module
from supportai.common import policy_graph as policy_graph_module
from supportai.common import state as state_module
from supportai.common import tracker as tracker_module


@pytest.fixture(name='create_graph_policy')
def _create_graph_policy(
        load_json,
) -> Callable[[str], policy_graph_module.PolicyGraph]:
    def policy(config_path: str) -> policy_graph_module.PolicyGraph:
        graph_policy = policy_graph_module.PolicyGraph()
        config = configuration.Configuration.deserialize(
            load_json(config_path),
        )
        graph_policy.load_from_configuration(config.policy_graph, config.flags)
        return graph_policy

    return policy


@pytest.mark.parametrize('config_path', ['configuration_policy_graph.json'])
async def test_graph_policy(web_context, create_graph_policy, config_path):
    policy = create_graph_policy(config_path)
    await policy.prepare()

    state = state_module.State()
    state.push_topic('example_topic')

    tracker = tracker_module.DialogStateTracker(None)

    types_ = ['ChangeStateAction', 'ResponseAction']
    i = 0
    async for iteration in await policy.get_next_action(
            web_context,
            'test',
            'chat_id',
            state,
            tracker,
            [],
            configuration.CoreFlags(),
    ):
        assert types_[i] == iteration.action.ref.__class__.__name__
        i += 1

    assert i == 2


@pytest.mark.parametrize(
    'config_path', ['configuration_policy_graph_with_greeting_and_main.json'],
)  # noqa E501 line too long
async def test_graph_policy_with_groups(
        web_context, create_graph_policy, config_path,
):
    policy = create_graph_policy(config_path)
    await policy.prepare()

    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message', value='тестовый текст',
                ),
            },
        ],
    )
    state.push_topic('example_topic')

    tracker = tracker_module.DialogStateTracker(None)

    types_ = ['ChangeStateAction', 'ResponseAction']
    tags_ = [['first'], ['second']]
    i = 0
    async for iteration in await policy.get_next_action(
            web_context,
            'test',
            'chat_id',
            state,
            tracker,
            [],
            configuration.CoreFlags(),
    ):
        assert types_[i] == iteration.action.ref.__class__.__name__
        assert tags_[i] == iteration.response_tags
        i += 1

    assert i == 2


@pytest.mark.parametrize(
    'config_path', ['configuration_policy_graph_with_main_and_fallback.json'],
)  # noqa E501 line too long
async def test_graph_policy_with_groups_main_and_fallback(
        web_context, create_graph_policy, config_path,
):
    policy = create_graph_policy(config_path)
    await policy.prepare()

    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message', value='тестовый текст',
                ),
            },
        ],
    )
    state.push_topic('example_topic')

    tracker = tracker_module.DialogStateTracker(None)
    i = 0
    async for iteration in await policy.get_next_action(
            web_context,
            'test',
            'chat_id',
            state,
            tracker,
            [],
            configuration.CoreFlags(),
    ):

        action = iteration.action
        assert action.ref.__class__.__name__ == 'ResponseAction'
        i += 1

    assert i == 1
