import decimal

from taxi_billing_subventions.common import models


def make_driver_fix_rule_data(attrs: dict) -> models.DriverFixRuleData:
    default_kwargs = {
        'profile_tariff_classes': ['econom'],
        'profile_payment_type_restrictions': models.ProfilePaymentTypeRule.ANY,
        'commission_rate_if_fraud': decimal.Decimal('0.1'),
        'pay_currency': 'RUB',
        'status': models.rule.Status.APPROVED,
        'budget': None,
        'rate_intervals': [
            models.DriverFixRateInterval(
                starts_at=models.DriverFixRateIntervalEndpoint(
                    iso_week_day=models.ISOWeekDay.mon, hour=0, minute=0,
                ),
                rate_per_minute=decimal.Decimal(1),
            ),
        ],
        'b2b_client_id': None,
        'geoarea': 'moscow_center',
    }
    default_kwargs.update(attrs)
    return models.DriverFixRuleData(**default_kwargs)  # type: ignore


def make_driver_fix_input_dict(attrs):
    default_kwargs = {
        'kind': 'driver_fix',
        'id': 'driver_fix_group_id_1',
        'zone': 'moscow',
        'profile_tariff_classes': ['econom', 'business'],
        'profile_payment_type_restrictions': 'online',
        'tag': 'driver_fix_cheap',
        'geoarea': 'moscow_center',
        'commission_rate_if_fraud': '0.2',
        'rates': [make_driver_fix_rate_input_dict({})],
        'budget': {'id': 'some_driver_fix_budget_id', 'weekly': '100500.0'},
        'begin_at': '2019-11-10',
        'end_at': '2019-12-10',
    }
    default_kwargs.update(attrs)
    return default_kwargs


def make_driver_fix_rate_input_dict(attrs):
    default_kwargs = {
        'week_day': 'mon',
        'start': '12:45',
        'rate_per_minute': '100500.0',
    }
    default_kwargs.update(attrs)
    return default_kwargs
