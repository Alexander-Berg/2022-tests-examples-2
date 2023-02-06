from aiohttp import web
import pytest

from taxi_billing_accounts import models


@pytest.mark.parametrize(
    'request_body',
    [
        {'external_id': 'taximeter_driver_id', 'kind': 'driver'},
        {'external_id': 'corp/client/client_id', 'kind': 'corp_client'},
        {
            'external_id': 'corp/client_department/department_id',
            'kind': 'corp_client_department',
        },
        {
            'external_id': 'corp/client_employee/employee_id',
            'kind': 'corp_client_employee',
        },
        {'external_id': 'wallet_id/wallet_number', 'kind': 'wallet'},
    ],
)
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_entities_create(
        billing_accounts_client, request_headers, request_body,
):
    first = await billing_accounts_client.post(
        '/v1/entities/create', json=request_body, headers=request_headers,
    )

    second = await billing_accounts_client.post(
        '/v1/entities/create', json=request_body, headers=request_headers,
    )

    # check idempotency feature
    assert first.status == second.status
    assert await first.json() == await second.json()

    assert first.status == web.HTTPOk.status_code
    ans = await first.json()

    assert ans.get('created') is not None

    # test original fields
    ans.pop('created')
    assert ans == request_body


@pytest.mark.parametrize(
    'entity',
    [
        models.Entity(
            external_id='unique_driver_id/598c4d2689216ea4eee49939',
            kind='driver',
            created='2018-01-01T00:00:00',
        ),
        models.Entity(
            external_id='unique_driver_id/5b60199b41e102a72fe8268c',
            kind='driver',
            created='2018-01-02T00:00:00',
        ),
        models.Entity(
            external_id='unique_driver_id/5b0913df30a2e52b7633b3e6',
            kind='driver',
            created='2018-01-03T00:00:00',
        ),
        models.Entity(
            external_id='unique_driver_id/5b6c154741e102a72fddf926',
            kind='driver',
            created='2018-01-04T00:00:00',
        ),
    ],
)
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql', 'entities@0.sql'))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql', 'entities@1.sql'))
async def test_entities_search(
        billing_accounts_client, request_headers, entity,
):
    request_body = {'external_id': entity.external_id}
    response = await billing_accounts_client.post(
        '/v1/entities/search', json=request_body, headers=request_headers,
    )
    assert response.status == web.HTTPOk.status_code
    found_entities = await response.json()

    # exactly one entity has to be found
    assert found_entities and len(found_entities) == 1
    found_entity = models.Entity(**found_entities[0])
    assert found_entity == entity


@pytest.mark.parametrize(
    'entity',
    [
        models.Entity(
            external_id='n-unique_driver_id/598c4d2689216ea4eee49939',
        ),
        models.Entity(
            external_id='n-unique_driver_id/5b60199b41e102a72fe8268c',
        ),
        models.Entity(
            external_id='n-unique_driver_id/5b0913df30a2e52b7633b3e6',
        ),
        models.Entity(
            external_id='n-unique_driver_id/5b6c154741e102a72fddf926',
        ),
    ],
)
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql', 'entities@0.sql'))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql', 'entities@1.sql'))
async def test_entities_search_not_found(
        billing_accounts_client, request_headers, entity,
):
    request_body = {'external_id': entity.external_id}
    response = await billing_accounts_client.post(
        '/v1/entities/search', json=request_body, headers=request_headers,
    )
    assert response.status == web.HTTPOk.status_code
    entity_json = await response.json()
    assert not entity_json


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (None, web.HTTPUnsupportedMediaType),
        ({}, web.HTTPBadRequest),
        # Make sure valid request is fine
        ({'external_id': 'test/entity_id', 'kind': 'driver'}, web.HTTPOk),
        # Start play with invalid requests
        (
            {'entity_external_id': 'test/entity_id', 'kind': 'driver'},
            web.HTTPBadRequest,
        ),
        ({'kind': 'driver'}, web.HTTPBadRequest),
        ({'external_id': 'test/entity_id'}, web.HTTPBadRequest),
        (
            {'external_id': 'test/entity_id', 'kind': 'non-driver'},
            web.HTTPBadRequest,
        ),
    ],
)
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_entities_create_invalid(
        billing_accounts_client,
        request_headers,
        request_body,
        expected_response,
):
    response = await billing_accounts_client.post(
        '/v1/entities/create', json=request_body, headers=request_headers,
    )
    assert response.status == expected_response.status_code


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (None, web.HTTPUnsupportedMediaType),
        ({}, web.HTTPBadRequest),
        (
            {'entity_external_id': 'test/entity_id', 'kind': 'driver'},
            web.HTTPBadRequest,
        ),
        ({'kind': 'driver'}, web.HTTPBadRequest),
    ],
)
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_entities_search_invalid(
        billing_accounts_client,
        request_headers,
        request_body,
        expected_response,
):
    response = await billing_accounts_client.post(
        '/v1/entities/search', json=request_body, headers=request_headers,
    )
    assert response.status == expected_response.status_code
