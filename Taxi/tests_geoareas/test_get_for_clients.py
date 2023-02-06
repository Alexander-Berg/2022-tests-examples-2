import pytest

from tests_geoareas import common


@pytest.mark.config(GEOAREAS_SERVICE_ENABLED=False)
@pytest.mark.parametrize(
    'collection_endpoint',
    [
        '/geoareas/v1/tariff-areas',
        '/subvention-geoareas/v1/geoareas',
        '/typed-geoareas/v1/fetch_geoareas',
    ],
)
async def test_get_for_clients_service_check(
        taxi_geoareas, collection_endpoint,
):
    if collection_endpoint == '/typed-geoareas/v1/fetch_geoareas':
        res = await taxi_geoareas.post(
            collection_endpoint,
            {'geoareas_types': ['logistic_dispatch_attractor']},
        )
    else:
        res = await taxi_geoareas.get(collection_endpoint)

    assert res.status_code == 500
    assert res.json()['code'] == 'service_disabled'


@pytest.mark.parametrize(
    'collection_endpoint',
    [
        '/geoareas/v1/tariff-areas',
        '/subvention-geoareas/v1/geoareas',
        '/typed-geoareas/v1/fetch_geoareas',
    ],
)
async def test_get_for_clients_bad_request(taxi_geoareas, collection_endpoint):
    if collection_endpoint == '/typed-geoareas/v1/fetch_geoareas':
        res = await taxi_geoareas.post(
            collection_endpoint,
            {
                'updated_after': 'not_datetime',
                'geoareas_types': ['logistic_dispatch_attractor'],
            },
        )
    else:
        res = await taxi_geoareas.get(
            collection_endpoint, params={'updated_after': 'not_datetime'},
        )

    assert res.status_code == 400
    data = res.json()
    assert data['code'] == '400'


@pytest.mark.filldb(geoareas='spb_msk2')
@pytest.mark.filldb(subvention_geoareas='spb_msk2')
@pytest.mark.filldb(typed_geoareas='spb_msk2')
@pytest.mark.parametrize(
    ['updated_after', 'expected_area_ids', 'expected_removed_names'],
    [
        (None, ['<spb>', '<msk2>', '<removed_in_future>'], []),
        (
            '2020-02-02T02:00:00.000000Z',
            ['<spb>', '<msk2>', '<removed_in_future>'],
            ['removed_with_ts'],
        ),
        ('2020-02-02T02:03:02.000000Z', ['<msk2>'], []),
        ('2020-02-02T03:02:02.000000Z', [], []),
        ('2030-01-01T00:00:00.000000Z', [], []),
    ],
)
@pytest.mark.parametrize(
    'collection_endpoint, collection_name',
    [
        ('/geoareas/v1/tariff-areas', 'geoareas'),
        ('/subvention-geoareas/v1/geoareas', 'subvention_geoareas'),
        ('/typed-geoareas/v1/fetch_geoareas', 'typed_geoareas'),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': [],
        'fetchable_geoareas_types': ['logistic_dispatch_attractor'],
    },
)
async def test_get_for_clients(
        taxi_geoareas,
        load_json,
        updated_after,
        expected_area_ids,
        expected_removed_names,
        collection_endpoint,
        collection_name,
):
    if collection_endpoint == '/typed-geoareas/v1/fetch_geoareas':
        res = await taxi_geoareas.post(
            collection_endpoint,
            {
                'updated_after': updated_after,
                'geoareas_types': ['logistic_dispatch_attractor'],
            }
            if updated_after is not None
            else {'geoareas_types': ['logistic_dispatch_attractor']},
        )
    else:
        res = await taxi_geoareas.get(
            collection_endpoint,
            params={'updated_after': updated_after}
            if updated_after is not None
            else {},
        )
    expected = list(
        filter(
            lambda x: x['id'] in expected_area_ids,
            load_json(f'{collection_name}_response_spb_msk2.json'),
        ),
    )
    assert res.status_code == 200
    common.check_get_response(res, expected, locale='ignore', many=True)

    response = res.json()
    if collection_endpoint == '/typed-geoareas/v1/fetch_geoareas':
        assert 'removed' in response
        got_removed = response['removed']
        assert got_removed == [
            {'name': name, 'type': 'logistic_dispatch_attractor'}
            for name in expected_removed_names
        ]
    else:
        assert 'removed_names' in response
        got_removed_names = response['removed_names']
        assert got_removed_names == expected_removed_names


@pytest.mark.config(SUBVENTION_GEOAREAS_USE_CACHE_FOR_FULL_UPDATE=True)
@pytest.mark.parametrize(
    ['collection_endpoint', 'collection_name'],
    [
        pytest.param(
            '/geoareas/v1/tariff-areas',
            'geoareas',
            marks=[pytest.mark.filldb(geoareas='spb_msk2')],
        ),
        pytest.param(
            '/subvention-geoareas/v1/geoareas',
            'subvention_geoareas',
            marks=[pytest.mark.filldb(subvention_geoareas='spb_msk2')],
        ),
    ],
)
async def test_get_for_clients_full_update_cache(
        taxi_geoareas,
        load_json,
        mongodb,
        collection_endpoint,
        collection_name,
):
    # otherwise caches are invalidated on endpoint call
    await taxi_geoareas.invalidate_caches()
    getattr(mongodb, collection_name).remove()

    expected = load_json(f'{collection_name}_response_spb_msk2.json')
    res = await taxi_geoareas.get(collection_endpoint)
    assert res.status_code == 200
    common.check_get_response(res, expected, locale='ignore', many=True)


@pytest.mark.filldb(typed_geoareas='spb_msk2')
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': [],
        'fetchable_geoareas_types': ['unknown_geoarea_type'],
    },
)
async def test_get_for_clients_no_fetchable(taxi_geoareas):
    res = await taxi_geoareas.post(
        '/typed-geoareas/v1/fetch_geoareas',
        {'geoareas_types': ['logistic_dispatch_attractor']},
    )
    expected = []
    assert res.status_code == 200
    common.check_get_response(res, expected, locale='ignore', many=True)

    response = res.json()
    assert 'removed' in response
    got_removed = response['removed']
    assert got_removed == []
