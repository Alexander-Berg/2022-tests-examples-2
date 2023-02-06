# pylint: disable=C0302
import logging

import pytest

from supportai_lib.generated import models as api_module


from supportai.common import agent as agent_module
from supportai.common import configuration as configuration_module
from supportai.common import constants
from supportai.common import core_features
from supportai.common import exceptions
from supportai.common import state as state_module


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        CLIENT_SUPPORTAI_MODELS_SETTINGS={'use_v2_models_handlers': True},
    ),
]


logger = logging.getLogger(__name__)


async def _call_agent(
        web_context, agent: agent_module.Agent, request: dict, state=None,
) -> api_module.SupportResponse:
    data = api_module.SupportRequest.deserialize(request)
    state = state or await agent.init_state_from_db(
        context=web_context, request_data=data,
    )
    print('state info:', state)
    return await agent(
        context=web_context,
        request_data=data,
        state=state,
        return_all_features=True,
    )


@pytest.mark.parametrize('config_path', ['configuration_policy_block.json'])
async def test_call_agent_with_models_service(
        create_agent, web_context, mockserver, config_path,
):
    project_id = 'test_project'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': 'order_status',
            'probabilities': [
                {'topic_name': 'test_topic', 'probability': 1.0},
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
    assert response.reply is None
    assert response.features is not None
    assert response.features.most_probable_topic == 'order_status'


@pytest.mark.parametrize(
    'config_path', ['configuration_policy_block_process_predicate.json'],
)
# @pytest.mark.skip
async def test_call_agent_with_processes_predicate(
        create_agent, web_context, mockserver, config_path,
):
    project_id = 'test_project'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': 'order_status',
            'probabilities': [
                {'topic_name': 'test_topic', 'probability': 1.0},
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
    assert response.reply is None
    assert response.features is not None
    assert response.features.most_probable_topic == 'order_status'


@pytest.mark.parametrize(
    'config_path', ['configuration_with_line_template.json'],
)
async def test_call_agent_with_line_template(
        create_agent, web_context, mockserver, config_path,
):
    project_id = 'test_project'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': 'order_status',
            'probabilities': [
                {'topic_name': 'test_topic', 'probability': 1.0},
            ],
        },
    )
    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [{'author': 'user', 'text': 'Добрый день!'}],
            },
            'features': [{'key': 'feature', 'value': '12345'}],
            'chat_id': '123',
        },
    )
    assert response.reply.text == 'Hello'
    assert response.forward.line == '__12345__'


@pytest.mark.parametrize('config_path', ['configuration_policy_block.json'])
async def test_call_agent_without_models_service(
        create_agent, web_context, mockserver, config_path,
):
    @mockserver.json_handler(
        '/supportai-models/internal/supportai-models/v1/shard_id',
    )
    async def _(request):
        return mockserver.make_response(
            status=404,
            json={'code': 'model_not_found', 'message': 'Model not found'},
        )

    project_id = 'test_project_2'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': 'test_topic',
            'probabilities': [
                {'topic_name': 'test_topic', 'probability': 1.0},
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
            'features': [],
            'chat_id': '123',
        },
    )

    assert response.reply is None
    assert response.features is not None
    assert response.features.most_probable_topic is None


def test_get_info_from_backend():
    pass


def test_get_info_from_user():
    pass


