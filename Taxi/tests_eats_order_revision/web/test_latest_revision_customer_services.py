import datetime as dt
import json

import pytest

from tests_eats_order_revision import helpers


@pytest.mark.parametrize(
    'file, file_with_mixin, path',
    [
        (
            'revisions_without_details/revision_doc.json',
            'revisions_without_details/revision_doc_with_mixins_2.json',
            'v1/revision/latest/customer-services',
        ),
        (
            'revisions_with_details/revision_doc.json',
            'revisions_with_details/revision_doc_with_mixins.json',
            'v1/revision/latest/customer-services/details',
        ),
    ],
)
async def test_latest_revision_customer_services_correct(
        taxi_eats_order_revision,
        pgsql,
        load_json,
        file,
        file_with_mixin,
        path,
):
    doc = load_json(file)
    doc_with_mixin = load_json(file_with_mixin)

    helpers.insert_revision(
        pgsql=pgsql,
        order_id='test_order',
        origin_revision_id='test_revision',
        document=json.dumps(doc),
        created_at=dt.datetime.now(),
    )

    helpers.insert_revision(
        pgsql=pgsql,
        order_id='test_order',
        origin_revision_id='test_revision_1',
        document=json.dumps(doc),
        created_at=dt.datetime.now(),
    )

    helpers.insert_revision(
        pgsql=pgsql,
        order_id='test_order_1',
        origin_revision_id='test_revision_2',
        document=json.dumps(doc),
        created_at=dt.datetime.now(),
    )

    helpers.insert_default_mixins(pgsql, load_json)

    request = {'order_id': 'test_order'}

    response = await taxi_eats_order_revision.post(path, json=request)

    assert response.status == 200
    assert response.json()['origin_revision_id'] == 'test_revision_1'
    assert (
        response.json()['customer_services']
        == doc_with_mixin['customer_services']
    )
    if 'discounts' in doc_with_mixin:
        assert response.json()['discounts'] == doc_with_mixin['discounts']


@pytest.mark.parametrize(
    'path',
    [
        'v1/revision/latest/customer-services',
        'v1/revision/latest/customer-services/details',
    ],
)
async def test_latest_revision_customer_services_not_found(
        taxi_eats_order_revision, path,
):
    request = {'order_id': 'test_order'}
    response = await taxi_eats_order_revision.post(path, json=request)
    assert response.status == 404


@pytest.mark.parametrize(
    'path',
    [
        'v1/revision/latest/customer-services',
        'v1/revision/latest/customer-services/details',
    ],
)
async def test_latest_revision_customer_services_bad_request(
        taxi_eats_order_revision, path,
):
    request = {}
    response = await taxi_eats_order_revision.post(path, json=request)
    assert response.status == 400


@pytest.mark.parametrize(
    'path',
    [
        'v1/revision/latest/customer-services',
        'v1/revision/latest/customer-services/details',
    ],
)
@pytest.mark.config(
    EATS_ORDER_REVISION_FALLBACK={'core_fallback_enabled': True},
)
async def test_latest_revision_customer_services_server_error(
        taxi_eats_order_revision, path, mock_core_revision_list,
):
    request = {'order_id': 'test_order'}
    mock_core_revision_list(order_id='test_order_id', response={}, status=500)
    response = await taxi_eats_order_revision.post(path, json=request)
    assert response.status == 500


@pytest.mark.parametrize(
    'file, path',
    [
        (
            'revisions_without_details/revision_doc.json',
            'v1/revision/latest/customer-services',
        ),
        (
            'revisions_with_details/revision_doc.json',
            'v1/revision/latest/customer-services/details',
        ),
    ],
)
@pytest.mark.config(
    EATS_ORDER_REVISION_FALLBACK={'core_fallback_enabled': True},
)
async def test_latest_revision_customer_services_fallback(
        taxi_eats_order_revision,
        path,
        file,
        pgsql,
        load_json,
        mock_core_customer_services,
        mock_core_revision_list,
):
    doc = load_json(file)
    revision_list = load_json('core_revision_list.json')
    mock = mock_core_customer_services(
        order_id='test_order_id',
        revision_id='test_revision_id_1',
        response=doc,
    )
    mock_list = mock_core_revision_list(
        order_id='test_order_id', response=revision_list,
    )
    request = {'order_id': 'test_order_id'}
    response = await taxi_eats_order_revision.post(path, json=request)
    assert response.status == 200
    assert mock_list.times_called == 1
    assert mock.times_called == 1

    helpers.insert_revision(
        pgsql=pgsql,
        order_id='test_order_id',
        origin_revision_id='test_revision_id_1',
        document=json.dumps(doc),
    )
    response = await taxi_eats_order_revision.post(path, json=request)
    assert response.status == 200
    assert mock_list.times_called == 1
    assert mock.times_called == 1

    mock = mock_core_customer_services(
        order_id='test_order_id_1',
        revision_id='test_revision_id_1',
        response={},
        status=404,
    )
    mock_list = mock_core_revision_list(
        order_id='test_order_id_1', response=revision_list,
    )
    request = {'order_id': 'test_order_id_1'}
    response = await taxi_eats_order_revision.post(path, json=request)
    assert response.status == 404
    assert mock.times_called == 1
    assert mock_list.times_called == 1
