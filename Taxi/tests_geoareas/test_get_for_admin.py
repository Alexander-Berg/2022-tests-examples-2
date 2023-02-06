import datetime

import pytest

from tests_geoareas import common


DEFAULT_EDITABLE_TYPES = {
    'editable_geoareas_types': ['logistic_dispatch_attractor'],
    'fetchable_geoareas_types': [],
}

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.translations(geoareas=common.GEOAREAS_KEYSET),
    pytest.mark.translations(subvention_geoareas=common.GEOAREAS_KEYSET),
    pytest.mark.translations(
        typed_geoareas={
            f'logistic_dispatch_attractor__{k}': v
            for k, v in common.GEOAREAS_KEYSET.items()
        },
    ),
    pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en']),
]


def assert_sorted(lhs, rhs, sort_key):
    assert sorted(lhs, key=lambda x: x[sort_key]) == sorted(
        rhs, key=lambda x: x[sort_key],
    )


# pylint: disable=W0102
async def call_get_endpoint(
        taxi_geoareas, endpoint, locale='ru', bulk_names=[], prefix=None,
):
    if endpoint == '/subvention-geoareas/admin/v1/geoareas_names':
        if prefix:
            res = await taxi_geoareas.get(
                endpoint,
                params={'prefix': prefix},
                headers={'accept-language': locale},
            )
        else:
            res = await taxi_geoareas.get(
                endpoint, headers={'accept-language': locale},
            )
    elif endpoint == '/typed-geoareas/admin/v1/geoareas_names':
        res = await taxi_geoareas.get(
            endpoint,
            params={'geoarea_type': 'logistic_dispatch_attractor'},
            headers={'accept-language': locale},
        )
    elif endpoint == '/subvention-geoareas/admin/v1/geoareas' and bulk_names:
        res = await taxi_geoareas.post(
            endpoint, {'names': bulk_names, 'locale': locale},
        )
    else:
        res = await taxi_geoareas.get(endpoint, params={'locale': locale})
    return res


