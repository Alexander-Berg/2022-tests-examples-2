# pylint: disable=C0302
import pytest

from supportai_lib.generated import models as api_module

from supportai.common import agent as agent_module
from supportai.common import configuration as configuration_module


async def _call_agent(
        web_context, agent: agent_module.Agent, request: dict,
) -> api_module.SupportResponse:
    data = api_module.SupportRequest.deserialize(request)
    state = await agent.init_state_from_db(
        context=web_context, request_data=data,
    )
    return await agent(context=web_context, request_data=data, state=state)


@pytest.mark.parametrize('from_request', [True, False])
@pytest.mark.parametrize('clear_slots_after_topic_change', [True, False])
async def test_clear_slots_after_topic_change(
        create_agent,
        web_context,
        mockserver,
        clear_slots_after_topic_change,
        from_request,
):
    flags = (
        configuration_module.CoreFlags(
            clear_slots_after_topic_change=clear_slots_after_topic_change,
        )
        if not from_request
        else None
    )

    agent = await create_agent(
        namespace='test_project',
        config_path='configuration.json',
        flags=flags,
        supportai_models_response={
            'most_probable_topic': 'order_status',
            'probabilities': [
                {'topic_name': 'order_status', 'probability': 1.0},
            ],
        },
    )

    request = {
        'dialog': {
            'messages': [
                {
                    'author': 'user',
                    'text': 'Добрый день! Где мой заказ 1234567?',
                },
            ],
        },
        'features': [
            {'key': 'iteration_number', 'value': 1},
            {'key': 'order_status', 'value': 'доставка'},
        ],
        'chat_id': '123',
    }

    if from_request:
        request['core_configuration'] = {
            'flags': [
                {
                    'key': 'clear_slots_after_topic_change',
                    'value': clear_slots_after_topic_change,
                },
            ],
        }

    await _call_agent(web_context, agent, request=request)

    agent = await create_agent(
        namespace='test_project',
        config_path='configuration.json',
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
                {'key': 'iteration_number', 'value': 2},
                {'key': 'order_status', 'value': 'доставка'},
            ],
            'chat_id': '123',
        },
    )

    if clear_slots_after_topic_change:
        assert response.reply.text == 'Подскажите номер вашего заказа?'
    else:
        assert response.reply.text == 'Ваш заказ 1234567 будет отменен'


async def test_incorrect_feature_flag(create_agent, web_context, mockserver):
    agent = await create_agent(
        namespace='test_project',
        config_path='configuration.json',
        flags=None,
        supportai_models_response={
            'most_probable_topic': 'order_status',
            'probabilities': [
                {'topic_name': 'order_status', 'probability': 1.0},
            ],
        },
    )

    request = {
        'dialog': {
            'messages': [
                {
                    'author': 'user',
                    'text': 'Добрый день! Где мой заказ 1234567?',
                },
            ],
        },
        'features': [
            {'key': 'iteration_number', 'value': 1},
            {'key': 'order_status', 'value': 'доставка'},
        ],
        'chat_id': '123',
        'core_configuration': {
            'flags': [
                {'key': 'clear_slots_after_topic_change', 'value': False},
                {'key': 'unknown', 'value': True},
            ],
        },
    }

    await _call_agent(web_context, agent, request=request)

    agent = await create_agent(
        namespace='test_project',
        config_path='configuration.json',
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
                {'key': 'iteration_number', 'value': 2},
                {'key': 'order_status', 'value': 'доставка'},
            ],
            'chat_id': '123',
        },
    )

    assert response.reply.text == 'Подскажите номер вашего заказа?'


@pytest.mark.parametrize('dst_validate_feature_type', [True, False])
async def test_dst_validate_feature_type(
        create_agent, web_context, mockserver, dst_validate_feature_type,
):
    flags = configuration_module.CoreFlags(
        dst_validate_feature_type=dst_validate_feature_type,
    )

    agent = await create_agent(
        namespace='test_project',
        config_path='configuration.json',
        flags=flags,
        supportai_models_response={
            'most_probable_topic': 'order_status',
            'probabilities': [
                {'topic_name': 'order_status', 'probability': 1.0},
            ],
        },
    )

    request = {
        'dialog': {
            'messages': [{'author': 'user', 'text': 'Что с моим заказом?'}],
        },
        'features': [
            {'key': 'order_id', 'value': '123f'},
            {'key': 'order_status', 'value': 'доставка'},
            {'key': 'some_array_feature', 'value': [1, 2, 'str']},
        ],
        'chat_id': '123',
    }

    response = await _call_agent(web_context, agent, request=request)

    if dst_validate_feature_type:
        assert response.reply.text == 'Подскажите номер вашего заказа?'
    else:
        assert response.reply.text == 'Ваш заказ находится в статусе доставка'