@pytest.mark.parametrize('config_path', ['configuration_policy_block.json'])
async def test_unique_state_for_chat_id(
        create_agent, web_context, mockserver, config_path,
):
    project_id = 'test_project'
    supportai_models_response = {
        'most_probable_topic': 'order_status',
        'probabilities': [{'topic_name': 'order_status', 'probability': 1.0}],
    }
    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response=supportai_models_response,
    )

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Добрый день! Где мой заказ'},
                ],
            },
            'features': [
                {
                    'key': core_features.ITERATION_NUMBER_FEATURE_NAME,
                    'value': 1,
                },
                {
                    'key': core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME,
                    'value': 'ru',
                },
            ],
            'chat_id': '123',
        },
    )

    assert (
        response.reply.text == f'Здравствуйте!{constants.SPLIT_TOKEN}'
        f'Подскажите номер вашего заказа?'
    )

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': '1234567'}]},
            'features': [
                {
                    'key': core_features.ITERATION_NUMBER_FEATURE_NAME,
                    'value': 1,
                },
                {'key': 'order_status', 'value': 'доставка'},
                {
                    'key': core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME,
                    'value': 'ru',
                },
            ],
            'chat_id': '123',
        },
    )

    assert (
        response.reply.text == f'Здравствуйте!{constants.SPLIT_TOKEN}'
        f'Ваш заказ находится в статусе доставка'
    )

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Добрый день! Где мой заказ'},
                ],
            },
            'features': [
                {
                    'key': core_features.ITERATION_NUMBER_FEATURE_NAME,
                    'value': 1,
                },
                {
                    'key': core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME,
                    'value': 'ru',
                },
            ],
            'chat_id': '1234',
        },
    )

    assert (
        response.reply.text == f'Здравствуйте!{constants.SPLIT_TOKEN}'
        f'Подскажите номер вашего заказа?'
    )


@pytest.mark.parametrize('config_path', ['configuration_policy_block.json'])
async def test_policy_block_scenario(
        create_agent, web_context, mockserver, config_path,
):
    project_id = 'test_project'
    supportai_models_response = {
        'most_probable_topic': 'order_status',
        'probabilities': [{'topic_name': 'order_status', 'probability': 1.0}],
    }
    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response=supportai_models_response,
    )
    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Добрый день! Где мой заказ'},
                ],
            },
            'features': [
                {
                    'key': core_features.ITERATION_NUMBER_FEATURE_NAME,
                    'value': 1,
                },
                {
                    'key': core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME,
                    'value': 'ru',
                },
            ],
            'chat_id': '123',
        },
    )

    features = {
        feature.key: feature.value for feature in response.features.features
    }
    assert (
        response.reply.text == f'Здравствуйте!{constants.SPLIT_TOKEN}'
        f'Подскажите номер вашего заказа?'
    )
    assert response.features is not None
    assert response.features.most_probable_topic == 'order_status'
    assert response.features.sure_topic == 'order_status'
    assert features.get('order_id') is None
    assert features.get('order_ids') is None

    assert response.tag.add == ['1']

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [
                    {
                        'author': 'user',
                        'text': 'Добрый день! Где мой заказ 1234567',
                    },
                ],
            },
            'features': [
                {
                    'key': core_features.ITERATION_NUMBER_FEATURE_NAME,
                    'value': 1,
                },
                {
                    'key': core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME,
                    'value': 'ru',
                },
            ],
            'chat_id': '123',
        },
    )

    features = {
        feature.key: feature.value for feature in response.features.features
    }
    assert response.reply is None
    assert response.features is not None
    assert response.features.most_probable_topic == 'order_status'
    assert response.features.sure_topic == 'order_status'
    assert features['order_id'] == 1234567
    assert features['order_ids'] == [1234567]

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [
                    {
                        'author': 'user',
                        'text': 'Добрый день! Где мой заказ 1234567',
                    },
                ],
            },
            'features': [
                {
                    'key': core_features.ITERATION_NUMBER_FEATURE_NAME,
                    'value': 1,
                },
                {
                    'key': core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME,
                    'value': 'ru',
                },
                {'key': 'order_status', 'value': 'доставка'},
            ],
            'chat_id': '123',
        },
    )

    features = {
        feature.key: feature.value for feature in response.features.features
    }
    assert (
        response.reply.text == f'Здравствуйте!{constants.SPLIT_TOKEN}'
        f'Ваш заказ находится в статусе доставка'
    )
    assert response.features is not None
    assert response.features.most_probable_topic == 'order_status'
    assert response.features.sure_topic == 'order_status'
    assert features['order_id'] == 1234567

    assert response.tag.add == ['2']