@pytest.mark.filldb(typed_geoareas='spb_spb_msk2_msk3')
@pytest.mark.parametrize(
    ['updated_after', 'expected_area_ids', 'expected_removed_names'],
    [
        (None, ['<spb>', '<msk2>', '<spb_2>', '<msk2_2>'], []),
        (
            '2020-02-02T02:00:00.000000Z',
            ['<spb>', '<msk2>', '<spb_2>', '<msk2_2>'],
            ['removed_with_ts'],
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': [],
        'fetchable_geoareas_types': [
            'logistic_dispatch_attractor_1',
            'logistic_dispatch_attractor_2',
        ],
    },
)
async def test_fetch_typed_geoareas_with_different_types_same_names(
        taxi_geoareas,
        load_json,
        updated_after,
        expected_area_ids,
        expected_removed_names,
):
    params = {
        'geoareas_types': [
            'logistic_dispatch_attractor_1',
            'logistic_dispatch_attractor_2',
        ],
    }
    if updated_after is not None:
        params['updated_after'] = updated_after
    res = await taxi_geoareas.post('/typed-geoareas/v1/fetch_geoareas', params)
    expected = list(
        filter(
            lambda x: x['id'] in expected_area_ids,
            load_json('typed_geoareas_response_spb_spb_msk2_msk3.json'),
        ),
    )
    assert res.status_code == 200
    common.check_get_response(res, expected, locale='ignore', many=True)

    response = res.json()
    assert 'removed' in response
    got_removed = response['removed']
    expected_removed = []
    for name in expected_removed_names:
        expected_removed.append(
            {'name': name, 'type': 'logistic_dispatch_attractor_1'},
        )
        expected_removed.append(
            {'name': name, 'type': 'logistic_dispatch_attractor_2'},
        )
    got_removed.sort(key=lambda x: (x.get('type', ''), x['name']))
    expected_removed.sort(key=lambda x: (x.get('type', ''), x['name']))
    assert got_removed == expected_removed


@pytest.mark.parametrize(
    'collection_endpoint',
    [
        '/geoareas/admin/v1/tariff-areas',
        '/subvention-geoareas/admin/v1/geoareas',
        '/subvention-geoareas/admin/v1/geoareas_names',
        '/subvention-geoareas/admin/v1/geoareas',
        '/typed-geoareas/admin/v1/geoareas',
        '/typed-geoareas/admin/v1/geoareas_names',
    ],
)
@pytest.mark.config(GEOAREAS_SERVICE_ENABLED=False)
async def test_get_for_admin_service_check(taxi_geoareas, collection_endpoint):
    res = await call_get_endpoint(taxi_geoareas, collection_endpoint)

    assert res.status_code == 500
    assert res.json()['code'] == 'service_disabled'


@pytest.mark.parametrize(
    'collection_endpoint',
    [
        '/geoareas/admin/v1/tariff-areas',
        '/subvention-geoareas/admin/v1/geoareas',
        '/typed-geoareas/admin/v1/geoareas',
    ],
)
async def test_get_for_admin_bad_request(taxi_geoareas, collection_endpoint):
    res = await taxi_geoareas.get(
        collection_endpoint, params={'id': '1', 'name': '2'},
    )

    assert res.status_code == 400
    data = res.json()
    assert data['code'] == '400'
    assert 'same time' in data['message']


@pytest.mark.filldb(geoareas='spb_msk2')
@pytest.mark.filldb(subvention_geoareas='spb_msk2')
@pytest.mark.filldb(typed_geoareas='spb_msk2')
@pytest.mark.parametrize('locale', [None, 'ru', 'en'])
@pytest.mark.parametrize(
    'collection_endpoint, collection_name, only_names',
    [
        ('/geoareas/admin/v1/tariff-areas', 'geoareas', False),
        (
            '/subvention-geoareas/admin/v1/geoareas',
            'subvention_geoareas',
            False,
        ),
        (
            '/subvention-geoareas/admin/v1/geoareas_names',
            'subvention_geoareas',
            True,
        ),
        ('/typed-geoareas/admin/v1/geoareas', 'typed_geoareas', False),
        ('/typed-geoareas/admin/v1/geoareas_names', 'typed_geoareas', True),
    ],
)
@pytest.mark.config(TYPED_GEOAREAS_SETTINGS=DEFAULT_EDITABLE_TYPES)
async def test_get_for_admin_all(
        taxi_geoareas,
        load_json,
        locale,
        collection_endpoint,
        collection_name,
        only_names,
):
    res = await call_get_endpoint(taxi_geoareas, collection_endpoint, locale)
    expected = load_json(f'{collection_name}_response_spb_msk2.json')
    common.check_get_response(
        res, expected, locale, many=True, only_names=only_names,
    )


@pytest.mark.filldb(geoareas='msk1')
@pytest.mark.filldb(subvention_geoareas='msk1')
@pytest.mark.filldb(typed_geoareas='msk1')
@pytest.mark.config(TYPED_GEOAREAS_SETTINGS=DEFAULT_EDITABLE_TYPES)
@pytest.mark.parametrize(
    'missing_field', ['name', 'area', 'created', 'geometry'],
)
@pytest.mark.parametrize(
    'collection_endpoint, collection_name, only_names',
    [
        ('/geoareas/admin/v1/tariff-areas', 'geoareas', False),
        (
            '/subvention-geoareas/admin/v1/geoareas',
            'subvention_geoareas',
            False,
        ),
        (
            '/subvention-geoareas/admin/v1/geoareas_names',
            'subvention_geoareas',
            True,
        ),
        ('/typed-geoareas/admin/v1/geoareas', 'typed_geoareas', False),
        ('/typed-geoareas/admin/v1/geoareas_names', 'typed_geoareas', True),
    ],
)
async def test_get_for_admin_all_missing_field(
        taxi_geoareas,
        mongodb,
        missing_field,
        collection_endpoint,
        collection_name,
        only_names,
):
    getattr(mongodb, collection_name).update(
        {}, {'$unset': {missing_field: 1}},
    )

    res = await call_get_endpoint(taxi_geoareas, collection_endpoint)
    expected = []
    common.check_get_response(
        res, expected, locale='ignore', many=True, only_names=only_names,
    )


@pytest.mark.filldb(geoareas='msk1')
@pytest.mark.filldb(subvention_geoareas='msk1')
@pytest.mark.filldb(typed_geoareas='msk1')
@pytest.mark.config(TYPED_GEOAREAS_SETTINGS=DEFAULT_EDITABLE_TYPES)
@pytest.mark.parametrize(
    'collection_endpoint, collection_name, only_names',
    [
        ('/geoareas/admin/v1/tariff-areas', 'geoareas', False),
        (
            '/subvention-geoareas/admin/v1/geoareas',
            'subvention_geoareas',
            False,
        ),
        (
            '/subvention-geoareas/admin/v1/geoareas_names',
            'subvention_geoareas',
            True,
        ),
        ('/typed-geoareas/admin/v1/geoareas', 'typed_geoareas', False),
        ('/typed-geoareas/admin/v1/geoareas_names', 'typed_geoareas', True),
    ],
)
async def test_get_for_admin_all_bad_geometry(
        taxi_geoareas,
        load_json,
        mongodb,
        collection_endpoint,
        collection_name,
        only_names,
):
    bad_geometry = load_json('bad_geometry.json')
    for i, geometry in enumerate(bad_geometry):
        getattr(mongodb, collection_name).update(
            {},
            {'$set': {'geometry': geometry, 'name': 'testcase #' + str(i)}},
        )

        res = await call_get_endpoint(taxi_geoareas, collection_endpoint)
        expected = []
        common.check_get_response(
            res, expected, locale='ignore', many=True, only_names=only_names,
        )


@pytest.mark.filldb(geoareas='fixable_geometry')
@pytest.mark.filldb(subvention_geoareas='fixable_geometry')
@pytest.mark.filldb(typed_geoareas='fixable_geometry')
@pytest.mark.config(TYPED_GEOAREAS_SETTINGS=DEFAULT_EDITABLE_TYPES)
@pytest.mark.parametrize(
    'collection_endpoint, collection_name, only_names',
    [
        ('/geoareas/admin/v1/tariff-areas', 'geoareas', False),
        (
            '/subvention-geoareas/admin/v1/geoareas',
            'subvention_geoareas',
            False,
        ),
        (
            '/subvention-geoareas/admin/v1/geoareas_names',
            'subvention_geoareas',
            True,
        ),
        ('/typed-geoareas/admin/v1/geoareas', 'typed_geoareas', False),
        ('/typed-geoareas/admin/v1/geoareas_names', 'typed_geoareas', True),
    ],
)
async def test_get_for_admin_all_fix_geometry(
        taxi_geoareas,
        load_json,
        collection_endpoint,
        collection_name,
        only_names,
):
    res = await call_get_endpoint(taxi_geoareas, collection_endpoint)
    expected = load_json(f'{collection_name}_response_fixed_geometry.json')
    common.check_get_response(
        res, expected, locale='ignore', many=True, only_names=only_names,
    )


@pytest.mark.filldb(geoareas='fixable_geometry')
@pytest.mark.filldb(subvention_geoareas='fixable_geometry')
@pytest.mark.filldb(typed_geoareas='fixable_geometry')
@pytest.mark.config(
    GEOAREAS_ENABLE_RETURNED_GEOMETRY_VALIDATION=False,
    TYPED_GEOAREAS_SETTINGS=DEFAULT_EDITABLE_TYPES,
)
@pytest.mark.parametrize(
    'collection_endpoint, collection_name, only_names',
    [
        ('/geoareas/admin/v1/tariff-areas', 'geoareas', False),
        (
            '/subvention-geoareas/admin/v1/geoareas',
            'subvention_geoareas',
            False,
        ),
        (
            '/subvention-geoareas/admin/v1/geoareas_names',
            'subvention_geoareas',
            True,
        ),
        ('/typed-geoareas/admin/v1/geoareas', 'typed_geoareas', False),
        ('/typed-geoareas/admin/v1/geoareas_names', 'typed_geoareas', True),
    ],
)
async def test_get_for_admin_all_validate_geometry_disabled(
        taxi_geoareas,
        load_json,
        collection_endpoint,
        collection_name,
        only_names,
):
    res = await call_get_endpoint(taxi_geoareas, collection_endpoint)
    expected = load_json(f'{collection_name}_response_not_fixed_geometry.json')
    common.check_get_response(
        res, expected, locale='ignore', many=True, only_names=only_names,
    )


@pytest.mark.filldb(geoareas='spb_msk2')
@pytest.mark.filldb(subvention_geoareas='spb_msk2')
@pytest.mark.filldb(typed_geoareas='spb_msk2')
@pytest.mark.config(TYPED_GEOAREAS_SETTINGS=DEFAULT_EDITABLE_TYPES)
@pytest.mark.parametrize(
    'collection_endpoint, collection_name, only_names',
    [
        ('/geoareas/admin/v1/tariff-areas', 'geoareas', False),
        (
            '/subvention-geoareas/admin/v1/geoareas',
            'subvention_geoareas',
            False,
        ),
        (
            '/subvention-geoareas/admin/v1/geoareas_names',
            'subvention_geoareas',
            True,
        ),
        ('/typed-geoareas/admin/v1/geoareas', 'typed_geoareas', False),
        ('/typed-geoareas/admin/v1/geoareas_names', 'typed_geoareas', True),
    ],
)
async def test_get_for_admin_all_bad_geometry_type(
        taxi_geoareas,
        load_json,
        mongodb,
        collection_endpoint,
        collection_name,
        only_names,
):
    getattr(mongodb, collection_name).update(
        {}, {'$push': {'type': '<invalid>'}},
    )

    res = await call_get_endpoint(taxi_geoareas, collection_endpoint)
    expected = load_json(f'{collection_name}_response_spb_msk2.json')
    common.check_get_response(
        res, expected, locale='ignore', many=True, only_names=only_names,
    )


@pytest.mark.filldb(geoareas='spb_msk2')
@pytest.mark.parametrize('name', ['msk', 'spb', 'nonexistent', 'removed'])
async def test_get_for_admin_by_name(taxi_geoareas, load_json, name):
    res = await taxi_geoareas.get(
        '/geoareas/admin/v1/tariff-areas', params={'name': name},
    )
    expected = list(
        filter(
            lambda x: x['name'] == name,
            load_json('geoareas_response_spb_msk2.json'),
        ),
    )
    common.check_get_response(res, expected, locale='ignore')


@pytest.mark.filldb(subvention_geoareas='spb_msk2')
@pytest.mark.filldb(typed_geoareas='spb_msk2')
@pytest.mark.parametrize('name', ['msk', 'spb', 'nonexistent', 'removed'])
@pytest.mark.parametrize(
    'collection_endpoint, collection_name',
    [
        ('/subvention-geoareas/admin/v1/geoareas', 'subvention_geoareas'),
        ('/typed-geoareas/admin/v1/geoareas', 'typed_geoareas'),
    ],
)
@pytest.mark.config(TYPED_GEOAREAS_SETTINGS=DEFAULT_EDITABLE_TYPES)
async def test_sg_tg_get_for_admin_by_name(
        taxi_geoareas, load_json, name, collection_endpoint, collection_name,
):
    if collection_endpoint == '/typed-geoareas/admin/v1/geoareas':
        res = await taxi_geoareas.get(
            collection_endpoint,
            params={
                'geoarea_type': 'logistic_dispatch_attractor',
                'name': name,
            },
        )
    else:
        res = await taxi_geoareas.get(
            collection_endpoint, params={'name': name},
        )
    if name in ('msk', 'spb'):
        expected = list(
            filter(
                lambda x: x['name'] == name,
                load_json(f'{collection_name}_response_spb_msk2.json'),
            ),
        )
        common.check_get_response(res, expected, locale='ignore')
    else:
        assert res.status_code == 404
        got = res.json()
        assert got['code'] == 'NOT_FOUND'
        if collection_endpoint == '/typed-geoareas/admin/v1/geoareas':
            assert (
                got['message']
                == 'Could not find geoarea with geoarea_type: '
                + 'logistic_dispatch_attractor, name: '
                + name
            )
        else:
            assert (
                got['message'] == f'Could not find geoarea with name: {name}'
            )


@pytest.mark.filldb(typed_geoareas='types')
@pytest.mark.parametrize(
    'geoarea_type',
    [
        'logistic_dispatch_attractor_1',
        'logistic_dispatch_attractor_2',
        'logistic_dispatch_attractor_3',
        'logistic_dispatch_attractor_4',
        '',
        None,
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': [
            '',
            'logistic_dispatch_attractor_1',
            'logistic_dispatch_attractor_2',
            'logistic_dispatch_attractor_3',
        ],
        'fetchable_geoareas_types': [],
    },
)
async def test_tg_get_for_admin_by_type(
        taxi_geoareas, load_json, geoarea_type,
):
    params = dict()
    if geoarea_type is not None:
        params['geoarea_type'] = geoarea_type
    res = await taxi_geoareas.get(
        '/typed-geoareas/admin/v1/geoareas', params=params,
    )
    if geoarea_type in ['', 'logistic_dispatch_attractor_4']:
        assert res.status_code == 400
        got = res.json()
        assert got['code'] == 'unsupported_geoarea_type'
        assert (
            got['message']
            == f'no geoarea type [{geoarea_type}] '
            + 'in config TYPED_GEOAREAS_SETTINGS.editable_geoareas_types'
        )
    else:
        geoarea_types_filter = []
        if geoarea_type is not None:
            geoarea_types_filter = [geoarea_type]
        else:
            geoarea_types_filter = [
                'logistic_dispatch_attractor_1',
                'logistic_dispatch_attractor_2',
            ]
        expected = list(
            filter(
                lambda x: x['geoarea_type'] in geoarea_types_filter,
                load_json('typed_geoareas_response_types.json'),
            ),
        )
        common.check_get_response(res, expected, many=True, locale='ignore')


