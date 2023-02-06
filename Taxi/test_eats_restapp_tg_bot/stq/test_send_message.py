# pylint: disable=redefined-outer-name, protected-access

import functools
import logging

import pytest

from eats_restapp_tg_bot.stq import send_message

logger = logging.getLogger(__name__)


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


@pytest.fixture
def mock_send_message(monkeypatch):
    @_calls
    def _send_message(self, *args, **kwargs):
        pass

    monkeypatch.setattr('telegram.bot.Bot.send_message', _send_message)
    return _send_message


@pytest.fixture(name='send_message_stq_runner')
def _send_message_stq_runner(stq3_context, load_json):
    async def call_stq(kwargs_name=None):
        if kwargs_name is None:
            kwargs_name = 'default'
        await send_message.task(
            stq3_context, **load_json('stq_kwargs.json')[kwargs_name],
        )

    return call_stq


@pytest.fixture
def proxy_mocks(mock_rate_limiter_proxy, mockserver):
    @mock_rate_limiter_proxy('/quota')
    async def _quota(request):
        return mockserver.make_response(
            request._data,  # pylint: disable=protected-access
            content_type='application/flatbuffer',
        )


@pytest.mark.pgsql('eats_restapp_tg_bot', files=['default.sql'])
async def test_should_send_message_if_login_exist_in_database(
        send_message_stq_runner, mock_send_message, proxy_mocks, stq3_context,
):
    await send_message_stq_runner()
    assert len(mock_send_message.calls) == 1


@pytest.mark.pgsql('eats_restapp_tg_bot', files=['default.sql'])
async def test_should_not_send_message_if_login_does_not_exist(
        send_message_stq_runner, mock_send_message, proxy_mocks, stq3_context,
):
    await send_message_stq_runner('not_existed')
    assert not mock_send_message.calls


@pytest.mark.pgsql('eats_restapp_tg_bot', files=['default.sql'])
@pytest.mark.config(
    EATS_RESTAPP_TG_BOT_SEND_MESSAGE_SETTINGS={
        'max_message_size': 5,
        'max_retries': 3,
        'parse_mode': 'html',
    },
)
async def test_should_send_more_than_one_message_if_length_more_than_max_size(
        send_message_stq_runner, mock_send_message, proxy_mocks, stq3_context,
):
    await send_message_stq_runner()
    assert len(mock_send_message.calls) == 2


@pytest.mark.pgsql('eats_restapp_tg_bot', files=['default.sql'])
async def test_should_send_message_for_multiple_logins(
        send_message_stq_runner, mock_send_message, proxy_mocks, stq3_context,
):
    await send_message_stq_runner('multiple_logins')
    assert len(mock_send_message.calls) == 2


@pytest.mark.pgsql('eats_restapp_tg_bot', files=['default.sql'])
@pytest.mark.config(EATS_RESTAPP_TG_BOT_ENABLE_PERSONAL=True)
async def test_should_send_message_if_personal_login_exist_in_database(
        send_message_stq_runner,
        mock_send_message,
        proxy_mocks,
        stq3_context,
        mock_personal,
):
    @mock_personal('/v1/telegram_ids/retrieve')
    async def _mock_retrieve(request):
        return {'id': '1', 'value': '2'}

    await send_message_stq_runner('personal')
    assert len(mock_send_message.calls) == 1


@pytest.mark.pgsql('eats_restapp_tg_bot', files=['default.sql'])
@pytest.mark.config(EATS_RESTAPP_TG_BOT_ENABLE_PERSONAL=True)
async def test_should_not_send_message_if_personal_login_does_not_exist(
        send_message_stq_runner,
        mock_send_message,
        proxy_mocks,
        stq3_context,
        mock_personal,
):
    @mock_personal('/v1/telegram_ids/retrieve')
    async def _mock_retrieve(request):
        return {'id': '1', 'value': '2'}

    await send_message_stq_runner('not_existed_personal')
    assert not mock_send_message.calls


@pytest.mark.pgsql('eats_restapp_tg_bot', files=['default.sql'])
@pytest.mark.config(EATS_RESTAPP_TG_BOT_ENABLE_PERSONAL=True)
async def test_should_send_message_for_multiple_logins_with_personal(
        send_message_stq_runner,
        mock_send_message,
        proxy_mocks,
        stq3_context,
        mock_personal,
):
    @mock_personal('/v1/telegram_ids/retrieve')
    async def _mock_retrieve(request):
        return {'id': '1', 'value': '2'}

    await send_message_stq_runner('multiple_logins_personal')
    assert len(mock_send_message.calls) == 2
