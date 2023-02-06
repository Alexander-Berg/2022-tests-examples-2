import pytest


@pytest.fixture(autouse=True)
def eats_shifts_journal(mockserver):
    @mockserver.json_handler(
        '/eats-performer-shifts/internal/eats-performer-shifts/v1/courier-shift-states/updates',  # noqa: E501
    )
    def _eats_shifts_journal(request):
        if not request.args['cursor']:
            return {
                'data': {
                    'shifts': [
                        {
                            'courier_id': 'dbid0_uuid3',
                            'eats_courier_id': '10',
                            'shift_id': '19950',
                            'zone_id': '6341',
                            'zone_group_id': None,
                            'meta_group_id': None,
                            'status': 'closed',
                            'started_at': '2020-07-28T08:47:00Z',
                            'closes_at': '2020-07-28T09:07:12Z',
                            'paused_at': None,
                            'unpauses_at': None,
                            'updated_ts': '2020-07-28T09:07:12Z',
                            'is_high_priority': False,
                        },
                        {
                            'courier_id': 'dbid0_uuid4',
                            'eats_courier_id': '11',
                            'shift_id': '19950',
                            'zone_id': '6341',
                            'zone_group_id': None,
                            'meta_group_id': '67890',
                            'status': 'in_progress',
                            'started_at': '2020-07-28T08:47:00Z',
                            'closes_at': '2020-07-28T09:07:12Z',
                            'paused_at': None,
                            'unpauses_at': None,
                            'updated_ts': '2020-07-28T09:07:12Z',
                            'is_high_priority': True,
                        },
                    ],
                    'cursor': '1',
                },
            }
        return {'data': {'shifts': [], 'cursor': '1'}}


@pytest.mark.config(
    EXTRA_EXAMS_BY_ZONE={},
    TAGS_INDEX={
        'enabled': True,
        'request_interval': 100,
        'request_size': 8192,
    },
    ROUTER_SELECT=[{'ids': ['moscow'], 'routers': ['linear-fallback']}],
)
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid2', 'scooters_energizer'),
        ('dbid_uuid', 'dbid0_uuid3', 'scooters_energizer'),
        ('dbid_uuid', 'dbid0_uuid4', 'scooters_energizer'),
        ('dbid_uuid', 'dbid0_uuid5', 'scooters_relocator'),
    ],
)
@pytest.mark.parametrize(
    'operators_type, expected_candidates',
    [
        # - dbid0_uuid0, dbid0_uuid1 will be filtered because they don't have operator tag
        # - dbid0_uuid3 will be filtered because his shift is closed
        # - dbid0_uuid5 will be filtered because he's relocator
        ('energizers', ['dbid0_uuid2', 'dbid0_uuid4']),
        # - dbid0_uuid0, dbid0_uuid1 will be filtered because they don't have operator tag
        # - dbid0_uuid2, dbid0_uuid3, dbid0_uuid4 will be filtered because they're energizers
        ('relocators', ['dbid0_uuid5']),
    ],
)
async def test_filter_scooters_operators(
        taxi_candidates,
        driver_positions,
        experiments3,
        operators_type,
        expected_candidates,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [35, 55]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [35, 55]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [35, 55]},
            {'dbid_uuid': 'dbid0_uuid3', 'position': [35, 55]},
            {'dbid_uuid': 'dbid0_uuid4', 'position': [35, 55]},
            {'dbid_uuid': 'dbid0_uuid5', 'position': [35, 55]},
        ],
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='scooters_operators_taximeter_version',
        consumers=['candidates/filters'],
        clauses=[],
        default_value={'enabled': True},
    )

    request_body = {
        'point': [35, 55],
        'zone_id': 'moscow',
        'allowed_classes': ['scooters'],
        'max_distance': 10000,
        'order': {'request': {'scooters': {'operators_type': operators_type}}},
    }

    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200
    assert 'candidates' in response.json()
    candidates = [
        candidate['id'] for candidate in response.json()['candidates']
    ]
    assert sorted(candidates) == sorted(expected_candidates)


@pytest.mark.config(
    EXTRA_EXAMS_BY_ZONE={},
    TAGS_INDEX={
        'enabled': True,
        'request_interval': 100,
        'request_size': 8192,
    },
    ROUTER_SELECT=[{'ids': ['moscow'], 'routers': ['linear-fallback']}],
)
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid2', 'scooters_energizer'),
        ('dbid_uuid', 'dbid0_uuid4', 'scooters_relocator'),
    ],
)
@pytest.mark.parametrize(
    'operators_type, version_for_energizers, version_for_relocators, application, expected_candidates',
    [
        ('energizers', '8.0.0', '8.0.0', 'taximeter', ['dbid0_uuid2']),
        ('energizers', '9.0.0', '8.0.0', 'taximeter', []),
        ('energizers', '8.0.0', '8.0.0', 'taximeter-ios', []),
        ('relocators', '8.0.0', '8.0.0', 'taximeter', ['dbid0_uuid4']),
        ('relocators', '8.0.0', '9.0.0', 'taximeter', []),
        ('relocators', '8.0.0', '8.0.0', 'taximeter-ios', []),
    ],
)
async def test_filter_scooters_operators_taximeter_version(
        taxi_candidates,
        driver_positions,
        operators_type,
        application,
        version_for_energizers,
        version_for_relocators,
        expected_candidates,
        experiments3,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid2', 'position': [35, 55]},
            {'dbid_uuid': 'dbid0_uuid4', 'position': [35, 55]},
        ],
    )

    experiments3.add_config(
        match={
            'consumers': [{'name': 'candidates/filters'}],
            'enabled': True,
            'predicate': {'init': {}, 'type': 'true'},
        },
        name='scooters_operators_taximeter_version',
        consumers=['candidates/filters'],
        clauses=[
            {
                'enabled': True,
                'extension_method': 'replace',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'tags',
                                    'set_elem_type': 'string',
                                    'value': 'scooters_energizer',
                                },
                                'type': 'contains',
                            },
                            {
                                'init': {
                                    'arg_name': 'version',
                                    'arg_type': 'version',
                                    'value': version_for_energizers,
                                },
                                'type': 'gte',
                            },
                            {
                                'init': {
                                    'arg_name': 'application',
                                    'arg_type': 'string',
                                    'value': application,
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'title': 'energizers',
                'value': {'enabled': True},
            },
            {
                'enabled': True,
                'extension_method': 'replace',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'tags',
                                    'set_elem_type': 'string',
                                    'value': 'scooters_relocator',
                                },
                                'type': 'contains',
                            },
                            {
                                'init': {
                                    'arg_name': 'version',
                                    'arg_type': 'version',
                                    'value': version_for_relocators,
                                },
                                'type': 'gte',
                            },
                            {
                                'init': {
                                    'arg_name': 'application',
                                    'arg_type': 'string',
                                    'value': application,
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'title': 'relocators',
                'value': {'enabled': True},
            },
        ],
        default_value={'enabled': False},
    )

    request_body = {
        'point': [35, 55],
        'zone_id': 'moscow',
        'allowed_classes': ['scooters'],
        'max_distance': 10000,
        'order': {'request': {'scooters': {'operators_type': operators_type}}},
    }

    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200
    assert 'candidates' in response.json()
    candidates = [
        candidate['id'] for candidate in response.json()['candidates']
    ]
    assert sorted(candidates) == sorted(expected_candidates)