@pytest.mark.filldb(geoareas='msk1')
async def test_get_for_admin_by_name_malformed(taxi_geoareas, mongodb):
    mongodb.geoareas.update({}, {'$unset': {'area': 1}})

    res = await taxi_geoareas.get(
        '/geoareas/admin/v1/tariff-areas', params={'name': 'msk'},
    )
    expected = []
    common.check_get_response(res, expected, locale='ignore')


@pytest.mark.filldb(subvention_geoareas='msk1')
@pytest.mark.filldb(typed_geoareas='msk1')
@pytest.mark.parametrize(
    'collection_endpoint, collection_name',
    [
        ('/subvention-geoareas/admin/v1/geoareas', 'subvention_geoareas'),
        ('/typed-geoareas/admin/v1/geoareas', 'typed_geoareas'),
    ],
)
@pytest.mark.config(TYPED_GEOAREAS_SETTINGS=DEFAULT_EDITABLE_TYPES)
async def test_sg_tg_get_for_admin_by_name_malformed(
        taxi_geoareas, mongodb, collection_endpoint, collection_name,
):
    getattr(mongodb, collection_name).update({}, {'$unset': {'area': 1}})

    if collection_endpoint == '/typed-geoareas/admin/v1/geoareas':
        res = await taxi_geoareas.get(
            collection_endpoint,
            params={
                'geoarea_type': 'logistic_dispatch_attractor',
                'name': 'msk',
            },
        )
    else:
        res = await taxi_geoareas.get(
            collection_endpoint, params={'name': 'msk'},
        )

    assert res.status_code == 404
    got = res.json()
    assert got['code'] == 'NOT_FOUND'
    if collection_endpoint == '/typed-geoareas/admin/v1/geoareas':
        assert (
            got['message']
            == 'Could not find geoarea with geoarea_type: '
            + 'logistic_dispatch_attractor, name: msk'
        )
    else:
        assert got['message'] == 'Could not find geoarea with name: msk'


