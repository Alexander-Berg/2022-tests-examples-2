import pytest

from taxi_support_chat.internal import chat_types

CLIENT_ROLE = 'client'
DRIVER_ROLE = 'driver'
SELFREG_DRIVER_ROLE = 'selfreg_driver'
FACEBOOK_USER_ROLE = 'facebook_user'
SMS_CLIENT_ROLE = 'sms_client'
EATS_CLIENT_ROLE = 'eats_client'
EATS_APP_CLIENT_ROLE = 'eats_app_client'
SAFETY_CENTER_CLIENT_ROLE = 'safety_center_client'
OPTEUM_CLIENT_ROLE = 'opteum_client'
CORP_CABINET_ROLE = 'corp_cabinet_client'
GOOGLE_PLAY_REVIEW = 'google_play_review'
HELP_YANDEX_CLIENT = 'help_yandex_client'
LABS_ADMIN_YANDEX_CLIENT = 'labs_admin_yandex_client'
CARSHARING_CLIENT_ROLE = 'carsharing_client'
SCOUTS_CLIENT_ROLE = 'scouts_client'
LAVKA_STORAGES_CLIENT_ROLE = 'lavka_storages_client'
WEBSITE_CLIENT_ROLE = 'website_client'
RESTAPP_CLIENT_ROLE = 'restapp_client'
MARKET_CLIENT_ROLE = 'market_client'

USER_ROLES = [
    CLIENT_ROLE,
    DRIVER_ROLE,
    SELFREG_DRIVER_ROLE,
    FACEBOOK_USER_ROLE,
    SMS_CLIENT_ROLE,
    EATS_CLIENT_ROLE,
    EATS_APP_CLIENT_ROLE,
    SAFETY_CENTER_CLIENT_ROLE,
    OPTEUM_CLIENT_ROLE,
    CORP_CABINET_ROLE,
    GOOGLE_PLAY_REVIEW,
    HELP_YANDEX_CLIENT,
    LABS_ADMIN_YANDEX_CLIENT,
    CARSHARING_CLIENT_ROLE,
    SCOUTS_CLIENT_ROLE,
    LAVKA_STORAGES_CLIENT_ROLE,
    WEBSITE_CLIENT_ROLE,
    RESTAPP_CLIENT_ROLE,
    MARKET_CLIENT_ROLE,
]

DRIVER_SUPPORT_CHAT = 'driver_support'
SELFREG_DRIVER_SUPPORT_CHAT = 'selfreg_driver_support'
CLIENT_SUPPORT_CHAT = 'client_support'
FACEBOOK_SUPPORT_CHAT = 'facebook_support'
SMS_SUPPORT_CHAT = 'sms_support'
EATS_SUPPORT_CHAT = 'eats_support'
EATS_APP_SUPPORT_CHAT = 'eats_app_support'
SAFETY_CENTER_SUPPORT_CHAT = 'safety_center_support'
OPTEUM_SUPPORT_CHAT = 'opteum_support'
CORP_CABINET_CHAT = 'corp_cabinet_support'
GOOGLE_PLAY_REVIEW_CHAT = 'google_play_support'
HELP_YANDEX_CHAT = 'help_yandex_support'
LABS_ADMIN_YANDEX_CHAT = 'labs_admin_yandex_support'
CARSHARING_SUPPORT_CHAT = 'carsharing_support'
SCOUTS_SUPPORT_CHAT = 'scouts_support'
LAVKA_STORAGES_SUPPORT_CHAT = 'lavka_storages_support'
WEBSITE_SUPPORT_CHAT = 'website_support'
RESTAPP_SUPPORT_CHAT = 'restapp_support'
MARKET_SUPPORT_CHAT = 'market_support'

