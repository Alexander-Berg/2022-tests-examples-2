# pylint: disable=redefined-outer-name, protected-access

import functools
import logging

import pytest

from taxi.stq import async_worker_ng

from eats_supply_orders_bot.stq import send_message


PERSONAL_ID_TO_TG_ID = {'pd123456': '-999123456'}


logger = logging.getLogger(__name__)


@pytest.fixture
def mock_send_message(monkeypatch):
    @_calls
    def _send_message(self, *args, **kwargs):
        pass

    monkeypatch.setattr('telegram.bot.Bot.send_message', _send_message)
    return _send_message


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


def _build_task_info():
    return async_worker_ng.TaskInfo(
        id='1', exec_tries=1, reschedule_counter=1, queue='',
    )


@pytest.mark.pgsql(
    'eats_supply_orders_bot', files=['notification_history.sql'],
)
async def test_should_not_send_message_if_no_telegram_id(
        personal, load_json, stq3_context, mock_send_message,
):
    json = load_json('send_message.json')
    with pytest.raises(Exception):
        await send_message.task(stq3_context, _build_task_info(), **json)
    assert not mock_send_message.calls


@pytest.mark.pgsql(
    'eats_supply_orders_bot', files=['notification_history.sql'],
)
async def test_should_not_send_message_if_exceed_retry_limit(
        personal, load_json, stq3_context, mock_send_message,
):
    personal.set_personal_to_tg_id(PERSONAL_ID_TO_TG_ID)
    json = load_json('send_message_with_exceeded_limit.json')
    await send_message.task(stq3_context, _build_task_info(), **json)
    assert not mock_send_message.calls


@pytest.mark.pgsql(
    'eats_supply_orders_bot', files=['notification_history.sql'],
)
async def test_send_message(
        personal, load_json, stq3_context, mock_send_message,
):
    personal.set_personal_to_tg_id(PERSONAL_ID_TO_TG_ID)
    json = load_json('send_message.json')
    await send_message.task(stq3_context, _build_task_info(), **json)
    assert len(mock_send_message.calls) == 1
