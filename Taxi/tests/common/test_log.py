import io
import os
import socket
import sys

import pytest

from libstall import cfg
from libstall.loggers.base import get_logger
from stall import log


def test_log(tap):
    """Тестируем логи"""
    tap.plan(5)

    tap.eq(log.debug('Тестовое сообщение'), None, 'debug')
    tap.eq(log.info('Тестовое сообщение'), None, 'info')
    tap.eq(log.warning('Тестовое сообщение'), None, 'warning')
    tap.eq(log.error('Тестовое сообщение'), None, 'error')
    tap.eq(log.critical('Тестовое сообщение'), None, 'critical')

    tap()


@pytest.mark.parametrize('mode', ['stdout', 'syslog'])
@pytest.mark.parametrize('fmt', ['tskv', 'json', 'metrics'])
async def test_loggers_modes(tap, monkeypatch, mode, fmt):
    error_stream = io.StringIO()
    monkeypatch.setattr(sys, 'stderr', error_stream)

    with tap:
        loggers_conf = cfg('logs')

        for name, config in loggers_conf.items():
            cfg.set(f'logs.{name}', {
                **config,
                'mode': [[mode, fmt]],
            })

            logger = get_logger(name)
            logger.error('Тестовое сообщение', name='test-name', value=1)

            if not tap.eq(error_stream.tell(), 0, 'no logging errors'):
                error_stream.seek(0)
                monkeypatch.undo()
                sys.stderr.write(error_stream.read())

        cfg.reload()


@pytest.fixture(autouse=True)
def syslog_socket(uuid):
    socket_file = str(uuid())

    server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    server.bind(socket_file)

    cfg.set('syslog.address', socket_file)
    yield socket_file
    cfg.reload()

    server.close()
    os.remove(socket_file)
