import pytest

from tests_tags.tags import constants


@pytest.mark.nofilldb()
async def test_entity_types(taxi_tags):
    await taxi_tags.invalidate_caches()
    response = await taxi_tags.get('v1/entity_types')
    assert response.status_code == 200
    response_entity_types = response.json()['entity_types']
    assert sorted(response_entity_types) == sorted(
        constants.SUPPORTED_ENTITY_TYPES,
    )
