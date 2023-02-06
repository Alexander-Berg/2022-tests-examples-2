# pylint: disable=too-many-lines
import copy

import pytest

from taxi import discovery
from taxi.billing import resource_limiter

from taxi_billing_orders import config as orders_config
from taxi_billing_orders.resource_classifiers import (
    v2_process_async_classifier as res_cls,
)

ENTRIES_TEMPLATES = [
    {
        'agreement_id': 'taxi/%',
        'entity_external_id': 'taximeter_driver_id/%/%',
        'sub_account': '%',
        'mappers': ['park_entry_mapper'],
        'actions': ['send_to_taximeter'],
        'applied_at': {
            'begin': '2020-09-20T12:00:00.00000+00:00',
            'end': '2099-01-01T00:00:00.00000+00:00',
        },
    },
]
ENTRIES_MAPPERS_AND_ACTIONS = {
    'actions': [{'name': 'send_to_taximeter', 'vars': {}}],
    'mappers': [
        {
            'name': 'park_entry_mapper',
            'vars': {
                'alias_id': 'context.alias_id',
                'driver_uuid': 'context.driver.driver_uuid',
            },
        },
    ],
}

BILLING_REMITTANCE_ORDER_SETTINGS_BY_TRANSFER_TYPE = {
    'lightbox_rent': {
        'sender_service_id': 124,
        'recipient_service_id': 222,
        'request_type': 'TRANSFER_ORDER',
    },
    'signalq_rent': {
        'sender_service_id': 124,
        'recipient_service_id': 124,
        'request_type': 'OTHER_REVENUE',
    },
    'store_payment': {
        'sender_service_id': 124,
        'recipient_service_id': 222,
        'request_type': 'TRANSFER_ORDER',
    },
}

