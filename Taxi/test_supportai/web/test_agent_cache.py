# pylint: disable=W0212
import datetime

from aiohttp import web
import pytest

from supportai_lib.generated import models

from supportai import models as db_models
from supportai.api import support_v1
from supportai.generated.service.swagger import requests

# pylint: disable=C0103
pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        SUPPORTAI_RELEASE_SETTINGS={
            'projects': [{'project_slug': 'ya_lavka', 'limit': 10}],
        },
        CLIENT_SUPPORTAI_MODELS_SETTINGS={'use_v2_models_handlers': True},
    ),
    pytest.mark.pgsql('supportai', files=['cache_data.sql']),
]


@pytest.fixture(name='mocked_agent_handlers')
def mock_agent_handlers(mock, monkeypatch, mockserver):
    @mockserver.json_handler('/wizard/wizard')
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={
                'rules': {
                    'Date': {
                        'Pos': '1',
                        'Length': '1',
                        'Body': '{"Day":"1D"}',
                    },
                },
            },
        )

    @mockserver.json_handler('/tr.json/detect')
    async def _detect(request):
        return mockserver.make_response(
            status=200, json={'code': 200, 'lang': 'ru'},
        )

    @mockserver.json_handler('/tr.json/translate')
    async def _dummy_translate(*args, **kwargs):
        return mockserver.make_response(
            status=200, json={'code': 200, 'lang': 'ru-ru', 'text': [None]},
        )

    @mockserver.json_handler('/spellchecker/misspell.json/check')
    async def _misspell(_):
        return mockserver.make_response(
            status=200,
            json={'code': 200, 'lang': 'ru', 'rule': '', 'flags': 0, 'f': {}},
        )


async def test_release_agent_cache_reload(
        web_context, web_app_client, mockserver, mocked_agent_handlers,
):

    handler_data = {
        'most_probable_topic': 'topic1',
        'probabilities': [
            {'topic_name': 'topic2', 'probability': 0.1},
            {'topic_name': 'topic1', 'probability': 0.9},
        ],
    }

    request = {
        'chat_id': '12334567890',
        'dialog': {
            'messages': [
                {'author': 'user', 'text': 'У вас лучшая поддержка!!!'},
            ],
        },
        'features': [{'key': 'feature1', 'value': 1}],
    }

    @mockserver.json_handler(
        '/supportai-models-alpha/internal/supportai-models/v2/apply/text_classify',  # noqa pylint: disable=line-too-long
    )
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(data=handler_data)

    support_request = requests.SupportV1(
        log_extra=None,
        middlewares=[],
        project_id='sunlight',
        simulated=False,
        mocked=False,
        is_async=False,
        ask_features=False,
        body=models.SupportRequest.deserialize(request),
        version=None,
    )
    # Use straight call to handle,
    # because web app is another thread
    # and cache can not be reloaded correctly
    response = await support_v1.handle_old(support_request, web_context)

    assert response.status == 200
    assert response.data.reply is not None
    assert response.data.reply.text == 'Feature1 is 1'

    handler_data['probabilities'][0]['probability'] = 0.6
    handler_data['probabilities'][1]['probability'] = 0.2
    handler_data['most_probable_topic'] = 'topic2'

    request['features'][0] = {'key': 'feature2', 'value': 2}

    response = await web_app_client.post(
        '/v1/versions/draft/release',
        params={'project_slug': 'sunlight', 'user_id': 34},
    )

    assert response.status == 200

    await web_app_client.post(
        '/v1/versions/percentage?project_slug=sunlight&user_id=34',
        json={
            'mapping': [
                {'version_id': 2, 'percentage': 0},
                {'version_id': 6, 'percentage': 100},
            ],
        },
    )

    # Wait for cache reload
    await web_context.supportai_agent_cache.refresh_cache()

    support_request.body = models.SupportRequest.deserialize(request)
    support_request.version = '6'
    response = await support_v1.handle_old(support_request, web_context)

    assert response.status == 200
    assert response.data.reply is not None
    assert response.data.reply.text == 'Feature2 is 2'


