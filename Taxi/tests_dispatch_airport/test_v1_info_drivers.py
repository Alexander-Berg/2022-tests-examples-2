import pytest

from tests_dispatch_airport import common
import tests_dispatch_airport.utils as utils

NUMBER_OF_DRIVERS = 29


def check(etalon, driver):
    near_zone = driver.get('nearest_zone', None)
    active_zone = driver.get('active_zone', None)
    assert bool(near_zone) != bool(active_zone)
    if near_zone:
        assert etalon['nearest_zone'] == near_zone
    else:
        assert etalon['active_zone'] == active_zone

    driver['transitions'].sort(
        key=lambda x: (x['dialog_id'], x.get('from', '')),
    )

    assert etalon['transitions'] == driver['transitions']
    assert etalon['dialogs'] == driver['dialogs']


@pytest.mark.now('2020-05-01T21:00:00+0000')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid_uuid8', 'airport_queue_kick_user_cancel_warning'),
        (
            'dbid_uuid',
            'dbid_uuid10',
            'airport_queue_kick_driver_cancel_warning',
        ),
    ],
    topic_relations=[
        ('airport_queue', 'airport_queue_kick_user_cancel_warning'),
        ('airport_queue', 'airport_queue_kick_driver_cancel_warning'),
    ],
)
@pytest.mark.config(
    DISPATCH_AIRPORT_FORBIDDEN_BY_PARTNER_TIMEOUTS={
        '__default__': {'warn_timeout': 60},
    },
    DISPATCH_AIRPORT_NO_COMMUNICATIONS_FOR_OFFLINE_DRIVERS=True,
)
@pytest.mark.parametrize('hide_no_classes_drivers', [True, False])
async def test_v1_info_drivers(
        taxi_dispatch_airport, taxi_config, load_json, hide_no_classes_drivers,
):
    url = '/v1/info/drivers'
    headers = common.DEFAULT_DISPATCH_AIRPORT_HEADER

    tanker_keys = taxi_config.get('DISPATCH_AIRPORT_ZONES_TANKER_KEYS')
    airport_keys = tanker_keys['airport']
    airport_keys['static'].update(
        {'warn.freeze_expired': 'dispatch_airport.warning.freeze_expired'},
    )
    airport_keys['errors'].update(
        {'freeze_expired': 'dispatch_airport.error.freeze_expired'},
    )
    taxi_config.set_values(tanker_keys)
    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_HIDE_QUEUE_FOR_DRIVER_WITH_NO_CLASSES': (
                hide_no_classes_drivers
            ),
        },
    )

    # dbid_uuid1 - entered (notification zone), not kicked driver
    # dbid_uuid2 - entered (notification zone), no classes
    # dbid_uuid3 - entered (waiting zone), kicked driver

    # dbid_uuid4 - queued, gps warning problem driver
    # dbid_uuid5 - filtered, gps kicked driver
    # dbid_uuid6 - queued, left warning driver
    # dbid_uuid6_2 - queued, left warning driver but with cancelled order
    # dbid_uuid7 - filtered, left kicked driver
    # dbid_uuid8 - queued, user cancel warning driver
    # dbid_uuid9 - filtered, user cancel kicked driver
    # dbid_uuid10 - queued, driver cancel warning
    # dbid_uuid11 - filtered, driver cancel kicked
    # dbid_uuid12 - queued, allowed max time + freeze warnings
    # dbid_uuid13 - filtered, allowed max time kicked driver
    # dbid_uuid14 - filtered, no_classes kicked driver
    # dbid_uuid15 - filtered, holded kicked driver
    # dbid_uuid16 - queued, gps and left warnings driver
    # dbid_uuid17 - filtered, wrong client driver
    # dbid_uuid18 - filtered, not airport input order
    # dbid_uuid19 - filtered, wrong output order
    # dbid_uuid20 - filtered, low order price
    # dbid_uuid21 - filtered, changed tariff
    # dbid_uuid22 - filtered, offline
    # dbid_uuid23 - filtered, left_zone
    # dbid_uuid24 - filtered, gps
    # dbid_uuid25 - entered, offline
    # dbid_uuid26 - filtered, freeze kick
    # dbid_uuid27 - queued, no_classes
    # dbid_uuid28 - queued, gps - no_classes - left queue
    # dbid_uuid29 - queued, gps - left queue - no_classes
    # dbid_uuid30 - entered, waiting zone, forbidden_by_partner info timeout
    # dbid_uuid31 - entered, no_classes
    # dbid_uuid32 - entered, waiting zone, forbidden_by_partner info
    # + no_classes => show forbidden_by_partner info
    # dbid_uuid33 - wrong provider
    # dbid_uuid34 - entered, waiting zone, forbidden_by_partner warn
    # dbid_uuid35 - filtered, offline taximeter off -> no communications
    # dbid_uuid36 - filtered, offline verybusy -> no communications
    # dbid_uuid37 - entered, offline verybusy -> no communications

    etalons = load_json('etalons.json')

    response = await taxi_dispatch_airport.get(
        url, headers=headers, params={'airport': 'ekb'},
    )
    r_json = response.json()
    expected_number_of_drivers = NUMBER_OF_DRIVERS
    if hide_no_classes_drivers:
        expected_number_of_drivers -= 5
        etalons.pop('dbid_uuid27')
        etalons.pop('dbid_uuid28')
        etalons.pop('dbid_uuid29')
        etalons.pop('dbid_uuid31')
        etalons.pop('dbid_uuid32')
    assert len(r_json['driver_infos']) == expected_number_of_drivers
    for driver in r_json['driver_infos']:
        check(etalons[driver['dbid_uuid']], driver)


