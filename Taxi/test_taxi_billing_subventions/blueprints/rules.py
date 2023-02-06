import datetime as dt
import decimal

import pytz

from taxi import billing

from taxi_billing_subventions.common import const
from taxi_billing_subventions.common import containers
from taxi_billing_subventions.common import intervals
from taxi_billing_subventions.common import models
from test_taxi_billing_subventions.blueprints import driver_fix_rule


def moscow_matcher(attrs: dict) -> models.rule.Matcher:
    default_kwargs = {
        'city_id': 'Москва',
        'zone_name': 'moscow',
        'geoareas': containers.Universe(),
        'tags': containers.Universe(),
        'tariff_classes': containers.Universe(),
        'payment_types': containers.Universe(),
        'branding_types': containers.Universe(),
        'original_start': dt.datetime(2018, 5, 9, 21, tzinfo=dt.timezone.utc),
        'start': dt.datetime(2018, 5, 9, 21, tzinfo=dt.timezone.utc),
        'end': dt.datetime(2018, 5, 11, 21, tzinfo=dt.timezone.utc),
        'active_week_days': const.ALL_WEEK_DAYS,
        'active_hours': const.ALL_DAY_HOURS,
        'activity_points': None,
        'tzinfo': pytz.timezone('Europe/Moscow'),
    }
    default_kwargs.update(attrs)
    return models.rule.Matcher(**default_kwargs)  # type: ignore


def geo_booking(attrs):
    identity = models.rule.Identity('geo_booking_id', 'some_group_id')
    geoarea = 'moscow'
    matcher = moscow_matcher({'geoareas': [geoarea]})
    workshift = models.GeoBookingWorkshift(0, 1)
    data = models.GeoBookingRuleData(
        rule_type=models.rule.PaymentType.GUARANTEE,
        agreement_ref=models.AgreementRef.from_str(
            'subvention_agreement/1/default/_id/geo_booking_id',
        ),
        has_commission=False,
        pay_currency='RUB',
        workshift=workshift,
        min_online_minutes=10,
        rate_on_order_per_minute=decimal.Decimal(5),
        rate_free_per_minute=decimal.Decimal(2),
        status=models.rule.Status.APPROVED,
        profile_payment_type_restrictions=models.ProfilePaymentTypeRule.CASH,
        budget=models.Budget(
            budget_id='geo_booking_budget_id', weekly=decimal.Decimal(12345),
        ),
        geoarea=geoarea,
    )
    default_kwargs = {'identity': identity, 'matcher': matcher, 'data': data}
    default_kwargs.update(attrs)
    return models.GeoBookingRule(**default_kwargs)


def single_order(attrs):
    default_kwargs = {
        'identity': models.rule.Identity(
            'extra_30_rubles_rule_id', 'fake_group_id',
        ),
        'idempotency_token': None,
        'matcher': moscow_matcher({}),
        'bonus_calculator': models.StepsBonusCalculator(
            steps=[
                models.BonusStep(
                    num_orders_interval=intervals.at_least(1),
                    bonus_calculator=models.ExtraBonusCalculator(
                        bonus_sum=_make_money('30 RUB'),
                        has_commission=True,
                        is_additive=False,
                    ),
                    id='extra_30_rubles_rule_id',
                    group_member_id=None,
                ),
            ],
        ),
        'agreement_ref': models.AgreementRef.from_str(
            'subvention_agreement/1/default/_id/extra_30_rubles_rule_id',
        ),
        'is_goal': False,
        'priority': 1000,
        'days_span': 1,
        'display_in_taximeter': True,
        'status': models.rule.Status.APPROVED,
        'budget': models.Budget(
            budget_id='single_order_budget_id', weekly=decimal.Decimal(54321),
        ),
    }
    default_kwargs.update(attrs)
    return models.SingleOrderRule(
        models.SingleOrderRule.Data(**default_kwargs),
    )


def single_order_guarantee(attrs):
    default_kwargs = {'bonus_calculator': _guarantee_steps_bonus_calculator()}
    default_kwargs.update(attrs)
    return single_order(default_kwargs)


def driver_fix(attrs: dict) -> models.DriverFixRule:
    default_identity = models.rule.Identity(
        'driver_fix_rule_id', 'driver_fix_rule_group_id',
    )
    identity: models.rule.Identity = attrs.get('identity', default_identity)
    agreement_ref = models.AgreementRef(
        version='1',
        scope=models.AgreementRef.DEFAULT_SCOPE,
        identity_kind=models.AgreementRef.ID_IDENTITY_KIND,
        identity_value=identity.id,
    )
    default_kwargs = {
        'identity': identity,
        'matcher': moscow_matcher({'geoareas': ['moscow_center']}),
        'data': driver_fix_rule.make_driver_fix_rule_data({}),
        'agreement_ref': agreement_ref,
    }
    default_kwargs.update(attrs)
    return models.DriverFixRule(**default_kwargs)  # type: ignore


def _guarantee_steps_bonus_calculator():
    return models.StepsBonusCalculator(
        steps=[
            models.BonusStep(
                num_orders_interval=intervals.at_least(1),
                bonus_calculator=models.GuaranteeBonusCalculator(
                    guarantee_sum=_make_money('30 RUB'),
                    has_commission=True,
                    is_additive=False,
                ),
                id='extra_30_rubles_rule_id',
                group_member_id=None,
            ),
        ],
    )


def _make_money(money_str) -> billing.Money:
    amount_str, currency = money_str.split()
    return billing.Money(decimal.Decimal(amount_str), currency)