async def test_agent_cache_draft(
        web_context, web_app_client, mockserver, mocked_agent_handlers,
):

    handler_data = {
        'most_probable_topic': 'topic2',
        'probabilities': [
            {'topic_name': 'topic2', 'probability': 0.6},
            {'topic_name': 'topic1', 'probability': 0.2},
        ],
    }

    request = {
        'chat_id': '12334567890',
        'dialog': {
            'messages': [
                {'author': 'user', 'text': 'У вас лучшая поддержка!!!'},
            ],
        },
        'features': [{'key': 'feature2', 'value': 2}],
    }

    @mockserver.json_handler(
        '/supportai-models-alpha/internal/supportai-models/v2/apply/text_classify',  # noqa pylint: disable=line-too-long
    )
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(data=handler_data)

    support_request = requests.SupportV1(
        log_extra=None,
        middlewares=[],
        project_id='sunlight',
        simulated=False,
        mocked=False,
        is_async=False,
        ask_features=False,
        body=models.SupportRequest.deserialize(request),
        version='draft',
    )

    response = await support_v1.handle_old(support_request, web_context)

    assert response.status == 200
    assert response.data.reply is not None
    assert response.data.reply.text == 'Feature2 is 2'

    delete_resp = await web_app_client.delete(
        '/v1/scenarios/3', params={'project_slug': 'sunlight', 'user_id': 1},
    )

    assert delete_resp.status == 200

    response = await support_v1.handle_old(support_request, web_context)

    assert response.status == 200
    assert response.data.reply is None


async def test_draft_agent_cache_reload(
        web_context, web_app_client, mockserver, mocked_agent_handlers,
):
    # change draft
    await web_app_client.put(
        '/v1/topics/2',
        json={
            'id': '2',
            'slug': 'topic1',
            'title': 'Topic 1',
            'rule': 'false',
        },
        params={'project_slug': 'sunlight', 'user_id': 34},
    )

    # start reload
    response = await web_app_client.post(
        '/v1/versions/draft/reload',
        params={'project_slug': 'sunlight', 'user_id': 34},
    )

    assert response.status == 200

    # Wait for draft cache reload
    draft_cache = web_context.supportai_agent_cache._draft_cache
    await draft_cache.refresh_cache()
    await draft_cache.wait_load()

    handler_data = {
        'most_probable_topic': 'topic1',
        'probabilities': [
            {'topic_name': 'topic2', 'probability': 0.1},
            {'topic_name': 'topic1', 'probability': 0.9},
        ],
    }

    request = {
        'chat_id': '12334567890',
        'dialog': {
            'messages': [
                {'author': 'user', 'text': 'У вас лучшая поддержка!!!'},
            ],
        },
        'features': [{'key': 'feature1', 'value': 1}],
    }

    @mockserver.json_handler(
        '/supportai-models-alpha/internal/supportai-models/v2/apply/text_classify',  # noqa pylint: disable=line-too-long
    )
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(data=handler_data)

    support_request = requests.SupportV1(
        log_extra=None,
        middlewares=[],
        project_id='sunlight',
        simulated=False,
        mocked=False,
        is_async=False,
        ask_features=False,
        body=models.SupportRequest.deserialize(request),
        version='draft',
    )

    # Use straight call to handle,
    # because web app is another thread
    # and cache can not be reloaded correctly
    response = await support_v1.handle_old(support_request, web_context)

    assert response.status == 200
    assert response.data.reply is None

    # Second check to ensure db is not locked
    await draft_cache.refresh_cache()
    await draft_cache.wait_load()

    response = await support_v1.handle_old(support_request, web_context)

    assert response.status == 200
    assert response.data.reply is None


