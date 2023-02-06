import pytest


_DEFAULT_ROUTER_SELECT = [
    {'routers': ['yamaps']},
    {'ids': ['moscow'], 'routers': ['linear-fallback']},
]


@pytest.mark.config(
    TAGS_INDEX={'enabled': True},
    CANDIDATES_SHIFT_SETTINGS={
        'grocery': {'classes': ['uberblack', 'uberx']},
        'eats': {'classes': ['eda']},
    },
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT,
    EXTRA_EXAMS_BY_ZONE={},
    CANDIDATES_FILTER_GROCERY_STOREKEEPER_COURIERS_TAGS=['lavka_storekeeper'],
)
@pytest.mark.tags_v2_index(
    tags_list=[
        # lavka_courier
        ('dbid_uuid', 'dbid0_uuid0', 'lavka_courier'),
        ('dbid_uuid', 'dbid0_uuid1', 'lavka_courier'),
        # storekeeper couriers
        ('dbid_uuid', 'dbid0_uuid1', 'lavka_storekeeper'),
    ],
)
@pytest.mark.parametrize(
    'exclude_storekeepers, expected_couriers',
    [(True, ['dbid0_uuid0']), (False, ['dbid0_uuid0', 'dbid0_uuid1'])],
)
async def test_exclude_storekeepers(
        taxi_candidates,
        driver_positions,
        exclude_storekeepers,
        expected_couriers: list,
        grocery_depots,
        mockserver,
):
    grocery_depots.add_depot(0, legacy_depot_id='12345')
    grocery_depots.add_depot(1, legacy_depot_id='67890')

    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v1/shifts/shifts-info',
    )
    def _grocery_shifts_info(request):
        by_depots = {
            # external_depot_id -> shift response
            '12345': {
                'shifts': [
                    {
                        'performer_id': 'dbid0_uuid0',
                        'shift_id': '19950',
                        'shift_status': 'closed',
                        'started_at': '2020-07-28T08:47:00Z',
                        'closes_at': '2020-07-28T09:07:12Z',
                        'shift_type': 'wms',
                    },
                ],
            },
            '67890': {
                'shifts': [
                    {
                        'performer_id': 'dbid0_uuid1',
                        'shift_id': '19951',
                        'shift_status': 'in_progress',
                        'started_at': '2020-07-28T08:47:00Z',
                        'closes_at': '2020-07-28T09:07:12Z',
                        'shift_type': 'wms',
                    },
                ],
            },
        }
        return by_depots.get(request.json['depot_id'], {'shifts': []})

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.630971, 55.743789]},
        ],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 10,
        'point': [37.630971, 55.743789],
        'allowed_classes': ['uberblack', 'uberx'],
        'order': {
            'request': {
                'shift': {
                    'type': 'grocery',
                    'zone_group': {'required_ids': ['67890', '12345']},
                },
            },
        },
        'filters': (
            ['grocery/storekeeper_couriers'] if exclude_storekeepers else []
        ),
    }

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200, response.text

    candidates = response.json()['drivers']
    candidates_list = [
        candidate['dbid'] + '_' + candidate['uuid'] for candidate in candidates
    ]
    assert sorted(candidates_list) == sorted(expected_couriers)
