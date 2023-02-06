import pytest
from pprint import pformat
from datetime import timedelta, datetime

from nile.api.v1 import MockCluster
from nile.api.v1.local import StreamSource, ListSink

from dmp_suite import datetime_utils as dtu

from demand_etl.layer.yt.cdm.product_user.user_appsession.impl import \
    ApplicationSessionBuilder, ApplicationSession, ScenarioSession, SubscenarioSession, ScreenSession

from .impl import event, application, scenario, subscenario, screen


@pytest.mark.parametrize(
    'events, expected_application, expected_scenario, expected_subscenario, expected_screen',
    [
        pytest.param(
            [
                event(
                    utc_event_dttm='2019-08-01 10:00:00'
                ),
                event(
                    utc_event_dttm='2019-08-01 10:29:59'
                ),
                event(
                    utc_event_dttm='2019-08-01 10:59:59'
                ),
                event(
                    utc_event_dttm='2019-08-01 11:30:00'
                )
            ],
            [
                application(
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    utc_session_end_dttm='2019-08-01 10:59:59',
                    break_reason='timeout'
                ),
                application(
                    utc_session_start_dttm='2019-08-01 11:30:00',
                    utc_session_end_dttm='2019-08-01 11:30:00',
                    break_reason='timeout'
                )
            ],
            None,
            None,
            None,
            id='Break reason test: timeout'
        ),
        pytest.param(
            [
                event(
                    utc_event_dttm=dtu.format_datetime(
                        dtu.parse_datetime('2019-08-01 00:00:00') + timedelta(minutes=30 * i)
                    )
                ) for i in range(10)
            ],
            [
                application(
                    utc_session_start_dttm='2019-08-01 00:00:00',
                    utc_session_end_dttm='2019-08-01 03:00:00',
                    break_reason='session_duration'
                ),
                application(
                    utc_session_start_dttm='2019-08-01 03:30:00',
                    utc_session_end_dttm='2019-08-01 04:30:00',
                    break_reason='timeout'
                )
            ],
            None,
            None,
            None,
            id='Break reason test: session duration'
        ),
        pytest.param(
            [
                event(utc_event_dttm=dtu.format_datetime(datetime(2019, 8, 1) + i * timedelta(milliseconds=100)))
                for i in range(25000)
            ],
            [
                application(
                    utc_session_start_dttm='2019-08-01 00:00:00',
                    utc_session_end_dttm='2019-08-01 00:33:19',
                    break_reason='event_cnt_limit'
                ),
                application(
                    utc_session_start_dttm='2019-08-01 00:33:20',
                    utc_session_end_dttm='2019-08-01 00:41:39',
                    break_reason='timeout'
                )
            ],
            None,
            None,
            None,
            id='Break reason test: event count limit'
        ),
        pytest.param(
            [
                event(
                    utc_event_dttm='2019-08-01 10:00:00',
                    yandex_uid=None
                ),
                event(
                    utc_event_dttm='2019-08-01 10:00:05',
                    yandex_uid='foo'
                ),
                event(
                    utc_event_dttm='2019-08-01 10:00:10',
                    yandex_uid='foo'
                ),
                event(
                    utc_event_dttm='2019-08-01 10:00:15',
                    yandex_uid='bar'
                ),
                event(
                    utc_event_dttm='2019-08-01 10:00:20',
                    yandex_uid=None
                )
            ],
            [
                application(
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    utc_session_end_dttm='2019-08-01 10:00:15',
                    yandex_uid_list=['bar', 'foo'],
                    break_reason='reset_yandex_uid'
                ),
                application(
                    utc_session_start_dttm='2019-08-01 10:00:20',
                    utc_session_end_dttm='2019-08-01 10:00:20',
                    yandex_uid_list=[],
                    break_reason='timeout'
                )
            ],
            None,
            None,
            None,
            id='Break reason test: reset appmetrica uid'
        ),
        pytest.param(
            [
                event(
                    utc_event_dttm='2019-08-01 10:00:00',
                    application_version='23'
                ),
                event(
                    utc_event_dttm='2019-08-01 10:05:00',
                    application_version='23'
                ),
                event(
                    utc_event_dttm='2019-08-01 10:10:00',
                    application_version='42'
                )
            ],
            [
                application(
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    utc_session_end_dttm='2019-08-01 10:05:00',
                    break_reason='application_version_change',
                    application_version='23'
                ),
                application(
                    utc_session_start_dttm='2019-08-01 10:10:00',
                    utc_session_end_dttm='2019-08-01 10:10:00',
                    break_reason='timeout',
                    application_version='42'
                )
            ],
            None,
            None,
            None,
            id='Break reason test: application version change'
        ),
        pytest.param(
            [
                event(
                    utc_event_dttm='2019-08-01 10:00:00',
                    application_version='16',
                    yandex_uid='foo'
                ),
                event(
                    utc_event_dttm='2019-08-01 10:31:00',
                    application_version='23',
                    yandex_uid=None
                ),
                event(
                    utc_event_dttm='2019-08-01 10:31:01',
                    application_version='23',
                    yandex_uid='foo'
                ),
                event(
                    utc_event_dttm='2019-08-01 10:36:00',
                    application_version='42',
                    yandex_uid=None
                ),
                event(
                    utc_event_dttm='2019-08-02 11:40:00',
                    application_version='42',
                    yandex_uid=None
                )
            ],
            [
                application(
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    utc_session_end_dttm='2019-08-01 10:00:00',
                    application_version='16',
                    yandex_uid_list=['foo'],
                    break_reason='timeout'
                ),
                application(
                    utc_session_start_dttm='2019-08-01 10:31:00',
                    utc_session_end_dttm='2019-08-01 10:31:01',
                    application_version='23',
                    yandex_uid_list=['foo'],
                    break_reason='application_version_change'
                ),
                application(
                    utc_session_start_dttm='2019-08-01 10:36:00',
                    utc_session_end_dttm='2019-08-01 10:36:00',
                    application_version='42',
                    yandex_uid_list=[],
                    break_reason='timeout'
                ),
                application(
                    utc_session_start_dttm='2019-08-02 11:40:00',
                    utc_session_end_dttm='2019-08-02 11:40:00',
                    application_version='42',
                    yandex_uid_list=[],
                    break_reason='timeout'
                )
            ],
            None,
            None,
            None,
            id='Break reason test: multiply break reason'
        ),
        pytest.param(
            [
                event(
                    utc_event_dttm='2019-08-01 10:00:00',
                    scenario='scenario_0',
                    subscenario='subscenario_0',
                    screen='screen_0',
                ),
                event(
                    utc_event_dttm='2019-08-01 10:01:00',
                    scenario='scenario_1',
                    subscenario='subscenario_0',
                    screen='screen_0',
                ),
                event(
                    utc_event_dttm='2019-08-01 10:02:00',
                    scenario='scenario_1',
                    subscenario='subscenario_1',
                    screen='screen_0',
                ),
                event(
                    utc_event_dttm='2019-08-01 10:03:00',
                    scenario='scenario_1',
                    subscenario='subscenario_1',
                    screen='screen_1',
                ),
                event(
                    utc_event_dttm='2019-08-01 10:04:00',
                    scenario='scenario_2',
                    subscenario='subscenario_2',
                    screen='screen_2',
                )
            ],
            None,
            [
                scenario(
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    utc_session_end_dttm='2019-08-01 10:00:59',
                    scenario='scenario_0',
                    break_reason='new_scenario'
                ),
                scenario(
                    utc_session_start_dttm='2019-08-01 10:01:00',
                    utc_session_end_dttm='2019-08-01 10:03:59',
                    scenario='scenario_1',
                    break_reason='new_scenario'
                ),
                scenario(
                    utc_session_start_dttm='2019-08-01 10:04:00',
                    utc_session_end_dttm='2019-08-01 10:04:00',
                    scenario='scenario_2',
                    break_reason='timeout'
                )
            ],
            [
                subscenario(
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    utc_session_end_dttm='2019-08-01 10:01:59',
                    subscenario='subscenario_0',
                    break_reason='new_subscenario'
                ),
                subscenario(
                    utc_session_start_dttm='2019-08-01 10:02:00',
                    utc_session_end_dttm='2019-08-01 10:03:59',
                    subscenario='subscenario_1',
                    break_reason='new_subscenario'
                ),
                subscenario(
                    utc_session_start_dttm='2019-08-01 10:04:00',
                    utc_session_end_dttm='2019-08-01 10:04:00',
                    subscenario='subscenario_2',
                    break_reason='timeout'
                )
            ],
            [
                screen(
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    utc_session_end_dttm='2019-08-01 10:02:59',
                    screen='screen_0',
                    break_reason='new_screen'
                ),
                screen(
                    utc_session_start_dttm='2019-08-01 10:03:00',
                    utc_session_end_dttm='2019-08-01 10:03:59',
                    screen='screen_1',
                    break_reason='new_screen'
                ),
                screen(
                    utc_session_start_dttm='2019-08-01 10:04:00',
                    utc_session_end_dttm='2019-08-01 10:04:00',
                    screen='screen_2',
                    break_reason='timeout'
                )
            ],
            id='Break reason test: subsession break'
        ),
        pytest.param(
            [
                event(
                    utc_event_dttm='2019-08-01 10:00:00',
                    application_version='16',
                    scenario='scenario_0',
                    subscenario='subscenario_0',
                    screen='screen_0',
                ),
                event(
                    utc_event_dttm='2019-08-01 10:01:00',
                    application_version='23',
                    scenario='scenario_1',
                    subscenario='subscenario_0',
                    screen='screen_0',
                ),
                event(
                    utc_event_dttm='2019-08-01 10:02:00',
                    application_version='42',
                    scenario='scenario_2',
                    subscenario='subscenario_2',
                    screen='screen_2',
                )
            ],
            [
                application(
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    utc_session_end_dttm='2019-08-01 10:00:00',
                    application_version='16',
                    break_reason='application_version_change'
                ),
                application(
                    utc_session_start_dttm='2019-08-01 10:01:00',
                    utc_session_end_dttm='2019-08-01 10:01:00',
                    application_version='23',
                    break_reason='application_version_change'
                ),
                application(
                    utc_session_start_dttm='2019-08-01 10:02:00',
                    utc_session_end_dttm='2019-08-01 10:02:00',
                    application_version='42',
                    break_reason='timeout'
                )
            ],
            [
                scenario(
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    utc_session_end_dttm='2019-08-01 10:00:00',
                    scenario='scenario_0',
                    break_reason='application_version_change'
                ),
                scenario(
                    utc_session_start_dttm='2019-08-01 10:01:00',
                    utc_session_end_dttm='2019-08-01 10:01:00',
                    scenario='scenario_1',
                    break_reason='application_version_change'
                ),
                scenario(
                    utc_session_start_dttm='2019-08-01 10:02:00',
                    utc_session_end_dttm='2019-08-01 10:02:00',
                    scenario='scenario_2',
                    break_reason='timeout'
                )
            ],
            [
                subscenario(
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    utc_session_end_dttm='2019-08-01 10:00:00',
                    subscenario='subscenario_0',
                    break_reason='application_version_change'
                ),
                subscenario(
                    utc_session_start_dttm='2019-08-01 10:01:00',
                    utc_session_end_dttm='2019-08-01 10:01:00',
                    subscenario='subscenario_0',
                    break_reason='application_version_change'
                ),
                subscenario(
                    utc_session_start_dttm='2019-08-01 10:02:00',
                    utc_session_end_dttm='2019-08-01 10:02:00',
                    subscenario='subscenario_2',
                    break_reason='timeout'
                )
            ],
            [
                screen(
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    utc_session_end_dttm='2019-08-01 10:00:00',
                    screen='screen_0',
                    break_reason='application_version_change'
                ),
                screen(
                    utc_session_start_dttm='2019-08-01 10:01:00',
                    utc_session_end_dttm='2019-08-01 10:01:00',
                    screen='screen_0',
                    break_reason='application_version_change'
                ),
                screen(
                    utc_session_start_dttm='2019-08-01 10:02:00',
                    utc_session_end_dttm='2019-08-01 10:02:00',
                    screen='screen_2',
                    break_reason='timeout'
                )
            ],
            id='Break reason test: subsession break from application session'
        ),
        pytest.param(
            [
                event(
                    utc_event_dttm='2019-08-01 10:00:00',
                    scenario='scenario_0'
                ),
                event(
                    utc_event_dttm='2019-08-01 10:01:00',
                    scenario='scenario_1'
                ),
                event(
                    utc_event_dttm='2019-08-01 10:07:30',
                    scenario='scenario_1'
                ),
                event(
                    utc_event_dttm='2019-08-01 12:00:00',
                    scenario='scenario_2'
                )
            ],
            [
                application(
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    utc_session_end_dttm='2019-08-01 10:07:30',
                    duration_sec=450
                ),
                application(
                    utc_session_start_dttm='2019-08-01 12:00:00',
                    utc_session_end_dttm='2019-08-01 12:00:00',
                    duration_sec=0
                )
            ],
            [
                scenario(
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    utc_session_end_dttm='2019-08-01 10:00:59',
                    scenario='scenario_0',
                    duration_sec=0
                ),
                scenario(
                    utc_session_start_dttm='2019-08-01 10:01:00',
                    utc_session_end_dttm='2019-08-01 10:07:30',
                    scenario='scenario_1',
                    duration_sec=390
                ),
                scenario(
                    utc_session_start_dttm='2019-08-01 12:00:00',
                    utc_session_end_dttm='2019-08-01 12:00:00',
                    scenario='scenario_2',
                    duration_sec=0
                )
            ],
            None,
            None,
            id='Attribute test: duration'
        ),
        pytest.param(
            [
                event(
                    utc_event_dttm='2019-08-01 10:00:00',
                    os_version='450',
                    battery_level=88,
                    active_order_cnt=0,
                    tariff='econom',
                    scenario='scenarion_0',
                    latitude=None,
                    longitude=None,
                    account_type='yandex',
                    api_key='3',
                    application_platform='ios',
                    event_id='101'
                ),
                event(
                    utc_event_dttm='2019-08-01 10:01:00',
                    os_version='451',
                    battery_level=80,
                    lower_power_mode_flg=True,
                    scenario='scenarion_1',
                    latitude=47.15,
                    longitude=126.72,
                    account_type='phone',
                    application_platform='ios',
                    connection_type='CONN_CELL',
                    event_name='order_received',
                    event_id='102'
                ),
                event(
                    utc_event_dttm='2019-08-01 10:02:00',
                    os_version=None,
                    battery_level=85,
                    active_order_cnt=2,
                    scenario='scenarion_1',
                    account_type='social',
                    application_platform='ios',
                    connection_type='CONN_WIFI',
                    event_name='order_received',
                    event_id='103'
                ),
                event(
                    utc_event_dttm='2019-08-01 12:00:00',
                    os_version=None,
                    scenario='scenarion_1',
                    tariff='uberx',
                    latitude=47.16,
                    longitude=126.73,
                    connection_type='CONN_WIFI',
                    application_platform='ios',
                    event_id='104'
                )
            ],
            [
                application(
                    appsession_id='349a749674d0c5d87ce88076a4c27531',
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    utc_session_end_dttm='2019-08-01 10:02:00',
                    last_os_version='451',
                    first_battery_level=88,
                    last_battery_level=85,
                    lower_power_mode_flg=True,
                    last_active_order_cnt=2,
                    first_tariff='econom',
                    last_tariff='econom',
                    first_lat=47.15,
                    first_lon=126.72,
                    account_type_list=['phone', 'social', 'yandex'],
                    api_key='3',
                    application_platform='ios',
                    first_connection_type='CONN_CELL',
                    last_connection_type='CONN_WIFI',
                    order_connection_type_list=['CONN_CELL', 'CONN_WIFI'],
                    event_list=['101', '102', '103']
                ),
                application(
                    appsession_id='7992aab5ef9cb64f9738725ee74d9010',
                    utc_session_start_dttm='2019-08-01 12:00:00',
                    utc_session_end_dttm='2019-08-01 12:00:00',
                    last_os_version=None,
                    first_battery_level=None,
                    last_battery_level=None,
                    lower_power_mode_flg=False,
                    last_active_order_cnt=0,
                    first_tariff='uberx',
                    last_tariff='uberx',
                    first_lat=47.16,
                    first_lon=126.73,
                    account_type_list=[],
                    api_key=None,
                    application_platform='ios',
                    first_connection_type='CONN_WIFI',
                    last_connection_type='CONN_WIFI',
                    order_connection_type_list=[],
                    event_list=['104']
                )
            ],
            [
                scenario(
                    session_id='eca7918e742404219680c1851c077460',
                    appsession_id='349a749674d0c5d87ce88076a4c27531',
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    utc_session_end_dttm='2019-08-01 10:00:59',
                    first_battery_level=88,
                    last_battery_level=88,
                    last_active_order_cnt=0
                ),
                scenario(
                    session_id='f786906dc8f1bd85c3e71b5568b8bccc',
                    appsession_id='349a749674d0c5d87ce88076a4c27531',
                    utc_session_start_dttm='2019-08-01 10:01:00',
                    utc_session_end_dttm='2019-08-01 10:02:00',
                    first_battery_level=80,
                    last_battery_level=85,
                    last_active_order_cnt=2
                ),
                scenario(
                    session_id='26783bc8760286e4d2f42f2406722ca8',
                    appsession_id='7992aab5ef9cb64f9738725ee74d9010',
                    utc_session_start_dttm='2019-08-01 12:00:00',
                    utc_session_end_dttm='2019-08-01 12:00:00',
                    first_battery_level=None,
                    last_battery_level=None,
                    last_active_order_cnt=0
                )
            ],
            None,
            None,
            id='Aggregator attribute test'
        ),
pytest.param(
            [
                event(
                    utc_event_dttm='2019-08-01 10:00:00',
                    yandex_uid=None,
                    event_id='101'
                ),
                event(
                    utc_event_dttm='2019-08-01 10:01:00',
                    yandex_uid='foo',
                    event_id='102'
                ),
                event(
                    utc_event_dttm='2019-08-01 12:00:00',
                    account_type='foo',
                    event_id='103'
                ),
                event(
                    utc_event_dttm='2019-08-01 12:01:00',
                    account_type='bar',
                    event_id='104'
                ),
                event(
                    utc_event_dttm='2019-08-01 14:00:00',
                    account_type='foo',
                    event_id='105'
                ),
                event(
                    utc_event_dttm='2019-08-01 14:01:00',
                    account_type=None,
                    event_id='106'
                ),
                event(
                    utc_event_dttm='2019-08-01 16:00:00',
                    account_type=None,
                    event_id='107'
                ),
                event(
                    utc_event_dttm='2019-08-01 16:01:00',
                    account_type=None,
                    event_id='108'
                ),
            ],
            [
                application(
                    appsession_id='349a749674d0c5d87ce88076a4c27531',
                    event_list=['101', '102'],
                    fact_authorization_flg=True
                ),
                application(
                    appsession_id='7992aab5ef9cb64f9738725ee74d9010',
                    event_list=['103', '104'],
                    fact_authorization_flg=False
                ),
                application(
                    appsession_id='78c2bc10f38c1214938904a87102c997',
                    event_list=['105', '106'],
                    fact_authorization_flg=False
                ),
                application(
                    appsession_id='3dab79fc377904c7223e308aaa756acf',
                    event_list=['107', '108'],
                    fact_authorization_flg=False
                ),
            ],
            None,
            None,
            None,
            id='Authorization test'
        ),
        pytest.param(
            [
                event(
                    utc_event_dttm='2019-08-01 10:00:00',
                    account_type='social',
                    event_id='101'
                ),
                event(
                    utc_event_dttm='2019-08-01 10:01:00',
                    account_type='yandex',
                    event_id='102'
                ),
                event(
                    utc_event_dttm='2019-08-01 10:02:00',
                    account_type='social',
                    event_id='103'
                ),
                event(
                    utc_event_dttm='2019-08-01 12:00:00',
                    account_type='social',
                    event_id='104'
                ),
                event(
                    utc_event_dttm='2019-08-01 12:01:00',
                    account_type='phone',
                    event_id='105'
                ),
                event(
                    utc_event_dttm='2019-08-01 12:02:00',
                    account_type='social',
                    event_id='106'
                ),
                event(
                    utc_event_dttm='2019-08-01 14:00:00',
                    account_type='yandex',
                    event_id='107'
                ),
                event(
                    utc_event_dttm='2019-08-01 14:01:00',
                    account_type='yandex',
                    event_id='108'
                )
            ],
            [
                application(
                    appsession_id='349a749674d0c5d87ce88076a4c27531',
                    event_list=['101', '102', '103'],
                    fact_yandex_authorization_flg=True
                ),
                application(
                    appsession_id='7992aab5ef9cb64f9738725ee74d9010',
                    event_list=['104', '105', '106'],
                    fact_yandex_authorization_flg=False
                ),
                application(
                    appsession_id='78c2bc10f38c1214938904a87102c997',
                    event_list=['107', '108'],
                    fact_yandex_authorization_flg=False
                ),
            ],
            None,
            None,
            None,
            id='Yandex authorization test'
        ),
        pytest.param(
            [
                event(
                    utc_event_dttm='2019-08-01 10:00:00',
                    background_flg=True,
                    event_id='101'
                ),
                event(
                    utc_event_dttm='2019-08-01 10:01:00',
                    background_flg=True,
                    event_id='102'
                ),
                event(
                    utc_event_dttm='2019-08-02 10:00:00',
                    background_flg=True,
                    event_id='201'
                ),
                event(
                    utc_event_dttm='2019-08-02 10:01:00',
                    background_flg=False,
                    event_id='202'
                ),
                event(
                    utc_event_dttm='2019-08-03 10:00:00',
                    background_flg=False,
                    event_id='301'
                ),
                event(
                    utc_event_dttm='2019-08-03 10:01:00',
                    background_flg=True,
                    event_id='302'
                ),
                event(
                    utc_event_dttm='2019-08-04 10:00:00',
                    background_flg=False,
                    event_id='401'
                ),
                event(
                    utc_event_dttm='2019-08-04 10:01:00',
                    background_flg=False,
                    event_id='402'
                )
            ],
            [
                application(
                    appsession_id='349a749674d0c5d87ce88076a4c27531',
                    event_list=['101', '102'],
                    background_flg=True
                ),
                application(
                    appsession_id='53c2aa65a4373c0247d79778f100bedd',
                    event_list=['201', '202'],
                    background_flg=False
                ),
                application(
                    appsession_id='294ff83c37cf4f27c0914935493e0678',
                    event_list=['301', '302'],
                    background_flg=False
                ),
                application(
                    appsession_id='67586d88f2f5fd2ee54fbc7d7b8cd0dc',
                    event_list=['401', '402'],
                    background_flg=False
                ),
            ],
            None,
            None,
            None,
            id='Background session test'
        ),
    ]
)
def test_session_build(events, expected_application, expected_scenario, expected_subscenario, expected_screen):
    session_builder = ApplicationSessionBuilder(
        ApplicationSession, ScenarioSession, SubscenarioSession, ScreenSession,
        '2019-08-29 23:59:59'
    )

    cluster = MockCluster()
    job = cluster.job('test_session_build')

    actual_application = []
    actual_scenario = []
    actual_subscenario = []
    actual_screen = []

    application_stream, scenario_stream, subscenario_stream, screen_stream = job.table('stub') \
        .label('events') \
        .groupby('appmetrica_device_id', 'appmetrica_uuid') \
        .sort('utc_event_dttm', 'event_id') \
        .reduce(session_builder)

    application_stream.label('actual_application')
    scenario_stream.label('actual_scenario')
    subscenario_stream.label('actual_subscenario')
    screen_stream.label('actual_screen')

    job.local_run(
        sources={'events': StreamSource(events)},
        sinks={
            'actual_application': ListSink(actual_application),
            'actual_scenario': ListSink(actual_scenario),
            'actual_subscenario': ListSink(actual_subscenario),
            'actual_screen': ListSink(actual_screen)
        }
    )
    for actual_session_list, expected_session_list, session_name in zip(
        (actual_application, actual_scenario, actual_subscenario, actual_screen),
        (expected_application, expected_scenario, expected_subscenario, expected_screen),
        ('application', 'scenario', 'subscenario', 'screen')
    ):
        if expected_session_list is None:
            continue
        actual_session_list = sorted(
            [
                rec.to_dict()
                for rec in actual_session_list
            ],
            key=lambda rec: (
                rec.get('appmetrica_device_id'),
                rec.get('appmetrica_uuid'),
                rec.get('utc_session_start_dttm')
            )
        )
        assert len(expected_session_list) == len(actual_session_list), \
                'Expected {} sessions have different length from actual:\nexpected\n{},\nactual\n{}' \
                    .format(session_name, pformat(expected_session_list), pformat(actual_session_list))
        for i, (expected_session, actual_session) in enumerate(zip(expected_session_list, actual_session_list)):
            for key in expected_session:
                assert expected_session.get(key) == actual_session.get(key), \
                'Expected {} sessions have different {} from actual in {}th session:\nexpected\n{},\nactual\n{}' \
                    .format(session_name, key, i, pformat(expected_session_list), pformat(actual_session_list))
