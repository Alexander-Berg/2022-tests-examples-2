import pytest

from supportai_lib.generated import models as api_module

from supportai import models as db_models
from supportai.common import agent as agent_module
from supportai.common import core_features
from supportai.common import exceptions
from supportai.utils import agent_graph_helper


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai', files=['default.sql']),
]


async def _call_agent(
        web_context, agent: agent_module.Agent, request: dict,
) -> api_module.SupportResponse:
    data = api_module.SupportRequest.deserialize(request)
    state = await agent.init_state_from_db(
        context=web_context, request_data=data,
    )
    return await agent(context=web_context, request_data=data, state=state)


@pytest.mark.parametrize('config_path', ['configuration_graph.json'])
async def test_call_graph_agent(
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
    )

    assert response.features is not None
    assert response.features.most_probable_topic == 'order_status'
    assert response.reply is not None
    assert response.reply.texts[0] == 'Подскажите номер вашего заказа?'
    assert response.close is None
    assert response.tag.add == ['totalchest']

    for feature in response.features.features:
        if feature.key == core_features.STACK_LENGTH:
            assert feature.value == 0
            break
    else:
        assert False
    for feature in response.features.features:
        if feature.key == core_features.PREV_NODE_COUNT:
            assert feature.value == 1
            break
    else:
        assert False
    for feature in response.features.features:
        if feature.key == core_features.CURR_NODE_COUNT:
            assert feature.value == 1
            break
    else:
        assert False


@pytest.mark.parametrize('config_path', ['configuration_graph_condition.json'])
async def test_call_graph_agent_condition(
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
    )

    assert response.features is not None
    assert response.features.most_probable_topic == 'order_status'
    assert response.reply is not None
    assert response.reply.texts[0] == 'Подскажите номер вашего заказа?'
    assert response.close is None

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': '9768576'}]},
            'features': [{'key': 'iteration_number', 'value': 2}],
            'chat_id': '123',
        },
    )

    assert response.reply is not None
    assert response.reply.texts[0] == 'Cтатус заказа ГОТОВ'


@pytest.mark.parametrize(
    'config_path', ['configuration_graph_form_condition.json'],
)
@pytest.mark.parametrize(
    ('text', 'answer'),
    [('+', True), ('+-', False), ('-', False), (':', False)],
)
async def test_call_graph_form_condition(
        create_agent, web_context, mockserver, config_path, text, answer,
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
            'features': [{'key': 'text', 'value': text}],
            'chat_id': '123',
        },
    )

    assert response.features is not None
    assert response.features.most_probable_topic == 'order_status'
    assert response.reply is not None
    if answer:
        assert response.reply.texts[0] == 'answer'
    else:
        assert response.reply.texts[0] == 'not answer'


@pytest.mark.parametrize(
    ('config_path', 'actions_response_status'),
    [
        ('configuration_graph_integration_action_no_fail.json', 200),
        ('configuration_graph_integration_action_no_fail.json', 404),
        ('configuration_graph_integration_action_no_fail.json', 500),
        ('configuration_graph_integration_action.json', 200),
        pytest.param(
            'configuration_graph_integration_action.json',
            404,
            marks=pytest.mark.xfail(
                raises=exceptions.AgentActionException, strict=True,
            ),
        ),
    ],
)
async def test_call_graph_integration_action(
        create_agent,
        web_context,
        mockserver,
        config_path,
        actions_response_status,
):
    @mockserver.json_handler('/supportai-actions/supportai-actions/v1/action')
    async def _(request):
        assert request.json['params'] == [
            {
                'integration_id': 3,
                'parameters': {'promocode_size': 1000, 'mode': 'critical'},
            },
        ]

        if actions_response_status != 200:
            return mockserver.make_response(status=actions_response_status)

        return mockserver.make_response(
            status=200,
            json={
                'state': {
                    'features': [
                        {'key': 'promocode_feature', 'value': '12345'},
                    ],
                },
            },
        )

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
                        'text': 'Заказ очень сильно опаздывает! Ужас!',
                    },
                ],
            },
            'features': [{'key': 'iteration_number', 'value': 1}],
            'chat_id': '123',
        },
    )

    expected_text = (
        'Простите, ваш промокод: 12345'
        if actions_response_status == 200
        else 'Простите, произошел троллинг (экшны упали, хех). Вот ошибка: '
    )

    assert response.features is not None
    assert response.features.most_probable_topic == 'order_status'
    assert response.reply is not None
    assert expected_text in response.reply.texts[0]
    assert response.close is None

    action_error = None
    for feature in response.features.features:
        if feature.key == 'action_error_description':
            action_error = feature.value

    if actions_response_status == 200:
        assert action_error is None
    else:
        assert action_error is not None


