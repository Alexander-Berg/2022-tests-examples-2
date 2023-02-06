import uuid

import asyncpg
import pytest


# pylint: disable=unused-variable,function-redefined
from taxi.util import dates


async def test_new_verify_communication_idempotency_ok(web_app_client, patch):
    times_called = 0

    @patch('crm_hub.logic.yt_absorber_v2.create_absorber_task')
    async def create_absorber_task(*args, **kwargs):
        nonlocal times_called
        times_called += 1

    response = await web_app_client.post(
        '/v1/communication/bulk/verify',
        json={'campaign_id': 123, 'group_id': 123},
        headers={
            'X-Idempotency-Token': '5d7d1d3d-0a32-4c63-88ad-865d1aaaa01e',
        },
    )

    assert response.status == 200
    assert times_called == 1

    # duplicate token
    response = await web_app_client.post(
        '/v1/communication/bulk/verify',
        json={'campaign_id': 123, 'group_id': 123},
        headers={
            'X-Idempotency-Token': '5d7d1d3d-0a32-4c63-88ad-865d1aaaa01e',
        },
    )
    assert response.status == 200
    assert times_called == 1

    # new token
    response = await web_app_client.post(
        '/v1/communication/bulk/verify',
        json={'campaign_id': 123, 'group_id': 123},
        headers={
            'X-Idempotency-Token': '7477b161-04bb-4e50-acc4-83ec0da8cdc3',
        },
    )
    assert response.status == 200
    assert times_called == 2

    # no token
    response = await web_app_client.post(
        '/v1/communication/bulk/verify',
        json={'campaign_id': 123, 'group_id': 123},
    )
    assert response.status == 200
    assert times_called == 3

    # invalid token
    response = await web_app_client.post(
        '/v1/communication/bulk/verify',
        json={'campaign_id': 123, 'group_id': 123},
        headers={'X-Idempotency-Token': 'this-is-no-guid'},
    )
    assert response.status == 400
    assert times_called == 3


IDEMPOTENCY_TEST_TIME = '2021-01-25 01:00:00'


@pytest.mark.now(IDEMPOTENCY_TEST_TIME)
async def test_new_verify_communication_idempotency_db_table_entry_ok(
        web_app_client, patch, web_context,
):
    @patch('crm_hub.logic.yt_absorber_v2.create_absorber_task')
    async def create_absorber_task(*args, **kwargs):
        pass

    idempotency_token = '5d7d1d3d-0a32-4c63-88ad-865d1aaaa01e'
    await web_app_client.post(
        '/v1/communication/bulk/verify',
        json={'campaign_id': 123, 'group_id': 123},
        headers={'X-Idempotency-Token': idempotency_token},
    )

    async with web_context.pg.master_pool.acquire() as conn:
        entries = await conn.fetch(
            'SELECT id, path, created_at FROM crm_hub.idempotency_token;',
        )
    assert len(entries) == 1
    id_, path, created_at = entries[0]
    assert id_ == uuid.UUID(idempotency_token)
    assert path == '/v1/communication/bulk/verify'
    assert str(created_at) == IDEMPOTENCY_TEST_TIME


async def test_new_verify_communication_idempotency_unhandled_exception(
        web_app_client, patch,
):
    times_called = 0

    @patch('crm_hub.logic.yt_absorber_v2.create_absorber_task')
    async def create_absorber_task(*args, **kwargs):
        nonlocal times_called
        times_called += 1
        raise Exception('spanish inquisition')

    idempotency_token = '5d7d1d3d-0a32-4c63-88ad-865d1aaaa01e'
    response = await web_app_client.post(
        '/v1/communication/bulk/verify',
        json={'campaign_id': 123, 'group_id': 123},
        headers={'X-Idempotency-Token': idempotency_token},
    )
    assert response.status == 500
    assert times_called == 1

    @patch('crm_hub.logic.yt_absorber_v2.create_absorber_task')  # noqa: F811
    async def create_absorber_task(*args, **kwargs):
        nonlocal times_called
        times_called += 1

    # same token should still work after exception
    response = await web_app_client.post(
        '/v1/communication/bulk/verify',
        json={'campaign_id': 123, 'group_id': 123},
        headers={'X-Idempotency-Token': idempotency_token},
    )
    assert response.status == 200
    assert times_called == 2


async def test_new_verify_communication_idempotency_request_error(
        web_app_client, patch,
):
    times_called = 0

    @patch('crm_hub.logic.yt_absorber_v2.create_absorber_task')
    async def create_absorber_task(*args, **kwargs):
        nonlocal times_called
        times_called += 1
        raise asyncpg.exceptions.UniqueViolationError(
            'this exception expected to be caught inside in api handle func',
        )

    idempotency_token = '5d7d1d3d-0a32-4c63-88ad-865d1aaaa01e'
    response = await web_app_client.post(
        '/v1/communication/bulk/verify',
        json={'campaign_id': 123, 'group_id': 123},
        headers={'X-Idempotency-Token': idempotency_token},
    )
    assert response.status == 422
    assert times_called == 1

    @patch('crm_hub.logic.yt_absorber_v2.create_absorber_task')  # noqa: F811
    async def create_absorber_task(*args, **kwargs):
        nonlocal times_called
        times_called += 1

    # same token should still work after error
    response = await web_app_client.post(
        '/v1/communication/bulk/verify',
        json={'campaign_id': 123, 'group_id': 123},
        headers={'X-Idempotency-Token': idempotency_token},
    )
    assert response.status == 200
    assert times_called == 2


async def test_new_verify_communication_idempotency_request_processing_error(
        web_context, web_app_client, patch,
):
    request_path = '/v1/communication/bulk/verify'
    idempotency_token = '5d7d1d3d-0a32-4c63-88ad-865d1aaaa01e'
    timestamp = dates.utcnow()
    query, binds = web_context.sqlt.idempotency_checker_create(
        created_at=timestamp,
        updated_at=timestamp,
        id=idempotency_token,
        path=request_path,
        state='processing',
    )
    async with web_context.pg.master_pool.acquire() as conn:
        await conn.execute(query, *binds)

    response = await web_app_client.post(
        request_path,
        json={'campaign_id': 123, 'group_id': 123},
        headers={'X-Idempotency-Token': idempotency_token},
    )
    assert response.status == 409
