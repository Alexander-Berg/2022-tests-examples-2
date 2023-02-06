import pytest
# pylint: disable=C0302

import generated.clients_libs.supportai_models.supportai_lib as supportai_lib_module  # noqa pylint: disable=line-too-long

from supportai.common import configuration as configuration_module
from supportai.common import feature as feature_module
from supportai.common import state as state_module
from supportai.common.nlu.preprocessor import (
    preprocessor as preprocessor_module,
)


async def test_preprocessor(create_nlu, web_context, core_flags):

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {
                        'author': 'user',
                        'text': 'препроцессор тест',
                        'preprocessor_results': {
                            'spelled_message': 'препроцессор тест',
                            'normalized_message': 'препроцессор тест',
                        },
                    },
                    {'author': 'user', 'text': 'тест препроцессора'},
                ],
            },
            'features': [],
        },
    )

    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    state = state_module.State(feature_layers=[])
    nlu = await create_nlu(
        config_path='configuration_net_rules_combination.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {}},
    )
    core_flags = configuration_module.CoreFlags(**{'preprocess': True})
    nlu_response = await nlu(request, state, web_context, core_flags)
    basic_features = nlu_response.features

    assert basic_features['united_user_messages'].value == '\n'.join(
        [message.text for message in request.dialog.messages],
    )
    assert basic_features['last_user_message'].value == 'тест препроцессора'
    assert (
        basic_features['normalized_last_user_message'].value
        == 'тест препроцессор'
    )
    assert (
        basic_features['normalized_united_user_messages'].value
        == 'препроцессор тест\nтест препроцессор'
    )


async def test_preprocessor_flag(create_nlu, web_context, core_flags):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {
                        'author': 'user',
                        'text': 'хочу отменить урок',
                        'preprocessor_results': {
                            'spelled_message': 'хочу отменить урок',
                            'normalized_message': 'хотеть отменить урок',
                        },
                    },
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {
                        'author': 'user',
                        'text': 'очень хочу отменить урок, а то не буду!',
                    },
                    {'author': 'support', 'text': 'и что?)'},
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[])
    nlu = await create_nlu(
        config_path='configuration_with_no_project_model.json',
        namespace='foxford_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
    )

    core_flags = configuration_module.CoreFlags(**{'preprocess': True})

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        nlu_response.features['last_user_message'].value
        == 'очень хочу отменить урок, а то не буду!'
    )
    assert (
        nlu_response.features['united_user_messages'].value
        == 'хочу отменить урок\nочень хочу отменить урок, а то не буду!'
    )
    assert (
        nlu_response.features['normalized_last_user_message'].value
        == 'очень хотеть отменить урок, а то не буду!'
    )
    assert (
        nlu_response.features['normalized_united_user_messages'].value
        == 'хотеть отменить урок\nочень хотеть отменить урок, а то не буду!'
    )


async def test_net_rules_combination_topic_with_preprocessor_features(
        create_nlu, web_context, core_flags,
):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }
    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {'author': 'user', 'text': 'как отменить урок!'},
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[])
    nlu = await create_nlu(
        config_path='configuration_net_rules_combination.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {}},
    )

    core_flags = configuration_module.CoreFlags(**{'preprocess': True})
    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        nlu_response.custom_model_features['most_probable_topic'].value
        == 'Cancel_lesson'
    )
    assert nlu_response.sure_topic == 'Cancel_lesson_how_to'


async def test_preprocessor_text_filter_html(
        create_nlu, web_context, core_flags,
):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {
                        'author': 'user',
                        'text': """<div>
                                    <span class="validity"></span>
                                    <p>ребёнок не может зайти в МЭШ</p>
                                    </div>
                                    <div>""",
                    },
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'united_user_messages': feature_module.Feature.as_defined(
                    key='united_user_messages', value='хочу отменить урок',
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_only_preprocessor.json',
        namespace='mesh_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
    )

    core_flags = configuration_module.CoreFlags(**{'preprocess': True})

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        nlu_response.features['last_user_message'].value
        == 'ребёнок не может зайти в мэш'
    )