@pytest.mark.parametrize('config_path', ['configuration_graph_no_topic.json'])
async def test_call_graph_agent_no_topic(
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
    )

    assert response.features is not None
    assert response.features.most_probable_topic == 'order_status'
    assert response.reply is not None
    assert response.reply.texts[0] == 'Подскажите номер вашего заказа?'
    assert response.close is None


@pytest.mark.parametrize('config_path', ['configuration_market_test.json'])
async def test_call_graph_market_test(
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
            'dialog': {'messages': [{'author': 'user', 'text': '*'}]},
            'features': [{'key': 'iteration_number', 'value': 1}],
            'chat_id': '123',
        },
    )

    assert response.reply is not None
    assert response.reply.texts[0] == 'что то'
    assert response.close is not None


async def test_agent_helper_config(web_context, web_app_client):
    sample_not_empty = {
        'id': '0',
        'topic_id': '1',
        'title': 'Test',
        'nodes': [
            {
                'id': 'XXXX',
                'version': 'SOME',
                'type': 'close',
                'action': {'type': 'close'},
                'meta': {'title': '', 'x': 0.0, 'y': 0.0},
                'tags': [],
            },
        ],
        'links': [{'from_id': '', 'to_id': 'XXXX', 'meta': {'path': []}}],
    }

    response = await web_app_client.post(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka', json=sample_not_empty,
    )

    assert response.status == 200

    async with web_context.pg.slave_pool.acquire() as conn:
        version = await db_models.Version.select_draft_by_project_slug(
            web_context, conn, 'ya_lavka',
        )

        graphs = await db_models.ScenarioGraph.select_by_version_id(
            web_context, conn, version.id,
        )

        assert len(graphs) == 1

        nodes = await db_models.ScenarioGraphNode.select_by_scenario_ids(
            web_context, conn, [g.id for g in graphs],
        )

        assert len(nodes) == 1

        actions = await db_models.ScenarioGraphAction.select_by_scenario_ids(
            web_context, conn, [g.id for g in graphs],
        )
        assert len(actions) == 1

        links = await db_models.ScenarioGraphLink.select_by_scenario_ids(
            web_context, conn, [g.id for g in graphs],
        )

        assert len(links) == 1

    graph = await agent_graph_helper.compile_policy_graph(
        web_context, web_context.pg.slave_pool, version,
    )

    assert len(graph.main.graph) == 1
    assert len(graph.main.nodes) == 1


@pytest.mark.parametrize(
    'config_path', ['configuration_graph_general_loop.json'],
)
async def test_general_loop(
        create_agent, web_context, mockserver, config_path,
):
    project_id = 'test_project'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={},
    )
    agent._policy_graph.max_loops = 1  # pylint: disable=W0212

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': '*'}]},
            'features': [{'key': 'iteration_number', 'value': 1}],
            'chat_id': '123',
        },
    )

    assert response.reply.texts[0] == 'general answer'

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': '*'}]},
            'features': [{'key': 'iteration_number', 'value': 1}],
            'chat_id': '123',
        },
    )

    assert not response.reply


@pytest.mark.parametrize(
    'config_path', ['configuration_graph_general_loop.json'],
)
async def test_response_loop(
        create_agent, web_context, mockserver, config_path,
):
    project_id = 'test_project'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={},
    )

    for phrase in ('general answer', 'answer 1', 'answer 2', 'answer 3'):
        response = await _call_agent(
            web_context,
            agent,
            {
                'dialog': {'messages': [{'author': 'user', 'text': '*'}]},
                'features': [{'key': 'iteration_number', 'value': 1}],
                'chat_id': '123',
            },
        )
        assert response.reply.texts[0] == phrase


@pytest.mark.parametrize(
    'config_path', ['configuration_graph_general_loop.json'],
)
async def test_response_loop_failure(
        create_agent, web_context, mockserver, config_path,
):
    project_id = 'test_project'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={},
    )

    for phrase in (
            'general answer',
            'answer 1',
            'answer 2',
            'answer 3',
            'ERROR',
    ):
        response = await _call_agent(
            web_context,
            agent,
            {
                'dialog': {'messages': [{'author': 'user', 'text': '*'}]},
                'features': [{'key': 'iteration_number', 'value': 1}],
                'chat_id': '123',
            },
        )

        if phrase != 'ERROR':
            assert response.reply.texts[0] == phrase
        else:
            assert not response.reply


