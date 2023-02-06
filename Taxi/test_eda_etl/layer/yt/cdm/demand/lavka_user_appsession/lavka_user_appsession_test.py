import pytest
from pprint import pformat

from nile.api.v1 import MockCluster
from nile.api.v1.local import StreamSource, ListSink

from eda_etl.layer.yt.cdm.demand.lavka_user_appsession.impl import LavkaApplicationSessionBuilder, ApplicationSession

from .impl import lavka_appmetrica_record, lavka_appsession_record


@pytest.mark.parametrize(
    'lavka_appmetrica_events, lavka_expected_sessions',
    [
        pytest.param(
            [
                lavka_appmetrica_record(),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    os_version_code='1.2.4',
                    device_id='123asdf123',
                    event_name='abcder1',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf123',
                    order_id='123qwe1',
                    app_version_code='123456',
                    max_lavka_surge_val=700,
                    lavka_surge_val=None,
                    device_type='LAPTOP',
                    request_id='abcd1234',
                    lavka_place_id=None,
                    eda_place_id_list=None,
                    eda_surge_val_list=None,
                    eda_client_id='1234',
                    region_id=1234,
                    place_city_name='Химки',
                    lavka_city_name='Москва',
                    personal_phone_id='124',
                    layout_id='124',
                    appmetrica_user_locale='enEN'
                )
            ],
            [
                lavka_appsession_record(
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='9a8f8892b9016797405c5b3a4181818f',
                    last_app_version_code='123456',
                    event_id_list=['1234567890','1234567891'],
                    os_version_code='1.2.4',
                    duration_sec=1800,
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf123',
                    region_id=1234,
                    detail_city_name='Химки',
                    agg_city_name='Москва',
                    phone_pd_id='124',
                    layout_id='124',
                    appmetrica_user_locale_code='enEN',
                )
            ],
            id='Base session with break: timeout'
        ),
        pytest.param(
            [
                lavka_appmetrica_record(),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 11:00:01',
                    event_id='1234567892',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 11:30:01',
                    event_id='1234567893',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 12:00:01',
                    event_id='1234567894',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 12:30:01',
                    event_id='1234567895',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 13:00:01',
                    event_id='1234567896',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 13:30:01',
                    event_id='1234567897',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 14:00:01',
                    event_id='1234567898',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 14:30:01',
                    event_id='1234567899',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 15:00:01',
                    event_id='12345678910',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 15:30:01',
                    event_id='12345678911',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 16:00:01',
                    event_id='12345678912',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 16:30:01',
                    event_id='12345678913',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 17:00:01',
                    event_id='12345678914',
                    os_version_code='1.2.4',
                    event_name='abcder1',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf123',
                )
            ],
            [
                lavka_appsession_record(
                    utc_session_end_dttm='2019-08-01 16:00:01',
                    appsession_id='9a8f8892b9016797405c5b3a4181818f',
                    event_id_list=['1234567890', '1234567891', '1234567892', '1234567893', '1234567894',
                                   '1234567895', '1234567896', '1234567897', '1234567898', '1234567899',
                                   '12345678910', '12345678911', '12345678912'],
                    os_version_code='1.2.3',
                    break_reason='session_duration',
                    duration_sec=21600,
                    appmetrica_uuid='123asdf123',
                    appmetrica_device_id='123asdf123',

                ),
                lavka_appsession_record(
                    utc_session_start_dttm='2019-08-01 16:30:01',
                    utc_session_end_dttm='2019-08-01 17:00:01',
                    appsession_id='54991b017b2ebbd1de2116fc717c9d6e',
                    event_id_list=['12345678913', '12345678914'],
                    os_version_code='1.2.4',
                    break_reason='timeout',
                    duration_sec=1800,
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf123',
                ),
            ],
            id='Base session with break: session_duration'
        ),
        pytest.param(
            [
                lavka_appmetrica_record(),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    os_version_code='1.2.4',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf123',
                    app_version_code='123456',
                    battery_level=None,
                ),
                lavka_appmetrica_record(
                    appmetrica_device_id='123asdf124',
                    battery_level=None,
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    os_version_code='1.2.4',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    app_version_code='123456',
                    battery_level=None,
                ),
                lavka_appmetrica_record(
                    appmetrica_device_id='123asdf125',
                    battery_level=90,
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    os_version_code='1.2.4',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf125',
                    app_version_code='123456',
                    battery_level=80,
                ),
                lavka_appmetrica_record(
                    appmetrica_device_id='123asdf126',
                    battery_level=80,
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    os_version_code='1.2.4',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf126',
                    app_version_code='123456',
                    battery_level=90,
                ),
            ],
            [
                lavka_appsession_record(
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='9a8f8892b9016797405c5b3a4181818f',
                    last_app_version_code='123456',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf123',
                ),
                lavka_appsession_record(
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='6e3d4d21acd9cfa187f890571a00a2c4',
                    last_app_version_code='123456',
                    appmetrica_device_id='123asdf124',
                    battery_level_pcnt=None,
                    battery_level_diff_pcnt=None,
                ),
                lavka_appsession_record(
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='ed3c811cc26988f242703fd3c532a4d5',
                    last_app_version_code='123456',
                    appmetrica_device_id='123asdf125',
                    battery_level_pcnt=90,
                    battery_level_diff_pcnt=10,
                ),
                lavka_appsession_record(
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='009f7564b35159eb1726ab68aeb22912',
                    last_app_version_code='123456',
                    appmetrica_device_id='123asdf126',
                    battery_level_pcnt=80,
                    battery_level_diff_pcnt=-10,
                )
            ],
            id='Check battery'
        ),
        pytest.param(
            [
                lavka_appmetrica_record(
                    app='Browser',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    os_version_code='1.2.4',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf123',
                    app_version_code=None,
                    app='Lavka',
                ),
                lavka_appmetrica_record(
                    app='Browser',
                    appmetrica_device_id='123asdf124',
                    app_version_code=None,
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    os_version_code='1.2.4',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    app_version_code='000',
                    app='Lavka',
                )
            ],
            [
                lavka_appsession_record(
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='9a8f8892b9016797405c5b3a4181818f',
                    last_app_version_code=None,
                    event_id_list=['1234567890','1234567891'],
                    os_version_code='1.2.4',
                    duration_sec=1800,
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf123',
                    session_app_list=['Browser', 'Lavka'],
                ),
                lavka_appsession_record(
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='6e3d4d21acd9cfa187f890571a00a2c4',
                    last_app_version_code='000',
                    first_app_version_code=None,
                    event_id_list=['1234567890', '1234567891'],
                    os_version_code='1.2.4',
                    duration_sec=1800,
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf124',
                    session_app_list=['Browser', 'Lavka'],
                )
            ],
            id='Check first_/last_app_version_code'
        ),
        pytest.param(
            [

                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 13:30:00',
                    event_id='2234567890',
                    place_id=1,
                    surge_val=0,
                    delivery_cost=99,
                    offer_id='111',
                    zone_mode='active',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 13:30:02',
                    event_id='2234567891',
                    place_id=1,
                    surge_val=0,
                    delivery_cost=99,
                    offer_id='111',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 13:30:03',
                    event_id='2234567892',
                    place_id=2,
                    surge_val=700,
                    delivery_cost=0,
                    offer_id='222',
                    zone_mode='active',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 13:30:03',
                    event_id='22345678921',
                    zone_mode='unactive',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 13:30:04',
                    event_id='2234567893',
                    place_id=None,
                    surge_val=None,
                    delivery_cost=None,
                    offer_id=None,
                    zone_mode='unactive',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 13:30:05',
                    event_id='2234567894',
                    place_id=2,
                    surge_val=700,
                    delivery_cost=0,
                    offer_id='222',
                    zone_mode='active',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 13:30:06',
                    event_id='2234567895',
                    place_id=1,
                    surge_val=0,
                    delivery_cost=69,
                    offer_id='333',
                    zone_mode=None,
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 13:30:07',
                    event_id='2234567896',
                    place_id=1,
                    surge_val=0,
                    delivery_cost=69,
                    offer_id='333',
                ),
            ],
            [
                lavka_appsession_record(
                    utc_session_end_dttm='2019-08-01 13:30:07',
                    utc_session_start_dttm='2019-08-01 13:30:00',
                    appsession_id='c79acd12bd13eb54cca6912b069330a7',
                    event_id_list=['2234567890', '2234567891', '2234567892', '22345678921', '2234567893',
                                   '2234567894', '2234567895', '2234567896'],
                    os_version_code='1.2.3',
                    break_reason='timeout',
                    duration_sec=7,
                    appmetrica_uuid='123asdf123',
                    appmetrica_device_id='123asdf123',
                    place_id_list=[1, 2, 1],
                    surge_val_list=[0, 700, 0],
                    delivery_cost_list=[99, 0, 69],
                    offer_id_list=['111', '222', '333'],
                    zone_mode_list=[
                        ('2019-08-01 13:30:00', 'active'),
                        ('2019-08-01 13:30:04', 'unactive'),
                        ('2019-08-01 13:30:05', 'active'),
                    ],
                    misclick_flg=True
                ),
            ],
            id='Check surge_val_list, place_id_list, delivery_cost_list, offer_id_list, zone_mode_list'
        ),
        pytest.param(
            [
                lavka_appmetrica_record(),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    category_menu_opened={'1': 1},
                    autologin_successfully_finished='true',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 11:00:01',
                    event_id='1234567892',
                    category_menu_cart_updated={'1': 1},
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 11:30:01',
                    event_id='1234567893',
                    category_menu_cart_updated={'1': 1},
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 12:00:01',
                    event_id='1234567894',
                    cart_loaded={'1': 1},
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 12:30:01',
                    event_id='1234567895',
                    checkout_loaded={'1': 1},
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 13:00:01',
                    event_id='1234567896',
                    event_name='lavka',
                    is_background_flg=True,
                    category_list_opened={'1': 1},
                ),
                lavka_appmetrica_record(
                    appmetrica_device_id='123asdf126',
                    is_background_flg=True,
                ),
                lavka_appmetrica_record(
                    appmetrica_device_id='123asdf126',
                    event_id='1234567891',
                    is_background_flg=True,
                    confirmed_flg=True,
                    order_id='123',
                    event_name='eda.checkout.first_purchase',
                ),
                lavka_appmetrica_record(
                    appmetrica_device_id='123asdf127',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    event_name='superapp.eda.lavka.category_menu.opened',
                    appmetrica_device_id='123asdf127',

                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 11:00:01',
                    event_id='1234567892',
                    event_name='superapp.eda.cart.basket_updated',
                    appmetrica_device_id='123asdf127',

                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 11:30:01',
                    event_id='1234567893',
                    event_name='superapp.eda.lavka.cart_updated',
                    appmetrica_device_id='123asdf127',

                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 12:00:01',
                    event_id='1234567894',
                    event_name='superapp.eda.lavka.cart.opened',
                    appmetrica_device_id='123asdf127',

                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 12:30:01',
                    event_id='1234567895',
                    event_name='eda.lavka.checkout.opened',
                    appmetrica_device_id='123asdf127',

                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 12:30:02',
                    event_id='12345678951',
                    event_name='eda.lavka.backend_search.opened',
                    appmetrica_device_id='123asdf127',

                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 12:30:03',
                    event_id='12345678952',
                    event_name='eda.lavka.backend_search.suggest_clicked',
                    appmetrica_device_id='123asdf127',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 12:30:04',
                    event_id='12345678953',
                    event_name='eda.lavka.onboarding.opened',
                    appmetrica_device_id='123asdf127',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 12:30:06',
                    event_id='12345678955',
                    event_name='eda.lavka.category_list.loaded',
                    appmetrica_device_id='123asdf127',
                    active_parcel_ids=['11111111111111111111111111111111000200010001:st-pa'],
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 13:00:01',
                    event_id='1234567896',
                    event_name='lavka',
                    is_background_flg=True,
                    appmetrica_device_id='123asdf127',
                ),
            ],
            [
                lavka_appsession_record(
                    utc_session_end_dttm='2019-08-01 13:00:01',
                    appsession_id='9a8f8892b9016797405c5b3a4181818f',
                    event_id_list=['1234567890', '1234567891', '1234567892', '1234567893', '1234567894',
                                   '1234567895', '1234567896'],
                    os_version_code='1.2.3',
                    break_reason='timeout',
                    duration_sec=10800,
                    appmetrica_uuid='123asdf123',
                    appmetrica_device_id='123asdf123',
                    is_checkout_succeeded_flg=False,
                    is_background_flg=False,
                    is_menu_opened_flg=True,
                    is_cart_updated_flg=True,
                    is_cart_opened_flg=True,
                    is_checkout_opened_flg=True,
                    has_important_event_flg=True,
                    is_category_list_opened_flg=True,
                    utc_first_cart_opened_dttm='2019-08-01 12:00:01',
                    utc_first_cart_updated_dttm='2019-08-01 11:00:01',
                    utc_first_category_list_opened_dttm='2019-08-01 13:00:01',
                    utc_first_checkout_opened_dttm='2019-08-01 12:30:01',
                    utc_first_menu_opened_dttm='2019-08-01 10:30:01',
                    utc_last_cart_opened_dttm='2019-08-01 12:00:01',
                    utc_last_cart_updated_dttm='2019-08-01 11:30:01',
                    utc_last_category_list_opened_dttm='2019-08-01 13:00:01',
                    utc_last_checkout_opened_dttm='2019-08-01 12:30:01',
                    utc_last_menu_opened_dttm='2019-08-01 10:30:01',
                    login_type_id=2,
                ),
                lavka_appsession_record(
                    utc_session_end_dttm='2019-08-01 10:00:01',
                    appsession_id='009f7564b35159eb1726ab68aeb22912',
                    event_id_list=['1234567890', '1234567891'],
                    duration_sec=0,
                    appmetrica_device_id='123asdf126',
                    is_checkout_succeeded_flg=True,
                    is_background_flg=True,
                    os_version_code='1.2.3',
                    appmetrica_uuid='123asdf123',
                    order_id_paid_list=['123'],
                    order_id_created_list=['123'],
                    order_paid_from_app_list=['Lavka'],
                    utc_first_checkout_succeeded_dttm='2019-08-01 10:00:01',
                    utc_last_checkout_succeeded_dttm='2019-08-01 10:00:01',
                    checkout_attempt_flg=True,
                    utc_first_checkout_attempt_dttm='2019-08-01 10:00:01',
                    utc_last_checkout_attempt_dttm='2019-08-01 10:00:01',
                ),
                lavka_appsession_record(
                    utc_session_end_dttm='2019-08-01 13:00:01',
                    appsession_id='39362e0f2dae0d4490263bf5042753f3',
                    event_id_list=['1234567890', '1234567891', '1234567892', '1234567893', '1234567894',
                                   '1234567895', '12345678951', '12345678952', '12345678953', '12345678955',
                                   '1234567896'],
                    os_version_code='1.2.3',
                    break_reason='timeout',
                    duration_sec=10800,
                    appmetrica_uuid='123asdf123',
                    appmetrica_device_id='123asdf127',
                    is_checkout_succeeded_flg=False,
                    is_background_flg=False,
                    is_menu_opened_flg=True,
                    is_cart_updated_flg=True,
                    is_cart_opened_flg=True,
                    is_checkout_opened_flg=True,
                    has_important_event_flg=True,
                    utc_first_cart_opened_dttm='2019-08-01 12:00:01',
                    utc_first_cart_updated_dttm='2019-08-01 11:00:01',
                    utc_first_checkout_opened_dttm='2019-08-01 12:30:01',
                    utc_first_menu_opened_dttm='2019-08-01 10:30:01',
                    utc_last_cart_opened_dttm='2019-08-01 12:00:01',
                    utc_last_cart_updated_dttm='2019-08-01 11:30:01',
                    utc_last_checkout_opened_dttm='2019-08-01 12:30:01',
                    utc_last_menu_opened_dttm='2019-08-01 10:30:01',
                    search_opened_flg=True,
                    utc_first_search_opened_dttm='2019-08-01 12:30:02',
                    utc_last_search_opened_dttm='2019-08-01 12:30:02',
                    search_succeeded_flg=True,
                    utc_first_search_succeeded_dttm='2019-08-01 12:30:03',
                    utc_last_search_succeeded_dttm='2019-08-01 12:30:03',
                    onboarding_opened_flg=True,
                    utc_first_onboarding_opened_dttm='2019-08-01 12:30:04',
                    utc_last_onboarding_opened_dttm='2019-08-01 12:30:04',
                    parcel_market_flg=True,
                ),
            ],
            id='Check event flags'
        ),
        pytest.param(
            [
                lavka_appmetrica_record(),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    event_name='eda.checkout.first_purchase',
                    order_id='11',
                    confirmed_flg=True,
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 11:00:01',
                    event_id='1234567892',
                    event_name='checkout',
                    order_id='22',
                    app='Taxi',
                    repeat_purchase={
                        "type: applepay": {
                            "order_id": "200810-356006"
                        }
                    },
                    confirmed_flg=True,
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 11:30:01',
                    event_id='1234567893',
                    event_name='eda.checkout.order_created',
                    order_id='33',
                    app='Eda',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 12:00:01',
                    event_id='1234567894',
                    event_name='checkout',
                    order_id='44',
                    app='Eda',
                    order_created={
                        "type: applepay":{
                            "order_id":"200810-356006"
                        }
                    }
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 12:30:01',
                    event_id='1234567895',
                    event_name='eda.checkout.11first_purchase',
                    order_id='111',
                    app='Eda',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 13:00:01',
                    event_id='1234567896',
                    event_name='eda.checkout.11order_created',
                    order_id='222',
                    app='Eda',
                ),
            ],
            [
                lavka_appsession_record(
                    utc_session_end_dttm='2019-08-01 13:00:01',
                    appsession_id='9a8f8892b9016797405c5b3a4181818f',
                    event_id_list=['1234567890', '1234567891', '1234567892', '1234567893', '1234567894',
                                   '1234567895', '1234567896'],
                    os_version_code='1.2.3',
                    break_reason='timeout',
                    duration_sec=10800,
                    appmetrica_uuid='123asdf123',
                    appmetrica_device_id='123asdf123',
                    order_id_paid_list=['11', '22'],
                    order_id_created_list=['11', '22', '33', '44'],
                    order_paid_from_app_list=['Lavka', 'Taxi'],
                    session_app_list=['Lavka', 'Taxi', 'Eda'],
                    is_checkout_succeeded_flg=True,
                    utc_first_checkout_succeeded_dttm='2019-08-01 10:30:01',
                    utc_last_checkout_succeeded_dttm='2019-08-01 11:00:01',
                    checkout_attempt_flg=True,
                    utc_first_checkout_attempt_dttm='2019-08-01 10:30:01',
                    utc_last_checkout_attempt_dttm='2019-08-01 12:00:01',
                ),
            ],
            id='Check order_lists'
        ),
        pytest.param(
            [
                lavka_appmetrica_record(
                    user_id='z123',
                ),
                lavka_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    os_version_code='1.2.4',
                    device_id='123asdf123',
                    event_name='abcder1',
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf123',
                    order_id='123qwe1',
                    app_version_code='123456',
                    max_lavka_surge_val=700,
                    lavka_surge_val=None,
                    device_type='LAPTOP',
                    request_id='abcd1234',
                    lavka_place_id=None,
                    eda_place_id_list=None,
                    eda_surge_val_list=None,
                    eda_client_id='1234',
                    region_id=1234,
                    place_city_name='Химки',
                    lavka_city_name='Москва',
                    personal_phone_id='124',
                    layout_id='124',
                    appmetrica_user_locale='enEN',
                    user_id='123',
                )
            ],
            [
                lavka_appsession_record(
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='9a8f8892b9016797405c5b3a4181818f',
                    last_app_version_code='123456',
                    event_id_list=['1234567890', '1234567891'],
                    os_version_code='1.2.4',
                    duration_sec=1800,
                    appmetrica_uuid='123asdf124',
                    appmetrica_device_id='123asdf123',
                    region_id=1234,
                    detail_city_name='Химки',
                    agg_city_name='Москва',
                    phone_pd_id='124',
                    layout_id='124',
                    appmetrica_user_locale_code='enEN',
                    is_registered_flg=True,
                    utc_registered_dttm='2019-08-01 10:30:01',
                    user_id_list=['123','z123'],
                    login_type_id=1,
                )
            ],
            id='Check registered flg'
        ),
    ]
)
def test_lavka_user_appsession_build(lavka_appmetrica_events, lavka_expected_sessions):
    session_builder = LavkaApplicationSessionBuilder(ApplicationSession, '2019-08-03 23:59:59')

    cluster = MockCluster()
    job = cluster.job('test_session_build')
    actual_sessions = []
    job.table('stub') \
        .label('lavka_appmetrica_events') \
        .groupby('appmetrica_device_id') \
        .sort('utc_event_dttm', 'sort_order', 'event_id') \
        .reduce(session_builder) \
        .label('actual_sessions')
    job.local_run(
        sources={'lavka_appmetrica_events': StreamSource(lavka_appmetrica_events)},
        sinks={'actual_sessions': ListSink(actual_sessions)}
    )

    actual_sessions = sorted(
        actual_sessions,
        key=lambda rec: (rec.get('appmetrica_device_id'), rec.get('utc_session_start_dttm'))
    )

    assert sorted(lavka_expected_sessions) == actual_sessions, \
        'Expected sessions is different from actual:\nexpected\n{},\nactual\n{}' \
            .format(pformat(lavka_expected_sessions), pformat(actual_sessions))
