# pylint: disable=C0302
import json

import pytest

from taxi import discovery
from taxi.billing import util
from taxi.billing.util import dates
from testsuite.utils import ordered_object

from taxi_billing_calculators import models as calc_models
from taxi_billing_calculators.calculators import handling_exceptions
from taxi_billing_calculators.calculators.payout import converter
from taxi_billing_calculators.calculators.payout import helper
from taxi_billing_calculators.calculators.payout import models
from taxi_billing_calculators.calculators.payout import taximeter_builders
from taxi_billing_calculators.calculators.payout.actions import filters
from taxi_billing_calculators.calculators.tlog import tlog_store

_PAYMENT_KIND_TO_REBATE_MAP = {
    'park_b2b_trip_payment': 'rebate_b2b_trip_payment',
    'park_b2b_trip_payment_test': 'rebate_b2b_trip_payment_test',
    # cargo
    'cargo_park_b2b_logistics_payment': (
        'cargo_rebate_park_b2b_logistics_payment'
    ),
    'cargo_multi_park_b2b_trip_payment': (
        'cargo_multi_rebate_park_b2b_trip_payment'
    ),
    'cargo_park_b2b_logistics_payment_test': (
        'cargo_rebate_park_b2b_logistics_payment_test'
    ),
    'cargo_multi_park_b2b_trip_payment_test': (
        'cargo_multi_rebate_park_b2b_trip_payment_test'
    ),
    # delivery
    'delivery_park_b2b_logistics_payment': (
        'delivery_park_rebate_b2b_logistics_payment'
    ),
    'delivery_multi_park_b2b_trip_payment': (
        'delivery_multi_rebate_park_b2b_trip_payment'
    ),
    'delivery_park_b2b_logistics_payment_test': (
        'delivery_rebate_park_b2b_logistics_payment_test'
    ),
    'delivery_multi_park_b2b_trip_payment_test': (
        'delivery_multi_rebate_park_b2b_trip_payment_test'
    ),
    # original b2b_partner_payment
    'cargo_park_b2b_trip_payment': 'cargo_rebate_b2b_trip_payment',
    'cargo_park_b2b_trip_payment_test': 'cargo_rebate_b2b_trip_payment_test',
    'delivery_park_b2b_trip_payment': 'delivery_rebate_b2b_trip_payment',
    'delivery_park_b2b_trip_payment_test': (
        'delivery_rebate_b2b_trip_payment_test'
    ),
}


