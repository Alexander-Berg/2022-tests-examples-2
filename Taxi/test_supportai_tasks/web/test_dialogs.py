from aiohttp import web
import pytest


@pytest.fixture(name='dialog_history')
def gen_dialog_history():
    return {
        'contexts': [
            {
                'created_at': '2021-04-01 10:00:00',
                'chat_id': '123',
                'records': [
                    {
                        'id': '1',
                        'request': {
                            'chat_id': '123',
                            'dialog': {
                                'messages': [{'text': 'hi', 'author': 'user'}],
                            },
                            'features': [{'key': 'feature1', 'value': 1}],
                        },
                        'response': {
                            'reply': {'text': 'hello', 'texts': ['hello']},
                            'features': {
                                'most_probable_topic': 'topic1',
                                'sure_topic': 'topic1',
                                'probabilities': [
                                    {
                                        'topic_name': 'topic1',
                                        'probability': 0.8,
                                    },
                                    {
                                        'topic_name': 'topic2',
                                        'probability': 0.1,
                                    },
                                ],
                            },
                            'graph_positions_stack': {
                                'positions_stack': ['1111', '2222'],
                            },
                        },
                    },
                    {
                        'id': '2',
                        'mark': 'ok',
                        'mark_comment': 'excellent',
                        'request': {
                            'chat_id': '123',
                            'dialog': {
                                'messages': [
                                    {
                                        'text': 'help help help',
                                        'author': 'user',
                                    },
                                ],
                            },
                            'features': [
                                {'key': 'feature2', 'value': 'Feature 2'},
                                {'key': 'feature3', 'value': 'Feature 3'},
                            ],
                        },
                        'response': {
                            'reply': {
                                'text': 'Im on my way',
                                'texts': ['Im on my way'],
                            },
                            'close': {},
                            'defer': {'time_sec': 1},
                            'forward': {'line': 'line1'},
                            'tag': {'add': ['tag1', 'tag2']},
                            'features': {
                                'most_probable_topic': 'topic1',
                                'sure_topic': 'topic1',
                                'probabilities': [
                                    {
                                        'topic_name': 'topic1',
                                        'probability': 0.9,
                                    },
                                ],
                            },
                        },
                    },
                ],
            },
        ],
        'total': 2,
    }


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_dialogs_history(web_app_client, mockserver, dialog_history):
    @mockserver.json_handler('/supportai-context/v1/contexts')
    # pylint: disable=unused-variable
    async def context_handler(request):
        return web.json_response(data=dialog_history)

    dialogs = await web_app_client.get(
        '/v1/dialogs/history?user_id=34&project_id=1',
    )
    assert dialogs.status == 200
    data = await dialogs.json()

    assert len(data['dialogs']) == 1


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_dialogs_record_mark(web_app_client, mockserver):
    @mockserver.json_handler('/supportai-context/v1/context/record/mark')
    # pylint: disable=unused-variable
    async def context_handler(request):
        assert request.query['chat_id'] == '123'
        assert request.json['context_id'] == '1'
        assert request.json['mark'] == 'not_ok'
        assert request.json['mark_comment'] == 'Very bad'

        return web.json_response()

    response = await web_app_client.post(
        '/v1/dialogs/record/mark?user_id=34&project_id=1',
        json={
            'chat_id': '123',
            'record_id': '1',
            'mark': 'not_ok',
            'mark_comment': 'Very bad',
        },
    )
    assert response.status == 200


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_dialog_clone(web_app_client, mockserver, dialog_history):
    @mockserver.json_handler('/supportai-context/v1/context/clone')
    # pylint: disable=unused-variable
    async def context_handler(request):
        assert request.query['chat_id'] == 'old_chat_id'
        assert request.json['new_chat_id'] == 'new_chat_id'

        context = dialog_history['contexts'][0]
        context['chat_id'] = request.json['new_chat_id']
        context['records'] = context['records'][:1]

        return web.json_response(data=context)

    @mockserver.json_handler('/supportai/supportai/v1/states/clone')
    # pylint: disable=unused-variable
    async def supportai_handler(request):
        assert request.json['chat_id'] == 'old_chat_id'
        assert request.json['new_chat_id'] == 'new_chat_id'
        assert request.json['iteration'] == 1

        return web.json_response()

    response = await web_app_client.post(
        '/v1/dialogs/clone?user_id=34&project_id=1',
        json={
            'chat_id': 'old_chat_id',
            'new_chat_id': 'new_chat_id',
            'clone_count': 1,
        },
    )
    assert response.status == 200

    response_json = await response.json()

    assert response_json['chat_id'] == 'new_chat_id'
    assert response_json['records'][-1]['response']['graph_positions_stack'][
        'positions_stack'
    ] == ['1111', '2222']


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_dialogs_examples(web_app_client, mockserver, dialog_history):
    @mockserver.json_handler('/supportai-context/v1/contexts')
    # pylint: disable=unused-variable
    async def context_handler(request):
        return web.json_response(data=dialog_history)

    dialogs = await web_app_client.get(
        '/v1/dialogs/examples?user_id=34&project_id=1&topic_slug=topic1',
    )
    assert dialogs.status == 200
    data = await dialogs.json()

    assert len(data['dialogs']) == 1


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_dialogs_thresholds_examples(
        web_app_client, mockserver, dialog_history,
):
    @mockserver.json_handler('/supportai-context/v1/contexts')
    # pylint: disable=unused-variable
    async def context_handler(request):
        return web.json_response(data=dialog_history)

    dialogs = await web_app_client.get(
        '/v1/dialogs/thresholds/examples?user_id=34&project_id=1'
        '&most_probable_topic_slug=topic1&mpt_probability=0.87'
        '&mpt_probability_pos=above',
    )
    assert dialogs.status == 200
    data = await dialogs.json()

    assert len(data['dialogs']) == 1
