from copy import deepcopy

from nile.processing.record import Record

EDA_GO_APPMETRICA = dict(
    app_platform_name='android',
    app_version_code='1234',
    appmetrica_device_id='123asdf123',
    appmetrica_uuid='123asdf123',
    eda_client_id='abcdef',
    taxi_user_id='zxcvb',
    event_name='abcder',
    event_type='EVENT_CLIENT',
)

EDA_GO_APPSESSION_ATTRIBUTES = dict(
    app_platform_name='android',
    app_version_code='1234',
    appmetrica_device_id='123asdf123',
    appmetrica_uuid='123asdf123',
    break_reason='timeout',
    created_order_id_list=None,
    destination_diff_m=None,
    destination_lat=None,
    destination_lon=None,
    eda_client_id='abcdef',
    taxi_user_id='zxcvb',
    device_type_name=None,
    geobase_city_name=None,
    geobase_city_name_ru=None,
    geobase_region_id=None,
    is_filter_used_flg=False,
    is_rest_list_search_used_flg=False,
    is_rest_menu_opened_flg=False,
    is_rest_menu_restaurant_opened_flg=False,
    is_rest_menu_retail_opened_flg=False,
    is_rest_menu_search_used_flg=False,
    push_only_flg=False,
    os_version_code=None,
    order_id_paid_list=None,
    user_lat=None,
    user_lon=None,
    user_move_diff_m=None,
    utc_first_cart_dttm=None,
    utc_first_checkout_dttm=None,
    utc_first_dish_count_changed_dttm=None,
    utc_first_rest_list_dttm=None,
    utc_first_rest_menu_dttm=None,
    utc_first_tracking_dttm=None,
    utc_last_cart_dttm=None,
    utc_last_checkout_dttm=None,
    utc_last_dish_count_changed_dttm=None,
    utc_last_rest_list_dttm=None,
    utc_last_rest_menu_dttm=None,
    utc_last_tracking_dttm=None,
    yandex_uid=None,
    place_slug_list=[],
)


def create_default_record(default_args):
    def _record(**kwargs):
        attributes = deepcopy(default_args)
        attributes.update(**kwargs)
        return Record(**attributes)
    return _record


eda_go_appmetrica_record = create_default_record(EDA_GO_APPMETRICA)
eda_go_appsession_record = create_default_record(EDA_GO_APPSESSION_ATTRIBUTES)
