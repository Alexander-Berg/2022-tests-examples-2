import pytest


_DEFAULT_ROUTER_SELECT = [
    {'routers': ['yamaps']},
    {'ids': ['moscow'], 'routers': ['linear-fallback']},
]


def _get_candidates(json):
    # ignore some redundant and volatile fields
    whitelist = set(['position', 'classes', 'is_satisfied', 'reasons'])

    candidates = {}
    for candidate in json['candidates']:
        candidates[candidate['id']] = {
            k: candidate[k] for k in whitelist if k in candidate
        }

    return candidates


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
async def test_order_satisfy(taxi_candidates, taxi_config, driver_positions):

    # dbid1_uuid3 drivers park(clid1) deactivated
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [55, 35]},
        ],
    )
    body = {
        'driver_ids': [
            {'uuid': 'uuid0', 'dbid': 'dbid0'},
            {'uuid': 'uuid1', 'dbid': 'dbid0'},
            {'uuid': 'uuid3', 'dbid': 'dbid1'},
            {'uuid': 'uuid8', 'dbid': 'dbid0'},
        ],
        'allowed_classes': ['econom'],
        'zone_id': 'moscow',
        'point': [55, 35],
    }
    response = await taxi_candidates.post('order-satisfy', json=body)
    assert response.status_code == 200
    json = response.json()
    candidates = _get_candidates(json)

    assert candidates == {
        'dbid0_uuid0': {
            'classes': ['econom'],
            'position': [55.0, 35.0],
            'is_satisfied': True,
        },
        'dbid0_uuid1': {
            'position': [55.0, 35.0],
            'is_satisfied': False,
            'reasons': {'infra/fetch_profile_classes': []},
        },
        'dbid1_uuid3': {
            'classes': ['econom'],
            'position': [55.0, 35.0],
            'is_satisfied': False,
            'reasons': {'infra/deactivated_park_v2': []},
        },
        'dbid0_uuid8': {
            'position': [0, 0],
            'is_satisfied': False,
            'reasons': {
                'infra/fetch_route_info': [],
                'infra/fetch_position_timestamps': [],
                'infra/meta_status_searchable': [],
                'infra/fetch_driver': [],
            },
        },
    }


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
async def test_order_satisfy_no_position(
        taxi_candidates, driver_positions, taxi_config,
):

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]}],
    )
    body = {
        'driver_ids': [
            {'uuid': 'uuid0', 'dbid': 'dbid0'},
            {'uuid': 'uuid1', 'dbid': 'dbid0'},
        ],
        'allowed_classes': ['econom'],
        'zone_id': 'moscow',
        'point': [55, 35],
    }
    response = await taxi_candidates.post('order-satisfy', json=body)
    assert response.status_code == 200
    json = response.json()
    candidates = _get_candidates(json)

    assert candidates == {
        'dbid0_uuid0': {
            'classes': ['econom'],
            'position': [0, 0],
            'is_satisfied': False,
            'reasons': {
                'infra/fetch_route_info': [],
                'infra/fetch_position_timestamps': [],
            },
        },
        'dbid0_uuid1': {
            'position': [55.0, 35.0],
            'is_satisfied': False,
            'reasons': {'infra/fetch_profile_classes': []},
        },
    }