@pytest.mark.parametrize('config_path', ['configuration_policy_block.json'])
async def test_ask_again(create_agent, web_context, mockserver, config_path):
    agent = await create_agent(
        namespace='test_project',
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': 'order_status',
            'probabilities': [
                {'topic_name': 'order_status', 'probability': 1.0},
            ],
        },
    )

    await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Добрый день! Где мой заказ?'},
                ],
            },
            'features': [{'key': 'iteration_number', 'value': 1}],
            'chat_id': '123',
        },
    )

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': 'не скажу'}]},
            'features': [{'key': 'iteration_number', 'value': 1}],
            'chat_id': '123',
        },
    )

    assert (
        response.reply.text
        == 'Здравствуйте![NEW]Подскажите номер вашего заказа?'
    )
    features = {
        feature.key: feature.value for feature in response.features.features
    }

    assert features['last_policy_apply_count'] == 2

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': '1234567'}]},
            'features': [
                {'key': 'iteration_number', 'value': 3},
                {'key': 'order_status', 'value': 'доставка'},
            ],
            'chat_id': '123',
        },
    )

    assert response.reply.text == 'Ваш заказ находится в статусе доставка'

    features = {
        feature.key: feature.value for feature in response.features.features
    }

    assert features['last_policy_apply_count'] == 1


@pytest.mark.parametrize('config_path', ['configuration_policy_block.json'])
async def test_ask_again_limit(
        create_agent, web_context, mockserver, config_path,
):

    agent = await create_agent(
        namespace='test_project',
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': 'general_thanks',
            'probabilities': [
                {'topic_name': 'general_thanks', 'probability': 1.0},
            ],
        },
    )
    request = {
        'dialog': {
            'messages': [
                {'author': 'user', 'text': 'Какой-то странный текст'},
            ],
        },
        'features': [{'key': 'iteration_number', 'value': 2}],
        'chat_id': '123',
    }

    response = await _call_agent(web_context, agent, request)
    assert response.reply.text == 'Всегда пожалуйста'

    response = await _call_agent(web_context, agent, request)

    assert response.reply.text == 'Всегда пожалуйста'
    features = {
        feature.key: feature.value for feature in response.features.features
    }

    assert features['last_policy_apply_count'] == 2

    response = await _call_agent(web_context, agent, request)

    assert response.reply is None


@pytest.mark.parametrize('config_path', ['configuration_policy_block.json'])
async def test_prev_topic_return(
        create_agent, web_context, mockserver, config_path,
):
    agent = await create_agent(
        namespace='test_project',
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': 'order_status',
            'probabilities': [
                {'topic_name': 'order_status', 'probability': 1.0},
            ],
        },
    )

    await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Добрый день! Где мой заказ?'},
                ],
            },
            'features': [
                {'key': 'iteration_number', 'value': 1},
                {'key': 'order_status', 'value': 'доставка'},
            ],
            'chat_id': '123',
        },
    )

    agent = await create_agent(
        namespace='test_project',
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': 'bonuses',
            'probabilities': [{'topic_name': 'bonuses', 'probability': 1.0}],
        },
    )

    await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'А бонусы у вас как работают?'},
                ],
            },
            'features': [{'key': 'iteration_number', 'value': 2}],
            'chat_id': '123',
        },
    )

    agent = await create_agent(
        namespace='test_project',
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': 'other__classes',
            'probabilities': [
                {'topic_name': 'other__classes', 'probability': 1.0},
            ],
        },
    )

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': 'ну и?'}]},
            'features': [{'key': 'iteration_number', 'value': 3}],
            'chat_id': '123',
        },
    )

    assert response.reply.text == 'Подскажите номер вашего заказа?'
    assert response.features.sure_topic == 'order_status'


