import datetime
from unittest import mock

import pytest

from taxi_billing_subventions.common.models.config import migration

_NOW = datetime.datetime(2021, 10, 1, tzinfo=datetime.timezone.utc)


@pytest.mark.parametrize(
    'config, expected_mode',
    [
        (
            {
                'BILLING_FUNCTIONS_TAXI_ORDER_MIGRATION': {
                    'by_zone': {
                        '__default__': {
                            'enabled': [
                                {'since': '1999-06-18T07:15:00+00:00'},
                            ],
                        },
                    },
                },
            },
            migration.Mode.ENABLED,
        ),
        (
            {
                'BILLING_FUNCTIONS_TAXI_ORDER_MIGRATION': {
                    'by_zone': {'__default__': {}},
                },
            },
            migration.Mode.DISABLED,
        ),
        (
            {
                'BILLING_FUNCTIONS_TAXI_ORDER_MIGRATION': {
                    'by_zone': {
                        '__default__': {
                            'enabled': [
                                {'since': '1999-06-18T07:15:00+00:00'},
                            ],
                        },
                        'kursk': {
                            'disabled': [
                                {'since': '2021-09-29T00:00:00+00:00'},
                            ],
                        },
                    },
                },
            },
            migration.Mode.DISABLED,
        ),
        pytest.param(
            {
                'BILLING_FUNCTIONS_TAXI_ORDER_MIGRATION': {
                    'by_zone': {
                        '__default__': {
                            'enabled': [
                                {'since': '1999-06-18T07:15:00+00:00'},
                            ],
                        },
                        'kursk': {
                            'disabled': [
                                {
                                    'since': '2021-09-29T00:00:00+00:00',
                                    'till': '2021-09-30T00:00:00+00:00',
                                },
                            ],
                        },
                    },
                },
            },
            migration.Mode.ENABLED,
            id='enabled by default due to no match interval in zone config',
        ),
        pytest.param(
            {
                'BILLING_FUNCTIONS_TAXI_ORDER_MIGRATION': {
                    'by_zone': {
                        '__default__': {
                            'enabled': [
                                {
                                    'since': '2021-09-30T00:10:00+00:00',
                                    'till': '2021-10-02T00:10:00+00:00',
                                },
                            ],
                            'test': [
                                {
                                    'since': '2021-09-30T00:10:00+00:00',
                                    'till': '2021-10-02T00:10:00+00:00',
                                },
                            ],
                        },
                    },
                },
            },
            migration.Mode.TEST,
            id='`test` priority is higher than `enabled`',
        ),
        pytest.param(
            {
                'BILLING_FUNCTIONS_TAXI_ORDER_MIGRATION': {
                    'by_zone': {
                        '__default__': {
                            'test': [
                                {
                                    'since': '2021-09-30T00:10:00+00:00',
                                    'till': '2021-10-02T00:10:00+00:00',
                                },
                            ],
                            'disabled': [
                                {
                                    'since': '2021-09-30T00:10:00+00:00',
                                    'till': '2021-10-02T00:10:00+00:00',
                                },
                            ],
                        },
                    },
                },
            },
            migration.Mode.DISABLED,
            id='`disabled` priority is highest',
        ),
    ],
)
def test(config, expected_mode):
    migration_obj = migration.Migration(mock.Mock(**config))
    assert migration_obj.match_taxi_order('kursk', _NOW) == expected_mode
