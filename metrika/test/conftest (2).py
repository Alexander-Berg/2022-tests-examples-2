import pytest
import os
import logging

import metrika.pylib.structures.dotdict as dotdict
import metrika.admin.python.cms.judge.lib.judge as lib_judge
import metrika.admin.python.cms.judge.lib.helpers as helpers
import metrika.admin.python.cms.lib.pg.queue as lib_queue
from metrika.admin.python.cms.judge.lib.decider import decision, utils
from metrika.admin.python.cms.judge.lib.decider.decider_provider import deciders, make

from metrika.pylib.daemon.tests.fixtures import daemon_runner  # noqa

logger = logging.getLogger(__name__)


@pytest.fixture()
def config(monkeypatch, http_input_steps):
    config = {
        "debug": True,
        "master": {
            "loggers": ["judge", "metrika", ""],
            "number_of_workers": 1,
            "port": http_input_steps.port,
            "logger_settings": {
                "stdout": True,
                "log_format": "%(asctime)s %(threadName)-12.12s %(processName)-12.12s %(name)48.48s %(levelname)-.1s %(message)s"
            }
        },
        "database": {
            "host": os.getenv("POSTGRES_RECIPE_HOST"),
            "port": os.getenv("POSTGRES_RECIPE_PORT"),
            "name": os.getenv("POSTGRES_RECIPE_DBNAME"),
            "user": os.getenv("POSTGRES_RECIPE_USER"),
            "password": "",
        },
        "iteration_idle_time": 1,
        "frontend": "some url",
        "queue": "judge_queue",
        "lock": "judge_lock",
        "postpone_inprogress_seconds": 1,
        "agent_port": 0,
        "decider": {
            "max_unloaded_hosts": 1,
            "mtcmsstand": {
                "testing": {
                    "enabled": True,
                    "max_unloaded_hosts": 1,
                    "max_unloaded_hosts_per_shard": 1
                }
            },
            "mtcalclog": {
                "testing": {
                    "enabled": True,
                    "max_unloaded_hosts": 1
                }
            },
            "test": {
                "test": {
                    "enabled": True,
                }
            }
        }
    }

    logger.info("config: {}".format(config))

    config_obj = dotdict.DotDict.from_dict(config)

    monkeypatch.setattr(helpers, "_config", config_obj)

    return config_obj


@pytest.fixture()
def judge(config):
    return lib_judge.Judge()


@pytest.fixture()
def daemon(judge, output_steps):
    output_steps.setup_internal_api_mock()
    output_steps.setup_cluster_api_mock()
    output_steps.setup_agent_api_mock()
    return judge


@pytest.fixture()
def queue(config):
    q = lib_queue.Queue(identity="test-step-judge", name=config.queue, connection_manager=helpers.get_connection_manager())
    yield q
    try:
        logger.info("Queue items: {}".format(q.list()))
        q.connection_manager.close()
    except:
        logger.warning("Exception in queue listing. Continue.", exc_info=True)


deciders.register_builder(make("test-cluster-always-ok", "unit-testing"), utils.create_decider(decision.Decision.OK))
deciders.register_builder(make("test-cluster-always-reject", "unit-testing"), utils.create_decider(decision.Decision.REJECT))
deciders.register_builder(make("test-cluster-always-inprogress", "unit-testing"), utils.create_decider(decision.Decision.IN_PROGRESS))