@pytest.mark.parametrize('config_path', ['configuration_policy_block.json'])
async def test_clarifying_question(
        create_agent, web_context, mockserver, config_path,
):
    agent = await create_agent(
        namespace='test_project',
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
                    {'author': 'user', 'text': 'Добрый день! Где мой заказ?'},
                ],
            },
            'features': [
                {'key': 'iteration_number', 'value': 1},
                {'key': 'order_status', 'value': 'доставка'},
            ],
            'chat_id': '123',
        },
    )

    agent = await create_agent(
        namespace='test_project',
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': 'other__classes',
            'probabilities': [
                {'topic_name': 'other__classes', 'probability': 1.0},
            ],
        },
    )

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': '1234567'}]},
            'features': [
                {'key': 'iteration_number', 'value': 2},
                {'key': 'order_status', 'value': 'доставка'},
            ],
            'chat_id': '123',
        },
    )

    features = {
        feature.key: feature.value for feature in response.features.features
    }

    assert response.reply.text == f'Ваш заказ находится в статусе доставка'
    assert response.features is not None
    assert response.features.most_probable_topic == 'other__classes'
    assert response.features.sure_topic == 'order_status'
    assert features['order_id'] == 1234567


@pytest.mark.parametrize('config_path', ['configuration_policy_block.json'])
async def test_new_intent_process(
        create_agent, web_context, mockserver, config_path,
):
    agent = await create_agent(
        namespace='test_project',
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
                    {'author': 'user', 'text': 'Добрый день! Где мой заказ?'},
                ],
            },
            'features': [
                {
                    'key': core_features.ITERATION_NUMBER_FEATURE_NAME,
                    'value': 1,
                },
                {
                    'key': core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME,
                    'value': 'ru',
                },
                {'key': 'order_status', 'value': 'доставка'},
            ],
            'chat_id': '123',
        },
    )

    agent = await create_agent(
        namespace='test_project',
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': 'cancel_order',
            'probabilities': [
                {'topic_name': 'cancel_order', 'probability': 1.0},
            ],
        },
    )
    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': '1234567, отмените его'},
                ],
            },
            'features': [
                {
                    'key': core_features.ITERATION_NUMBER_FEATURE_NAME,
                    'value': 2,
                },
                {
                    'key': core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME,
                    'value': 'ru',
                },
                {'key': 'order_status', 'value': 'доставка'},
            ],
            'chat_id': '123',
        },
    )

    features = {
        feature.key: feature.value for feature in response.features.features
    }

    assert response.reply.text == 'Ваш заказ 1234567 будет отменен'
    assert response.features is not None
    assert response.features.most_probable_topic == 'cancel_order'
    assert response.features.sure_topic == 'cancel_order'
    assert features['order_id'] == 1234567

    agent = await create_agent(
        namespace='test_project',
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': 'general_thanks',
            'probabilities': [
                {'topic_name': 'general_thanks', 'probability': 1.0},
            ],
        },
    )

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': 'спасибо'}]},
            'features': [
                {'key': 'iteration_number', 'value': 3},
                {'key': 'order_status', 'value': 'доставка'},
            ],
            'chat_id': '123',
        },
    )

    assert response.reply.text == 'Всегда пожалуйста'
    assert response.features is not None
    assert response.features.most_probable_topic == 'general_thanks'
    assert response.features.sure_topic == 'general_thanks'