@pytest.mark.filldb(typed_geoareas='msk1')
async def test_tg_get_for_admin_by_name_invalid_geoarea_type(taxi_geoareas):
    res = await taxi_geoareas.get(
        '/typed-geoareas/admin/v1/geoareas',
        params={'geoarea_type': 'logistic_dispatch_attractor', 'name': 'msk'},
    )

    assert res.status_code == 400
    got = res.json()
    assert got['code'] == 'unsupported_geoarea_type'
    assert (
        got['message']
        == 'no geoarea type [logistic_dispatch_attractor] '
        + 'in config TYPED_GEOAREAS_SETTINGS.editable_geoareas_types'
    )


@pytest.mark.filldb(geoareas='spb_msk2')
@pytest.mark.parametrize(
    'area_id', ['<msk1>', '<msk2>', '<spb>', '<removed>', '<nonexistent>'],
)
async def test_get_for_admin_by_id(taxi_geoareas, load_json, area_id):
    res = await taxi_geoareas.get(
        '/geoareas/admin/v1/tariff-areas', params={'id': area_id},
    )
    expected = list(
        filter(
            lambda x: x['id'] == area_id,
            load_json('geoareas_response_spb_msk2.json')
            + load_json('geoareas_response_spb_msk2_removed.json'),
        ),
    )
    common.check_get_response(res, expected, locale='ignore')


