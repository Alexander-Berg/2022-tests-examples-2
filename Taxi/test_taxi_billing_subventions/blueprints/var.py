import decimal
from typing import Any
from typing import Dict

from taxi import billing

from taxi_billing_subventions.common import models
from test_taxi_billing_subventions import helpers


def zero(attrs: dict) -> models.Var:
    return models.Var(billing.Money.zero('RUB'), attrs['reason'])


def with_value(attrs: dict) -> models.Var:
    if 'reason' in attrs:
        reason = attrs['reason']
        details: Dict[str, Any] = {}
    else:
        reason = attrs['details'].pop('reason')
        details = attrs['details']
    return models.Var(helpers.money(attrs['money']), reason, details)


def with_many_values(attrs: dict) -> models.Var:
    values = attrs['values']
    var = with_value(values[0])
    for a_value in values[1:]:
        var = var.set(helpers.money(a_value['money']), a_value['reason'])
    return var


def with_calculations(attrs: dict) -> models.Var:
    return models.Var(attrs['value'], attrs['calculations'])


def with_rebated_value(attrs: dict) -> models.Var:
    var = with_value(attrs)
    return var.set(billing.Money.zero(var.value.currency), 'set_from_rebate')


def with_ind_bel_nds_value(attrs: dict) -> models.Var:
    var = with_value(attrs)
    return var.set(
        billing.Money(decimal.Decimal('1.05'), var.value.currency),
        'set_from_ind_bel_nds_rate',
    )