ROLE_CHAT_TYPE_MAPPING = {
    CLIENT_ROLE: CLIENT_SUPPORT_CHAT,
    DRIVER_ROLE: DRIVER_SUPPORT_CHAT,
    SELFREG_DRIVER_ROLE: SELFREG_DRIVER_SUPPORT_CHAT,
    FACEBOOK_USER_ROLE: FACEBOOK_SUPPORT_CHAT,
    SMS_CLIENT_ROLE: SMS_SUPPORT_CHAT,
    EATS_CLIENT_ROLE: EATS_SUPPORT_CHAT,
    EATS_APP_CLIENT_ROLE: EATS_APP_SUPPORT_CHAT,
    SAFETY_CENTER_CLIENT_ROLE: SAFETY_CENTER_SUPPORT_CHAT,
    OPTEUM_CLIENT_ROLE: OPTEUM_SUPPORT_CHAT,
    CORP_CABINET_ROLE: CORP_CABINET_CHAT,
    GOOGLE_PLAY_REVIEW: GOOGLE_PLAY_REVIEW_CHAT,
    HELP_YANDEX_CLIENT: HELP_YANDEX_CHAT,
    LABS_ADMIN_YANDEX_CLIENT: LABS_ADMIN_YANDEX_CHAT,
    CARSHARING_CLIENT_ROLE: CARSHARING_SUPPORT_CHAT,
    SCOUTS_CLIENT_ROLE: SCOUTS_SUPPORT_CHAT,
    LAVKA_STORAGES_CLIENT_ROLE: LAVKA_STORAGES_SUPPORT_CHAT,
    WEBSITE_CLIENT_ROLE: WEBSITE_SUPPORT_CHAT,
    RESTAPP_CLIENT_ROLE: RESTAPP_SUPPORT_CHAT,
    MARKET_CLIENT_ROLE: MARKET_SUPPORT_CHAT,
}

DRIVER_SUPPORT_CHAT = 'driver_support'
SELFREG_DRIVER_SUPPORT_CHAT = 'selfreg_driver_support'
CLIENT_SUPPORT_CHAT = 'client_support'
FACEBOOK_SUPPORT_CHAT = 'facebook_support'
SMS_SUPPORT_CHAT = 'sms_support'
EATS_SUPPORT_CHAT = 'eats_support'
EATS_APP_SUPPORT_CHAT = 'eats_app_support'
SAFETY_CENTER_SUPPORT_CHAT = 'safety_center_support'
OPTEUM_SUPPORT_CHAT = 'opteum_support'
CORP_CABINET_CHAT = 'corp_cabinet_support'
GOOGLE_PLAY_REVIEW_CHAT = 'google_play_support'
HELP_YANDEX_CHAT = 'help_yandex_support'
LABS_ADMIN_YANDEX_CHAT = 'labs_admin_yandex_support'
CARSHARING_SUPPORT_CHAT = 'carsharing_support'
SCOUTS_SUPPORT_CHAT = 'scouts_support'
LAVKA_STORAGES_SUPPORT_CHAT = 'lavka_storages_support'
WEBSITE_SUPPORT_CHAT = 'website_support'
RESTAPP_SUPPORT_CHAT = 'restapp_support'
MARKET_SUPPORT_CHAT = 'market_support'

CHAT_TYPE_ROLE_MAPPING = {
    SMS_SUPPORT_CHAT: SMS_CLIENT_ROLE,
    CLIENT_SUPPORT_CHAT: CLIENT_ROLE,
    DRIVER_SUPPORT_CHAT: DRIVER_ROLE,
    SELFREG_DRIVER_SUPPORT_CHAT: SELFREG_DRIVER_ROLE,
    FACEBOOK_SUPPORT_CHAT: FACEBOOK_USER_ROLE,
    EATS_SUPPORT_CHAT: EATS_CLIENT_ROLE,
    EATS_APP_SUPPORT_CHAT: EATS_APP_CLIENT_ROLE,
    SAFETY_CENTER_SUPPORT_CHAT: SAFETY_CENTER_CLIENT_ROLE,
    OPTEUM_SUPPORT_CHAT: OPTEUM_CLIENT_ROLE,
    CORP_CABINET_CHAT: CORP_CABINET_ROLE,
    GOOGLE_PLAY_REVIEW_CHAT: GOOGLE_PLAY_REVIEW,
    HELP_YANDEX_CHAT: HELP_YANDEX_CLIENT,
    LABS_ADMIN_YANDEX_CHAT: LABS_ADMIN_YANDEX_CLIENT,
    CARSHARING_SUPPORT_CHAT: CARSHARING_CLIENT_ROLE,
    SCOUTS_SUPPORT_CHAT: SCOUTS_CLIENT_ROLE,
    LAVKA_STORAGES_SUPPORT_CHAT: LAVKA_STORAGES_CLIENT_ROLE,
    WEBSITE_SUPPORT_CHAT: WEBSITE_CLIENT_ROLE,
    RESTAPP_SUPPORT_CHAT: RESTAPP_CLIENT_ROLE,
    MARKET_SUPPORT_CHAT: MARKET_CLIENT_ROLE,
}

