import hashlib
import json
import os

import pytest

from market_b2c_etl.layer.greenplum.ods.checkouter.order_event.extractors import EXTRACTORS
from test_market_b2c_etl.layer.greenplum.ods.common.test_extractors import execute_extractors


def test_whole_object():
    dirname = os.path.dirname(__file__)
    with open(os.path.join(dirname, 'data/input.json'), 'r') as f:
        parsed = execute_extractors(json.load(f), EXTRACTORS)
    expected = {'utc_event_from_dttm': '2021-04-04 04:47:20.029727', 'msk_event_from_dttm': '2021-04-04 07:47:20',
                'event_id': 1078029727, 'author_role': 'SYSTEM',
                'buyer_currency': 'RUR', 'customer_auth_flg': True, 'customer_region_id': 21623,
                'cancellation_role_name': None, 'creation_date': '2021-04-03 18:16:00',
                'creation_date_raw': '2021-04-03 18:16:00', 'msk_order_created_dttm': '2021-04-03 18:16:00',
                'currency': 'RUR', 'lcl_actual_delivery_from_dt': '2021-04-04', 'delivery_min_time_of_day': '09:00',
                'delivery_price': '0', 'delivery_region_id': 21623, 'delivery_service_id': '1005477',
                'lcl_actual_delivery_to_dt': '2021-04-04', 'delivery_max_time_of_day': '22:00', 'delivery_type': 'DELIVERY',
                'dont_call_flg': True, 'customer_muid': None, 'notes_desc': None, 'order_id': 1234, 'order_fake_flg': False,
                'order_status': 'DELIVERY', 'order_sub_status': 'DELIVERY_SERVICE_RECEIVED',
                'payment_method_type': 'CASH_ON_DELIVERY', 'payment_type': 'POSTPAID', 'platform_type': 'ANDROID', 'rgb': 'BLUE',
                'customer_uid': 4949494, 'customer_id_type': 'passport', 'customer_uuid': 'f16dc741577440f8abd0c7179c18ad14',
                'yandex_employee_flg': True, 'yandex_uid': None, 'mrid': 'rgergewr4-360c-4b2a-bd61-6ba10575ae9b',
                'payment_id': None, 'multi_order_flg': True,
                'multiorder_id': 'multiorder_id-rgergewr4-360c-4b2a-bd61-6ba10575ae9b',
                'cancel_reason_custom_desc': None, 'preorder_flg': False, 'shipment_datetime': '2021-04-04T03:51:00',
                'shipment_flag': True, 'outlet_id': None, 'post_outlet_id': None,
                'raw_delivery_precise_region_id': None, 'coupon_flg': True, 'yandex_plus_flg': False,
                'order_declared_price_rub': '334.0', 'multiorder_total_cashback_spasibo_amount': '0.0',
                'purchase_referrer_code': None, 'market_fulfilment_flg': True, 'delivery_partner_type': 'YANDEX_MARKET',
                'yandex_plus_user_flg': False,
                'customer_email_code': '0cf9dacee1412b6cbd5bab766a286b6a3c66bc7d169e11611991a1fc43910a12',
                'order_express_delivery_flg': False,
                'order_on_demand_delivery_flg': False,
                'order_on_demand_lavka_delivery_flg': False,
                'order_on_demand_market_pickup_delivery_flg': False,
                'b2b_partner_warehouse_flg': 'YANDEX_MARKET',
                'market_request_code': '1617462960083/dbdbea5b00629f85a1512cf112bf0500/10',
                'msk_before_user_changed_pickup_storage_limit_dt': None,
                'msk_pickup_storage_limit_dt': None,
                'msk_user_changed_pickup_storage_limit_dt': None,
                'payment_submethod_type': None,
                'plan_b2b_partner_shipment_dttm': '2021-04-03 00:00:00',
                'plan_shipment_dt': '2021-04-03',
                "event_type": "TRACK_CHECKPOINT_CHANGED",
                "assessor_flg": False,
                "bnpl_flg": False,
                "checkouter_shoot_flg": False,
                "customer_fake_flg": False,
                "deleted_item_event_flg": False,
                "delivery_lift_price_rub": '0.0',
                "delivery_lift_type": '',
                "leave_at_the_door_flg": False,
                "missing_item_event_flg": False,
                "placement_context_type": 'MARKET',
                'customer_type': None,
                'legal_contract_id': None,
                'legal_balance_id': None,
                'order_parcel_depth_m': 0.26,
                'order_parcel_height_m': 0.25,
                'order_parcel_width_m': 0.1,
                'order_parcel_weight_kg': 1.0,
                'customer_icookie': 'fff_test_bbb_icookie_fff',
                'order_estimated_delivery_date_flg': 0,
                'order_custom_flg': 0,
                'order_wide_interval_delivery_flg': False,
                'order_one_hour_interval_delivery_flg': False,
                }

    assert parsed['customer_email_code'] == hashlib.sha256('qqqqqq@fake.ru'.encode('utf-8')).hexdigest()
    assert parsed == expected


@pytest.mark.parametrize('extractor, expected, obj', [
    ('bnpl_flg', True, {'orderAfter': {'bnpl': True}}),
    ('checkouter_shoot_flg', True, {
        'orderAfter': {'buyer': {'email': 'checkouter-shooting@yandex-team.ru'}}
    }),
    ('checkouter_shoot_flg', True, {
        'orderBefore': {'buyer': {'email': 'checkouter-shooting@yandex-team.ru'}}
    }),
    ('placement_context_type', 'SANDBOX', {'orderAfter': {'context': 'SANDBOX'}}),
    ('assessor_flg', True, {'orderAfter': {'buyer': {'assessor': True}}}),
    ('customer_fake_flg', True, {'orderAfter': {'context': 'SANDBOX'}}),
    ('customer_fake_flg', True, {'orderAfter': {'buyer': {'assessor': True}}}),
    ('deleted_item_event_flg', True, {'type': 'ITEMS_UPDATED'}),
    ('delivery_lift_price_rub', '322.22', {'orderAfter': {'delivery': {'liftPrice': '322.22'}}}),
    ('delivery_lift_type', 'soviet-old-crap', {
        'orderAfter': {'delivery': {'liftType': 'soviet-old-crap'}}
    }),
    ('leave_at_the_door_flg', True, {'orderAfter': {'notes': 'оставить у двери'}}),
    ('missing_item_event_flg', True, {
        'type': 'ORDER_STATUS_UPDATED',
        'orderAfter': {'status': 'CANCELLED', 'substatus': 'MISSING_ITEM'}
    }),
    (
        'customer_email_code',
        hashlib.sha256(''.encode('utf-8')).hexdigest(),
        {'orderAfter': {'buyer': {}}}
    ),
    (
        'customer_email_code',
        hashlib.sha256('this_is_email@yandex.ru'.encode('utf-8')).hexdigest(),
        {'orderAfter': {'buyer': {'email': 'this_is_email@yandex.ru'}}}
    ),
])
def test_extractors(extractor, obj, expected):
    assert EXTRACTORS[extractor](obj) == expected
