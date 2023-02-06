import bson
import pytest


import tests_candidates.helpers


def _mock_virtual_tariffs(mockserver):
    @mockserver.json_handler(
        '/virtual-tariffs/v1/special-requirements/updates',
    )
    def _special_requirements_updates(request):
        cursor = 'string'
        if not request.query:
            return {
                'special_requirements': [
                    {
                        'id': 'wrong_requirement',
                        'requirements': [
                            {
                                'field': 'foo',
                                'operation': 'bar',
                                'arguments': [{'value': 'ыыыы'}],
                            },
                        ],
                    },
                    {
                        'id': 'tag_group1',
                        'requirements': [
                            {
                                'field': 'Tags',
                                'operation': 'ContainsAll',
                                'arguments': [
                                    {'value': 'tag1'},
                                    {'value': 'tag2'},
                                    {'value': 'tag3'},
                                ],
                            },
                        ],
                    },
                    {
                        'id': 'tag_group2',
                        'requirements': [
                            {
                                'field': 'Tags',
                                'operation': 'ContainsAll',
                                'arguments': [
                                    {'value': 'tag1'},
                                    {'value': 'tag2'},
                                    {'value': 'tag3'},
                                    {'value': 'tag4'},
                                ],
                            },
                        ],
                    },
                    {
                        'id': 'my_driver',
                        'requirements': [
                            {
                                'field': 'Tags',
                                'operation': 'ContainsAll',
                                'arguments': [
                                    {'value': 'tag1'},
                                    {'value': 'tag2'},
                                    {'value': 'tag3'},
                                ],
                            },
                            {
                                'field': 'TaximeterFeatures',
                                'operation': 'ContainsAll',
                                'arguments': [
                                    {'value': 'feature1'},
                                    {'value': 'feature2'},
                                ],
                            },
                            {
                                'field': 'Exams',
                                'operation': 'ContainsAll',
                                'arguments': [{'value': 'econom'}],
                            },
                        ],
                    },
                ],
                'cursor': cursor,
                'has_more_records': True,
            }
        assert request.query['cursor'] == cursor
        return {
            'special_requirements': [],
            'cursor': cursor,
            'has_more_records': False,
        }


@pytest.mark.tags_v2_index(
    tags_list=[
        ('park_car_id', 'dbid0_car_id0', 'tag1'),
        ('dbid_uuid', 'dbid0_uuid0', 'tag2'),
        ('dbid_uuid', 'dbid0_uuid0_unregistered', 'tag4'),
        ('udid', '56f968f07c0aa65c44998e4b', 'tag3'),
    ],
)
@pytest.mark.config(
    ROUTER_SELECT=[
        {'routers': ['yamaps']},
        {'ids': ['moscow'], 'routers': ['linear-fallback']},
    ],
    EXTRA_EXAMS_BY_ZONE={},
    TAGS_INDEX={'enabled': True},
)
async def test_tags_required(
        taxi_candidates, driver_positions, mock_virtual_tariffs,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )
    body = {
        'allowed_classes': ['econom'],
        'limit': 3,
        'zone_id': 'moscow',
        'point': [55, 35],
        'order': {
            'virtual_tariffs': [
                {
                    'class': 'econom',
                    'special_requirements': [{'id': 'tag_group1'}],
                },
            ],
        },
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(),
        expected={
            'candidates': [
                {
                    'id': 'dbid0_uuid0',
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'car_number': '\u0425492\u041d\u041a77',
                    'classes': ['econom'],
                    'position': [55.0, 35.0],
                    'route_info': {
                        'distance': 0,
                        'time': 0,
                        'approximate': False,
                    },
                    'status': {
                        'driver': 'free',
                        'orders': [],
                        'status': 'online',
                        'taximeter': 'free',
                    },
                    'unique_driver_id': '56f968f07c0aa65c44998e4b',
                    'license_id': 'AB0253_id',
                    'transport': {'type': 'car'},
                },
            ],
        },
    )
    assert actual == expected

    body = {
        'allowed_classes': ['econom'],
        'limit': 3,
        'zone_id': 'moscow',
        'point': [55, 35],
        'order': {
            'virtual_tariffs': [
                {
                    'class': 'econom',
                    'special_requirements': [{'id': 'tag_group2'}],
                },
            ],
        },
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    assert response.json() == {'candidates': []}


@pytest.mark.tags_v2_index(
    tags_list=[
        ('park_car_id', 'dbid0_car_id0', 'tag1'),
        ('dbid_uuid', 'dbid0_uuid0', 'tag2'),
        ('dbid_uuid', 'dbid0_uuid0_unregistered', 'tag4'),
        ('udid', '56f968f07c0aa65c44998e4b', 'tag3'),
    ],
)
@pytest.mark.config(
    ROUTER_SELECT=[
        {'routers': ['yamaps']},
        {'ids': ['moscow'], 'routers': ['linear-fallback']},
    ],
    EXTRA_EXAMS_BY_ZONE={},
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'disabled': [],
            'feature_support': {'feature1': '9.00'},
            'min': '7.00',
        },
        'taximeter-beta': {
            'disabled': [],
            'feature_support': {'feature2': '9.01'},
            'min': '8.00',
        },
    },
    TAGS_INDEX={'enabled': True},
)
async def test_filter_virtual_tariffs(
        taxi_candidates, driver_positions, mongodb, mockserver,
):
    _mock_virtual_tariffs(mockserver)
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )
    body = {
        'allowed_classes': ['econom'],
        'limit': 3,
        'zone_id': 'moscow',
        'point': [55, 35],
        'order': {
            'virtual_tariffs': [
                {
                    'class': 'econom',
                    'special_requirements': [{'id': 'my_driver'}],
                },
            ],
        },
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(),
        expected={
            'candidates': [
                {
                    'id': 'dbid0_uuid0',
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'car_number': '\u0425492\u041d\u041a77',
                    'classes': ['econom'],
                    'position': [55.0, 35.0],
                    'route_info': {
                        'distance': 0,
                        'time': 0,
                        'approximate': False,
                    },
                    'status': {
                        'driver': 'free',
                        'orders': [],
                        'status': 'online',
                        'taximeter': 'free',
                    },
                    'unique_driver_id': '56f968f07c0aa65c44998e4b',
                    'license_id': 'AB0253_id',
                    'transport': {'type': 'car'},
                },
            ],
        },
    )
    assert actual == expected
    # banned by version features
    mongodb.dbdrivers.update(
        {'park_id': 'dbid0', 'driver_id': 'uuid0'},
        {'$set': {'taximeter_version': '8.01 (123)'}},
    )
    await taxi_candidates.invalidate_caches()
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    assert json == {'candidates': []}
    # banned by exams
    mongodb.dbdrivers.update(
        {'park_id': 'dbid0', 'driver_id': 'uuid0'},
        {'$set': {'taximeter_version': '9.29 (123)'}},
    )
    mongodb.unique_drivers.update(
        {'_id': bson.ObjectId('56f968f07c0aa65c44998e4b')},
        {'$set': {'exams': []}},
    )
    await taxi_candidates.invalidate_caches()
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    assert json == {'candidates': []}


