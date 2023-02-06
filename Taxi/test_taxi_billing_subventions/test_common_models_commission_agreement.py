import decimal
import typing as tp


import pytest

from taxi import billing
from taxi.billing.clients import models as client_models

from taxi_billing_subventions.common import models
from taxi_billing_subventions.common.db import commission


@pytest.mark.parametrize(
    'commission_contract, order_json, group, expected_commission_json',
    [
        (
            'fixed_rate/commission_contract.json',
            'order.json',
            'base',
            'fixed_rate/expected_commission_and_vat.json',
        ),
        (
            'fixed_rate/commission_contract_with_cancel_rate.json',
            'cancel_order.json',
            'base',
            'fixed_rate/expected_cancel_commission_and_vat.json',
        ),
        (
            'fixed_rate/commission_contract_with_expired_rate.json',
            'expired_order.json',
            'base',
            'fixed_rate/expected_expired_commission_and_vat.json',
        ),
        (
            'fixed_rate/commission_contract.json',
            'order_with_rebate.json',
            'base',
            'fixed_rate/expected_commission_and_vat_for_rebate.json',
        ),
        (
            'fixed_rate/commission_contract.json',
            'order_with_ind_bel_nds.json',
            'base',
            'fixed_rate/expected_commission_and_vat_ind_bel_nds.json',
        ),
        (
            'fixed_rate/commission_contract.json',
            'too_high_cost_order.json',
            'base',
            'fixed_rate/expected_high_cost_commission_and_vat.json',
        ),
        (
            'fixed_rate/commission_contract.json',
            'too_low_cost_order.json',
            'base',
            'fixed_rate/expected_low_cost_commission_and_vat.json',
        ),
        (
            'fixed_rate/commission_contract.json',
            'order_with_driver_promocode.json',
            'base',
            'fixed_rate/expected_commission_and_vat_driver_promocode.json',
        ),
        (
            'fixed_rate/commission_contract.json',
            'order_with_driver_workshift.json',
            'base',
            'fixed_rate/expected_commission_and_vat_driver_workshift.json',
        ),
        (
            'fixed_rate/commission_contract.json',
            'not_billable_order.json',
            'base',
            'fixed_rate/expected_not_billable_commission_and_vat.json',
        ),
        (
            'absolute_value/commission_contract.json',
            'order.json',
            'base',
            'absolute_value/expected_commission_and_vat.json',
        ),
        (
            'absolute_value/commission_contract_with_cancel_rate.json',
            'cancel_order.json',
            'base',
            'absolute_value/expected_cancel_commission_and_vat.json',
        ),
        (
            'absolute_value/commission_contract_with_expired_rate.json',
            'expired_order.json',
            'base',
            'absolute_value/expected_expired_commission_and_vat.json',
        ),
        (
            'absolute_value/commission_contract.json',
            'order_with_ind_bel_nds.json',
            'base',
            'absolute_value/expected_commission_and_vat_ind_bel_nds.json',
        ),
        (
            'absolute_value/commission_contract.json',
            'order_with_driver_promocode.json',
            'base',
            'absolute_value/expected_commission_and_vat_driver_promocode.json',
        ),
        (
            'absolute_value/commission_contract.json',
            'order_with_driver_workshift.json',
            'base',
            'absolute_value/expected_commission_and_vat_driver_workshift.json',
        ),
        (
            'asymptotic_rate/commission_contract.json',
            'order.json',
            'base',
            'asymptotic_rate/expected_commission_and_vat.json',
        ),
        (
            'asymptotic_rate/commission_contract_for_card_order.json',
            'card_order.json',
            'base',
            'asymptotic_rate/expected_card_commission_and_vat.json',
        ),
        (
            'asymptotic_rate/commission_contract.json',
            'order_with_ind_bel_nds.json',
            'base',
            'asymptotic_rate/expected_commission_and_vat_ind_bel_nds.json',
        ),
        (
            'asymptotic_rate/commission_contract.json',
            'too_high_cost_order.json',
            'base',
            'asymptotic_rate/expected_high_cost_commission_and_vat.json',
        ),
        (
            'asymptotic_rate/commission_contract.json',
            'too_low_cost_order.json',
            'base',
            'asymptotic_rate/expected_low_cost_commission_and_vat.json',
        ),
        (
            'asymptotic_rate/commission_contract.json',
            'order_with_driver_promocode.json',
            'base',
            'asymptotic_rate/'
            'expected_commission_and_vat_driver_promocode.json',
        ),
        (
            'asymptotic_rate/commission_contract.json',
            'order_with_driver_workshift.json',
            'base',
            'asymptotic_rate/'
            'expected_commission_and_vat_driver_workshift.json',
        ),
        (
            'pool_htan/commission_contract.json',
            'order.json',
            'base',
            'pool_htan/expected_commission_and_vat.json',
        ),
        (
            'call_center/commission_contract.json',
            'call_center/order.json',
            'call_center',
            'call_center/expected_commission_and_vat.json',
        ),
        (
            'call_center/commission_contract.json',
            'call_center/order_with_driver_promocode.json',
            'call_center',
            'call_center/expected_commission_and_vat.json',
        ),
        (
            'call_center/commission_contract.json',
            'call_center/order_with_driver_workshift.json',
            'call_center',
            'call_center/expected_commission_and_vat_driver_workshift.json',
        ),
        (
            'hiring/commission_contract.json',
            'hiring/order_without_hiring.json',
            'hiring',
            'hiring/expected_commission_and_vat_without_hiring.json',
        ),
        (
            'hiring/commission_contract.json',
            'hiring/order_with_hiring.json',
            'hiring',
            'hiring/expected_commission_and_vat_with_hiring.json',
        ),
        (
            'hiring/commission_contract.json',
            'hiring/order_with_hiring_with_rent.json',
            'hiring',
            'hiring/expected_commission_and_vat_with_hiring_with_rent.json',
        ),
        (
            'hiring/commission_contract.json',
            'hiring/order_with_hiring_with_rent_increased.json',
            'hiring',
            'hiring/'
            'expected_commission_and_vat_with_hiring_with_rent_increased.json',
        ),
        (
            'hiring/commission_contract.json',
            'order_with_rebate.json',
            'hiring',
            'hiring/expected_commission_and_vat_for_rebate.json',
        ),
        (
            'hiring/commission_contract.json',
            'order_with_rebate_and_inner_vat.json',
            'hiring',
            'hiring/expected_commission_and_vat_for_rebate_with_inner_vat'
            '.json',
        ),
        (
            'hiring/commission_contract.json',
            'hiring/order_with_driver_promocode.json',
            'hiring',
            'hiring/expected_commission_and_vat_with_hiring.json',
        ),
        (
            'hiring/commission_contract.json',
            'hiring/order_with_driver_workshift.json',
            'hiring',
            'hiring/expected_commission_and_vat_driver_workshift.json',
        ),
        (
            'acquiring/commission_contract.json',
            'acquiring/card_order.json',
            'acquiring',
            'acquiring/expected_commission_and_vat_card_order.json',
        ),
        (
            'acquiring/commission_contract.json',
            'cash_order.json',
            'acquiring',
            'acquiring/expected_commission_and_vat_cash_order.json',
        ),
        (
            'acquiring/commission_contract.json',
            'acquiring/order_with_driver_promocode.json',
            'acquiring',
            'acquiring/expected_commission_and_vat_driver_promocode.json',
        ),
        (
            'acquiring/commission_contract.json',
            'acquiring/order_with_driver_workshift.json',
            'acquiring',
            'acquiring/expected_commission_and_vat_driver_workshift.json',
        ),
        (
            'agent/commission_contract.json',
            'agent/card_order.json',
            'agent',
            'agent/expected_commission_and_vat_card_order.json',
        ),
        (
            'agent/commission_contract.json',
            'cash_order.json',
            'agent',
            'agent/expected_commission_and_vat_cash_order.json',
        ),
        (
            'agent/commission_contract.json',
            'agent/order_with_driver_promocode.json',
            'agent',
            'agent/expected_commission_and_vat_driver_promocode.json',
        ),
        (
            'agent/commission_contract.json',
            'agent/order_with_driver_workshift.json',
            'agent',
            'agent/expected_commission_and_vat_driver_workshift.json',
        ),
        (
            'voucher/commission_contract.json',
            'order.json',
            'voucher',
            'voucher/expected_commission_and_vat.json',
        ),
        (
            'voucher/commission_contract.json',
            'order_with_rebate.json',
            'voucher',
            'voucher/expected_commission_and_vat_for_rebate.json',
        ),
        (
            'voucher/commission_contract.json',
            'order_with_driver_promocode.json',
            'voucher',
            'voucher/expected_commission_and_vat.json',
        ),
        (
            'voucher/commission_contract.json',
            'order_with_driver_workshift.json',
            'voucher',
            'voucher/expected_commission_and_vat_driver_workshift.json',
        ),
        (
            'taximeter/commission_contract.json',
            'order.json',
            'taximeter',
            'taximeter/expected_commission_and_vat.json',
        ),
        (
            'taximeter/zero_commission_contract.json',
            'taximeter/zero_order.json',
            'taximeter',
            'taximeter/expected_zero_commission_and_vat.json',
        ),
        (
            'taximeter/commission_contract.json',
            'order_with_ind_bel_nds.json',
            'taximeter',
            'taximeter/expected_commission_and_vat_ind_bel_nds.json',
        ),
        (
            'taximeter/commission_contract.json',
            'order_with_driver_promocode.json',
            'taximeter',
            'taximeter/expected_commission_and_vat_driver_promocode.json',
        ),
        (
            'taximeter/commission_contract.json',
            'order_with_driver_workshift.json',
            'taximeter',
            'taximeter/expected_commission_and_vat_driver_workshift.json',
        ),
        (
            'childseat_rental/commission_contract.json',
            'childseat_rental/order.json',
            'childseat_rental',
            'childseat_rental/expected_commission_and_vat_with_childseat.json',
        ),
        (
            'childseat_rental/commission_contract.json',
            'order.json',
            'childseat_rental',
            'childseat_rental/expected_commission_and_vat.json',
        ),
        (
            'childseat_rental/commission_contract.json',
            'childseat_rental/cancel_order.json',
            'childseat_rental',
            'childseat_rental/expected_cancel_commission_and_vat.json',
        ),
        (
            'childseat_rental/commission_contract.json',
            'childseat_rental/order_with_driver_promocode.json',
            'childseat_rental',
            'childseat_rental/expected_commission_and_vat_with_childseat.json',
        ),
        (
            'childseat_rental/commission_contract.json',
            'childseat_rental/order_with_driver_workshift.json',
            'childseat_rental',
            'childseat_rental/expected_commission_and_vat_with_childseat.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_get_commission_details(
        commission_contract,
        order_json,
        group,
        expected_commission_json,
        load_py_json_dir,
):
    # pylint: disable=too-many-locals
    agreements: tp.List[models.commission.Agreement]
    commission_input: models.doc.CommissionInput
    agreements, commission_input, expected_commission_and_vat = (
        load_py_json_dir(
            'test_get_commission_details',
            commission_contract,
            order_json,
            expected_commission_json,
        )
    )
    relevant_agreements = [
        an_agreement
        for an_agreement in agreements
        if an_agreement.group == group
    ]
    assert len(relevant_agreements) == 1
    an_agreement = relevant_agreements[0]

    expected_unrealized_commission = expected_commission_and_vat[
        'unrealized_commission'
    ]
    expected_support_info = expected_commission_and_vat['support_info']
    expected_support_info_v2 = expected_commission_and_vat['support_info_v2']
    net_commission = _commission(expected_commission_and_vat['commission'])
    gross_commission = _commission(
        expected_commission_and_vat['gross_commission'],
    )
    branding_discount = _commission(
        expected_commission_and_vat['branding_discount'],
    )
    promocode_discount = _commission(
        expected_commission_and_vat['promocode_discount'],
    )
    expected_commission_details = models.commission.CommissionDetails(
        gross_commission=gross_commission,
        branding_discount=branding_discount,
        promocode_discount=promocode_discount,
        commission=net_commission,
        unrealized_commission=(
            billing.Money(
                decimal.Decimal(expected_unrealized_commission['value']),
                expected_unrealized_commission['currency'],
            )
            if expected_unrealized_commission
            else None
        ),
        support_info=expected_support_info,
        support_info_v2=expected_support_info_v2,
    )

    actual_details = an_agreement.get_commission_details(
        commission_input, commission_input.driver_promocode_min_commission,
    )
    currency = commission_input.currency
    aggregated = (
        _none_to_zero(actual_details.gross_commission, currency)
        - _none_to_zero(actual_details.branding_discount, currency)
        - _none_to_zero(actual_details.promocode_discount, currency)
    )
    assert round(aggregated.value.amount, 10) == round(
        _none_to_zero(net_commission, currency).value.amount, 10,
    )
    assert round(aggregated.vat.amount, 10) == round(
        _none_to_zero(net_commission, currency).vat.amount, 10,
    )
    assert actual_details == expected_commission_details


def _none_to_zero(
        commission_: tp.Optional[models.commission.Commission],
        fallback_currency: str,
) -> models.commission.Commission:
    if commission_ is None:
        return models.commission.Commission.zero(fallback_currency)
    return commission_


def _commission(
        value_and_vat: tp.Optional[list],
) -> tp.Optional[models.commission.Commission]:
    if value_and_vat is None:
        return None
    value, vat = value_and_vat
    return models.commission.Commission(
        billing.Money(decimal.Decimal(value['value']), value['currency']),
        billing.Money(decimal.Decimal(vat['value']), vat['currency']),
    )


@pytest.mark.parametrize(
    'commission_contract, order_json, group, expected_rebate_value',
    [
        (
            'hiring/commission_contract.json',
            'order_with_rebate.json',
            'hiring',
            billing.Money(amount=decimal.Decimal('160'), currency='RUB'),
        ),
        # corp vat included in cost
        (
            'hiring/commission_contract.json',
            'order_with_rebate_and_inner_vat.json',
            'hiring',
            billing.Money(amount=decimal.Decimal('160'), currency='RUB'),
        ),
        # corp vat appended to max_cost_for_commission
        (
            'hiring/commission_contract.json',
            'order_with_rebate_and_inner_vat_and_limitation.json',
            'hiring',
            billing.Money(amount=decimal.Decimal('3540'), currency='RUB'),
        ),
    ],
)
def test_get_rebate_value(
        commission_contract,
        order_json,
        group,
        expected_rebate_value,
        load_py_json_dir,
):
    agreements: tp.List[models.commission.Agreement]
    commission_input: models.doc.CommissionInput
    agreements, commission_input = load_py_json_dir(
        'test_get_rebate_value', commission_contract, order_json,
    )
    relevant_agreements = [
        an_agreement
        for an_agreement in agreements
        if an_agreement.group == group
    ]
    assert len(relevant_agreements) == 1
    an_agreement = relevant_agreements[0]

    assert (
        an_agreement.calculator.get_rebate_value(commission_input)
        == expected_rebate_value
    )


@pytest.mark.parametrize(
    'order_json,expected_conditions',
    [
        ('order.json', {'p': 'cash', 'tariff_class': 'econom', 'z': 'moscow'}),
        (
            'kazan_order_without_tag.json',
            {'p': 'cash', 'tariff_class': 'econom', 'z': 'kazan'},
        ),
        (
            'kazan_order_with_tag.json',
            {
                'p': 'cash',
                'tariff_class': 'econom',
                'z': 'kazan',
                'tag': 'reposition_home',
            },
        ),
        (
            'kazan_order_with_irrelevant_tag.json',
            {'p': 'cash', 'tariff_class': 'econom', 'z': 'kazan'},
        ),
        (
            'abakan_order_with_conflicting_commission_tags.json',
            {
                'p': 'cash',
                'tariff_class': 'econom',
                'z': 'abakan',
                'tag': 'conflicting_tag_1',
            },
        ),
        (
            'ryazan_order_with_conflicting_tag_and_nontag_rules.json',
            {'p': 'cash', 'z': 'ryazan', 'tag': 'some_ryazan_tag'},
        ),
    ],
)
@pytest.mark.filldb(
    commission_contracts='for_test_get_most_specific_agreements',
)
async def test_get_most_specific_agreements(
        order_json, expected_conditions, db, load_py_json_dir,
):
    order = load_py_json_dir('test_get_most_specific_agreements', order_json)
    search_params = models.commission.SearchParams(
        due=order.due,
        zone_name=order.zone_name,
        tariff_class=order.tariff.class_,
        payment_type=order.payment_type,
        tags=order.performer.tags,
    )
    agreements = await commission.find_commission_agreements(db, search_params)
    ids = {agreement.contract_id for agreement in agreements}
    assert len(ids) == 1
    actual_conditions = agreements[0].conditions
    assert actual_conditions == expected_conditions


@pytest.mark.parametrize(
    'agreement, billing_type, expected',
    [
        (
            models.commission.FixedRateServiceAgreement(
                client_models.billing_commissions.Agreement.from_json(
                    {
                        'cancelation_settings': {
                            'pickup_location_radius': 300,
                            'park_billable_cancel_interval': ['420', '600'],
                            'user_billable_cancel_interval': ['120', '600'],
                        },
                        'contract_id': 'contract_id',
                        'group': 'base',
                        'kind': 'fixed_rate',
                        'rate': {'kind': 'flat', 'rate': '200'},
                        'vat': '1.18',
                        'effective_billing_type': 'normal',
                    },
                ),
            ),
            models.commission.const.CANCEL_BILLING_TYPE,
            False,
        ),
        (
            models.commission.FixedRateServiceAgreement(
                client_models.billing_commissions.Agreement.from_json(
                    {
                        'cancelation_settings': {
                            'pickup_location_radius': 300,
                            'park_billable_cancel_interval': ['420', '600'],
                            'user_billable_cancel_interval': ['120', '600'],
                        },
                        'contract_id': 'contract_id',
                        'group': 'base',
                        'kind': 'fixed_rate',
                        'rate': {'kind': 'flat', 'rate': '200'},
                        'vat': '1.18',
                        'effective_billing_type': 'cancel',
                    },
                ),
            ),
            models.commission.const.CANCEL_BILLING_TYPE,
            True,
        ),
        (
            models.commission.FixedRateServiceAgreement(
                client_models.billing_commissions.Agreement.from_json(
                    {
                        'cancelation_settings': {
                            'pickup_location_radius': 300,
                            'park_billable_cancel_interval': ['420', '600'],
                            'user_billable_cancel_interval': ['120', '600'],
                        },
                        'contract_id': 'contract_id',
                        'group': 'base',
                        'kind': 'fixed_rate',
                        'rate': {'kind': 'flat', 'rate': '0'},
                        'vat': '1.18',
                        'effective_billing_type': 'cancel',
                    },
                ),
            ),
            models.commission.const.CANCEL_BILLING_TYPE,
            False,
        ),
        (
            [
                agreement
                for agreement in (
                    commission.Converter.build_agreements_from_doc(
                        {
                            '_id': 'id_value',
                            'cn': {},
                            'bv': {
                                'bcd': 300,
                                'p_max': 600,
                                'p_min': 420,
                                'u_max': 600,
                                'u_min': 120,
                            },
                            'cm': {
                                'acp': 0,
                                'agp': 0,
                                'bd': [
                                    {
                                        'marketing_level': [
                                            'lightbox',
                                            'co_branding',
                                        ],
                                        'value': 400,
                                    },
                                    {
                                        'marketing_level': ['lightbox'],
                                        'value': 200,
                                    },
                                ],
                                'callcenter_commission_percent': 0,
                                'cp': 0,
                                'ec': 1500000,
                                'ep': 0,
                                'has_fixed_cancel_percent': True,
                                'hc': True,
                                'hiring': {
                                    'extra_percent': 200,
                                    'extra_percent_with_rent': 400,
                                    'max_age_in_seconds': 15552000,
                                },
                                'max': 150000000,
                                'min': 1000000,
                                'p': 1000,
                                't': 'fixed_percent',
                                'taximeter_payment': 10000,
                                'vat': 11800,
                                'voucher_commission_percent': 0,
                            },
                        },
                    )
                )
                if agreement.group == models.commission.Group.BASE.value
            ][0],
            models.commission.const.CANCEL_BILLING_TYPE,
            False,
        ),
        (
            [
                agreement
                for agreement in (
                    commission.Converter.build_agreements_from_doc(
                        {
                            '_id': 'id_value',
                            'cn': {},
                            'bv': {
                                'bcd': 300,
                                'p_max': 600,
                                'p_min': 420,
                                'u_max': 600,
                                'u_min': 120,
                            },
                            'cm': {
                                'acp': 0,
                                'agp': 0,
                                'bd': [
                                    {
                                        'marketing_level': [
                                            'lightbox',
                                            'co_branding',
                                        ],
                                        'value': 400,
                                    },
                                    {
                                        'marketing_level': ['lightbox'],
                                        'value': 200,
                                    },
                                ],
                                'callcenter_commission_percent': 0,
                                'cp': 1,
                                'ec': 1500000,
                                'ep': 0,
                                'has_fixed_cancel_percent': True,
                                'hc': True,
                                'hiring': {
                                    'extra_percent': 200,
                                    'extra_percent_with_rent': 400,
                                    'max_age_in_seconds': 15552000,
                                },
                                'max': 150000000,
                                'min': 1000000,
                                'p': 0,
                                't': 'asymptotic_formula',
                                'taximeter_payment': 10000,
                                'vat': 11800,
                                'voucher_commission_percent': 0,
                                'd': {
                                    'asymp': 200000,
                                    'cost_norm': 500000,
                                    'max_commission_percent': 300000,
                                    'numerator': 20000000,
                                },
                            },
                        },
                    )
                )
                if agreement.group == models.commission.Group.BASE.value
            ][0],
            models.commission.const.CANCEL_BILLING_TYPE,
            True,
        ),
        (
            [
                agreement
                for agreement in (
                    commission.Converter.build_agreements_from_doc(
                        {
                            '_id': 'id_value',
                            'cn': {},
                            'bv': {
                                'bcd': 300,
                                'p_max': 600,
                                'p_min': 420,
                                'u_max': 600,
                                'u_min': 120,
                            },
                            'cm': {
                                'acp': 0,
                                'agp': 0,
                                'bd': [
                                    {
                                        'marketing_level': [
                                            'lightbox',
                                            'co_branding',
                                        ],
                                        'value': 400,
                                    },
                                    {
                                        'marketing_level': ['lightbox'],
                                        'value': 200,
                                    },
                                ],
                                'callcenter_commission_percent': 0,
                                'cp': 1,
                                'ec': 1500000,
                                'ep': 0,
                                'has_fixed_cancel_percent': True,
                                'hc': True,
                                'hiring': {
                                    'extra_percent': 200,
                                    'extra_percent_with_rent': 400,
                                    'max_age_in_seconds': 15552000,
                                },
                                'max': 150000000,
                                'min': 1000000,
                                'p': 0,
                                't': 'asymptotic_formula',
                                'taximeter_payment': 10000,
                                'vat': 11800,
                                'voucher_commission_percent': 0,
                                'd': {
                                    'asymp': 200000,
                                    'cost_norm': 500000,
                                    'max_commission_percent': 300000,
                                    'numerator': 20000000,
                                },
                            },
                        },
                    )
                )
                if agreement.group == models.commission.Group.BASE.value
            ][0],
            models.commission.const.NORMAL_BILLING_TYPE,
            False,
        ),
    ],
)
def test_get_service_agreements_is_zero_cancel_percent(
        agreement: models.commission.Agreement,
        billing_type: str,
        expected: bool,
):
    assert agreement.is_non_zero_cancel_percent(billing_type) == expected
