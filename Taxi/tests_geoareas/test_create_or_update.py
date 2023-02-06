# pylint: disable=C0302
import json

import pytest

from tests_geoareas import common

GEOAREAS_KEYSET = {
    'msk': {'ru': 'Москва', 'en': 'Moscow'},
    'spb': {'en': 'SPB'},
    'ololo_activation': {'ru': 'Пыщ-пыщ'},
}

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.translations(geoareas=GEOAREAS_KEYSET),
    pytest.mark.translations(subvention_geoareas=GEOAREAS_KEYSET),
    pytest.mark.translations(
        typed_geoareas={
            f'logistic_dispatch_attractor__{k}': v
            for k, v in GEOAREAS_KEYSET.items()
        },
    ),
    pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en']),
]


def get_geoarea_type_by_endpoint(endpoint: str):
    assert endpoint[0] == '/'
    second_slash_idx = endpoint.find('/', 1)
    return endpoint[1:second_slash_idx]


def get_tanker_key(geoarea_type, name):
    if geoarea_type:
        return f'{geoarea_type}__{name}'
    return name


def get_tanker_keyset_by_endpoint(endpoint):
    return get_geoarea_type_by_endpoint(endpoint).replace('-', '_')


@pytest.mark.config(GEOAREAS_SERVICE_ENABLED=False)
@pytest.mark.parametrize(
    'collection_endpoint, endpoint_type, geoarea_type, header',
    [
        ('/geoareas/admin/v1/tariff-areas', 'post', None, None),
        (
            '/subvention-geoareas/admin/v1/create_geoarea',
            'post',
            None,
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        (
            '/subvention-geoareas/admin/v1/update_geoarea',
            'put',
            None,
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        (
            '/typed-geoareas/admin/v1/create_geoarea',
            'post',
            'logistic_dispatch_attractor',
            None,
        ),
        (
            '/typed-geoareas/admin/v1/update_geoarea',
            'put',
            'logistic_dispatch_attractor',
            None,
        ),
    ],
)
async def test_create_or_update_service_check(
        taxi_geoareas,
        load_json,
        collection_endpoint,
        endpoint_type,
        geoarea_type,
        header,
):
    req_body = load_json('request_msk1.json')
    if geoarea_type:
        req_body['geoarea']['geoarea_type'] = geoarea_type
    if endpoint_type == 'post':
        res = await taxi_geoareas.post(
            collection_endpoint, req_body, headers=header,
        )
    else:
        req_body['id'] = 'a738f40b8ade4fed8939023e527d9358'
        res = await taxi_geoareas.put(
            collection_endpoint, req_body, headers=header,
        )

    assert res.status_code == 500
    assert json.loads(res.content)['code'] == 'service_disabled'


@pytest.mark.config(GEOAREAS_SERVICE_ENABLED=False)
@pytest.mark.parametrize(
    'collection_endpoint, endpoint_type, geoarea_type',
    [
        (
            '/subvention-geoareas/admin/v1/create_geoarea/check',
            'check_create',
            None,
        ),
        (
            '/subvention-geoareas/admin/v1/update_geoarea/check',
            'check_update',
            None,
        ),
        (
            '/typed-geoareas/admin/v1/create_geoarea/check',
            'check_create',
            'logistic_dispatch_attractor',
        ),
        (
            '/typed-geoareas/admin/v1/update_geoarea/check',
            'check_update',
            'logistic_dispatch_attractor',
        ),
    ],
)
async def test_check_endpoints_service_check(
        taxi_geoareas,
        load_json,
        collection_endpoint,
        endpoint_type,
        geoarea_type,
):
    req_body = load_json('request_msk1.json')
    if geoarea_type:
        req_body['geoarea']['geoarea_type'] = geoarea_type
    if endpoint_type == 'check_create':
        res = await taxi_geoareas.post(collection_endpoint, req_body)
    else:
        req_body['id'] = 'a738f40b8ade4fed8939023e527d9358'
        res = await taxi_geoareas.post(collection_endpoint, req_body)

    assert res.status_code == 500
    assert json.loads(res.content)['code'] == 'service_disabled'


MARKS_IGNORE_ALL = pytest.mark.config(
    GEOAREAS_IGNORE_MISSING_TRANSLATIONS=True,
    SUBVENTION_GEOAREAS_IGNORE_MISSING_TRANSLATIONS=True,
    TYPED_GEOAREAS_IGNORE_MISSING_TRANSLATIONS=True,
)


MARKS_IGNORE_ACTIVATION = pytest.mark.config(
    GEOAREAS_ALLOW_UNTRANSLATED={'regexes': ['_activation$']},
    SUBVENTION_GEOAREAS_ALLOW_UNTRANSLATED={'regexes': ['_activation$']},
    TYPED_GEOAREAS_ALLOW_UNTRANSLATED={'regexes': ['_activation$']},
)


@pytest.mark.parametrize(
    ['name', 'untranslated_locales'],
    [
        ['msk', []],
        ['spb', ['ru']],
        ['xxx', ['ru', 'en']],
        pytest.param('xxx', [], marks=MARKS_IGNORE_ALL),
        pytest.param(
            'ololo_activationololo',
            ['ru', 'en'],
            marks=MARKS_IGNORE_ACTIVATION,
        ),
        pytest.param('ololo_activation', [], marks=MARKS_IGNORE_ACTIVATION),
    ],
)
@pytest.mark.parametrize(
    'collection_endpoint, geoarea_type, header',
    [
        ('/geoareas/admin/v1/tariff-areas', None, None),
        (
            '/subvention-geoareas/admin/v1/create_geoarea',
            None,
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        ('/subvention-geoareas/admin/v1/create_geoarea/check', None, None),
        (
            '/typed-geoareas/admin/v1/create_geoarea',
            'logistic_dispatch_attractor',
            None,
        ),
        (
            '/typed-geoareas/admin/v1/create_geoarea/check',
            'logistic_dispatch_attractor',
            None,
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': ['logistic_dispatch_attractor'],
        'fetchable_geoareas_types': [],
    },
)
async def test_create_or_update_translation_check(
        taxi_geoareas,
        load_json,
        name,
        untranslated_locales,
        collection_endpoint,
        geoarea_type,
        header,
):
    req_body = load_json('request_msk1.json')
    if geoarea_type:
        req_body['geoarea']['geoarea_type'] = geoarea_type
    req_body['geoarea']['name'] = name
    res = await taxi_geoareas.post(
        collection_endpoint, req_body, headers=header,
    )

    if untranslated_locales == []:
        assert res.status_code == 200
        return

    assert res.status_code == 400
    data = json.loads(res.content)

    assert data['code'] == 'geoarea_name_untranslated'
    assert 'details' in data
    assert data['details']['tanker_key'] == get_tanker_key(geoarea_type, name)
    assert data['details']['tanker_keyset'] == get_tanker_keyset_by_endpoint(
        collection_endpoint,
    )
    assert data['details']['locale'] in untranslated_locales


@pytest.mark.filldb(subvention_geoareas='msk1')
@pytest.mark.filldb(typed_geoareas='msk1')
@pytest.mark.parametrize(
    ['name', 'untranslated_locales'],
    [
        ['msk', []],
        ['spb', ['ru']],
        ['xxx', ['ru', 'en']],
        pytest.param('xxx', [], marks=MARKS_IGNORE_ALL),
        pytest.param(
            'ololo_activationololo',
            ['ru', 'en'],
            marks=MARKS_IGNORE_ACTIVATION,
        ),
        pytest.param('ololo_activation', [], marks=MARKS_IGNORE_ACTIVATION),
    ],
)
@pytest.mark.parametrize(
    'collection_endpoint, endpoint_type, geoarea_type, collection_name, header',  # noqa: E501
    [
        (
            '/subvention-geoareas/admin/v1/update_geoarea',
            'update',
            None,
            'subvention_geoareas',
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        (
            '/subvention-geoareas/admin/v1/update_geoarea/check',
            'check',
            None,
            'subvention_geoareas',
            None,
        ),
        (
            '/typed-geoareas/admin/v1/update_geoarea',
            'update',
            'logistic_dispatch_attractor',
            'typed_geoareas',
            None,
        ),
        (
            '/typed-geoareas/admin/v1/update_geoarea/check',
            'check',
            'logistic_dispatch_attractor',
            'typed_geoareas',
            None,
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': ['logistic_dispatch_attractor'],
        'fetchable_geoareas_types': [],
    },
)
async def test_sg_tg_create_update_translation_check(
        mongodb,
        taxi_geoareas,
        load_json,
        name,
        untranslated_locales,
        collection_endpoint,
        endpoint_type,
        geoarea_type,
        collection_name,
        header,
):
    getattr(mongodb, collection_name).update({}, {'$set': {'name': name}})

    req_body = load_json('request_msk1.json')
    if geoarea_type:
        req_body['geoarea']['geoarea_type'] = geoarea_type
    req_body['geoarea']['name'] = name
    req_body['id'] = 'a738f40b8ade4fed8939023e527d9358'
    if endpoint_type == 'update':
        res = await taxi_geoareas.put(
            collection_endpoint, req_body, headers=header,
        )
    else:
        res = await taxi_geoareas.post(
            collection_endpoint, req_body, headers=header,
        )

    if not untranslated_locales:
        assert res.status_code == 200
        return

    assert res.status_code == 400
    data = json.loads(res.content)

    assert data['code'] == 'geoarea_name_untranslated'
    assert 'details' in data
    assert data['details']['tanker_key'] == get_tanker_key(geoarea_type, name)
    assert data['details']['tanker_keyset'] == get_tanker_keyset_by_endpoint(
        collection_endpoint,
    )
    assert data['details']['locale'] in untranslated_locales


@pytest.mark.parametrize(
    ['country', 'good'], [[None, True], ['rus', True], ['xxx', False]],
)
@pytest.mark.parametrize(
    'collection_endpoint, geoarea_type, header',
    [
        ('/geoareas/admin/v1/tariff-areas', None, None),
        (
            '/subvention-geoareas/admin/v1/create_geoarea',
            None,
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        ('/subvention-geoareas/admin/v1/create_geoarea/check', None, None),
        (
            '/typed-geoareas/admin/v1/create_geoarea',
            'logistic_dispatch_attractor',
            None,
        ),
        (
            '/typed-geoareas/admin/v1/create_geoarea/check',
            'logistic_dispatch_attractor',
            None,
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': ['logistic_dispatch_attractor'],
        'fetchable_geoareas_types': [],
    },
)
async def test_create_or_update_country_check(
        taxi_geoareas,
        load_json,
        country,
        good,
        collection_endpoint,
        geoarea_type,
        header,
):
    req_body = load_json('request_msk1.json')
    if geoarea_type:
        req_body['geoarea']['geoarea_type'] = geoarea_type
    req_body['geoarea']['country'] = country
    res = await taxi_geoareas.post(
        collection_endpoint, req_body, headers=header,
    )

    if good:
        assert res.status_code == 200
        return

    assert res.status_code == 400
    data = json.loads(res.content)

    assert data['code'] == 'unknown_country'


@pytest.mark.filldb(subvention_geoareas='msk1')
@pytest.mark.filldb(typed_geoareas='msk1')
@pytest.mark.parametrize(
    ['country', 'good'], [[None, True], ['rus', True], ['xxx', False]],
)
@pytest.mark.parametrize(
    'collection_endpoint, endpoint_type, geoarea_type, header',
    [
        (
            '/subvention-geoareas/admin/v1/update_geoarea',
            'update',
            None,
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        (
            '/subvention-geoareas/admin/v1/update_geoarea/check',
            'check',
            None,
            None,
        ),
        (
            '/typed-geoareas/admin/v1/update_geoarea',
            'update',
            'logistic_dispatch_attractor',
            None,
        ),
        (
            '/typed-geoareas/admin/v1/update_geoarea/check',
            'check',
            'logistic_dispatch_attractor',
            None,
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': ['logistic_dispatch_attractor'],
        'fetchable_geoareas_types': [],
    },
)
async def test_sg_update_country_check(
        taxi_geoareas,
        load_json,
        country,
        good,
        collection_endpoint,
        endpoint_type,
        geoarea_type,
        header,
):
    req_body = load_json('request_msk1.json')
    if geoarea_type:
        req_body['geoarea']['geoarea_type'] = geoarea_type
    req_body['geoarea']['country'] = country
    req_body['id'] = 'a738f40b8ade4fed8939023e527d9358'
    if endpoint_type == 'update':
        res = await taxi_geoareas.put(
            collection_endpoint, req_body, headers=header,
        )
    else:
        res = await taxi_geoareas.post(
            collection_endpoint, req_body, headers=header,
        )

    if good:
        assert res.status_code == 200
        return

    assert res.status_code == 400
    data = json.loads(res.content)

    assert data['code'] == 'unknown_country'


@pytest.mark.now('2020-02-02T02:02:02.000000Z')
@pytest.mark.parametrize(
    'collection_endpoint, collection_name, geoarea_type, header',
    [
        ('/geoareas/admin/v1/tariff-areas', 'geoareas', None, None),
        (
            '/subvention-geoareas/admin/v1/create_geoarea',
            'subvention_geoareas',
            None,
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        (
            '/typed-geoareas/admin/v1/create_geoarea',
            'typed_geoareas',
            'logistic_dispatch_attractor',
            None,
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': ['logistic_dispatch_attractor'],
        'fetchable_geoareas_types': [],
    },
)
async def test_create_or_update_create(
        taxi_geoareas,
        load_json,
        mongodb,
        bson_hook,
        collection_endpoint,
        collection_name,
        geoarea_type,
        header,
):
    req_body = load_json('request_msk1.json')
    if geoarea_type:
        req_body['geoarea']['geoarea_type'] = geoarea_type
    res = await taxi_geoareas.post(
        collection_endpoint, req_body, headers=header,
    )

    assert res.status_code == 200
    doc_id = res.json()['id']
    db_content = list(getattr(mongodb, collection_name).find())
    expected_db_content = load_json(
        'db_geoareas_msk1.json', object_hook=bson_hook,
    )
    expected_db_content[0]['_id'] = doc_id
    if collection_name == 'typed_geoareas':
        expected_db_content[0]['geoarea_type'] = 'logistic_dispatch_attractor'
    elif collection_name == 'subvention_geoareas':
        expected_db_content[0]['create_draft_id'] = 'some_id'
    assert db_content == common.deep_approx(expected_db_content)


@pytest.mark.now('2020-02-02T03:02:02.000000Z')
@pytest.mark.filldb(geoareas='msk1')
@pytest.mark.filldb(subvention_geoareas='msk1')
@pytest.mark.filldb(typed_geoareas='msk1')
@pytest.mark.parametrize(
    'collection_endpoint, collection_name, geoarea_type, header',
    [
        ('/geoareas/admin/v1/tariff-areas', 'geoareas', None, None),
        (
            '/subvention-geoareas/admin/v1/update_geoarea',
            'subvention_geoareas',
            None,
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        (
            '/typed-geoareas/admin/v1/update_geoarea',
            'typed_geoareas',
            'logistic_dispatch_attractor',
            None,
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': ['logistic_dispatch_attractor'],
        'fetchable_geoareas_types': [],
    },
)
async def test_create_or_update_update(
        taxi_geoareas,
        load_json,
        mongodb,
        bson_hook,
        collection_endpoint,
        collection_name,
        geoarea_type,
        header,
):
    req_body = load_json(f'{collection_name}_request_msk2.json')
    if geoarea_type:
        req_body['geoarea']['geoarea_type'] = geoarea_type
    if collection_name == 'geoareas':
        res = await taxi_geoareas.post(
            collection_endpoint, req_body, headers=header,
        )
        await taxi_geoareas.invalidate_caches()
    else:
        res = await taxi_geoareas.put(
            collection_endpoint, req_body, headers=header,
        )

    assert res.status_code == 200
    doc_id = res.json()['id']
    db_content = list(getattr(mongodb, collection_name).find())
    expected_db_content = load_json(
        f'db_{collection_name}_msk2.json', object_hook=bson_hook,
    )
    expected_db_content[1]['_id'] = doc_id
    assert db_content == common.deep_approx(expected_db_content)


@pytest.mark.now('2021-01-31T00:00:00.000000Z')
@pytest.mark.filldb(subvention_geoareas='msk1')
@pytest.mark.parametrize(
    'collection_endpoint, is_check_handle, header',
    [
        (
            '/subvention-geoareas/admin/v1/update_geoarea',
            False,
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        ('/subvention-geoareas/admin/v1/update_geoarea/check', True, None),
    ],
)
async def test_sg_update_in_future(
        taxi_geoareas,
        load_json,
        mongodb,
        bson_hook,
        collection_endpoint,
        is_check_handle,
        header,
):
    req_body = load_json(
        'subvention_geoareas_request_msk2_for_future_update.json',
    )
    res = await common.make_edit_or_check_request(
        taxi_geoareas, collection_endpoint, req_body, is_check_handle, header,
    )

    assert res.status_code == 200
    if not is_check_handle:
        doc_id = res.json()['id']
        db_content = list(mongodb.subvention_geoareas.find())
        expected_db_content = load_json(
            f'db_subvention_geoareas_msk2_with_future_update.json',
            object_hook=bson_hook,
        )
        expected_db_content[1]['_id'] = doc_id
        assert db_content == common.deep_approx(expected_db_content)


@pytest.mark.now('2021-01-31T00:00:00.000000Z')
@pytest.mark.filldb(subvention_geoareas='msk1')
@pytest.mark.parametrize(
    'collection_endpoint, is_check_handle, header',
    [
        (
            '/subvention-geoareas/admin/v1/update_geoarea',
            False,
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        ('/subvention-geoareas/admin/v1/update_geoarea/check', True, None),
    ],
)
async def test_sg_update_in_future_wrong_params(
        taxi_geoareas,
        load_json,
        mongodb,
        bson_hook,
        collection_endpoint,
        is_check_handle,
        header,
):
    req_body = load_json(
        'subvention_geoareas_request_msk2_for_future_update.json',
    )
    req_body['time_of_applying'] = '2020-01-31T00:00:00.000000Z'
    res = await common.make_edit_or_check_request(
        taxi_geoareas, collection_endpoint, req_body, is_check_handle, header,
    )

    assert res.status_code == 400
    assert res.json()['code'] == 'time_of_applying_is_in_the_past'


@pytest.mark.now('2021-01-31T00:00:00.000000Z')
@pytest.mark.filldb(subvention_geoareas='msk2_with_future_update')
@pytest.mark.parametrize(
    'collection_endpoint, is_check_handle, header',
    [
        (
            '/subvention-geoareas/admin/v1/update_geoarea',
            False,
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        ('/subvention-geoareas/admin/v1/update_geoarea/check', True, None),
    ],
)
async def test_sg_already_has_update_in_future(
        taxi_geoareas,
        load_json,
        mongodb,
        bson_hook,
        collection_endpoint,
        is_check_handle,
        header,
):
    req_body = load_json(
        'subvention_geoareas_request_msk2_for_future_update.json',
    )
    res = await common.make_edit_or_check_request(
        taxi_geoareas, collection_endpoint, req_body, is_check_handle, header,
    )

    assert res.status_code == 409
    assert res.json()['code'] == 'version_has_update_in_future'


@pytest.mark.now('2020-02-02T03:02:02.000000Z')
@pytest.mark.parametrize(
    [],
    [
        pytest.param(
            marks=pytest.mark.config(
                GEOAREAS_ALLOW_INSERTING_BAD_GEOMETRY=False,
                SUBVENTION_GEOAREAS_ALLOW_INSERTING_BAD_GEOMETRY=False,
                TYPED_GEOAREAS_ALLOW_INSERTING_BAD_GEOMETRY=False,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                GEOAREAS_ALLOW_INSERTING_BAD_GEOMETRY=True,
                SUBVENTION_GEOAREAS_ALLOW_INSERTING_BAD_GEOMETRY=True,
                TYPED_GEOAREAS_ALLOW_INSERTING_BAD_GEOMETRY=True,
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'collection_endpoint, geoarea_type, header',
    [
        ('/geoareas/admin/v1/tariff-areas', None, None),
        (
            '/subvention-geoareas/admin/v1/create_geoarea',
            None,
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        (
            '/typed-geoareas/admin/v1/create_geoarea',
            'logistic_dispatch_attractor',
            None,
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': ['logistic_dispatch_attractor'],
        'fetchable_geoareas_types': [],
    },
)
async def test_create_or_update_invalid_geometry(
        taxi_geoareas,
        load_json,
        mongodb,
        taxi_config,
        collection_endpoint,
        geoarea_type,
        header,
):
    allow_invalid_geometry = taxi_config.get(
        'GEOAREAS_ALLOW_INSERTING_BAD_GEOMETRY',
    )

    req_body = load_json('request_invalid_geometry.json')
    if geoarea_type:
        req_body['geoarea']['geoarea_type'] = geoarea_type
    res = await taxi_geoareas.post(
        collection_endpoint, req_body, headers=header,
    )

    if allow_invalid_geometry:
        # mongo will not allow inserting such invalid geometry
        assert res.status_code == 500
        return

    assert res.status_code == 400
    res_json = res.json()
    assert res_json['code'] == 'invalid_geometry'
    assert 'Geometry has wrong topological dimension' in res_json['message']

    db_content = list(mongodb.geoareas.find())
    assert db_content == []


@pytest.mark.now('2020-02-02T02:02:02.000000Z')
@MARKS_IGNORE_ALL
@pytest.mark.parametrize(
    'collection_endpoint, collection_name, geoarea_type, header',
    [
        ('/geoareas/admin/v1/tariff-areas', 'geoareas', None, None),
        (
            '/subvention-geoareas/admin/v1/create_geoarea',
            'subvention_geoareas',
            None,
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        (
            '/typed-geoareas/admin/v1/create_geoarea',
            'typed_geoareas',
            'logistic_dispatch_attractor',
            None,
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': ['logistic_dispatch_attractor'],
        'fetchable_geoareas_types': [],
    },
)
async def test_create_or_update_fixable_geometry(
        taxi_geoareas,
        load_json,
        mongodb,
        bson_hook,
        collection_endpoint,
        collection_name,
        geoarea_type,
        header,
):
    req_body = load_json('request_fixable_geometry.json')
    if geoarea_type:
        req_body['geoarea']['geoarea_type'] = geoarea_type
    res = await taxi_geoareas.post(
        collection_endpoint, req_body, headers=header,
    )

    assert res.status_code == 200
    doc_id = res.json()['id']
    db_content = list(getattr(mongodb, collection_name).find())
    expected_db_content = load_json(
        'db_geoareas_fixed_geometry.json', object_hook=bson_hook,
    )
    expected_db_content[0]['_id'] = doc_id
    if collection_name == 'typed_geoareas':
        expected_db_content[0]['geoarea_type'] = 'logistic_dispatch_attractor'
    elif collection_name == 'subvention_geoareas':
        expected_db_content[0]['create_draft_id'] = 'some_id'
    assert db_content == common.deep_approx(expected_db_content)


@pytest.mark.now('2020-02-02T02:02:02.000000Z')
@pytest.mark.parametrize(
    'collection_endpoint, collection_name, response',
    [
        (
            '/subvention-geoareas/admin/v1/create_geoarea/check',
            'subvention_geoareas',
            {'change_doc_id': 'msk'},
        ),
        (
            '/typed-geoareas/admin/v1/create_geoarea/check',
            'typed_geoareas',
            {'change_doc_id': 'logistic_dispatch_attractor__msk'},
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': ['logistic_dispatch_attractor'],
        'fetchable_geoareas_types': [],
    },
)
async def test_sg_tg_create_check(
        taxi_geoareas,
        load_json,
        collection_endpoint,
        collection_name,
        response,
):
    req_body = load_json('request_msk1.json')
    if collection_name == 'typed_geoareas':
        req_body['geoarea']['geoarea_type'] = 'logistic_dispatch_attractor'
    res = await taxi_geoareas.post(collection_endpoint, req_body)

    assert res.status_code == 200
    response['data'] = req_body

    if collection_name == 'subvention_geoareas':
        response['diff'] = {
            'new': {
                'name': req_body['geoarea']['name'],
                'geometry': req_body['geoarea']['geometry'],
            },
        }

    assert res.json() == common.deep_approx(response)


@pytest.mark.now('2020-02-02T03:02:02.000000Z')
@pytest.mark.filldb(subvention_geoareas='msk1')
@pytest.mark.filldb(typed_geoareas='msk1')
@pytest.mark.parametrize(
    'collection_endpoint, collection_name, response',
    [
        (
            '/subvention-geoareas/admin/v1/update_geoarea/check',
            'subvention_geoareas',
            {'change_doc_id': 'msk'},
        ),
        (
            '/typed-geoareas/admin/v1/update_geoarea/check',
            'typed_geoareas',
            {'change_doc_id': 'logistic_dispatch_attractor__msk'},
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': ['logistic_dispatch_attractor'],
        'fetchable_geoareas_types': [],
    },
)
async def test_sg_tg_update_check(
        taxi_geoareas,
        load_json,
        collection_endpoint,
        collection_name,
        response,
):
    req_name = f'{collection_name}_request_msk2.json'
    req_body = load_json(req_name)
    if collection_name == 'typed_geoareas':
        req_body['geoarea']['geoarea_type'] = 'logistic_dispatch_attractor'
    res = await taxi_geoareas.post(collection_endpoint, req_body)

    assert res.status_code == 200
    response['data'] = req_body
    if collection_name == 'subvention_geoareas':
        db_before_request = load_json('db_subvention_geoareas_msk1.json')
        db_before_request[0]['id'] = db_before_request[0].pop('_id')
        db_before_request[0]['created'] = db_before_request[0][
            'created'
        ].strftime('%Y-%m-%dT%H:%M:%S+0000')
        response['diff'] = {
            'new': {
                'name': req_body['geoarea']['name'],
                'geometry': req_body['geoarea']['geometry'],
            },
            'current': {
                'name': db_before_request[0]['name'],
                'geometry': db_before_request[0]['geometry'],
            },
        }

    assert res.json() == common.deep_approx(response)


@pytest.mark.now('2020-02-02T02:02:02.000000Z')
@pytest.mark.filldb(subvention_geoareas='msk1')
@pytest.mark.filldb(typed_geoareas='msk1')
@pytest.mark.parametrize(
    'collection_endpoint, geoarea_type, header',
    [
        (
            '/subvention-geoareas/admin/v1/create_geoarea',
            None,
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        ('/subvention-geoareas/admin/v1/create_geoarea/check', None, None),
        (
            '/typed-geoareas/admin/v1/create_geoarea',
            'logistic_dispatch_attractor',
            None,
        ),
        (
            '/typed-geoareas/admin/v1/create_geoarea/check',
            'logistic_dispatch_attractor',
            None,
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': ['logistic_dispatch_attractor'],
        'fetchable_geoareas_types': [],
    },
)
async def test_sg_tg_create_check_duplicate(
        taxi_geoareas, load_json, collection_endpoint, geoarea_type, header,
):
    req_body = load_json('request_msk1.json')
    if geoarea_type:
        req_body['geoarea']['geoarea_type'] = geoarea_type
    res = await taxi_geoareas.post(
        collection_endpoint, req_body, headers=header,
    )

    assert res.status_code == 409


@pytest.mark.now('2020-02-02T02:02:02.000000Z')
@pytest.mark.filldb(subvention_geoareas='msk1_removed')
@pytest.mark.filldb(typed_geoareas='msk1_removed')
@pytest.mark.parametrize(
    'request_filename, expected_code',
    [
        ('subvention_geoareas_request_msk2.json', 400),
        ('subvention_geoareas_request_msk2_404.json', 404),
        ('typed_geoareas_request_msk2.json', 400),
        ('typed_geoareas_request_msk2_404.json', 404),
    ],
)
@pytest.mark.parametrize(
    'collection_endpoint, endpoint_type, geoarea_type, header',
    [
        (
            '/subvention-geoareas/admin/v1/update_geoarea',
            'update',
            None,
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        (
            '/subvention-geoareas/admin/v1/update_geoarea/check',
            'check',
            None,
            None,
        ),
        (
            '/typed-geoareas/admin/v1/update_geoarea',
            'update',
            'logistic_dispatch_attractor',
            None,
        ),
        (
            '/typed-geoareas/admin/v1/update_geoarea/check',
            'check',
            'logistic_dispatch_attractor',
            None,
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': ['logistic_dispatch_attractor'],
        'fetchable_geoareas_types': [],
    },
)
async def test_sg_tg_update_check_version(
        taxi_geoareas,
        load_json,
        request_filename,
        expected_code,
        collection_endpoint,
        endpoint_type,
        geoarea_type,
        header,
):
    req_body = load_json(request_filename)
    if geoarea_type:
        req_body['geoarea']['geoarea_type'] = geoarea_type
    if endpoint_type == 'update':
        res = await taxi_geoareas.put(
            collection_endpoint, req_body, headers=header,
        )
    else:
        res = await taxi_geoareas.post(
            collection_endpoint, req_body, headers=header,
        )

    assert res.status_code == expected_code


@pytest.mark.now('2020-02-02T02:02:02.000000Z')
@pytest.mark.parametrize(
    'collection_endpoint, geoarea_type, status_code, response_code',
    [
        (
            '/typed-geoareas/admin/v1/create_geoarea',
            'logistic_dispatch_attractor',
            200,
            None,
        ),
        ('/typed-geoareas/admin/v1/create_geoarea', None, 400, '400'),
        (
            '/typed-geoareas/admin/v1/create_geoarea',
            'unknown_geoarea_type',
            400,
            'unsupported_geoarea_type',
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': [
            'logistic_dispatch_attractor',
            'logistic_dispatch_attractor_2',
        ],
        'fetchable_geoareas_types': [],
    },
)
async def test_tg_create_invalid_geoarea_type(
        taxi_geoareas,
        load_json,
        collection_endpoint,
        geoarea_type,
        status_code,
        response_code,
):
    req_body = load_json('request_msk1.json')
    if geoarea_type:
        req_body['geoarea']['geoarea_type'] = geoarea_type
    res = await taxi_geoareas.post(collection_endpoint, req_body)

    assert res.status_code == status_code
    if status_code != 200:
        assert res.json()['code'] == response_code


@pytest.mark.now('2020-02-02T03:02:02.000000Z')
@pytest.mark.filldb(typed_geoareas='msk1')
@pytest.mark.parametrize(
    'collection_endpoint, geoarea_type, status_code, response_code',
    [
        (
            '/typed-geoareas/admin/v1/update_geoarea',
            'logistic_dispatch_attractor',
            200,
            None,
        ),
        ('/typed-geoareas/admin/v1/update_geoarea', None, 400, '400'),
        (
            '/typed-geoareas/admin/v1/update_geoarea',
            'unknown_geoarea_type',
            400,
            'unsupported_geoarea_type',
        ),
        (
            '/typed-geoareas/admin/v1/update_geoarea',
            'logistic_dispatch_attractor_2',
            400,
            'geoarea_type_change_attempt',
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': [
            'logistic_dispatch_attractor',
            'logistic_dispatch_attractor_2',
        ],
        'fetchable_geoareas_types': [],
    },
)
async def test_tg_update_invalid_geoarea_type(
        taxi_geoareas,
        load_json,
        collection_endpoint,
        geoarea_type,
        status_code,
        response_code,
):
    req_body = load_json('typed_geoareas_request_msk2.json')
    if geoarea_type:
        req_body['geoarea']['geoarea_type'] = geoarea_type
    res = await taxi_geoareas.put(collection_endpoint, req_body)

    assert res.status_code == status_code
    if status_code != 200:
        assert res.json()['code'] == response_code


@pytest.mark.now('2020-02-02T02:02:02.000000Z')
@pytest.mark.parametrize(
    'collection_endpoint, geoarea_type, status_code, response_code',
    [
        (
            '/typed-geoareas/admin/v1/create_geoarea/check',
            'logistic_dispatch_attractor',
            200,
            None,
        ),
        ('/typed-geoareas/admin/v1/create_geoarea/check', None, 400, '400'),
        (
            '/typed-geoareas/admin/v1/create_geoarea/check',
            'unknown_geoarea_type',
            400,
            'unsupported_geoarea_type',
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': [
            'logistic_dispatch_attractor',
            'logistic_dispatch_attractor_2',
        ],
        'fetchable_geoareas_types': [],
    },
)
async def test_tg_create_check_invalid_geoarea_type(
        taxi_geoareas,
        load_json,
        collection_endpoint,
        geoarea_type,
        status_code,
        response_code,
):
    req_body = load_json('request_msk1.json')
    if geoarea_type:
        req_body['geoarea']['geoarea_type'] = geoarea_type
    res = await taxi_geoareas.post(collection_endpoint, req_body)

    assert res.status_code == status_code
    if status_code != 200:
        assert res.json()['code'] == response_code


@pytest.mark.now('2020-02-02T03:02:02.000000Z')
@pytest.mark.filldb(typed_geoareas='msk1')
@pytest.mark.parametrize(
    'collection_endpoint, geoarea_type, status_code, response_code',
    [
        (
            '/typed-geoareas/admin/v1/update_geoarea/check',
            'logistic_dispatch_attractor',
            200,
            None,
        ),
        ('/typed-geoareas/admin/v1/update_geoarea/check', None, 400, '400'),
        (
            '/typed-geoareas/admin/v1/update_geoarea/check',
            'unknown_geoarea_type',
            400,
            'unsupported_geoarea_type',
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': [
            'logistic_dispatch_attractor',
            'logistic_dispatch_attractor_2',
        ],
        'fetchable_geoareas_types': [],
    },
)
async def test_tg_update_check_invalid_geoarea_type(
        taxi_geoareas,
        load_json,
        collection_endpoint,
        geoarea_type,
        status_code,
        response_code,
):
    req_body = load_json('typed_geoareas_request_msk2.json')
    if geoarea_type:
        req_body['geoarea']['geoarea_type'] = geoarea_type
    res = await taxi_geoareas.post(collection_endpoint, req_body)

    assert res.status_code == status_code
    if status_code != 200:
        assert res.json()['code'] == response_code


@pytest.mark.filldb(subvention_geoareas='msk1')
@pytest.mark.parametrize(
    'collection_endpoint, endpoint_type, header',
    [
        (
            '/subvention-geoareas/admin/v1/create_geoarea',
            'post',
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        ('/subvention-geoareas/admin/v1/create_geoarea/check', 'post', None),
        (
            '/subvention-geoareas/admin/v1/update_geoarea',
            'put',
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        (
            '/subvention-geoareas/admin/v1/update_geoarea/check',
            'update_post',
            None,
        ),
    ],
)
async def test_create_or_update_check_name_validity(
        taxi_geoareas, load_json, collection_endpoint, endpoint_type, header,
):
    req_body = load_json('empty_name_request.json')
    if endpoint_type == 'post':
        res = await taxi_geoareas.post(
            collection_endpoint, req_body, headers=header,
        )
    elif endpoint_type == 'put':
        req_body['id'] = 'a738f40b8ade4fed8939023e527d9358'
        res = await taxi_geoareas.put(
            collection_endpoint, req_body, headers=header,
        )
    elif endpoint_type == 'update_post':
        req_body['id'] = 'a738f40b8ade4fed8939023e527d9358'
        res = await taxi_geoareas.post(
            collection_endpoint, req_body, headers=header,
        )

    assert res.status_code == 400
    data = json.loads(res.content)

    assert data['code'] == 'invalid_name'


@pytest.mark.parametrize(
    'collection_endpoint, status_code',
    [
        ('/subvention-geoareas/admin/v1/create_geoarea', 400),
        ('/subvention-geoareas/internal/v1/create_geoarea', 200),
    ],
)
async def test_create_or_update_create_without_draft_id(
        taxi_geoareas, load_json, mongodb, collection_endpoint, status_code,
):
    req_body = load_json('request_msk1.json')

    res = await taxi_geoareas.post(collection_endpoint, req_body)
    assert res.status_code == status_code
    if status_code == 200:
        db_content = getattr(mongodb, 'subvention_geoareas').find()
        draft_id = db_content[0].get('create_draft_id', None)
        assert draft_id is None
