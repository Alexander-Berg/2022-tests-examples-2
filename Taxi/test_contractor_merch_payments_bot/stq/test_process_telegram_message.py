import contractor_merch_payments_bot.generated.stq3.pytest_plugin as stq_plugin  # noqa: E501 (line too long)
import test_contractor_merch_payments_bot.mocks.authorization as authorization_mocks  # noqa: E501 (line too long)
import test_contractor_merch_payments_bot.mocks.telegram as telegram_mocks


CHAT_ID = 11111
UPDATE_REQUEST = {
    'update_id': 10000,
    'message': {
        'date': 1441645532,
        'chat': {
            'last_name': 'Test Lastname',
            'id': 11111,
            'type': 'private',
            'first_name': 'Test Firstname',
            'username': 'test_username',
        },
        'message_id': 1365,
        'from': {
            'is_bot': False,
            'last_name': 'Test Lastname',
            'id': 11111,
            'first_name': 'Test Firstname',
            'username': 'test_username',
        },
        'text': 'test',
    },
}


async def test_process_telegram_message(
        stq_runner: stq_plugin.Stq3Runner,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: authorization_mocks.MockedAuthorizationServicesContext,  # noqa: E501 (line too long)
        mockserver,  # To fail if there are unmocked calls
):
    update = UPDATE_REQUEST
    await stq_runner.contractor_merch_payments_bot_process_telegram_message.call(  # noqa: E501 (line too long)
        task_id='task_id', args=[], kwargs=dict(update=update),
    )
    mock_authorization_services.assert_services_called_once()
    assert mock_telegram_service.send_message.handler.times_called == 1
    request = mock_telegram_service.send_message.handler.next_call()['request']
    assert request.json == {
        'chat_id': CHAT_ID,
        'text': (
            'Простите, не могу понять Вас!\n'
            '\n'
            'Введите /start для начала работы!'
        ),
        'parse_mode': 'markdown',
    }
