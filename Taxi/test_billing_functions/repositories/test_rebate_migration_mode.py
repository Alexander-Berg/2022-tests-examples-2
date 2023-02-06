import datetime

import pytest

from billing_functions.repositories import migration_mode

_NOW = datetime.datetime(2021, 10, 1, tzinfo=datetime.timezone.utc)


@pytest.mark.parametrize(
    'expected_mode',
    [
        pytest.param(
            migration_mode.Mode.ENABLED,
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_REBATES_MIGRATION={
                    'by_zone': {
                        '__default__': {
                            'enabled': [
                                {'since': '1999-06-18T07:15:00+00:00'},
                            ],
                        },
                    },
                },
            ),
        ),
        pytest.param(
            migration_mode.Mode.DISABLED,
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_REBATES_MIGRATION={
                    'by_zone': {'__default__': {}},
                },
            ),
        ),
        pytest.param(
            migration_mode.Mode.DISABLED,
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_REBATES_MIGRATION={
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
            ),
        ),
        pytest.param(
            migration_mode.Mode.ENABLED,
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_REBATES_MIGRATION={
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
            ),
            id='service by default due to no match interval in zone config',
        ),
        pytest.param(
            migration_mode.Mode.TEST,
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_REBATES_MIGRATION={
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
            ),
            id='`test` priority is higher than `service`',
        ),
        pytest.param(
            migration_mode.Mode.DISABLED,
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_REBATES_MIGRATION={
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
            ),
            id='`order` priority is highest',
        ),
    ],
)
def test_match(expected_mode, *, stq3_context):
    migration = stq3_context.migration_mode
    actual_mode = migration.match_for_rebate('kursk', _NOW)
    assert actual_mode == expected_mode
