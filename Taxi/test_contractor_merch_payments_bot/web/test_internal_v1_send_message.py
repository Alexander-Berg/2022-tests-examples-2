import test_contractor_merch_payments_bot.mocks.telegram as telegram_mocks

CHAT_ID = 128918423094533274
MESSAGE = 'test_message'
VALID_REQUEST = {
    'merchant_id': 'test_merchant_id',
    'message': MESSAGE,
    'chat_id': CHAT_ID,
}


async def test_ok(
        web_app_client,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
):
    update = VALID_REQUEST

    endpoint = '/internal/v1/send-message'
    response = await web_app_client.post(endpoint, json=update)
    assert response.status == 200
    assert mock_telegram_service.send_message.handler.times_called == 1
    request = mock_telegram_service.send_message.handler.next_call()['request']
    assert request.json == {
        'chat_id': CHAT_ID,
        'text': MESSAGE,
        'parse_mode': 'markdown',
    }
