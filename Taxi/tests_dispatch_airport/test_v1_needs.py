import copy
import datetime

import pytest
import pytz

from tests_dispatch_airport import common
import tests_dispatch_airport.utils as utils

_DISPATCH_AIRPORT_ZONES = {
    'ekb': {
        'use_queue': False,
        'enabled': True,
        'main_area': 'ekb_airport',
        'notification_area': 'ekb_airport_notification',
        'update_interval_sec': 1,
        'waiting_area': 'ekb_airport_waiting',
        'tariff_home_zone': 'ekb_home_zone',
        'old_mode_enabled': True,
        'airport_title_key': 'ekb_airport_key',
        'whitelist_classes': {
            # demand from ml, nearest mins config
            'econom': {'reposition_enabled': True, 'nearest_mins': 30},
            # ignore business
            'comfortplus': {
                'reposition_enabled': False,  # ignore comfortplus
                'nearest_mins': 60,
            },
            # demand from config, nearest mins from config
            'business2': {'reposition_enabled': True, 'nearest_mins': 90},
        },
    },
    'svo': {
        'use_queue': False,
        'enabled': True,
        'main_area': 'svo_airport',
        'notification_area': 'svo_airport_notification',
        'update_interval_sec': 1,
        'waiting_area': 'svo_airport_waiting',
        'tariff_home_zone': 'svo_home_zone',
        'old_mode_enabled': True,
        'airport_title_key': 'svo_airport_key',
        'whitelist_classes': {
            # demand from ml, nearest mins from config
            'econom': {'reposition_enabled': True, 'nearest_mins': 60},
            # demand from config, nearest mins from config
            'comfortplus': {'reposition_enabled': True, 'nearest_mins': 60},
            # demand from ml, nearest mins from config
            'vip': {'reposition_enabled': True, 'nearest_mins': 100},
        },
    },
}

URL = '/info/needs/v1'
HEADERS = common.DEFAULT_DISPATCH_AIRPORT_HEADER