@pytest.mark.parametrize('config_path', ['configuration_graph_switch.json'])
async def test_graph_switch(
        create_agent, web_context, mockserver, config_path,
):
    project_id = 'test_project'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': 'hello',
            'probabilities': [{'topic_name': 'hello', 'probability': 1.0}],
        },
    )

    for i, phrase in enumerate(('Привет', 'Статус')):
        response = await _call_agent(
            web_context,
            agent,
            {
                'dialog': {'messages': [{'author': 'user', 'text': phrase}]},
                'features': [{'key': 'iteration_number', 'value': i}],
                'chat_id': '123',
            },
        )

        assert response.reply.texts[0] == phrase


@pytest.mark.parametrize(
    'config_path', ['configuration_graph_two_policies.json'],
)
async def test_response_scenario_old_fallback(
        create_agent, web_context, mockserver, config_path,
):
    project_id = 'test_project'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': '',
            'probabilities': [{'topic_name': '', 'probability': 1.0}],
        },
    )

    for i, phrase in enumerate(('graph', 'fallback')):
        response = await _call_agent(
            web_context,
            agent,
            {
                'dialog': {'messages': [{'author': 'user', 'text': '*'}]},
                'features': [{'key': 'iteration_number', 'value': 1 + i}],
                'chat_id': '1234',
            },
        )

        assert response.reply.texts[0] == phrase


@pytest.mark.parametrize('client_answer', ['iOS', 'Не знаю'])
async def test_response_scenario_with_buttons(
        create_agent, web_context, mockserver, client_answer,
):
    project_id = 'test_project'

    agent = await create_agent(
        namespace=project_id,
        config_path='configuration_graph_with_buttons.json',
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
                        'text': 'Как установить ваше приложение?',
                    },
                ],
            },
            'features': [{'key': 'iteration_number', 'value': 1}],
            'chat_id': '123',
        },
    )

    assert response.reply.texts[0] == 'Подскажите вашу операционную систему?'
    assert len(response.buttons_block.buttons) == 2
    assert 'Android' in [
        button.text for button in response.buttons_block.buttons
    ]
    assert 'iOS' in [button.text for button in response.buttons_block.buttons]

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [{'author': 'user', 'text': client_answer}],
            },
            'features': [{'key': 'iteration_number', 'value': 1}],
            'chat_id': '123',
        },
    )

    if client_answer == 'iOS':
        assert response.reply.texts[0] == 'Cкачайте его в приложении AppStore'
    else:
        assert response.reply.texts[0] == 'Я вас не понял'


async def test_response_scenario_buttons_array(create_agent, web_context):
    project_id = 'test_project'

    agent = await create_agent(
        namespace=project_id,
        config_path='configuration_graph_with_buttons_array.json',
        supportai_models_response={
            'most_probable_topic': 'order_status',
            'probabilities': [
                {'topic_name': 'order_status', 'probability': 1.0},
            ],
        },
    )

    orders = ['order_1', 'order_2', 'order_3']

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Подскажите статус заказа?'},
                ],
            },
            'features': [
                {'key': 'iteration_number', 'value': 1},
                {'key': 'orders', 'value': orders},
            ],
            'chat_id': '123',
        },
    )

    assert response.reply.texts[0] == 'Выберите заказ кнопкой:'
    assert len(response.buttons_block.buttons) == 3

    buttons = [button.text for button in response.buttons_block.buttons]
    for order in orders:
        assert f'заказ {order}' in buttons

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [{'author': 'user', 'text': 'заказ order_2'}],
            },
            'features': [{'key': 'iteration_number', 'value': 1}],
            'chat_id': '123',
        },
    )

    assert response.reply.texts[0] == 'Вы выбрали заказ: заказ order_2'


@pytest.mark.parametrize(
    'config_path', ['configuration_select_scenario_node.json'],
)
async def test_select_scenarios_node(
        create_agent, web_context, mockserver, config_path,
):
    project_id = 'test_project'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': '',
            'probabilities': [{'topic_name': '', 'probability': 1.0}],
        },
    )

    for i, phrase in enumerate(('внутри сценария', 'Cтатус заказа ГОТОВ')):
        response = await _call_agent(
            web_context,
            agent,
            {
                'dialog': {'messages': [{'author': 'user', 'text': '*'}]},
                'features': [{'key': 'iteration_number', 'value': 1 + i}],
                'chat_id': '1234',
            },
        )

        assert response.reply.texts[0] == phrase


