# pylint: disable=C0302
import pytest

import generated.clients_libs.supportai_models.supportai_lib as supportai_lib_module  # noqa pylint: disable=line-too-long

from supportai.common import configuration as configuration_module
from supportai.common import feature as feature_module
from supportai.common import state as state_module

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        SUPPORTAI_MODELS_SETTINGS={'use_v2_models_handlers': True},
    ),
]


@pytest.mark.parametrize('preprocess', [True, False])
async def test_only_net_topic(create_nlu, web_context, core_flags, preprocess):
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
                'messages': [{'author': 'user', 'text': 'отмените мой урок'}],
            },
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[{}])
    nlu = await create_nlu(
        config_path='configuration_only_net.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {}},
    )

    nlu_response = await nlu(
        request,
        state,
        web_context,
        configuration_module.CoreFlags(**{'preprocess': preprocess}),
    )

    assert (
        nlu_response.custom_model_features['most_probable_topic'].value
        == 'Cancel_lesson'
    )
    assert nlu_response.sure_topic == 'Cancel_lesson'

    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.45},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
            {'topic_name': 'Order_status', 'probability': 0.35},
        ],
    }
    nlu = await create_nlu(
        config_path='configuration_only_net.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {}},
    )

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        nlu_response.custom_model_features['most_probable_topic'].value
        == 'Cancel_lesson'
    )
    assert nlu_response.sure_topic is None


async def test_only_rules_topic(
        create_nlu, web_context, mockserver, core_flags,
):
    @mockserver.json_handler(
        '/supportai-models/internal/supportai-models/v1/shard_id',
    )
    async def _(request):
        return mockserver.make_response(
            status=404,
            json={'code': 'model_not_found', 'message': 'Model not found'},
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
                'messages': [{'author': 'user', 'text': 'хочу отменить урок'}],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message', value='хочу отменить урок',
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_only_rules.json',
        namespace='detmir_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {}},
    )

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        nlu_response.custom_model_features['most_probable_topic'].value is None
    )
    assert nlu_response.sure_topic == 'Cancel_lesson'


async def test_net_rules_combination_topic(
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
                    {'author': 'user', 'text': 'как отменить урок'},
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message', value='как отменить урок',
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_net_rules_combination.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {}},
    )

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        nlu_response.custom_model_features['most_probable_topic'].value
        == 'Cancel_lesson'
    )
    assert nlu_response.sure_topic == 'Cancel_lesson_how_to'


@pytest.mark.parametrize('uses_common_topics', [True, False])
async def test_common_topic_patched_general(
        create_nlu, web_context, core_flags, uses_common_topics,
):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    dialogue_acts_response = {}
    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {'author': 'user', 'text': 'как отменить урок'},
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message', value='как отменить урок',
                ),
                'last_user_message_length': feature_module.Feature.as_defined(
                    key='last_user_message_length', value=10,
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_with_patched_bb_model.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        dialogue_acts_response=dialogue_acts_response,
        wiz_response={
            'rules': {
                'Date': {'Pos': '1', 'Length': '1', 'Body': '{"Day":"1D"}'},
            },
        },
    )

    nlu_response = await nlu(
        request,
        state,
        web_context,
        configuration_module.CoreFlags(
            **{'uses_common_topics': uses_common_topics},
        ),
    )

    if not uses_common_topics:
        assert nlu_response.sure_topic is None
    else:
        assert nlu_response.sure_topic == 'Cancel_lesson_how_to'


@pytest.mark.core_flags(uses_nlu_features_extractor=True)
@pytest.mark.core_flags(uses_common_topics=True)
async def test_common_topic_single_dialogue_act_based_on_rules(
        create_nlu, web_context, core_flags,
):
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
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {'author': 'user', 'text': 'привет'},
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message', value='привет',
                ),
                'last_user_message_length': feature_module.Feature.as_defined(
                    key='last_user_message_length', value=3,
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_with_rules_da.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={
            'rules': {
                'Date': {'Pos': '1', 'Length': '1', 'Body': '{"Day":"1D"}'},
            },
        },
    )

    nlu_response = await nlu(request, state, web_context, core_flags)

    nlu_features = {
        'intent': feature_module.Feature.as_defined(key='intent', value=False),
        'greeting': feature_module.Feature.as_defined(
            key='greeting', value=True,
        ),
        'gratitude': feature_module.Feature.as_defined(
            key='gratitude', value=False,
        ),
        'agreement': feature_module.Feature.as_defined(
            key='agreement', value=False,
        ),
        'disagreement': feature_module.Feature.as_defined(
            key='disagreement', value=False,
        ),
    }
    assert nlu_response.nlu_features == nlu_features