@pytest.mark.parametrize(
    'config_bits, driver_infos',
    [
        (
            {'distributive_zone_type': 'waiting'},
            [
                {'id': 'dbid_uuid1', 'has_time': False},
                {'id': 'dbid_uuid2', 'has_time': False},
            ],
        ),
        (
            {'distributive_zone_type': 'distributive'},
            [
                {'id': 'dbid_uuid0', 'has_time': False},
                {'id': 'dbid_uuid1', 'has_time': False},
                {'id': 'dbid_uuid2', 'has_time': False},
            ],
        ),
        (
            {},
            [
                {'id': 'dbid_uuid0', 'has_time': True},
                {'id': 'dbid_uuid1', 'has_time': False},
                {'id': 'dbid_uuid2', 'has_time': False},
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'dispatch_airport', files=['drivers_queue_partner_parking_type.sql'],
)
async def test_v1_info_drivers_partner_parking_type(
        taxi_dispatch_airport, taxi_config, config_bits, driver_infos,
):
    config = utils.custom_config(True)
    config['DISPATCH_AIRPORT_ZONES']['ekb'].update(config_bits)
    taxi_config.set_values(config)

    tanker_keys = taxi_config.get('DISPATCH_AIRPORT_ZONES_TANKER_KEYS')
    airport_keys = tanker_keys['airport']
    airport_keys['static'].update(
        {
            'info.waiting_parking_relocation': (
                'dispatch_airport.info.waiting_parking_relocation'
            ),
        },
    )
    taxi_config.set_values(tanker_keys)

    headers = common.DEFAULT_DISPATCH_AIRPORT_HEADER
    response = await taxi_dispatch_airport.get(
        '/v1/info/drivers', headers=headers, params={'airport': 'ekb'},
    )
    infos = [
        {
            'id': info['dbid_uuid'],
            'has_time': (
                'nearest_zone' in info
                and 'queue_exact_time' in info['nearest_zone']
            ),
        }
        for info in response.json()['driver_infos']
    ]

    # dbid_uuid0 - entered notification area
    # dbid_uuid1 - queued
    # dbid_uuid2 - filtered
    assert sorted(infos, key=lambda x: x['id']) == driver_infos

    queued_driver_dialogs = response.json()['driver_infos'][1]['dialogs']
    if config_bits.get('distributive_zone_type') == 'distributive':
        dialog_etalon = 'dispatch_airport.info.waiting_parking_relocation'
    else:
        dialog_etalon = 'dispatch_airport.info.waiting_order'
    assert queued_driver_dialogs[2]['text']['key'] == dialog_etalon


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tags_v2_index(
    tags_list=[],
    topic_relations=[
        ('airport_queue', 'airport_queue_kick_user_cancel_warning'),
        ('airport_queue', 'airport_queue_kick_driver_cancel_warning'),
    ],
)
@pytest.mark.pgsql('dispatch_airport', files=['taximeter_visible_queue.sql'])
async def test_taximeter_visible_area(
        taxi_dispatch_airport, load_json, taxi_config,
):
    url = '/v1/info/drivers'
    headers = common.DEFAULT_DISPATCH_AIRPORT_HEADER
    # ekb has a defined taximeter_visible_area => it is shown
    # svo has a defined taximeter_visible_area and
    # has ekb as a distributive zone => ekb taximeter_visible_area
    # is shown
    config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    config['ekb'].update(
        {
            'distributive_zone_type': 'distributive',
            'group_id': '1',
            'taximeter_visible_area': 'ekb_airport',
        },
    )
    config['svo'].update(
        {
            'group_id': '1',
            'distributive_zone_type': 'waiting',
            'taximeter_visible_area': 'svo_airport',
        },
    )
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': config})

    # dbid_uuid1 - entered, ekb
    # dbid_uuid2 - queued, ekb
    # dbid_uuid3 - entered, svo - replaced by ekb
    # dbid_uuid4 - queued, svo - is not replaced

    etalons = load_json('taximeter_visible_etalons.json')

    for airport in ['ekb', 'svo']:
        response = await taxi_dispatch_airport.get(
            url, headers=headers, params={'airport': airport},
        )
        r_json = response.json()
        assert len(r_json['driver_infos']) == 2
        for driver in r_json['driver_infos']:
            check(etalons[airport][driver['dbid_uuid']], driver)


@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.now('2020-05-01T21:00:00+0000')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.experiments3(
    filename='experiments3_umlaas_queue_predictions.json',
)
@pytest.mark.config(
    DISPATCH_AIRPORT_NO_COMMUNICATIONS_FOR_OFFLINE_DRIVERS=True,
)
async def test_v1_waiting_times_ml_prediction(
        taxi_dispatch_airport, load_json, taxi_config,
):
    url = '/v1/info/drivers'
    headers = common.DEFAULT_DISPATCH_AIRPORT_HEADER

    etalons = load_json('etalons.json')

    response = await taxi_dispatch_airport.get(
        url, headers=headers, params={'airport': 'ekb'},
    )
    r_json = response.json()
    assert len(r_json['driver_infos']) == NUMBER_OF_DRIVERS
    for driver in r_json['driver_infos']:
        etalon_zone = etalons[driver['dbid_uuid']].get('active_zone')
        zone = driver.get('active_zone')
        if etalon_zone is None:
            assert zone is None
            continue

        etalon_queues_infos = etalon_zone['queues_infos']
        queues_infos = zone['queues_infos']

        assert etalon_queues_infos == queues_infos


@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.now('2020-05-01T21:00:00+0000')
@pytest.mark.parametrize('umlaas_data_ttl_reached', [True, False])
@pytest.mark.experiments3(
    filename='experiments3_umlaas_queue_predictions.json',
)
@pytest.mark.config(
    DISPATCH_AIRPORT_NO_COMMUNICATIONS_FOR_OFFLINE_DRIVERS=True,
)
async def test_waiting_times_umlaas_data_ttl(
        taxi_dispatch_airport,
        load_json,
        taxi_config,
        mockserver,
        mocked_time,
        umlaas_data_ttl_reached,
):
    url = '/v1/info/drivers'
    headers = common.DEFAULT_DISPATCH_AIRPORT_HEADER

    etalons = load_json('etalons.json')

    await taxi_dispatch_airport.invalidate_caches()

    @mockserver.json_handler('/umlaas/airport_queue_size/v1')
    def _umlaas(request):
        return mockserver.make_response('fail', status=500)

    taxi_config.set(DISPATCH_AIRPORT_UMLAAS_DATA_TTL=1)
    if umlaas_data_ttl_reached:
        mocked_time.sleep(61)
    await taxi_dispatch_airport.invalidate_caches()

    response = await taxi_dispatch_airport.get(
        url, headers=headers, params={'airport': 'ekb'},
    )
    r_json = response.json()
    assert len(r_json['driver_infos']) == NUMBER_OF_DRIVERS
    for driver in r_json['driver_infos']:
        etalon_zone = etalons[driver['dbid_uuid']].get('active_zone')
        zone = driver.get('active_zone')
        if etalon_zone is None:
            assert zone is None
            continue

        etalon_queues_infos = etalon_zone['queues_infos']
        queues_infos = zone['queues_infos']
        if umlaas_data_ttl_reached:
            for info in etalon_queues_infos:
                info.pop('queue_exact_time', None)
            queues_infos = sorted(queues_infos, key=lambda x: x['class_name'])
            etalon_queues_infos = sorted(
                etalon_queues_infos, key=lambda x: x['class_name'],
            )

        assert etalon_queues_infos == queues_infos


@pytest.mark.parametrize(
    'group_ids',
    [
        {'ekb': 'test_group_id_1', 'svo': None},
        {'ekb': 'test_group_id_1', 'svo': 'test_group_id_2'},
        {'ekb': 'test_group_id_1', 'svo': 'test_group_id_1'},
    ],
)
@pytest.mark.pgsql(
    'dispatch_airport', files=['drivers_queue_group_partner_parking_type.sql'],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_v1_info_drivers_group_partner_parking_type(
        taxi_dispatch_airport, taxi_config, load_json, group_ids,
):
    # dbid_uuid0 - entered driver in notification zone
    # dbid_uuid1 - entered driver in waiting zone

    config = taxi_config.get_values()['DISPATCH_AIRPORT_ZONES']
    for airport_id in ('ekb', 'svo'):
        config[airport_id].update({'group_id': group_ids[airport_id]})
    config['ekb']['distributive_zone_type'] = 'waiting'
    config['svo']['distributive_zone_type'] = 'distributive'
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': config})

    headers = common.DEFAULT_DISPATCH_AIRPORT_HEADER
    response = await taxi_dispatch_airport.get(
        '/v1/info/drivers', headers=headers, params={'airport': 'ekb'},
    )
    sorted_response = response.json()
    sorted_response['driver_infos'] = sorted(
        sorted_response['driver_infos'], key=lambda x: x['dbid_uuid'],
    )
    result = {'driver_infos': []}
    if group_ids['ekb'] == group_ids['svo']:
        result = load_json('group_partner_parking_type_etalon.json')
    assert result == sorted_response


@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.now('2020-05-01T21:00:00+0000')
@pytest.mark.geoareas(filename='geoareas.json')
async def test_v1_info_drivers_hide_etr(
        taxi_dispatch_airport, taxi_config, load_json,
):
    url = '/v1/info/drivers'
    headers = common.DEFAULT_DISPATCH_AIRPORT_HEADER

    config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    config['ekb']['whitelist_classes']['econom'][
        'hide_queue_exact_time'
    ] = True
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': config})

    response = await taxi_dispatch_airport.get(
        url, headers=headers, params={'airport': 'ekb'},
    )
    r_json = response.json()

    etalon = load_json('hidden_etr_etalon.json')

    for driver in r_json['driver_infos']:
        if driver['dbid_uuid'] in etalon:
            for queue in driver['active_zone']['queues_infos']:
                if 'queue_exact_time' in queue:
                    assert (
                        queue['queue_exact_time']
                        == etalon[driver['dbid_uuid']][queue['class_name']]
                    )
                else:
                    assert (
                        etalon[driver['dbid_uuid']][queue['class_name']]
                        is None
                    )


@pytest.mark.now('2020-05-01T21:00:00+0000')
@pytest.mark.pgsql(
    'dispatch_airport', files=['drivers_queue_parking_relocation.sql'],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_v1_info_drivers_parking_relocation(
        taxi_dispatch_airport, load_json, taxi_config,
):
    tanker_keys = taxi_config.get('DISPATCH_AIRPORT_ZONES_TANKER_KEYS')
    airport_keys = tanker_keys['airport']
    airport_keys['static'].update(
        {
            'info.parking_relocation': (
                'dispatch_airport.info.parking_relocation'
            ),
        },
    )
    taxi_config.set_values(tanker_keys)

    # dbid_uuid0 - queued driver with parking repo
    # dbid_uuid1 - filtered driver with parking repo
    # dbid_uuid2 - entered driver by parking repo

    headers = common.DEFAULT_DISPATCH_AIRPORT_HEADER
    response = await taxi_dispatch_airport.get(
        '/v1/info/drivers', headers=headers, params={'airport': 'ekb'},
    )
    sorted_response = response.json()
    sorted_response['driver_infos'] = sorted(
        sorted_response['driver_infos'], key=lambda x: x['dbid_uuid'],
    )
    result = load_json('parking_relocation_etalon.json')
    assert result == sorted_response
