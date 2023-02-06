# pylint: disable=invalid-name

import pytest


class Context:
    def __init__(self, experiments3, taxi_config):
        self.experiments3 = experiments3
        self.taxi_config = taxi_config

    def set_mocked_status_response(self, response):
        self.experiments3.add_config(
            name='grocery_payments_tracking_status_mock',
            consumers=['grocery-payments-tracking'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'response': response},
                },
            ],
        )


@pytest.fixture(name='grocery_payments_tracking_configs', autouse=True)
def grocery_payments_tracking_configs(experiments3, taxi_config):
    return Context(experiments3, taxi_config)
