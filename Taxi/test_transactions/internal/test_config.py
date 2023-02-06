import datetime

import pytest

from transactions.internal import config as config_helper
from transactions.usecases import store_error


@pytest.mark.parametrize(
    'error_kind, error_scope, expected_period_kind',
    [
        ('unknown_error_kind', 'eda', store_error.PeriodKind.NONE),
        ('hanging_transaction', 'eda', store_error.PeriodKind.DAILY),
        ('unexpected_payment_not_found', 'eda', store_error.PeriodKind.DAILY),
        ('unexpected_payment_not_found', 'taxi', store_error.PeriodKind.NONE),
    ],
)
@pytest.mark.config(
    TRANSACTIONS_ERROR_AGGREGATION_PERIOD={
        '__default__': {'__default__': 'none'},
        'hanging_transaction': {'__default__': 'daily'},
        'unexpected_payment_not_found': {
            '__default__': 'none',
            'eda': 'daily',
        },
    },
)
def test_get_aggregation_period_kind(
        stq3_context, error_kind, error_scope, expected_period_kind,
):
    config = config_helper.Config(stq3_context)
    actual_period_kind = config.get_aggregation_period_kind(
        error_kind=error_kind, error_scope=error_scope,
    )
    assert actual_period_kind == expected_period_kind


@pytest.mark.config(TRANSACTIONS_ERROR_NOTIFICATION_DELAY=12345)
def test_get_error_notification_delay(stq3_context):
    config = config_helper.Config(stq3_context)
    actual_delay = config.get_error_notification_delay()
    assert actual_delay == datetime.timedelta(seconds=12345)


@pytest.mark.parametrize(
    'scope, expected_value', [('foobar', 420), ('taxi', 123)],
)
@pytest.mark.config(
    TRANSACTIONS_REFUND_ATTEMPTS_MINUTES_BY_SCOPE={
        '__default__': 420,
        'taxi': 123,
    },
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
def test_get_refund_attempts_minutes(stq3_context, scope, expected_value):
    config = config_helper.Config(stq3_context)
    actual_value = config.get_refund_attempts_minutes(scope=scope)
    assert actual_value == expected_value
