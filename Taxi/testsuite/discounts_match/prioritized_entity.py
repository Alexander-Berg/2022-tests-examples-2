from typing import Optional

import pytest


@pytest.fixture
def add_prioritized_entity(
        client, prioritized_entity_url: str, draft_headers: dict,
):
    async def func(
            request_body: dict,
            expected_body: Optional[dict] = None,
            expected_status_code: int = 200,
    ):
        response = await client.post(
            prioritized_entity_url, request_body, headers=draft_headers,
        )
        assert response.status_code == expected_status_code, response.json()
        response_json = response.json()
        if expected_status_code == 200:
            assert response_json == request_body
        elif expected_body is not None:
            assert response_json == expected_body

    return func
