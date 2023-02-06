from .base import BaseClient


class TelegramClient(BaseClient):
    def __init__(self, chat_id, bot_token, **kwargs):
        super().__init__(**kwargs)
        self._chat_id = chat_id
        self._base_url = 'https://api.telegram.org/' + 'bot' + bot_token + '/'

    def send_message(self, message, parse_mode=None):
        params = {'chat_id': self._chat_id, 'text': message}
        if parse_mode:
            params.update({'parse_mode': parse_mode})
        return self._perform_post('sendMessage', params=params)

    def make_bold(self, text):
        return '<strong>{}</strong>'.format(text)

    def make_code_style(self, text):
        return '<code>{}</code>'.format(text)
