# pylint: disable=no-value-for-parameter
import pytest

from taxi_corp.stq import send_drive_promocode_sms_task

MOCK_ID = 'promocode'


@pytest.mark.parametrize(
    'user_id, expected_message',
    [('user1', 'link={}. promocode=None'.format(MOCK_ID))],
)
@pytest.mark.translations(
    corp={
        'sms.link_drive_with_promocode': {
            'ru': 'link={link}. promocode={promocode}',
        },
    },
)
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
async def test_send_link(
        taxi_corp_app_stq, patch, monkeypatch, db, user_id, expected_message,
):
    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)

    @patch('taxi.clients.user_api.UserApiClient.get_user_phone')
    async def _get_user_phone(*args, **kwargs):
        return None

    @patch(
        'taxi.clients.ucommunications.UcommunicationsClient.send_sms_to_user',
    )
    async def _send_message(personal_phone_id, text, intent):
        assert text == expected_message
        assert personal_phone_id == 'client1_phone_id'
        assert intent == 'taxi_corp_send_link'

    await send_drive_promocode_sms_task(taxi_corp_app_stq, user_id, MOCK_ID)

    send_sms_calls = _send_message.calls
    assert len(send_sms_calls) == 1


@pytest.mark.parametrize(['user_id'], [('user2',)])
async def test_send_link_no_request(taxi_corp_app_stq, patch, db, user_id):
    @patch('taxi.sms_sender.send_message')
    async def _send_message(db, settings, phone, message, intent):
        pass

    await send_drive_promocode_sms_task(taxi_corp_app_stq, user_id, MOCK_ID)

    send_sms_calls = _send_message.calls
    assert not send_sms_calls
