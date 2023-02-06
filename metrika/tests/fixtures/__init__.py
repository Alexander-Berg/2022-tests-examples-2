import pytest
import logging
import threading

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def daemon_runner(daemon):
    """
    Fixture for running daemon in test. Useful in tests of various daemon implementations.

    :param daemon: fully configured daemon object fixture
    :return: thread running daemon.start() method so that we get in-process daemon running with monkey-patching available
    """
    logger.info("Starting daemon {}".format(daemon.name))
    daemon_runner = threading.Thread(target=daemon.start, daemon=True, name="daemon")
    daemon_runner.start()
    logger.info("Started daemon {}".format(daemon.name))
    yield daemon_runner
    logger.info("Stopping daemon {}".format(daemon.name))
    daemon.stop()
    daemon_runner.join()
    logger.info("Stopped daemon {}".format(daemon.name))
