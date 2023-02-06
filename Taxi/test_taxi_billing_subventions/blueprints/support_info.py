import datetime as dt
import decimal

from taxi_billing_subventions.common import models
from test_taxi_billing_subventions import helpers


def commission(attrs):
    default_base_rate = models.Var(
        helpers.money('0.1789473684210526315789473684 XXX'),
        'set_from_normal_rate_formula',
        {'formula_params': {'A': '20', 'B': '2000', 'C': '50'}},
    )
    base_rate = attrs.get('base_rate', default_base_rate)
    workshift = attrs.get('applied_driver_workshift', False)
    promocode = attrs.get('applied_driver_promocode', False)
    base_commission_var = models.Var(
        helpers.money('178.9473684210526315789473684 RUB'),
        'set_from_mul_cost_by_rate',
    )
    base_vat_var = models.Var(
        helpers.money('32.2105263157894736842105263 RUB'),
        'set_from_mul_by_vat_rate',
    )
    if workshift or promocode:
        if workshift:
            base_commission_var = base_commission_var.set(
                helpers.money('0 RUB'), 'set_from_driver_workshift',
            )
            base_vat_var = base_vat_var.set(
                helpers.money('0 RUB'), 'set_from_driver_workshift',
            )
            taximeter_reason = 'set_from_driver_workshift'
        elif promocode:
            base_commission_var = base_commission_var.set(
                helpers.money('0.8474576271186440677966101695 RUB'),
                'set_from_driver_promocode_commission',
            )
            base_vat_var = base_vat_var.set(
                helpers.money('0.1525423728813559322033898305 RUB'),
                'set_from_driver_promocode',
            )
            taximeter_reason = 'set_from_driver_promocode'
        taximeter = models.CommissionSupportInfo(
            contract_id='000000000000000000000001',
            rate_var=None,
            cost_var=None,
            initial_rate=None,
            discount_rate=None,
            applied_driver_workshift=workshift,
            applied_driver_promocode=promocode,
            commission_var=models.Var(
                helpers.money('0 RUB'), taximeter_reason,
            ),
            vat_var=models.Var(helpers.money('0 RUB'), taximeter_reason),
            vat_rate_var=models.Var(helpers.money('1 XXX'), taximeter_reason),
            applied_rebate=False,
        )

    else:
        taximeter = models.CommissionSupportInfo(
            contract_id='000000000000000000000001',
            rate_var=None,
            cost_var=None,
            initial_rate=None,
            discount_rate=None,
            applied_driver_workshift=workshift,
            applied_driver_promocode=False,
            commission_var=models.Var(
                helpers.money('1 RUB'), 'set_from_value',
            ),
            vat_var=models.Var(
                helpers.money('0.18 RUB'), 'set_from_mul_by_vat_rate',
            ),
            vat_rate_var=models.Var(
                helpers.money('1.18 XXX'), 'set_from_contract_rate',
            ),
            applied_rebate=False,
        )
    has_childseat = attrs.get('has_childseat', False)
    if has_childseat:
        childseat_rental = models.CommissionSupportInfo(
            contract_id='000000000000000000000001',
            rate_var=None,
            cost_var=None,
            initial_rate=None,
            discount_rate=None,
            applied_driver_workshift=False,
            applied_driver_promocode=False,
            commission_var=models.Var(
                helpers.money('76.27118644067796610169491525 RUB'),
                'set_from_mul_rental_cost_by_count',
                {'rental_cost': '90.0 RUB', 'count': 1},
            ),
            vat_var=models.Var(
                helpers.money('13.72881355932203389830508475 RUB'),
                'set_from_mul_by_vat_rate',
            ),
            vat_rate_var=models.Var(
                helpers.money('1.18 XXX'), 'set_from_contract_rate',
            ),
            applied_rebate=False,
        )
    else:
        childseat_rental = models.CommissionSupportInfo(
            contract_id='000000000000000000000001',
            rate_var=None,
            cost_var=None,
            initial_rate=None,
            discount_rate=None,
            applied_driver_workshift=False,
            applied_driver_promocode=False,
            commission_var=models.Var(
                helpers.money('0 RUB'), 'set_from_no_childseat',
            ),
            vat_var=models.Var(
                helpers.money('0 RUB'), 'set_from_no_childseat',
            ),
            vat_rate_var=models.Var(
                helpers.money('1 XXX'), 'set_from_no_childseat',
            ),
            applied_rebate=False,
        )

    return models.CompositeCommissionSupportInfo(
        search_params=models.commission.SearchParams(
            due=dt.datetime(2019, 2, 5, 16, 16, tzinfo=dt.timezone.utc),
            zone_name='moscow',
            tariff_class='econom',
            payment_type='cash',
            tags=frozenset(),
        ),
        by_agreement_kind={
            'base': models.CommissionSupportInfo(
                contract_id='000000000000000000000001',
                rate_var=base_rate,
                cost_var=models.Var(helpers.money('1000 RUB'), []),
                initial_rate=decimal.Decimal('0.1789473684210526315789473684'),
                discount_rate=decimal.Decimal('0'),
                applied_driver_workshift=workshift,
                applied_driver_promocode=promocode,
                commission_var=base_commission_var,
                vat_var=base_vat_var,
                vat_rate_var=models.Var(
                    helpers.money('1.18 XXX'), 'set_from_contract_rate',
                ),
                applied_rebate=False,
            ),
            'hiring': models.CommissionSupportInfo(
                contract_id='000000000000000000000001',
                rate_var=None,
                cost_var=None,
                initial_rate=None,
                discount_rate=None,
                applied_driver_workshift=False,
                applied_driver_promocode=False,
                commission_var=models.Var(
                    helpers.money('0 RUB'),
                    'set_from_not_hiring',
                    {'hiring_type': None, 'applied_by_age': False},
                ),
                vat_var=models.Var(
                    helpers.money('0 RUB'), 'set_from_not_hiring',
                ),
                vat_rate_var=models.Var(
                    helpers.money('1 XXX'), 'set_from_not_hiring',
                ),
                applied_rebate=False,
            ),
            'acquiring': models.CommissionSupportInfo(
                contract_id='000000000000000000000001',
                rate_var=None,
                cost_var=None,
                initial_rate=None,
                discount_rate=None,
                applied_driver_workshift=False,
                applied_driver_promocode=False,
                commission_var=models.Var(
                    helpers.money('0 RUB'),
                    'set_from_payment_type',
                    {'payment_type': 'cash'},
                ),
                vat_var=models.Var(
                    helpers.money('0 RUB'), 'set_from_payment_type',
                ),
                vat_rate_var=models.Var(
                    helpers.money('1 XXX'), 'set_from_payment_type',
                ),
                applied_rebate=False,
            ),
            'agent': models.CommissionSupportInfo(
                contract_id='000000000000000000000001',
                rate_var=None,
                cost_var=None,
                initial_rate=None,
                discount_rate=None,
                applied_driver_workshift=False,
                applied_driver_promocode=False,
                commission_var=models.Var(
                    helpers.money('0 RUB'),
                    'set_from_payment_type',
                    {'payment_type': 'cash'},
                ),
                vat_var=models.Var(
                    helpers.money('0 RUB'), 'set_from_payment_type',
                ),
                vat_rate_var=models.Var(
                    helpers.money('1 XXX'), 'set_from_payment_type',
                ),
                applied_rebate=False,
            ),
            'taximeter': taximeter,
            'childseat_rental': childseat_rental,
        },
    )