@pytest.mark.core_flags(uses_nlu_features_extractor=True)
@pytest.mark.core_flags(uses_common_topics=True)
async def test_common_topic_based_only_rules(
        create_nlu, web_context, core_flags,
):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.1},
            {'topic_name': 'Move_lesson', 'probability': 0.1},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [{'author': 'user', 'text': 'привет, хочу урок'}],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message', value='привет, хочу урок',
                ),
                'last_user_message_length': feature_module.Feature.as_defined(
                    key='last_user_message_length', value=10,
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_with_rules_da.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={
            'rules': {
                'Date': {'Pos': '1', 'Length': '1', 'Body': '{"Day":"1D"}'},
            },
        },
    )

    nlu_response = await nlu(request, state, web_context, core_flags)

    nlu_features = {
        'intent': feature_module.Feature.as_defined(key='intent', value=True),
        'greeting': feature_module.Feature.as_defined(
            key='greeting', value=True,
        ),
        'gratitude': feature_module.Feature.as_defined(
            key='gratitude', value=False,
        ),
        'agreement': feature_module.Feature.as_defined(
            key='agreement', value=False,
        ),
        'disagreement': feature_module.Feature.as_defined(
            key='disagreement', value=False,
        ),
    }
    assert nlu_response.nlu_features == nlu_features
    assert nlu_response.sure_topic == 'order_lesson'


@pytest.mark.parametrize('uses_nlu_features_extractor', [True, False])
@pytest.mark.parametrize('uses_common_topics', [True, False])
async def test_common_topic_models_dialogue_act(
        create_nlu,
        web_context,
        core_flags,
        uses_common_topics,
        uses_nlu_features_extractor,
):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    dialogue_acts_response = {
        'result': [
            {
                'slug': 'greeting',
                'probabilities': [
                    {'slug': 'yes', 'probability': 0.9},
                    {'slug': 'no', 'probability': 0.1},
                ],
            },
            {
                'slug': 'intent',
                'probabilities': [
                    {'slug': 'yes', 'probability': 0.9},
                    {'slug': 'no', 'probability': 0.1},
                ],
            },
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {'author': 'user', 'text': 'Доброго дня!'},
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message', value='Доброго дня!',
                ),
                'last_user_message_length': feature_module.Feature.as_defined(
                    key='last_user_message_length', value=7,
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_with_models_da.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={
            'rules': {
                'Date': {'Pos': '1', 'Length': '1', 'Body': '{"Day":"1D"}'},
            },
        },
        dialogue_acts_response=dialogue_acts_response,
    )

    nlu_response = await nlu(
        request,
        state,
        web_context,
        configuration_module.CoreFlags(
            **{
                'uses_common_topics': uses_common_topics,
                'uses_nlu_features_extractor': uses_nlu_features_extractor,
            },
        ),
    )

    if uses_nlu_features_extractor:
        nlu_features = {
            'intent': feature_module.Feature.as_defined(
                key='intent', value=True,
            ),
            'greeting': feature_module.Feature.as_defined(
                key='greeting', value=True,
            ),
            'gratitude': feature_module.Feature.as_defined(
                key='gratitude', value=False,
            ),
            'agreement': feature_module.Feature.as_defined(
                key='agreement', value=False,
            ),
            'disagreement': feature_module.Feature.as_defined(
                key='disagreement', value=False,
            ),
        }
    else:
        nlu_features = {
            'intent': feature_module.Feature.as_defined(
                key='intent', value=True,
            ),
        }
    assert nlu_response.nlu_features == nlu_features
    assert nlu_response.sure_topic == 'Cancel_lesson'


@pytest.mark.core_flags(uses_common_topics=True)
async def test_common_topic_multi(create_nlu, web_context, core_flags):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }
    dialogue_acts_response = {}
    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {
                        'author': 'user',
                        'text': 'очень хочу отменить урок, как это сделать?',
                    },
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message',
                    value='очень хочу отменить урок, как это сделать?',
                ),
                'last_user_message_length': feature_module.Feature.as_defined(
                    key='last_user_message_length', value=10,
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_with_patched_bb_model.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        dialogue_acts_response=dialogue_acts_response,
        wiz_response={
            'rules': {
                'Date': {'Pos': '1', 'Length': '1', 'Body': '{"Day":"1D"}'},
            },
        },
    )

    nlu_response = await nlu(request, state, web_context, core_flags)
    assert nlu_response.sure_topic == 'Cancel_lesson_how_to'