def config(**extra):
    return pytest.mark.config(
        BILLING_TLOG_SERVICE_IDS={
            'b2b_user_on_delivery_payment_fee': 718,
            'card': 124,
            'cargo_card': 1162,
            'cargo_childchair': 1161,
            'cargo_client_b2b_logistics_payment': 718,
            'cargo_client_b2b_trip_payment': 650,
            'cargo_coupon/netted': 1161,
            'cargo_coupon/paid': 1164,
            'cargo_park_b2b_logistics_payment': 719,
            'cargo_park_b2b_trip_payment': 651,
            'childchair': 111,
            'client_b2b_drive_payment': 672,
            'client_b2b_trip_payment': 650,
            'commission/card': 128,
            'commission/cash': 111,
            'commission/driver_fix': 128,
            'coupon/netted': 111,
            'coupon/paid': 137,
            'delivery_client_b2b_logistics_payment': 718,
            'delivery_client_b2b_trip_payment': 650,
            'delivery_park_b2b_logistics_payment': 719,
            'delivery_park_b2b_trip_payment': 651,
            'driver_referrals': 137,
            'food_payment': 668,
            'park_b2b_fixed_commission': 697,
            'park_b2b_trip_payment': 651,
            'partner_scoring': 128,
            'payment': 137,
            'refund': 111,
            'scout': 619,
            'subvention/netted': 111,
            'subvention/paid': 137,
            'uber': 125,
        },
        BILLING_PAYOUT_PAYMENTS_SETTINGS={
            'delivery_client_b2b_trip_payment': {
                'accounting_table': 'revenues',
                'detailed_product': 'client_b2b_trip_payment',
                'product': 'delivery_client_b2b_trip_payment',
                'service_id': 650,
            },
            'delivery_decoupling_client_b2b_trip_payment': {
                'accounting_table': 'revenues',
                'detailed_product': 'decoupling_b2b_trip_payment',
                'product': 'delivery_client_b2b_trip_payment',
                'service_id': 650,
            },
            'delivery_park_b2b_logistics_payment': {
                'accounting_table': 'expenses',
                'detailed_product': 'delivery_park_b2b_logistics_payment',
                'product': 'delivery_park_b2b_logistics_payment',
                'service_id': 719,
            },
            'cargo_park_b2b_logistics_payment_test': {
                'accounting_table': 'expenses',
                'detailed_product': 'cargo_park_b2b_logistics_payment_test',
                'product': 'cargo_park_b2b_logistics_payment',
                'service_id': 719,
            },
            'cargo_multi_rebate_park_b2b_trip_payment': {
                'accounting_table': 'expenses',
                'detailed_product': 'multi_rebate_b2b_trip_payment',
                'product': 'cargo_park_b2b_trip_payment',
                'service_id': 651,
            },
            'delivery_park_rebate_b2b_logistics_payment': {
                'accounting_table': 'expenses',
                'detailed_product': (
                    'delivery_rebate_park_b2b_logistics_payment'
                ),
                'product': 'delivery_park_b2b_logistics_payment',
                'service_id': 719,
            },
            'user_on_delivery_payment': {
                'accounting_table': 'payments',
                'detailed_product': 'user_on_delivery_payment',
                'product': 'user_on_delivery_payment',
                'service_id': 1040,
            },
            'external_delivery_b2b_logistics_payment': {
                'accounting_table': 'expenses',
                'detailed_product': 'external_delivery_b2b_logistics_payment',
                'product': 'external_delivery_b2b_logistics_payment',
                'service_id': 719,
            },
            'signalq_rent': {
                'accounting_table': 'expenses',
                'detailed_product': 'signalq_monitoring_fee',
                'product': 'signalq_monitoring_fee',
                'service_id': 724,
            },
            'grocery_courier_delivery': {
                'accounting_table': 'expenses',
                'product': 'grocery_courier_delivery',
                'detailed_product': 'grocery_courier_delivery',
                'service_id': 664,
            },
            'dooh_fix': {
                'accounting_table': 'expenses',
                'product': 'dooh_fix',
                'detailed_product': 'dooh_fix',
                'service_id': 724,
            },
            'dooh_rent': {
                'accounting_table': 'expenses',
                'product': 'dooh_rent',
                'detailed_product': 'dooh_rent',
                'service_id': 724,
            },
            'dooh_bonus': {
                'accounting_table': 'expenses',
                'product': 'dooh_bonus',
                'detailed_product': 'dooh_bonus',
                'service_id': 724,
            },
            'grocery_courier_coupon': {
                'accounting_table': 'expenses',
                'product': 'grocery_courier_coupon',
                'detailed_product': 'grocery_courier_coupon',
                'service_id': 664,
            },
            'grocery_item_sale_vat_0': {
                'accounting_table': 'revenues',
                'product': 'grocery_item_sale_vat_0',
                'detailed_product': 'grocery_item_sale_vat_0',
                'service_id': 663,
            },
            'discount_grocery_item_sale_vat_0': {
                'accounting_table': 'revenues',
                'product': 'grocery_item_sale_vat_0',
                'detailed_product': 'discount',
                'service_id': 663,
            },
            'grocery_item_sale_vat_17': {
                'accounting_table': 'revenues',
                'product': 'grocery_item_sale_vat_17',
                'detailed_product': 'grocery_item_sale_vat_17',
                'service_id': 663,
            },
            'grocery_tips_vat_17': {
                'accounting_table': 'revenues',
                'product': 'grocery_tips_vat_17',
                'detailed_product': 'grocery_tips_vat_17',
                'service_id': 663,
            },
            'discount_grocery_item_sale_vat_17': {
                'accounting_table': 'revenues',
                'product': 'grocery_item_sale_vat_17',
                'detailed_product': 'discount',
                'service_id': 663,
            },
            'lead_fee': {
                'accounting_table': 'revenues',
                'product': 'lead_fee',
                'detailed_product': 'lead_fee',
                'service_id': 128,
            },
            'food_payment': {
                'accounting_table': 'revenues',
                'detailed_product': 'food_payment',
                'product': 'food_payment',
                'service_id': 668,
            },
            'client_b2b_drive_payment': {
                'accounting_table': 'revenues',
                'detailed_product': 'client_b2b_drive_payment',
                'product': 'client_b2b_drive_payment',
                'service_id': 672,
            },
            'cargo_multi_client_b2b_trip_payment': {
                'accounting_table': 'revenues',
                'detailed_product': 'multi_client_b2b_trip_payment',
                'product': 'cargo_client_b2b_trip_payment',
                'service_id': 650,
            },
            'delivery_multi_client_b2b_trip_payment': {
                'accounting_table': 'revenues',
                'detailed_product': 'multi_client_b2b_trip_payment',
                'product': 'delivery_client_b2b_trip_payment',
                'service_id': 650,
            },
            'cargo_client_b2b_logistics_payment': {
                'accounting_table': 'revenues',
                'detailed_product': 'cargo_client_b2b_logistics_payment',
                'product': 'cargo_client_b2b_logistics_payment',
                'service_id': 718,
            },
            'delivery_client_b2b_logistics_payment': {
                'accounting_table': 'revenues',
                'detailed_product': 'delivery_client_b2b_logistics_payment',
                'product': 'delivery_client_b2b_logistics_payment',
                'service_id': 718,
            },
            'partner_scoring': {
                'accounting_table': 'revenues',
                'detailed_product': 'partner_scoring',
                'product': 'partner_scoring',
                'service_id': 128,
            },
            'scout': {
                'accounting_table': 'revenues',
                'detailed_product': 'scout',
                'product': 'scout',
                'service_id': 619,
            },
            'scout_sz': {
                'accounting_table': 'revenues',
                'detailed_product': 'scout_sz',
                'product': 'scout_sz',
                'service_id': 619,
            },
            'cargo_scout': {
                'accounting_table': 'revenues',
                'detailed_product': 'cargo_scout',
                'product': 'cargo_scout',
                'service_id': 619,
            },
            'cargo_scout_sz': {
                'accounting_table': 'revenues',
                'detailed_product': 'cargo_scout_sz',
                'product': 'cargo_scout_sz',
                'service_id': 619,
            },
            'cargo_multi_park_b2b_trip_payment': {
                'accounting_table': 'expenses',
                'detailed_product': 'multi_park_b2b_trip_payment',
                'product': 'cargo_park_b2b_trip_payment',
                'service_id': 651,
            },
            'delivery_park_b2b_logistics_payment_test': {
                'accounting_table': 'expenses',
                'detailed_product': 'delivery_park_b2b_logistics_payment_test',
                'product': 'delivery_park_b2b_logistics_payment',
                'service_id': 719,
            },
            'b2b_user_on_delivery_payment_fee': {
                'accounting_table': 'revenues',
                'detailed_product': 'b2b_user_on_delivery_payment_fee',
                'product': 'b2b_user_on_delivery_payment_fee',
                'service_id': 718,
            },
            'scooter_trip_payment_insurance': {
                'accounting_table': 'revenues',
                'detailed_product': 'scooter_insurance',
                'product': 'scooter_trip_payment',
                'service_id': 1122,
            },
            'scooter_trip_payment_per_minute': {
                'accounting_table': 'revenues',
                'detailed_product': 'scooter_per_minute',
                'product': 'scooter_trip_payment',
                'service_id': 1122,
            },
            'scooter_trip_payment_start_fix': {
                'accounting_table': 'revenues',
                'detailed_product': 'scooter_start_fix',
                'product': 'scooter_trip_payment',
                'service_id': 1122,
            },
            'coupon_plus_scooter': {
                'accounting_table': 'revenues',
                'detailed_product': 'coupon_plus_scooter',
                'product': 'coupon_plus_scooter',
                'service_id': 1122,
            },
            'grocery_gross_sales_b2c': {
                'accounting_table': 'grocery_revenues',
                'detailed_product': 'gross_sales_b2c',
                'product': 'gross_sales_b2c',
                'service_id': 663,
            },
            'grocery_delivery_fee_b2c_agent': {
                'accounting_table': 'grocery_agent',
                'detailed_product': 'delivery_fee_b2c_agent',
                'product': 'delivery_fee_b2c_agent',
                'service_id': 663,
            },
            'eats_delivery_fee_cs': {
                'product': 'eats_delivery_fee',
                'service_id': 645,
                'accounting_table': 'eats_revenues',
                'detailed_product': 'delivery_fee_cs',
            },
            'eats_badge_corporate': {
                'product': 'eats_badge_corporate',
                'service_id': 645,
                'accounting_table': 'eats_agent',
                'detailed_product': 'eats_badge_corporate',
            },
            'eats_marketing_promocode_picker': {
                'product': 'eats_marketing_promocode_picker',
                'service_id': 645,
                'accounting_table': 'eats_expenses',
                'detailed_product': 'eats_marketing_promocode_picker',
            },
            'eats_client_service_fee': {
                'product': 'eats_client_service_fee',
                'service_id': 741,
                'accounting_table': 'eats_payments',
                'detailed_product': 'eats_client_service_fee',
            },
            'trip_payment_card': {
                'product': 'trip_payment',
                'service_id': 124,
                'accounting_table': 'payments',
                'detailed_product': 'trip_payment',
            },
        },
        BILLING_GET_MVP_OEBS_ID=True,
        BILLING_DRIVER_MODES_ENABLED=True,
        BILLING_ARBITRARY_ENTRIES_TEMPLATES=[
            {
                'agreement_id': 'taxi/%',
                'entity_external_id': 'taximeter_driver_id/%/%',
                'sub_account': '%',
                'mappers': ['park_entry_mapper', 'driver_balance_mapper'],
                'actions': ['send_to_taximeter'],
                'applied_at': {
                    'begin': '2020-09-20T12:00:00.00000+00:00',
                    'end': '2099-01-01T00:00:00.00000+00:00',
                },
            },
        ],
        BILLING_CALCULATORS_PAYMENTS_WITH_SHARDED_CLIENT_ID=['plus_payment'],
        BILLING_ARBITRARY_PAYOUT_PAYMENTS_WITH_SHARDED_CLIENT_ID=[
            'scooter_trip_payment_per_minute',
            'scooter_trip_payment_start_fix',
            'scooter_trip_payment_insurance',
            'coupon_plus_scooter',
            'grocery_gross_sales_b2c',
        ],
        BILLING_ARBITRARY_ENTRIES_MAPPERS_AND_ACTIONS={
            'actions': [
                {
                    'name': 'send_to_taximeter',
                    'vars': {
                        'alias_id': 'context.alias_id',
                        'driver_uuid': 'context.driver.driver_uuid',
                        'park_id': 'context.driver.park_id',
                        'taximeter_kind': 'context.taximeter_kind',
                    },
                },
                {'name': 'send_balance_update', 'vars': {}},
            ],
            'mappers': [
                {
                    'name': 'park_entry_mapper',
                    'vars': {
                        'alias_id': 'context.alias_id',
                        'driver_uuid': 'context.driver.driver_uuid',
                        'park_id': 'context.driver.park_id',
                    },
                },
                {
                    'name': 'driver_balance_mapper',
                    'vars': {
                        'driver_uuid': 'context.driver.driver_uuid',
                        'park_id': 'context.driver.park_id',
                    },
                },
            ],
        },
        BILLING_CALCULATORS_ADD_TLOG_EXTERNAL_REF=True,
        BILLING_CALCULATORS_ADD_TLOG_TARGET=True,
        **extra,
    )


