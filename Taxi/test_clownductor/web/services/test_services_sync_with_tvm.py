from typing import NamedTuple
from typing import Optional

import pytest

from clownductor.crontasks.sync_market_services import tvm_services_syncer
from clownductor.internal.market_sync import constants as market_constants


class TvmService(NamedTuple):
    name: str
    production_id: Optional[int] = None
    testing_id: Optional[int] = None
    clown_id: Optional[int] = None
    project_id: Optional[int] = None


TvmRule = tvm_services_syncer.TvmRule

EXISTED_SERVICES = [
    TvmService('taxi_exp', 123, 123, 123, 123),
    TvmService('experiments3-proxy', 124, 124, 124, 124),
    TvmService('statistics', 125, 125, 125, 125),
]


@pytest.mark.pgsql('clownductor', ['init_test_data.sql'])
@pytest.mark.usefixtures('perforator_mockserver')
@pytest.mark.parametrize(
    'params_input',
    [
        (
            {
                'name': 'some-project',
                'abc_slug': 'some-prj-slug',
                'services': [
                    {
                        'name': 'some-service',
                        'abc_slug': 'some-slug',
                        'tvm': {'testing': 32323, 'production': 7567546},
                        'updated_at': 2133.5443,
                    },
                    {
                        'name': 'some-service-2',
                        'abc_slug': 'some-slug-2',
                        'tvm': {'testing': 3232, 'production': 672},
                        'updated_at': 21332.5443,
                    },
                ],
            }
        ),
    ],
)
async def test_services_sync_with_tvm(
        web_app_client,
        mock_task_processor,
        mock_perforator_context,
        params_input,
        web_context,
):
    for tvm_service in EXISTED_SERVICES:
        mock_perforator_context.add_service(
            tvm_service.name,
            tvm_service.production_id,
            tvm_service.testing_id,
            tvm_service.clown_id,
            tvm_service.project_id,
        )

    response = await web_app_client.post(
        '/v1/services/sync_with_tvm', json=params_input,
    )
    assert response.status == 200
    data = await response.json()

    input_services = {
        service['name']: service for service in params_input['services']
    }
    for service_name, service_id in data.items():
        service = await web_context.service_manager.services.get_by_id(
            service_id,
        )
        input_service = input_services[service_name]
        assert input_service['name'] == service['name']
        assert input_service['abc_slug'] == service['abc_service']
        tvm_service_added = False
        tvm_envs_added = False
        tvm_name = 'market_' + input_service['name']
        for service in mock_perforator_context.services:
            if service.tvm_name == tvm_name:
                tvm_service_added = True
                tvm_obj = {
                    env.env_type: env.tvm_id for env in service.environments
                }
                tvm_envs_added = input_service['tvm'] == tvm_obj
                break
        assert tvm_service_added
        assert tvm_envs_added
        tvm_rules = {
            TvmRule(
                rule.source.tvm_name, rule.destination.tvm_name, rule.env_type,
            )
            for rule in mock_perforator_context.rules
            if rule.source.tvm_name == tvm_name
        }
        rules_expected = [
            TvmRule(
                source=tvm_name, destination=destination, env_type=env_type,
            )
            for destination in market_constants.DEFAULT_DESTINATIONS
            for env_type in mock_perforator_context.POSSIBLE_ENVIRONMENTS
        ]
        assert set(tvm_rules) == set(rules_expected)

    project = await web_context.service_manager.projects.get_by_name(
        params_input['name'],
    )
    assert params_input['name'] == project['name']
    assert params_input['abc_slug'] == project['service_abc']
