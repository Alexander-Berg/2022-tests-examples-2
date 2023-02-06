import pytest


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


@pytest.mark.config(
    TAXIMETER_QC_COUNTRIES=dict(
        __default__=dict(block=['rus'], disable=[], visible=[]),
    ),
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


@pytest.mark.config(
    TAXIMETER_QC_CITIES=dict(
        __default__=dict(block=['Москва'], disable=[], visible=[]),
    ),
)
async def test_if_blocked_by_city(taxi_candidates, driver_positions):
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


@pytest.mark.config(
    TAXIMETER_QC_PARKS=dict(
        __default__=dict(block=['dbid0'], disable=[], visible=[]),
    ),
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


@pytest.mark.config(
    TAXIMETER_QC_DRIVERS=dict(
        __default__=dict(block=['uuid0'], disable=[], visible=[]),
    ),
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


@pytest.mark.config(
    QC_CHECK_TAGS_ENABLED=True,
    TAXIMETER_QC_TAGS=dict(
        __default__=dict(block=['qc_block'], disable=[], visible=[]),
    ),
    TAGS_INDEX=dict(enabled=True),
)
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


@pytest.mark.config(
    TAXIMETER_QC_COUNTRIES=dict(
        __default__=dict(block=['rus'], disable=[], visible=[]),
        sts=dict(block=[], disable=[], visible=[]),
    ),
)
async def test_if_free_by_specialization(taxi_candidates, driver_positions):
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


@pytest.mark.config(
    TAXIMETER_QC_COUNTRIES=dict(
        __default__=dict(block=['rus'], disable=[], visible=[]),
    ),
    TAXIMETER_QC_CITIES=dict(
        __default__=dict(block=[], disable=[], visible=['Москва']),
    ),
)
async def test_if_free_by_city(taxi_candidates, driver_positions):
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


@pytest.mark.config(
    TAXIMETER_QC_CITIES=dict(
        __default__=dict(block=['Москва'], disable=[], visible=[]),
    ),
    TAXIMETER_QC_PARKS=dict(
        __default__=dict(block=[], disable=['dbid0'], visible=[]),
    ),
)
async def test_if_free_by_park(taxi_candidates, driver_positions):
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


@pytest.mark.config(
    TAXIMETER_QC_PARKS=dict(
        __default__=dict(block=['dbid0'], disable=[], visible=[]),
    ),
    TAXIMETER_QC_DRIVERS=dict(
        __default__=dict(block=[], disable=[], visible=['uuid0']),
    ),
)
async def test_if_free_by_driver(taxi_candidates, driver_positions):
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


@pytest.mark.config(
    TAXIMETER_QC_DRIVERS=dict(
        __default__=dict(block=['uuid0'], disable=[], visible=[]),
    ),
    QC_CHECK_TAGS_ENABLED=True,
    TAXIMETER_QC_TAGS=dict(
        __default__=dict(block=[], disable=['qc_skip'], visible=[]),
    ),
    TAGS_INDEX=dict(enabled=True),
)
@pytest.mark.tags_v2_index(tags_list=[('dbid_uuid', 'dbid0_uuid0', 'qc_skip')])
async def test_if_free_by_tags(taxi_candidates, driver_positions):
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


@pytest.mark.config(
    TAXIMETER_QC_COUNTRIES=dict(
        __default__=dict(block=['rus'], disable=[], visible=[]),
    ),
    QC_CANDIDATES_BLOCK_SKIP_EXAMS=['sts'],
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
    assert len(response.json()['drivers']) == 1
