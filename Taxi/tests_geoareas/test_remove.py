import pytest

from tests_geoareas import common


@pytest.mark.config(GEOAREAS_SERVICE_ENABLED=False)
async def test_remove_service_check(taxi_geoareas):
    res = await taxi_geoareas.put('/geoareas/admin/v1/tariff-areas/archive')

    assert res.status_code == 500
    assert res.json()['code'] == 'service_disabled'


@pytest.mark.parametrize(
    'params, error_code',
    [
        ({}, 'must_have_id_or_name'),
        (
            {'id': 'some_id', 'name': 'some_name'},
            'cannot_have_both_id_and_name',
        ),
    ],
)
async def test_remove_bad_request(taxi_geoareas, params, error_code):
    res = await taxi_geoareas.put(
        '/geoareas/admin/v1/tariff-areas/archive', params=params,
    )

    assert res.status_code == 400
    data = res.json()
    assert data['code'] == error_code


@pytest.mark.filldb(geoareas='spb_msk2')
@pytest.mark.parametrize(
    ['params', 'n_modified'],
    [
        ({'id': '<removed>'}, 0),
        ({'id': '<nonexistent>'}, 0),
        ({'id': '<msk1>'}, 0),
        ({'id': '<msk2>'}, 1),
        ({'id': '<spb>'}, 1),
        ({'name': 'removed'}, 0),
        ({'name': 'nonexistent'}, 0),
        ({'name': 'msk'}, 1),
        ({'name': 'spb'}, 1),
    ],
)
async def test_remove(taxi_geoareas, mockserver, params, n_modified):
    @mockserver.json_handler('/taxi-tariffs/v1/tariffs')
    def _mock_tariffs(request):
        return {'tariffs': []}

    res = await taxi_geoareas.put(
        '/geoareas/admin/v1/tariff-areas/archive', params=params,
    )

    assert res.status_code == 200
    assert res.json() == {'n_modified': n_modified}


@pytest.mark.filldb(geoareas='spb_msk2')
@pytest.mark.parametrize(
    ['params', 'should_remove'],
    [
        ({'id': '<msk2>'}, False),
        ({'id': '<spb>'}, True),
        ({'name': 'msk'}, False),
        ({'name': 'msk_activation'}, False),
        ({'name': 'spb'}, True),
        ({'name': 'foo'}, False),
    ],
)
async def test_remove_tariffs_check(
        taxi_geoareas, mockserver, params, should_remove,
):
    @mockserver.json_handler('/taxi-tariffs/v1/tariffs')
    def _mock_tariffs(request):
        return {
            'tariffs': [
                {
                    'id': 'msk_tariff',
                    'categories_names': ['econom'],
                    'home_zone': 'msk',
                    'activation_zone': 'msk_activation',
                    'related_zones': ['foo'],
                },
            ],
        }

    res = await taxi_geoareas.put(
        '/geoareas/admin/v1/tariff-areas/archive', params=params,
    )

    if should_remove:
        assert res.status_code == 200
        return

    assert res.status_code == 400
    data = res.json()
    assert data['code'] == 'geoarea_used_in_tariff'
    assert 'details' in data
    assert data['details'] == {'tariff_id': 'msk_tariff'}


@pytest.mark.parametrize(
    'collection_endpoint, endpoint_type',
    [
        ('/subvention-geoareas/admin/v1/remove_geoarea', 'remove'),
        ('/subvention-geoareas/admin/v1/remove_geoarea/check', 'check'),
        ('/typed-geoareas/admin/v1/remove_geoarea', 'remove'),
        ('/typed-geoareas/admin/v1/remove_geoarea/check', 'check'),
    ],
)
async def test_sg_remove_bad_request(
        taxi_geoareas, collection_endpoint, endpoint_type,
):
    if endpoint_type == 'remove':
        res = await taxi_geoareas.put(collection_endpoint)
    else:
        res = await taxi_geoareas.post(collection_endpoint)

    assert res.status_code == 400
    data = res.json()
    assert data['code'] == '400'


