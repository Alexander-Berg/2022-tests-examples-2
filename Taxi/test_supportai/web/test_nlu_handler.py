import pytest

from taxi.clients import translate


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        CLIENT_SUPPORTAI_MODELS_SETTINGS={'use_v2_models_handlers': True},
    ),
]


@pytest.mark.pgsql('supportai', files=['default.sql', 'data.sql'])
async def test_nlu_handler(web_app_client, mockserver, mock, monkeypatch):
    @mockserver.json_handler(
        '/supportai-models-alpha/internal/supportai-models/v2/apply/text_classify',  # noqa pylint: disable=line-too-long
    )
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={
                'most_probable_topic': 'topic1',
                'probabilities': [
                    {'topic_name': 'topic1', 'probability': 0.8},
                    {'topic_name': 'hello', 'probability': 0.15},
                    {'topic_name': 'bye', 'probability': 0.05},
                ],
            },
        )

    @mockserver.json_handler('/wizard/wizard')
    async def _(request):
        return mockserver.make_response(
            status=200, json={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        )

    @mock
    async def _dummy_detect(*args, **kwargs):
        return {'code': 200, 'lang': 'ru'}

    @mock
    async def _dummy_translate(*args, **kwargs):
        return {'code': 200, 'lang': 'ru-ru', 'text': ['Отлично']}

    monkeypatch.setattr(
        translate.TranslateAPIClient, 'detect_language', _dummy_detect,
    )
    monkeypatch.setattr(
        translate.TranslateAPIClient, 'translate', _dummy_translate,
    )

    response = await web_app_client.post(
        '/supportai/v1/nlu?project_slug=ya_lavka&version=draft',
        json={
            'dialog': {
                'messages': [{'text': 'help help help', 'author': 'user'}],
            },
            'features': [{'key': 'tariff', 'value': 'business'}],
        },
    )
    assert response.status == 200

    response_json = await response.json()
    assert response_json['sure_topic'] == 'topic1'
    assert response_json['custom_model_sure_topic'] == 'topic1'
    assert len(response_json['features']) == 13
    assert 'intent' in set(
        feature['key'] for feature in response_json['features']
    )
