# pylint: disable=protected-access
import datetime
import time
import uuid

import pytest
import yarl

from taxi.util import evlog
from taxi.util.evlog import _timings

NOW = datetime.datetime(2018, 5, 7, 12, 34, 56)


@pytest.mark.now(NOW.isoformat())
async def test_event_logger(loop, db, simple_secdist, monkeypatch, mock):
    @mock
    def _dummy_log(*args, **kwargs):
        pass

    monkeypatch.setattr(_timings.logger, 'info', _dummy_log)
    monkeypatch.setattr(uuid, 'uuid4', _DummyUUID4)
    monkeypatch.setattr(time, 'clock', _dummy_clock)

    log_extra = evlog.new_group_extra()
    meta = {'some': 'meta', 'key': 123}
    some_event_logger = evlog.new_event('some_event', log_extra, **meta)
    some_event_logger.update(new_meta_key='convertable_to_string_value')
    some_event_logger.flush()

    logger_calls = _dummy_log.calls
    assert logger_calls[0]['args'] == (
        'tskv\ttskv_format=evlog\tgroup=hex\tevent=some_event\t'
        'timestamp=1525696496.0\telapsed_time=0.0\telapsed_clock=0.0\t'
        'elapsed_time_from_start=0.0\telapsed_clock_from_start=0.0\t'
        'some=meta\tkey=123\tnew_meta_key=convertable_to_string_value',
    )


@pytest.mark.now(NOW.isoformat())
async def test_time_storage(loop, db, simple_secdist, monkeypatch, mock):
    @mock
    def _dummy_log(*args, **kwargs):
        pass

    monkeypatch.setattr(_timings.logger, 'info', _dummy_log)
    monkeypatch.setattr(uuid, 'uuid4', _DummyUUID4)

    meta = {'some': 'meta', 'key': 123}
    time_storage = evlog.new_time_storage('some_event', **meta)

    with time_storage.get_timer('some_timer'):
        pass

    time_storage.write_log()

    logger_calls = _dummy_log.calls
    assert logger_calls[0]['args'] == (
        'tskv\ttskv_format=time_storage\tstopwatch_name=some_event\t'
        'timestamp=1525696496.0\tsome_timer_time=0.0\ttotal_time=0.0\t'
        'some=meta\tkey=123',
    )


@pytest.mark.now(NOW.isoformat())
async def test_log(loop, db, simple_secdist, monkeypatch, mock):
    @mock
    def _dummy_log(*args, **kwargs):
        pass

    monkeypatch.setattr(_timings.logger, 'info', _dummy_log)
    monkeypatch.setattr(uuid, 'uuid4', _DummyUUID4)

    log_extra = evlog.new_group_extra()
    evlog.log('some message', log_extra)

    logger_calls = _dummy_log.calls
    assert logger_calls[0]['args'] == (
        'tskv\ttskv_format=evlog\tgroup=hex\tevent=some message\t'
        'timestamp=1525696496.0\ttskv\ttskv_format=',
    )


@pytest.mark.now(NOW.isoformat())
async def test_wrap(monkeypatch, mock):
    @mock
    def _dummy_log(*args, **kwargs):
        pass

    monkeypatch.setattr(_timings.logger, 'info', _dummy_log)
    monkeypatch.setattr(uuid, 'uuid4', _DummyUUID4)
    monkeypatch.setattr(time, 'clock', _dummy_clock)

    @evlog.wrap('some_event', some='meta', key='123')
    def some_func(evlogger=None):
        evlogger.update(new_meta_key='convertable_to_string_value')

    some_func()

    logger_calls = _dummy_log.calls
    assert logger_calls[0]['args'] == (
        'tskv\ttskv_format=evlog\tgroup=hex\tevent=some_event\t'
        'timestamp=1525696496.0\telapsed_time=0.0\telapsed_clock=0.0\t'
        'elapsed_time_from_start=0.0\telapsed_clock_from_start=0.0\t'
        'some=meta\tkey=123\tnew_meta_key=convertable_to_string_value',
    )


@pytest.mark.now(NOW.isoformat())
async def test_wrap_async(monkeypatch, mock):
    @mock
    def _dummy_log(*args, **kwargs):
        pass

    monkeypatch.setattr(_timings.logger, 'info', _dummy_log)
    monkeypatch.setattr(uuid, 'uuid4', _DummyUUID4)
    monkeypatch.setattr(time, 'clock', _dummy_clock)

    @evlog.wrap_async('some_event', some='meta', key='123')
    async def some_func(evlogger=None):
        evlogger.update(new_meta_key='convertable_to_string_value')

    await some_func()

    logger_calls = _dummy_log.calls
    assert logger_calls[0]['args'] == (
        'tskv\ttskv_format=evlog\tgroup=hex\tevent=some_event\t'
        'timestamp=1525696496.0\telapsed_time=0.0\telapsed_clock=0.0\t'
        'elapsed_time_from_start=0.0\telapsed_clock_from_start=0.0\t'
        'some=meta\tkey=123\tnew_meta_key=convertable_to_string_value',
    )


@pytest.mark.now(NOW.isoformat())
async def test_wrap_session_request(monkeypatch, mock, response_mock):
    @mock
    def _dummy_log(*args, **kwargs):
        pass

    monkeypatch.setattr(_timings.logger, 'info', _dummy_log)
    monkeypatch.setattr(uuid, 'uuid4', _DummyUUID4)
    monkeypatch.setattr(time, 'clock', _dummy_clock)

    @evlog.wrap_session_request('some_event')
    async def some_func(evlogger=None):
        return response_mock(
            method='POST', url=yarl.URL('http://qwerty/asd'), status=200,
        )

    await some_func()

    logger_calls = _dummy_log.calls
    assert logger_calls[0]['args'] == (
        'tskv\ttskv_format=evlog\tgroup=hex\tevent=some_event\t'
        'timestamp=1525696496.0\telapsed_time=0.0\telapsed_clock=0.0\t'
        'elapsed_time_from_start=0.0\telapsed_clock_from_start=0.0\t'
        'url=http://qwerty/asd\tmethod=POST\tresponse_code=200',
    )


class _DummyUUID4:
    hex = 'hex'


def _dummy_clock():
    return 1.23
