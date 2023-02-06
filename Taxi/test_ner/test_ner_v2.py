# pylint: disable=C0302
import pytest

import generated.clients_libs.supportai_models.supportai_lib as supportai_lib_module  # noqa pylint: disable=line-too-long

from supportai.common import configuration as configuration_module
from supportai.common import state as state_module


@pytest.mark.parametrize('use_multilingual_ner', [True])
async def test_ner_v2_ru(
        create_nlu, web_context, core_flags, mockserver, use_multilingual_ner,
):
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
                        'title': 'Wizard',
                        'slug': 'wizard',
                        'version': '1',
                        'type': 'one_message_text_classification',
                        'preprocess_type': 'one_message',
                        'language': 'ru',
                        'model_kind': 'sentence_bert',
                        'model_arch': 'text_classification',
                    },
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

    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.1},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {
                        'author': 'user',
                        'text': (
                            'Отвезите меня в город Лондон на Бейкер-стрит'
                            '5 в 12:00. После чего позвоните Тэтчер Маргарет.'
                            'Её номер: +79853555535.'
                            # noqa pylint: disable=line-too-long
                        ),
                    },
                ],
            },
            'features': [],
        },
    )
    wiz_response = {
        'rules': {
            'Fio': {'RuleResult': '3', 'Fio': 'тэтчер маргарет'},
            'Date': {
                'Pos': '7',
                'Length': '3',
                'RuleResult': '3',
                'Body': '{"TimePrep":"в","Hour":12,"Min":0}',
            },
            'GeoAddr': {
                'Pos': '2',
                'prep_geo_addr': 'в лондон',
                'Type': 'City',
                'RuleResult': '3',
                'prep': 'в',
                'NormalizedText': 'лондон',
                'geo': 'в лондон',
                'geo_addr': 'лондон',
                'city': 'лондон',
            },
            'PhoneNumber': {
                'Normalized': '7(985)3555535',
                'Tel': 'tel_full:"8(985)3555535", tel_full:"7(985)3555535", tel_full:"(985)3555535"',  # noqa pylint: disable=line-too-long
                'End': '17',
                'Begin': '16',
                'RuleResult': '3',
                'PhoneNumberIsFound': '1',
                'TelLocal': '1',
            },
        },
    }
    state = state_module.State(feature_layers=[])

    default_models_info = not use_multilingual_ner
    nlu = await create_nlu(
        config_path='configuration_new_ner.json',
        namespace='yango',
        supportai_models_response=supportai_models_response,
        wiz_response=wiz_response,
        default_models_info=default_models_info,
        flags={'use_multilingual_ner': use_multilingual_ner},
    )
    nlu_response = await nlu(
        request,
        state,
        web_context,
        configuration_module.CoreFlags(
            **{'use_multilingual_ner': use_multilingual_ner},
        ),
    )

    assert nlu_response.entities['last_name_extractor'].values == ['тэтчер']
    assert nlu_response.entities['first_name_extractor'].values == ['маргарет']


@pytest.mark.parametrize('use_multilingual_ner', [True])
async def test_ner_v2_en(
        create_nlu, web_context, core_flags, mockserver, use_multilingual_ner,
):
    @mockserver.json_handler('/translator/tr.json/detect')
    async def _(request):
        return mockserver.make_response(
            status=200, json={'code': 200, 'lang': 'en'},
        )

    @mockserver.json_handler('/translator/tr.json/translate')
    async def _(request):
        request_text = request.form['text']
        request_lang_direction = request.form['lang']
        response_text = request_text
        if request_lang_direction == 'en-ru':
            response_text = """
            Отвези меня в Лондонский сити на Бейкер-стрит, 5, в 12:00.
            Тогда позвони Тэтчер Маргарет. А потом Уинстону Черчилю.
            Его номер: +79853555535. И я знаю пароль: абракадабра
            """
        elif request_lang_direction == 'ru-en':
            if request_text == 'тэтчер':
                response_text = 'tether'
            elif request_text == 'маргарет':
                response_text = 'margaret'
            elif request_text == 'уинстон':
                response_text = 'winston'
            elif request_text == 'черчиль':
                response_text = 'churchill'
        return mockserver.make_response(
            status=200,
            json={
                'code': 200,
                'lang': request_lang_direction,
                'text': [response_text],
            },
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
                        'slug': 'wizard',
                        'version': '1',
                        'type': 'one_message_text_classification',
                        'preprocess_type': 'one_message',
                        'language': 'ru',
                        'model_kind': 'wizard',
                        'model_arch': 'wizard',
                    },
                ],
            },
        )

    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.1},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {
                        'author': 'user',
                        'text': """
                        Take me to the city of London at 5 Baker Street at
                        12:00.Then call Thatcher Margaret and Winston Churchill
                        His number: +79853555535.
                        And I know password: abracadabra
                        """,
                    },
                ],
            },
            'features': [],
        },
    )
    wiz_response = {
        'rules': {
            'Fio': {
                'RuleResult': '3',
                'Fio': ['тэтчер маргарет', 'черчиль уинстон'],
            },
            'Date': {
                'Pos': '7',
                'Length': '3',
                'RuleResult': '3',
                'Body': '{"TimePrep":"в","Hour":12,"Min":0}',
            },
            'GeoAddr': {
                'Pos': '2',
                'prep_geo_addr': 'в лондон',
                'Type': 'City',
                'RuleResult': '3',
                'prep': 'в',
                'NormalizedText': 'лондон',
                'geo': 'в лондон',
                'geo_addr': 'лондон',
                'city': 'лондон',
            },
        },
    }
    state = state_module.State(feature_layers=[])

    nlu = await create_nlu(
        config_path='configuration_new_ner_en.json',
        namespace='yango',
        supportai_models_response=supportai_models_response,
        wiz_response=wiz_response,
        default_translator_handle=False,
        default_detector_handle=False,
        default_spell_handle=False,
        default_models_info=False,
        flags={'use_multilingual_ner': use_multilingual_ner},
    )

    nlu_response = await nlu(
        request,
        state,
        web_context,
        configuration_module.CoreFlags(
            **{'use_multilingual_ner': use_multilingual_ner},
        ),
    )

    assert nlu_response.entities['last_name_extractor'].values == [
        'tether',
        'churchill',
    ]
    assert nlu_response.entities['first_name_extractor'].values == [
        'margaret',
        'winston',
    ]
    assert nlu_response.entities['abracadabra_entity'].values == [
        'abracadabra',
    ]