@pytest.mark.core_flags(uses_common_topics=True)
async def test_common_topic_patched(create_nlu, web_context, core_flags):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }
    dialogue_acts_response = {}
    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {
                        'author': 'user',
                        'text': 'очень хочу отменить урок, как это сделать?',
                    },
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message',
                    value='очень хочу отменить урок, как это сделать?',
                ),
                'last_user_message_length': feature_module.Feature.as_defined(
                    key='last_user_message_length', value=10,
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_with_patched_bb_model.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        dialogue_acts_response=dialogue_acts_response,
        wiz_response={
            'rules': {
                'Date': {'Pos': '1', 'Length': '1', 'Body': '{"Day":"1D"}'},
            },
        },
    )

    nlu_response = await nlu(request, state, web_context, core_flags)
    assert nlu_response.sure_topic == 'Cancel_lesson_how_to'


@pytest.mark.core_flags(uses_common_topics=True)
async def test_common_topic_no_project_model(
        create_nlu, web_context, core_flags,
):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }
    dialogue_acts_response = {}
    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {
                        'author': 'user',
                        'text': 'очень хочу отменить урок, как это сделать?',
                    },
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message',
                    value='очень хочу отменить урок, как это сделать?',
                ),
                'last_user_message_length': feature_module.Feature.as_defined(
                    key='last_user_message_length', value=10,
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_with_no_project_model.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        dialogue_acts_response=dialogue_acts_response,
        wiz_response={
            'rules': {
                'Date': {'Pos': '1', 'Length': '1', 'Body': '{"Day":"1D"}'},
            },
        },
    )

    nlu_response = await nlu(request, state, web_context, core_flags)
    assert nlu_response.sure_topic == 'Cancel_lesson_how_to'


async def test_model_id(create_nlu, web_context, core_flags):
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
                'messages': [{'author': 'user', 'text': 'отмените мой урок'}],
            },
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[{}])
    nlu = await create_nlu(
        config_path='configuration_with_model_id.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {}},
    )

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert (
        nlu_response.custom_model_features['most_probable_topic'].value
        == 'Cancel_lesson'
    )
    assert nlu_response.sure_topic == 'Cancel_lesson'


@pytest.mark.config(SUPPORTAI_WIZARD_SETTINGS={'projects': 'none'})
async def test_wizard_disabled(create_nlu, web_context, core_flags):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [{'topic_name': 'Cancel_lesson', 'probability': 0.8}],
    }
    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'отмените мой урок завтра'},
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[{}])
    nlu = await create_nlu(
        config_path='configuration.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Pos': '3', 'Body': '{"Day":"1D"}'}}},
    )

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert not nlu_response.entities['datetime'].values


@pytest.mark.config(
    SUPPORTAI_WIZARD_SETTINGS={'projects': ['justschool_dialog']},
)
async def test_wizard_enabled_to_project(create_nlu, web_context, core_flags):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [{'topic_name': 'Cancel_lesson', 'probability': 0.8}],
    }
    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'отмените мой урок завтра'},
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[{}])
    nlu = await create_nlu(
        config_path='configuration.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Pos': '3', 'Body': '{"Day":"1D"}'}}},
    )

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert nlu_response.entities['datetime'].values


@pytest.mark.config(SUPPORTAI_WIZARD_SETTINGS={'projects': 'all'})
async def test_wizard_enabled_all(create_nlu, web_context, core_flags):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [{'topic_name': 'Cancel_lesson', 'probability': 0.8}],
    }
    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'отмените мой урок завтра'},
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[{}])
    nlu = await create_nlu(
        config_path='configuration.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Pos': '3', 'Body': '{"Day":"1D"}'}}},
    )

    nlu_response = await nlu(request, state, web_context, core_flags)

    assert nlu_response.entities['datetime'].values