@pytest.mark.config(
    ROUTER_SELECT=[
        {'routers': ['yamaps']},
        {'ids': ['moscow'], 'routers': ['linear-fallback']},
    ],
    TAGS_INDEX={'enabled': True},
)
@pytest.mark.parametrize('ignore_thermobag_requirement', [False, True])
async def test_ignore_special_requirement(
        taxi_candidates,
        driver_positions,
        mock_virtual_tariffs,
        mockserver,
        ignore_thermobag_requirement,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )

    @mockserver.json_handler('/cargo-claims/v1/claims/list/performer-lookup')
    def _mock_active_claims(request):
        response = {
            'claims': [
                {'claim_id': 'cargo_order', 'allowed_classes': ['econom']},
            ],
        }
        if ignore_thermobag_requirement:
            response['claims'][0]['ignorable_special_requirements'] = [
                {'tariff_class': 'econom', 'requirements': ['tag_group1']},
            ]
        return response

    body = {
        'allowed_classes': ['econom'],
        'limit': 3,
        'zone_id': 'moscow',
        'point': [55, 35],
        'order': {
            'cargo_ref_id': 'cargo_order',
            'virtual_tariffs': [
                {
                    'class': 'econom',
                    'special_requirements': [{'id': 'tag_group1'}],
                },
            ],
        },
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = set(d['uuid'] for d in json['candidates'])

    if ignore_thermobag_requirement:
        assert candidates == {'uuid0'}
    else:
        assert not candidates


@pytest.mark.config(
    ROUTER_SELECT=[
        {'routers': ['yamaps']},
        {'ids': ['moscow'], 'routers': ['linear-fallback']},
    ],
    TAGS_INDEX={'enabled': True},
)
@pytest.mark.parametrize(
    'claims_cache,ignore_thermobag_requirement',
    [
        pytest.param(
            {
                'claim1': {'ignore_requirements': ['tag_group1']},
                'claim2': {'ignore_requirements': ['tag_group1']},
            },
            True,
            id='both-in-cache-ignore-requirement',
        ),
        pytest.param(
            {'claim1': {'ignore_requirements': ['tag_group1']}},
            True,
            id='only-one-in-cache-ignore-requirement',
        ),
        pytest.param({}, False, id='empty-cache-no-ignore-requirement'),
    ],
)
async def test_merged_requirements(
        taxi_candidates,
        driver_positions,
        mock_virtual_tariffs,
        mockserver,
        claims_cache,
        ignore_thermobag_requirement,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )

    @mockserver.json_handler('/cargo-claims/v1/claims/list/performer-lookup')
    def _mock_active_claims(request):
        claims = []
        for claim_id, params in claims_cache.items():
            record = {'claim_id': claim_id, 'allowed_classes': ['econom']}
            if params.get('ignore_requirements'):
                record['ignorable_special_requirements'] = [
                    {
                        'tariff_class': 'econom',
                        'requirements': params['ignore_requirements'],
                    },
                ]
            claims.append(record)
        return {'claims': claims}

    body = {
        'allowed_classes': ['econom'],
        'limit': 3,
        'zone_id': 'moscow',
        'point': [55, 35],
        'order': {
            'cargo_ref_ids': ['claim1', 'claim2'],
            'virtual_tariffs': [
                {
                    'class': 'econom',
                    'special_requirements': [{'id': 'tag_group1'}],
                },
            ],
        },
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = set(d['uuid'] for d in json['candidates'])

    if ignore_thermobag_requirement:
        assert candidates == {'uuid0'}
    else:
        assert not candidates
