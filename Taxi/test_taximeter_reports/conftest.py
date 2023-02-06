# pylint: disable=redefined-outer-name,protected-access
import pytest

from taxi.pytest_plugins import service


pytest_plugins = ['taxi.pytest_plugins.stq_agent']


@pytest.fixture
def taximeter_reports_app(loop, simple_secdist, db, mongodb_init, monkeypatch):
    # should be here because of use secdist in stq_config
    from taximeter_reports import app
    from taximeter_reports import stq_setup

    monkeypatch.setattr(
        'taxi.util.aiohttp_kit.context.cache_refresh_periodic', _dummy,
    )
    app_instance = app.create_app(loop=loop, db=db)
    _patch_stq(monkeypatch)
    loop.run_until_complete(
        stq_setup._add_taximeter_reports_utils(app_instance),
    )
    monkeypatch.setattr(
        app_instance.config, 'TAXIMETER_BACKEND_APIKEY', 'secret',
    )
    return app_instance


@pytest.fixture
def taximeter_reports_client(aiohttp_client, taximeter_reports_app, loop):
    return loop.run_until_complete(aiohttp_client(taximeter_reports_app))


def _patch_stq(monkeypatch):
    monkeypatch.setattr('stq.config.setup_config', _dummy)


async def _dummy(*args, **kwargs):
    pass


service.install_service_local_fixtures(__name__)
