from typing import List

import pytest

from tests_ride_discounts import common

PRIORITY_CHECK_URL = '/v1/admin/priority/check/'

PRIORITIZED_ENTITY_TYPE = 'class'


@pytest.mark.parametrize(
    'handler',
    (
        pytest.param(common.PRIORITY_URL, id='priority'),
        pytest.param(PRIORITY_CHECK_URL, id='check_priority'),
    ),
)
@pytest.mark.parametrize(
    'expected_status_code, entities_names',
    (
        pytest.param(200, [], id='OK_with_0_class'),
        pytest.param(200, ['experimental'], id='OK_with_1_class'),
        pytest.param(400, ['another_class'], id='KO_with_1_class'),
        pytest.param(
            200, ['experimental', 'another_class'], id='OK_with_2_class',
        ),
        pytest.param(
            400, ['another_class', 'experimental'], id='KO_with_2_class',
        ),
    ),
)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_priority_experimental_is_first(
        client,
        headers,
        handler: str,
        expected_status_code: int,
        entities_names: List[str],
):
    """
    A test to check that the experimental class is the first,
    otherwise the handler should give an error 400
    """
    request_body = {
        'priority_groups': [
            {'name': 'default', 'entities_names': entities_names},
        ],
        'prioritized_entity_type': PRIORITIZED_ENTITY_TYPE,
    }
    priority_warning = {
        'code': 'Validation error',
        'message': 'It is expected that the first class is \'experimental\'',
    }
    headers = (
        common.get_headers()
        if handler == PRIORITY_CHECK_URL
        else common.get_draft_headers()
    )
    response = await client.post(handler, request_body, headers=headers)
    assert response.status_code == expected_status_code
    if expected_status_code == 400:
        assert response.json() == priority_warning
