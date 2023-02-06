# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest


@pytest.mark.pgsql('eats_restapp_support_chat', files=['insert_chats.sql'])
@pytest.mark.parametrize(
    'partner_id,expected_response_code,expected_message_count',
    [(10, 200, 2), (11, 200, 0)],
)
async def test_partner_login_list(
        taxi_eats_restapp_support_chat,
        partner_id,
        expected_response_code,
        expected_message_count,
):
    response = await taxi_eats_restapp_support_chat.get(
        '/4.0/restapp-front/support_chat/v1/partner/notifications/count',
        headers={'X-YaEda-PartnerId': str(partner_id)},
    )
    assert response.status == expected_response_code
    assert response.json()['count'] == expected_message_count
