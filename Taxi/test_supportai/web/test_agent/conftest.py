# pylint: disable=C0302
import pytest

from client_supportai_models import constants
from taxi.clients import translate

from supportai.common import agent as agent_module
from supportai.common import configuration as configuration_module


@pytest.fixture(name='create_agent')
def create_agent_fixture(
        load_json,
        get_directory_path,
        web_context,
        mock,
        mockserver,
        monkeypatch,
        client_supportai_models_mock,
):
    async def agent_fn(
            namespace, config_path, supportai_models_response, flags=None,
    ):
        configuration_data = load_json(config_path)
        agent = agent_module.Agent(namespace=namespace)

        configuration = configuration_module.Configuration.deserialize(
            configuration_data,
        )

        if flags:
            configuration.flags = flags

        agent.load_from_configuration(configuration)
        client_supportai_models_mock(
            constants.MULTICLASS_CLASSIFICATION, supportai_models_response,
        )

        @mockserver.json_handler(
            '/supportai-models/internal/supportai-models/v1/model_info_by_slugs_versions',  # noqa pylint: disable=line-too-long
        )
        async def _(_):
            return mockserver.make_response(
                status=200,
                json={
                    'models': [
                        {
                            'id': '5',
                            'title': 'Тестовая модель',
                            'slug': 'test_model',
                            'version': '1',
                            'type': 'one_message_text_classification',
                            'preprocess_type': 'one_message',
                            'language': 'rus',
                        },
                    ],
                },
            )

        @mockserver.json_handler('/wizard/wizard')
        async def _(request):
            return mockserver.make_response(
                status=200,
                json={
                    'rules': {
                        'Date': {
                            'Pos': '0',
                            'Length': '1',
                            'Body': '{"Day":"1D"}',
                        },
                        'GeoAddr': {
                            'Body': '{"Variants":[{"City":"москва","HasOwnGeoIds":true,"Weight":0.986,"CityIDs":[213]}],"BestGeo":213,"BestInheritedGeo":213}',  # noqa
                        },
                    },
                },
            )

        @mockserver.json_handler('/spellchecker/misspell.json/check')
        async def _(request):
            return mockserver.make_response(
                status=200,
                json={
                    'code': 200,
                    'flags': 0,
                    'lang': 'ru',
                    'rule': 'rule',
                    'f': {'use_py3_isoformat': True},
                },
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

        await agent.prepare()

        return agent

    return agent_fn
