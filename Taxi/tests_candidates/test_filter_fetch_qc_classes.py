import pytest


async def _check(
        taxi_candidates,
        driver_positions,
        driver,
        zone_id,
        allowed_classes,
        assert_classes,
):
    await driver_positions([{'dbid_uuid': driver, 'position': [55, 35]}])

    request_body = {
        'geoindex': 'kdtree',
        'limit': 2,
        'filters': ['partners/fetch_qc_classes'],
        'point': [55, 35],
        'zone_id': zone_id,
        'allowed_classes': allowed_classes,
    }
    response = await taxi_candidates.post('searchable', json=request_body)
    assert response.status_code == 200
    drivers = response.json().get('drivers')
    assert len(drivers) == 1
    assert set(drivers[0]['classes']) == assert_classes


@pytest.mark.config(
    QC_CANDIDATES_EXAMS=['dkk'],
    TAXIMETER_QC_DRIVERS=dict(
        __default__=dict(block=['uuid0'], disable=[], visible=[]),
    ),
    QC_CANDIDATES_CLASSES_FILTER_SETTINGS=dict(
        countries=[
            dict(
                names=['rus'],
                rules=dict(
                    dkk=dict(
                        dkk_econom_off=dict(
                            classes=['econom'], is_allowing=False,
                        ),
                    ),
                ),
            ),
        ],
        zones=[
            dict(
                names=['moscow'],
                rules=dict(
                    dkk=dict(
                        dkk_econom_off=dict(
                            classes=['uberx'], is_allowing=True,
                        ),
                    ),
                ),
            ),
        ],
        __default__=dict(),
    ),
)
@pytest.mark.parametrize(
    'driver, zone_id, assert_classes',
    [
        ('dbid0_uuid0', 'moscow', {'uberx'}),
        ('dbid0_uuid0', 'spb', {'uberx', 'minivan'}),
        ('dbid0_uuid0', 'riga', {'uberx', 'econom', 'minivan'}),
    ],
)
async def test_fetch_qc_classes_car_and_driver(
        taxi_candidates, driver_positions, driver, zone_id, assert_classes,
):
    await _check(
        taxi_candidates,
        driver_positions,
        driver,
        zone_id,
        ['econom', 'minivan', 'uberx'],
        assert_classes,
    )


@pytest.mark.config(
    QC_CANDIDATES_CLASSES_FILTER_SETTINGS=dict(
        countries=[
            dict(
                names=['rus'],
                rules=dict(
                    offline_inspection=dict(
                        offline_inspection_default_off=dict(
                            classes=['minivan'], is_allowing=False,
                        ),
                    ),
                ),
            ),
        ],
        zones=[
            dict(
                names=['moscow'],
                rules=dict(
                    offline_inspection=dict(
                        offline_inspection_default_off=dict(
                            classes=['uberx', 'minivan'], is_allowing=False,
                        ),
                    ),
                ),
            ),
        ],
        __default__=dict(),
    ),
)
@pytest.mark.parametrize(
    'driver, zone_id, allowed_classes, assert_classes',
    [
        # no entity in qc, default sanctions for russia
        (
            'dbid0_uuid0',
            'spb',
            ['uberx', 'econom', 'minivan'],
            {'econom', 'uberx'},
        ),
        # no entity in qc, default sanctions for moscow
        ('dbid0_uuid0', 'moscow', ['uberx', 'econom', 'minivan'], {'econom'}),
        # no sanctions by __default__
        (
            'dbid0_uuid0',
            'riga',
            ['uberx', 'econom', 'minivan'],
            {'uberx', 'econom', 'minivan'},
        ),
    ],
)
async def test_fetch_qc_classes_vehicle_default(
        taxi_candidates,
        driver_positions,
        driver,
        zone_id,
        allowed_classes,
        assert_classes,
):
    await _check(
        taxi_candidates,
        driver_positions,
        driver,
        zone_id,
        allowed_classes,
        assert_classes,
    )


@pytest.mark.config(
    QC_CANDIDATES_CLASSES_FILTER_SETTINGS=dict(
        countries=[
            dict(
                names=['rus'],
                rules=dict(
                    offline_inspection=dict(
                        offline_inspection_uberx_off=dict(
                            classes=['uberx'], is_allowing=False,
                        ),
                    ),
                ),
            ),
        ],
        zones=[
            dict(
                names=['moscow'],
                rules=dict(
                    offline_inspection=dict(
                        offline_inspection_uberx_off=dict(
                            classes=['uberx'], is_allowing=False,
                        ),
                        offline_inspection_minivan_off=dict(
                            classes=['minivan'], is_allowing=False,
                        ),
                    ),
                ),
            ),
        ],
        __default__=dict(
            offline_inspection=dict(
                offline_inspection_uberx_off=dict(
                    classes=['minivan'], is_allowing=True,
                ),
            ),
        ),
    ),
)
@pytest.mark.parametrize(
    'driver, zone_id, allowed_classes, assert_classes',
    [
        # default sanctions for russia
        (
            'dbid0_uuid0',
            'spb',
            ['uberx', 'econom', 'minivan'],
            {'econom', 'minivan'},
        ),
        # default sanctions for moscow
        ('dbid0_uuid0', 'moscow', ['uberx', 'econom', 'minivan'], {'econom'}),
        # sanctions by __default__
        ('dbid0_uuid0', 'riga', ['minivan'], {'minivan'}),
    ],
)
async def test_fetch_qc_classes_vehicle(
        taxi_candidates,
        driver_positions,
        driver,
        zone_id,
        allowed_classes,
        assert_classes,
):
    await _check(
        taxi_candidates,
        driver_positions,
        driver,
        zone_id,
        allowed_classes,
        assert_classes,
    )
