from collections import namedtuple
from demand_etl.layer.yt.rep.user_features.order.common.impl_rep import pivot
from os import environ

GmvRecord = namedtuple('GmvRecord', [
    'service_name',
    'brand_name',
    'tariff_name',
    'first_order_dt',
    'last_order_dt',
    'gmv_w_vat_rub',
    'gmv_w_vat_rub_prev_week',
    'gmv_w_vat_rub_prev_6weeks',
    'gmv_w_vat_rub_prev_13weeks',
    'order_cnt',
    'order_cnt_prev_week',
    'order_cnt_prev_6weeks',
    'order_cnt_prev_13weeks',
])


def test_pivot():
    environ['ID_TYPE'] = 'yandex_uid'
    assert list(pivot((b'user1', b'2018-08-01'), iter([
        GmvRecord(b'taxi', b'yandex', b'econom', b'2018-01-01', b'2018-07-01', 100.0, 20.0, 80.0, 90.0, 10, 3, 5, 7),
        GmvRecord(b'taxi', b'yandex', b'business', b'2018-01-02', b'2018-07-20', 300.0, 40.0, 90.0, 180.0, 7, 1, 2, 3),
        GmvRecord(b'eda', b'', b'', b'2018-01-01', b'2018-08-01', 350.0, 90.0, 140.0, 230.0, 8, 2, 3, 4),
        GmvRecord(b'drive', b'', b'', b'2018-03-01', b'2018-08-01', 400.0, 80.0, 120.0, 300.0, 3, 1, 2, 3),
    ]))) == [
        {'yandex_uid': b'user1',
         'report_dt': b'2018-08-01',
         'taxi_yandex_last_order_dt': {'econom': b'2018-07-01', 'business': b'2018-07-20'},
         'taxi_yandex_first_order_dt': {'econom': b'2018-01-01', 'business': b'2018-01-02'},
         'taxi_yandex_all_time_order_cnt': {'econom': 10, 'business': 7},
         'taxi_yandex_1_week_order_cnt': {'econom': 3, 'business': 1},
         'taxi_yandex_6_week_order_cnt': {'econom': 5, 'business': 2},
         'taxi_yandex_13_week_order_cnt': {'econom': 7, 'business': 3},
         'taxi_yandex_all_time_gmv_w_vat_rub': {'econom': 100.0, 'business': 300.0},
         'taxi_yandex_1_week_gmv_w_vat_rub': {'econom': 20.0, 'business': 40.0},
         'taxi_yandex_6_week_gmv_w_vat_rub': {'econom': 80.0, 'business': 90.0},
         'taxi_yandex_13_week_gmv_w_vat_rub': {'econom': 90.0, 'business': 180.0},
         'eda_last_order_dt': b'2018-08-01',
         'eda_first_order_dt': b'2018-01-01',
         'eda_all_time_order_cnt': 8,
         'eda_1_week_order_cnt': 2,
         'eda_6_week_order_cnt': 3,
         'eda_13_week_order_cnt': 4,
         'eda_all_time_gmv_w_vat_rub': 350.0,
         'eda_1_week_gmv_w_vat_rub': 90.0,
         'eda_6_week_gmv_w_vat_rub': 140.0,
         'eda_13_week_gmv_w_vat_rub': 230.0,
         'drive_last_order_dt': b'2018-08-01',
         'drive_first_order_dt': b'2018-03-01',
         'drive_all_time_order_cnt': 3,
         'drive_1_week_order_cnt': 1,
         'drive_6_week_order_cnt': 2,
         'drive_13_week_order_cnt': 3,
         'drive_all_time_gmv_w_vat_rub': 400.0,
         'drive_1_week_gmv_w_vat_rub': 80.0,
         'drive_6_week_gmv_w_vat_rub': 120.0,
         'drive_13_week_gmv_w_vat_rub': 300.0
         }
    ]
