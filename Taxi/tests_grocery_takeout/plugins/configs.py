import pytest

from .. import models


class Context:
    def __init__(self, experiments3, taxi_config, mockserver):
        self.experiments3 = experiments3
        self.taxi_config = taxi_config
        self.mockserver = mockserver

        self.settings()
        self.entity_response_validator(is_valid=True)

    def settings(self, job_start_eta_hours=0):
        self.experiments3.add_config(
            name='grocery_takeout_settings',
            consumers=['grocery-takeout/stq'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            default_value=dict(job_start_eta_hours=job_start_eta_hours),
        )

    def entity_response_validator(self, is_valid: bool):
        self.experiments3.add_config(
            name='grocery_takeout_entity_response_validator',
            consumers=['grocery-takeout/entity-response-validator'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            default_value=dict(is_valid=is_valid),
        )

    def entity_graph(self, graph: models.EntityGraph):
        self.taxi_config.set(GROCERY_TAKEOUT_GRAPH=graph.serialize())


@pytest.fixture(name='grocery_takeout_configs', autouse=True)
def grocery_takeout_configs(experiments3, taxi_config, mockserver):
    return Context(experiments3, taxi_config, mockserver)