async def test_preprocessor_text_filter(create_nlu, web_context, core_flags):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {
                        'author': 'user',
                        'text': """Описание проблемы: описание:
                                    ребёнок не может зайти в МЭШ""",
                    },
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[])
    nlu = await create_nlu(
        config_path='configuration_only_preprocessor.json',
        namespace='mesh_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
    )

    core_flags = configuration_module.CoreFlags(**{'preprocess': True})

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        nlu_response.features['last_user_message'].value
        == 'ребёнок не может зайти в мэш'
    )


async def test_preprocessor_text_filter_with_none(
        create_nlu, web_context, core_flags,
):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {
                        'author': 'user',
                        'text': 'один два три четыре тест пять' '',
                    },
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[])
    nlu = await create_nlu(
        config_path='configuration_only_preprocessor.json',
        namespace='mesh_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
    )

    core_flags = configuration_module.CoreFlags(**{'preprocess': True})

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        nlu_response.features['last_user_message'].value
        == 'один два три четыре '
    )


async def test_preprocessor_replacer(create_nlu, web_context, core_flags):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {
                        'author': 'user',
                        'text': (
                            r"""У mеня bолиt жиvот!!!"""
                            r"""Я уже 12 часов ничего     не     ел!!!"""
                            r""" Мой номер 83231459897."""
                        ),
                    },
                ],
            },
            'features': [],
        },
    )

    state = state_module.State(
        feature_layers=[
            {
                'united_user_messages': feature_module.Feature.as_defined(
                    key='united_user_messages', value='хочу отменить урок',
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_only_text_replacer.json',
        namespace='mesh_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
    )

    core_flags = configuration_module.CoreFlags(**{'preprocess': True})

    nlu_response = await nlu(request, state, web_context, core_flags)
    assert (
        nlu_response.features['last_user_message'].value
        == 'у_меня_болит_живот.я_уже_ЧИСЛО_часов_ничего_не_ел._мой_номер_ЧИСЛО.'  # noqa pylint: disable=line-too-long
    )


async def test_preprocessor_normalizer(create_nlu, web_context, core_flags):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {'author': 'user', 'text': 'Я хочу отдохнуть сегодня'},
                ],
            },
            'features': [],
        },
    )

    state = state_module.State(
        feature_layers=[
            {
                'united_user_messages': feature_module.Feature.as_defined(
                    key='united_user_messages', value='хочу отменить урок',
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_only_text_normalizer.json',
        namespace='mesh_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
    )

    core_flags = configuration_module.CoreFlags(**{'preprocess': True})

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        nlu_response.features['normalized_last_user_message'].value
        == 'я хотеть отдохнуть сегодня'
    )


async def test_preprocessor_patched(create_nlu, web_context, core_flags):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    nlu = await create_nlu(
        config_path='configuration_preprocessor_patched.json',
        namespace='mesh_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
    )

    assert nlu.get_preprocessor_mapping() == {
        'test_model': preprocessor_module.ModelParams(
            type='one_message', language='ru',
        ),
    }


async def test_preprocessor_speller_ru(
        create_nlu, web_context, mockserver, core_flags,
):
    @mockserver.json_handler('/spellchecker/misspell.json/check')
    async def _(request):
        return mockserver.make_response(
            status=201,
            json={
                'code': 201,
                'lang': 'ru',
                'rule': 'Misspell',
                'flags': 0,
                'r': 10000,
                'srcText': 'хачу отминить урок',
                'text': 'хочу отменить урок',
                'f': {},
            },
        )

    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [{'author': 'user', 'text': 'хачу отминить урок'}],
            },
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[])
    nlu = await create_nlu(
        config_path='configuration_only_preprocessor.json',
        namespace='mesh_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        default_spell_handle=False,
    )

    core_flags = configuration_module.CoreFlags(**{'preprocess': True})

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        nlu_response.features['last_user_message'].value
        == 'хочу отменить урок'
    )


async def test_preprocessor_speller_ru_not_correct(
        create_nlu, web_context, mockserver, core_flags,
):
    @mockserver.json_handler('/spellchecker/misspell.json/check')
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={
                'code': 200,
                'lang': '',
                'rule': '',
                'flags': 0,
                'r': 0,
                'f': {},
            },
        )

    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [{'author': 'user', 'text': 'хачу отминить урок'}],
            },
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[])
    nlu = await create_nlu(
        config_path='configuration_only_preprocessor.json',
        namespace='mesh_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        default_spell_handle=False,
    )
    core_flags = configuration_module.CoreFlags(**{'preprocess': True})

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        nlu_response.features['last_user_message'].value
        == 'хачу отминить урок'
    )