@pytest.mark.parametrize(
    'test_data_path',
    [
        pytest.param('arbitrary_entries.json', marks=config()),
        pytest.param('arbitrary_entries_with_tags.json', marks=config()),
        pytest.param('arbitrary_entries_no_details.json', marks=config()),
        pytest.param('arbitrary_payout.json', marks=config()),
        pytest.param('arbitrary_payout_lavka_revenues.json', marks=config()),
        pytest.param('arbitrary_payout_scooter.json', marks=config()),
        pytest.param('arbitrary_payout_with_entries.json', marks=config()),
        pytest.param('arbitrary_payout_v2.json', marks=config()),
        pytest.param('arbitrary_payout_v3.json', marks=config()),
        pytest.param('arbitrary_payout_lightbox.json', marks=config()),
        pytest.param('arbitrary_payout_signalq_rent.json', marks=config()),
        pytest.param('arbitrary_payout_payments.json', marks=config()),
        pytest.param('b2b_drive_payment.json', marks=config()),
        pytest.param(
            'b2b_drive_payment_with_contract_id.json', marks=config(),
        ),
        pytest.param('b2b_eda_payment.json', marks=config()),
        pytest.param('b2b_eda_payment_empty_payments.json', marks=config()),
        pytest.param('b2b_eda_payment_with_contract_id.json', marks=config()),
        pytest.param('b2b_client_payment.json', marks=config()),
        pytest.param(
            'b2b_client_payment_tlog_subaccount.json',
            marks=config(
                BILLING_CALCULATORS_B2B_CLIENT_PAYMENT_TLOG_SUBACCOUNT_SINCE=(
                    '2019-01-01T00:00:00+00:00'
                ),
            ),
        ),
        pytest.param('b2b_client_payment_logistics.json', marks=config()),
        pytest.param(
            'b2b_client_payment_on_delivery_logistics.json', marks=config(),
        ),
        pytest.param(
            'b2b_client_payment_decoupling.json',
            marks=config(
                BILLING_CALCULATORS_B2B_CLIENT_PAYMENT_TLOG_SUBACCOUNT_SINCE=(
                    '2019-01-01T00:00:00+00:00'
                ),
            ),
        ),
        pytest.param('b2b_external_partner_payment.json', marks=config()),
        pytest.param('b2b_partner_payment_orders.json', marks=config()),
        pytest.param(
            'b2b_partner_payment_with_rebate.json',
            marks=config(),
            id='no_rebate_request',
        ),
        pytest.param(
            'b2b_partner_payment_with_rebate.json',
            marks=config(
                BILLING_CALCULATORS_B2B_EVENT_REBATE_MIGRATION={
                    'b2b_partner_payment': {
                        '__default__': {
                            'test': [{'since': '1099-09-30T00:10:00+00:00'}],
                        },
                    },
                },
                BILLING_CALCULATORS_PAYMENT_KIND_TO_ADD_REBATE=(
                    _PAYMENT_KIND_TO_REBATE_MAP
                ),
            ),
            id='rebate_from_service_test_only',
        ),
        pytest.param(
            'b2b_partner_payment_with_rebate_from_service.json',
            marks=config(
                BILLING_CALCULATORS_B2B_EVENT_REBATE_MIGRATION={
                    'b2b_partner_payment': {
                        '__default__': {
                            'enabled': [
                                {'since': '1099-09-30T00:10:00+00:00'},
                            ],
                        },
                    },
                },
                BILLING_CALCULATORS_PAYMENT_KIND_TO_ADD_REBATE=(
                    _PAYMENT_KIND_TO_REBATE_MAP
                ),
            ),
            id='rebate_from_service_enabled',
        ),
        pytest.param(
            'b2b_partner_payment_with_rebate_0.04.json',
            marks=config(
                BILLING_CALCULATORS_B2B_EVENT_REBATE_MIGRATION={
                    'b2b_partner_payment': {
                        '__default__': {
                            'enabled': [
                                {'since': '1099-09-30T00:10:00+00:00'},
                            ],
                        },
                    },
                },
                BILLING_CALCULATORS_PAYMENT_KIND_TO_ADD_REBATE=(
                    _PAYMENT_KIND_TO_REBATE_MAP
                ),
            ),
            id='rebate_from_service_enabled_and_have_different_value',
        ),
        pytest.param(
            'b2b_partner_payment_with_rebate_and_park_vat_from_partner.json',
            marks=config(
                BILLING_CALCULATORS_B2B_EVENT_REBATE_MIGRATION={
                    'b2b_partner_payment': {
                        '__default__': {
                            'test': [{'since': '1099-09-30T00:10:00+00:00'}],
                        },
                    },
                },
                BILLING_CALCULATORS_PAYMENT_KIND_TO_ADD_REBATE=(
                    _PAYMENT_KIND_TO_REBATE_MAP
                ),
            ),
            id='rebate_from_partner_with_park_vat',
        ),
        pytest.param(
            'b2b_partner_payment_with_rebate_and_park_vat_from_service.json',
            marks=config(
                BILLING_CALCULATORS_B2B_EVENT_REBATE_MIGRATION={
                    'b2b_partner_payment': {
                        '__default__': {
                            'enabled': [
                                {'since': '1099-09-30T00:10:00+00:00'},
                            ],
                        },
                    },
                },
                BILLING_CALCULATORS_PAYMENT_KIND_TO_ADD_REBATE=(
                    _PAYMENT_KIND_TO_REBATE_MAP
                ),
            ),
            id='rebate_from_service_with_park_vat',
        ),
        pytest.param(
            'b2b_partner_payment_with_rebate.json',
            marks=config(
                BILLING_CALCULATORS_B2B_EVENT_REBATE_MIGRATION={
                    'b2b_partner_payment': {
                        '__default__': {
                            'enabled': [
                                {'since': '2099-09-30T00:10:00+00:00'},
                            ],
                        },
                    },
                },
            ),
            id='rebate_from_service_disabled',
        ),
        pytest.param('b2b_partner_payment_driver_fix.json', marks=config()),
        pytest.param('b2b_partner_payment_logistics.json', marks=config()),
        pytest.param('b2b_trip_payout.json', marks=config()),
        pytest.param('b2b_trip_payout_with_contract_id.json', marks=config()),
        pytest.param('b2b_trip_payout_no_entries.json', marks=config()),
        pytest.param(
            'b2b_user_payment_on_delivery_logistics.json', marks=config(),
        ),
        pytest.param('cashback.json', marks=config()),
        pytest.param('cashback_with_payload.json', marks=config()),
        pytest.param('cashback_with_free_form_payload.json', marks=config()),
        pytest.param('cashback_with_wallet_id.json', marks=config()),
        pytest.param('cashback_with_transaction_type.json', marks=config()),
        pytest.param('childseat_v3.json', marks=config()),
        pytest.param('cargo_childseat.json', marks=config()),
        pytest.param('commission_driver_fix_v3.json', marks=config()),
        pytest.param('commission_driver_fix_fact_v3.json', marks=config()),
        pytest.param(
            'commission_custom_category_tlog_product_v3.json',
            marks=config(BILLING_CALCULATORS_PROCESS_COMMISSION_FEES=True),
        ),
        pytest.param(
            'commission_custom_category_with_total_v3.json',
            marks=config(BILLING_CALCULATORS_PROCESS_COMMISSION_FEES=True),
        ),
        pytest.param('commission_v3.json', marks=config()),
        pytest.param('commission_hiring_v3.json', marks=config()),
        pytest.param('commission_hiring_with_car_v3.json', marks=config()),
        pytest.param(
            'commission_software_subscription_with_total_v3.json',
            marks=config(),
        ),
        pytest.param(
            'commission_software_subscription_wo_total_v3.json',
            marks=config(),
        ),
        pytest.param(
            'commission_software_subscription_with_total_with_vat_v3.json',
            marks=config(),
        ),
        pytest.param(
            'commission_software_subscription_wo_total_with_vat_v3.json',
            marks=config(),
        ),
        pytest.param(
            'commission_with_park_commission_v3.json', marks=config(),
        ),
        pytest.param('driver_partner_v1.json', marks=config()),
        pytest.param('driver_partner_v1_tax.json', marks=config()),
        pytest.param('driver_partner_v1_transfer_order.json', marks=config()),
        pytest.param('driver_referral_v3.json', marks=config()),
        pytest.param(
            'driver_referral_v3_with_contract_id.json', marks=config(),
        ),
        pytest.param('dry_childseat_v3.json', marks=config()),
        pytest.param('dry_driver_referral_v3.json', marks=config()),
        pytest.param('invoice_transaction_cleared.json', marks=config()),
        pytest.param(
            'invoice_transaction_cleared_amount_details.json', marks=config(),
        ),
        pytest.param(
            'invoice_transaction_cleared_amount_details_cargo.json',
            marks=config(),
        ),
        pytest.param(
            'invoice_transaction_cleared_amt_reward.json',
            marks=config(
                BILLING_CALCULATORS_PROCESS_AGENT_COMMISSION_FEES=True,
                BILLING_CALCULATORS_MIN_AGENT_COMMISSION_SETTINGS=[
                    {
                        'start': '2019-01-01T00:00:00+03:00',
                        'settings': {
                            'no_min_value_firm_ids': [1, 2, 3],
                            'firm_settings': {
                                'firm_id': [4, 5, 6],
                                'min_reward': '0.01',
                            },
                            'region_settings': {
                                236: {
                                    'min_cashback_reward': '0.01',
                                    'min_reward': '0',
                                },
                            },
                            'currency_settings': {'KZT': '12', 'AMD': '1'},
                            'default_min_reward': '0.01',
                            'add_vat': [24],
                            'rounding_rules': {'__default__': 4, 'RUB': 2},
                            'ignore_rules': {
                                'payment_kinds': [],
                                'transaction_types': [],
                            },
                        },
                    },
                ],
            ),
        ),
        pytest.param(
            'invoice_transaction_cleared_amt_reward_skip.json',
            marks=config(
                BILLING_CALCULATORS_PROCESS_AGENT_COMMISSION_FEES=True,
                BILLING_CALCULATORS_MIN_AGENT_COMMISSION_SETTINGS=[
                    {
                        'start': '2019-01-01T00:00:00+03:00',
                        'settings': {
                            'no_min_value_firm_ids': [1, 2, 3],
                            'firm_settings': {
                                'firm_id': [4, 5, 6],
                                'min_reward': '0.01',
                            },
                            'region_settings': {
                                236: {
                                    'min_cashback_reward': '0.01',
                                    'min_reward': '0',
                                },
                            },
                            'currency_settings': {'KZT': '12', 'AMD': '1'},
                            'default_min_reward': '0.01',
                            'add_vat': [24],
                            'rounding_rules': {'__default__': 4, 'RUB': 2},
                            'ignore_rules': {
                                'transaction_types': ['refund'],
                                'payment_kinds': ['trip_payment'],
                            },
                        },
                    },
                ],
            ),
        ),
        pytest.param(
            'invoice_transaction_cleared_amt_reward_custom_vat.json',
            marks=config(
                COUNTRY_VAT_BY_DATE={
                    'rus': [
                        {
                            'end': '2070-01-01 00:00:00',
                            'start': '1970-01-01 00:00:00',
                            'value': 11800,
                        },
                    ],
                },
                BILLING_CALCULATORS_PROCESS_AGENT_COMMISSION_FEES=True,
                BILLING_CALCULATORS_MIN_AGENT_COMMISSION_SETTINGS=[
                    {
                        'start': '2019-01-01T00:00:00+03:00',
                        'settings': {
                            'no_min_value_firm_ids': [1, 2, 3],
                            'firm_settings': {
                                'firm_id': [4, 5, 6],
                                'min_reward': '0.01',
                            },
                            'region_settings': {
                                236: {
                                    'min_cashback_reward': '0.01',
                                    'min_reward': '0',
                                },
                            },
                            'currency_settings': {'KZT': '12', 'AMD': '1'},
                            'default_min_reward': '0.01',
                            'add_vat': [24],
                            'rounding_rules': {
                                '__default__': 4,
                                'RUB': 2,
                                'KZT': 1,
                            },
                            'ignore_rules': {
                                'payment_kinds': [],
                                'transaction_types': [],
                            },
                        },
                    },
                ],
            ),
        ),
        pytest.param(
            'invoice_transaction_cleared_amt_reward_rounding_check.json',
            marks=config(
                COUNTRY_VAT_BY_DATE={
                    'rus': [
                        {
                            'end': '2070-01-01 00:00:00',
                            'start': '1970-01-01 00:00:00',
                            'value': 11800,
                        },
                    ],
                },
                BILLING_CALCULATORS_PROCESS_AGENT_COMMISSION_FEES=True,
                BILLING_CALCULATORS_MIN_AGENT_COMMISSION_SETTINGS=[
                    {
                        'start': '2019-01-01T00:00:00+03:00',
                        'settings': {
                            'no_min_value_firm_ids': [1, 2, 3],
                            'firm_settings': {
                                'firm_id': [4, 5, 6],
                                'min_reward': '0.01',
                            },
                            'region_settings': {
                                236: {
                                    'min_cashback_reward': '0.01',
                                    'min_reward': '0',
                                },
                            },
                            'currency_settings': {'KZT': '12', 'AMD': '1'},
                            'default_min_reward': '0.01',
                            'add_vat': [24],
                            'rounding_rules': {
                                '__default__': 4,
                                'RUB': 2,
                                'KZT': 1,
                                'AMD': 0,
                            },
                            'ignore_rules': {
                                'payment_kinds': [],
                                'transaction_types': [],
                            },
                        },
                    },
                ],
            ),
        ),
        pytest.param(
            (
                'invoice_transaction_cleared_amt_reward_'
                'rounding_check_same_as_trust.json'
            ),
            marks=config(
                COUNTRY_VAT_BY_DATE={
                    'rus': [
                        {
                            'end': '2070-01-01 00:00:00',
                            'start': '1970-01-01 00:00:00',
                            'value': 11800,
                        },
                    ],
                },
                BILLING_CALCULATORS_PROCESS_AGENT_COMMISSION_FEES=True,
                BILLING_CALCULATORS_MIN_AGENT_COMMISSION_SETTINGS=[
                    {
                        'start': '2019-01-01T00:00:00+03:00',
                        'settings': {
                            'no_min_value_firm_ids': [1, 2, 3],
                            'firm_settings': {
                                'firm_id': [4, 5, 6],
                                'min_reward': '0.01',
                            },
                            'region_settings': {
                                236: {
                                    'min_cashback_reward': '0.01',
                                    'min_reward': '0',
                                },
                            },
                            'currency_settings': {'KZT': '12', 'AMD': '1'},
                            'default_min_reward': '0.01',
                            'add_vat': [24],
                            'rounding_rules': {
                                '__default__': 4,
                                'RUB': 2,
                                'KZT': 1,
                                'AMD': 0,
                                'USD': 2,
                            },
                            'ignore_rules': {
                                'payment_kinds': [],
                                'transaction_types': [],
                            },
                        },
                    },
                ],
            ),
        ),
        pytest.param('invoice_transaction_cleared_plus.json', marks=config()),
        pytest.param(
            'invoice_transaction_cleared_payment_applepay.json',
            marks=config(),
        ),
        pytest.param(
            'invoice_transaction_cleared_payment_googlepay.json',
            marks=config(),
        ),
        pytest.param(
            'invoice_transaction_cleared_payment_applepay_driver_fix.json',
            marks=config(),
        ),
        pytest.param(
            'invoice_transaction_cleared_payment_googlepay_driver_fix.json',
            marks=config(),
        ),
        pytest.param(
            'invoice_transaction_cleared_tips_card.json', marks=config(),
        ),
        pytest.param(
            'invoice_transaction_cleared_tips_applepay.json', marks=config(),
        ),
        pytest.param(
            'invoice_transaction_cleared_tips_googlepay.json', marks=config(),
        ),
        pytest.param(
            'invoice_transaction_cleared_tips_card_driver_fix.json',
            marks=config(),
        ),
        pytest.param(
            'invoice_transaction_cleared_tips_applepay_driver_fix.json',
            marks=config(),
        ),
        pytest.param(
            'invoice_transaction_cleared_tips_googlepay_driver_fix.json',
            marks=config(),
        ),
        pytest.param('invoice_transaction_cleared_agent.json', marks=config()),
        pytest.param(
            'invoice_transaction_cleared_agent_compensation.json',
            marks=config(),
        ),
        pytest.param(
            'invoice_transaction_cleared_agent_refund_cancel.json',
            marks=config(),
        ),
        pytest.param(
            'invoice_transaction_cleared_agent_driver_fix.json',
            marks=config(),
        ),
        pytest.param(
            'invoice_transaction_cleared_agent_driver_fix_compensation.json',
            marks=config(),
        ),
        pytest.param(
            'invoice_transaction_cleared_agent_driver_fix_refund_cancel.json',
            marks=config(),
        ),
        pytest.param(
            'invoice_transaction_cleared_with_driver_details.json',
            marks=config(),
        ),
        pytest.param('partner_scoring_v1.json', marks=config()),
        pytest.param('park_commission.json', marks=config()),
        pytest.param('park_commission_zero_rate.json', marks=config()),
        pytest.param('partners_payment.json', marks=config()),
        pytest.param('driver_fix_payout.json', marks=config()),
        pytest.param('promocode.json', marks=config()),
        pytest.param('promocode_driver_fix.json', marks=config()),
        pytest.param('promocode_driver_fix_fact.json', marks=config()),
        pytest.param('promocode_no_contract.json', marks=config()),
        pytest.param('cargo_promocode.json', marks=config()),
        pytest.param('promocode_v3.json', marks=config()),
        pytest.param('promocode_v3_no_tags.json', marks=config()),
        pytest.param(
            'promocode_driver_fix_with_two_payments.json', marks=config(),
        ),
        pytest.param('promocode_driver_fix_empty.json', marks=config()),
        pytest.param('scout_v1.json', marks=config()),
        pytest.param('subvention_antifraud_check.json', marks=config()),
        pytest.param(
            'subvention_antifraud_check_with_contract_id.json', marks=config(),
        ),
        pytest.param('subvention_antifraud_decision.json', marks=config()),
        pytest.param(
            'subvention_covid-19_compensation_v3.json', marks=config(),
        ),
        pytest.param('subvention_driver_fix_v3.json', marks=config()),
        pytest.param('subvention_driver_fix_fact_v3.json', marks=config()),
        pytest.param('subvention_revoke_v3.json', marks=config()),
        pytest.param('subvention_v3.json', marks=config()),
        pytest.param('zero_commission.json', marks=config()),
        pytest.param('park_b2b_fixed_commission.json', marks=config()),
        pytest.param('coupon_plus.json', marks=config()),
        pytest.param(
            'grocery_agent.json',
            marks=config(
                BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT={
                    'delivery_fee_b2c_agent': {'payment': 1, 'refund': -1},
                },
            ),
        ),
        pytest.param(
            'grocery_agent_refund.json',
            marks=config(
                BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT={
                    'delivery_fee_b2c_agent': {'payment': 1, 'refund': -1},
                },
            ),
        ),
        pytest.param(
            'grocery_revenues.json',
            marks=config(
                BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT={
                    'gross_sales_b2c': {'payment': 1, 'refund': -1},
                },
            ),
        ),
        pytest.param(
            'grocery_revenues_refund.json',
            marks=config(
                BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT={
                    'gross_sales_b2c': {'payment': 1, 'refund': -1},
                },
            ),
        ),
        pytest.param(
            'eats_revenues.json',
            marks=config(
                BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT={
                    'eats_delivery_fee': {'payment': 1, 'refund': -1},
                },
            ),
        ),
        pytest.param(
            'eats_expenses.json',
            marks=config(
                BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT={
                    'eats_marketing_promocode_picker': {
                        'payment': 1,
                        'refund': -1,
                    },
                },
            ),
        ),
        pytest.param(
            'eats_agent.json',
            marks=config(
                BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT={
                    'eats_badge_corporate': {'payment': 1, 'refund': -1},
                },
            ),
        ),
        pytest.param(
            'eats_payments.json',
            marks=config(
                BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT={
                    'eats_client_service_fee': {'payment': 1, 'refund': -1},
                },
            ),
        ),
    ],
)
# pylint: disable=invalid-name
async def test_convert_to_payout(
        patch_aiohttp_session,
        response_mock,
        test_data_path,
        load_json,
        taxi_billing_calculators_stq_main_ctx,
        mockserver,
):
    @patch_aiohttp_session(discovery.find_service('agglomerations').url, 'GET')
    def _patch_agglomerations_request(*args, **kwargs):
        return response_mock(json={'oebs_mvp_id': 'mvp'})

    ctx = taxi_billing_calculators_stq_main_ctx
    test_data = load_json(test_data_path)

    @mockserver.json_handler('/billing-commissions/v1/rebate/match')
    async def _mock_rebate_match(request, *args, **kwargs):
        return test_data.get('billing_commission_response', {})

    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _parks_retrieve(*args, **kwargs):
        return test_data.get('parks_replica_response')

    @patch_aiohttp_session(
        discovery.find_service('billing_reports').url, 'POST',
    )
    def _patch_billing_reports_request(
            method, url, headers, json_data, **kwargs,
    ):
        if 'docs/select' in url:
            result = []
            for one_doc in test_data['reports']['docs/select']['docs']:
                if all(
                        one_doc[key] == value
                        for key, value in json_data.items()
                        if key in ('external_obj_id', 'kind')
                ):
                    result.append(one_doc)
            return response_mock(json={'docs': result})
        raise NotImplementedError

    @patch_aiohttp_session(
        discovery.find_service('driver-work-modes').url, 'GET',
    )
    def _patch_driver_work_modes_request(
            method, url, headers, params, **kwargs,
    ):
        assert 'park-commission-rate' in url
        return response_mock(
            json={'park_commission_rate': test_data['park_commission_rate']},
        )

    @mockserver.json_handler('/territories/v1/countries/retrieve')
    def _find(request):
        return test_data['territories_response']

    input_doc = calc_models.Doc.from_json(test_data['input_doc'])
    converter_to_payout = converter.get_converter_to_payout(input_doc.kind)
    actual_payout = None
    try:
        actual_payout = await converter_to_payout(input_doc, ctx, None)
    except handling_exceptions.FinishHandling:
        pass
    json_actual_payout = (
        _convert_payout_to_json(actual_payout) if actual_payout else {}
    )
    ordered_object.assert_eq(
        json_actual_payout, test_data['expected_payout'], paths=['entries'],
    )

    # test entries filters and all required fields specified
    journal_entries = []
    if actual_payout:
        # check if reversal entries customizer is registered
        customizer = converter.get_reversal_entries_customizer(
            actual_payout.kind,
        )
        assert customizer is not None
        journal_entries = [
            entry.to_journal_entry(default_event_at=actual_payout.event_at)
            for entry in actual_payout.entries
        ]
    expected_tlog_entries_count = test_data['expected_tlog_entries_count']

    tlog_filters = [
        tuple(filter)
        for filter in test_data.get(
            'tlog_entry_filters', filters.TLOG_ENTRIES_FILTERS,
        )
    ]
    _check_tlog_entries(
        journal_entries, expected_tlog_entries_count, tlog_filters,
    )
    # FIXME Doesn't work for arbitrary entries
    expected_taximeter_entries_count = test_data[
        'expected_taximeter_entries_count'
    ]

    _check_entries_for_taximeter(
        journal_entries, expected_taximeter_entries_count,
    )


