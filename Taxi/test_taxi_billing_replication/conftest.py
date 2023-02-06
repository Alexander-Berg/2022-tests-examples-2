# pylint: disable=redefined-outer-name,unused-variable
import pytest

from taxi.pg.policies import single_policies
from taxi.pytest_plugins import service

import taxi_billing_replication
from taxi_billing_replication import config
from taxi_billing_replication import web


@pytest.fixture(autouse=True)
def _config(request, monkeypatch, configs_mock, taxi_config):
    marker = request.node.get_closest_marker('config')
    if not marker:
        return

    for config_key, value in marker.kwargs.items():
        monkeypatch.setattr(config.Config, config_key, value, raising=False)


POSTGRES_POOL_KWARGS = {'min_size': 0, 'max_size': 1}
POSTGRES_POOL_POLICY = single_policies.Master(
    close_pool_timeout=10,
    max_time_between_checks=None,
    check_host_timeout=1.0,
)


@pytest.fixture
def fixed_secdist(simple_secdist, pgsql_local):
    connection_dsn = pgsql_local['billing_replication'].get_dsn()
    simple_secdist['postgresql_settings']['databases'][
        'billing_replication'
    ] = [{'shard_number': 0, 'hosts': [connection_dsn]}]


@pytest.fixture
async def billing_replictaion_cron_app(loop, fixed_secdist):
    app = taxi_billing_replication.TaxiBillingReplicationApplication(
        pg_pool_policy=POSTGRES_POOL_POLICY,
        pg_pool_kwargs=POSTGRES_POOL_KWARGS,
        loop=loop,
    )

    for method in app.on_startup:
        await method(app)

    yield app
    for method in app.on_shutdown:
        await method(app)


@pytest.fixture
def taxi_billing_replictaion_app(loop, fixed_secdist):
    return web.create_app(loop=loop)


@pytest.fixture
def taxi_billing_replication_client(
        aiohttp_client, taxi_billing_replictaion_app, loop,
):
    return loop.run_until_complete(
        aiohttp_client(taxi_billing_replictaion_app),
    )


service.install_service_local_fixtures(__name__)