@pytest.mark.filldb(subvention_geoareas='spb_msk2')
@pytest.mark.filldb(typed_geoareas='spb_msk2')
@pytest.mark.parametrize(
    'area_id', ['<msk1>', '<msk2>', '<spb>', '<removed>', '<nonexistent>'],
)
@pytest.mark.parametrize(
    'collection_endpoint, collection_name',
    [
        ('/subvention-geoareas/admin/v1/geoareas', 'subvention_geoareas'),
        ('/typed-geoareas/admin/v1/geoareas', 'typed_geoareas'),
    ],
)
async def test_sg_get_for_admin_by_id(
        taxi_geoareas,
        load_json,
        area_id,
        collection_endpoint,
        collection_name,
):
    res = await taxi_geoareas.get(collection_endpoint, params={'id': area_id})
    if area_id != '<nonexistent>':
        expected = list(
            filter(
                lambda x: x['id'] == area_id,
                load_json(f'{collection_name}_response_spb_msk2.json')
                + load_json(
                    f'{collection_name}_response_spb_msk2_removed.json',
                ),
            ),
        )
        common.check_get_response(res, expected, locale='ignore')
    else:
        assert res.status_code == 404
        got = res.json()
        assert got['code'] == 'NOT_FOUND'
        assert (
            got['message'] == f'Could not find geoarea with id: <nonexistent>'
        )


