import pytest


@pytest.fixture
def telegram(patch, mock, monkeypatch):
    patch_token = 'telegram-token'
    monkeypatch.setenv('TELEGRAM_BOT_TOKEN', patch_token)

    @mock
    def init(token):
        pass

    @mock
    def send_message(
            chat_id,
            text,
            parse_mode,
            disable_notification,
            disable_web_page_preview,
    ):
        pass

    class Bot:
        def __init__(self, token):
            init(token)

        @staticmethod
        def send_message(*args, **kwargs):
            send_message(*args, **kwargs)

    monkeypatch.setattr('telegram.Bot', Bot)

    yield send_message

    assert all(call['token'] == patch_token for call in init.calls)
