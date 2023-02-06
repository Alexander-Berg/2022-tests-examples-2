from copy import deepcopy

from nile.processing.record import Record

EDA_APPMETRICA = dict(
    utc_event_dttm='2019-08-01 10:00:01',
    event_id='1234567890',
    app_platform_name='android',
    os_version_code='1.2.3',
    device_id='123asdf123',
    event_type='EVENT_CLIENT',
    event_name='abcder',
    event_value={},
    appmetrica_uuid='123asdf123',
    appmetrica_device_id='123asdf123',
    order_id='123qwe',
    app_version_code='12345',
    config_ab={},
    lat=1.1,
    lon=2.2,
    destination_lat=11.11,
    destination_lon=22.22,
    request_id='abcd123',
    eda_place_id_list=[14, 24, 34],
    eda_surge_val_list=[114, 224, 334],
    eda_client_id='1234',
    device_type='PHONE',
    eda_user_id=123,
    yandex_uid='123',
    plus_screen_available_flg=False,
    geobase_city_name='Moscow',
    geobase_city_name_ru='Москва',
    region_id=213,
)

EDA_APPSESSION_ATTRIBUTES = dict(
    device_id='123asdf123',
    utc_session_start_dttm='2019-08-01 10:00:01',
    utc_session_end_dttm='2019-08-01 10:30:01',
    appsession_id='9a8f8892b9016797405c5b3a4181818f',
    app_platform_name='android',
    app_version_code='12345',
    event_id_list=['1234567890', '1234567891'],
    os_version_code='1.2.4',
    break_reason='timeout',
    duration_sec=1800,
    appmetrica_uuid='123asdf124',
    appmetrica_device_id='123asdf124',
    is_lavka_opened_flg=False,
    is_rest_menu_opened_flg=False,
    is_filter_used_flg=False,
    is_rest_list_search_used_flg=False,
    is_rest_menu_search_used_flg=False,
    is_rest_menu_retail_opened_flg=False,
    is_rest_menu_restaurant_opened_flg=False,
    push_only_flg=False,
    config_ab_dict={},
    order_id_paid_list=['123qwe', '123qwe1'],
    order_id_paid_list_lavka=None,
    user_move_diff_m=0.0,
    destination_diff_m=0.0,
    user_lat=1.1,
    user_lon=2.2,
    destination_lat=11.11,
    destination_lon=22.22,
    eda_client_id='1234',
    utc_first_rest_list_dttm=None,
    utc_first_rest_menu_dttm=None,
    utc_first_cart_dttm=None,
    utc_first_checkout_dttm=None,
    utc_first_tracking_dttm=None,
    utc_last_rest_list_dttm=None,
    utc_last_rest_menu_dttm=None,
    utc_last_cart_dttm=None,
    utc_last_checkout_dttm=None,
    utc_last_tracking_dttm=None,
    device_type_name='PHONE',
    request_id_list=['abcd123'],
    first_request_eda_place_id_list=[14, 24, 34],
    first_request_eda_surge_val_list=[114, 224, 334],
    created_order_id_list=None,
    last_request_eda_place_id_list=[14, 24, 34],
    last_request_eda_surge_val_list=[114, 224, 334],
    utc_first_dish_count_changed_dttm=None,
    utc_last_dish_count_changed_dttm=None,
    eda_user_id=123,
    yandex_uid='123',
    plus_screen_available_flg=False,
    geobase_city_name='Moscow',
    geobase_city_name_ru='Москва',
    geobase_region_id=213,
    place_name_list=[],
    place_slug_list=[],
)


def create_default_record(default_args):
    def _record(**kwargs):
        attributes = deepcopy(default_args)
        attributes.update(**kwargs)
        return Record(**attributes)
    return _record


eda_appmetrica_record = create_default_record(EDA_APPMETRICA)
eda_appsession_record = create_default_record(EDA_APPSESSION_ATTRIBUTES)
