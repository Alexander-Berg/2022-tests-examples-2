import logging
import time

from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor
from twisted.internet.task import deferLater


logger = logging.getLogger('stq')


def sleep(secs):
    return deferLater(reactor, secs, lambda: None)


def async_setup():
    reactor.callLater(0, logger.info, '<test queue worker async setup>')


def blocking_setup():
    logger.info('<test queue worker blocking setup>')


@inlineCallbacks
def async_process(failure=False):
    logger.info('<test queue worker async process>')
    yield sleep(0.1)
    if failure:
        raise RuntimeError('test error')


def blocking_process(failure=False):
    logger.info('<test queue worker blocking process>')
    time.sleep(0.1)
    if failure:
        raise RuntimeError('test error')