@pytest.mark.core_flags(uses_reference_phrases=True)
async def test_online_model_only(create_nlu, web_context, core_flags):

    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.1},
            {'topic_name': 'Move_lesson', 'probability': 0.1},
        ],
    }

    text_embed_response = {
        'text': 'очень хочу отменить урок, как это сделать?',
        'embedding': {'embedding': [0.1 for _ in range(1024)]},
    }

    reference_phrases_response = {
        'project_topic_slug': 'Отмена урока',
        'common_topic_slug': None,
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {
                        'author': 'user',
                        'text': 'очень хочу отменить урок, как это сделать?',
                    },
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message',
                    value='очень хочу отменить урок, как это сделать?',
                ),
                'last_user_message_length': feature_module.Feature.as_defined(
                    key='last_user_message_length', value=10,
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_only_online_model.json',
        namespace='foxford_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        text_embed_response=text_embed_response,
        reference_phrases_response=reference_phrases_response,
    )

    nlu_response = await nlu(request, state, web_context, core_flags)
    assert nlu_response.sure_topic == 'Отмена урока'


@pytest.mark.parametrize('uses_reference_phrases', [True, False])
async def test_blending_custom_online(
        create_nlu, web_context, core_flags, uses_reference_phrases,
):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    text_embed_response = {
        'text': 'очень хочу отменить или перенести урок, как это сделать?',
        'embedding': {'embedding': [0.1 for _ in range(1024)]},
    }

    reference_phrases_response = {
        'project_topic_slug': 'Move_lesson',
        'common_topic_slug': None,
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {
                        'author': 'user',
                        'text': 'очень хочу отменить урок, как это сделать?',
                    },
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message',
                    value='очень хочу отменить урок, как это сделать?',
                ),
                'last_user_message_length': feature_module.Feature.as_defined(
                    key='last_user_message_length', value=15,
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_with_model_id.json',
        namespace='foxford_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        text_embed_response=text_embed_response,
        reference_phrases_response=reference_phrases_response,
    )

    nlu_response = await nlu(
        request,
        state,
        web_context,
        core_flags,
        configuration_module.CoreFlags(
            **{'uses_reference_phrases': uses_reference_phrases},
        ),
    )
    assert nlu_response.sure_topic == 'Cancel_lesson'


@pytest.mark.parametrize('uses_reference_phrases', [True, False])
async def test_blending_blackbox_online(
        create_nlu, web_context, core_flags, uses_reference_phrases,
):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    text_embed_response = {
        'text': 'очень хочу отменить или перенести урок, как это сделать?',
        'embedding': {'embedding': [0.1 for _ in range(1024)]},
    }

    reference_phrases_response = {
        'project_topic_slug': 'Move_lesson',
        'common_topic_slug': None,
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {
                        'author': 'user',
                        'text': 'очень хочу отменить урок, как это сделать?',
                    },
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message',
                    value='очень хочу отменить урок, как это сделать?',
                ),
                'last_user_message_length': feature_module.Feature.as_defined(
                    key='last_user_message_length', value=15,
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_with_no_project_model.json',
        namespace='foxford_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        text_embed_response=text_embed_response,
        reference_phrases_response=reference_phrases_response,
    )

    nlu_response = await nlu(
        request,
        state,
        web_context,
        configuration_module.CoreFlags(
            **{
                'uses_reference_phrases': uses_reference_phrases,
                'uses_common_topics': True,
            },
        ),
    )
    assert nlu_response.sure_topic == (
        'Move_lesson' if uses_reference_phrases else 'Cancel_lesson_how_to'
    )


@pytest.mark.parametrize('uses_zeliboba_model', [True, False])
async def test_blending_zeliboba_intent_model_only(
        create_nlu, web_context, core_flags, uses_zeliboba_model,
):
    supportai_models_response = {
        'most_probable_topic': 'Move_lesson',
        'probabilities': [
            {'topic_name': 'Move_lesson', 'probability': 0.8},
            {'topic_name': 'Cancel_lesson', 'probability': 0.2},
        ],
    }

    zeliboba_intent_response = {
        'input_text': 'очень хочу отменить урок, как это сделать?',
        'embedding': [0.1] * 256,
        'knowledge': {
            'local_id': 1,
            'probability': 0.47,
            'url': 'kek.lol',
            'title': 'lol',
            'content': 'Cancel_lesson',
        },
        'embed_model_id': 'kek',
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {
                        'author': 'user',
                        'text': 'очень хочу отменить урок, как это сделать?',
                    },
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message',
                    value='очень хочу отменить урок, как это сделать?',
                ),
                'last_user_message_length': feature_module.Feature.as_defined(
                    key='last_user_message_length', value=15,
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_only_zeliboba_model.json',
        namespace='foxford_dialog',
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        supportai_models_response=supportai_models_response,
        zeliboba_intent_response=zeliboba_intent_response,
    )

    nlu_response = await nlu(
        request,
        state,
        web_context,
        configuration_module.CoreFlags(
            **{'uses_zeliboba_model': uses_zeliboba_model},
        ),
    )
    assert nlu_response.sure_topic == (
        'Cancel_lesson' if uses_zeliboba_model else None
    )


