from pprint import pformat

import pytest

from nile.api.v1 import MockCluster
from nile.api.v1.local import StreamSource
from nile.api.v1.local import ListSink

from eda_etl.layer.yt.cdm.user_product.eda_go_user_appsession.impl import ApplicationSessionBuilder
from eda_etl.layer.yt.cdm.user_product.eda_go_user_appsession.impl import ApplicationSession

from .impl import eda_go_appmetrica_record
from .impl import eda_go_appsession_record


@pytest.mark.parametrize(
    'appmetrica_events, expected_sessions',
    [
        pytest.param(
            [
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:00:01',
                    event_id='1234567890',
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                ),
            ],
            [
                eda_go_appsession_record(
                    utc_session_start_dttm='2019-08-01 10:00:01',
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='da7d3204ab680ab622d3961658d3384b',
                    event_id_list=['1234567890', '1234567891'],
                    duration_sec=1800,
                ),
            ],
            id='Base session with break: timeout',
        ),
        pytest.param(
            [
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:00:01',
                    event_id='1234567890',
                    app_version_code='12345',
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    app_version_code='54321',
                ),
            ],
            [
                eda_go_appsession_record(
                    utc_session_start_dttm='2019-08-01 10:00:01',
                    utc_session_end_dttm='2019-08-01 10:00:01',
                    appsession_id='da7d3204ab680ab622d3961658d3384b',
                    app_version_code='12345',
                    event_id_list=['1234567890'],
                    break_reason='app_version_change',
                    duration_sec=0,
                ),
                eda_go_appsession_record(
                    utc_session_start_dttm='2019-08-01 10:30:01',
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='8f1ccd71c26632842ffac8d29969fa3c',
                    app_version_code='54321',
                    event_id_list=['1234567891'],
                    break_reason='timeout',
                    duration_sec=0,
                ),
            ],
            id='Base session with break: app_version',
        ),
        pytest.param(
            [
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:00:01',
                    event_id='1234567890',
                    eda_client_id='abcdef',
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:00:02',
                    event_id='1234567892',
                    eda_client_id=None,
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    eda_client_id='klmnop',
                ),
            ],
            [
                eda_go_appsession_record(
                    utc_session_start_dttm='2019-08-01 10:00:01',
                    utc_session_end_dttm='2019-08-01 10:00:02',
                    appsession_id='da7d3204ab680ab622d3961658d3384b',
                    event_id_list=['1234567890', '1234567892'],
                    break_reason='eda_client_id_change',
                    duration_sec=1,
                    eda_client_id='abcdef',
                ),
                eda_go_appsession_record(
                    utc_session_start_dttm='2019-08-01 10:30:01',
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='8f1ccd71c26632842ffac8d29969fa3c',
                    event_id_list=['1234567891'],
                    break_reason='timeout',
                    duration_sec=0,
                    eda_client_id='klmnop',
                ),
            ],
            id='Base session with break: eda_client_id',
        ),
        pytest.param(
            [
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:00:01',
                    event_id='1234567890',
                    event_name='rest_menu',
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 12:30:01',
                    event_id='1234567891',
                ),
            ],
            [
                eda_go_appsession_record(
                    utc_session_start_dttm='2019-08-01 10:00:01',
                    utc_session_end_dttm='2019-08-01 10:00:01',
                    appsession_id='da7d3204ab680ab622d3961658d3384b',
                    event_id_list=['1234567890'],
                    break_reason='timeout',
                    duration_sec=0,
                    is_rest_menu_opened_flg=True,
                    utc_first_rest_menu_dttm='2019-08-01 10:00:01',
                    utc_last_rest_menu_dttm='2019-08-01 10:00:01',

                ),
                eda_go_appsession_record(
                    utc_session_start_dttm='2019-08-01 12:30:01',
                    utc_session_end_dttm='2019-08-01 12:30:01',
                    appsession_id='83c5c71baa050b4ac2c2f7d16f7ddee2',
                    event_id_list=['1234567891'],
                    break_reason='timeout',
                    duration_sec=0,
                    is_rest_menu_opened_flg=False,
                ),
            ],
            id='Check is_rest',
        ),
        pytest.param(
            [
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:00:01',
                    event_id='1234567890',
                    lat=1.1,
                    lon=2.2,
                    destination_lat=11.11,
                    destination_lon=22.22,
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 11:00:01',
                    event_id='1234567891',
                    lat=3.3,
                    lon=4.4,
                    destination_lat=33.33,
                    destination_lon=44.44,
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 14:30:01',
                    event_id='1234567894',
                    lat=47.212665,
                    lon=39.702643,
                    destination_lat=55.829537,
                    destination_lon=37.593938,
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 14:30:02',
                    event_id='1234567895',
                    lat=47.212665,
                    lon=39.702643,
                    destination_lat=55.829537,
                    destination_lon=37.593938,
                ),
            ],
            [
                eda_go_appsession_record(
                    utc_session_start_dttm='2019-08-01 10:00:01',
                    utc_session_end_dttm='2019-08-01 11:00:01',
                    appsession_id='da7d3204ab680ab622d3961658d3384b',
                    duration_sec=3600,
                    event_id_list=['1234567890', '1234567891'],
                    user_lat=3.3,
                    user_lon=4.4,
                    destination_lat=33.33,
                    destination_lon=44.44,
                    destination_diff_m=3350735.856011135,
                    user_move_diff_m=345819.26718250634,
                ),
                eda_go_appsession_record(
                    utc_session_start_dttm='2019-08-01 14:30:01',
                    utc_session_end_dttm='2019-08-01 14:30:02',
                    appsession_id='597b9a7ad9af4a54663b4adb570c12f3',
                    duration_sec=1,
                    event_id_list=['1234567894', '1234567895'],
                    user_lat=47.212665,
                    user_lon=39.702643,
                    destination_lat=55.829537,
                    destination_lon=37.593938,
                    destination_diff_m=0.0,
                    user_move_diff_m=0.0,
                ),
            ],
            id='Check lat/lon',
        ),
        pytest.param(
            [
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_name='rest_list',
                    event_id='1234567890',
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:02',
                    event_name='rest_list',
                    event_id='1234567891',
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 00:30:01',
                    event_name='rest_menu',
                    event_id='1234567892',
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 00:30:02',
                    event_id='1234567893',
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 04:30:01',
                    event_name='cart',
                    event_id='1234567894',
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 04:30:02',
                    event_name='cart',
                    event_id='1234567895',
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 06:30:01',
                    event_name='checkout',
                    event_id='1234567896',
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 06:30:02',
                    event_id='1234567897',
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 08:30:01',
                    event_name='tracking',
                    event_id='1234567898',
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 08:30:02',
                    event_name='tracking',
                    event_id='1234567899',
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 23:30:01',
                    event_name='dish_count_changed',
                    event_id='1234567900',
                    dish_count_changed=True,
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 23:30:02',
                    event_name='dish_count_changed',
                    event_id='1234567901',
                    dish_count_changed=True,
                ),
            ],
            [
                eda_go_appsession_record(
                    utc_session_start_dttm='2019-08-01 00:30:01',
                    utc_session_end_dttm='2019-08-01 00:30:02',
                    appsession_id='132a68ab82ed74270e8830431c0bbe6f',
                    utc_first_rest_menu_dttm='2019-08-01 00:30:01',
                    utc_last_rest_menu_dttm='2019-08-01 00:30:01',
                    duration_sec=1,
                    event_id_list=['1234567892', '1234567893'],
                    is_rest_menu_opened_flg=True,
                ),
                eda_go_appsession_record(
                    utc_session_start_dttm='2019-08-01 04:30:01',
                    utc_session_end_dttm='2019-08-01 04:30:02',
                    appsession_id='4a28beaa3e07aadb15b7fb6f21ab4cf2',
                    utc_first_cart_dttm='2019-08-01 04:30:01',
                    utc_last_cart_dttm='2019-08-01 04:30:02',
                    event_id_list=['1234567894', '1234567895'],
                    duration_sec=1,
                ),
                eda_go_appsession_record(
                    utc_session_start_dttm='2019-08-01 06:30:01',
                    utc_session_end_dttm='2019-08-01 06:30:02',
                    appsession_id='29bfeec9873ed0861198040cba7c774e',
                    utc_first_checkout_dttm='2019-08-01 06:30:01',
                    utc_last_checkout_dttm='2019-08-01 06:30:01',
                    duration_sec=1,
                    event_id_list=['1234567896', '1234567897'],
                ),
                eda_go_appsession_record(
                    utc_session_start_dttm='2019-08-01 08:30:01',
                    utc_session_end_dttm='2019-08-01 08:30:02',
                    appsession_id='6e5bfefa3916500b0c5d437ba839b47a',
                    utc_first_tracking_dttm='2019-08-01 08:30:01',
                    utc_last_tracking_dttm='2019-08-01 08:30:02',
                    event_id_list=['1234567898', '1234567899'],
                    duration_sec=1,
                ),
                eda_go_appsession_record(
                    utc_session_start_dttm='2019-08-01 10:30:01',
                    utc_session_end_dttm='2019-08-01 10:30:02',
                    appsession_id='8f1ccd71c26632842ffac8d29969fa3c',
                    utc_first_rest_list_dttm='2019-08-01 10:30:01',
                    utc_last_rest_list_dttm='2019-08-01 10:30:02',
                    event_id_list=['1234567890', '1234567891'],
                    duration_sec=1,
                ),
                eda_go_appsession_record(
                    utc_session_start_dttm='2019-08-01 23:30:01',
                    utc_session_end_dttm='2019-08-01 23:30:02',
                    appsession_id='275fa31b12f2832e37a11e5843fcad73',
                    utc_first_dish_count_changed_dttm='2019-08-01 23:30:01',
                    utc_last_dish_count_changed_dttm='2019-08-01 23:30:02',
                    duration_sec=1,
                    event_id_list=['1234567900', '1234567901'],
                ),
            ],
            id='Check first & last event utc_dttm-s',
        ),
        pytest.param(
            [
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:00:01',
                    event_id='1234567890',
                    place_slug_list=['demand']
                ),
                eda_go_appmetrica_record(
                    utc_event_dttm='2019-08-01 10:30:01',
                    event_id='1234567891',
                    place_slug_list=['eda']
                ),
            ],
            [
                eda_go_appsession_record(
                    utc_session_start_dttm='2019-08-01 10:00:01',
                    utc_session_end_dttm='2019-08-01 10:30:01',
                    appsession_id='da7d3204ab680ab622d3961658d3384b',
                    event_id_list=['1234567890', '1234567891'],
                    duration_sec=1800,
                    place_slug_list=['demand', 'eda']
                ),
            ],
            id='Check place slug list',
        ),
    ],
)
def test_eda_go_user_appsession_build(appmetrica_events, expected_sessions):
    cluster = MockCluster()
    job = cluster.job('test_session_build')
    actual_sessions = []
    job.table(
        'stub',
    ).label(
        'eda_go_appmetrica_events',
    ).groupby(
        'appmetrica_device_id',
    ).sort(
        'utc_event_dttm',
        'event_id',
    ).reduce(
        ApplicationSessionBuilder(ApplicationSession, '2019-08-03 23:59:59'),
    ).label(
        'actual_sessions',
    )
    job.local_run(
        sources={'eda_go_appmetrica_events': StreamSource(appmetrica_events)},
        sinks={'actual_sessions': ListSink(actual_sessions)},
    )
    actual_sessions = sorted(
        actual_sessions,
        key=lambda rec: (rec.get('appmetrica_device_id'), rec.get('utc_session_start_dttm')),
    )
    assert [r.to_dict() for r in expected_sessions] == [r.to_dict() for r in actual_sessions]