async def test_preprocessor_translator_default_en(
        create_nlu, web_context, mockserver, core_flags,
):
    @mockserver.json_handler('/translator/tr.json/translate')
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={
                'code': 200,
                'lang': 'ru-en',
                'text': ['Hello! Uncle, how are you'],
            },
        )

    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Привет! Дядечка, ты как?'},
                ],
            },
            'features': [],
        },
    )

    state = state_module.State(feature_layers=[])
    nlu = await create_nlu(
        config_path='configuration_only_preprocessor.json',
        namespace='mesh_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        default_translator_handle=False,
    )
    core_flags = configuration_module.CoreFlags(**{'preprocess': True})

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        nlu_response.features['text_en'].value == 'Hello! Uncle, how are you'
    )


async def test_preprocessor_lang_detector(
        create_nlu, web_context, mockserver, core_flags,
):
    @mockserver.json_handler('/translator/tr.json/detect')
    async def _(request):

        text = request.form['text']
        if text == 'hello! uncle, how are you?':
            return mockserver.make_response(
                status=200, json={'code': 200, 'lang': 'en'},
            )
        if text == '5':
            return mockserver.make_response(
                status=200, json={'code': 200, 'lang': ''},
            )

    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Hello! Uncle, how are you?'},
                ],
            },
            'features': [],
        },
    )

    state = state_module.State(feature_layers=[])
    nlu = await create_nlu(
        config_path='configuration_only_preprocessor.json',
        namespace='mesh_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        default_detector_handle=False,
    )

    core_flags = configuration_module.CoreFlags(**{'preprocess': True})

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert nlu_response.features['language'].value == 'en'

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {'messages': [{'author': 'user', 'text': '5'}]},
            'features': [],
        },
    )

    nlu_response = await nlu(request, state, web_context, core_flags)
    assert nlu_response.features['language'].value == 'en'


async def test_preprocessor_features_mapping(
        create_nlu, web_context, core_flags,
):

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [{'author': 'user', 'text': 'тест препроцессора'}],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'task_language': feature_module.Feature.as_defined(
                    key='task_language', value='az',
                ),
            },
        ],
    )

    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    nlu = await create_nlu(
        config_path='configuration_only_preprocessor.json',
        namespace='mesh_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        default_detector_handle=False,
    )

    core_flags = configuration_module.CoreFlags(**{'preprocess': True})

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert nlu_response.features['language'].value == 'az'


async def test_preprocessor_saved_features(
        create_nlu, web_context, mockserver, core_flags,
):
    @mockserver.json_handler('/spellchecker/misspell.json/check')
    async def _(request):
        return mockserver.make_response(
            status=201,
            json={
                'code': 201,
                'lang': 'ru',
                'rule': 'Misspell',
                'flags': 0,
                'r': 10000,
                'srcText': 'превет, сдесь были ашибки',
                'text': 'привет, здесь были ошибки',
                'f': {},
            },
        )

    @mockserver.json_handler('/translator/tr.json/translate')
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={
                'code': 200,
                'lang': 'ru-en',
                'text': ['hello, here is error'],
            },
        )

    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Превет, сдесь  были ашибки'},
                ],
            },
            'features': [],
        },
    )

    state = state_module.State(feature_layers=[])
    nlu = await create_nlu(
        config_path='configuration_only_preprocessor.json',
        namespace='mesh_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        default_translator_handle=False,
        default_spell_handle=False,
    )

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        nlu_response.preprocessor_results[-1].spelled_message
        == 'привет, здесь были ошибки'
    )
    assert (
        nlu_response.preprocessor_results[-1].normalized_message
        == 'привет, здесь были ошибки'
    )
    assert (
        nlu_response.preprocessor_results[-1].translated_message
        == 'hello, here is error'
    )