async def test_draft_agent_cache_error(
        web_context, web_app_client, mockserver, mocked_agent_handlers,
):
    # change draft with visible in answer change and incorrect
    await web_app_client.put(
        '/v1/topics/2',
        json={
            'id': '2',
            'slug': 'topic1',
            'title': 'Topic 1',
            'rule': 'false',
        },
        params={'project_slug': 'sunlight', 'user_id': 34},
    )

    await web_app_client.post(
        '/v1/configs/custom',
        json={'id': '', 'value': {'general': {'lang': 228}}},
        params={'project_slug': 'sunlight', 'user_id': 34},
    )

    # start reload
    response = await web_app_client.post(
        '/v1/versions/draft/reload',
        params={'project_slug': 'sunlight', 'user_id': 34},
    )

    assert response.status == 200

    # Wait for draft cache reload
    draft_cache = web_context.supportai_agent_cache._draft_cache
    await draft_cache.refresh_cache()
    await draft_cache.wait_load()

    handler_data = {
        'most_probable_topic': 'topic1',
        'probabilities': [
            {'topic_name': 'topic2', 'probability': 0.1},
            {'topic_name': 'topic1', 'probability': 0.9},
        ],
    }

    request = {
        'chat_id': '12334567890',
        'dialog': {
            'messages': [
                {'author': 'user', 'text': 'У вас лучшая поддержка!!!'},
            ],
        },
        'features': [{'key': 'feature1', 'value': 1}],
    }

    @mockserver.json_handler(
        '/supportai-models-alpha/internal/supportai-models/v2/apply/text_classify',  # noqa pylint: disable=line-too-long
    )
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(data=handler_data)

    support_request = requests.SupportV1(
        log_extra=None,
        middlewares=[],
        project_id='sunlight',
        simulated=False,
        mocked=False,
        is_async=False,
        ask_features=False,
        body=models.SupportRequest.deserialize(request),
        version='draft',
    )

    # Use straight call to handle,
    # because web app is another thread
    # and cache can not be reloaded correctly
    response = await support_v1.handle_old(support_request, web_context)

    assert response.status == 200
    assert response.data.reply is not None

    version_response = await web_app_client.get(
        '/v1/versions/draft',
        params={'project_slug': 'sunlight', 'user_id': 34},
    )

    assert response.status == 200
    version_response_json = await version_response.json()

    assert version_response_json['status'] == 'error'
    assert 'error_description' in version_response_json


async def test_agent_cache_random_choice(
        web_context,
        web_app_client,
        monkeypatch,
        mockserver,
        mocked_agent_handlers,
):

    version = db_models.Version(
        id=1,
        project_slug='sunlight',
        version=0,
        draft=False,
        hidden=False,
        created=datetime.datetime.now(),
        lock_id=None,
        need_to_load=False,
    )

    monkeypatch.setattr('random.Random.choices', lambda self, x, y: [version])
    agent_cache = await web_context.supportai_agent_cache.get_agent_cache(
        project_slug='sunlight', version=None,
    )

    assert agent_cache is None

    version.id = 2

    monkeypatch.setattr('random.Random.choices', lambda self, x, y: [version])
    agent_cache = await web_context.supportai_agent_cache.get_agent_cache(
        project_slug='sunlight', version=None,
    )

    assert agent_cache is not None
    assert agent_cache.version is not None
    assert agent_cache.version.id == 2


async def test_agent_cache_percentage(web_context, web_app_client, mockserver):

    agent_cache = await web_context.supportai_agent_cache.get_agent_cache(
        project_slug='sunlight', version=None, chat_id=1,
    )

    assert agent_cache is not None
    assert agent_cache.version is not None
    assert agent_cache.version.id == 2

    response = await web_app_client.post(
        '/v1/versions/percentage?project_slug=sunlight&user_id=34',
        json={
            'mapping': [
                {'version_id': 2, 'percentage': 0},
                {'version_id': 1, 'percentage': 100},
            ],
        },
    )

    assert response.status == 200

    await web_context.supportai_agent_cache.refresh_cache()

    agent_cache = await web_context.supportai_agent_cache.get_agent_cache(
        project_slug='sunlight', version=None, chat_id=2,
    )

    assert agent_cache is not None
    assert agent_cache.version is not None
    assert agent_cache.version.id == 1


async def test_agent_cache_chat_id_random(
        web_context, web_app_client, mockserver,
):

    await web_app_client.post(
        '/v1/versions/percentage?project_slug=sunlight',
        json={
            'mapping': [
                {'version_id': 1, 'percentage': 50},
                {'version_id': 2, 'percentage': 50},
            ],
        },
    )

    agent_cache = await web_context.supportai_agent_cache.get_agent_cache(
        project_slug='sunlight', version=None, chat_id=1,
    )

    assert agent_cache is not None
    assert agent_cache.version is not None
    version_id = agent_cache.version.id

    for _ in range(10):
        agent_cache = await web_context.supportai_agent_cache.get_agent_cache(
            project_slug='sunlight', version=None, chat_id=1,
        )

        assert agent_cache is not None
        assert agent_cache.version is not None
        assert agent_cache.version.id == version_id
