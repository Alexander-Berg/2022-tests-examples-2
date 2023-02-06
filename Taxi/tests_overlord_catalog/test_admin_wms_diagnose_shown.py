import pytest


@pytest.mark.parametrize(
    'product_id, title, case_id',
    [
        ('aaaaaaaa-aaaa-aaaa-aaaa-000000000000', None, 0),
        (None, 'product_name_1', 0),
        ('aaaaaaaa-aaaa-aaaa-aaaa-000000000000', 'product_name_1', 0),
        (None, 'product_name', 1),
        (None, 'profd', 2),
        ('aaaaaaaa-aaaa-aaaa-aaaa-000000000000', 'product_name_2', 2),
    ],
)
@pytest.mark.pgsql('overlord_catalog', files=['create_catalog_wms.sql'])
async def test_ok(
        taxi_overlord_catalog, load_json, product_id, title, case_id,
):

    request_json = {'depot_id': 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000'}
    if product_id:
        request_json['product_id'] = product_id
    if title:
        request_json['title'] = title

    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/wms/diagnose_shown', json=request_json,
    )

    expected_json = load_json('expected.json')

    assert response.status_code == 200
    assert expected_json[case_id] == response.json()


@pytest.mark.parametrize(
    'product_id, title, case_id',
    [
        ('aaaaaaaa-aaaa-aaaa-aaaa-000000000000', None, 0),
        (None, 'product_name_1', 0),
        ('aaaaaaaa-aaaa-aaaa-aaaa-000000000000', 'product_name_1', 0),
        (None, 'product_name', 1),
        (None, 'profd', 2),
        ('aaaaaaaa-aaaa-aaaa-aaaa-000000000000', 'product_name_2', 2),
    ],
)
@pytest.mark.pgsql('overlord_catalog', files=['create_catalog_wms.sql'])
async def test_ok_external_id(
        taxi_overlord_catalog, load_json, product_id, title, case_id,
):

    request_json = {'depot_id': '111'}
    if product_id:
        request_json['product_id'] = product_id
    if title:
        request_json['title'] = title

    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/wms/diagnose_shown', json=request_json,
    )

    expected_json = load_json('expected.json')

    assert response.status_code == 200
    assert expected_json[case_id] == response.json()


@pytest.mark.pgsql('overlord_catalog', files=['create_catalog_wms.sql'])
async def test_no_title_and_product_id(taxi_overlord_catalog):
    request_json = {'depot_id': 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000'}

    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/wms/diagnose_shown', json=request_json,
    )

    assert response.status_code == 400
