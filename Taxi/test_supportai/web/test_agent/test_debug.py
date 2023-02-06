import pytest

from supportai_lib.generated import models as api_module

from supportai.common import agent as agent_module


@pytest.mark.supportai_actions(
    action_id='test_supportai_actions',
    version=1,
    response={
        'state': {'features': [{'key': 'new_feature', 'value': 'value'}]},
        'debug_info': 'some info',
    },
)
@pytest.mark.config(
    SUPPORTAI_DEBUG_SETTINGS={
        'default_debug_ttl_days': 3,
        'projects': ['test_project'],
    },
)
@pytest.mark.parametrize(
    'project_id,iteration_number,text,code,scenarios_number',
    [
        ('test_project', 1, 'Здравствуйте!', 200, 1),
        ('test_project', 2, 'Привет', 200, 2),
        ('other_project', 3, 'Привет', 204, 2),
    ],
)
async def test_collect_debug(
        web_app_client,
        create_agent,
        web_context,
        project_id,
        iteration_number,
        text,
        code,
        scenarios_number,
):
    agent = await create_agent(
        namespace=project_id,
        config_path='configuration.json',
        supportai_models_response={
            'most_probable_topic': 'order_status',
            'probabilities': [
                {'topic_name': 't_2', 'probability': 0.9},
                {'topic_name': 't_3', 'probability': 0.8},
                {'topic_name': 't_1', 'probability': 1.0},
            ],
        },
    )

    request = {
        'dialog': {'messages': [{'author': 'user', 'text': text}]},
        'features': [{'key': 'iteration_number', 'value': iteration_number}],
        'chat_id': '1234',
    }

    data = api_module.SupportRequest.deserialize(request)
    agent.init_debug(context=web_context)
    state = await agent.init_state_from_db(
        context=web_context, request_data=data,
    )
    response = await agent(context=web_context, request_data=data, state=state)

    await agent.debug.save_debug(
        context=web_context,
        chat_id='1234',
        iteration_number=iteration_number,
        api_flags=agent_module.ApiFlags(simulated=False, mocked=False),
    )

    assert response.explanation.topic_explanation is not None
    assert response.explanation.policy_explanation is None
    assert len(response.explanation.policy_titles) == scenarios_number

    await web_context.supportai_debug_cache.refresh_cache()

    response = await web_app_client.get(
        f'/v1/debug?project_slug={project_id}&chat_id=1234&'
        f'iteration_number={iteration_number}',
    )
    assert response.status == code

    if iteration_number == 1:
        blocks = (await response.json())['debug_blocks']
        info_descriptions = set()

        for block in blocks:
            extra = {
                feature['key']: feature['value'] for feature in block['extra']
            }
            if block['title'] == 'tags':
                assert extra == {'tags': ['tag']}
            if block['title'] == 'probabilities':
                assert extra == {'t_1': 1.0, 't_2': 0.9, 't_3': 0.8}
            if block['title'] == 'policy':
                assert extra == {'policy_title': 'with_action'}
            if (
                    block['title'] == 'action'
                    and extra['action'] != 'ResponseAction'
            ):
                assert extra == {'action': 'test_supportai_actions'}
                features = [feature['key'] for feature in block['features']]
                assert 'new_feature' in features
            if block['title'] == 'response':
                assert extra == {'texts': ['Добрый день!'], 'operator': True}
            if block['title'] == 'info':
                info_descriptions.add(block['description'])
        assert len(info_descriptions) == 2
        assert 'some info' in info_descriptions

    if iteration_number == 2:
        blocks = (await response.json())['debug_blocks']

        for block in blocks:
            extra = {
                feature['key']: feature['value'] for feature in block['extra']
            }
            if block['title'] == 'probabilities':
                assert extra == {'t_1': 1.0, 't_2': 0.9, 't_3': 0.8}
            if block['title'] == 'policy':
                assert extra in (
                    {'policy_title': 'first_policy'},
                    {'policy_title': 'second_policy'},
                )
            if (
                    block['title'] == 'action'
                    and extra['action'] == 'ChangeStateAction'
            ):
                # assert extra == {'action': 'ChangeStateAction'}
                features = [feature['key'] for feature in block['features']]
                assert 'new_feature' in features
            if block['title'] == 'response':
                assert extra == {
                    'texts': ['Пока'],
                    'close': True,
                    'defer_time_sec': 125,
                    'forward_line': 'line1',
                }
