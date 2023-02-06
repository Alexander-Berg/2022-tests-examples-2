import pytest

AIRPORT_POINT = [37.584373, 55.817079]
CITY_POINT = [37.646516, 55.665302]


def get_airport_zones_config():
    return {
        'moscow': {
            'airport_title_key': 'moscow_airport_key',
            'enabled': True,
            'main_area': 'moscow_airport',
            'notification_area': 'moscow_airport_notification',
            'old_mode_enabled': False,
            'tariff_home_zone': 'moscow',
            'update_interval_sec': 5,
            'use_queue': True,
            'waiting_area': 'moscow_airport_waiting',
            'whitelist_classes': {
                'econom': {'reposition_enabled': False, 'nearest_mins': 60},
            },
            'mix_city_orders': True,
        },
    }


def get_request_body(uuids, point, destination, order_calc_time=0):
    request_body = {
        'driver_ids': [{'uuid': uuid, 'dbid': 'dbid0'} for uuid in uuids],
        'geoindex': 'graph',
        'max_distance': 9999999,
        'limit': 3,
        'filters': ['efficiency/airport_entry_limit'],
        'point': point,
        'destination': destination,
        'zone_id': 'moscow_airport',
        'order': {'calc': {'time': order_calc_time}},
    }

    return request_body


@pytest.mark.parametrize(
    'order_point, order_dest, limit_end, order_time, '
    'use_ttl_config, is_driver_in_result',
    [
        # Order not in airport
        (CITY_POINT, CITY_POINT, '2020-04-20T20:10:00+00:00', 0, False, True),
        # Source in airport, no limit
        (AIRPORT_POINT, CITY_POINT, None, 0, False, True),
        # Source in airport, has limit
        (
            AIRPORT_POINT,
            CITY_POINT,
            '2020-04-20T20:00:00+00:00',
            0,
            False,
            False,
        ),
        # Source in airport, limit drops
        (
            AIRPORT_POINT,
            CITY_POINT,
            '2020-04-20T09:55:00+00:00',
            0,
            False,
            True,
        ),
        # Source in airport, limit doesn't drop cause with config
        (
            AIRPORT_POINT,
            CITY_POINT,
            '2020-04-20T09:55:00+00:00',
            0,
            True,
            False,
        ),
        # Destination in airport, no limit
        (CITY_POINT, AIRPORT_POINT, None, 0, False, True),
        # Destination in airport, has limit
        (
            CITY_POINT,
            AIRPORT_POINT,
            '2020-04-20T20:00:00+00:00',
            0,
            False,
            False,
        ),
        # Destination in airport, limit drops 1
        (
            CITY_POINT,
            AIRPORT_POINT,
            '2020-04-20T10:00:00+00:00',
            0,
            False,
            True,
        ),
        # Destination in airport, limit drops 2
        (
            CITY_POINT,
            AIRPORT_POINT,
            '2020-04-20T10:00:00+00:00',
            100000,
            False,
            True,
        ),
        # Destination in airport, limit drops 3
        (
            CITY_POINT,
            AIRPORT_POINT,
            '2020-04-20T11:00:00+00:00',
            2000,
            False,
            True,
        ),
        # Destination in airport, limit doesn't drop with config
        (
            CITY_POINT,
            AIRPORT_POINT,
            '2020-04-20T11:00:00+00:00',
            2000,
            True,
            False,
        ),
    ],
)
@pytest.mark.geoareas(filename='airport_geoareas_graph_search.json')
@pytest.mark.config(
    DISPATCH_AIRPORT_CACHE_TTL=10,
    DISPATCH_AIRPORT_ZONES=get_airport_zones_config(),
    DISPATCH_AIRPORT_AREA_ENTRY_TRACKING={
        'moscow': {'candidates_filter_settings': {'': True}},
    },
    DISPATCH_AIRPORT_QUEUES_CACHE_GET_ENTRY_LIMIT_REACHED=True,
)
@pytest.mark.now('2020-04-20T10:00:00+00:00')
async def test_airport_idx(
        taxi_candidates,
        taxi_config,
        driver_positions,
        mockserver,
        order_point,
        order_dest,
        limit_end,
        order_time,
        use_ttl_config,
        is_driver_in_result,
):
    if use_ttl_config:
        add_raw = 300
        add_percent = 0.2
    else:
        add_raw = 0
        add_percent = 0
    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_AREA_ENTRY_TRACKING': {
                'moscow': {
                    'candidates_filter_settings': {
                        'filter_enabled': True,
                        'eta_correction_raw': add_raw,
                        'eta_correction_percent': add_percent,
                    },
                },
            },
        },
    )

    @mockserver.json_handler('/dispatch-airport/v1/active-drivers-queues')
    def _active_drivers_queues(request):
        if limit_end:
            return {
                'queues': [],
                'entry_limit_reached': [
                    {'dbid_uuid': 'dbid0_uuid0', 'limit_end_ts': limit_end},
                ],
            }
        return {'queues': [], 'entry_limit_reached': []}

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': AIRPORT_POINT}],
    )

    request_body = get_request_body(
        uuids=['uuid0'],
        point=order_point,
        destination=order_dest,
        order_calc_time=order_time,
    )
    await taxi_candidates.invalidate_caches(
        cache_names=['dispatch-airport-queues-cache'],
    )
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    if is_driver_in_result:
        assert len(json['drivers']) == 1
        assert json['drivers'][0]['uuid'] == 'uuid0'
    else:
        assert not json['drivers']