# TODO: ksenilis  global features
# how to decide which to store somehow and which not to store
@pytest.mark.parametrize('config_path', ['configuration_policy_block.json'])
@pytest.mark.parametrize('clear_slots_after_topic_change', [True, False])
async def test_new_intent_with_previous_features(
        create_agent,
        web_context,
        mockserver,
        config_path,
        clear_slots_after_topic_change,
):
    agent = await create_agent(
        namespace='test_project',
        config_path=config_path,
        flags=configuration_module.CoreFlags(
            clear_slots_after_topic_change=clear_slots_after_topic_change,
        ),
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
                        'text': 'Добрый день! Где мой заказ 1234567?',
                    },
                ],
            },
            'features': [
                {
                    'key': core_features.ITERATION_NUMBER_FEATURE_NAME,
                    'value': 1,
                },
                {
                    'key': core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME,
                    'value': 'ru',
                },
                {'key': 'order_status', 'value': 'доставка'},
            ],
            'chat_id': '123',
        },
    )

    agent = await create_agent(
        namespace='test_project',
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': 'cancel_order',
            'probabilities': [
                {'topic_name': 'cancel_order', 'probability': 1.0},
            ],
        },
    )

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [{'author': 'user', 'text': 'отмените его'}],
            },
            'features': [
                {
                    'key': core_features.ITERATION_NUMBER_FEATURE_NAME,
                    'value': 2,
                },
                {
                    'key': core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME,
                    'value': 'ru',
                },
                {'key': 'order_status', 'value': 'доставка'},
            ],
            'chat_id': '123',
        },
    )

    if clear_slots_after_topic_change:
        assert response.reply.text == 'Подскажите номер вашего заказа?'
    else:
        assert response.reply.text == 'Ваш заказ 1234567 будет отменен'

    assert response.features is not None
    assert response.features.most_probable_topic == 'cancel_order'
    assert response.features.sure_topic == 'cancel_order'

    agent = await create_agent(
        namespace='test_project',
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': 'general_thanks',
            'probabilities': [
                {'topic_name': 'general_thanks', 'probability': 1.0},
            ],
        },
    )

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': 'спасибо'}]},
            'features': [
                {'key': 'iteration_number', 'value': 3},
                {'key': 'order_status', 'value': 'доставка'},
            ],
            'chat_id': '123',
        },
    )

    assert response.reply.text == 'Всегда пожалуйста'
    assert response.features is not None
    assert response.features.most_probable_topic == 'general_thanks'
    assert response.features.sure_topic == 'general_thanks'


@pytest.mark.supportai_actions(
    action_id='test_supportai_actions',
    version=1,
    response={'state': {'features': [{'key': 'order_test', 'value': 'Test'}]}},
)
@pytest.mark.supportai_actions(
    action_id='test_supportai_actions_bad',
    status=400,
    version=1,
    response={'state': {'features': []}},
)
@pytest.mark.parametrize(
    'config_path',
    [
        'configuration_policy_api_call_actions.json',
        'configuration_policy_api_call_actions_400_continue_on_fail.json',
        pytest.param(
            'configuration_policy_api_call_actions_400.json',
            marks=pytest.mark.xfail(
                raises=exceptions.AgentActionException, strict=True,
            ),
        ),
        pytest.param(
            'configuration_policy_api_call_actions_400.json',
            marks=pytest.mark.xfail(
                raises=exceptions.AgentActionException, strict=True,
            ),
        ),
    ],
)
async def test_agent_with_supportai_actions(
        create_agent, web_context, mockserver, config_path,
):
    agent = await create_agent(
        namespace='test_project',
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
                        'text': 'Добрый день! Где мой заказ 1234567?',
                    },
                ],
            },
            'features': [
                {'key': 'iteration_number', 'value': 2},
                {'key': 'order_status', 'value': 'доставка'},
            ],
            'chat_id': '123',
        },
    )

    value = None
    action_error = None
    for feature in response.features.features:
        if feature.key == 'order_test':
            value = feature.value
        if feature.key == 'action_error_description':
            action_error = feature.value

    if value is not None:
        assert action_error is None
        assert value == 'Test'
    else:
        assert action_error is not None


@pytest.mark.parametrize('config_path', ['call_configuration.json'])
async def test_call_configuration(
        create_agent, web_context, mockserver, config_path,
):
    project_id = 'call_project'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': '',
            'probabilities': [],
        },
    )
    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': ''}]},
            'features': [{'key': 'event_type', 'value': 'dial'}],
            'chat_id': '123',
        },
    )

    assert response.reply.text == 'Здравствуйте! Это Тестовый бот!'

    assert response.tag.add == ['speak']

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': 'алло'}]},
            'features': [{'key': 'event_type', 'value': 'ask'}],
            'chat_id': '123',
        },
    )

    assert response.reply.text == f'Это Тестовый бот!'

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': 'трали-вали'}]},
            'features': [],
            'chat_id': '123',
        },
    )

    assert response.reply.text == f'Не понял'

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': 'что хочешь'}]},
            'features': [],
            'chat_id': '123',
        },
    )

    assert response.reply.text == f'Просто поболтать'

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': 'пока'}]},
            'features': [],
            'chat_id': '123',
        },
    )

    assert response.reply.text == f'Пока!'


