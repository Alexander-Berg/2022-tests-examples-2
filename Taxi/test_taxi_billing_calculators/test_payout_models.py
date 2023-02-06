import decimal

import pytest

from taxi.billing import util

from taxi_billing_calculators.calculators.payout import models as payout_models


@pytest.mark.parametrize(
    'config',
    [
        [
            {
                'start': '2020-01-01T00:00:00+03:00',
                'settings': {
                    'no_min_value_firm_ids': [1, 2, 3],
                    'firm_settings': {
                        'firm_id': [4, 5, 6],
                        'min_reward': '0.01',
                    },
                    'region_settings': {
                        '236': {
                            'min_cashback_reward': '0.01',
                            'min_reward': '0',
                        },
                    },
                    'currency_settings': {'KZT': '12', 'AMD': '1'},
                    'default_min_reward': '0.01',
                    'add_vat': [4, 5, 6],
                    'rounding_rules': {'__default__': 4, 'RUB': 2},
                    'ignore_rules': {
                        'payment_kinds': [],
                        'transaction_types': [],
                    },
                },
            },
            {
                'start': '2019-01-01T00:00:00+03:00',
                'settings': {
                    'no_min_value_firm_ids': [119, 219, 319],
                    'firm_settings': {
                        'firm_id': [419, 519, 619],
                        'min_reward': '0.0119',
                    },
                    'region_settings': {
                        '236': {
                            'min_cashback_reward': '0.0119',
                            'min_reward': '019',
                        },
                    },
                    'currency_settings': {'KZT': '1219', 'AMD': '119'},
                    'default_min_reward': '0.0119',
                    'add_vat': [],
                    'rounding_rules': {'__default__': 4, 'RUB': 2},
                    'ignore_rules': {
                        'payment_kinds': [],
                        'transaction_types': [],
                    },
                },
            },
        ],
    ],
)
@pytest.mark.parametrize(
    'due,expected',
    [
        ('2018-01-01T00:00:00+03:00', None),
        (
            '2019-01-01T00:00:01+03:00',
            payout_models.AgentRewardSettings.from_config(
                {
                    'no_min_value_firm_ids': [119, 219, 319],
                    'firm_settings': {
                        'firm_id': [419, 519, 619],
                        'min_reward': '0.0119',
                    },
                    'region_settings': {
                        '236': {
                            'min_cashback_reward': '0.0119',
                            'min_reward': '019',
                        },
                    },
                    'currency_settings': {'KZT': '1219', 'AMD': '119'},
                    'default_min_reward': '0.0119',
                    'add_vat': [],
                    'rounding_rules': {'__default__': 4, 'RUB': 2},
                    'ignore_rules': {
                        'payment_kinds': [],
                        'transaction_types': [],
                    },
                },
            ),
        ),
        (
            '2020-01-01T00:00:01+03:00',
            payout_models.AgentRewardSettings.from_config(
                {
                    'no_min_value_firm_ids': [1, 2, 3],
                    'firm_settings': {
                        'firm_id': [4, 5, 6],
                        'min_reward': '0.01',
                    },
                    'region_settings': {
                        '236': {
                            'min_cashback_reward': '0.01',
                            'min_reward': '0',
                        },
                    },
                    'currency_settings': {'KZT': '12', 'AMD': '1'},
                    'default_min_reward': '0.01',
                    'add_vat': [4, 5, 6],
                    'rounding_rules': {'__default__': 4, 'RUB': 2},
                    'ignore_rules': {
                        'payment_kinds': [],
                        'transaction_types': [],
                    },
                },
            ),
        ),
    ],
)
def test_min_reward_config(config, due, expected):
    config = payout_models.AgentRewardConfig.from_config(config)
    assert config
    assert config.by_due(util.dates.parse_datetime(due)) == expected


@pytest.mark.parametrize(
    'settings, config, expected_min_reward',
    [
        (
            payout_models.AgentRewardSettings.from_config(
                {
                    'no_min_value_firm_ids': [1, 2, 3],
                    'firm_settings': {
                        'firm_id': [4, 5, 6],
                        'min_reward': '0.01',
                    },
                    'region_settings': {
                        '236': {
                            'min_cashback_reward': '0.01',
                            'min_reward': '0',
                        },
                    },
                    'currency_settings': {'KZT': '12', 'AMD': '1'},
                    'default_min_reward': '0.01',
                    'add_vat': [4, 5, 6],
                    'rounding_rules': {'__default__': 4, 'RUB': 2},
                    'ignore_rules': {
                        'payment_kinds': [],
                        'transaction_types': [],
                    },
                },
            ),
            {
                'contract_details': payout_models.ContractDetails(
                    firm_id=1,
                    region_id=12,
                    currency='AMD',
                    agent_percent=decimal.Decimal('0'),
                ),
                'is_cashback': False,
            },
            decimal.Decimal(0),
        ),
        (
            payout_models.AgentRewardSettings.from_config(
                {
                    'no_min_value_firm_ids': [1, 2, 3],
                    'firm_settings': {
                        'firm_id': [4, 5, 6],
                        'min_reward': '0.01',
                    },
                    'region_settings': {
                        '236': {
                            'min_cashback_reward': '0.01',
                            'min_reward': '0',
                        },
                    },
                    'currency_settings': {'KZT': '12', 'AMD': '1'},
                    'default_min_reward': '0.01',
                    'add_vat': [4, 5, 6],
                    'rounding_rules': {'__default__': 4, 'RUB': 2},
                    'ignore_rules': {
                        'payment_kinds': [],
                        'transaction_types': [],
                    },
                },
            ),
            {
                'contract_details': payout_models.ContractDetails(
                    firm_id=100500,
                    region_id=236,
                    currency='AMD',
                    agent_percent=decimal.Decimal('0.42'),
                ),
                'is_cashback': True,
            },
            decimal.Decimal('0.01'),
        ),
    ],
)
def test_reward_settings(settings, config, expected_min_reward):
    assert settings.get_min_reward(**config) == expected_min_reward
