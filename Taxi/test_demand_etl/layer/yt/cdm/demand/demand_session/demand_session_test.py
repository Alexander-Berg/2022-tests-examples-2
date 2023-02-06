import pytest
from pprint import pformat

from nile.api.v1 import MockCluster
from nile.api.v1.local import StreamSource, ListSink

from demand_etl.layer.yt.cdm.demand.demand_session.impl import DemandSession, DemandSessionBuilder

from .impl import pin_record, offer_record, order_record, session_record


@pytest.mark.parametrize(
    'events, expected_session_list',
    [
        pytest.param(
            [
                pin_record(
                    event_id='100',
                    utc_event_dttm='2019-08-01 10:00:00',
                    tariff_zone='asdfgh',
                ),
                pin_record(
                    event_id='101',
                    utc_event_dttm='2019-08-01 10:00:01',
                    source_lat=39.3441,
                    source_lon=72.8781,
                    surge_value=1.2,
                    estimated_waiting_sec=90.,
                    tariff_zone=None,
                ),
                offer_record(
                    event_id='102',
                    utc_event_dttm='2019-08-01 10:00:02',
                ),
                order_record(
                    event_id='103',
                    utc_event_dttm='2019-08-01 10:00:03',
                    order_application_platform='android',
                    user_id='goo',
                ),
                order_record(
                    event_id='104',
                    utc_event_dttm='2019-08-01 10:00:04',
                    order_application_platform='iphone',
                    success_order_flg=True,
                    source_lat=39.3440,
                    source_lon=72.8780,
                )
            ],
            [
                session_record(
                    app_platform_list=['android', 'iphone'],
                    break_reason='success_order',
                    last_app_platform='iphone',
                    duration_h=0.0011111111111111111,
                    first_success_order_app_platform='iphone',
                    last_event_lat=39.3440,
                    last_event_lon=72.8780,
                    last_tariff_zone='asdfgh',
                    offer_cnt=1,
                    offer_list=['102'],
                    order_list=['103', '104'],
                    pin_cnt=2,
                    pin_list=['100', '101'],
                    session_id='8447bb8ba0faa42a286310fbd8b98f4b',
                    success_order_cnt=1,
                    user_id_list=['foo', 'goo'],
                    utc_session_end_dttm='2019-08-01 10:00:04',
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    last_surge_value=1.2,
                    last_waiting_time_sec=90.,
                    pin_w_wait_time_cnt=2,
                )
            ],
            id='Multiapp session'
        ),
        pytest.param(
            [
                offer_record(
                    event_id='100',
                    utc_event_dttm='2019-08-01 10:00:00',
                    source_lat=None,
                    source_lon=None
                ),
                order_record(
                    event_id='101',
                    utc_event_dttm='2019-08-01 10:00:01',
                    success_order_flg=True,
                    source_lat=39.3440,
                    source_lon=72.8780,
                    user_application_platform='iphone'
                ),
                pin_record(
                    event_id='102',
                    utc_event_dttm='2019-08-01 10:00:59',
                    surge_value=None
                )
            ],
            [
                session_record(
                    app_platform_list=['android', 'iphone'],
                    last_app_platform='android',
                    break_reason='success_order',
                    duration_h=0.0002777777777777778,
                    first_event_lat=39.3440,
                    first_event_lon=72.8780,
                    first_success_order_app_platform='android',
                    last_event_lat=39.3440,
                    last_event_lon=72.8780,
                    last_tariff_zone=None,
                    pin_cnt=0,
                    offer_cnt=1,
                    offer_list=['100'],
                    order_list=['101'],
                    session_id='113e3062ab018c18b797e9d3b3819a3e',
                    success_order_cnt=1,
                    utc_session_end_dttm='2019-08-01 10:00:01',
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    first_surge_value=None,
                    last_surge_value=None,
                    first_waiting_time_sec=None,
                    last_waiting_time_sec=None,
                    pin_w_wait_time_cnt=0,
                ),
                session_record(
                    duration_h=0.0,
                    pin_cnt=1,
                    offer_cnt=0,
                    success_order_cnt=0,
                    pin_list=['102'],
                    session_id='2e6bbd5edaed6cd4a630511de5141898',
                    utc_session_end_dttm='2019-08-01 10:00:59',
                    utc_session_start_dttm='2019-08-01 10:00:59',
                    first_surge_value=None,
                    last_surge_value=None,
                    pin_w_wait_time_cnt=1
                )
            ],
            id='Success order break'
        ),
pytest.param(
            [
                offer_record(
                    event_id='100',
                    utc_event_dttm='2019-08-01 10:00:00',
                    source_lat=None,
                    source_lon=None
                ),
                order_record(
                    event_id='101',
                    utc_event_dttm='2019-08-01 10:00:01',
                    success_order_flg=True,
                    source_lat=39.3440,
                    source_lon=72.8780,
                    user_application_platform='iphone'
                ),
                pin_record(
                    event_id='102',
                    order_id='101',
                    utc_event_dttm='2019-08-01 10:00:59',
                    surge_value=None
                ),
                pin_record(
                    event_id='103',
                    utc_event_dttm='2019-08-01 10:10:59',
                    surge_value=None
                ),
            ],
            [
                session_record(
                    app_platform_list=['android', 'iphone'],
                    last_app_platform='android',
                    break_reason='success_order',
                    duration_h=0.01638888888888889,
                    first_event_lat=39.3440,
                    first_event_lon=72.8780,
                    first_success_order_app_platform='android',
                    last_event_lat=39.3436,
                    last_event_lon=72.8776,
                    last_tariff_zone='qwerty',
                    pin_cnt=1,
                    offer_cnt=1,
                    pin_list=['102'],
                    offer_list=['100'],
                    order_list=['101'],
                    session_id='e389457f9e968f4ce5c5d6bd254057f0',
                    success_order_cnt=1,
                    utc_session_end_dttm='2019-08-01 10:00:59',
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    first_surge_value=None,
                    last_surge_value=None,
                    first_waiting_time_sec=60.0,
                    last_waiting_time_sec=60.0,
                    pin_w_wait_time_cnt=1,
                ),
                session_record(
                    duration_h=0.0,
                    pin_cnt=1,
                    offer_cnt=0,
                    success_order_cnt=0,
                    pin_list=['103'],
                    session_id='94c1efc04737ebbafc7aa063cb59c25a',
                    utc_session_end_dttm='2019-08-01 10:10:59',
                    utc_session_start_dttm='2019-08-01 10:10:59',
                    first_surge_value=None,
                    last_surge_value=None,
                    pin_w_wait_time_cnt=1
                )
            ],
            id='Success order with driver pin'
        ),
        pytest.param(
            [
                pin_record(
                    event_id='100',
                    utc_event_dttm='2019-08-01 10:00:00'
                ),
                pin_record(
                    event_id='101',
                    utc_event_dttm='2019-08-01 10:00:01'
                ),
                pin_record(
                    event_id='102',
                    utc_event_dttm='2019-08-01 10:00:02',
                    source_lat=66.7189,
                    source_lon=64.3955,
                    tariff_zone='asdfgh',
                    estimated_waiting_sec=None
                )
            ],
            [
                session_record(
                    break_reason='distance',
                    duration_h=0.0002777777777777778,
                    pin_cnt=2,
                    pin_list=['100', '101'],
                    session_id='113e3062ab018c18b797e9d3b3819a3e',
                    utc_session_end_dttm='2019-08-01 10:00:01',
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    pin_w_wait_time_cnt=2,
                ),
                session_record(
                    duration_h=0.0,
                    first_event_lat=66.7189,
                    first_event_lon=64.3955,
                    last_event_lat=66.7189,
                    last_event_lon=64.3955,
                    last_tariff_zone='asdfgh',
                    pin_cnt=1,
                    pin_list=['102'],
                    session_id='7c1b0965e4d788f7c594330987ed2174',
                    utc_session_end_dttm='2019-08-01 10:00:02',
                    utc_session_start_dttm='2019-08-01 10:00:02',
                    first_waiting_time_sec=None,
                    last_waiting_time_sec=None,
                    pin_w_wait_time_cnt=0,
                )
            ],
            id='Distance break'
        ),
        pytest.param(
            [
                pin_record(
                    event_id='100',
                    utc_event_dttm='2019-08-01 10:00:00'
                ),
                pin_record(
                    event_id='101',
                    utc_event_dttm='2019-08-01 10:00:01'
                ),
                pin_record(
                    event_id='102',
                    utc_event_dttm='2019-08-01 23:59:59'
                )
            ],
            [
                session_record(
                    duration_h=0.0002777777777777778,
                    pin_cnt=2,
                    pin_list=['100', '101'],
                    session_id='113e3062ab018c18b797e9d3b3819a3e',
                    utc_session_end_dttm='2019-08-01 10:00:01',
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    pin_w_wait_time_cnt=2
                ),
                session_record(
                    duration_h=0.0,
                    pin_cnt=1,
                    pin_list=['102'],
                    session_id='f8894c1816dc3eaf89465a66953608c3',
                    utc_session_end_dttm='2019-08-01 23:59:59',
                    utc_session_start_dttm='2019-08-01 23:59:59',
                    pin_w_wait_time_cnt=1
                )
            ],
            id='Timeout break'
        ),
        pytest.param(
            [
                pin_record(
                    event_id='100',
                    utc_event_dttm='2019-08-01 10:00:00'
                ),
                pin_record(
                    event_id='101',
                    utc_event_dttm='2019-08-01 10:30:00'
                ),
                pin_record(
                    event_id='102',
                    utc_event_dttm='2019-08-01 11:00:00'
                ),
                pin_record(
                    event_id='103',
                    utc_event_dttm='2019-08-01 11:30:00'
                ),
                pin_record(
                    event_id='104',
                    utc_event_dttm='2019-08-01 12:00:00'
                ),
                pin_record(
                    event_id='105',
                    utc_event_dttm='2019-08-01 12:30:00'
                )
            ],
            [
                session_record(
                    break_reason='session_duration',
                    duration_h=2.0,
                    pin_cnt=5,
                    pin_list=['100', '101', '102', '103', '104'],
                    session_id='8447bb8ba0faa42a286310fbd8b98f4b',
                    utc_session_end_dttm='2019-08-01 12:00:00',
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    pin_w_wait_time_cnt=5,
                ),
                session_record(
                    duration_h=0.0,
                    pin_cnt=1,
                    pin_list=['105'],
                    session_id='c21565c40a607f862425fa37032de66f',
                    utc_session_end_dttm='2019-08-01 12:30:00',
                    utc_session_start_dttm='2019-08-01 12:30:00',
                    pin_w_wait_time_cnt=1
                )
            ],
            id='Session duration break'
        ),
        pytest.param(
            [
                pin_record(
                    event_id='100',
                    utc_event_dttm='2019-08-01 10:00:00'
                ),
                order_record(
                    event_id='101',
                    utc_event_dttm='2019-08-01 10:00:01',
                    success_order_flg=True
                ),
                pin_record(
                    event_id='102',
                    utc_event_dttm='2019-08-01 10:00:02'
                ),
                pin_record(
                    event_id='103',
                    utc_event_dttm='2019-08-01 10:00:02'
                ),
                offer_record(
                    event_id='104',
                    utc_event_dttm='2019-08-01 10:00:02'
                ),
                pin_record(
                    event_id='105',
                    utc_event_dttm='2019-08-01 10:00:03'
                )
            ],
            [
                session_record(
                    app_platform_list=['android'],
                    last_app_platform='android',
                    break_reason='success_order',
                    duration_h=0.0005555555555555556,
                    first_success_order_app_platform='android',
                    offer_cnt=1,
                    offer_list=['104'],
                    order_list=['101'],
                    pin_cnt=3,
                    pin_list=['100', '102', '103'],
                    session_id='cefc1e535424780e0cac56407abf157f',
                    success_order_cnt=1,
                    utc_session_end_dttm='2019-08-01 10:00:02',
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    pin_w_wait_time_cnt=3
                ),
                session_record(
                    duration_h=0.0,
                    pin_cnt=1,
                    pin_list=['105'],
                    success_order_cnt=0,
                    session_id='9a2bc291df717d334465ba15e5162253',
                    utc_session_end_dttm='2019-08-01 10:00:03',
                    utc_session_start_dttm='2019-08-01 10:00:03',
                    pin_w_wait_time_cnt=1
                )
            ],
            id='Last pin append'
        ),
        pytest.param(
            [
                pin_record(
                    event_id='100',
                    utc_event_dttm='2019-08-01 10:00:00'
                ),
                order_record(
                    event_id='101',
                    utc_event_dttm='2019-08-01 10:00:01',
                    success_order_flg=True,
                    multiorder_flg=True

                ),
                order_record(
                    event_id='102',
                    utc_event_dttm='2019-08-01 10:00:02',
                    success_order_flg=True,
                    multiorder_flg=True
                ),
                order_record(
                    event_id='103',
                    utc_event_dttm='2019-08-01 10:00:03',
                    multiorder_flg=True
                ),
                pin_record(
                    event_id='104',
                    utc_event_dttm='2019-08-01 10:00:04'
                ),
                pin_record(
                    event_id='105',
                    utc_event_dttm='2019-08-01 23:59:59'
                )
            ],
            [
                session_record(
                    app_platform_list=['android'],
                    last_app_platform='android',
                    break_reason='success_order',
                    duration_h=0.0011111111111111111,
                    first_success_order_app_platform='android',
                    multiorder_flg=True,
                    order_list=['101', '102', '103'],
                    pin_cnt=2,
                    pin_list=['100', '104'],
                    session_id='3095808c06a17b26a17cc1c55d22ea6d',
                    success_order_cnt=2,
                    utc_session_end_dttm='2019-08-01 10:00:04',
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    pin_w_wait_time_cnt=2
                ),
                session_record(
                    duration_h=0.0,
                    pin_cnt=1,
                    pin_list=['105'],
                    success_order_cnt=0,
                    session_id='6866bc92d149a6df9052e7cb7ba42bd3',
                    utc_session_end_dttm='2019-08-01 23:59:59',
                    utc_session_start_dttm='2019-08-01 23:59:59',
                    pin_w_wait_time_cnt=1
                )
            ],
            id='Multiorder'
        ),
        pytest.param(
            [
                pin_record(
                    event_id='100',
                    utc_event_dttm='2019-08-01 10:00:00'
                ),
                pin_record(
                    event_id='101',
                    utc_event_dttm='2019-08-04 10:00:00'
                )
            ],
            [
                session_record(
                    pin_cnt=1,
                    pin_list=['100'],
                    session_id='058768f721e3f01e8825ee0109a14cd2',
                    utc_session_end_dttm='2019-08-01 10:00:00',
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    pin_w_wait_time_cnt=1
                )
            ],
            id='Period filter'
        ),
        pytest.param(
            [
                pin_record(
                    event_id='100',
                    utc_event_dttm='2019-08-01 10:00:00'
                ),
                pin_record(
                    event_id='101',
                    utc_event_dttm='2019-08-01 10:00:01'
                ),
                pin_record(
                    event_id='102',
                    utc_event_dttm='2019-08-01 10:00:01',
                    source_lat=66.7189,
                    source_lon=64.3955
                ),
                pin_record(
                    event_id='103',
                    utc_event_dttm='2019-08-01 10:00:02',
                    source_lat=66.7189,
                    source_lon=64.3955,
                ),
                pin_record(
                    event_id='104',
                    utc_event_dttm='2019-08-01 10:00:02'
                )
            ],
            [
                session_record(
                    break_reason='distance',
                    duration_h=0.0002777777777777778,
                    last_event_lat=66.7189,
                    last_event_lon=64.3955,
                    pin_cnt=3,
                    pin_list=['100', '101', '102'],
                    session_id='400d9cb894f10b11d16b0fed6f44f06b',
                    utc_session_end_dttm='2019-08-01 10:00:01',
                    utc_session_start_dttm='2019-08-01 10:00:00',
                    pin_w_wait_time_cnt=3
                ),
                session_record(
                    duration_h=0.0,
                    first_event_lat=66.7189,
                    first_event_lon=64.3955,
                    pin_cnt=2,
                    pin_list=['103', '104'],
                    session_id='eaeca66ab082b79de52a796fa193f80f',
                    utc_session_end_dttm='2019-08-01 10:00:02',
                    utc_session_start_dttm='2019-08-01 10:00:02',
                    pin_w_wait_time_cnt=2
                )
            ],
            id='Simultaneous distant events'
        ),
        pytest.param(
            [
                pin_record(
                    event_id='100',
                    utc_event_dttm='2019-08-01 05:00:00',
                    pin_w_altpin_offer_id='101',
                ),
                offer_record(
                    event_id='101',
                    utc_event_dttm='2019-08-01 05:00:01',
                ),
                offer_record(
                    event_id='102',
                    utc_event_dttm='2019-08-01 05:00:02',
                ),
                order_record(
                    event_id='103',
                    utc_event_dttm='2019-08-01 05:00:03',
                    order_offer_id='101',
                ),

                pin_record(
                    event_id='110',
                    utc_event_dttm='2019-08-01 10:00:00',
                    pin_w_altpin_offer_id='114',
                ),
                offer_record(
                    event_id='111',
                    utc_event_dttm='2019-08-01 10:00:01',
                ),
                order_record(
                    event_id='112',
                    utc_event_dttm='2019-08-01 10:00:02',
                    order_offer_id='113',
                ),

                pin_record(
                    event_id='120',
                    utc_event_dttm='2019-08-01 15:00:00',
                    pin_w_altpin_offer_id='122',
                ),
                order_record(
                    event_id='121',
                    utc_event_dttm='2019-08-01 15:00:01',
                    order_offer_id='122',
                ),

                pin_record(
                    event_id='130',
                    utc_event_dttm='2019-08-01 20:00:00',
                    pin_w_altpin_offer_id='133',
                ),
                pin_record(
                    event_id='131',
                    utc_event_dttm='2019-08-01 20:00:01',
                    pin_w_altpin_offer_id='150',
                ),
                offer_record(
                    event_id='132',
                    utc_event_dttm='2019-08-01 20:00:02',
                ),
                offer_record(
                    event_id='133',
                    utc_event_dttm='2019-08-01 20:00:03',
                ),
                offer_record(
                    event_id='134',
                    utc_event_dttm='2019-08-01 20:00:04',
                ),
                order_record(
                    event_id='135',
                    utc_event_dttm='2019-08-01 20:00:05',
                    order_offer_id='133',
                ),
                order_record(
                    event_id='136',
                    utc_event_dttm='2019-08-01 20:00:06',
                    order_offer_id='150',
                ),
                order_record(
                    event_id='137',
                    utc_event_dttm='2019-08-01 20:00:07',
                    order_offer_id='150',
                ),
            ],
            [
                session_record(
                    pin_list=['100'],
                    offer_list=['101', '102'],
                    order_list=['103'],
                    shown_altoffer_list=['101'],
                    used_altoffer_list=['101'],
                    session_id='3aadf051791483173998805dd1c2e9c7',
                ),
                session_record(
                    pin_list=['110'],
                    offer_list=['111'],
                    order_list=['112'],
                    shown_altoffer_list=[],
                    used_altoffer_list=[],
                    session_id='2b7e73db8cb2ea371f439d841447fbd6',
                ),
                session_record(
                    pin_list=['120'],
                    offer_list=[],
                    order_list=['121'],
                    shown_altoffer_list=[],
                    used_altoffer_list=['122'],
                    session_id='1be07c1f08db6250074ed9ab6745900f',
                ),
                session_record(
                    pin_list=['130', '131'],
                    offer_list=['132', '133', '134'],
                    order_list=['135', '136', '137'],
                    shown_altoffer_list=['133'],
                    used_altoffer_list=['133', '150'],
                    session_id='fb69d6cce30bd61c275c4b6b5d4a1db8',
                )
            ],
            id='Altoffers'
        )
    ]
)
def test_session_build(events, expected_session_list):
    session_builder = DemandSessionBuilder(DemandSession, '2019-08-03 23:59:59')

    cluster = MockCluster()
    job = cluster.job('test_session_build')
    actual_session_list = []
    job.table('stub') \
        .label('events') \
        .groupby('phone_pd_id') \
        .sort('utc_event_dttm', 'sort_order', 'event_id') \
        .reduce(session_builder) \
        .label('actual_session_list')
    job.local_run(
        sources={'events': StreamSource(events)},
        sinks={'actual_session_list': ListSink(actual_session_list)}
    )

    actual_session_list = sorted(actual_session_list, key=lambda rec: (rec.get('phone_pd_id'), rec.get('utc_session_start_dttm')))

    assert len(expected_session_list) == len(actual_session_list), \
        'Expected sessions have different length from actual:\nexpected\n{},\nactual\n{}' \
            .format(pformat(expected_session_list), pformat(actual_session_list))
    for i, (expected_session, actual_session) in enumerate(zip(expected_session_list, actual_session_list)):
        for key in expected_session.to_dict():
            assert expected_session.get(key) == actual_session.get(key), \
                'Expected sessions have different {} from actual in {}th session:\nexpected\n{},\nactual\n{}' \
                    .format(key, i, pformat(expected_session), pformat(actual_session))
