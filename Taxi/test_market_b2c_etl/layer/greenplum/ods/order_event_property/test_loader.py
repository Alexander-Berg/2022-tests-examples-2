import json
import os

from market_b2c_etl.layer.greenplum.ods.checkouter.order_property.loader import get_order_events_properties_raw


def test_whole_object_parser():
    dirname = os.path.dirname(__file__)
    with open(os.path.join(dirname, 'data/input.json'), 'r') as f:
        input = json.load(f)

    actual = []
    for i in get_order_events_properties_raw(input):
        actual.append(i)

    print(actual)
    assert len(actual) == 10
    expected = [{'event_id': 1078029727, 'order_id': 1234, 'from_date': '04-04-2021 07:47:20', 'key': 'appVersion',
                 'value': '2.8.9'},
                {'event_id': 1078029727, 'order_id': 1234, 'from_date': '04-04-2021 07:47:20', 'key': 'mrid',
                 'value': '1617462960083/dbdbea5b00629f85a1512cf112bf0500/10'},
                {'event_id': 1078029727, 'order_id': 1234, 'from_date': '04-04-2021 07:47:20', 'key': 'yandexPlusUser',
                 'value': 'false'},
                {'event_id': 1078029727, 'order_id': 1234, 'from_date': '04-04-2021 07:47:20', 'key': 'experiments',
                 'value': 'market_white_cpa_on_blue=2;market_promo_blue_cheapest_as_gift=1;dyn_main_page_off;promo_bbb_blue_set=1;market_blue_meta_formula_type=meta_fml_formula_740170;market_textless_search_mn_algo=MNA_fml_formula_761156;market_promo_blue_generic_bundle=1;promo_bbb_generic_bundle=1;market_blue_buybox_gmv_epsilon=0.005;promo_bbb_cheapest_as_gift=1;show_digital_dsbs_goods=0;market_promo_blue_flash=1;items_removal_if_missing;promo_bbb_blue_flash=1;market_blue_buybox_cheapest_as_gift_promo_rate=0.8;market_search_mn_algo=DbD_loss_699480_046_x_Click_699743_x_Binary_699599_030;promo_price_in_buybox=1;market_rebranded=1;market_blue_add_delivery_service_options=1;market_cashback_for_not_ya_plus=1;market_blue_buybox_randomization_fix=1;market_blue_buybox_generic_bundle_promo_rate=0.1;market_blue_buybox_promocode=1;market_promo_blue_cheapest_as_gift_4=1;market_use_bert_dssm=1'},
                {'event_id': 1078029727, 'order_id': 1234, 'from_date': '04-04-2021 07:47:20', 'key': 'multiOrderId',
                 'value': 'rgergewr4-360c-4b2a-bd61-6ba10575ae9b'},
                {'event_id': 1078029727, 'order_id': 1234, 'from_date': '04-04-2021 07:47:20', 'key': 'clid',
                 'value': '625'},
                {'event_id': 1078029727, 'order_id': 1234, 'from_date': '04-04-2021 07:47:20', 'key': 'multiOrderSize',
                 'value': '2'},
                {'event_id': 1078029727, 'order_id': 1234, 'from_date': '04-04-2021 07:47:20', 'key': 'deviceId',
                 'value': '{"androidBuildModel":"HRY-LX1","androidDeviceId":"ee5fc6217953db32","googleServiceId":"cc3859bb-d087-4ac7-8ef9-ae93af1edab7","androidBuildManufacturer":"HUAWEI","androidHardwareSerial":"unknown"}'},
                {'event_id': 1078029727, 'order_id': 1234, 'from_date': '04-04-2021 07:47:20', 'key': 'platform',
                 'value': 'ANDROID'},
                {'event_id': 1078029727, 'order_id': 1234, 'from_date': '04-04-2021 07:47:20', 'key': 'testBuckets',
                 'value': '350493,0,43;349177,0,43;348214,0,45;345052,0,63;342074,0,-1;304341,0,63;300574,0,-1;200206,0,60;101608,0,28'}]

    assert expected == actual
