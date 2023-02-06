import pytest

from nile.api.v1 import MockCluster
from nile.api.v1.local import StreamSource, ListSink

from eda_etl.layer.yt.cdm.user_product.eda_user_appsession.impl import ApplicationSessionBuilder, ApplicationSession

from test_eda_etl.layer.yt.cdm.user_product.eda_user_appsession.impl import eda_appmetrica_record, eda_appsession_record


@pytest.mark.parametrize(
    'eda_appmetrica_events, eda_expected_sessions',
    [
        pytest.param(
            [
                eda_appmetrica_record(
                    lavka_place_id=123,
                    geobase_city_name='Narnia',
                    geobase_city_name_ru='Нарния',
                    region_id=2222,
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    os_version_code='1.2.4',
                    device_id='123asdf123',
                    event_name='abcder1',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id='123qwe1',
                    app_version_code='12345',
                    device_type='LAPTOP',
                    request_id='abcd1234',
                    eda_place_id_list=None,
                    eda_surge_val_list=None,
                    eda_client_id='1234',
                    eda_user_id=1234,
                    yandex_uid='124',
                    plus_screen_available_flg=True,
                    geobase_city_name='Artem',
                    geobase_city_name_ru='Артем',
                    region_id=1996,
                )
            ],
            [
                eda_appsession_record(
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='9a8f8892b9016797405c5b3a4181818f',
                    app_version_code='12345',
                    event_id_list=['1234567890','1234567891'],
                    os_version_code='1.2.4',
                    duration_sec=1800,
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id_paid_list=['123qwe', '123qwe1'],
                    request_id_list=['abcd123', 'abcd1234'],
                    eda_client_id='1234',
                    device_type_name='LAPTOP',
                    last_request_eda_place_id_list=None,
                    last_request_eda_surge_val_list=None,
                    yandex_uid='124',
                    plus_screen_available_flg=True,
                    geobase_city_name='Artem',
                    geobase_city_name_ru='Артем',
                    geobase_region_id=1996,
                )
            ],
            id='Base session with break: timeout'
        ),
        pytest.param(
            [
                eda_appmetrica_record(),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    os_version_code='1.2.4',
                    event_name='abcder1',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id='123qwe1',
                    app_version_code='12346',
                    request_id='abcd1234',
                )
            ],
            [
                eda_appsession_record(
                    utc_session_end_dttm='2019-08-01 10:00:01',
                    appsession_id='9a8f8892b9016797405c5b3a4181818f',
                    app_version_code='12345',
                    event_id_list=['1234567890'],
                    os_version_code='1.2.3',
                    break_reason='app_version_change',
                    duration_sec=0,
                    appmetrica_uuid='123asdf123',
                    appmetrica_device_id='123asdf123',
                    order_id_paid_list=['123qwe'],
                ),
                eda_appsession_record(
                    utc_session_start_dttm='2019-08-01 10:30:01',
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='c97a5463260fd556c5aeef91795b278f',
                    app_version_code='12346',
                    event_id_list=['1234567891'],
                    os_version_code='1.2.4',
                    break_reason='timeout',
                    duration_sec=0,
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id_paid_list=['123qwe1'],
                    request_id_list=['abcd1234'],
                ),
            ],
            id='Base session with break: app_version'
        ),
        pytest.param(
            [
                eda_appmetrica_record(),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:00:02',
                    eda_client_id=None,
                    event_id='1234567892'
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    os_version_code='1.2.4',
                    event_name='abcder1',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id='123qwe1',
                    app_version_code='12345',
                    eda_client_id='1235',
                    request_id='abcd1234',
                )
            ],
            [
                eda_appsession_record(
                    utc_session_end_dttm='2019-08-01 10:00:02',
                    appsession_id='9a8f8892b9016797405c5b3a4181818f',
                    app_version_code='12345',
                    event_id_list=['1234567890', '1234567892'],
                    os_version_code='1.2.3',
                    break_reason='eda_client_id_change',
                    duration_sec=1,
                    appmetrica_uuid='123asdf123',
                    appmetrica_device_id='123asdf123',
                    order_id_paid_list=['123qwe'],
                    eda_client_id='1234',
                ),
                eda_appsession_record(
                    utc_session_start_dttm='2019-08-01 10:30:01',
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='c97a5463260fd556c5aeef91795b278f',
                    app_version_code='12345',
                    event_id_list=['1234567891'],
                    os_version_code='1.2.4',
                    break_reason='timeout',
                    duration_sec=0,
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id_paid_list=['123qwe1'],
                    request_id_list=['abcd1234'],
                    eda_client_id='1235',
                ),
            ],
            id='Base session with break: eda_client_id'
        ),
        pytest.param(
            [
                eda_appmetrica_record(
                    event_id='1234567890',
                    event_name='rest_menu',
                    event_value={},
                    order_id='123qwe',
                    app_version_code='12345',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 12:30:01',
                    event_id='1234567891',
                    os_version_code='1.2.4',
                    event_name='thisislavka1234',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id='123qwe1',
                    app_version_code='12346',
                )
            ],
            [
                eda_appsession_record(
                    utc_session_start_dttm='2019-08-01 10:00:01',
                    utc_session_end_dttm='2019-08-01 10:00:01',
                    appsession_id='9a8f8892b9016797405c5b3a4181818f',
                    app_version_code='12345',
                    event_id_list=['1234567890'],
                    os_version_code='1.2.3',
                    break_reason='timeout',
                    duration_sec=0,
                    appmetrica_uuid='123asdf123',
                    appmetrica_device_id='123asdf123',
                    is_lavka_opened_flg=False,
                    is_rest_menu_opened_flg=True,
                    order_id_paid_list=['123qwe'],
                    utc_first_rest_menu_dttm='2019-08-01 10:00:01',
                    utc_last_rest_menu_dttm='2019-08-01 10:00:01',
                ),
                eda_appsession_record(
                    utc_session_start_dttm='2019-08-01 12:30:01',
                    utc_session_end_dttm='2019-08-01 12:30:01',
                    appsession_id='45fa8f9e5c84470754a386e07c12f3a6',
                    app_version_code='12346',
                    event_id_list=['1234567891'],
                    os_version_code='1.2.4',
                    break_reason='timeout',
                    duration_sec=0,
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    is_lavka_opened_flg=True,
                    is_rest_menu_opened_flg=False,
                    order_id_paid_list=['123qwe1'],
                ),
            ],
            id='Check is_lavka and is_rest'
        ),
        pytest.param(
            [
                eda_appmetrica_record(
                    config_ab=
                            {
                                "eda_new_year_statistics": "new_year_statistics",
                                "ny_courier_icon_tracking": "ny_is_here"
                            },
                    lavka_place_id=None
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    app_platform_name='android',
                    os_version_code='1.2.4',
                    event_name='config',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id='123qwe1',
                    application_version='12345',
                    config_ab=
                            {
                                "eda_new_year_statistics": "new_year_statistics1",
                                "ny_courier_icon_tracking1": "ny_is_here1"
                            },
                    lavka_place_id=123,
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567892',
                    os_version_code='1.2.4',
                    event_name='config',
                    event_value={},
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id='123qwe2',
                    app_version_code='12345',
                    config_ab=
                    {
                        "eda_new_year_statistics": "new_year_statistics2",
                    },
                    lavka_place_id=1234,
                )
            ],
            [
                eda_appsession_record(
                    device_id='123asdf123',
                    utc_session_start_dttm='2019-08-01 10:00:01',
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='9a8f8892b9016797405c5b3a4181818f',
                    app_version_code='12345',
                    event_id_list=['1234567890', '1234567891', '1234567892'],
                    os_version_code='1.2.4',
                    duration_sec=1800,
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    is_lavka_opened_flg=False,
                    is_rest_menu_opened_flg=False,
                    config_ab_dict={
                                "ny_courier_icon_tracking1": "ny_is_here1",
                                "ny_courier_icon_tracking": "ny_is_here"
                            },
                    order_id_paid_list=['123qwe', '123qwe1', '123qwe2'],
                )
            ],
            id='Check config_ab_list'
        ),
        pytest.param(
            [
                eda_appmetrica_record(),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    os_version_code='1.2.4',
                    device_id='123asdf123',
                    event_name='abcder1',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id='123qwe1',
                    app_version_code='12345',
                    lat=3.3,
                    lon=4.4,
                    destination_lat=33.33,
                    destination_lon=44.44,
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567890',
                    os_version_code='1.2.4',
                    device_id='123asdf124',
                    event_name='abcder1',
                    appmetrica_uuid='123asdf123',
                    appmetrica_device_id='123asdf123',
                    order_id='123qwe1',
                    app_version_code='12345',
                    lat=47.212665,
                    lon=39.702643,
                    destination_lat=55.829537,
                    destination_lon=37.593938,
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:02',
                    event_id='1234567891',
                    os_version_code='1.2.4',
                    device_id='123asdf124',
                    event_name='abcder1',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id='123qwe',
                    app_version_code='12345',
                    lat=47.212665,
                    lon=39.702643,
                    destination_lat=55.829537,
                    destination_lon=37.593938,
                )

            ],
            [
                eda_appsession_record(
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='9a8f8892b9016797405c5b3a4181818f',
                    duration_sec=1800,
                    user_lat=3.3,
                    user_lon=4.4,
                    destination_lat=33.33,
                    destination_lon=44.44,
                    destination_diff_m=3350735.856011135,
                    user_move_diff_m=345819.26718250634,
                ),
                eda_appsession_record(
                    device_id='123asdf124',
                    utc_session_start_dttm='2019-08-01 10:30:01',
                    utc_session_end_dttm='2019-08-01 10:30:02',
                    appsession_id='d49ee7a2594a08740784ddaca7bcb0aa',
                    duration_sec=1,
                    user_lat=47.212665,
                    user_lon=39.702643,
                    destination_lat=55.829537,
                    destination_lon=37.593938,
                    destination_diff_m=0.0,
                    user_move_diff_m=0.0,
                )
            ],
            id='Check lat/lon'
        ),
        pytest.param(
            [
                eda_appmetrica_record(
                    lavka_place_id=123,
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:15:01',
                    event_id='1234567891',
                    os_version_code='1.2.4',
                    device_id='123asdf123',
                    event_name='abcder1',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id='123qwe1',
                    app_version_code='12345',
                    max_lavka_surge_val=700,
                    lavka_surge_val=700,
                    request_id='abcd1234',
                    lavka_place_id=1234,
                    eda_place_id_list=[14, 24, 34],
                    eda_surge_val_list=[114, 224, 334],
                    eda_client_id='1234',
                    plus_screen_available_flg=False,
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:16:01',
                    event_id='1234567892',
                    os_version_code='1.2.4',
                    device_id='123asdf123',
                    event_name='abcder1',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id='123qwe1',
                    app_version_code='12345',
                    eda_client_id='1234',
                    created_order_id='1234',
                    plus_screen_available_flg=True,
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567893',
                    os_version_code='1.2.4',
                    device_id='123asdf123',
                    event_name='abcder1',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id='123qwe1',
                    app_version_code='12345',
                    max_lavka_surge_val=500,
                    lavka_surge_val=500,
                    request_id='abcd1234',
                    lavka_place_id=1235,
                    eda_place_id_list=[15, 25, 35],
                    eda_surge_val_list=[115, 225, 335],
                    eda_client_id='1234',
                    plus_screen_available_flg=False,
                )
            ],
            [
                eda_appsession_record(
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='9a8f8892b9016797405c5b3a4181818f',
                    app_version_code='12345',
                    event_id_list=['1234567890','1234567891', '1234567892', '1234567893'],
                    os_version_code='1.2.4',
                    duration_sec=1800,
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id_paid_list=['123qwe', '123qwe1'],
                    request_id_list=['abcd123', 'abcd1234'],
                    eda_client_id='1234',
                    created_order_id_list=['1234'],
                    plus_screen_available_flg=True,
                )
            ],
            id='Check last surge'
        ),
        pytest.param(
            [
                eda_appmetrica_record(
                    lavka_place_id=123,
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:14:01',
                    event_id='123456789',
                    created_order_id='1234',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:15:01',
                    event_id='1234567891',
                    os_version_code='1.2.4',
                    device_id='123asdf123',
                    event_name='abcder1',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id='123qwe1',
                    app_version_code='12345',
                    max_lavka_surge_val=None,
                    lavka_surge_val=None,
                    request_id='abcd1234',
                    lavka_place_id=None,
                    eda_place_id_list=None,
                    eda_surge_val_list=None,
                    eda_client_id='1234',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:16:01',
                    event_id='1234567892',
                    os_version_code='1.2.4',
                    device_id='123asdf123',
                    event_name='abcder1',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id='123qwe1',
                    app_version_code='12345',
                    eda_client_id='1234',
                    created_order_id='1234',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567893',
                    os_version_code='1.2.4',
                    device_id='123asdf123',
                    event_name='abcder1',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id='123qwe1',
                    app_version_code='12345',
                    max_lavka_surge_val=500,
                    request_id='abcd1234',
                    lavka_place_id=1235,
                    eda_place_id_list=[15, 25, 35],
                    eda_surge_val_list=[115, 225, 335],
                    eda_client_id='1234',
                )
            ],
            [
                eda_appsession_record(
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='9a8f8892b9016797405c5b3a4181818f',
                    app_version_code='12345',
                    event_id_list=['1234567890','123456789','1234567891', '1234567892', '1234567893'],
                    os_version_code='1.2.4',
                    duration_sec=1800,
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    order_id_paid_list=['123qwe', '123qwe1'],
                    request_id_list=['abcd123', 'abcd1234'],
                    eda_client_id='1234',
                    last_request_eda_place_id_list=None,
                    last_request_eda_surge_val_list=None,
                    created_order_id_list=['1234'],
                )
            ],
            id='Check last null surge before order'
        ),
        pytest.param(
            [
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    device_id='123asdf123',
                    event_name='rest_list',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:02',
                    device_id='123asdf123',
                    event_name='rest_list',
                    event_id='1234567891',
                    order_id='123qwe1',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 00:30:01',
                    device_id='123asdf123',
                    event_name='rest_menu',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 00:30:02',
                    device_id='123asdf123',
                    event_name='category_menu',
                    event_id='1234567891',
                    order_id='123qwe1',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 04:30:01',
                    device_id='123asdf123',
                    event_name='cart',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 04:30:02',
                    device_id='123asdf123',
                    event_name='cart',
                    event_id='1234567891',
                    order_id='123qwe1',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 06:30:01',
                    device_id='123asdf123',
                    event_name='checkout',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 06:30:02',
                    device_id='123asdf123',
                    event_name='test.eda.lavka.checkout.order',
                    event_id='1234567891',
                    order_id='123qwe1',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 08:30:01',
                    device_id='123asdf123',
                    event_name='tracking',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 08:30:02',
                    device_id='123asdf123',
                    event_name='tracking',
                    event_id='1234567891',
                    order_id='123qwe1',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 23:30:01',
                    device_id='123asdf123',
                    event_name='rest_menu',
                    dish_count_changed='"dish_count_changed":1',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 23:30:02',
                    device_id='123asdf123',
                    event_name='category_menu',
                    event_id='1234567891',
                    order_id='123qwe1',
                    dish_count_changed='"dish_count_changed":1'
                ),
            ],
            [
                eda_appsession_record(
                    utc_session_start_dttm='2019-08-01 00:30:01',
                    utc_session_end_dttm='2019-08-01 00:30:02',
                    appsession_id='00db10d67555f0cd0d6601c6262cbe13',
                    utc_first_rest_menu_dttm='2019-08-01 00:30:01',
                    utc_last_rest_menu_dttm='2019-08-01 00:30:02',
                    appmetrica_device_id='123asdf123',
                    appmetrica_uuid='123asdf123',
                    duration_sec=1,
                    os_version_code='1.2.3',
                    is_rest_menu_opened_flg=True,
                ),
                eda_appsession_record(
                    utc_session_start_dttm='2019-08-01 04:30:01',
                    utc_session_end_dttm='2019-08-01 04:30:02',
                    appsession_id='d9b5910b58ba28861aec4791207cb824',
                    utc_first_cart_dttm='2019-08-01 04:30:01',
                    utc_last_cart_dttm='2019-08-01 04:30:02',
                    appmetrica_device_id='123asdf123',
                    appmetrica_uuid='123asdf123',
                    duration_sec=1,
                    os_version_code='1.2.3',
                ),
                eda_appsession_record(
                    utc_session_start_dttm='2019-08-01 06:30:01',
                    utc_session_end_dttm='2019-08-01 06:30:02',
                    appsession_id='2ff5c5444d75621e3f98c46678726a9c',
                    utc_first_checkout_dttm='2019-08-01 06:30:01',
                    utc_last_checkout_dttm='2019-08-01 06:30:01',
                    appmetrica_device_id='123asdf123',
                    appmetrica_uuid='123asdf123',
                    duration_sec=1,
                    os_version_code='1.2.3',
                    is_lavka_opened_flg=True,
                ),
                eda_appsession_record(
                    utc_session_start_dttm='2019-08-01 08:30:01',
                    utc_session_end_dttm='2019-08-01 08:30:02',
                    appsession_id='7fb328f36dd32c8db5ced88cef37bdcd',
                    utc_first_tracking_dttm='2019-08-01 08:30:01',
                    utc_last_tracking_dttm='2019-08-01 08:30:02',
                    appmetrica_device_id='123asdf123',
                    appmetrica_uuid='123asdf123',
                    duration_sec=1,
                    os_version_code='1.2.3',
                ),
                eda_appsession_record(
                    utc_session_start_dttm='2019-08-01 10:30:01',
                    utc_session_end_dttm='2019-08-01 10:30:02',
                    appsession_id='c97a5463260fd556c5aeef91795b278f',
                    utc_first_rest_list_dttm='2019-08-01 10:30:01',
                    utc_last_rest_list_dttm='2019-08-01 10:30:02',
                    appmetrica_device_id='123asdf123',
                    appmetrica_uuid='123asdf123',
                    duration_sec=1,
                    os_version_code='1.2.3',
                ),
                eda_appsession_record(
                    utc_session_start_dttm='2019-08-01 23:30:01',
                    utc_session_end_dttm='2019-08-01 23:30:02',
                    appsession_id='019d5ba87ecf181a84cef6a30ec5951b',
                    utc_first_rest_menu_dttm='2019-08-01 23:30:01',
                    utc_last_rest_menu_dttm='2019-08-01 23:30:02',
                    utc_first_dish_count_changed_dttm='2019-08-01 23:30:01',
                    utc_last_dish_count_changed_dttm='2019-08-01 23:30:02',
                    appmetrica_device_id='123asdf123',
                    appmetrica_uuid='123asdf123',
                    duration_sec=1,
                    os_version_code='1.2.3',
                    is_rest_menu_opened_flg=True,
                ),
            ],
            id='Check utc_dttm-s'
        ),
        pytest.param(
            [
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    device_id='123asdf123',
                    event_name='rest_list',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:02',
                    device_id='123asdf123',
                    event_name='rest_list',
                    event_id='1234567891',
                    order_id='123qwe1',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 00:30:01',
                    device_id='123asdf123',
                    event_name='eda.lavka.category_list.open',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 00:30:02',
                    device_id='123asdf123',
                    event_name='lavka',
                    category_list={'1': '1'},
                    event_id='1234567891',
                    order_id='123qwe1',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 04:30:01',
                    device_id='123asdf123',
                    event_name='cart',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 04:30:02',
                    device_id='123asdf123',
                    event_name='lavka.eda.lavka.cart.opened',
                    event_id='1234567891',
                    order_id='123qwe1',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 06:30:01',
                    device_id='123asdf123',
                    event_name='checkout',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 06:30:02',
                    device_id='123asdf123',
                    event_name='test.eda.checkout.opened',
                    event_id='1234567891',
                    order_id='123qwe1',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 08:30:01',
                    device_id='123asdf123',
                    event_name='tracking',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 08:30:02',
                    device_id='123asdf123',
                    event_name='tracking',
                    event_id='1234567891',
                    order_id='123qwe1',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 23:30:01',
                    device_id='123asdf123',
                    event_name='lavka',
                    category_menu_cart_updated='"dish_count_changed":1',
                ),
                eda_appmetrica_record(
                    utc_event_dttm='2019-08-01 23:30:02',
                    device_id='123asdf123',
                    event_name='rest_menu',
                    event_id='1234567891',
                    order_id='123qwe1',
                    basket_updated='"dish_count_changed":1'
                ),
            ],
            [
                eda_appsession_record(
                    utc_session_start_dttm='2019-08-01 00:30:01',
                    utc_session_end_dttm='2019-08-01 00:30:02',
                    appsession_id='00db10d67555f0cd0d6601c6262cbe13',
                    utc_first_rest_menu_dttm=None,
                    utc_last_rest_menu_dttm=None,
                    appmetrica_device_id='123asdf123',
                    appmetrica_uuid='123asdf123',
                    duration_sec=1,
                    os_version_code='1.2.3',
                    is_rest_menu_opened_flg=False,
                    is_lavka_opened_flg=True,
                ),
                eda_appsession_record(
                    utc_session_start_dttm='2019-08-01 04:30:01',
                    utc_session_end_dttm='2019-08-01 04:30:02',
                    appsession_id='d9b5910b58ba28861aec4791207cb824',
                    utc_first_cart_dttm='2019-08-01 04:30:01',
                    utc_last_cart_dttm='2019-08-01 04:30:01',
                    appmetrica_device_id='123asdf123',
                    appmetrica_uuid='123asdf123',
                    duration_sec=1,
                    os_version_code='1.2.3',
                    is_lavka_opened_flg=True,
                ),
                eda_appsession_record(
                    utc_session_start_dttm='2019-08-01 06:30:01',
                    utc_session_end_dttm='2019-08-01 06:30:02',
                    appsession_id='2ff5c5444d75621e3f98c46678726a9c',
                    utc_first_checkout_dttm='2019-08-01 06:30:01',
                    utc_last_checkout_dttm='2019-08-01 06:30:02',
                    appmetrica_device_id='123asdf123',
                    appmetrica_uuid='123asdf123',
                    duration_sec=1,
                    os_version_code='1.2.3',
                ),
                eda_appsession_record(
                    utc_session_start_dttm='2019-08-01 08:30:01',
                    utc_session_end_dttm='2019-08-01 08:30:02',
                    appsession_id='7fb328f36dd32c8db5ced88cef37bdcd',
                    utc_first_tracking_dttm='2019-08-01 08:30:01',
                    utc_last_tracking_dttm='2019-08-01 08:30:02',
                    appmetrica_device_id='123asdf123',
                    appmetrica_uuid='123asdf123',
                    duration_sec=1,
                    os_version_code='1.2.3',
                ),
                eda_appsession_record(
                    utc_session_start_dttm='2019-08-01 10:30:01',
                    utc_session_end_dttm='2019-08-01 10:30:02',
                    appsession_id='c97a5463260fd556c5aeef91795b278f',
                    utc_first_rest_list_dttm='2019-08-01 10:30:01',
                    utc_last_rest_list_dttm='2019-08-01 10:30:02',
                    appmetrica_device_id='123asdf123',
                    appmetrica_uuid='123asdf123',
                    duration_sec=1,
                    os_version_code='1.2.3',
                ),
                eda_appsession_record(
                    utc_session_start_dttm='2019-08-01 23:30:01',
                    utc_session_end_dttm='2019-08-01 23:30:02',
                    appsession_id='019d5ba87ecf181a84cef6a30ec5951b',
                    utc_first_rest_menu_dttm='2019-08-01 23:30:02',
                    utc_last_rest_menu_dttm='2019-08-01 23:30:02',
                    utc_first_dish_count_changed_dttm='2019-08-01 23:30:02',
                    utc_last_dish_count_changed_dttm='2019-08-01 23:30:02',
                    appmetrica_device_id='123asdf123',
                    appmetrica_uuid='123asdf123',
                    duration_sec=1,
                    os_version_code='1.2.3',
                    is_rest_menu_opened_flg=True,
                    is_lavka_opened_flg=True,
                ),
            ],
            id='Check utc_dttm-s new'
        ),
        pytest.param(
            [
                eda_appmetrica_record(
                    event_id='1234567890',
                    place_name_list=['Wаверма', 'Мама, я дома'],
                    place_slug_list=['shavarma', 'mama_ya_doma'],
                ),
                eda_appmetrica_record(
                    event_id='1234567891',
                    place_name_list=['Wаверма', 'Мама, я дома', 'Doner Master'],
                    place_slug_list=['shavarma', 'mama_ya_doma', 'doner_master'],
                )
            ],
            [
                eda_appsession_record(
                    duration_sec=0,
                    appmetrica_uuid='123asdf123',
                    appmetrica_device_id='123asdf123',
                    order_id_paid_list=['123qwe'],
                    os_version_code='1.2.3',
                    utc_session_end_dttm='2019-08-01 10:00:01',
                    place_name_list=['Doner Master', 'Wаверма', 'Мама, я дома'],
                    place_slug_list=['doner_master', 'mama_ya_doma', 'shavarma'],
                )
            ],
            id='Check place list (name/slug)'
        ),
    ]
)
def test_eda_user_appsession_build(eda_appmetrica_events, eda_expected_sessions):
    session_builder = ApplicationSessionBuilder(ApplicationSession, '2019-08-03 23:59:59')

    cluster = MockCluster()
    job = cluster.job('test_session_build')
    actual_sessions = []
    job.table('stub') \
        .label('eda_appmetrica_events') \
        .groupby('device_id') \
        .sort('utc_event_dttm', 'sort_order', 'event_id') \
        .reduce(session_builder) \
        .label('actual_sessions')
    job.local_run(
        sources={'eda_appmetrica_events': StreamSource(eda_appmetrica_events)},
        sinks={'actual_sessions': ListSink(actual_sessions)}
    )

    actual_sessions = sorted(actual_sessions, key=lambda rec: (rec.get('device_id'), rec.get('utc_session_start_dttm')))

    assert [rec.to_dict() for rec in eda_expected_sessions] == [rec.to_dict() for rec in actual_sessions]
