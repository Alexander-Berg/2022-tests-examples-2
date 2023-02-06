import datetime

import pytest

from taxi.conf import settings
from taxi.internal import commission_manager
from taxi.internal import dbh
from taxi.internal import park_manager
from taxi.internal.order_kit import payment_helpers
from taxi.util import decimal
from taxi.util import math_numbers

_NORMAL = commission_manager.NORMAL_BILLING_TYPE
_EXPIRED = commission_manager.EXPIRED_BILLING_TYPE
_CANCEL = commission_manager.CANCEL_BILLING_TYPE


_DEFAULT_CONTRACT_KWARGS = dict(
    id='some_id',
    type='fixed_percent',
    payment_type='cash',
    has_commission=True,
    min_order_cost=1990000,
    max_order_cost=60000000,
    expired_cost=8000000,
    percent=1100,
    cancel_percent=1100,
    expired_percent=1100,
    vat=11800,
    branding_discounts=[],
    marketing_level=[],
    corp_vat=11800,
    has_fixed_cancel_percent=True,
    has_acquiring_percent=True,
    acquiring_percent=0,
    agent_percent=0,
    data={}
)

_BRANDING_DISCOUNTS = [
    {'marketing_level': ['co_branding', 'sticker', 'lightbox'], 'value': 650},
    {'marketing_level': ['co_branding', 'sticker'], 'value': 300},
    {'marketing_level': ['co_branding', 'lightbox'], 'value': 300},
    {'marketing_level': ['sticker', 'lightbox'], 'value': 600},
    {'marketing_level': ['sticker'], 'value': 275},
    {'marketing_level': ['lightbox'], 'value': 250},
    # just franchise
    {'marketing_level': ['franchise'], 'value': 700},
    # lightbox + franchise
    {'marketing_level': ['lightbox', 'franchise'], 'value': 900},
    # discount over 11% (contract percent)
    {'marketing_level': ['sticker', 'franchise'], 'value': 1800},
    # negative discount case
    {'marketing_level': ['co_branding'], 'value': -1000},
]


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('billing_type, type,payment_type,min_order_cost,'
                         'max_order_cost,expired_cost, percent,'
                         'cancel_percent,'
                         'expired_percent,marketing_level,'
                         'branding_discounts,'
                         'acquiring_percent,'
                         'agent_percent,cost,data,'
                         'expected_commission_value,expected_str', [
    # cash, cost * percent
    (_NORMAL, 'fixed_percent', 'cash', 1990000, 60000000, 8000000,
     1100, 1100, 1100, [], [], 200, 1,
     400, {}, '44',
     '11.00%'),
    # cash, cost * percent
    (_NORMAL, 'fixed_percent', 'cash', 1990000, 60000000, 8000000,
     1100, 1100, 1100, [], [], 200, 1,
     199, {}, '21.89',
     '11.00%'),
    # cash, cost * percent
    (_NORMAL, 'fixed_percent', 'cash', 1990000, 60000000, 8000000,
     1100, 1100, 1100, [], [], 200, 1,
     6000, {}, '660',
     '11.00%'),
    # cash, 0 < 199, min_cost * percent
    (_NORMAL, 'fixed_percent', 'cash', 1990000, 60000000, 8000000,
     1100, 1100, 1100, [], [], 200, 1,
     0, {}, '21.89',
     '11.00%'),
    # cash, 7000 > 6000, min_cost * percent
    (_NORMAL, 'fixed_percent', 'cash', 1990000, 60000000, 8000000,
     1100, 1100, 1100, [], [], 200, 1,
     7000, {}, '660',
     '11.00%'),
    # card, cost * percent
    (_NORMAL, 'fixed_percent', 'card', 1990000, 60000000, 8000000,
     899, 1100, 1100, [], [], 200, 1,
     400, {}, '35.96',
     '8.99% + 2.00% + 0.01%'),
    # card, cost * percent
    (_NORMAL, 'fixed_percent', 'card', 1990000, 60000000, 8000000,
     899, 1100, 1100, [], [], 200, 1,
     199, {}, '17.8901',
     '8.99% + 2.00% + 0.01%'),
    # card, cost * percent
    (_NORMAL, 'fixed_percent', 'card', 1990000, 60000000, 8000000,
     899, 1100, 1100, [], [], 200, 1,
     6000, {}, '539.4',
     '8.99% + 2.00% + 0.01%'),
    # card, 0 < 199, min_cost * percent
    (_NORMAL, 'fixed_percent', 'card', 1990000, 60000000, 8000000,
     899, 1100, 1100, [], [], 200, 1,
     0, {}, '17.8901',
     '8.99% + 2.00% + 0.01%'),
    # card, 7000 > 6000, min_cost * percent
    (_NORMAL, 'fixed_percent', 'card', 1990000, 60000000, 8000000,
     899, 1100, 1100, [], [], 200, 1,
     7000, {}, '539.4',
     '8.99% + 2.00% + 0.01%'),
    # cash, marketing discount, cost * (percent - discount)
    (_NORMAL, 'fixed_percent', 'cash', 1990000, 60000000, 8000000,
     1100, 1100, 1100, ['lightbox'], _BRANDING_DISCOUNTS, 200, 1,
     4000, {}, '340',
     '11.00%'),
    # cash, just franchise marketing discount, cost * (percent - discount)
    (_NORMAL, 'fixed_percent', 'cash', 1990000, 60000000, 8000000,
     1100, 1100, 1100, ['franchise'], _BRANDING_DISCOUNTS, 200, 1,
     4000, {}, '160',
     '11.00%'),
    # cash, more marketing discount with franchise, cost * (percent - discount)
    (_NORMAL, 'fixed_percent', 'cash', 1990000, 60000000, 8000000,
     1100, 1100, 1100, ['lightbox', 'franchise'],
     _BRANDING_DISCOUNTS, 200, 1,
     4000, {}, '80',
     '11.00%'),
    # cash, marketing discount without franchise, cost * (percent - discount)
    (_NORMAL, 'fixed_percent', 'cash', 1990000, 60000000, 8000000,
     1100, 1100, 1100, ['sticker', 'co_branding', 'franchise'],
     _BRANDING_DISCOUNTS, 200, 1,
     4000, {}, '0',
     '11.00%'),
    # cash, big marketing discount with franchise, cost * (percent - discount)
    (_NORMAL, 'fixed_percent', 'cash', 1990000, 60000000, 8000000,
     1100, 1100, 1100, ['sticker', 'franchise'],
     _BRANDING_DISCOUNTS, 200, 1,
     4000, {}, '0',
     '11.00%'),
    # cash, negative discount (more commission), cost * (percent + discount)
    (_NORMAL, 'fixed_percent', 'cash', 1990000, 60000000, 8000000,
     1100, 1100, 1100, ['co_branding'],
     _BRANDING_DISCOUNTS, 200, 1,
     4000, {}, '440',
     '11.00%'),
    # cash, marketing discount is greater than percent, commission is 0
    (_NORMAL, 'fixed_percent', 'cash', 1990000, 60000000, 8000000,
     200, 1100, 1100, ['lightbox'], _BRANDING_DISCOUNTS, 200, 1,
     4000, {}, '0',
     '2.00%'),
    # cash, fixed_percent, cancel 11% * cost
    (_CANCEL, 'fixed_percent', 'cash', 1990000, 60000000, 8000000,
     1100, 1100, 1100, [], _BRANDING_DISCOUNTS, 200, 1,
     4000, {}, '440',
     '11.00%'),
    # cash, fixed_percent, expired 11% * cost
    (_EXPIRED, 'fixed_percent', 'cash', 1990000, 60000000, 8000000,
     1100, 1100, 1100, [], _BRANDING_DISCOUNTS, 200, 1,
     4000, {}, '440',
     '11.00%'),
    # cash, fixed_percent, marketing discount, cancel 8% * cost
    (_CANCEL, 'fixed_percent', 'cash', 1990000, 60000000, 8000000,
     1100, 1100, 1100, ['lightbox'], _BRANDING_DISCOUNTS, 200, 1,
     4000, {}, '340',
     '11.00%'),
    # cash, fixed_percent, expired, marketing discount 8% * cost
    (_EXPIRED, 'fixed_percent', 'cash', 1990000, 60000000, 8000000,
     1100, 1100, 1100, ['lightbox'], _BRANDING_DISCOUNTS, 200, 1,
     4000, {}, '340',
     '11.00%'),
    # card, fixed_percent, cancel 11% * cost
    (_CANCEL, 'fixed_percent', 'card', 1990000, 60000000, 8000000,
     699, 1100, 1200, [], _BRANDING_DISCOUNTS, 200, 1,
     4000, {}, '440',
     '6.99% + 2.00% + 0.01%'),
    # card, fixed_percent, expired 12% * cost
    (_EXPIRED, 'fixed_percent', 'card', 1990000, 60000000, 8000000,
     699, 1100, 1200, [], _BRANDING_DISCOUNTS, 200, 1,
     4000, {}, '480',
     '6.99% + 2.00% + 0.01%'),
    # card, fixed_percent, marketing discount, cancel 8% * cost
    (_CANCEL, 'fixed_percent', 'card', 1990000, 60000000, 8000000,
     699, 1100, 1200, ['lightbox'], _BRANDING_DISCOUNTS, 200, 1,
     4000, {}, '340',
     '6.99% + 2.00% + 0.01%'),
    # card, fixed_percent, expired, marketing discount 9% * cost
    (_EXPIRED, 'fixed_percent', 'card', 1990000, 60000000, 8000000,
     699, 1100, 1200, ['lightbox'], _BRANDING_DISCOUNTS, 200, 1,
     4000, {}, '380',
     '6.99% + 2.00% + 0.01%'),
    # cash, asymptotic formula
    (_NORMAL, 'asymptotic_formula', 'cash', 1990000, 60000000, 8000000,
     900, 900, 900, [], _BRANDING_DISCOUNTS, 200, 1,
     300, {
         'cost_norm': 221000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '33.24491183879093199',
     '20.53 - 2625.7 / (cost - 22.1) %'),
    # cash, asymptotic formula, moscow conditions (as of 2016-april-21)
    (_NORMAL, 'asymptotic_formula', 'cash', 0, 60000000, 8000000,
     1100, 1100, 1100, [], _BRANDING_DISCOUNTS, 200, 1,
     300, {
         'cost_norm': -955824, 'numerator': 34392000, 'asymp': 177000,
         'max_commission_percent': 1770
     },
     '27.01794983801099341',
     '17.7 - 3439.2 / (cost + 95.5824) %'),
    # cash, asymptotic formula, moscow conditions (as of 2016-april-21)
    # cost 99, formula still works, (because zero of hudaverdan's asymptotic
    # function is not 99, it's ~ 98.72...)
    (_NORMAL, 'asymptotic_formula', 'cash', 0, 60000000, 8000000,
     1100, 1100, 1100, [], _BRANDING_DISCOUNTS, 200, 1,
     99, {
         'cost_norm': -955824, 'numerator': 34392000, 'asymp': 177000,
         'max_commission_percent': 1770
     },
     '0.02497345700330554048',
     '17.7 - 3439.2 / (cost + 95.5824) %'),
    # cash, asymptotic formula, moscow conditions (as of 2016-april-21)
    # cost less than zero of the function, commission is 0.
    (_NORMAL, 'asymptotic_formula', 'cash', 0, 60000000, 8000000,
     1100, 1100, 1100, [], _BRANDING_DISCOUNTS, 200, 1,
     decimal.Decimal('98.6'), {
         'cost_norm': -955824, 'numerator': 34392000, 'asymp': 177000,
         'max_commission_percent': 1770
     },
     '0',
     '17.7 - 3439.2 / (cost + 95.5824) %'),
    # cash, asymptotic formula, moscow conditions (as of 2016-april-21)
    # cost > 6000, we're getting commission from 6000.
    (_NORMAL, 'asymptotic_formula', 'cash', 0, 60000000, 8000000,
     1100, 1100, 1100, [], _BRANDING_DISCOUNTS, 200, 1,
     6100, {
         'cost_norm': -955824, 'numerator': 34392000, 'asymp': 177000,
         'max_commission_percent': 1770
     },
     '1028.147287255111177',
     '17.7 - 3439.2 / (cost + 95.5824) %'),
    # corp, asymptotic formula, moscow conditions (as of 2016-april-21)
    # same as cash
    (_NORMAL, 'asymptotic_formula', 'corp', 0, 60000000, 8000000,
     1100, 1100, 1100, [], _BRANDING_DISCOUNTS, 200, 1,
     100, {
         'cost_norm': -955824, 'numerator': 34392000, 'asymp': 177000,
         'max_commission_percent': 1770
     },
     '0.1155956773206587096',
     '17.7 - 3439.2 / (cost + 95.5824) %'),
    # corp, asymptotic formula, moscow conditions (as of 2016-april-21)
    # as usual
    (_NORMAL, 'asymptotic_formula', 'corp', 0, 60000000, 8000000,
     1100, 1100, 1100, [], _BRANDING_DISCOUNTS, 200, 1,
     6100, {
         'cost_norm': -955824, 'numerator': 34392000, 'asymp': 177000,
         'max_commission_percent': 1770
     },
     '1028.147287255111177',
     '17.7 - 3439.2 / (cost + 95.5824) %'),
    # cash, asymptotic formula, marketing discount
    (_NORMAL, 'asymptotic_formula', 'cash', 1990000, 60000000, 8000000,
     900, 900, 900, ['lightbox'], _BRANDING_DISCOUNTS, 200, 1,
     300, {
         'cost_norm': 221000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '25.74491183879093199',
     '20.53 - 2625.7 / (cost - 22.1) %'),
    # cash, asymptotic formula - max_commission_percent cutoff
    (_NORMAL, 'asymptotic_formula', 'cash', 1990000, 60000000, 8000000,
     900, 900, 900, [], _BRANDING_DISCOUNTS, 200, 1,
     10000, {
         'cost_norm': 221000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '1200',
     '20.53 - 2625.7 / (cost - 22.1) %'),
    # card, asymptotic formula - max_commission_percent cutoff
    (_NORMAL, 'asymptotic_formula', 'card', 1990000, 60000000, 8000000,
     900, 900, 900, [], _BRANDING_DISCOUNTS, 200, 1,
     10000, {
         'cost_norm': 221000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '1079.4',
     '20.53 - 2625.7 / (cost - 22.1) - 2.00% - 0.01%'),
    # card, asymptotic formula - minus acquiring and agent
    (_NORMAL, 'asymptotic_formula', 'card', 1990000, 60000000, 8000000,
     900, 900, 900, [], _BRANDING_DISCOUNTS, 200, 1,
     300, {
         'cost_norm': 221000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '27.21491183879093199',
     '20.53 - 2625.7 / (cost - 22.1) - 2.00% - 0.01%'),
    # card, asymptotic formula, marketing discount
    (_NORMAL, 'asymptotic_formula', 'card', 1990000, 60000000, 8000000,
     900, 900, 900, ['lightbox'], _BRANDING_DISCOUNTS, 200, 1,
     300, {
         'cost_norm': 221000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '19.71491183879093199',
     '20.53 - 2625.7 / (cost - 22.1) - 2.00% - 0.01%'),
    # card, asymptotic formula, marketing discount - too small -
    # zero commission
    (_NORMAL, 'asymptotic_formula', 'card', 1990000, 60000000, 8000000,
     900, 900, 900, ['sticker', 'lightbox'], _BRANDING_DISCOUNTS, 200, 1,
     191, {
         'cost_norm': 221000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '0',
     '20.53 - 2625.7 / (cost - 22.1) - 2.00% - 0.01%'),
    # cash, asymptotic formula - order cost is too small - zero commission
    (_NORMAL, 'asymptotic_formula', 'cash', 1990000, 60000000, 8000000,
     900, 900, 900, [], _BRANDING_DISCOUNTS, 200, 1,
     149, {
         'cost_norm': 221000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '0',
     '20.53 - 2625.7 / (cost - 22.1) %'),
    # cash, asymptotic formula - really small commission
    (_NORMAL, 'asymptotic_formula', 'cash', 1990000, 60000000, 8000000,
     900, 900, 900, [], _BRANDING_DISCOUNTS, 200, 1,
     150, {
         'cost_norm': 221000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '0.001020328381548084441',
     '20.53 - 2625.7 / (cost - 22.1) %'),
    # cash, asymptotic formula - order cost equal to cost_norm -
    # zero commission
    (_NORMAL, 'asymptotic_formula', 'cash', 1990000, 60000000, 8000000,
     900, 900, 900, [], _BRANDING_DISCOUNTS, 200, 1,
     22, {
         'cost_norm': 220000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '0',
     '20.53 - 2625.7 / (cost - 22) %'),
    # cash, asymptotic formula, cancel - 9% * cost
    (_CANCEL, 'asymptotic_formula', 'cash', 1990000, 60000000, 8000000,
     900, 900, 900, [], _BRANDING_DISCOUNTS, 200, 1,
     22, {
         'cost_norm': 220000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '1.98',
     '20.53 - 2625.7 / (cost - 22) %'),
    # cash, asymptotic formula, marketing discount cancel - 6% * cost
    (_CANCEL, 'asymptotic_formula', 'cash', 1990000, 60000000, 8000000,
     900, 900, 900, ['lightbox'], _BRANDING_DISCOUNTS, 200, 1,
     22, {
         'cost_norm': 220000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '1.430',
     '20.53 - 2625.7 / (cost - 22) %'),
    # card, asymptotic formula, cancel - 9% * cost
    (_CANCEL, 'asymptotic_formula', 'card', 1990000, 60000000, 8000000,
     900, 900, 900, [], _BRANDING_DISCOUNTS, 200, 1,
     22, {
         'cost_norm': 220000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '1.98',
     '20.53 - 2625.7 / (cost - 22) - 2.00% - 0.01%'),
    # card, asymptotic formula, marketing discount cancel - 6% * cost
    (_CANCEL, 'asymptotic_formula', 'card', 1990000, 60000000, 8000000,
     900, 900, 900, ['lightbox'], _BRANDING_DISCOUNTS, 200, 1,
     22, {
         'cost_norm': 220000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '1.430',
     '20.53 - 2625.7 / (cost - 22) - 2.00% - 0.01%'),
    # cash, asymptotic formula, expired - 9% * cost
    (_EXPIRED, 'asymptotic_formula', 'cash', 1990000, 60000000, 8000000,
     900, 900, 900, [], _BRANDING_DISCOUNTS, 200, 1,
     22, {
         'cost_norm': 220000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '1.98',
     '20.53 - 2625.7 / (cost - 22) %'),
    # cash, asymptotic formula, marketing discount expired - 6% * cost
    (_EXPIRED, 'asymptotic_formula', 'cash', 1990000, 60000000, 8000000,
     900, 900, 900, ['lightbox'], _BRANDING_DISCOUNTS, 200, 1,
     22, {
         'cost_norm': 220000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '1.430',
     '20.53 - 2625.7 / (cost - 22) %'),
    # card, asymptotic formula, expired - 9% * cost
    (_EXPIRED, 'asymptotic_formula', 'card', 1990000, 60000000, 8000000,
     900, 900, 900, [], _BRANDING_DISCOUNTS, 200, 1,
     22, {
         'cost_norm': 220000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '1.98',
     '20.53 - 2625.7 / (cost - 22) - 2.00% - 0.01%'),
    # card, asymptotic formula, marketing discount expired - 6% * cost
    (_EXPIRED, 'asymptotic_formula', 'card', 1990000, 60000000, 8000000,
     900, 900, 900, ['lightbox'], _BRANDING_DISCOUNTS, 200, 1,
     22, {
         'cost_norm': 220000, 'numerator': 26257000, 'asymp': 205300,
         'max_commission_percent': 2000
     },
     '1.430',
     '20.53 - 2625.7 / (cost - 22) - 2.00% - 0.01%'),
])
def test_get_commission_value(
        billing_type, type, payment_type, min_order_cost, max_order_cost,
        expired_cost, percent, cancel_percent, expired_percent,
        marketing_level, branding_discounts,
        acquiring_percent,
        agent_percent, cost, data, expected_commission_value, expected_str):
    vat_inner = 11800
    vat_decimal = payment_helpers.inner_to_decimal(vat_inner)
    contract = _make_contract(
        type=type,
        payment_type=payment_type,
        has_commission=True,
        min_order_cost=min_order_cost,
        max_order_cost=max_order_cost,
        expired_cost=expired_cost,
        percent=percent,
        expired_percent=expired_percent,
        cancel_percent=cancel_percent,
        vat=vat_inner,
        acquiring_percent=acquiring_percent,
        agent_percent=agent_percent,
        branding_discounts=branding_discounts,
        marketing_level=marketing_level,
        corp_vat=11800,
        data=data,
    )
    decimal_value = decimal.Decimal(expected_commission_value)
    actual_value = contract.get_commission_value(
        commission_manager.make_simple_cost_info(cost), billing_type,
    )
    assert actual_value == decimal_value
    assert str(contract) == expected_str
    commission_data = contract.get_commission_data(
        commission_manager.make_simple_cost_info(cost),
        billing_type,
    )
    assert commission_data.commission == decimal_value
    with decimal.localcontext() as ctx:
        ctx.prec = settings.COMMISSION_PRECISION
        assert commission_data.commission_with_vat == decimal_value * vat_decimal


@pytest.mark.filldb(
    commission_contracts='for_get_commission_contracts_test',
    parks='for_get_commission_contracts_test'
)
@pytest.mark.parametrize(
    'payment_type,time,zone,tariff_class,city,tag,expected_percent', [
        # fallback contract without conditions
        (None, datetime.datetime(2016, 3, 8), None, None, None, None, '0.00'),
        # we always prefer more specific contract
        ('cash', datetime.datetime(2016, 3, 8), None, None, None, None, '0.01'),
        # we always prefer more specific contract
        ('card', datetime.datetime(2016, 3, 8), None, None, None, None, '0.02'),
        # we always prefer more specific contract
        ('card', datetime.datetime(2016, 3, 8), None, None, 'moscow', None, '0.03'),
        # search by tariff_class works
        (
            'card', datetime.datetime(2016, 3, 8), None,
            'uberx', 'moscow', None, '0.66',
        ),
        # when there's no most specific contract, we return None
        ('corp', datetime.datetime(2016, 3, 8), None, None, None, None, None),
        # no contract in 2018
        (None, datetime.datetime(2018, 3, 8), None, None, None, None, None),
        # Tag and non-tag rules are in conflict, pick one without tag
        (
            'card', datetime.datetime(2016, 3, 8), 'zone_1',
            'uberx', None, 'coms_reposition_district_low', '0.05',
        ),
        # Rule with tag is more specific, still pick one without tag
        # because tag is not specified
        (
            'card', datetime.datetime(2016, 3, 8), 'zone_2',
            'uberx', None, None, '0.05',
        ),
        # Default rule should be picked because
        # tag is not specified
        (
            'card', datetime.datetime(2016, 3, 8), 'zone_3',
            'uberx', None, None, '0.02',
        ),
        # Pick tag rule because tag is specified
        (
            'card', datetime.datetime(2016, 3, 8), 'zone_3',
            'uberx', None, 'tag_1', '0.07',
        ),
    ]
)
@pytest.inline_callbacks
def test_get_commission_contract(payment_type, time, zone, tariff_class, city,
                                 tag, expected_percent):
    conditions = commission_manager.Conditions(
        payment_type=payment_type,
        zone=zone,
        tariff_class=tariff_class,
        city=city,
        tag=tag,
    )
    doc = yield commission_manager.get_commission_contract(
        time=time,
        conditions=conditions,
        park_id='some_park_id',
    )
    if expected_percent is None:
        assert doc is None
    else:
        assert doc.percent == decimal.Decimal(expected_percent)


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('vat,cost,expected_commission', [
    (11800, 300, '38.94'),
    (10000, 300, '33'),
])
def test_get_commission_value_using_vat_info(vat, cost,
                                             expected_commission):
    contract = _make_contract(
        **dict(_DEFAULT_CONTRACT_KWARGS, vat=vat)
    )
    actual_commission = contract.get_commission_value_using_vat_info(
        commission_manager.make_simple_cost_info(cost),
        commission_manager.NORMAL_BILLING_TYPE,
    )
    assert actual_commission == decimal.Decimal(expected_commission)


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'has_commission,cost,expected_cost_for_commission_calc', [
    # commission inside of [199, 6000] same cost
    (True, 200, '200'),
    # no commission: same cost
    (False, 200, '200'),
    # no commission: always same cost, even if less than 199
    (False, 0, '0'),
    # no commission: always same cost, even if greater than 6000
    (False, 9000, '9000'),
    # commission less than 199: 199
    (True, 0, '199'),
    # commission greater than 6000: 6000
    (True, 9000, '6000'),
])
def test_has_no_commission(
    has_commission, cost, expected_cost_for_commission_calc):
    contract = _make_contract(
        **dict(_DEFAULT_CONTRACT_KWARGS, has_commission=has_commission)
    )
    actual_cost = contract.get_cost_for_commission_calc(
        cost, commission_manager.NORMAL_BILLING_TYPE
    )
    assert actual_cost == decimal.Decimal(expected_cost_for_commission_calc)


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'corp_vat,cost,expected_commission,expected_commission_with_vat,'
    'billing_type', [
    # nds
    (11800, 300, '33', '38.94', _NORMAL),
    # no nds
    (10000, 300, '33', '38.94', _NORMAL),
    # weird nds
    (12000, 300, '33', '38.94', _NORMAL),
    # < 234.82 (199 * 1.18) , becomes 234.82
    (11800, 199, '25.8302', '30.479636', _NORMAL),
    # > 7080 (6000 * 1.18), becomes 7080
    (11800, 8000, '778.8', '918.984', _NORMAL),
    # cancel
    (11800, 200, '22', '25.96', _CANCEL),
    # cancel < 199, becomes 199
    (11800, 100, '21.89', '25.8302', _CANCEL),
    # cancel > 6000, becomes 6000
    (11800, 7000, '660', '778.8', _CANCEL),
    # expired
    (11800, 200, '22', '25.96', _EXPIRED),
    # expired < 199, becomes 199
    (11800, 100, '21.89', '25.8302', _EXPIRED),
    # expired > 6000, becomes 6000
    (11800, 7000, '660', '778.8', _EXPIRED),
])
def test_get_commission_value_corp(
    corp_vat, cost, expected_commission, expected_commission_with_vat,
    billing_type):
    corp_vat = decimal.Decimal(corp_vat)
    expected_commission = decimal.Decimal(expected_commission)
    expected_commission_with_vat = decimal.Decimal(
        expected_commission_with_vat
    )
    contract = _make_contract(
        **dict(
            _DEFAULT_CONTRACT_KWARGS,
            corp_vat=corp_vat,
            payment_type='corp',
       )
    )
    actual_commission = contract.get_commission_value(
        commission_manager.make_simple_cost_info(cost), billing_type)
    assert actual_commission == decimal.Decimal(expected_commission)
    actual_commission_with_vat = contract.get_commission_value_using_vat_info(
        commission_manager.make_simple_cost_info(cost),
        billing_type
    )
    assert actual_commission_with_vat == expected_commission_with_vat


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('performer_brandings,expected_commission', [
    (['co_branding', 'sticker', 'lightbox'], 45),
    (['co_branding', 'sticker'], 80),
    (['co_branding', 'lightbox'], 80),
    (['co_branding'], 110),
    (['sticker', 'lightbox'], 50),
    (['sticker'], 82.5),
    (['lightbox'], 85),
    ([], 110),
    (['franchise'], 40),
    (['lightbox', 'franchise'], 20),
    (['sticker', 'franchise'], 0),
    (['co_branding', 'franchise'], 40),
])
def test_branding(performer_brandings, expected_commission):
    contract = _make_contract(
            **dict(
                _DEFAULT_CONTRACT_KWARGS,
                marketing_level=performer_brandings,
                branding_discounts=_BRANDING_DISCOUNTS
            )
    )
    actual_commission = contract.get_commission_value(
        commission_manager.make_simple_cost_info(1000),
        _NORMAL,
    )
    assert actual_commission == decimal.Decimal(expected_commission)


DATE_2 = datetime.datetime(2016, 1, 1)
DATE_1 = datetime.datetime(2015, 1, 1)
DATE_0 = datetime.datetime(2014, 1, 1)


@pytest.inline_callbacks
@pytest.mark.filldb(_fill=False)
@pytest.mark.config(
    BRANDING_DISCOUNT_ENABLED=True
)
@pytest.mark.parametrize('park,provided_level,franchise_zone,expected_level', [
    ({
        'disable_branding_discount': True,  # should be ignored
        dbh.parks.Doc.enable_branding_lightbox: [{'v': True, 'ts': DATE_0}]
    }, [
        dbh.drivers.BRANDING_STICKER,
        dbh.drivers.BRANDING_LIGHTBOX,
        dbh.drivers.BRANDING_CO_BRANDING
    ], None, {'lightbox'}),
    ({dbh.parks.Doc.enable_branding_sticker: [
        {'v': True, 'ts': DATE_1}, {'v': False, 'ts': DATE_0}
    ]}, [
        dbh.drivers.BRANDING_STICKER,
        dbh.drivers.BRANDING_LIGHTBOX,
        dbh.drivers.BRANDING_CO_BRANDING
    ], None, {'sticker'}),
    ({dbh.parks.Doc.enable_branding_co_branding: [
        {'v': True, 'ts': DATE_1}, {'v': False, 'ts': DATE_0}
    ]}, [
         dbh.drivers.BRANDING_STICKER,
         dbh.drivers.BRANDING_LIGHTBOX,
         dbh.drivers.BRANDING_CO_BRANDING
    ], None, {'co_branding'}),
    ({dbh.parks.Doc.enable_branding_lightbox: [{'v': True, 'ts': DATE_0}]}, [
        dbh.drivers.BRANDING_STICKER,
        dbh.drivers.BRANDING_LIGHTBOX,
        dbh.drivers.BRANDING_CO_BRANDING
    ], None, {'lightbox'}),
    ({dbh.parks.Doc.enable_branding_lightbox: [
        {'v': True, 'ts': DATE_2},
        {'v': False, 'ts': DATE_1},
        {'v': True, 'ts': DATE_0},
    ]}, [
        dbh.drivers.BRANDING_LIGHTBOX
    ], None, {'lightbox'}),
    ({dbh.parks.Doc.enable_branding_lightbox: [
        {'v': False, 'ts': DATE_1}, {'v': True, 'ts': DATE_0}
    ]}, [
         dbh.drivers.BRANDING_LIGHTBOX
     ], None, set()),
    ({
        dbh.parks.Doc.enable_branding_lightbox: [{'v': True, 'ts': DATE_0}],
        dbh.parks.Doc.enable_branding_sticker: [{'v': True, 'ts': DATE_0}],
        dbh.parks.Doc.enable_branding_co_branding: [{'v': True, 'ts': DATE_0}],
    }, [
        dbh.drivers.BRANDING_STICKER,
        dbh.drivers.BRANDING_LIGHTBOX,
        dbh.drivers.BRANDING_CO_BRANDING
    ], None, {'sticker', 'lightbox', 'co_branding'}),
    ({dbh.parks.Doc.enable_branding_sticker: [{'v': True, 'ts': DATE_0}]}, [
        dbh.drivers.BRANDING_LIGHTBOX,
        dbh.drivers.BRANDING_CO_BRANDING
    ], None, set()),
    # has park franchise zones, and order has the same zone
    # -> select franchise
    ({
        dbh.parks.Doc.franchise_zones: [
            {'v': ['rnd'], 'ts': DATE_0},
        ],
    }, [
        dbh.drivers.BRANDING_STICKER,
        dbh.drivers.BRANDING_LIGHTBOX,
        dbh.drivers.BRANDING_CO_BRANDING,
    ], 'rnd', {'franchise'}),
    # has sticker, empty park franchise zones, empty order franchise zone
    # -> select only sticker
    ({
        dbh.parks.Doc.franchise_zones: [
            {'v': [], 'ts': DATE_1},
            {'v': ['rnd'], 'ts': DATE_0},
        ],
        dbh.parks.Doc.enable_branding_sticker: [{'v': True, 'ts': DATE_0}],
    }, [
        dbh.drivers.BRANDING_STICKER,
        dbh.drivers.BRANDING_LIGHTBOX,
        dbh.drivers.BRANDING_CO_BRANDING,
    ], None, {'sticker'}),
    # has sticker, franchise zone not specified, but park has it
    # -> select all
    ({
        dbh.parks.Doc.franchise_zones: [
            {'v': ['msk', 'spb'], 'ts': DATE_1},
            {'v': ['rnd'], 'ts': DATE_0},
        ],
        dbh.parks.Doc.enable_branding_sticker: [{'v': True, 'ts': DATE_0}],
    }, [
        dbh.drivers.BRANDING_STICKER,
        dbh.drivers.BRANDING_LIGHTBOX,
        dbh.drivers.BRANDING_CO_BRANDING,
    ], None, {'sticker', 'franchise'}),
    # has sticker, has franchise in park, and it is specified
    # -> select sticker and franchise
    ({
        dbh.parks.Doc.franchise_zones: [
            {'v': ['msk', 'spb'], 'ts': DATE_1},
            {'v': ['rnd'], 'ts': DATE_0},
        ],
        dbh.parks.Doc.enable_branding_sticker: [{'v': True, 'ts': DATE_0}],
    }, [
        dbh.drivers.BRANDING_STICKER,
        dbh.drivers.BRANDING_LIGHTBOX,
        dbh.drivers.BRANDING_CO_BRANDING,
    ], 'msk', {'sticker', 'franchise'}),
    # has sticker, has franchise in park, but another zone is specified
    # -> select only sticker
    ({
        dbh.parks.Doc.franchise_zones: [
            {'v': ['msk', 'spb'], 'ts': DATE_1},
            {'v': ['rnd'], 'ts': DATE_0},
        ],
        dbh.parks.Doc.enable_branding_sticker: [{'v': True, 'ts': DATE_0}],
    }, [
        dbh.drivers.BRANDING_STICKER,
        dbh.drivers.BRANDING_LIGHTBOX,
        dbh.drivers.BRANDING_CO_BRANDING,
    ], 'rnd', {'sticker'}),
])
def test_calc_marketing_level(park, provided_level,
                              franchise_zone, expected_level):
    park_brandings = yield park_manager.branding_discount_level(
        park, datetime.datetime.max, franchise_zone
    )
    actual = commission_manager._calc_branding_level(
        park_brandings, provided_level
    )
    assert set(actual) == expected_level


def _make_contract(
        payment_type, type, min_order_cost, max_order_cost, expired_cost,
        percent, marketing_level, has_commission,
        expired_percent, cancel_percent, acquiring_percent,
        agent_percent, branding_discounts,
        data, vat=11800, taximeter_payment=0,
        corp_vat=11800, id='some_id', has_acquiring_percent=True,
        has_fixed_cancel_percent=True):
    Doc = dbh.commission_contracts.Doc
    doc = Doc({
        Doc.commission: {
            Doc.commission.type.key: type,
            Doc.commission.has_commission.key: has_commission,
            Doc.commission.min_order_cost.key: min_order_cost,
            Doc.commission.max_order_cost.key: max_order_cost,
            Doc.commission.expired_cost.key: expired_cost,
            Doc.commission.percent.key: percent,
            Doc.commission.expired_percent.key: expired_percent,
            Doc.commission.cancel_percent.key: cancel_percent,
            Doc.commission.vat.key: vat,
            Doc.commission.taximeter_payment.key: taximeter_payment,
            Doc.commission.has_acquiring_percent.key: has_acquiring_percent,
            Doc.commission.has_fixed_cancel_percent.key:
                has_fixed_cancel_percent,
            Doc.commission.acquiring_percent.key: acquiring_percent,
            Doc.commission.agent_percent.key: agent_percent,
            Doc.commission.branding_discounts.key:
                branding_discounts,
            Doc.commission.data.key: data,
            Doc.commission.hiring.key: {
                Doc.commission.hiring.extra_percent.key: 0,
                Doc.commission.hiring.extra_percent_with_rent.key: 0,
                Doc.commission.hiring.max_age_in_seconds.key: 15552000,
            }
        }
    })
    return commission_manager._make_contract_from_raw_data(
        id=id,
        payment_type=payment_type,
        marketing_level=marketing_level,
        performer_brandings=None,
        order_info=None,
        park_brandings=None,
        corp_vat=corp_vat,
        acquiring_percent=None,
        contract=commission_manager.StaticContract.from_doc(doc),
    )


@pytest.inline_callbacks
@pytest.mark.filldb(_fill=False)
@pytest.mark.config(
    BRANDING_DISCOUNT_ENABLED=False
)
@pytest.mark.parametrize('park,provided_level,expected_level,has_contract', [
    ({
         dbh.parks.Doc.enable_branding_lightbox: [{'v': False, 'ts': DATE_0}],
     }, [
         dbh.drivers.BRANDING_STICKER,
         dbh.drivers.BRANDING_LIGHTBOX
     ], {'lightbox', 'sticker'}, True),
    ({
         dbh.parks.Doc.enable_branding_lightbox: [{'v': False, 'ts': DATE_0}],
     }, [
         dbh.drivers.BRANDING_STICKER,
         dbh.drivers.BRANDING_LIGHTBOX
     ], set(), False)
])
def test_calc_marketing_level_for_discount_disabled(
        park, provided_level, expected_level, has_contract, patch
):
    @patch('taxi.internal.park_manager._has_marketing_contract')
    def foo(*args, **kwargs):
        return has_contract

    park_brandings = yield park_manager.branding_discount_level(
        park, None
    )
    actual = commission_manager._calc_branding_level(
        park_brandings, provided_level
    )
    assert set(actual) == expected_level


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('billing_type, type,payment_type,min_order_cost,'
                         'max_order_cost,expired_cost, percent,'
                         'cancel_percent,'
                         'expired_percent,marketing_level,'
                         'branding_discounts,'
                         'acquiring_percent,'
                         'agent_percent,cost,data', [
    (_NORMAL, 'fixed_percent', 'cash', 1990000, 60000000, 8000000,
     1100, 1100, 1100, [], [], 200, 1,
     4000, {}),
])
def test_apply_commission_promocode(
        billing_type, type, payment_type, min_order_cost, max_order_cost,
        expired_cost, percent, cancel_percent, expired_percent,
        marketing_level, branding_discounts,
        acquiring_percent,
        agent_percent, cost, data):
    vat_inner = 11800
    contract = _make_contract(
        type=type,
        payment_type=payment_type,
        has_commission=True,
        min_order_cost=min_order_cost,
        max_order_cost=max_order_cost,
        expired_cost=expired_cost,
        percent=percent,
        expired_percent=expired_percent,
        cancel_percent=cancel_percent,
        vat=vat_inner,
        acquiring_percent=acquiring_percent,
        agent_percent=agent_percent,
        branding_discounts=branding_discounts,
        marketing_level=marketing_level,
        corp_vat=11800,
        data=data,
    )
    cost_info = commission_manager.CostInfo(
        taximeter_cost=cost,
        sum_of_costs=cost,
        extra_commission=math_numbers.ZERO,
        rebate_percent=math_numbers.ZERO,
        callcenter_commission=math_numbers.ZERO,
        min_commission=decimal.Decimal(118),
    )
    commission_data = contract.get_commission_data(
        cost_info, billing_type, with_driver_promocode=True
    )
    assert commission_data.raw_commission == decimal.Decimal(100)