def _check_tlog_entries(
        journal_entries, expected_tlog_entries_count, tlog_filters,
):
    entries_for_tlog = helper.filter_entries_by_agreement_and_kind(
        entries=journal_entries, filters=tlog_filters,
    )
    assert len(entries_for_tlog) == expected_tlog_entries_count
    # ok, if can convert to tlog records
    tlog_records = (
        tlog_store.TLogEntrySchema(strict=True)
        .dump(entries_for_tlog, many=True)
        .data
    )
    assert len(tlog_records) == len(entries_for_tlog)


def _check_entries_for_taximeter(
        journal_entries, expected_taximeter_entries_count,
):
    entries_for_taximeter = helper.filter_entries_by_agreement_and_kind(
        entries=journal_entries, filters=filters.TAXIMETER_ENTRIES_FILTERS,
    )
    entries_for_taximeter = (
        helper.filter_exclude_park_entries_except_platform_order_commission(
            entries=entries_for_taximeter,
        )
    )
    entries_for_taximeter = (
        helper.filter_exclude_yandex_ride_park_commission_entries(
            entries=entries_for_taximeter,
        )
    )
    assert len(entries_for_taximeter) == expected_taximeter_entries_count


@pytest.mark.parametrize(
    'test_data_path',
    [
        'b2b_trip_payout.json',
        'invoice_transaction_cleared.json',
        'partners_payment.json',
        'subvention.json',
        'subvention_antifraud.json',
        'subvention_antifraud_no_reversal_data.json',
        'commission.json',
        'childseat.json',
        'dry_childseat.json',
        'promocode.json',
        'cashback.json',
        'park_commission.json',
        'b2b_eda_payment.json',
        'b2b_client_payment.json',
        'b2b_drive_payment.json',
        'b2b_external_partner_payment.json',
        'b2b_partner_payment.json',
        'b2b_user_payment.json',
    ],
)
# pylint: disable=invalid-name
async def test_reversal_entries_customizers(test_data_path, load_json):
    test_data = load_json(test_data_path)
    reversal_entries = [
        calc_models.FlatJournalEntry.from_json(entry)
        for entry in test_data['reversal_entries']
    ]
    payout = models.Payout.from_json(test_data['payout'])

    customizer = converter.get_reversal_entries_customizer(payout.kind)
    customizer(reversal_entries=reversal_entries, payout=payout)
    reversal_entries_json = [entry.to_json() for entry in reversal_entries]
    assert reversal_entries_json == test_data['expected_customized_entries']


