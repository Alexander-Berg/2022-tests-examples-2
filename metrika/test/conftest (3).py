import pytest
import os
import logging

import metrika.pylib.structures.dotdict as dotdict
import metrika.admin.python.cms.marshal.lib.marshal as lib_marshal
import metrika.admin.python.cms.marshal.lib.helpers as helpers
import metrika.admin.python.cms.lib.pg.queue as lib_queue

from metrika.pylib.daemon.tests.fixtures import daemon_runner  # noqa

logger = logging.getLogger(__name__)


@pytest.fixture()
def config(monkeypatch, http_input_steps):
    config = {
        "debug": True,
        "master": {
            "loggers": ["marshal", "metrika", ""],
            "number_of_workers": 1,
            "port": http_input_steps.port,
            "logger_settings": {
                "stdout": True,
                "log_format": "%(asctime)s %(threadName)-12.12s %(processName)-12.12s %(name)48.48s %(levelname)-.1s %(message)s"
            }
        },
        "agent_port": 99999,
        "database": {
            "host": os.getenv("POSTGRES_RECIPE_HOST"),
            "port": os.getenv("POSTGRES_RECIPE_PORT"),
            "name": os.getenv("POSTGRES_RECIPE_DBNAME"),
            "user": os.getenv("POSTGRES_RECIPE_USER"),
            "password": "",
        },
        "iteration_idle_time": 1,
        "frontend": "some url",
        "queue": "marshal_queue",
        "lock": "marshal_lock",
        "agent_operation_timeout": 5,
        "agent_operation_poll_period": 1,
        "poll_period": 1,
        "postpone_loading_initiate": 1,
        "postpone_loading_poll": 1
    }

    logger.info("config: {}".format(config))

    config_obj = dotdict.DotDict.from_dict(config)

    monkeypatch.setattr(helpers, "_config", config_obj)

    return config_obj


@pytest.fixture()
def marshal(config):
    return lib_marshal.Marshal()


@pytest.fixture()
def daemon(marshal, output_steps):
    output_steps.setup_internal_api_mock()
    output_steps.setup_agent_api_mock()
    output_steps.setup_walle_mock()
    return marshal


@pytest.fixture()
def queue(config):
    q = lib_queue.Queue(identity="test-step-marshal", name=config.queue, connection_manager=helpers.get_connection_manager())
    yield q
    try:
        logger.info("Queue items: {}".format(q.list()))
        q.connection_manager.close()
    except:
        logger.warning("Exception in queue listing. Continue.", exc_info=True)
