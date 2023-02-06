# pylint: disable=redefined-outer-name
import contextlib

import pytest

from taxi import config
from taxi import opentracing
from taxi.opentracing import _global_vars
from taxi.opentracing import tracer as tracer_
from taxi.opentracing.ext import web_app


@pytest.fixture
async def test_opentracing_app(loop, db, simple_secdist):
    app = web_app.TaxiApplication(
        config_cls=config.Config, loop=loop, db=db, service_name='TESTING',
    )
    yield app
    await app.close_sessions()


@pytest.fixture
def tracer(monkeypatch):
    _tracer = opentracing.init_tracing('testing')
    yield _tracer
    monkeypatch.setattr(
        _global_vars, 'TRACER', tracer_.NoOpTracer(config=config.Config),
    )


@pytest.fixture
def tracer_custom_config(monkeypatch):
    @contextlib.contextmanager
    def inner(**config_updates):
        cfg = opentracing.config_mock(**config_updates)
        _tracer = opentracing.init_tracing('testing', config=cfg)
        yield _tracer
        monkeypatch.setattr(
            _global_vars, 'TRACER', tracer_.NoOpTracer(config=config.Config),
        )

    return inner
