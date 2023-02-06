from typing import NamedTuple
from typing import Optional

from aiohttp import web
import pytest

from clownductor.crontasks.sync_market_services import tvm_services_syncer
from clownductor.generated.cron import run_cron
from clownductor.internal.market_sync import constants as market_constants


class TvmService(NamedTuple):
    name: str
    production_id: Optional[int] = None
    testing_id: Optional[int] = None
    clown_id: Optional[int] = None
    project_id: Optional[int] = None


TvmRule = tvm_services_syncer.TvmRule


TSUM_PROJECTS = [
    {
        'name': 'market-project-known',
        'abc_slug': 'market_project_known',
        'services': [
            {
                'abc_slug': 'market_service_known_1',
                'name': 'market-service-known-1',
                'tvm': {'production': 1000, 'testing': 1100},
            },
            {
                'abc_slug': 'market_service_unknown_1',
                'name': 'market-service-unknown-1',
                'tvm': {'production': 2000, 'testing': 2100},
            },
            {
                'abc_slug': 'nanny_service_known_1',
                'name': 'nanny-service-known-1',
                'tvm': {'testing': 3100},
            },
        ],
    },
    {
        'name': 'market-project-unknown',
        'abc_slug': 'market_project_unknown',
        'services': [
            {
                'abc_slug': 'market_service_unknown_2',
                'name': 'market-service-unknown-2',
                'tvm': {},
            },
            {
                'abc_slug': 'market_service_moved_1',
                'name': 'market-service-moved-1',
                'tvm': {'production': 4000, 'testing': 4100},
            },
        ],
    },
]


EXISTED_SERVICES = [
    TvmService('some_service', 900),
    TvmService('market_market-service-known-1', 1000, 1100),
    TvmService('market_market-service-unknown-1', None, 2100, 1, 1),
    TvmService('taxi_exp', 123, 123, 123, 123),
    TvmService('experiments3-proxy', 124, 124, 124, 124),
    TvmService('statistics', 125, 125, 125, 125),
]

EXISTED_RULES = [
    TvmRule('some_service', 'some_service', 'production'),
    TvmRule('market_market-service-known-1', 'statistics', 'testing'),
    TvmRule('market_market-service-known-1', 'statistics', 'production'),
    TvmRule('market_market-service-known-1', 'taxi_exp', 'testing'),
    TvmRule('market_market-service-known-1', 'experiments3-proxy', 'testing'),
]


@pytest.mark.pgsql('clownductor', files=['init_test_data.sql'])
@pytest.mark.usefixtures('perforator_mockserver')
@pytest.mark.features_on('sync_market_services_with_tvm')
async def test_sync_market_services(
        mock_tsum,
        get_project,
        get_service_by_name,
        mock_perforator_context,
        web_context,
):
    @mock_tsum('/registry/api/general/taxi-sync')
    async def _handler(request):
        assert request.headers['authorization']
        return web.json_response({'projects': TSUM_PROJECTS})

    for tvm_service in EXISTED_SERVICES:
        mock_perforator_context.add_service(
            tvm_service.name,
            tvm_service.production_id,
            tvm_service.testing_id,
            tvm_service.clown_id,
            tvm_service.project_id,
        )

    for tvm_rule in EXISTED_RULES:
        mock_perforator_context.add_env_rule(
            tvm_rule.source, tvm_rule.destination, tvm_rule.env_type,
        )

    await run_cron.main(
        [
            'clownductor.crontasks.sync_market_services.sync_market_services',
            '-t',
            '0',
        ],
    )

    assert _handler.times_called == 1
    tvm_services = {}
    for service in mock_perforator_context.services:
        tvm_obj = {env.env_type: env.tvm_id for env in service.environments}
        tvm_services[service.tvm_name] = tvm_obj

    tvm_rules = {
        TvmRule(rule.source.tvm_name, rule.destination.tvm_name, rule.env_type)
        for rule in mock_perforator_context.rules
    }

    all_projects = await web_context.service_manager.projects.get_all()
    assert len(all_projects) == len(TSUM_PROJECTS) + 1
    taxi_project = await get_project('taxi-project')
    assert taxi_project

    for tsum_project in TSUM_PROJECTS:
        stored_project = await get_project(tsum_project['name'])
        assert stored_project
        assert stored_project['service_abc'] == tsum_project['abc_slug']
        for service in tsum_project['services']:
            service_name = service['name']
            tvm_name = f'market_{service_name}'
            tvm_service = tvm_services.pop(tvm_name, {})
            assert tvm_service == service['tvm']
            for env_type in service['tvm']:
                for destination in market_constants.DEFAULT_DESTINATIONS:
                    tvm_rules.remove(TvmRule(tvm_name, destination, env_type))
            stored_service = await get_service_by_name(
                service_name, 'market_service', stored_project['id'],
            )
            assert stored_service, (
                stored_service['abc_service'] == service['abc_slug']
            )
    assert tvm_services.keys() == {'some_service'}.union(
        market_constants.DEFAULT_DESTINATIONS,
    )
    assert tvm_rules == {TvmRule('some_service', 'some_service', 'production')}
