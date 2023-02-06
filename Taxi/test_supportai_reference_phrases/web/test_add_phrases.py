# pylint: disable=W0621
import json

import pytest

from client_supportai_models import constants


@pytest.fixture(name='mock_translation', autouse=True)
def _mock_translation(patch_aiohttp_session, response_mock):
    def mock_handels(detect_lang, translate_response):
        url = 'http://translate.yandex.net/api/v1'

        @patch_aiohttp_session(f'{url}/tr.json/detect')
        def _patched_detect(method, url, params, json):
            return response_mock(json={'code': 200, 'lang': detect_lang})

        @patch_aiohttp_session(f'{url}/tr.json/translate', method='POST')
        def _patched_translate(method, url, params, data):
            json_ = {'code': 200, **translate_response}
            return response_mock(text=json.dumps(json_), json=json_)

    return mock_handels


@pytest.mark.xfail
@pytest.mark.pgsql('supportai_reference_phrases', files=['add_phrases.sql'])
async def test_add_no_phrases(
        web_app_client, client_supportai_models_mock, mock_translation,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    mock_translation({'lang': 'en'}, {'lang': 'en-ru', 'text': ['немного']})

    response = await web_app_client.post(
        '/v2/matrix?project_slug=project_1', json={},
    )
    assert response.status == 200
    response_json = await response.json()
    assert not response_json['phrases']


@pytest.mark.pgsql('supportai_reference_phrases', files=['add_phrases.sql'])
async def test_add_phrase(
        web_app_client, client_supportai_models_mock, mock_translation,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    mock_translation({'lang': 'en'}, {'lang': 'en-ru', 'text': ['немного']})

    response = await web_app_client.post(
        '/v1/matrix?project_slug=test_project',
        json={'text': 'some', 'topic': 'test_topic', 'type': 'addition'},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['text'] == 'some' and (
        response_json['topic'] == 'test_topic'
    )

    response = await web_app_client.get('/v1/matrix?project_slug=test_project')
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['matrix']) == 6


@pytest.mark.pgsql('supportai_reference_phrases', files=['add_phrases.sql'])
async def test_add_phrase_common_project(
        web_app_client, client_supportai_models_mock, mock_translation,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    mock_translation({'lang': 'en'}, {'lang': 'en-ru', 'text': ['немного']})

    response = await web_app_client.post(
        '/v1/matrix',
        json={
            'text': 'sample text here',
            'topic': 'test_common_topic',
            'type': 'addition',
        },
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['text'] == 'sample text here' and (
        response_json['topic'] == 'test_common_topic'
    )

    response = await web_app_client.get('/v1/matrix')
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['matrix']) == 5


@pytest.mark.pgsql('supportai_reference_phrases', files=['add_phrases.sql'])
async def test_add_phrase_new_project(
        web_app_client, client_supportai_models_mock, mock_translation,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    mock_translation({'lang': 'en'}, {'lang': 'en-ru', 'text': ['немного']})

    response = await web_app_client.post(
        '/v1/matrix?project_slug=new_project',
        json={
            'text': 'sample text here',
            'topic': 'test_new_topic',
            'type': 'addition',
        },
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['text'] == 'sample text here' and (
        response_json['topic'] == 'test_new_topic'
    )

    response = await web_app_client.get('/v1/matrix?project_slug=new_project')
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['matrix']) == 1


@pytest.mark.config(
    SUPPORTAI_REFERENCE_PHRASES_PROJECT={
        'project_1': {'translate': True},
        '__default__': {'translate': False},
    },
)
async def test_add_phrase_lang_not_detected(
        web_app_client, client_supportai_models_mock, mock_translation,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    mock_translation({'lang': ''}, {'lang': 'en-ru', 'text': ['немного']})

    response = await web_app_client.post(
        '/v1/matrix?project_slug=project_1',
        json={'text': 'some', 'topic': 'topic_1', 'type': 'addition'},
    )
    assert response.status == 200

    response = await web_app_client.get('/v1/matrix?project_slug=project_1')
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['matrix']) == 1
    assert response_json['matrix'][0]['text'] == 'some'


@pytest.mark.config(
    SUPPORTAI_REFERENCE_PHRASES_PROJECT={
        'project_2': {'translate': True},
        '__default__': {'translate': False},
    },
)
async def test_add_phrase_lang_tr(
        web_app_client, client_supportai_models_mock, mock_translation,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'text': '', 'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    mock_translation('tr', {'lang': 'tr-ru', 'text': ['здравствуйте']})

    response = await web_app_client.post(
        '/v1/matrix?project_slug=project_2',
        json={'text': 'merhaba', 'topic': 'topic_1', 'type': 'addition'},
    )
    assert response.status == 200

    response = await web_app_client.get('/v1/matrix?project_slug=project_2')
    assert response.status == 200
    response_json = await response.json()
    assert response_json['matrix'][0]['text'] == 'merhaba'


@pytest.mark.config(
    SUPPORTAI_REFERENCE_PHRASES_PROJECT={'__default__': {'translate': False}},
)
@pytest.mark.pgsql('supportai_reference_phrases', files=['add_phrases.sql'])
async def test_add_phrase_bulk(
        web_app_client,
        web_context,
        client_supportai_models_mock,
        mock_translation,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'text': '', 'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    mock_translation('', {'lang': 'en-ru', 'text': ['немного']})

    response = await web_app_client.post(
        '/v1/matrix/bulk?project_slug=test_project',
        json={
            'matrix': [
                {'text': 'текст 1', 'topic': 'topic_1', 'type': 'addition'},
                {'text': 'текст 2', 'topic': 'topic_2', 'type': 'addition'},
                {'text': 'текст 3', 'topic': 'topic_3', 'type': 'addition'},
            ],
        },
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['matrix']) == 3

    response = await web_app_client.get('/v1/matrix?project_slug=test_project')
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['matrix']) == 8


@pytest.mark.pgsql('supportai_reference_phrases', files=['add_phrases.sql'])
async def test_add_phrase_bulk_common_project(
        web_app_client,
        web_context,
        client_supportai_models_mock,
        mock_translation,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'text': '', 'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    mock_translation('', {'lang': 'en-ru', 'text': ['немного']})

    response = await web_app_client.post(
        '/v1/matrix/bulk',
        json={
            'matrix': [
                {'text': 'текст 1', 'topic': 'topic_1', 'type': 'addition'},
                {'text': 'текст 2', 'topic': 'topic_2', 'type': 'addition'},
                {'text': 'текст 3', 'topic': 'topic_3', 'type': 'addition'},
            ],
        },
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['matrix']) == 3

    response = await web_app_client.get('/v1/matrix')
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['matrix']) == 7


@pytest.mark.pgsql('supportai_reference_phrases', files=['add_phrases.sql'])
async def test_add_phrase_bulk_new_project(
        web_app_client,
        web_context,
        client_supportai_models_mock,
        mock_translation,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'text': '', 'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    mock_translation('', {'lang': 'en-ru', 'text': ['немного']})

    response = await web_app_client.get('/v1/matrix?project_slug=new_project')
    assert response.status == 200
    response_json = await response.json()
    assert not response_json['matrix']

    response = await web_app_client.post(
        '/v1/matrix/bulk?project_slug=new_project',
        json={
            'matrix': [
                {'text': 'текст 1', 'topic': 'topic_1', 'type': 'addition'},
                {'text': 'текст 2', 'topic': 'topic_2', 'type': 'addition'},
                {'text': 'текст 3', 'topic': 'topic_3', 'type': 'addition'},
            ],
        },
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['matrix']) == 3

    response = await web_app_client.get('/v1/matrix?project_slug=new_project')
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['matrix']) == 3