@pytest.mark.parametrize(
    'config_path', ['configuration_select_scenario_node_final_close.json'],
)
async def test_select_scenarios_node_final_node(
        create_agent, web_context, mockserver, config_path,
):
    project_id = 'test_project'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': '',
            'probabilities': [{'topic_name': '', 'probability': 1.0}],
        },
    )

    for i, phrase in enumerate(('внутри сценария',)):
        response = await _call_agent(
            web_context,
            agent,
            {
                'dialog': {'messages': [{'author': 'user', 'text': '*'}]},
                'features': [{'key': 'iteration_number', 'value': 1 + i}],
                'chat_id': '1234',
            },
        )

        assert response.close is not None
        assert response.reply.texts[0] == phrase


@pytest.mark.parametrize('config_path', ['configuration_node_counter.json'])
async def test_node_counter(
        create_agent, web_context, mockserver, config_path,
):
    project_id = 'test_project'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': '',
            'probabilities': [{'topic_name': '', 'probability': 1.0}],
        },
    )

    for i, phrase in enumerate(('repeat', 'repeat', 'repeat', 'ГОТОВ')):
        response = await _call_agent(
            web_context,
            agent,
            {
                'dialog': {'messages': [{'author': 'user', 'text': '*'}]},
                'features': [{'key': 'iteration_number', 'value': 1 + i}],
                'chat_id': '1234',
            },
        )

        assert response.reply.texts[0] == phrase


@pytest.mark.parametrize('config_path', ['configuration_switch.json'])
async def test_node_switch(create_agent, web_context, mockserver, config_path):
    project_id = 'test_project'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': '',
            'probabilities': [{'topic_name': '', 'probability': 1.0}],
        },
    )

    requests = ['test', 'no']

    for i, phrase in enumerate(('TEST', 'ГОТОВ')):
        response = await _call_agent(
            web_context,
            agent,
            {
                'dialog': {
                    'messages': [{'author': 'user', 'text': requests[i]}],
                },
                'features': [{'key': 'iteration_number', 'value': 1 + i}],
                'chat_id': '1234',
            },
        )

        assert response.reply.texts[0] == phrase


@pytest.mark.parametrize('config_path', ['configuration_operator.json'])
async def test_call_graph_operator(
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
            'dialog': {'messages': [{'author': 'user', 'text': 'totalchest'}]},
            'features': [{'key': 'iteration_number', 'value': 1}],
            'chat_id': '123',
        },
    )

    assert response.reply is None
    assert response.forward.line == 'line_1'
    assert response.operator is not None


@pytest.mark.parametrize(
    'config_path', ['configuration_response_fallback.json'],
)
async def test_call_graph_response_fallback(
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

    for response_text in ['0', '1', '2', '1', 'end']:
        response = await _call_agent(
            web_context,
            agent,
            {
                'dialog': {'messages': [{'author': 'user', 'text': 'repeat'}]},
                'features': [{'key': 'iteration_number', 'value': 1}],
                'chat_id': '123',
            },
        )

        assert response.reply.texts[0] == response_text


@pytest.mark.supportai_actions(
    action_id='action_1',
    version=1,
    response={
        'state': {
            'features': [
                {'key': 'feature_1', 'value': 'Test'},
                {'key': 'feature_2', 'value': 'Test_2'},
            ],
        },
    },
)
@pytest.mark.supportai_actions(
    action_id='action_2',
    version=1,
    response={
        'state': {
            'features': [
                {'key': 'feature_3', 'value': 'Test_3'},
                {'key': 'feature_4', 'value': 'Test_4'},
            ],
        },
    },
)
@pytest.mark.supportai_actions(
    action_id='action_3',
    version=1,
    response={
        'state': {'features': [{'key': 'feature_5', 'value': 'Test_5'}]},
    },
)
@pytest.mark.parametrize(
    'config_path', ['configuration_graph_multiple_action.json'],
)
async def test_multiple_action_call(
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
    agent._policy_graph.max_loops = 1  # pylint: disable=W0212

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': '*'}]},
            'features': [{'key': 'iteration_number', 'value': 1}],
            'chat_id': '123',
        },
    )

    features = {}
    for feature in response.features.features:
        features[feature.key] = feature.value
    assert 'feature_1' in features
    assert features['feature_1'] == 'Test'
    assert 'feature_2' in features
    assert features['feature_2'] == 'Test_2'
    assert 'feature_3' in features
    assert features['feature_3'] == 'Test_3'
    assert 'feature_4' in features
    assert features['feature_4'] == 'Test_4'
    assert 'feature_5' in features
    assert features['feature_5'] == 'Test_5'
