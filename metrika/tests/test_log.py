import logging

import pytest
import os
import signal

import six
from metrika.pylib.log import get_logger, init_logger
from metrika.pylib.utils import retry, handle_signal_reopen_logs
from metrika.pylib.sh import run


SECRET = 'ASDqweZxC'


def get_log_file(file_name):
    cwd = os.getcwd()
    logfile = os.path.join(cwd, file_name)

    return logfile


class StrangeError(Exception):
    pass


@retry(StrangeError, delay=0.1, backoff=1, debug=True)
def some_function(log, *args, **kwargs):
    log.info("run some_function")
    raise StrangeError


@pytest.mark.parametrize('header', ('OAuth %s' % SECRET, 'Basic %s' % SECRET))
def test_filter_auth(header):
    log_file = get_log_file('test_filter_auth.log')
    logger = get_logger('test_filter_auth', log_file=log_file)
    init_logger('mtutils', log_file=log_file)

    headers = {'a': 1, 'Authorization': header, 'c': 3}

    if os.path.exists(log_file):
        with open(log_file, 'w'):
            pass

    try:
        some_function(logger, headers=headers)
    except StrangeError:
        pass

    assert os.path.isfile(log_file)

    with open(log_file) as f:
        data = f.read()

    assert SECRET not in data
    assert '*CENSORED*' in data


def test_reopen_log():
    log_file = get_log_file('test_reopen_log.log')

    if os.path.isfile(log_file):
        os.unlink(log_file)

    logger = get_logger('test_open_logs', log_file=log_file, rotating_bytes=False)
    handle_signal_reopen_logs([logger])

    logger.debug('init logger')

    assert os.path.isfile(log_file)

    os.rename(log_file, log_file + '.1')
    assert not os.path.isfile(log_file)

    open_files = [six.ensure_str(x).lstrip('n') for x in run(["lsof", "-Fn", "-p", str(os.getpid())]).splitlines()]
    assert log_file not in open_files
    assert log_file + '.1' in open_files

    os.kill(os.getpid(), signal.SIGHUP)
    open_files = [six.ensure_str(x).lstrip('n') for x in run(["lsof", "-Fn", "-p", str(os.getpid())]).splitlines()]
    assert log_file in open_files
    assert log_file + '.1' not in open_files
