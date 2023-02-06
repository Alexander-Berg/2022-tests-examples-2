# pylint: disable=invalid-name

import pytest


class Context:
    def __init__(self, experiments3, taxi_config):
        self.experiments3 = experiments3
        self.taxi_config = taxi_config

        self.tracking_game_reward_params(max_amount='100')
        self.tracking_game_reward_enabled(enabled=True)

    def tracking_game_reward_params(self, max_amount):
        self.experiments3.add_config(
            name='grocery_tracking_game_reward_params',
            consumers=['grocery-cashback'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'max_amount': str(max_amount)},
                },
            ],
        )

    def tracking_game_reward_enabled(self, enabled):
        self.experiments3.add_config(
            name='grocery_tracking_game_reward_enabled',
            consumers=['grocery-cashback'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Disable for tristero',
                    'predicate': {
                        'type': 'eq',
                        'init': {
                            'arg_name': 'order_flow_version',
                            'arg_type': 'string',
                            'value': 'tristero_flow_v1',
                        },
                    },
                    'value': {'enabled': False},
                },
                {
                    'title': 'Other always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'enabled': enabled},
                },
            ],
        )


@pytest.fixture(name='grocery_cashback_configs', autouse=True)
def grocery_cashback_configs(experiments3, taxi_config):
    return Context(experiments3, taxi_config)