@pytest.mark.parametrize('config_path', ['call_configuration.json'])
@pytest.mark.parametrize('translate_dialog', [True, False])
async def test_translate(
        create_agent, web_context, mockserver, config_path, translate_dialog,
):
    project_id = 'call_project'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': '',
            'probabilities': [],
        },
        flags=configuration_module.CoreFlags(
            translate_dialog=translate_dialog,
        ),
    )
    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [
                    {
                        'author': 'user',
                        'text': 'Привет',
                        'preprocessor_results': {'spelled_message': 'привет'},
                    },
                    {'author': 'ai', 'text': 'Как дела?'},
                    {'author': 'user', 'text': 'Good', 'language': 'en'},
                ],
            },
            'features': [{'key': 'abc', 'value': '12345'}],
            'chat_id': '123',
        },
        state=state_module.State(feature_layers=[]),
    )

    united_user_messages = None
    for item in response.features.features:
        if item.key == 'united_user_messages':
            united_user_messages = item.value
            break
    if translate_dialog:
        assert united_user_messages == 'привет\nотлично'
    else:
        assert united_user_messages == 'привет\ngood'


@pytest.mark.parametrize('config_path', ['loop_configuration.json'])
@pytest.mark.xfail(strict=True, raises=exceptions.AgentException)
async def test_loop_of_actions(
        create_agent, web_context, mockserver, config_path,
):
    project_id = 'loop_project'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': '',
            'probabilities': [],
        },
    )
    _ = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': ''}]},
            'features': [],
            'chat_id': '123',
        },
    )


@pytest.mark.parametrize('config_path', ['calculate_configuration.json'])
async def test_calculate_of_actions(
        create_agent, web_context, mockserver, config_path,
):
    project_id = 'calculate_project'

    agent = await create_agent(
        namespace=project_id,
        config_path=config_path,
        supportai_models_response={
            'most_probable_topic': '',
            'probabilities': [],
        },
    )
    res = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': ''}]},
            'features': [{'key': 'iteration_number', 'value': 1}],
            'chat_id': '123',
        },
    )

    assert res.features is not None

    calculated = None
    calculated_first = None
    calculated_after_predicate = None
    for feature in res.features.features:
        logging.info(f'{feature.key}:{feature.value}')
        if feature.key == 'calculated':
            calculated = feature.value
        if feature.key == 'calculated_first':
            calculated_first = feature.value
        if feature.key == 'calculated_after_predicate':
            calculated_after_predicate = feature.value

    assert calculated is not None
    assert calculated is True
    assert calculated_first is not None
    assert calculated_first is True
    assert calculated_after_predicate is not None
    assert calculated == calculated_after_predicate


async def test_antifrod_features(web_context, create_agent):
    agent = await create_agent(
        namespace='test',
        config_path='configuration_policy_block.json',
        supportai_models_response={
            'most_probable_topic': 'cancel_order',
            'probabilities': [
                {'topic_name': 'cancel_order', 'probability': 0.8},
                {'topic_name': 'order_status', 'probability': 0.2},
            ],
        },
    )
    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {'author': 'user', 'text': 'очень хочу отменить урок!'},
                ],
            },
            'features': [{'key': 'iteration_number', 'value': 1}],
            'chat_id': '123',
        },
    )

    assert response.features is not None

    features = {
        feature.key: feature.value for feature in response.features.features
    }

    assert 'levenshtein_similarity' in features and features[
        'levenshtein_similarity'
    ] == pytest.approx(0.72)
    assert 'jaccard_similarity' in features and features[
        'jaccard_similarity'
    ] == pytest.approx(0.4)
    assert 'most_probable_topic_probability' in features and features[
        'most_probable_topic_probability'
    ] == pytest.approx(0.8)
    assert 'sure_topic_probability' in features and features[
        'sure_topic_probability'
    ] == pytest.approx(0.8)


