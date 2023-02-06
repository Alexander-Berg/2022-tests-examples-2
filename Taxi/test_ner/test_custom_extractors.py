# pylint: disable=C0302
import pytest

import generated.clients_libs.supportai_models.supportai_lib as supportai_lib_module  # noqa pylint: disable=line-too-long

from supportai.common import configuration as configuration_module
from supportai.common import state as state_module


@pytest.mark.parametrize('use_multilingual_ner', [False])
async def test_string_entity_extractor(
        create_nlu, web_context, core_flags, use_multilingual_ner,
):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }

    wiz_response = {'rules': {}}

    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Извлеки мне текст ru1234'},
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
        wiz_response=wiz_response,
    )
    nlu_response = await nlu(
        request,
        state,
        web_context,
        configuration_module.CoreFlags(
            **{'use_multilingual_ner': use_multilingual_ner},
        ),
    )
    assert nlu_response.entities['string_entity'].values == ['ru1234']
