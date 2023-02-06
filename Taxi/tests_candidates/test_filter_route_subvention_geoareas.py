import pytest

MOSCOW_POINT = [37.618506, 55.751080]
NON_MOSCOW_POINT = [36.0, 54.0]


# pylint: disable=redefined-outer-name
@pytest.mark.config(
    TAGS_INDEX={
        'enabled': True,
        'request_interval': 100,
        'request_size': 8192,
    },
    TAGS_SUBVENTION_GEOAREAS_RULES=[
        {
            'tags': {'any_of': ['ad_moscow']},
            'subvention_geoareas': {
                'point_a': ['moscow-driver-fix'],
                'point_b': ['moscow-driver-fix'],
                'midpoints': ['moscow-driver-fix'],
            },
        },
        {
            'tags': {'any_of': ['driver_fix_moscow']},
            'subvention_geoareas': {'point_b': ['moscow-driver-fix']},
        },
    ],
)
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid0', 'driver_fix_moscow'),
        ('dbid_uuid', 'dbid0_uuid1', 'ad_moscow'),
    ],
)
@pytest.mark.parametrize(
    'source, destinations, destination, expected',
    [
        (None, None, None, []),
        (MOSCOW_POINT, [NON_MOSCOW_POINT, MOSCOW_POINT], None, ['uuid0']),
        (None, None, MOSCOW_POINT, ['uuid0', 'uuid1']),
    ],
)
async def test_filter_route_subvention_geoareas(
        taxi_candidates,
        driver_positions,
        source,
        destinations,
        destination,
        expected,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': MOSCOW_POINT},
            {'dbid_uuid': 'dbid0_uuid1', 'position': MOSCOW_POINT},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 2,
        'filters': [
            'efficiency/fetch_tags',
            'efficiency/route_subvention_geoareas',
        ],
        'zone_id': 'moscow',
        'point': MOSCOW_POINT,
    }

    def to_geopoint(lon_lat):
        return {'geopoint': lon_lat}

    if source is not None:
        request_body.setdefault('order', {}).setdefault('request', {})[
            'source'
        ] = to_geopoint(source)
    if destinations is not None:
        request_body.setdefault('order', {}).setdefault('request', {})[
            'destinations'
        ] = [to_geopoint(dst) for dst in destinations]
    if destination is not None:
        request_body['destination'] = destination

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    candidates = json.get('drivers')
    assert candidates is not None

    actual = sorted([c['uuid'] for c in candidates])
    assert actual == sorted(expected)
