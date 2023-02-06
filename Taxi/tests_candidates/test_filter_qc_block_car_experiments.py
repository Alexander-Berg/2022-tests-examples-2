import pytest


@pytest.mark.config(
    TAXIMETER_QC_COUNTRIES=dict(
        __default__=dict(block=[], disable=[], visible=[]),
    ),
)
async def test_if_free_by_default(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/qc_block'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    assert len(response.json()['drivers']) == 2


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='qc_exam_enable_sts',
    consumers=['candidates/filters'],
    clauses=[
        {
            'title': '1',
            'predicate': {
                'init': {
                    'arg_name': 'country',
                    'set': ['rus'],
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {'mode': 'block'},
        },
    ],
    default_value={'mode': 'visible'},
    is_config=True,
)
async def test_if_blocked_by_country(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/qc_block'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    # lightbox_off is not blocking sanction
    assert len(response.json()['drivers']) == 1


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='qc_exam_enable_sts',
    consumers=['candidates/filters'],
    clauses=[
        {
            'title': '1',
            'predicate': {
                'init': {
                    'arg_name': 'driver_dbid',
                    'set': ['dbid0'],
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {'mode': 'block'},
        },
    ],
    default_value={'mode': 'visible'},
    is_config=True,
)
async def test_if_blocked_by_park(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/qc_block'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert response.json() == dict(drivers=[])


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='qc_exam_enable_sts',
    consumers=['candidates/filters'],
    clauses=[
        {
            'title': '1',
            'predicate': {
                'init': {
                    'arg_name': 'driver_uuid',
                    'set': ['uuid0'],
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {'mode': 'block'},
        },
    ],
    default_value={'mode': 'visible'},
    is_config=True,
)
async def test_if_blocked_by_driver(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/qc_block'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert response.json() == dict(drivers=[])


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='qc_exam_enable_sts',
    consumers=['candidates/filters'],
    clauses=[
        {
            'title': '1',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'type': 'contains',
                            'init': {
                                'arg_name': 'tags',
                                'set_elem_type': 'string',
                                'value': 'qc_block',
                            },
                        },
                    ],
                },
                'type': 'any_of',
            },
            'value': {'mode': 'block'},
        },
    ],
    default_value={'mode': 'disable'},
    is_config=True,
)
@pytest.mark.config(TAGS_INDEX=dict(enabled=True))
@pytest.mark.tags_v2_index(
    tags_list=[('dbid_uuid', 'dbid0_uuid0', 'qc_block')],
)
async def test_if_blocked_by_tags(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/qc_block'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert response.json() == dict(drivers=[])


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='qc_exam_enable_sts',
    consumers=['candidates/filters'],
    clauses=[],
    default_value={'mode': 'disable'},
    is_config=True,
)
async def test_if_free_by_default_clause(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/qc_block'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    assert len(response.json()['drivers']) == 1


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='qc_exam_enable_sts',
    consumers=['candidates/filters'],
    clauses=[],
    default_value={'mode': 'block'},
    is_config=True,
)
@pytest.mark.config(QC_CANDIDATES_BLOCK_SKIP_EXAMS=['sts'])
@pytest.mark.config(
    TAXIMETER_QC_COUNTRIES=dict(
        __default__=dict(block=['rus'], disable=[], visible=[]),
    ),
)
async def test_qc_block_skip_exams(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/qc_block'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    # neither config3.0, nor config2.0 does not block
    # driver, because exam was in ignore list
    assert len(response.json()['drivers']) == 1


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='qc_exam_enable_sts',
    consumers=['candidates/filters'],
    clauses=[],
    default_value={'mode': 'block'},
    is_config=True,
)
@pytest.mark.config(QC_CANDIDATES_EXAMS=[])
@pytest.mark.config(
    TAXIMETER_QC_COUNTRIES=dict(
        __default__=dict(block=['rus'], disable=[], visible=[]),
    ),
)
async def test_qc_block_empty_exam_list(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/qc_block'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    # neither config3.0, nor config2.0 does not block
    # driver, because enabled exams list is empty
    assert len(response.json()['drivers']) == 1


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='qc_exam_enable_sts',
    consumers=['candidates/filters'],
    clauses=[],
    default_value={'mode': 'block'},
    is_config=True,
)
async def test_qc_block_experiments_usage(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/qc_block'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    # used config3.0, because config2.0
    # contains 'rus' as visible exam
    assert not response.json()['drivers']


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='qc_exam_enable_sts',
    consumers=['candidates/filters'],
    clauses=[],
    default_value={'mode': 'disable'},
    is_config=True,
)
@pytest.mark.config(QC_CHECK_CONFIG_3_0_ENABLE=False)
async def test_qc_block_disabling_exp_flag(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/qc_block'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    # config3.0 was not used, because
    # QC_CHECK_CONFIG_3_0_ENABLE is False
    assert len(response.json()['drivers']) == 1
