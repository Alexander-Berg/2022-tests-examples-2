# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import pytest

from taxi.core import async
from taxi.internal import commission_manager
from taxi.internal import dbh
from taxi.util import decimal

from utils.protocol_1x.methods import get_commission_info


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_get_commission_info_fetch():
    class Method(get_commission_info.Method):
        @async.inline_callbacks
        def _fetch_contracts(self, data, city, zone_name):
            yield
            async.return_value({
                dbh.orders.PAYMENT_TYPE_CASH: _get_dummy_contract(
                    dbh.orders.PAYMENT_TYPE_CASH
                ),
                dbh.orders.PAYMENT_TYPE_CARD: _get_dummy_contract(
                    dbh.orders.PAYMENT_TYPE_CARD
                ),
                dbh.orders.PAYMENT_TYPE_CORP: _get_dummy_contract(
                    dbh.orders.PAYMENT_TYPE_CORP,
                    contract_type=commission_manager.ABSOLUTE_VALUE_TYPE,
                    contract_data={
                        'commission': '3000000',
                        'cancel_commission': '2000000',
                        'expired_commission': '1000000'
                    }
                )
            })

        @async.inline_callbacks
        def _fetch_geodata(self, data):
            yield
            async.return_value(
                get_commission_info.GeoData(
                    city='Москва', zone_name='moscow', country='rus')
            )

        @async.inline_callbacks
        def _get_currency_by_country(self, country):
            yield
            async.return_value('руб.')

    m = Method()

    commission_info = yield m.POST({}, {
        'city': 'Москва',
        'values': [1000],
    })
    assert commission_info == {
        'currency': 'руб.',
        'cash': [
            {
                'commission': 150.0,
                'commission_with_vat': 177.0,
                'percent': 15,
                'vat': 18,
            }
        ],
        'card': [
            {
                'commission': 150.0,
                'commission_with_vat': 177.0,
                'percent': 15,
                'vat': 18,
                'agent_percent': 5,
                'acquiring_percent': 0.01,
            },
        ],
        'corp': [
            {
                'commission': 300.0,
                'commission_with_vat': 354.0,
                'percent': 30.0,
                'vat': 18,
            }
        ],
    }


def _get_dummy_contract(
        payment_type=dbh.orders.PAYMENT_TYPE_CASH,
        contract_type=commission_manager.FIXED_PERCENT_TYPE,
        contract_data=None):
    if contract_type == commission_manager.FIXED_PERCENT_TYPE:
        contract_class = commission_manager.FixedPercentCommissionContract
    elif contract_type == commission_manager.ABSOLUTE_VALUE_TYPE:
        contract_class = commission_manager.AbsoluteValueCommissionContract
    else:
        raise ValueError('{} contract type is not supported'.format(
            contract_type
        ))

    class contract_doc:
        has_commission = True
        min_order_cost = decimal.Decimal('99')
        max_order_cost = decimal.Decimal('6000')
        expired_cost = decimal.Decimal('100')
        percent = decimal.Decimal('0.15')
        has_fixed_cancel_percent = True
        cancel_percent = decimal.Decimal('0.15')
        expired_percent = decimal.Decimal('0.15')
        vat = decimal.Decimal('1.18')
        taximeter_payment = decimal.Decimal('0')
        callcenter_commission_percent = decimal.Decimal('0')
        branding_discounts = {}
        acquiring_percent = decimal.Decimal('0.0001')
        has_acquiring_percent = True
        agent_percent = decimal.Decimal('0.05')
        commission_type = contract_type
        data = contract_data
        billable_cancel_distance = 300
        user_cancel_min_td = 120
        user_cancel_max_td = 600
        park_cancel_min_td = 420
        park_cancel_max_td = 600
        hiring_extra_percent = decimal.Decimal('0.02')
        hiring_max_age = datetime.timedelta(seconds=15552000)

    contract = contract_class(
        'test',
        payment_type=payment_type,
        marketing_level=frozenset(),
        performer_brandings=None,
        order_info=None,
        park_brandings=None,
        corp_vat=decimal.Decimal('1.18'),
        acquiring_percent=None,
        contract=contract_doc,
    )
    return contract