PAYOUT_PAYMENTS_SETTINGS = {
    'b2b_agent_logistics_expense': {
        'accounting_table': 'expenses',
        'detailed_product': 'b2b_agent_logistics_expense',
        'product': 'b2b_agent_logistics_expense',
        'service_id': 719,
    },
    'b2b_agent_logistics_revenue': {
        'accounting_table': 'revenues',
        'detailed_product': 'b2b_agent_logistics_revenue',
        'product': 'b2b_agent_logistics_revenue',
        'service_id': 718,
    },
    'b2b_agent_taxi_expense': {
        'accounting_table': 'expenses',
        'detailed_product': 'b2b_agent_taxi_expense',
        'product': 'b2b_agent_taxi_expense',
        'service_id': 651,
    },
    'b2b_agent_taxi_revenue': {
        'accounting_table': 'revenues',
        'detailed_product': 'b2b_agent_taxi_revenue',
        'product': 'b2b_agent_taxi_revenue',
        'service_id': 650,
    },
    'b2b_client_agent_payment': {
        'accounting_table': 'revenues',
        'detailed_product': 'b2b_client_agent_payment',
        'product': 'b2b_client_agent_payment',
        'service_id': 1183,
    },
    'b2b_client_agent_reward': {
        'accounting_table': 'revenues',
        'detailed_product': 'b2b_client_agent_reward',
        'product': 'b2b_client_agent_reward',
        'service_id': 1181,
    },
    'b2b_park_agent_payment': {
        'accounting_table': 'expenses',
        'detailed_product': 'b2b_park_agent_payment',
        'product': 'b2b_park_agent_payment',
        'service_id': 1182,
    },
    'b2b_tanker_payment': {
        'accounting_table': 'payments',
        'detailed_product': 'b2b_tanker_payment',
        'product': 'b2b_tanker_payment',
        'service_id': 636,
    },
    'b2b_taxi_tanker_revenue': {
        'accounting_table': 'revenues',
        'detailed_product': 'b2b_taxi_tanker_revenue',
        'product': 'b2b_tanker_revenue',
        'service_id': 650,
    },
    'b2b_user_on_delivery_payment_fee': {
        'accounting_table': 'revenues',
        'detailed_product': 'b2b_user_on_delivery_payment_fee',
        'product': 'b2b_user_on_delivery_payment_fee',
        'service_id': 718,
    },
    'cargo_client_b2b_logistics_payment': {
        'accounting_table': 'revenues',
        'detailed_product': 'cargo_client_b2b_logistics_payment',
        'product': 'cargo_client_b2b_logistics_payment',
        'service_id': 718,
    },
    'cargo_client_b2b_trip_payment': {
        'accounting_table': 'revenues',
        'detailed_product': 'client_b2b_trip_payment',
        'product': 'cargo_client_b2b_trip_payment',
        'service_id': 650,
    },
    'cargo_multi_client_b2b_trip_payment': {
        'accounting_table': 'revenues',
        'detailed_product': 'multi_client_b2b_trip_payment',
        'product': 'cargo_client_b2b_trip_payment',
        'service_id': 650,
    },
    'cargo_multi_park_b2b_trip_payment': {
        'accounting_table': 'expenses',
        'detailed_product': 'multi_park_b2b_trip_payment',
        'product': 'cargo_park_b2b_trip_payment',
        'service_id': 651,
    },
    'cargo_multi_rebate_park_b2b_trip_payment': {
        'accounting_table': 'expenses',
        'detailed_product': 'multi_rebate_b2b_trip_payment',
        'product': 'cargo_park_b2b_trip_payment',
        'service_id': 651,
    },
    'cargo_park_b2b_logistics_payment_test': {
        'accounting_table': 'expenses',
        'detailed_product': 'delivery_park_b2b_logistics_payment_test',
        'product': 'delivery_park_b2b_logistics_payment',
        'service_id': 719,
    },
    'cargo_park_rebate_b2b_logistics_payment_test': {
        'accounting_table': 'expenses',
        'detailed_product': 'cargo_park_rebate_b2b_logistics_payment_test',
        'product': 'cargo_park_b2b_logistics_payment',
        'service_id': 719,
    },
    'client_b2b_drive_discount': {
        'accounting_table': 'revenues',
        'detailed_product': 'drive_client_b2b_discount',
        'product': 'client_b2b_discount',
        'service_id': 672,
    },
    'client_b2b_drive_payment': {
        'accounting_table': 'revenues',
        'detailed_product': 'client_b2b_drive_payment',
        'product': 'client_b2b_drive_payment',
        'service_id': 672,
    },
    'client_b2b_eats_discount': {
        'accounting_table': 'revenues',
        'detailed_product': 'eats_b2b_client_discount',
        'product': 'client_b2b_discount',
        'service_id': 668,
    },
    'client_b2b_taxi_discount': {
        'accounting_table': 'revenues',
        'detailed_product': 'taxi_client_b2b_discount',
        'product': 'client_b2b_discount',
        'service_id': 650,
    },
    'client_b2b_trip_payment': {
        'accounting_table': 'revenues',
        'detailed_product': 'client_b2b_trip_payment',
        'product': 'client_b2b_trip_payment',
        'service_id': 650,
    },
    'coupon_plus_scooter': {
        'accounting_table': 'revenues',
        'detailed_product': 'coupon_plus_scooter',
        'product': 'coupon_plus_scooter',
        'service_id': 1122,
    },
    'decoupling_client_b2b_trip_payment': {
        'accounting_table': 'revenues',
        'detailed_product': 'decoupling_b2b_trip_payment',
        'product': 'client_b2b_trip_payment',
        'service_id': 650,
    },
    'delivery_client_b2b_logistics_payment': {
        'accounting_table': 'revenues',
        'detailed_product': 'delivery_client_b2b_logistics_payment',
        'product': 'delivery_client_b2b_logistics_payment',
        'service_id': 718,
    },
    'delivery_multi_client_b2b_trip_payment': {
        'accounting_table': 'revenues',
        'detailed_product': 'multi_client_b2b_trip_payment',
        'product': 'delivery_client_b2b_trip_payment',
        'service_id': 650,
    },
    'delivery_park_b2b_logistics_payment_test': {
        'accounting_table': 'expenses',
        'detailed_product': 'delivery_park_b2b_logistics_payment_test',
        'product': 'delivery_park_b2b_logistics_payment',
        'service_id': 719,
    },
    'delivery_park_rebate_b2b_logistics_payment_test': {
        'accounting_table': 'expenses',
        'detailed_product': 'delivery_park_rebate_b2b_logistics_payment_test',
        'product': 'delivery_park_b2b_logistics_payment',
        'service_id': 719,
    },
    'discount_grocery_item_sale_vat_0': {
        'accounting_table': 'revenues',
        'product': 'grocery_item_sale_vat_0',
        'detailed_product': 'discount',
        'service_id': 663,
    },
    'discount_grocery_item_sale_vat_17': {
        'accounting_table': 'revenues',
        'product': 'grocery_item_sale_vat_17',
        'detailed_product': 'discount',
        'service_id': 663,
    },
    'dooh_bonus': {
        'accounting_table': 'expenses',
        'product': 'dooh_bonus',
        'detailed_product': 'dooh_bonus',
        'service_id': 724,
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
    'eats_badge_corporate': {
        'product': 'eats_badge_corporate',
        'service_id': 645,
        'accounting_table': 'eats_agent',
        'detailed_product': 'eats_badge_corporate',
    },
    'eats_client_service_fee': {
        'product': 'eats_client_service_fee',
        'service_id': 721,
        'accounting_table': 'eats_payments',
        'detailed_product': 'eats_client_service_fee',
    },
    'eats_delivery_fee_cs': {
        'product': 'eats_delivery_fee',
        'service_id': 645,
        'accounting_table': 'eats_revenues',
        'detailed_product': 'delivery_fee_cs',
    },
    'eats_inplace_commission_cashback_payback': {
        'product': 'eats_cashback_payback',
        'service_id': 1177,
        'accounting_table': 'eats_revenues',
        'detailed_product': 'eats_cashback_payback',
    },
    'eats_marketing_promocode_picker': {
        'product': 'eats_marketing_promocode_picker',
        'service_id': 645,
        'accounting_table': 'eats_expenses',
        'detailed_product': 'eats_marketing_promocode_picker',
    },
    'external_delivery_b2b_logistics_payment': {
        'accounting_table': 'expenses',
        'detailed_product': 'external_delivery_b2b_logistics_payment',
        'product': 'external_delivery_b2b_logistics_payment',
        'service_id': 719,
    },
    'food_payment': {
        'accounting_table': 'revenues',
        'detailed_product': 'food_payment',
        'product': 'food_payment',
        'service_id': 668,
    },
    'grocery_coupon_plus': {
        'product': 'coupon_plus',
        'service_id': 663,
        'accounting_table': 'grocery_revenues',
        'detailed_product': 'coupon_plus',
    },
    'grocery_courier_coupon': {
        'accounting_table': 'expenses',
        'product': 'grocery_courier_coupon',
        'detailed_product': 'grocery_courier_coupon',
        'service_id': 664,
    },
    'grocery_courier_delivery': {
        'accounting_table': 'expenses',
        'product': 'grocery_courier_delivery',
        'detailed_product': 'grocery_courier_delivery',
        'service_id': 664,
    },
    'grocery_delivery_fee_b2c_agent': {
        'product': 'delivery_fee_b2c_agent',
        'service_id': 663,
        'accounting_table': 'grocery_agent',
        'detailed_product': 'delivery_fee_b2c_agent',
    },
    'grocery_delivery_fee_b2c_principal': {
        'product': 'delivery_fee_b2c_principal',
        'service_id': 663,
        'accounting_table': 'grocery_revenues',
        'detailed_product': 'delivery_fee_b2c_principal',
    },
    'grocery_delivery_fee_commission': {
        'product': 'delivery_fee_commission',
        'service_id': 663,
        'accounting_table': 'grocery_agent',
        'detailed_product': 'delivery_fee_commission',
    },
    'grocery_gross_sales_b2c': {
        'accounting_table': 'grocery_revenues',
        'detailed_product': 'gross_sales_b2c',
        'product': 'gross_sales_b2c',
        'service_id': 663,
    },
    'grocery_incentives_b2c_discount': {
        'product': 'incentives_b2c',
        'service_id': 663,
        'accounting_table': 'grocery_revenues',
        'detailed_product': 'incentives_b2c_discount',
    },
    'grocery_incentives_b2c_marketing_coupon': {
        'product': 'incentives_b2c',
        'service_id': 663,
        'accounting_table': 'grocery_revenues',
        'detailed_product': 'incentives_b2c_marketing_coupon',
    },
    'grocery_incentives_b2c_support_coupon': {
        'product': 'incentives_b2c',
        'service_id': 663,
        'accounting_table': 'grocery_revenues',
        'detailed_product': 'incentives_b2c_support_coupon',
    },
    'grocery_item_sale_vat_0': {
        'accounting_table': 'revenues',
        'product': 'grocery_item_sale_vat_0',
        'detailed_product': 'grocery_item_sale_vat_0',
        'service_id': 663,
    },
    'grocery_item_sale_vat_17': {
        'accounting_table': 'revenues',
        'product': 'grocery_item_sale_vat_17',
        'detailed_product': 'grocery_item_sale_vat_17',
        'service_id': 663,
    },
    'grocery_tips_b2c_agent': {
        'product': 'tips_b2c_agent',
        'service_id': 663,
        'accounting_table': 'grocery_agent',
        'detailed_product': 'tips_b2c_agent',
    },
    'grocery_tips_b2c_principal': {
        'product': 'tips_b2c_principal',
        'service_id': 663,
        'accounting_table': 'grocery_revenues',
        'detailed_product': 'tips_b2c_principal',
    },
    'grocery_tips_vat_17': {
        'accounting_table': 'revenues',
        'product': 'grocery_tips_vat_17',
        'detailed_product': 'grocery_tips_vat_17',
        'service_id': 663,
    },
    'lead_fee': {
        'accounting_table': 'revenues',
        'product': 'lead_fee',
        'detailed_product': 'lead_fee',
        'service_id': 128,
    },
    'marketplace_lukoil_oil_0w30': {
        'accounting_table': 'revenues',
        'detailed_product': 'lukoil_oil_0w30',
        'product': 'lukoil_oil_0w30',
        'service_id': 1130,
    },
    'marketplace_lukoil_oil_5w30': {
        'accounting_table': 'revenues',
        'detailed_product': 'lukoil_oil_5w30',
        'product': 'lukoil_oil_5w30',
        'service_id': 1130,
    },
    'marketplace_lukoil_oil_5w40': {
        'accounting_table': 'revenues',
        'detailed_product': 'lukoil_oil_5w40',
        'product': 'lukoil_oil_5w40',
        'service_id': 1130,
    },
    'park_b2b_trip_payment': {
        'accounting_table': 'expenses',
        'detailed_product': 'park_b2b_trip_payment',
        'product': 'park_b2b_trip_payment',
        'service_id': 651,
    },
    'park_rebate_b2b_trip_payment': {
        'accounting_table': 'expenses',
        'detailed_product': 'rebate_b2b_trip_payment',
        'product': 'park_b2b_trip_payment',
        'service_id': 651,
    },
    'partner_scoring': {
        'accounting_table': 'revenues',
        'detailed_product': 'partner_scoring',
        'product': 'partner_scoring',
        'service_id': 128,
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
    'scout': {
        'accounting_table': 'expenses',
        'detailed_product': 'scout',
        'product': 'scout',
        'service_id': 619,
    },
    'scout_sz': {
        'accounting_table': 'expenses',
        'detailed_product': 'scout_sz',
        'product': 'scout_sz',
        'service_id': 619,
    },
    'services_gross_commission_water': {
        'accounting_table': 'revenues',
        'detailed_product': 'services_gross_commission_water',
        'product': 'services_order',
        'service_id': 1215,
    },
    'services_marketing_coupon_compensation': {
        'accounting_table': 'expenses',
        'detailed_product': 'services_marketing_coupon_compensation',
        'product': 'services_coupon',
        'service_id': 1175,
    },
    'services_payment': {
        'accounting_table': 'payments',
        'detailed_product': 'services_payment',
        'product': 'services_payment',
        'service_id': 1208,
    },
    'signalq_monitoring_fee': {
        'accounting_table': 'revenues',
        'detailed_product': 'signalq_monitoring_fee',
        'product': 'signalq_monitoring_fee',
        'service_id': 128,
    },
    'subsidy_store_refund': {
        'accounting_table': 'expenses',
        'detailed_product': 'subsidy_store_refund',
        'product': 'subsidy',
        'service_id': 137,
    },
    'trip_payment_card': {
        'accounting_table': 'payments',
        'detailed_product': 'trip_payment',
        'product': 'trip_payment',
        'service_id': 124,
    },
    'truck_client_trip_payment': {
        'accounting_table': 'payments',
        'detailed_product': 'truck_client_trip_payment',
        'product': 'truck_client_trip_payment',
        'service_id': 1191,
    },
}

TLOG_AGGREGATION_SIGN_BY_PRODUCT = {
    'b2b_agent_logistics_revenue': {'payment': 1, 'refund': -1},
    'b2b_agent_taxi_revenue': {'payment': 1, 'refund': -1},
    'b2b_tanker_revenue': {'payment': 1, 'refund': -1},
    'client_b2b_discount': {'payment': -1, 'refund': 1},
    'coupon_plus': {'payment': -1, 'refund': 1},
    'coupon_plus_scooter': {'payment': -1, 'refund': 1},
    'delivery_fee_b2c_agent': {'payment': 1, 'refund': -1},
    'delivery_fee_b2c_principal': {'refund': -1, 'payment': 1},
    'delivery_fee_commission': {'payment': 1, 'refund': -1},
    'eats_badge_corporate': {'payment': 1, 'refund': -1},
    'eats_cashback_payback': {'payment': 1, 'refund': -1},
    'eats_client_service_fee': {'payment': 1, 'refund': -1},
    'eats_delivery_fee': {'payment': 1, 'refund': -1},
    'eats_marketing_promocode_picker': {'payment': 1, 'refund': -1},
    'grocery_item_sale_vat_0': {'payment': 1, 'refund': -1},
    'grocery_item_sale_vat_17': {'payment': 1, 'refund': -1},
    'grocery_tips_vat_17': {'payment': 1, 'refund': -1},
    'gross_sales_b2c': {'payment': 1, 'refund': -1},
    'incentives_b2c': {'refund': 1, 'payment': -1},
    'lead_fee': {'payment': 1, 'refund': -1},
    'lukoil_oil_0w30': {'payment': 1, 'refund': -1},
    'lukoil_oil_5w30': {'payment': 1, 'refund': -1},
    'lukoil_oil_5w40': {'payment': 1, 'refund': -1},
    'scooter_trip_payment': {'payment': 1, 'refund': -1},
    'services_order': {'payment': 1, 'refund': -1},
    'signalq_monitoring_fee': {'payment': 1, 'refund': -1},
    'tips_b2c_agent': {'payment': 1, 'refund': -1},
    'tips_b2c_principal': {'refund': 1, 'payment': -1},
}


@pytest.mark.config(
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
    BILLING_ARBITRARY_ENTRIES_TEMPLATES=ENTRIES_TEMPLATES,
    BILLING_ARBITRARY_ENTRIES_MAPPERS_AND_ACTIONS=ENTRIES_MAPPERS_AND_ACTIONS,
    BILLING_PAYOUT_PAYMENTS_SETTINGS=PAYOUT_PAYMENTS_SETTINGS,
    BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT=TLOG_AGGREGATION_SIGN_BY_PRODUCT,
    TVM_ENABLED=True,
    BILLING_PAYOUTS_VALIDATE_CONTRACTS='enable',
    BILLING_REMITTANCE_ORDER_SETTINGS_BY_TRANSFER_TYPE=(
        BILLING_REMITTANCE_ORDER_SETTINGS_BY_TRANSFER_TYPE
    ),
    BILLING_ORDERS_DISABLE_CONTRACT_CHECK=[
        'grocery_courier_coupon',
        'grocery_courier_delivery',
        'eats_inplace_commission_cashback_payback',
    ],
)
@pytest.mark.parametrize(
    'test_data_path',
    [
        'account_update.json',
        'arbitrary_entries.json',
        'arbitrary_entries_no_details.json',
        'arbitrary_entries_with_tags.json',
        'arbitrary_payout.json',
        'arbitrary_payout_b2b_agent_taxi_logistics.json',
        'arbitrary_payout_b2b_tanker_payment.json',
        'arbitrary_payout_b2b_tanker_revenue.json',
        'arbitrary_payout_duplicate_payments.json',
        'arbitrary_payout_grocery_sales.json',
        'arbitrary_payout_lead_fee.json',
        'arbitrary_payout_lightbox.json',
        'arbitrary_payout_no_check_contracts.json',
        'arbitrary_payout_no_contract.json',
        'arbitrary_payout_payments.json',
        'arbitrary_payout_scooter.json',
        'arbitrary_payout_scout.json',
        'arbitrary_payout_services.json',
        'arbitrary_payout_subsidy_store_refund.json',
        'arbitrary_payout_trunks_payments.json',
        'arbitrary_payout_v2.json',
        'arbitrary_payout_v3.json',
        'arbitrary_payout_wrong_grocery_courier.json',
        'b2b_agent_orders_inc_firm_id.json',
        'b2b_client_discount.json',
        'b2b_client_payment.json',
        'b2b_client_payment_logistics.json',
        'b2b_client_payment_no_contract.json',
        'b2b_client_payment_on_delivery_logistics.json',
        'b2b_client_payment_test_trip.json',
        'b2b_drive_payment.json',
        'b2b_eda_payment.json',
        'b2b_external_partner_payment.json',
        'b2b_orders_inc_firm_id.json',
        'b2b_partner_payment.json',
        'b2b_partner_payment_logistics.json',
        'b2b_partner_payment_logistics_with_rebate.json',
        'b2b_partner_payment_no_contract.json',
        'b2b_partner_payment_with_rebate.json',
        'b2b_trip_payout.json',
        'b2b_user_payment_on_delivery_logistics.json',
        'cargo_claim.json',
        'cargo_order.json',
        'cargo_order_with_claims.json',
        'cargo_promocode.json',
        'cashback.json',
        'cashback_with_free_form_payload.json',
        'cashback_with_payload.json',
        'cashback_with_transaction_type_payment.json',
        'cashback_with_transaction_type_refund.json',
        'cashback_with_wallet_id.json',
        'childseat_v3.json',
        'commission_v3.json',
        'driver_fix_docs.json',
        'driver_partner_raw_v1.json',
        'driver_partner_v1.json',
        'driver_referral_v3.json',
        'dry_promocode.json',
        'eats_agent.json',
        'eats_expenses.json',
        'eats_payments.json',
        'eats_revenues.json',
        'fine.json',
        'grocery_agent.json',
        'grocery_agent_invalid_contract_id.json',
        'grocery_revenues.json',
        'grocery_revenues_invalid_contract_id.json',
        'grocery_revenues_skip_contract_validation.json',
        'invoice_transaction_cleared.json',
        'invoice_transaction_cleared_agent.json',
        'invoice_transaction_cleared_with_driver_details.json',
        'lukoil_revenues.json',
        'park_commission.json',
        'partner_scoring.json',
        'partners_payment.json',
        'partners_payment_wrong_amount.json',
        'payment_order.json',
        'periodic_payment.json',
        'periodic_payment_cancel.json',
        'periodic_payment_cancel_confirm.json',
        'periodic_payment_cancel_platform.json',
        'periodic_payment_confirm.json',
        'periodic_payment_reject.json',
        'personal_wallet_charge.json',
        'personal_wallet_charge_v2.json',
        'personal_wallet_charge_with_order_completed_at.json',
        'personal_wallet_topup.json',
        'personal_wallet_topup_negative_amount.json',
        'personal_wallet_topup_refund.json',
        'personal_wallet_transfer.json',
        'personal_wallet_transfer_different_currencies.json',
        'promocode.json',
        'promocode_v3.json',
        'promocode_v3_personal_wallet.json',
        'promocode_v3_personal_wallet_expense.json',
        'remittance_order.json',
        'remittance_order_cancel.json',
        'remittance_order_confirm.json',
        'remittance_order_confirm_v2.json',
        'remittance_order_signalq_rent.json',
        'remittance_order_store_payment.json',
        'scout.json',
        'shuttle_order.json',
        'signalq_monitoring_fee.json',
        'subvention_antifraud_check.json',
        'subvention_antifraud_decision.json',
        'subvention_revoke_v3.json',
        'subvention_v3.json',
        'subvention_v3_with_driver_income_payload.json',
        'transfer_order.json',
        'transfer_order_cancel.json',
        'eats_order.json',
    ],
)
async def test_v2_process_async(
        test_data_path,
        load_py_json_dir,
        request_headers,
        patch_aiohttp_session,
        patch,
        response_mock,
        mockserver,
        patched_tvm_ticket_check,
        taxi_billing_orders_client,
        monkeypatch,
):
    data = load_py_json_dir('test_v2_process_async', test_data_path)

    next_doc_id: int = 1002

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        nonlocal next_doc_id
        assert 'create' in url
        resp = {'doc_id': next_doc_id, 'kind': json['kind']}
        next_doc_id += 1
        return response_mock(json=resp)

    @patch_aiohttp_session(
        discovery.find_service('billing_calculators').url, 'POST',
    )
    def _patch_billing_calculators_request(
            method, url, headers, json, **kwargs,
    ):
        return response_mock(json=json)

    @patch('taxi.clients.stq_agent.StqAgentClient.put_task')
    async def _patch_stq_client_put(
            queue, eta=None, task_id=None, args=None, kwargs=None,
    ):
        return

    actual_contracts_to_check = []

    @mockserver.json_handler('/billing-replication/v1/check_contracts/')
    def _check_contracts(request):
        actual_contracts_to_check.extend(request.json['contracts'])
        check_contracts = copy.deepcopy(request.json['contracts'])
        for contract in check_contracts:
            contract['is_valid'] = True
        return {'contracts': check_contracts}

    response = await taxi_billing_orders_client.post(
        '/v2/process/async', headers=request_headers, json=data['request'],
    )
    text = await response.text()
    assert response.status == data['response_status'], text

    assert len(_patch_billing_docs_request.calls) == data['docs_calls']
    assert len(_patch_billing_calculators_request.calls) == data['calc_calls']
    stq_calls = data.get('stq_calls')
    if stq_calls:
        assert len(_patch_stq_client_put.calls) == stq_calls['count']
        for call in _patch_stq_client_put.calls:
            assert call['queue'] == stq_calls['queue']

    if 'response_text' in data:
        assert text == data['response_text']

    check_json_response = data.get('check_json_response', True)
    if check_json_response:
        content = await response.json()
        assert content == data['response']
    if data.get('contracts_to_check') is not None:

        def _sort_contracts(contracts):
            return sorted(
                contracts,
                key=lambda contract: (
                    contract['client_id'],
                    contract['contract_id'],
                    contract['service_id'],
                    contract['currency'],
                ),
            )

        assert _sort_contracts(actual_contracts_to_check) == _sort_contracts(
            data['contracts_to_check'],
        )


@pytest.mark.config(
    TVM_ENABLED=True,
    BILLING_PAYOUTS_VALIDATE_CONTRACTS='disable',
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
)
@pytest.mark.parametrize(
    'test_data_path', ['orders_with_spent_resources.json'],
)
async def test_v2_process_async_resources(
        test_data_path,
        load_py_json_dir,
        request_headers,
        patch_aiohttp_session,
        patch,
        response_mock,
        patched_tvm_ticket_check,
        taxi_billing_orders_client,
        monkeypatch,
):
    data = load_py_json_dir('test_v2_process_async', test_data_path)

    next_doc_id: int = 1002

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        nonlocal next_doc_id
        assert 'create' in url
        resp = {'doc_id': next_doc_id, 'kind': json['kind']}
        next_doc_id += 1
        return response_mock(json=resp)

    @patch_aiohttp_session(
        discovery.find_service('billing_calculators').url, 'POST',
    )
    def _patch_billing_calculators_request(
            method, url, headers, json, **kwargs,
    ):
        return response_mock(json=json)

    requested_resources = []

    @patch('taxi.billing.resource_limiter.ResourceLimiter.request_resources')
    def _request_resources(
            client_tvm_service_name, required_resources, log_extra,
    ):
        requested_resources.extend(required_resources)

    response = await taxi_billing_orders_client.post(
        '/v2/process/async', headers=request_headers, json=data['request'],
    )

    spent_resources = await (
        res_cls.V2ProcessAsyncResourceClassifier().get_spent_resources(
            response,
        )
    )
    _compare_resources(requested_resources, spent_resources, data)


@pytest.mark.config(
    BILLING_ARBITRARY_ENTRIES_TEMPLATES=ENTRIES_TEMPLATES,
    BILLING_ARBITRARY_ENTRIES_MAPPERS_AND_ACTIONS=ENTRIES_MAPPERS_AND_ACTIONS,
    BILLING_PAYOUT_PAYMENTS_SETTINGS=PAYOUT_PAYMENTS_SETTINGS,
    BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT=TLOG_AGGREGATION_SIGN_BY_PRODUCT,
    TVM_ENABLED=True,
    BILLING_PAYOUTS_VALIDATE_CONTRACTS='enable',
    BILLING_REMITTANCE_ORDER_SETTINGS_BY_TRANSFER_TYPE=(
        BILLING_REMITTANCE_ORDER_SETTINGS_BY_TRANSFER_TYPE
    ),
)
@pytest.mark.parametrize(
    'test_data_path',
    [
        'account_update.json',
        'arbitrary_entries.json',
        'arbitrary_entries_with_tags.json',
        'arbitrary_entries_no_details.json',
        'arbitrary_payout.json',
        'arbitrary_payout_grocery_sales.json',
        'arbitrary_payout_wrong_grocery_courier.json',
        'arbitrary_payout_duplicate_payments.json',
        'arbitrary_payout_v2.json',
        'arbitrary_payout_v3.json',
        'arbitrary_payout_lightbox.json',
        'arbitrary_payout_lead_fee.json',
        'arbitrary_payout_scooter.json',
        'b2b_client_discount.json',
        'b2b_client_payment.json',
        'b2b_client_payment_logistics.json',
        'b2b_client_payment_on_delivery_logistics.json',
        'b2b_client_payment_test_trip.json',
        'b2b_client_payment_no_contract.json',
        'b2b_drive_payment.json',
        'b2b_eda_payment.json',
        'b2b_trip_payout.json',
        'b2b_external_partner_payment.json',
        'b2b_partner_payment.json',
        'b2b_partner_payment_with_rebate.json',
        'b2b_partner_payment_logistics.json',
        'b2b_partner_payment_logistics_with_rebate.json',
        'b2b_user_payment_on_delivery_logistics.json',
        'cargo_claim.json',
        'cargo_order.json',
        'cargo_order_with_claims.json',
        'cashback.json',
        'cashback_with_payload.json',
        'cashback_with_free_form_payload.json',
        'cashback_with_wallet_id.json',
        'cashback_with_transaction_type_payment.json',
        'cashback_with_transaction_type_refund.json',
        'childseat_v3.json',
        'commission_v3.json',
        'driver_fix_docs.json',
        'driver_partner_v1.json',
        'driver_partner_raw_v1.json',
        'driver_partner_raw_v2.json',
        'driver_referral_v3.json',
        'dry_promocode.json',
        'invoice_transaction_cleared.json',
        'invoice_transaction_cleared_with_driver_details.json',
        'invoice_transaction_cleared_agent.json',
        'payment_order.json',
        'park_commission.json',
        'partner_scoring.json',
        'partners_payment.json',
        'partners_payment_wrong_amount.json',
        'personal_wallet_charge.json',
        'personal_wallet_charge_v2.json',
        'personal_wallet_charge_with_order_completed_at.json',
        'personal_wallet_topup.json',
        'personal_wallet_topup_negative_amount.json',
        'personal_wallet_topup_refund.json',
        'personal_wallet_transfer.json',
        'personal_wallet_transfer_different_currencies.json',
        'promocode.json',
        'promocode_v3.json',
        'promocode_v3_personal_wallet.json',
        'periodic_payment.json',
        'periodic_payment_confirm.json',
        'periodic_payment_cancel.json',
        'periodic_payment_cancel_platform.json',
        'periodic_payment_cancel_confirm.json',
        'periodic_payment_reject.json',
        'subvention_antifraud_check.json',
        'subvention_antifraud_decision.json',
        'subvention_v3.json',
        'subvention_revoke_v3.json',
        'scout.json',
        'transfer_order.json',
        'transfer_order_cancel.json',
        'remittance_order.json',
        'remittance_order_cancel.json',
        'remittance_order_confirm.json',
        'remittance_order_signalq_rent.json',
        'remittance_order_store_payment.json',
        'arbitrary_payout_no_contract.json',
        'arbitrary_payout_no_check_contracts.json',
        'b2b_partner_payment_no_contract.json',
        'grocery_agent.json',
        'grocery_agent_invalid_contract_id.json',
        'grocery_revenues.json',
        'grocery_revenues_invalid_contract_id.json',
        'grocery_revenues_skip_contract_validation.json',
        'eats_revenues.json',
        'eats_expenses.json',
        'eats_agent.json',
        'eats_payments.json',
        'lukoil_revenues.json',
        'signalq_monitoring_fee.json',
        'shuttle_order.json',
        'eats_order.json',
    ],
)
async def test_v2_process_async_event_at_validation(
        test_data_path,
        load_py_json_dir,
        request_headers,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        patched_tvm_ticket_check,
        taxi_billing_orders_client,
        monkeypatch,
):
    data = load_py_json_dir('test_v2_process_async', test_data_path)

    next_doc_id: int = 1002

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        nonlocal next_doc_id
        assert 'create' in url
        resp = {'doc_id': next_doc_id, 'kind': json['kind']}
        next_doc_id += 1
        return response_mock(json=resp)

    @patch_aiohttp_session(
        discovery.find_service('billing_calculators').url, 'POST',
    )
    def _patch_billing_calculators_request(
            method, url, headers, json, **kwargs,
    ):
        return response_mock(json=json)

    @mockserver.json_handler('/billing-replication/v1/check_contracts/')
    def _check_contracts(request):
        check_contracts = copy.deepcopy(request.json['contracts'])
        for contract in check_contracts:
            contract['is_valid'] = True
        return {'contracts': check_contracts}

    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS',
        {'__default__': 24},
    )

    response = await taxi_billing_orders_client.post(
        '/v2/process/async', headers=request_headers, json=data['request'],
    )
    text = await response.text()
    assert response.status == 400, text

    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS',
        {'__default__': 10 ** 6},
    )
    response = await taxi_billing_orders_client.post(
        '/v2/process/async', headers=request_headers, json=data['request'],
    )
    text = await response.text()
    assert response.status == data['response_status'], text


def _compare_resources(requested_resources, spent_resources, json_data):
    expected_requested_resources = [
        resource_limiter.Resource(name=res[0], amount=res[1])
        for res in json_data['expected_requested_resources']
    ]
    expected_spent_resources = [
        resource_limiter.Resource(name=res[0], amount=res[1])
        for res in json_data['expected_spent_resources']
    ]

    def _sorted_res(resources):
        return sorted(resources, key=lambda res: res.name)

    assert _sorted_res(requested_resources) == _sorted_res(
        expected_requested_resources,
    )

    assert _sorted_res(spent_resources) == _sorted_res(
        expected_spent_resources,
    )