@pytest.mark.filldb(geoareas='msk1')
async def test_get_for_admin_by_id_malformed(taxi_geoareas, mongodb):
    mongodb.geoareas.update({}, {'$unset': {'area': 1}})

    res = await taxi_geoareas.get(
        '/geoareas/admin/v1/tariff-areas',
        params={'id': 'a738f40b8ade4fed8939023e527d9358'},
    )
    expected = []
    common.check_get_response(res, expected, locale='ignore')


@pytest.mark.filldb(subvention_geoareas='msk1')
@pytest.mark.filldb(typed_geoareas='msk1')
@pytest.mark.parametrize(
    'collection_endpoint, collection_name',
    [
        ('/subvention-geoareas/admin/v1/geoareas', 'subvention_geoareas'),
        ('/typed-geoareas/admin/v1/geoareas', 'typed_geoareas'),
    ],
)
async def test_sg_get_for_admin_by_id_malformed(
        taxi_geoareas, mongodb, collection_endpoint, collection_name,
):
    getattr(mongodb, collection_name).update({}, {'$unset': {'area': 1}})

    res = await taxi_geoareas.get(
        collection_endpoint, params={'id': 'a738f40b8ade4fed8939023e527d9358'},
    )
    assert res.status_code == 404
    got = res.json()
    assert got['code'] == 'NOT_FOUND'
    assert (
        got['message']
        == f'Could not find geoarea with id: a738f40b8ade4fed8939023e527d9358'
    )