VISIBILITY = {
    CLIENT_ROLE: False,
    DRIVER_ROLE: True,
    SELFREG_DRIVER_ROLE: True,
    FACEBOOK_USER_ROLE: True,
    SMS_CLIENT_ROLE: True,
    EATS_CLIENT_ROLE: True,
    EATS_APP_CLIENT_ROLE: True,
    SAFETY_CENTER_CLIENT_ROLE: True,
    OPTEUM_CLIENT_ROLE: True,
    CORP_CABINET_ROLE: True,
    GOOGLE_PLAY_REVIEW: True,
    HELP_YANDEX_CLIENT: True,
    LABS_ADMIN_YANDEX_CLIENT: True,
    CARSHARING_CLIENT_ROLE: False,
    SCOUTS_CLIENT_ROLE: True,
    LAVKA_STORAGES_CLIENT_ROLE: True,
    WEBSITE_CLIENT_ROLE: True,
    RESTAPP_CLIENT_ROLE: True,
    MARKET_CLIENT_ROLE: True,
}


def test_all_user_roles(web_context):
    for role in USER_ROLES:
        assert chat_types.is_registered_user_role(role, web_context.config)


def test_role_chat_type_mapping(web_context):
    for role, support_chat in ROLE_CHAT_TYPE_MAPPING.items():
        assert support_chat == chat_types.support_chat_for_role(
            role, web_context.config,
        )


def test_chat_type_role_mapping(web_context):
    for support_chat, role in CHAT_TYPE_ROLE_MAPPING.items():
        assert role == chat_types.role_for_support_chat(
            support_chat, web_context.config,
        )


def test_role_visibility(web_context):
    for role, visibility in VISIBILITY.items():
        assert visibility == chat_types.get_initial_visibility(
            role, web_context.config,
        )


@pytest.mark.parametrize(
    ('chat_type', 'expected_support_chat'),
    [
        ('carsharing', 'carsharing_support'),
        ('client', 'client_support'),
        ('eats', 'eats_support'),
        ('eats_app', 'eats_app_support'),
        ('market', 'market_support'),
        ('scouts', 'scouts_support'),
    ],
)
def test_support_chat_for_chat_type(
        web_context, chat_type, expected_support_chat,
):
    support_chat = chat_types.support_chat_for_chat_type(
        chat_type, web_context.config,
    )
    assert support_chat == expected_support_chat


@pytest.mark.parametrize(
    ('chat_type', 'expected_owner_id'),
    [
        ('carsharing', 'yandex_uid'),
        ('client', 'phone_id'),
        ('eats', 'yandex_uid'),
        ('eats_app', 'eats_user_id'),
        ('lavka_storages', 'lavka_storage_id'),
        ('restapp', 'restapp_partner_id'),
        ('website', 'website_user_id'),
    ],
)
def test_owner_id_for_chat_type(web_context, chat_type, expected_owner_id):
    owner_id = chat_types.owner_id_for_chat_type(chat_type, web_context.config)
    assert owner_id == expected_owner_id
