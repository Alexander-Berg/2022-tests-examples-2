import pytest


@pytest.mark.config(
    LOGISTIC_SUPPLY_CONDUCTOR_SUPPLY_REGIONS={
        'enable_filter': True,
        'enable_logistic_workshifts_filtering_by_employer': True,
        'enable_logistic_workshifts_filtering_by_source': True,
    },
    API_OVER_DATA_ENABLE_CACHES=True,
    API_OVER_DATA_ENABLE_SPECIFIC_CACHE={
        'candidates': {'logistic-supply-conductor': True},
    },
    API_OVER_DATA_OPENING_LAG_MS={
        'candidates': {'logistic-supply-conductor': -1},
    },
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={
        '3fbec49a491248328a0d9ab1c8ba7891': 'eda',
        '27751a2d0b534affb80d243bc2f68981': 'vkusvill',
        '6ff90205fcf648018aecb61b61d2ec32': 'lavka',
    },
)
@pytest.mark.parametrize(
    'request_extra, expected_candidates',
    [
        (
            {
                'point': [55, 35],
                'order': {
                    'request': {
                        'corp': {
                            'client_id': '3fbec49a491248328a0d9ab1c8ba7891',
                        },
                    },
                },
            },
            {'uuid11', 'uuid12'},
        ),
        (
            {
                'point': [55, 63],
                'order': {
                    'request': {
                        'corp': {
                            'client_id': '3fbec49a491248328a0d9ab1c8ba7891',
                        },
                    },
                },
            },
            {'uuid10', 'uuid12'},
        ),
        ({'point': [55, 55]}, {'uuid12'}),
        (
            {
                'order': {
                    'request': {
                        'source': {'geopoint': [55, 35]},
                        'destinations': [
                            {'geopoint': [55, 35.01]},
                            {'geopoint': [55, 35.02]},
                            {'geopoint': [55, 35.03]},
                        ],
                        'corp': {
                            'client_id': '3fbec49a491248328a0d9ab1c8ba7891',
                        },
                    },
                },
            },
            {'uuid11', 'uuid12'},
        ),
        (
            {
                'order': {
                    'request': {
                        'source': {'geopoint': [55, 35]},
                        'destinations': [
                            {'geopoint': [55, 35.01]},
                            {'geopoint': [55, 35.02]},
                            {'geopoint': [55, 35.03]},
                        ],
                        'corp': {
                            'client_id': '27751a2d0b534affb80d243bc2f68981',
                        },
                    },
                },
            },
            {'uuid11', 'uuid12'},
        ),
        (
            {
                'point': [55, 35],
                'order': {
                    'request': {
                        'corp': {
                            'client_id': '6ff90205fcf648018aecb61b61d2ec32',
                        },
                    },
                },
            },
            {'uuid12'},
        ),
        ({'point': [55, 63]}, {'uuid12', 'uuid13'}),
    ],
)
async def test_workshifts(
        taxi_candidates, driver_positions, request_extra, expected_candidates,
):
    # using different dbid_uuid here because of api_over_db bug
    # TODO : fix after TAXIHEJMDAL-653
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid10', 'position': [56, 36]},
            {'dbid_uuid': 'dbid0_uuid11', 'position': [55, 36]},
            {'dbid_uuid': 'dbid0_uuid12', 'position': [54, 36]},
            {'dbid_uuid': 'dbid0_uuid13', 'position': [56, 36]},
        ],
    )

    await taxi_candidates.invalidate_caches()

    request_body = {
        'geoindex': 'kdtree',
        'max_distance': 9999999,
        'limit': 3,
        'filters': ['logistic/supply_regions'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    request_body.update(request_extra)

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = set(d['uuid'] for d in json['drivers'])
    assert drivers == expected_candidates