@pytest.mark.now('2021-01-31T00:00:00.000000Z')
@pytest.mark.filldb(subvention_geoareas='msk2_with_future_update')
@pytest.mark.parametrize(
    'collection_endpoint, is_check_handle, header',
    [
        ('/subvention-geoareas/v1/remove_geoarea', False, None),
        (
            '/subvention-geoareas/admin/v1/remove_geoarea',
            False,
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        ('/subvention-geoareas/admin/v1/remove_geoarea/check', True, None),
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
    request = {
        'id': 'a738f40b8ade4fed8939023e527d9358',
        'time_of_applying': '2030-01-31T00:00:00+0000',
    }
    res = await common.make_edit_or_check_request(
        taxi_geoareas, collection_endpoint, request, is_check_handle, header,
    )

    assert res.status_code == 409
    assert res.json()['code'] == 'version_has_update_in_future'


@pytest.mark.filldb(subvention_geoareas='spb_msk2')
@pytest.mark.filldb(typed_geoareas='spb_msk2')
@pytest.mark.parametrize(
    'collection_endpoint, header',
    [
        ('/typed-geoareas/admin/v1/remove_geoarea', None),
        (
            '/subvention-geoareas/admin/v1/remove_geoarea',
            common.SUBVENTION_GEOAREA_HEADER,
        ),
        ('/subvention-geoareas/v1/remove_geoarea', None),
    ],
)
@pytest.mark.parametrize(
    ['version_id', 'n_modified', 'expected_code'],
    [
        ('<removed>', 0, 400),
        ('<nonexistent>', 0, 404),
        ('<msk2>', 1, 200),
        ('<spb2>', 2, 200),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': ['logistic_dispatch_attractor'],
        'fetchable_geoareas_types': [],
    },
)
async def test_sg_tg_remove(
        taxi_geoareas,
        version_id,
        n_modified,
        expected_code,
        collection_endpoint,
        header,
):
    request = {'id': version_id}
    res = await taxi_geoareas.put(collection_endpoint, request, headers=header)

    assert res.status_code == expected_code
    if expected_code == 200:
        assert res.json() == {'n_modified': n_modified}


@pytest.mark.filldb(typed_geoareas='spb_msk2')
async def test_tg_remove_invalid_type(taxi_geoareas):
    res = await taxi_geoareas.put(
        '/typed-geoareas/admin/v1/remove_geoarea', {'id': '<msk2>'},
    )

    assert res.status_code == 400
    assert res.json()['code'] == 'unsupported_geoarea_type'
    assert (
        res.json()['message']
        == 'no geoarea type [logistic_dispatch_attractor] '
        + 'in config TYPED_GEOAREAS_SETTINGS.editable_geoareas_types'
    )


@pytest.mark.filldb(subvention_geoareas='spb_msk2')
@pytest.mark.filldb(typed_geoareas='spb_msk2')
@pytest.mark.parametrize(
    ['version_id', 'expected_code', 'expected_change_doc_id_suffix'],
    [
        ('<removed>', 400, None),
        ('<nonexistent>', 404, None),
        ('<msk2>', 200, 'msk'),
        ('<spb2>', 200, 'spb'),
    ],
)
@pytest.mark.parametrize(
    'collection_endpoint, collection_name, expected_change_doc_id_prefix',
    [
        (
            '/subvention-geoareas/admin/v1/remove_geoarea/check',
            'subvention_geoareas',
            '',
        ),
        (
            '/typed-geoareas/admin/v1/remove_geoarea/check',
            'typed_geoareas',
            'logistic_dispatch_attractor__',
        ),
    ],
)
@pytest.mark.config(
    TYPED_GEOAREAS_SETTINGS={
        'editable_geoareas_types': ['logistic_dispatch_attractor'],
        'fetchable_geoareas_types': [],
    },
)
async def test_sg_tg_remove_check(
        taxi_geoareas,
        load_json,
        version_id,
        expected_code,
        collection_endpoint,
        collection_name,
        expected_change_doc_id_prefix,
        expected_change_doc_id_suffix,
):
    request = {'id': version_id}
    res = await taxi_geoareas.post(collection_endpoint, request)

    assert res.status_code == expected_code

    # if status_code == 4xx, there won't be anything in the response
    if res.status_code == 200:
        response = {
            'data': request,
            'change_doc_id': (
                expected_change_doc_id_prefix + expected_change_doc_id_suffix
            ),
        }
        if collection_name == 'subvention_geoareas':
            db_before_request = load_json(
                'db_subvention_geoareas_spb_msk2.json',
            )
            needed_geoarea = None
            for geoarea in db_before_request:
                if geoarea['_id'] == version_id:
                    needed_geoarea = geoarea
                    break
            response['diff'] = {
                'current': {
                    'name': needed_geoarea['name'],
                    'geometry': needed_geoarea['geometry'],
                },
            }

        assert res.json() == response
