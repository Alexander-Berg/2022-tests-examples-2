# pylint: disable=redefined-outer-name, protected-access

import contextlib
import functools
import logging
import threading

import pytest
import telegram

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def run_poll(context):
    context.tgm_bot.bot.start()
    try:
        yield
    finally:
        context.tgm_bot.bot.stop()


def _calls(func):
    calls = []

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug('Call %s', func.__qualname__)
        result = func(*args, **kwargs)
        calls.append({'args': args, 'kwargs': kwargs, 'result': result})
        return result

    wrapper.calls = calls

    return wrapper


@pytest.fixture(autouse=True)
def mock_delete_webhook(monkeypatch):
    @_calls
    def _delete_webhook(self, *args, **kwargs):
        pass

    monkeypatch.setattr('telegram.bot.Bot.delete_webhook', _delete_webhook)
    return _delete_webhook


@pytest.fixture(autouse=True)
def check_non_mocked_telegram_calls(patch):
    is_called = threading.Event()
    calls = set()

    @patch('telegram.utils.request.Request._request_wrapper')
    def _request_wrapper(method, url, *args, **kwargs):
        calls.add((method, url))
        is_called.set()

    yield

    if is_called.is_set():
        assert False, 'Not mocked calls: {}'.format(
            ', '.join(f'{x[0]} {x[1]}' for x in calls),
        )


@pytest.fixture
def mock_get_me(monkeypatch):
    @_calls
    def _get_me(self, *args, **kwargs):
        assert self.base_url == 'https://api.telegram.org/bot123:some'
        self.bot = telegram.User(
            id='123',
            username='bot-name',
            first_name='bot-name',
            is_bot=True,
            bot=self,
        )
        return self.bot

    monkeypatch.setattr('telegram.bot.Bot.get_me', _get_me)
    return _get_me


@pytest.fixture
def mock_get_my_commands(monkeypatch):
    @_calls
    def _get_my_commands(self, *args, **kwargs):
        self._commands = []
        return self._commands

    monkeypatch.setattr('telegram.bot.Bot.get_my_commands', _get_my_commands)
    return _get_my_commands


@pytest.fixture
def mock_get_updates(monkeypatch):
    def _do_it(raw_updates, called_event: threading.Event):
        already_called = False

        @_calls
        def _get_updates(self, *args, **kwargs):
            nonlocal already_called
            if already_called:
                return []

            already_called = True
            called_event.set()
            return [telegram.Update.de_json(x, self) for x in raw_updates]

        monkeypatch.setattr('telegram.bot.Bot.get_updates', _get_updates)
        return _get_updates

    return _do_it


@pytest.fixture
def mock_send_message(monkeypatch):
    @_calls
    def _send_message(self, *args, **kwargs):
        pass

    monkeypatch.setattr('telegram.bot.Bot.send_message', _send_message)
    return _send_message


@pytest.mark.config(
    EDA_QC_PHOTO_BOT_SETTINGS={
        'developer_ids': [],
        'poll_interval': 0.1,
        'polling_enabled': True,
    },
)
def test_empty_updates(
        web_context, mock_get_me, mock_get_my_commands, mock_get_updates,
):
    updates_called = threading.Event()
    updates_mocker = mock_get_updates([], updates_called)

    with run_poll(web_context):
        updates_called.wait()

    assert len(mock_get_me.calls) == 1
    assert len(mock_get_my_commands.calls) == 1
    assert all(not x['result'] for x in updates_mocker.calls)


@pytest.mark.config(
    EDA_QC_PHOTO_BOT_SETTINGS={
        'developer_ids': [],
        'poll_interval': 0.1,
        'polling_enabled': True,
    },
)
@pytest.mark.parametrize('command', ['s', 'start'])
def test_start_commands(
        web_context,
        mock_get_me,
        mock_get_my_commands,
        mock_get_updates,
        mock_send_message,
        command,
):
    updates_called = threading.Event()
    updates_mocker = mock_get_updates(
        [
            {
                'update_id': 985498436,
                'message': {
                    'message_id': 41,
                    'date': 1590651144,
                    'chat': {
                        'id': 379425963,
                        'type': 'private',
                        'username': 'd1mbas',
                        'first_name': '[ONLINE] Дмитрий',
                        'last_name': 'Тамбовцев',
                    },
                    'text': f'/{command}',
                    'entities': [
                        {'type': 'bot_command', 'offset': 0, 'length': 7},
                    ],
                    'caption_entities': [],
                    'photo': [],
                    'new_chat_members': [],
                    'new_chat_photo': [],
                    'delete_chat_photo': False,
                    'group_chat_created': False,
                    'supergroup_chat_created': False,
                    'channel_chat_created': False,
                    'from': {
                        'id': 379425963,
                        'first_name': '[ONLINE] Дмитрий',
                        'is_bot': False,
                        'last_name': 'Тамбовцев',
                        'username': 'd1mbas',
                        'language_code': 'ru',
                    },
                },
            },
        ],
        updates_called,
    )

    with run_poll(web_context):
        updates_called.wait()

    assert len(mock_get_me.calls) == 1
    assert len(mock_get_my_commands.calls) == 1
    non_empty_result = [
        x['result'] for x in updates_mocker.calls if x['result']
    ]
    assert len(non_empty_result) == 1

    assert len(mock_send_message.calls) == 1
    assert mock_send_message.calls[0]['args'] == (
        web_context.tgm_bot.bot._updater.bot,
        379425963,
        'Чтобы загрузить фото, нажмите на кнопку',
    )
    assert mock_send_message.calls[0]['kwargs'].keys() == {'reply_markup'}
    assert mock_send_message.calls[0]['kwargs']['reply_markup'].keyboard == [
        ['Загрузить фото'],
    ]
