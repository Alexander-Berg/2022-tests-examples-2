# pylint: disable=protected-access
import json

import pytest


@pytest.mark.parametrize(
    'request_body, expected_status, expected_response',
    [
        ({}, 400, {'schemas': []}),
        (
            {
                'source_type': 'postgres',
                'schema_database': 'does-not-exist',
                'source_ident': 'table_name',
            },
            400,
            None,
        ),
        (
            {
                'source_type': 'postgres',
                'source_ident': 'table_name',
                'secret': {
                    'secret_id': 'STRONGBOX_ID',
                    'secret_type': 'strongbox',
                },
            },
            404,
            None,
        ),
    ],
)
async def test_schemas_retrieve(
        replication_client, request_body, expected_status, expected_response,
):
    response = await replication_client.post(
        f'/schemas/v1/source/retrieve', data=json.dumps(request_body),
    )
    assert response.status == expected_status, await response.text()
    if expected_status == 200:
        assert await response.json() == expected_response
