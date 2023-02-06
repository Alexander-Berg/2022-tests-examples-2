import decimal
import time

import pytest

from taxi import billing

from taxi_billing_subventions import config
from taxi_billing_subventions.common import config_helper
from taxi_billing_subventions.common import models

_CONFIG_VALUE = {'USD': 100, '__default__': 2000}


@pytest.mark.parametrize(
    'value, currency, expected_max_discount',
    [
        (_CONFIG_VALUE, 'USD', billing.Money(decimal.Decimal(100), 'USD')),
        (_CONFIG_VALUE, 'RUB', billing.Money(decimal.Decimal(2000), 'RUB')),
    ],
)
@pytest.mark.nofilldb()
def test_get_max_discount(value, currency, expected_max_discount):
    actual_max_discount = config_helper.get_max_discount(value, currency)
    assert expected_max_discount == actual_max_discount


# pylint: disable=invalid-name
@pytest.mark.nofilldb()
def test_get_antifraud_config_at_returns_default_values(unittest_settings):
    conf: config.Config = config.Config(settings=unittest_settings)
    actual = config_helper.get_antifraud_config_at(conf, 0)
    expected = models.doc.AntifraudConfig(0, 0)
    assert actual == expected


# pylint: disable=invalid-name
@pytest.mark.nofilldb()
def test_get_antifraud_config_at_respects_history(unittest_settings):
    conf: config.Config = config.Config(settings=unittest_settings)

    setattr(
        conf,
        'SUBVENTION_MIN_RIDE',
        [
            {'start': 0, 'seconds': 1},
            {'start': 1, 'seconds': 2},
            {'start': 2, 'seconds': 3},
        ],
    )
    setattr(
        conf,
        'SUBVENTION_MIN_DISTANCE',
        [
            {'start': 1, 'meters': 20},
            {'start': 2, 'meters': 30},
            {'start': 3, 'meters': 40},
        ],
    )

    actual = config_helper.get_antifraud_config_at(conf, 1)
    expected = models.doc.AntifraudConfig(2, 20)
    assert actual == expected

    actual = config_helper.get_antifraud_config_at(conf, 5)
    expected = models.doc.AntifraudConfig(3, 40)
    assert actual == expected


# pylint: disable=invalid-name
@pytest.mark.nofilldb()
def test_get_antifraud_config_now_ticks(unittest_settings):
    current_unix_time = int(time.time())
    conf: config.Config = config.Config(settings=unittest_settings)

    setattr(
        conf,
        'SUBVENTION_MIN_RIDE',
        [
            # Config was updated in the past
            {'start': current_unix_time - 1, 'seconds': 1},
        ],
    )
    setattr(
        conf,
        'SUBVENTION_MIN_DISTANCE',
        [
            # Config will be updated in the future (in 1h)
            {'start': current_unix_time + 60 * 60, 'meters': 20},
        ],
    )

    actual = config_helper.get_antifraud_config_now(conf)
    expected = models.doc.AntifraudConfig(1, 0)
    assert actual == expected
