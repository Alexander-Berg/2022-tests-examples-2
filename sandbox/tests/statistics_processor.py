import os
import random
import inspect
import itertools
import datetime as dt

import mock
import pytest

from sandbox import common
from sandbox.services.base import loader
from sandbox.services.modules import statistics_processor as sp
from sandbox.services.modules.statistics_processor.processors.base import Processor as BaseProcessor
from sandbox.common.types.statistics import SignalType


@pytest.fixture(scope="function")
def activate_config(config_path, client_node_id):
    os.environ["SANDBOX_CONFIG"] = config_path
    common.config.Registry().reload()
    assert common.config.Registry().this.id == client_node_id, "Config patching didn't work -- go figure"

    yield

    os.environ.pop("SANDBOX_CONFIG", None)
    common.config.Registry().reload()


@pytest.fixture(scope="function")
def statistics_processor(activate_config, statistics_db_name):
    """
    :rtype: sp.StatisticsProcessor
    """
    instance = loader.load_service(sp.StatisticsProcessor)
    instance._model = mock.MagicMock()
    instance.MAX_WORKER_IDLE_TIME = 0
    assert instance.make_db_connection().name == statistics_db_name

    yield instance


class TestStatisticsProcessor(object):
    def test__signals_are_removed_from_mongo(self, statistics_processor, monkeypatch):
        signal_type = SignalType.API_USAGE

        # provoke to add default value (for ClickHouseProcessor) to the dict
        # noinspection PyStatementEffect
        statistics_processor.PROCESSOR_CLASSES[signal_type]
        for class_ in filter(
            lambda c: inspect.isclass(c) and issubclass(c, BaseProcessor) and c is not BaseProcessor,
            list(itertools.chain.from_iterable(sp.StatisticsProcessor.PROCESSOR_CLASSES.values()))
        ):
            monkeypatch.setattr(class_, BaseProcessor.initialize.__name__, classmethod(lambda *_, **__: None))
            monkeypatch.setattr(class_, BaseProcessor.process.__name__, lambda *_, **__: None)

        payload = [
            {
                "date": dt.datetime.utcnow(),
                "timestamp": dt.datetime.utcnow(),
                "login": "white",
                "quota": random.random()
            }
            for _ in xrange(statistics_processor.MIN_CHUNK_SZ)
        ]

        db = statistics_processor.make_db_connection()
        db[signal_type].insert_many(payload)
        assert db[signal_type].find({}).count() == statistics_processor.MIN_CHUNK_SZ

        statistics_processor.tick()
        statistics_processor.on_stop()
        left = max(0, statistics_processor.MIN_CHUNK_SZ - statistics_processor.CHUNK_SZ[signal_type])

        # https://stackoverflow.com/questions/32666330/difference-between-count-and-find-count-in-mongodb
        assert db[signal_type].find({}).count() == left
