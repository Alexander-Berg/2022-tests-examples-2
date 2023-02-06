import pytest


_DEFAULT_ROUTER_SELECT = [
    {'routers': ['yamaps']},
    {'ids': ['moscow'], 'routers': ['linear-fallback']},
]


@pytest.mark.config(
    TAGS_INDEX={'enabled': True},
    CANDIDATES_SHIFT_SETTINGS={
        'eats': {'classes': ['eda']},
        'grocery': {'classes': ['uberblack', 'uberx']},
    },
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT,
    EXTRA_EXAMS_BY_ZONE={},
)
@pytest.mark.tags_v2_index(
    tags_list=[
        # lavka_courier
        ('dbid_uuid', 'dbid0_uuid0', 'lavka_courier'),
        ('dbid_uuid', 'dbid0_uuid1', 'lavka_courier'),
        # underage couriers
        ('dbid_uuid', 'dbid0_uuid0', 'grocery_male_under18_rus'),
        ('dbid_uuid', 'dbid0_uuid1', 'grocery_female_under18_rus'),
    ],
)
@pytest.mark.now('2020-07-28T10:30:00+00:00')
async def test_weight(
        taxi_candidates,
        driver_positions,
        experiments3,
        mockserver,
        grocery_depots,
):
    grocery_depots.add_depot(0, legacy_depot_id='2020')

    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v2/queue-info',
    )
    def _mock_queue_info(_request):
        return {
            'couriers': [
                {
                    'courier_id': 'dbid0_uuid0',
                    'checkin_timestamp': '2020-07-28T10:00:00+0000',
                },
                {
                    'courier_id': 'dbid0_uuid1',
                    'checkin_timestamp': '2021-07-28T10:00:00+0000',
                },
            ],
        }

    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v1/shifts/shifts-info',
    )
    def _mock_courier_shift_states(request):
        by_depots = {
            # external_depot_id -> shift response
            '2020': {
                'shifts': [
                    {
                        'performer_id': 'dbid0_uuid0',
                        'shift_id': '19950',
                        'shift_status': 'in_progress',
                        'started_at': '2020-07-28T10:00:00Z',
                        'closes_at': '2020-07-28T11:00:00Z',
                        'shift_type': 'wms',
                    },
                    {
                        'performer_id': 'dbid0_uuid1',
                        'shift_id': '19951',
                        'shift_status': 'in_progress',
                        'started_at': '2020-07-28T10:00:00Z',
                        'closes_at': '2020-07-28T11:00:00Z',
                        'shift_type': 'wms',
                    },
                ],
            },
        }
        return by_depots.get(request.json['depot_id'], {'shifts': []})

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'underage male',
                'predicate': {
                    'type': 'contains',
                    'init': {
                        'arg_name': 'tags',
                        'set_elem_type': 'string',
                        'value': 'grocery_male_under18_rus',
                    },
                },
                'value': {'enabled': True, 'weight': {'max': 4000}},
            },
            {
                'title': 'underage female',
                'predicate': {
                    'type': 'contains',
                    'init': {
                        'arg_name': 'tags',
                        'set_elem_type': 'string',
                        'value': 'grocery_female_under18_rus',
                    },
                },
                'value': {'enabled': True, 'weight': {'max': 3000}},
            },
        ],
        name='grocery_couriers_weight_limits',
        consumers=['candidates/grocery'],
        default_value={
            'enabled': True,
            'weight': {},
        },  # no weight, for test only
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 10,
        'max_distance': 100000,
        'point': [37.630971, 55.743789],
        'filters': ['grocery/fetch_weight'],
        'allowed_classes': ['uberblack', 'uberx'],
        'order': {
            'request': {
                'shift': {
                    'type': 'grocery',
                    'zone_group': {'required_ids': ['2020']},
                },
            },
        },
    }
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.630971, 55.743789]},
        ],
    )
    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200
    assert sorted([('uuid0', 4000), ('uuid1', 3000)]) == sorted(
        [
            (driver['uuid'], driver['logistic']['weight']['max'])
            for driver in response.json()['candidates']
        ],
    )
