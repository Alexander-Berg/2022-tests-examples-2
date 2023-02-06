import json

import pytest


@pytest.mark.now('2019-09-01T01:12:00+0000')
async def test_source_schemas_keeper(replication_client):
    request_body = {
        'source_type': 'postgres',
        'secret': {'secret_type': 'yav', 'secret_id': 'sec-example_pg'},
        'source_ident': 'just_table',
    }
    expected_response_text = (
        '{"schemas": [{"schemas": [{"source_ident": "just_table", '
        '"primary_keys": ["id", "doc_type"], "schema": [{"name": "id", '
        '"type": "varchar"}, {"name": "doc_type", "type": "varchar"}, '
        '{"name": "total", "type": "numeric"}, {"name": "created_at", '
        '"type": "timestamp"}, {"name": "modified_at", "type": "timestamp"}]}'
        '], "source_type": "postgres"}]}'
    )
    response = await replication_client.post(
        f'/schemas/v1/source/retrieve', data=json.dumps(request_body),
    )
    assert response.status == 200
    text = await response.text()
    assert text == expected_response_text
