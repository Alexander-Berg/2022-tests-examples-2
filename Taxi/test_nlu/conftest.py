# pylint: disable=C0302
from typing import List

import pytest

from client_supportai_models import constants

import generated.clients_libs.supportai_models.supportai_lib as supportai_lib_module  # noqa pylint: disable=line-too-long
from taxi.clients import translate

from supportai.common import configuration as configuration_module
from supportai.common import nlu as nlu_module


@pytest.fixture(name='create_nlu')
async def create_nlu_fixture(
        load_json,
        web_context,
        mock,
        mockserver,
        monkeypatch,
        client_supportai_models_mock,
):
    async def nlu_fn(
            config_path,
            namespace,
            supportai_models_response,
            wiz_response,
            dialogue_acts_response=None,
            text_embed_response=None,
            zeliboba_intent_response=None,
            reference_phrases_response=None,
            default_spell_handle=True,
            default_translator_handle=True,
            default_detector_handle=True,
            default_models_info=False,
            flags=None,
    ):
        if flags is None:
            flags = {}
        if supportai_models_response is not None:
            client_supportai_models_mock(
                constants.MULTICLASS_CLASSIFICATION, supportai_models_response,
            )

        if text_embed_response is not None:
            client_supportai_models_mock(
                constants.TEXT_EMBEDDING, text_embed_response,
            )

        if dialogue_acts_response is not None:
            client_supportai_models_mock(
                constants.MULTIHEAD_CLASSIFICATION, dialogue_acts_response,
            )

        @mockserver.json_handler('/supportai-zeliboba/autosupport/classify')
        async def _(request):
            return mockserver.make_response(
                status=200, json=zeliboba_intent_response,
            )

        @mockserver.json_handler(
            '/supportai-reference-phrases/supportai-reference-phrases/v1/classify',  # noqa pylint: disable=line-too-long
        )
        async def _(request):
            return mockserver.make_response(
                status=200, json=reference_phrases_response,
            )

        if default_models_info:

            @mockserver.json_handler(
                '/supportai-models/internal/supportai-models/v1/model_info_by_slugs_versions',  # noqa pylint: disable=line-too-long
                # noqa pylint: disable=line-too-long
            )
            async def _(_):
                return mockserver.make_response(
                    status=200,
                    json={
                        'models': [
                            {
                                'id': '5',
                                'title': 'Тестовая модель',
                                'slug': 'model_test',
                                'version': '1',
                                'type': 'one_message_text_classification',
                                'preprocess_type': 'one_message',
                                'language': 'ru',
                                'model_kind': 'sentence_bert',
                                'model_arch': 'text_classification',
                            },
                        ],
                    },
                )

        if isinstance(wiz_response, str):

            @mockserver.json_handler('/wizard/wizard')
            async def _(request):
                return mockserver.make_response(
                    status=200, response=wiz_response,
                )

        else:

            @mockserver.json_handler('/wizard/wizard')
            async def _(request):
                return mockserver.make_response(status=200, json=wiz_response)

        if default_spell_handle:

            @mockserver.json_handler('/spellchecker/misspell.json/check')
            async def _(request):
                return mockserver.make_response(
                    status=200,
                    json={
                        'code': 200,
                        'f': {},
                        'flags': 0,
                        'lang': '*',
                        'rule': '',
                        'r': 0,
                    },
                )

        if default_translator_handle:

            @mockserver.json_handler('/translator/tr.json/translate')
            async def _(request):
                return mockserver.make_response(
                    status=200,
                    json={'code': 200, 'lang': 'ru-en', 'text': []},
                )

        if default_detector_handle:

            @mockserver.json_handler('/translator/tr.json/detect')
            async def _(request):
                return mockserver.make_response(
                    status=200, json={'code': 200, 'lang': 'ru'},
                )

        @mock
        async def _dummy_detect(*args, **kwargs):
            return {'lang': 'ru'}

        monkeypatch.setattr(
            translate.TranslateAPIClient, 'detect_language', _dummy_detect,
        )

        nlu = nlu_module.NLU(namespace=namespace)
        configuration = configuration_module.Configuration.deserialize(
            load_json(config_path),
        )

        await configuration.service_patch_configuration(web_context)

        nlu.load_from_configuration(
            configuration.general,
            configuration.nlu,
            '0',
            flags=configuration_module.CoreFlags(**flags),
        )

        await nlu.prepare()
        return nlu

    to_clean_up: List[nlu_module.NLU] = []

    async def nlu_fn_wrap(
            config_path,
            namespace,
            supportai_models_response,
            wiz_response,
            dialogue_acts_response=None,
            text_embed_response=None,
            zeliboba_intent_response=None,
            reference_phrases_response=None,
            default_spell_handle=True,
            default_translator_handle=True,
            default_detector_handle=True,
            default_models_info=True,
            flags=None,
    ):
        if flags is None:
            flags = {}
        nlu = await nlu_fn(
            config_path,
            namespace,
            supportai_models_response,
            wiz_response,
            dialogue_acts_response,
            text_embed_response,
            zeliboba_intent_response,
            reference_phrases_response,
            default_spell_handle,
            default_translator_handle,
            default_detector_handle,
            default_models_info,
            flags=flags,
        )
        to_clean_up.append(nlu)
        return nlu

    yield nlu_fn_wrap

    for _nlu in to_clean_up:
        try:
            await _nlu.destroy()
        finally:
            pass
