import pytest

from taxi.clients import support_chat

from chatterbox.internal import chat_types


@pytest.mark.parametrize('service', support_chat.SENDER_USER_ROLES)
def test_user_roles(service, cbox_app):
    assert chat_types.is_registered_user_role(service, cbox_app.config)


@pytest.mark.parametrize('service', support_chat.SENDER_SUPPORT_ROLES)
def test_support_roles(service, cbox_app):
    assert not chat_types.is_registered_user_role(service, cbox_app.config)


@pytest.mark.parametrize('service', support_chat.SENDER_SCENATIOS_ROLES)
def test_scenarios_roles(service, cbox_app):
    assert not chat_types.is_registered_user_role(service, cbox_app.config)