@pytest.mark.parametrize(
    'test_data_path, send_zero_entries',
    [
        ('subvention.json', False),
        ('promocode.json', False),
        ('childseat.json', False),
        ('dry_childseat.json', False),
        ('commission_driver_fix.json', False),
        ('park_commission_driver_fix.json', False),
        ('zero_commission.json', False),
        ('zero_commission_send_zero_entries.json', True),
        ('workshift.json', True),
    ],
)
# pylint: disable=invalid-name
async def test_taximeter_builders(
        test_data_path, load_json, send_zero_entries,
):
    test_data = load_json(test_data_path)
    input_entries = [
        calc_models.FlatJournalEntry.from_json(entry)
        for entry in test_data['input_entries']
    ]
    taximeter_payload = models.TaximeterRequestPayload.from_json(
        test_data['taximeter_request_payload'],
    )

    # check build taximeter payments
    taximeter_payments_builder = (
        taximeter_builders.get_taximeter_payments_builder(
            taximeter_payload.kind,
        )
    )
    taximeter_payments = taximeter_payments_builder(
        entries=input_entries,
        request_payload=taximeter_payload,
        send_zero_entries=send_zero_entries,
    )
    payments_json = [entry.to_json() for entry in taximeter_payments]
    assert payments_json == test_data['expected_taximeter_payments']


def _convert_payout_to_json(self):
    def format_fn(func):
        if hasattr(func, 'func'):
            # functools.partial wrapped
            return {
                'func': func.func.__name__,
                'keywords': json.loads(util.to_json(func.keywords)),
            }
        return {'func': func.__name__, 'keywords': {}}

    data = {
        'kind': self.kind,
        'event_at': dates.format_datetime(self.event_at),
        'payout_doc_id': self.payout_doc_id,
        'base_doc_id': self.base_doc_id,
        'external_obj_id': self.external_obj_id,
        'entries': [entry.to_json() for entry in self.entries],
        'version': self.version,
        'topic_begin_at': dates.format_datetime(self.topic_begin_at),
        'tags': self.tags,
        'post_processing_actions': [
            format_fn(action) for action in self.post_processing_actions
        ],
        'dry_mode': self.dry_mode,
    }
    if self.reversal_data is not None:
        data['reversal_data'] = self.reversal_data
    return data