@pytest.mark.filldb(geoareas='msk1')
@pytest.mark.filldb(subvention_geoareas='msk1')
@pytest.mark.filldb(typed_geoareas='msk1')
@pytest.mark.config(TYPED_GEOAREAS_SETTINGS=DEFAULT_EDITABLE_TYPES)
@pytest.mark.parametrize(
    'collection_endpoint, collection_name, only_names',
    [
        ('/geoareas/admin/v1/tariff-areas', 'geoareas', False),
        ('/typed-geoareas/admin/v1/geoareas', 'typed_geoareas', False),
        ('/typed-geoareas/admin/v1/geoareas_names', 'typed_geoareas', True),
    ],
)
async def test_get_for_admin_duplicate(
        taxi_geoareas,
        load_json,
        mongodb,
        collection_endpoint,
        collection_name,
        only_names,
):
    area = getattr(mongodb, collection_name).find()[0]
    area['_id'] = 'other_id'
    area['created'] = datetime.datetime(2030, 2, 2)
    getattr(mongodb, collection_name).insert(area)

    res = await call_get_endpoint(taxi_geoareas, collection_endpoint)
    expected = load_json(f'{collection_name}_response_msk1_duplicate.json')
    common.check_get_response(
        res, expected, locale='ignore', only_names=only_names,
    )


@pytest.mark.filldb(subvention_geoareas='many')
@pytest.mark.filldb(typed_geoareas='many')
@pytest.mark.config(TYPED_GEOAREAS_SETTINGS=DEFAULT_EDITABLE_TYPES)
@pytest.mark.parametrize(
    'collection_endpoint, collection_name',
    [
        (
            '/subvention-geoareas/admin/v1/geoareas_names',
            'subvention_geoareas',
        ),
        ('/typed-geoareas/admin/v1/geoareas_names', 'typed_geoareas'),
    ],
)
async def test_get_sg_names_sorted(
        taxi_geoareas, load_json, collection_endpoint, collection_name,
):

    res = await call_get_endpoint(taxi_geoareas, collection_endpoint)
    expected = load_json('sg_tg_geoareas_names_sorted_response.json')
    got = res.json()
    assert got == expected


@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': ['one', 'two', 'seven'],
        'fetchable_geoareas_types': [],
    },
)
async def test_tg_get_types(taxi_geoareas):
    res = await taxi_geoareas.get('/typed-geoareas/admin/v1/types')
    assert res.status_code == 200
    assert set(res.json()['editable_types']) == {'one', 'two', 'seven'}


@pytest.mark.filldb(subvention_geoareas='many')
@pytest.mark.parametrize(
    'prefix, expected_response',
    [
        ('s', 'prefix_response_s.json'),
        ('msk', 'prefix_response_msk.json'),
        ('non_existing_prefix', 'prefix_response_empty.json'),
    ],
)
async def test_get_sg_names_by_prefix(
        taxi_geoareas, load_json, prefix, expected_response,
):

    res = await call_get_endpoint(
        taxi_geoareas,
        '/subvention-geoareas/admin/v1/geoareas_names',
        prefix=prefix,
    )
    expected = load_json(expected_response)
    got = res.json()

    assert_sorted(got['geoareas_names'], expected['geoareas_names'], 'name')


@pytest.mark.filldb(subvention_geoareas='many_for_bulk')
@pytest.mark.parametrize(
    'names, expected_code, expected_response',
    [
        (['spb'], 200, 'bulk_get_only_spb.json'),
        (['msk'], 200, 'bulk_get_only_msk.json'),
        (['spb', 'msk'], 200, 'bulk_msk_and_spb.json'),
        (['spb', 'msk', 'kazan'], 404, 'bulk_404_kazan.json'),
        (['spb', 'msk', 'kazan', 'ufa'], 404, 'bulk_404_kazan_ufa.json'),
    ],
)
async def test_sg_get_bulk(
        taxi_geoareas, load_json, names, expected_code, expected_response,
):

    res = await call_get_endpoint(
        taxi_geoareas,
        '/subvention-geoareas/admin/v1/geoareas',
        bulk_names=names,
    )

    assert res.status_code == expected_code
    if expected_code == 200:
        expected = load_json(expected_response)
        common.check_get_response(res, expected['geoareas'], 'ignore')
    else:
        got = res.json()
        expected = load_json(expected_response)
        assert got == expected