async def test_change_state_action(web_context, create_agent):
    agent = await create_agent(
        namespace='test',
        config_path='change_state_action.json',
        supportai_models_response={
            'most_probable_topic': '',
            'probabilities': [],
        },
    )
    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': 'Привет'}]},
            'features': [],
            'chat_id': '123',
        },
    )

    assert response.features is not None

    features = {
        feature.key: feature.value for feature in response.features.features
    }

    assert features['feature'] == 'value'
    assert features['last_user_message'] == 'привет'
    assert (
        'most_probable_topic_probability' in features
        and features['most_probable_topic_probability'] is None
    )
    assert (
        'sure_topic_probability' in features
        and features['sure_topic_probability'] is None
    )


async def test_explicit_requested_features(web_context, create_agent):
    agent = await create_agent(
        namespace='test',
        config_path='explicit_requested_features.json',
        supportai_models_response={
            'most_probable_topic': '',
            'probabilities': [],
        },
    )
    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': 'привет'}]},
            'features': [],
            'chat_id': '123',
        },
    )
    assert response.reply.text == 'назови первые 4 цифры'
    # pylint: disable=W0212
    state = await agent._tracker.load_bot_state(
        chat_id='123', context=web_context,
    )
    features = state.get_features()
    assert features['state'].value == '1'
    assert features['first_4'].value is None
    assert features['first_4'].status == 'in_progress'
    assert features['last_4'].value is None

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [{'author': 'user', 'text': 'первые цифры 1234'}],
            },
            'features': [],
            'chat_id': '123',
        },
        state,
    )
    assert response.reply.text == 'просто напиши хорошо'
    # pylint: disable=W0212
    state = await agent._tracker.load_bot_state(
        chat_id='123', context=web_context,
    )
    features = state.get_features()
    assert features['first_4'].value == '1234'
    assert features['last_4'].value == '1234'
    assert features['last_4'].status == 'defined'
    assert features['last_4_duplicate'].value == '1234'
    assert features['last_4_duplicate'].status == 'defined'

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': 'хорошо'}]},
            'features': [],
            'chat_id': '123',
        },
    )
    assert response.reply.text == 'назови последние 4 цифры'
    # pylint: disable=W0212
    state = await agent._tracker.load_bot_state(
        chat_id='123', context=web_context,
    )
    features = state.get_features()
    assert features['first_4'].value == '1234'
    assert features['last_4'].value is None
    assert features['last_4'].status == 'in_progress'
    assert features['last_4_duplicate'].value is None
    assert features['last_4_duplicate'].status == 'in_progress'

    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'последние цифры 7890'},
                ],
            },
            'features': [],
            'chat_id': '123',
        },
        state,
    )
    # pylint: disable=W0212
    state = await agent._tracker.load_bot_state(
        chat_id='123', context=web_context,
    )
    features = state.get_features()
    assert features['first_4'].value == '1234'
    assert features['last_4'].value == '7890'
    assert features['last_4_duplicate'].value == '7890'
    assert response.reply.text == 'первые 1234; последние 7890, верно?'


async def test_buttons(web_context, create_agent):
    agent = await create_agent(
        namespace='test',
        config_path='buttons.json',
        supportai_models_response={
            'most_probable_topic': '',
            'probabilities': [],
        },
    )
    response = await _call_agent(
        web_context,
        agent,
        {
            'dialog': {'messages': [{'author': 'user', 'text': 'привет'}]},
            'features': [],
            'chat_id': '123',
        },
    )
    assert response.reply.text == 'выбери один из вариантов'
    assert response.buttons_block.buttons[0].text == 'вариант 1'
    assert response.buttons_block.buttons[1].text == 'вариант 2'
    assert response.buttons_block.buttons[2].text == 'назад'
