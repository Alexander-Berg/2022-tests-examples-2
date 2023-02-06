import pytest

from contractor_merch_payments_bot.generated.stq3 import (
    pytest_plugin as stq_plugin,
)
from test_contractor_merch_payments_bot.mocks import (
    authorization as authorization_mocks,
)
from test_contractor_merch_payments_bot.mocks import telegram as telegram_mocks


def get_payment_id(text: str) -> str:
    start = text.index('*')
    end = text.rindex('*')

    return text[start + 1 : end]


PAYMENT_ID = 'YANDEXPRO-39df42fa77f7401fad39b72b2482379a'


@pytest.mark.parametrize(
    ['complexity'],
    [
        pytest.param('easy', id='easy'),
        pytest.param('medium', id='medium'),
        pytest.param('hard', id='hard'),
        pytest.param('ultra_hard', id='ultra_hard'),
        pytest.param('rotated', id='rotated'),
        pytest.param('vertically_inverted', id='vertically_inverted'),
        pytest.param('horizontally_inverted', id='horizontally_inverted'),
    ],
)
async def test_qr_code_parser(
        stq_runner: stq_plugin.Stq3Runner,
        mockserver,
        mock_telegram_service: telegram_mocks.MockedTelegramServiceContext,
        mock_authorization_services: (
            authorization_mocks.MockedAuthorizationServicesContext
        ),
        mock_contractor_merch_payments,
        load_json,
        complexity,
):
    mock_telegram_service.download_file.image = f'qr_codes/{complexity}.jpg'

    update = load_json('request_with_photo.json')
    await (
        stq_runner.contractor_merch_payments_bot_process_telegram_message.call(
            task_id='task_id', args=[], kwargs=dict(update=update),
        )
    )

    send_message_request = (
        mock_telegram_service.send_message.handler.next_call()['request']
    )
    assert get_payment_id(send_message_request.json['text']) == PAYMENT_ID