@pytest.mark.parametrize('uses_zeliboba_model', [True, False])
@pytest.mark.parametrize('uses_reference_phrases', [True, False])
@pytest.mark.parametrize('embedder_model_sure_topic', ['Embedder_topic', None])
async def test_blending_zeliboba_intent_and_embedder(
        create_nlu,
        web_context,
        core_flags,
        uses_zeliboba_model,
        uses_reference_phrases,
        embedder_model_sure_topic,
):
    supportai_models_response = {
        'most_probable_topic': 'Classify_topic',
        'probabilities': [
            {'topic_name': 'Classify_topic', 'probability': 0.8},
            {'topic_name': 'Classify_minor_topic', 'probability': 0.2},
        ],
    }

    text_embed_response = {
        'text': 'очень хочу отменить или перенести урок, как это сделать?',
        'embedding': {'embedding': [0.1 for _ in range(5)]},
    }

    reference_phrases_response = {
        'project_topic_slug': embedder_model_sure_topic,
        'common_topic_slug': None,
    }

    zeliboba_intent_response = {
        'input_text': 'очень хочу отменить урок, как это сделать?',
        'embedding': [0.1] * 5,
        'knowledge': {
            'local_id': [1, 2],
            'probability': [0.1, 0.9],
            'title': None,
            'content': 'Zeliboba_topic',
        },
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {
                        'author': 'user',
                        'text': 'очень хочу отменить урок, как это сделать?',
                    },
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message',
                    value='очень хочу отменить урок, как это сделать?',
                ),
                'last_user_message_length': feature_module.Feature.as_defined(
                    key='last_user_message_length', value=15,
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_embedder_and_zeliboba_models.json',
        namespace='foxford_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        text_embed_response=text_embed_response,
        zeliboba_intent_response=zeliboba_intent_response,
        reference_phrases_response=reference_phrases_response,
    )

    nlu_response = await nlu(
        request,
        state,
        web_context,
        configuration_module.CoreFlags(
            **{
                'uses_zeliboba_model': uses_zeliboba_model,
                'uses_reference_phrases': uses_reference_phrases,
                'uses_common_topics': False,
            },
        ),
    )
    if uses_reference_phrases and embedder_model_sure_topic is not None:
        assert nlu_response.sure_topic == embedder_model_sure_topic
    elif uses_zeliboba_model:
        assert nlu_response.sure_topic == 'Zeliboba_topic'
    else:
        assert nlu_response.sure_topic is None


@pytest.mark.parametrize('uses_zeliboba_model', [True, False])
async def test_blending_zeliboba_intent_model_only_empty_text(
        create_nlu, web_context, core_flags, uses_zeliboba_model,
):
    supportai_models_response = {
        'most_probable_topic': 'Move_lesson',
        'probabilities': [
            {'topic_name': 'Move_lesson', 'probability': 0.8},
            {'topic_name': 'Cancel_lesson', 'probability': 0.2},
        ],
    }

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {'messages': [{'author': 'user', 'text': ''}]},
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message', value='',
                ),
                'last_user_message_length': feature_module.Feature.as_defined(
                    key='last_user_message_length', value=0,
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_only_zeliboba_model.json',
        namespace='foxford_dialog',
        wiz_response={'rules': {'Date': {'Body': '{"Day":"1D"}'}}},
        supportai_models_response=supportai_models_response,
    )

    nlu_response = await nlu(
        request,
        state,
        web_context,
        configuration_module.CoreFlags(
            **{'uses_zeliboba_model': uses_zeliboba_model},
        ),
    )
    assert nlu_response.sure_topic is None
