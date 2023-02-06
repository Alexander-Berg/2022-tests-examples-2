from supportai_lib.generated import models as api_module

from supportai.common import core_features
from supportai.common import feature as feature_module


def test_get_messages(web_context) -> None:

    request = api_module.SupportRequest.deserialize(
        {
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Москва'},
                    {'author': 'ai', 'text': 'Воронеж'},
                    {'author': 'support', 'text': 'Тверь'},
                    {'author': 'user', 'text': 'Нижний Новгород'},
                ],
            },
            'features': [],
        },
    )
    messages_number = core_features.CORE_FEATURES.get(
        core_features.MESSAGES_NUMBER_FEATURE_NAME,
    )
    assert messages_number is not None
    assert (
        core_features.get_messages_number(request)
        == feature_module.Feature(
            value=4,
            status=feature_module.Status.DEFINED,
            spec=messages_number,
        )
    )

    user_messages_number = core_features.CORE_FEATURES.get(
        core_features.USER_MESSAGES_NUMBER_FEATURE_NAME,
    )
    assert user_messages_number is not None
    assert (
        core_features.get_user_messages_number(request)
        == feature_module.Feature(
            value=2,
            status=feature_module.Status.DEFINED,
            spec=user_messages_number,
        )
    )
