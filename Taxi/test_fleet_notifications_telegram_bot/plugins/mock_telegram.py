import pytest


@pytest.fixture(name='telegram')
def _mock_telegram(mockserver):
    class Telegram:
        def __init__(self):
            self.telegram_login = None

        def set_telegram_login(self, telegram_login):
            self.telegram_login = telegram_login

    telegram = Telegram()

    @mockserver.json_handler('/telegram/bot123456:test_token/sendMessage')
    async def _send(request):
        return {'ok': True}

    @mockserver.json_handler('/telegram/bot123456:test_token/getChat')
    async def _get_chat(request):
        return {'ok': True, 'result': {'username': telegram.telegram_login}}

    return telegram