@pytest.fixture(name='umlass_mock')
def _umlass_mock(mockserver, load_json):
    @mockserver.json_handler('/umlaas/airport_queue_size/v1')
    def _umlaas(request):
        tariff = request.query['tariff']
        airport = request.query['airport']
        assert airport in ('ekb_airport', 'ekb_airport2', 'svo_airport')
        assert tariff in (
            'econom',
            'business',
            'business2',
            'comfortplus',
            'vip',
        )

        if airport == 'ekb_airport':
            estimated_times_json = load_json('airport_queue_predictions.json')
            estimated_times_airport = estimated_times_json.get(airport, {})
            estimated_times_tariff = estimated_times_airport.get(tariff, {})
            estimated_times = estimated_times_tariff.get('predicted', [])
            response = {'estimated_times': estimated_times}
            if tariff != 'econom':
                response['queue_size'] = 5
            return response

        if airport == 'ekb_airport2':
            estimated_times = []
            if tariff == 'comfortplus':
                estimated_times = [9, 30, 33, 35, 43, 53, 63, 73]
            response = {'estimated_times': estimated_times, 'queue_size': 20}
            return response

        # check fallback for svo
        return mockserver.make_response('fail', status=500)


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.config(
    DISPATCH_AIRPORT_ZONES=_DISPATCH_AIRPORT_ZONES,
    DISPATCH_AIRPORT_RELOCATION_REPOSITION_SETTINGS={
        'by_point': {
            '__default__': {
                'accept_timeout_sec': 90,
                'auto_accept': False,
                'drive_timeout_sec': 1800,
                'image_id': 'plane',
                'mode': 'Sintegro',
            },
        },
    },
)
@pytest.mark.experiments3(
    filename='experiments3_umlaas_queue_predictions.json',
)
@pytest.mark.parametrize('is_holiday', [False, True])
async def test_v1_needs(
        taxi_dispatch_airport, is_holiday, mocked_time, umlass_mock, testpoint,
):
    @testpoint('queued_free_driver')
    def queued_free(data):
        return data

    @testpoint('expected_to_be_queued_on_action_driver')
    def expected_to_be_queued_on_action(data):
        return data

    @testpoint('expected_to_be_queued_on_reposition_driver')
    def expected_to_be_queued_on_repo(data):
        return data

    if not is_holiday:
        # Friday
        date = datetime.datetime(2020, 5, 22, 23, 59, 59)
    else:
        # Saturday
        date = datetime.datetime(2020, 5, 23, 00, 00, 00)

    await taxi_dispatch_airport.invalidate_caches()
    timezone = pytz.timezone('Europe/Moscow')
    mocked_time.set(timezone.localize(date))

    response = await taxi_dispatch_airport.get(
        URL, headers=HEADERS, params={'zone': 'unknown'},
    )
    assert response.status_code == 404

    response = await taxi_dispatch_airport.get(
        URL, headers=HEADERS, params={'zone': 'ekb_airport'},
    )
    resp_json = response.json()
    ekb_etalon = {
        'ekb': {
            'zone': 'ekb_airport_waiting',
            'airport': 'ekb_airport_key',
            'class_demand': {
                'business2': {'count': 20, 'expected_wait_time': 5400},
            },
        },
    }
    assert resp_json == ekb_etalon

    # if we use weights = predict
    # comfortplus: queued_free: 1.5(dbid_uuid5*0.5 + dbid_uuid6),
    # expected_to_be_queued: 0.5(dbid_uuid12*0.5)
    # all 2
    # vip: queued_free: 2.5(dbid_uuid5*0.5+dbid_uuid9+dbid_uuid10),
    # expected_to_be_queued: 1.5(dbid_uuid11+dbid_uuid12*0.5)
    # all 4

    comfortplus_available_drivers = 2
    vip_available_drivers = 4

    all_etalon = {
        'svo': {
            'zone': 'svo_airport_waiting',
            'airport': 'svo_airport_key',
            'class_demand': {
                'vip': {
                    'count': 20 - vip_available_drivers,
                    'expected_wait_time': 6000,
                },
                'comfortplus': {
                    'count': 20 - comfortplus_available_drivers,
                    'expected_wait_time': 3600,
                },
            },
        },
        **ekb_etalon,
    }
    response = await taxi_dispatch_airport.get(URL, headers=HEADERS)
    resp_json = response.json()
    assert resp_json == all_etalon

    assert (
        utils.get_calls_sorted_two_keys(
            queued_free, 5, 'data', 'driver_id', 'tariff',
        )
        == [
            {
                'driver_id': 'dbid_uuid10',
                'tariff': 'vip',
                'tariff_predict': 20,
                'total_predict': 20,
            },
            {
                'driver_id': 'dbid_uuid5',
                'tariff': 'comfortplus',
                'tariff_predict': 20,
                'total_predict': 40,
            },
            {
                'driver_id': 'dbid_uuid5',
                'tariff': 'vip',
                'tariff_predict': 20,
                'total_predict': 40,
            },
            {
                'driver_id': 'dbid_uuid6',
                'tariff': 'comfortplus',
                'tariff_predict': 20,
                'total_predict': 20,
            },
            {
                'driver_id': 'dbid_uuid9',
                'tariff': 'vip',
                'tariff_predict': 20,
                'total_predict': 20,
            },
        ]
    )
    assert (
        utils.get_calls_sorted_two_keys(
            expected_to_be_queued_on_action, 1, 'data', 'driver_id', 'tariff',
        )
        == [
            {
                'driver_id': 'dbid_uuid11',
                'tariff': 'vip',
                'tariff_predict': 20,
                'total_predict': 20,
            },
        ]
    )
    assert (
        utils.get_calls_sorted_two_keys(
            expected_to_be_queued_on_repo, 2, 'data', 'driver_id', 'tariff',
        )
        == [
            {
                'driver_id': 'dbid_uuid12',
                'tariff': 'comfortplus',
                'tariff_predict': 20,
                'total_predict': 40,
            },
            {
                'driver_id': 'dbid_uuid12',
                'tariff': 'vip',
                'tariff_predict': 20,
                'total_predict': 40,
            },
        ]
    )


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.experiments3(
    filename='experiments3_umlaas_queue_predictions.json',
)
@pytest.mark.config(
    DISPATCH_AIRPORT_RELOCATION_REPOSITION_SETTINGS={
        'by_point': {
            '__default__': {
                'accept_timeout_sec': 90,
                'auto_accept': False,
                'drive_timeout_sec': 1800,
                'image_id': 'plane',
                'mode': 'Sintegro',
            },
        },
    },
)
async def test_v1_needs_group_check(
        taxi_dispatch_airport, taxi_config, umlass_mock,
):
    zones_copy = copy.deepcopy(_DISPATCH_AIRPORT_ZONES)
    zones_copy['ekb'].update(
        {'group_id': 'test_group', 'distributive_zone_type': 'waiting'},
    )
    zones_copy['svo'].update(
        {'group_id': 'test_group', 'distributive_zone_type': 'distributive'},
    )
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': zones_copy})

    await taxi_dispatch_airport.invalidate_caches()

    # weighted drivers
    # svo values without group: vip = 16, comfortplus: 18
    # in group:
    # vip = 15-0.5 queued (dbid_uuid2) - 0.33 queued (dbid_uuid1) -
    # 0.33 entered with sintegro repo = 14
    # comfortplus = 18-0.33 queued driver (dbid_uuid1) = 18
    etalon = {
        'svo': {
            'zone': 'svo_airport_waiting',
            'airport': 'svo_airport_key',
            'class_demand': {
                'vip': {'count': 14, 'expected_wait_time': 6000},
                'comfortplus': {'count': 18, 'expected_wait_time': 3600},
            },
        },
        'ekb': {
            'zone': 'ekb_airport_waiting',
            'airport': 'ekb_airport_key',
            'class_demand': {
                'business2': {'count': 20, 'expected_wait_time': 5400},
            },
        },
    }
    response = await taxi_dispatch_airport.get(URL, headers=HEADERS)
    resp_json = response.json()
    assert resp_json == etalon


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.config(DISPATCH_AIRPORT_ZONES=_DISPATCH_AIRPORT_ZONES)
@pytest.mark.now('2020-05-01T21:00:00+0000')
@pytest.mark.parametrize('umlaas_data_ttl_reached', [True, False])
@pytest.mark.experiments3(
    filename='experiments3_umlaas_queue_predictions.json',
)
async def test_v1_needs_umlaas_data_ttl(
        taxi_dispatch_airport,
        umlass_mock,
        mocked_time,
        mockserver,
        taxi_config,
        umlaas_data_ttl_reached,
):
    await taxi_dispatch_airport.invalidate_caches()

    @mockserver.json_handler('/umlaas/airport_queue_size/v1')
    def _umlaas(request):
        return mockserver.make_response('fail', status=500)

    taxi_config.set(DISPATCH_AIRPORT_UMLAAS_DATA_TTL=1)
    if umlaas_data_ttl_reached:
        mocked_time.sleep(61)

    await taxi_dispatch_airport.invalidate_caches()

    response = await taxi_dispatch_airport.get(
        URL, headers=HEADERS, params={'zone': 'ekb_airport'},
    )
    resp_json = response.json()

    econom_demand = {}
    if umlaas_data_ttl_reached:
        econom_demand = {'econom': {'count': 19, 'expected_wait_time': 1800}}
    ekb_etalon = {
        'ekb': {
            'zone': 'ekb_airport_waiting',
            'airport': 'ekb_airport_key',
            'class_demand': {
                **econom_demand,
                'business2': {'count': 20, 'expected_wait_time': 5400},
            },
        },
    }
    assert resp_json == ekb_etalon


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.config(DISPATCH_AIRPORT_ZONES=_DISPATCH_AIRPORT_ZONES)
@pytest.mark.experiments3(
    filename='experiments3_umlaas_composite_prediction.json',
)
async def test_composite_ml_predict(
        taxi_dispatch_airport, taxi_config, testpoint, umlass_mock,
):
    @testpoint('airport-queue-predictions-cache-finished')
    def predictions_cache_finished(data):
        return data

    zones_config = taxi_config.get_values()['DISPATCH_AIRPORT_ZONES']
    zones_config['ekb'].update(
        {'ml_predict_based_geoareas': ['ekb_airport2', 'ekb_airport']},
    )
    ml_config = taxi_config.get_values()['DISPATCH_AIRPORT_ML_SETTINGS']
    ml_config['ekb_airport2'] = ml_config['ekb_airport']
    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_ZONES': zones_config,
            'DISPATCH_AIRPORT_ML_SETTINGS': ml_config,
        },
    )
    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    cache_data = (await predictions_cache_finished.wait_call())['data']
    cache_data.sort(key=lambda x: (x['airport_id'], x['tariff']))
    assert cache_data == [
        {
            'airport_id': 'ekb',
            'tariff': 'business2',
            'driver_needs_count': 25,
            'waiting_times': [],
        },
        {
            'airport_id': 'ekb',
            'tariff': 'comfortplus',
            'driver_needs_count': 25,
            'waiting_times': [
                9,
                15,
                25,
                30,
                33,
                35,
                35,
                43,
                45,
                53,
                55,
                63,
                65,
                73,
                75,
            ],
        },
        {
            'airport_id': 'ekb',
            'tariff': 'econom',
            'driver_needs_count': 20,
            'waiting_times': [3, 22, 32, 42, 52, 62, 72],
        },
        {
            'airport_id': 'svo',
            'tariff': 'comfortplus',
            'driver_needs_count': 20,
            'waiting_times': [],
        },
        {
            'airport_id': 'svo',
            'tariff': 'econom',
            'driver_needs_count': 20,
            'waiting_times': [],
        },
        {
            'airport_id': 'svo',
            'tariff': 'vip',
            'driver_needs_count': 20,
            'waiting_times': [],
        },
    ]

    response = await taxi_dispatch_airport.get(
        URL, headers=HEADERS, params={'zone': 'ekb_airport'},
    )
    r_json = response.json()
    assert r_json == {
        'ekb': {
            'zone': 'ekb_airport_waiting',
            'airport': 'ekb_airport_key',
            'class_demand': {
                'business2': {'count': 25, 'expected_wait_time': 5400},
                'econom': {'count': 19, 'expected_wait_time': 1800},
            },
        },
    }


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.config(
    DISPATCH_AIRPORT_ZONES=_DISPATCH_AIRPORT_ZONES,
    DISPATCH_AIRPORT_ML_SETTINGS={},
)
@pytest.mark.experiments3(
    filename='experiments3_umlaas_queue_predictions.json',
)
async def test_umlaas_prediction_disabled_by_ml_settings(
        taxi_dispatch_airport, testpoint,
):
    @testpoint('airport-queue-predictions-cache-finished')
    def predictions_cache_finished(data):
        return data

    await taxi_dispatch_airport.enable_testpoints()
    await taxi_dispatch_airport.invalidate_caches()

    cache_data = (await predictions_cache_finished.wait_call())['data']
    cache_data.sort(key=lambda x: (x['airport_id'], x['tariff']))
    assert cache_data == [
        {
            'airport_id': 'ekb',
            'tariff': 'business2',
            'driver_needs_count': 20,
            'waiting_times': [],
        },
        {
            'airport_id': 'ekb',
            'tariff': 'comfortplus',
            'driver_needs_count': None,
            'waiting_times': [],
        },
        {
            'airport_id': 'ekb',
            'tariff': 'econom',
            'driver_needs_count': None,
            'waiting_times': [],
        },
        {
            'airport_id': 'svo',
            'tariff': 'comfortplus',
            'driver_needs_count': 20,
            'waiting_times': [],
        },
        {
            'airport_id': 'svo',
            'tariff': 'econom',
            'driver_needs_count': 20,
            'waiting_times': [],
        },
        {
            'airport_id': 'svo',
            'tariff': 'vip',
            'driver_needs_count': 20,
            'waiting_times': [],
        },
    ]
