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


async def test_change_matrix(
        web_app_client, client_supportai_models_mock, mock_translation,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    mock_translation({'lang': 'en'}, {'lang': 'en-ru', 'text': ['немного']})

    response = await web_app_client.put(
        '/v1/matrix?project_slug=project_1',
        json={
            'matrix': [{'text': 'some', 'topic': 'topic_1', 'include': True}],
        },
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['matrix']) == 1

    response = await web_app_client.put(
        '/v1/matrix?project_slug=project_1',
        json={
            'matrix': [
                {'text': 'some 2', 'topic': 'topic_2', 'include': True},
            ],
            'delete_matrix_rows': [{'id': response_json['matrix'][0]['id']}],
        },
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['matrix']) == 1

    response = await web_app_client.put(
        '/v1/matrix?project_slug=project_1',
        json={
            'matrix': [],
            'delete_matrix_rows': [{'id': response_json['matrix'][0]['id']}],
        },
    )
    assert response.status == 200
    response_json = await response.json()
    assert not response_json['matrix']


async def test_change_matrix_empty(
        web_app_client, client_supportai_models_mock, mock_translation,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    mock_translation({'lang': 'en'}, {'lang': 'en-ru', 'text': ['немного']})

    response = await web_app_client.put(
        '/v1/matrix?project_slug=project_1', json={'matrix': []},
    )
    assert response.status == 200
    response_json = await response.json()
    assert not response_json['matrix']


async def test_change_matrix_lang_not_detected(
        web_app_client, client_supportai_models_mock, mock_translation,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    mock_translation({'lang': ''}, {'lang': 'en-ru', 'text': ['немного']})

    response = await web_app_client.put(
        '/v1/matrix?project_slug=project_1',
        json={
            'matrix': [{'text': 'some', 'topic': 'topic_1', 'include': True}],
        },
    )
    assert response.status == 200

    response = await web_app_client.get('/v1/matrix?project_slug=project_1')
    assert response.status == 200
    response_json = await response.json()
    assert response_json['matrix'][0]['text'] == 'some'


async def test_change_matrix_lang_tr(
        web_app_client, client_supportai_models_mock, mock_translation,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'text': '', 'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    mock_translation(
        {'lang': 'tr'}, {'lang': 'tr-ru', 'text': ['здравствуйте']},
    )

    response = await web_app_client.put(
        '/v1/matrix?project_slug=project_2',
        json={
            'matrix': [
                {'text': 'merhaba', 'topic': 'topic_1', 'include': True},
            ],
        },
    )
    assert response.status == 200

    response = await web_app_client.get('/v1/matrix?project_slug=project_2')
    assert response.status == 200
    response_json = await response.json()
    assert response_json['matrix'][0]['text'] == 'merhaba'


@pytest.mark.config(
    SUPPORTAI_REFERENCE_PHRASES_PROJECT={
        'project_2': {'translate': True},
        '__default__': {'translate': False},
    },
)
async def test_change_matrix_lang_exception_all(
        web_app_client,
        web_context,
        client_supportai_models_mock,
        mock_translation,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'text': '', 'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    mock_translation({'lang': 'tr'}, {'exception': True})

    response = await web_app_client.put(
        '/v1/matrix?project_slug=project_2',
        json={
            'matrix': [
                {'text': 'invalid txt 1', 'topic': 'topic_1', 'include': True},
                {'text': 'invalid txt 2', 'topic': 'topic_1', 'include': True},
            ],
        },
    )
    assert response.status == 500
