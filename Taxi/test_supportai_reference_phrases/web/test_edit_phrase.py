import pytest

from client_supportai_models import constants
from taxi.clients import translate


@pytest.fixture(name='mock_translation', autouse=True)
def _mock_translation(mock, monkeypatch):
    def mock_handels(detect_lang_response, translate_response):
        @mock
        async def _dummy_detect(*args, **kwargs):
            return detect_lang_response

        monkeypatch.setattr(
            translate.TranslateAPIClient, 'detect_language', _dummy_detect,
        )

        @mock
        async def _dummy_translate(*args, **kwargs):
            if translate_response.get('exception', False):
                raise Exception('Failed to trainslate text')
            return translate_response

        monkeypatch.setattr(
            translate.TranslateAPIClient, 'translate', _dummy_translate,
        )

    return mock_handels


@pytest.mark.pgsql('supportai_reference_phrases', files=['edit_phrases.sql'])
async def test_edit_phrase(
        web_app_client, client_supportai_models_mock, mock_translation,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    mock_translation({'lang': 'en'}, {'lang': 'en-ru', 'text': ['немного']})

    project_id = 'test_project'
    id_to_edit = str(3)
    new_phrase = {
        'text': 'edited_text',
        'topic': 'test_topic10',
        'type': 'addition',
    }

    response = await web_app_client.put(
        f'/v1/matrix/{id_to_edit}?project_slug={project_id}', json=new_phrase,
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['id'] == id_to_edit
    assert response_json['text'] == new_phrase['text']
