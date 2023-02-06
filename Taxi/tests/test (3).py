#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function

import os
import json
import sys
from zoo.utils import so_helpers
from zoo.utils import default_values
from taxi_ml_cxx.zoo.no_cars import FeaturesExtractor

ABS_SCRIPT_PATH = os.path.abspath(__file__)
TEST_DIR = os.path.dirname(ABS_SCRIPT_PATH)

request = {
    "experiments": [
        "no_cars_ml_test",
        "paid_supply_ml_control_permit",
        "aaa",
        "bbbb"
    ],
    "time": "2018-05-14T20:09:43Z",
    "phone_id": "qwe123_phone_id",
    "nz": "perm",
    "route_points": [[37.62540815185093, 55.770563889046514]],
    "classes_info": [

        {
            "tariff_class": "econom",
            "surge_info": {},
            "max_distance": 10000.1,
            "max_time": 900.1,
            "limit": 20,
            "max_line_distance": 8000.1,
            "estimated_waiting": 172.144
        }
    ]
}

features1 = [37.62540817260742, 55.770565032958984, 53.956050872802734, 52.14153289794922, 50.32701873779297, 48.51250076293945, 46.6979866027832, 44.88347244262695, 43.06895446777344, 41.25444030761719, 39.43992233276367, 233.8899688720703, 232.0243682861328, 230.17364501953125, 228.33767700195312, 226.51637268066406, 224.70957946777344, 222.91720581054688, 221.13912963867188, 219.37522888183594, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 1.0, 37.62540817260742, 55.770565032958984, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.6914401650428772, 0.024773478507995605, 0.3581068217754364, 0.8400810360908508, 0.17341434955596924, 0.5067476630210876, 0.6914401650428772, 0.024773478507995605, 0.3581068217754364, 0.8400810360908508, 0.17341434955596924, 0.5067476630210876, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, 10000.099609375, 8000.10009765625, 900.0999755859375, 20.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

request2 = {
    "experiments": [
        "no_cars_ml_control_deny",
        "paid_supply_ml_control_deny",
        "aaa",
        "bbbb"
    ],
    "time": "2018-05-14T20:09:43Z",
    "user_id": "qwe123user_id",
    "phone_id": "qwe123_phone_id",
    "yandex_uid": "qwe123_yandex_uid",
    "surge_id": "qwe123_surge_id",
    "nz": "mkad",
    "route_points": [[37.62540815185093, 55.770563889046514], [37.62540815185093, 55.770563889046514], [37.62540815185093, 55.770563889046514]],
    "route_distance": 10500.1,
    "route_duration": 960.1,
    "currency": "RUB",
    "classes_info": [
        {
            "tariff_class": "econom",
            "surge_info": {
                "radius": 2500,
                "pins": 100,
                "free": 10,
                "free_chain": 3,
                "total": 60,
                "surge_value": 0.7,
                "surge_value_smooth": 1.0
            },
            "cost": 300.1,
            "cost_original": 330.1,
            "cost_driver": 400.1,
            "max_distance": 10000.1,
            "max_time": 900.1,
            "limit": 20,
            "max_line_distance": 8000.1,
        }
    ]
}
features2 = [37.62540817260742, 55.770565032958984, 53.956050872802734, 52.14153289794922, 50.32701873779297, 48.51250076293945, 46.6979866027832, 44.88347244262695, 43.06895446777344, 41.25444030761719, 39.43992233276367, 233.8899688720703, 232.0243682861328, 230.17364501953125, 228.33767700195312, 226.51637268066406, 224.70957946777344, 222.91720581054688, 221.13912963867188, 219.37522888183594, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.6914401650428772, 0.024773478507995605, 0.3581068217754364, 0.8400810360908508, 0.17341434955596924, 0.5067476630210876, 0.6914401650428772, 0.024773478507995605, 0.3581068217754364, 0.8400810360908508, 0.17341434955596924, 0.5067476630210876, 100.0, 10.0, 3.0, 60.0, 0.699999988079071, 1.0, 10000.099609375, 8000.10009765625, 900.0999755859375, 20.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, -99.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

request3 = {
    "classes_info": [
        {
            "cost": 162,
            "cost_driver": 162,
            "limit": 5,
            "max_distance": 5000,
            "max_line_distance": 10000,
            "max_time": 780,
            "surge_info": {
                "free": 0,
                "free_chain": 0,
                "pins": 4,
                "radius": 2500,
                "surge_value": 1,
                "surge_value_smooth": 1,
                "total": 2
            },
            "tariff_class": "econom"
        },
        {
            "cost": 216,
            "cost_driver": 216,
            "limit": 5,
            "max_distance": 5000,
            "max_line_distance": 10000,
            "max_time": 780,
            "surge_info": {
                "free": 1,
                "free_chain": 0,
                "pins": 4,
                "radius": 2500,
                "surge_value": 1,
                "surge_value_smooth": 1,
                "total": 1
            },
            "tariff_class": "business"
        },
        {
            "cost": 140,
            "cost_driver": 140,
            "limit": 5,
            "max_distance": 5000,
            "max_line_distance": 10000,
            "max_time": 780,
            "surge_info": {
                "surge_value": 1,
                "surge_value_smooth": 1
            },
            "tariff_class": "start"
        }
    ],
    "currency": "RUB",
    "experiments": [
        "abijan_econom_show",
        "add_free_waiting_to_notification_on_driver_arriving",
        "address_change_logging",
        "altpin_hide_and_log",
        "altpin_money",
        "altpin_money_2",
        "altpin_time_improvements",
        "android_app_icon_update_2018",
        "b_on_main_next_white",
        "bad_gps_show",
        "black_price",
        "blocked_zones",
        "calc_graph_surge_EKB",
        "calc_info_cpp",
        "cars_on_map",
        "change_card_during_the_ride",
        "change_ride_report",
        "check_destination_restrictions",
        "check_forced_surge_cpp",
        "check_fraud_cpp",
        "check_requirements_cpp",
        "child_tariff3",
        "child_tariff4",
        "child_tbilisi",
        "client_geo",
        "client_geo_request",
        "colors_cars",
        "corp_info_cpp",
        "correct_multiorder_limits",
        "current_ride_in_oh",
        "decrease_sms_from_site",
        "destination_suggests_logging",
        "disable_zone_name_request",
        "discount_strike",
        "divining_point_a",
        "divining_point_b",
        "do_stick_in_all_zone_types",
        "driver_fio_removed",
        "ekb_child_show",
        "enable_contact_options_in_zoneinfo",
        "eta_mlaas",
        "eta_mlaas_fix_m0",
        "expected_destination_mlaas",
        "expected_destination_with_types",
        "expected_destinations_v2_mlaas",
        "expectedpositions_mlaas",
        "external_tc",
        "feedback_retrieve",
        "feedback_retrieve_wanted",
        "first_usage_per_classes",
        "five_stars",
        "five_stars_achievement",
        "fixed_price",
        "fixed_price_cpp",
        "forced_surge",
        "get_experiments_cpp",
        "graph_nearest_drivers",
        "hide_sms_with_push",
        "highlight_pool",
        "home_button_priority",
        "ios_app_icon_update_2018",
        "just_one_more_stuped_test_ikars",
        "lazy_update_selected_tarif",
        "login_menu",
        "login_new",
        "mastercard_discount",
        "multiorder_calc_can_make_more_orders",
        "multiorder_enabled_in_launch",
        "multiple_points",
        "nearest_entrances",
        "newbie_discount",
        "newbie_nosurge",
        "nizhnynovgorod_child_show",
        "no_cars_ml_control_permit",
        "no_cars_order_available",
        "notify_user_to_enable_push",
        "novosibirsk_child_show",
        "order_button_text_back",
        "order_cpp",
        "order_draft_cpp",
        "order_for_other",
        "order_for_other_distance",
        "order_for_other_new",
        "ordercommit_cpp",
        "orders_history_availability",
        "orders_history_detail",
        "orders_history_preload",
        "other_app",
        "paid_cancel",
        "pickup_points_enabled",
        "pickuppoints_ml",
        "pickuppoints_ml_stick",
        "poolX",
        "pool_help_screens",
        "pool_sounds",
        "pool_tooltip",
        "portal_account_proto",
        "ppp_first_sticky_street",
        "ppp_first_sticky_zone",
        "process_for_multiorder_on_order_commit",
        "quality_ufa_test",
        "refactored_routestats",
        "refactored_routestats_2",
        "refer_promo_contextmenu",
        "refer_promo_feedback_4",
        "refer_promo_feedback_empty",
        "referral_percent",
        "require_authorization_for_cash",
        "reserve_card_cpp",
        "reserve_coupon_cpp",
        "route_adjust",
        "route_adjust_eta",
        "routestats_cpp",
        "routestats_fixed_price_time",
        "routestats_nearest_spots",
        "routing_42",
        "save_users_show_start",
        "send_notification_on_driver_arriving",
        "show_distance",
        "show_ultimate",
        "suggested_expected_destinations",
        "support_commit_cpp",
        "supported_midpoint_change",
        "surge_dest_req",
        "surge_distance",
        "surge_reduced_lookandfeel",
        "taxiroute2",
        "tips_flat",
        "trust_bindings_v2",
        "ufa_business_show",
        "ufa_econom_show",
        "update_calc_info_cpp",
        "use_geotracks_for_orderhistory",
        "use_new_smooth_movement_android",
        "use_order_draft_commit",
        "use_support_chat_api",
        "user_chat",
        "user_position_enabled_2",
        "userplaces_in_b",
        "volgograd_business_show",
        "xiva",
        "ya_plus",
        "ya_plus_animated_for_twirl",
        "ya_plus_by_uid",
        "ya_plus_fullscreen_2",
        "yamaps_experiment_25",
        "yerevan_child_show"
    ],
    "nz": "perm",
    "phone_id": "5a0d379f4dbc78150b838a4e",
    "route_distance": 11172.195695877075,
    "route_duration": 889.7466587651965,
    "route_points": [
        [
            56.262916009925554,
            58.06227197711674
        ],
        [
            56.201219,
            58.010839
        ]
    ],
    "surge_id": "9bf797f902a94334aa32cf78dc7d95fc",
    "time": "2018-10-24T09:22:45.325596949+0500",
    "user_id": "0f1f78d7f73abb834d72194a36360b90"
}
features3 = [56.262916564941406, 58.06227111816406, 57.8823356628418, 57.70240020751953, 57.522464752197266, 57.342529296875, 57.162593841552734, 56.98265838623047, 56.8027229309082, 56.62278747558594, 56.44285202026367, 237.8817138671875, 237.70130920410156, 237.52102661132812, 237.3408966064453, 237.160888671875, 236.98101806640625, 236.80128479003906, 236.62168884277344, 236.44224548339844, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 1.0, 56.262916564941406, 58.06227111816406, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.0, -99.0, -99.0, 0.9129712581634521, 0.24630455672740936, 0.579637885093689, 0.3907985985279083, 0.7241319417953491, 0.05746527761220932, 0.8832093477249146, 0.21654266119003296, 0.5498759746551514, 0.18246528506278992, 0.5157986283302307, 0.8491319417953491, 4.0, 0.0, 0.0, 2.0, 1.0, 1.0, 5000.0, 10000.0, 780.0, 5.0, -1.0, -1.0, -1.0, -1.0, 1.0, 1.0, 4.0, 1.0, 0.0, 1.0, 1.0, 1.0, -99.0, -99.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

def test():
    print('Testing started')
    features_extractor = FeaturesExtractor()
    tariff_class = 'econom'
    if features_extractor.extract(request, tariff_class) != features1:
        print('FAIL1')
    if features_extractor.extract(request2, tariff_class) != features2:
        print('FAIL2')
    if features_extractor.extract(request3, tariff_class) != features3:
        print('FAIL3')
    print('test_end')



if __name__ == '__main__':
    test()
