import datetime as dt

import pytest

from taxi_billing_subventions.common.models.config import driver_mode


@pytest.mark.parametrize(
    'cfg, as_of, mode, expected_settings',
    [
        (
            {},
            dt.datetime(2019, 11, 26),
            'driver_fix',
            driver_mode.DEFAULT_SETTINGS,
        ),
        (
            {},
            dt.datetime(2019, 11, 26),
            '_unknown_mode',
            driver_mode.DEFAULT_SETTINGS,
        ),
        (
            {'driver_fix': []},
            dt.datetime(2019, 11, 26),
            'driver_fix',
            driver_mode.DEFAULT_SETTINGS,
        ),
        (
            {
                'driver_fix': [
                    {
                        'value': {
                            'additional_profile_tags': ['tag'],
                            'commission_enabled': False,
                            'promocode_compensation_enabled': True,
                        },
                        'start': '2019-11-26T00:00:00+00:00',
                    },
                ],
            },
            dt.datetime(2019, 11, 26, tzinfo=dt.timezone.utc),
            'driver_fix',
            driver_mode.DriverModeSettings(
                additional_profile_tags=frozenset(['tag']),
                commission_enabled=False,
                promocode_compensation_enabled=True,
            ),
        ),
        (
            {
                'driver_fix': [
                    {
                        'value': {
                            'additional_profile_tags': ['tag'],
                            'commission_enabled': True,
                            'promocode_compensation_enabled': False,
                        },
                        'start': '2019-11-26T00:00:00+00:00',
                    },
                ],
            },
            dt.datetime(2019, 11, 25, tzinfo=dt.timezone.utc),
            'driver_fix',
            driver_mode.DEFAULT_SETTINGS,
        ),
        (
            {
                'driver_fix': [
                    {
                        'value': {
                            'additional_profile_tags': ['tag2'],
                            'commission_enabled': False,
                            'promocode_compensation_enabled': False,
                        },
                        'start': '2019-11-27T00:00:00+00:00',
                    },
                    {
                        'value': {
                            'additional_profile_tags': ['tag'],
                            'commission_enabled': False,
                            'promocode_compensation_enabled': True,
                        },
                        'start': '2019-11-26T00:00:00+00:00',
                    },
                ],
            },
            dt.datetime(2019, 11, 26, tzinfo=dt.timezone.utc),
            'driver_fix',
            driver_mode.DriverModeSettings(
                additional_profile_tags=frozenset(['tag']),
                commission_enabled=False,
                promocode_compensation_enabled=True,
            ),
        ),
        (
            {
                'driver_fix': [
                    {
                        'value': {
                            'additional_profile_tags': ['tag2'],
                            'commission_enabled': False,
                            'promocode_compensation_enabled': False,
                        },
                        'start': '2019-11-27T00:00:00+00:00',
                    },
                    {
                        'value': {
                            'additional_profile_tags': ['tag'],
                            'commission_enabled': False,
                            'promocode_compensation_enabled': True,
                        },
                        'start': '2019-11-26T00:00:00+00:00',
                    },
                    {
                        'value': {
                            'additional_profile_tags': ['tag3'],
                            'commission_enabled': False,
                            'promocode_compensation_enabled': False,
                        },
                        'start': '2019-11-28T00:00:00+00:00',
                    },
                ],
            },
            dt.datetime(2019, 11, 27, tzinfo=dt.timezone.utc),
            'driver_fix',
            driver_mode.DriverModeSettings(
                additional_profile_tags=frozenset(['tag2']),
                commission_enabled=False,
                promocode_compensation_enabled=False,
            ),
        ),
    ],
)
def test_get_settings_as_of(cfg, as_of, mode, expected_settings):
    actual_settings = driver_mode.get_settings_as_of(cfg, mode, as_of)
    assert actual_settings == expected_settings


@pytest.mark.parametrize(
    'as_of, mode, msg',
    [
        (
            dt.datetime(2019, 11, 26, tzinfo=dt.timezone.utc),
            'orders',
            'No settings for mode "orders" on 2019-11-26 00:00:00+00:00.',
        ),
        (
            dt.datetime(2019, 11, 25, tzinfo=dt.timezone.utc),
            'driver_fix',
            'No settings for mode "driver_fix" on 2019-11-25 00:00:00+00:00.',
        ),
    ],
)
def test_get_settings_as_of_failure(as_of, mode, msg):
    cfg = {
        'driver_fix': [
            {
                'value': {
                    'additional_profile_tags': [],
                    'commission_enabled': True,
                    'promocode_compensation_enabled': True,
                },
                'start': '2019-11-26T00:00:00+00:00',
            },
        ],
    }
    with pytest.raises(RuntimeError) as excinfo:
        driver_mode.get_settings_as_of(cfg, mode, as_of, raise_exception=True)
    assert str(excinfo.value) == msg