@pytest.mark.core_flags(dialog_features_from_context=True)
async def test_preprocessor_iterative_features(
        create_nlu, web_context, mockserver, core_flags,
):
    @mockserver.json_handler('/translator/tr.json/translate')
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={'code': 200, 'lang': 'ru-en', 'text': ['i have problem']},
        )

    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {
                        'author': 'user',
                        'text': 'Превет',
                        'preprocessor_results': {
                            'spelled_message': 'привет',
                            'normalized_message': 'привет',
                            'translated_message': 'hello',
                        },
                    },
                    {'author': 'user', 'text': 'у меня проблема'},
                ],
            },
            'features': [],
        },
    )

    state = state_module.State(feature_layers=[])
    nlu = await create_nlu(
        config_path='configuration_only_preprocessor.json',
        namespace='mesh_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        default_translator_handle=False,
    )

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        nlu_response.features['united_text_en'].value
        == 'hello\ni have problem'
    )
    assert (
        nlu_response.features['normalized_united_user_messages'].value
        == 'привет\nу меня проблема'
    )
    assert (
        nlu_response.features['united_user_messages'].value
        == 'привет\nу меня проблема'
    )


async def test_preprocessor_without_results(
        create_nlu, web_context, mockserver, core_flags,
):
    @mockserver.json_handler('/translator/tr.json/translate')
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={'code': 200, 'lang': 'ru-en', 'text': ['i have problem']},
        )

    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Превет'},
                    {'author': 'ai', 'text': 'ничем не могу помочь'},
                    {'author': 'user', 'text': 'спасибо'},
                    {'author': 'user', 'text': 'а ты очень полезная железка'},
                ],
            },
            'features': [],
        },
    )

    state = state_module.State(feature_layers=[])
    nlu = await create_nlu(
        config_path='configuration_only_preprocessor.json',
        namespace='mesh_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        default_translator_handle=False,
    )

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        '\n'.join(
            pr.spelled_message for pr in nlu_response.preprocessor_results
        )
        == 'превет\nничем не могу помочь\nспасибо\nа ты очень полезная железка'
    )

    assert (
        '\n'.join(
            pr.normalized_message for pr in nlu_response.preprocessor_results
        )
        == 'превет\nничем не могу помочь\nспасибо\nа ты очень полезная железка'
    )

    assert (
        '\n'.join(
            pr.translated_message for pr in nlu_response.preprocessor_results
        )
        == 'i have problem\ni have problem\ni have problem\ni have problem'
    )


async def test_preprocessor_last_user_utterance(
        create_nlu, web_context, mockserver, core_flags,
):
    @mockserver.json_handler('/translator/tr.json/translate')
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={'code': 200, 'lang': 'ru-en', 'text': ['i have problem']},
        )

    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'у меня проблема'},
                    {'author': 'ai', 'text': 'ничем не могу помочь'},
                    {'author': 'user', 'text': 'а ты очень полезная железка'},
                    {'author': 'user', 'text': 'просто супер полезная'},
                ],
            },
            'features': [],
        },
    )

    state = state_module.State(feature_layers=[])
    nlu = await create_nlu(
        config_path='configuration_only_preprocessor.json',
        namespace='mesh_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        default_translator_handle=False,
    )

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        nlu_response.features['last_user_utterance'].value
        == 'а ты очень полезная железка\nпросто супер полезная'
    )


async def test_preprocessor_last_user_utterance_last_ai_message(
        create_nlu, web_context, mockserver, core_flags,
):
    @mockserver.json_handler('/translator/tr.json/translate')
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={'code': 200, 'lang': 'ru-en', 'text': ['i have problem']},
        )

    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'у меня проблема'},
                    {'author': 'ai', 'text': 'ничем не могу помочь'},
                    {'author': 'user', 'text': 'а ты очень полезная железка'},
                    {'author': 'user', 'text': 'просто супер полезная'},
                    {'author': 'ai', 'text': 'поставьте мне оценку 5'},
                ],
            },
            'features': [],
        },
    )

    state = state_module.State(feature_layers=[])
    nlu = await create_nlu(
        config_path='configuration_only_preprocessor.json',
        namespace='mesh_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        default_translator_handle=False,
    )

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        nlu_response.features['last_user_utterance'].value
        == 'а ты очень полезная железка\nпросто супер полезная'
    )


async def test_get_number_of_words(
        create_nlu, web_context, mockserver, core_flags,
):

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {'messages': [{'author': 'user', 'text': 'Москва'}]},
            'features': [],
        },
    )

    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    state = state_module.State(feature_layers=[])
    nlu = await create_nlu(
        config_path='configuration_only_preprocessor.json',
        namespace='mesh_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        default_translator_handle=False,
    )

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert nlu_response.features['number_of_words'].value == 1
