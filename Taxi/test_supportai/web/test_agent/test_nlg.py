# pylint: disable=W0212
import pytest

from supportai_lib.generated import models as api_module

from supportai.common import configuration as configuration_module
from supportai.common import constants as _constants
from supportai.common import core_features
from supportai.common import feature as feature_module
from supportai.common import nlg as nlg_module
from supportai.common import state as state_module


@pytest.fixture(name='nlg')
def gen_policy(load_json):
    nlg = nlg_module.NaturalLanguageGenerator(namespace=None)
    configuration = configuration_module.Configuration.deserialize(
        load_json('configuration.json'),
    )
    nlg.load_from_configuration(configuration.nlg)
    return nlg


@pytest.mark.core_flags(reply_as_texts=False)
async def test_nlg(nlg, core_flags):
    texts = ['Меня зовут {name}. А тебя?']
    state = state_module.State(
        feature_layers=[
            {
                _constants.DO_GREETING_FEATURE_NAME: (
                    feature_module.Feature.as_defined(
                        key=_constants.DO_GREETING_FEATURE_NAME, value=True,
                    )
                ),
            },
        ],
    )
    dialog = api_module.Dialog(
        messages=[api_module.Message(text='Привет!', author='user')],
    )
    assert await nlg(texts, state, dialog, core_flags) is None

    state = state_module.State(
        feature_layers=[
            {
                _constants.DO_GREETING_FEATURE_NAME: (
                    feature_module.Feature.as_defined(
                        key=_constants.DO_GREETING_FEATURE_NAME, value=True,
                    )
                ),
                core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME: (
                    feature_module.Feature.as_defined(
                        key=core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME,
                        value='ru',
                    )
                ),
            },
        ],
    )
    assert await nlg(texts, state, dialog, core_flags) is None

    state = state_module.State(
        feature_layers=[
            {
                _constants.DO_GREETING_FEATURE_NAME: (
                    feature_module.Feature.as_defined(
                        key=_constants.DO_GREETING_FEATURE_NAME, value=True,
                    )
                ),
                core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME: (
                    feature_module.Feature.as_defined(
                        key=core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME,
                        value='ru',
                    )
                ),
                'name': feature_module.Feature.as_defined(
                    key='name', value='Ботти',
                ),
            },
        ],
    )
    assert core_flags.reply_as_texts is False
    assert await nlg(texts, state, dialog, core_flags) == [
        f'Добрый день!{_constants.SPLIT_TOKEN}Меня зовут Ботти. А тебя?',
    ]

    state = state_module.State(
        feature_layers=[
            {
                _constants.DO_GREETING_WITH_NAME_FEATURE_NAME: (
                    feature_module.Feature.as_defined(
                        key=_constants.DO_GREETING_WITH_NAME_FEATURE_NAME,
                        value=True,
                    )
                ),
                core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME: (
                    feature_module.Feature.as_defined(
                        key=core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME,
                        value='ru',
                    )
                ),
                'name': feature_module.Feature.as_defined(
                    key='name', value='Ботти',
                ),
                'user_first_name': feature_module.Feature.as_defined(
                    key='user_first_name', value='Ботти',
                ),
            },
        ],
    )
    assert await nlg(texts, state, dialog, core_flags) == [
        f'Добрый день! Ботти{_constants.SPLIT_TOKEN}'
        f'Меня зовут Ботти. А тебя?',
    ]


@pytest.mark.core_flags(reply_as_texts=True)
async def test_nlg_separated(nlg, core_flags):
    texts = ['Меня зовут {name}. А тебя?']
    state = state_module.State(
        feature_layers=[
            {
                _constants.DO_GREETING_FEATURE_NAME: (
                    feature_module.Feature.as_defined(
                        key=_constants.DO_GREETING_FEATURE_NAME, value=True,
                    )
                ),
                core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME: (
                    feature_module.Feature.as_defined(
                        key=core_features.USER_MESSAGE_LANGUAGE_FEATURE_NAME,
                        value='ru',
                    )
                ),
                'name': feature_module.Feature.as_defined(
                    key='name', value='Ботти',
                ),
            },
        ],
    )
    dialog = api_module.Dialog(
        messages=[api_module.Message(text='Привет!', author='user')],
    )
    reply_texts = await nlg(texts, state, dialog, core_flags)
    assert reply_texts == ['Добрый день!', 'Меня зовут Ботти. А тебя?']
