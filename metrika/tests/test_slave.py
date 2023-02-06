import time
import mock
import threading
import pytest

from datetime import datetime
import metrika.pylib.daemon.slave as mslave


class SlaveTestError(Exception):
    def __init__(self, message=None):
        self.message = message


def test_slave_init(master):
    """
    Test slave set correct attributes if only master is given
    """
    value = 666
    _id = value
    name = 'TestSlave'
    slave = mslave.Slave(
        _id=_id,
        name=name,
        master=master,
    )

    assert slave.name == '{}-{}'.format(name, _id)
    assert slave.shutdown is master.shutdown

    assert slave.master == master
    assert slave.logger.parent == master.logger
    assert slave.logger.name.split('.')[-1] == name
    assert slave.config == master.config
    assert isinstance(slave.started, datetime)


def test_slave_init_override(master):
    """
    Test slave correctly override attributes even if master is given
    """
    value = 666
    slave = mslave.Slave(
        master=master,
        config=value,
        shutdown=value,
        logger=value,
    )
    assert slave.shutdown == value
    assert slave.logger == value
    assert slave.config == value


def test_init_without_name():
    slave = mslave.Slave()
    assert slave.name == 'Slave'


def test_run_not_implemented(slave):
    with pytest.raises(NotImplementedError):
        slave.run()


def test_default_status(slave):
    assert isinstance(slave.status(), dict)


def test_await_message(slave, monkeypatch):
    """
    Test if await correctly overrides default message
    """
    def mock_logger_debug(message):
        raise SlaveTestError(message=message)

    monkeypatch.setattr(slave.logger, 'debug', mock_logger_debug)

    await_timeout = 1
    desired_message = mslave.DEFAULT_AWAIT_MESSAGE_TPL.format(await_timeout)
    try:
        slave.sleep(await_timeout)
    except SlaveTestError as err:
        assert err.message == desired_message

    desired_message = 'Hello, World!'
    try:
        slave.sleep(await_timeout, message=desired_message)
    except SlaveTestError as err:
        assert err.message == desired_message


def test_await_timeout(slave, monkeypatch):
    """
    Test if await correctly uses timeout
    Count the number of times time.sleep called
    """
    mock_sleep = mock.Mock()

    monkeypatch.setattr(time, 'sleep', mock_sleep)
    await_timeout = 5
    slave.sleep(await_timeout)

    assert mock_sleep.call_count == await_timeout


def test_await_shutdowns_break(slave, monkeypatch):
    """
    Test if await correctly uses timeout
    Count the number of times time.sleep called
    """
    mock_sleep = mock.Mock()

    monkeypatch.setattr(time, 'sleep', mock_sleep)

    slave.shutdown.set()
    slave.sleep(5)

    assert mock_sleep.call_count == 0


def test_await_events_break(slave, monkeypatch):
    """
    Test if await correctly uses timeout
    Count the number of times time.sleep called
    """
    mock_sleep = mock.Mock()

    monkeypatch.setattr(time, 'sleep', mock_sleep)
    event = threading.Event()
    event.set()
    slave.sleep(5, events=[event])

    assert mock_sleep.call_count == 0


def test_await_events_type(slave):
    with pytest.raises(AttributeError):
        slave.sleep(1, events='string')

    with pytest.raises(AttributeError):
        slave.sleep(1, events=['hello'])


def test_await_timeout_type(slave):
    with pytest.raises(ValueError):
        slave.sleep('str')


def test_send_event_to_juggler(slave, monkeypatch):
    """
    Test master method are called
    """
    def mock_send_event_to_juggler(*args, **kwargs):
        raise SlaveTestError("Test Error")

    monkeypatch.setattr(slave.master, 'send_event_to_juggler', mock_send_event_to_juggler)

    with pytest.raises(SlaveTestError):
        slave.send_event_to_juggler()


def test_send_metric_to_graphite(slave, monkeypatch):
    """
    Test master method are called
    """
    def mock_send_metric_to_graphite(*args, **kwargs):
        raise SlaveTestError("Test Error")

    monkeypatch.setattr(slave.master, 'send_metric_to_graphite', mock_send_metric_to_graphite)

    with pytest.raises(SlaveTestError):
        slave.send_metric_to_graphite()
