# pylint: disable=C0302
import pytest

import generated.clients_libs.supportai_models.supportai_lib as supportai_lib_module  # noqa pylint: disable=line-too-long

from supportai.common import feature as feature_module
from supportai.common import state as state_module


@pytest.mark.parametrize(
    'last_user_message, true_sentiment',
    [
        ('ах вы очень нехороший человек!', 'negative'),
        ('хочу отменить урок', 'neutral'),
        ('вы просто красавчики!', 'positive'),
    ],
)
@pytest.mark.core_flags(nlu_20=True)
@pytest.mark.core_flags(uses_nlu_features_extractor=True)
@pytest.mark.core_flags(uses_common_topics=True)
async def test_sentiment_based_on_rules(
        create_nlu, web_context, core_flags, last_user_message, true_sentiment,
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
                    {
                        'author': 'user',
                        'text': 'ах вы очень нехороший человек!',
                    },  # noqa pylint: disable=line-too-long
                    {'author': 'user', 'text': 'хочу отменить урок'},
                    {'author': 'user', 'text': last_user_message},
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message', value=last_user_message,
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_sentiment_with_rules.json',
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
        'sentiment': feature_module.Feature.as_defined(
            key='sentiment', value=true_sentiment,
        ),
    }
    assert nlu_response.nlu_features == nlu_features


@pytest.mark.parametrize(
    'last_user_message, true_sentiment, nlu_features_result',
    [
        (
            'ах вы очень нехороший человек!',
            'negative',
            {
                'result': [
                    {
                        'slug': 'sentiment',
                        'probabilities': [
                            {'slug': 'positive', 'probability': 0.05},
                            {'slug': 'negative', 'probability': 0.9},
                            {'slug': 'neutral', 'probability': 0.05},
                        ],
                    },
                ],
            },
        ),
        (
            'хочу отменить урок',
            'neutral',
            {
                'result': [
                    {
                        'slug': 'sentiment',
                        'probabilities': [
                            {'slug': 'neutral', 'probability': 0.9},
                            {'slug': 'negative', 'probability': 0.05},
                            {'slug': 'positive', 'probability': 0.05},
                        ],
                    },
                ],
            },
        ),
        (
            'вы просто красавчики!',
            'positive',
            {
                'result': [
                    {
                        'slug': 'sentiment',
                        'probabilities': [
                            {'slug': 'neutral', 'probability': 0.05},
                            {'slug': 'negative', 'probability': 0.05},
                            {'slug': 'positive', 'probability': 0.9},
                        ],
                    },
                ],
            },
        ),
        (
            'ого какой вы странный',
            '__feature_extractor_empty_result',
            {
                'result': [
                    {
                        'slug': 'sentiment',
                        'probabilities': [
                            {'slug': 'neutral', 'probability': 0.33},
                            {'slug': 'negative', 'probability': 0.33},
                            {'slug': 'positive', 'probability': 0.34},
                        ],
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.core_flags(nlu_20=True)
@pytest.mark.core_flags(uses_nlu_features_extractor=True)
@pytest.mark.core_flags(uses_common_topics=True)
async def test_sentiment_based_on_model(
        create_nlu,
        web_context,
        core_flags,
        last_user_message,
        true_sentiment,
        nlu_features_result,
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
                    {'author': 'user', 'text': 'привет, я хочу отменить урок'},
                    {'author': 'ai', 'text': 'а зачем?)'},
                    {'author': 'user', 'text': 'ты чего '},
                ],
            },
            'features': [],
        },
    )
    state = state_module.State(
        feature_layers=[
            {
                'last_user_message': feature_module.Feature.as_defined(
                    key='last_user_message', value=last_user_message,
                ),
            },
        ],
    )
    nlu = await create_nlu(
        config_path='configuration_sentiment_with_model.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response={
            'rules': {
                'Date': {'Pos': '1', 'Length': '1', 'Body': '{"Day":"1D"}'},
            },
        },
        dialogue_acts_response=nlu_features_result,
    )

    nlu_response = await nlu(request, state, web_context, core_flags)

    nlu_features = {
        'sentiment': feature_module.Feature.as_defined(
            key='sentiment', value=true_sentiment,
        ),
    }
    assert nlu_response.nlu_features == nlu_features
