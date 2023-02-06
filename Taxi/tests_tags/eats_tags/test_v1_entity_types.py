import pytest

_SUPPORTED_ENTITY_TYPES = [
    'brand_id',
    'category_id',
    'personal_phone_id',
    'place_id',
    'user_id',
]


@pytest.mark.nofilldb()
async def test_entity_types(taxi_eats_tags):
    await taxi_eats_tags.invalidate_caches()
    response = await taxi_eats_tags.get('v1/entity_types')
    assert response.status_code == 200
    response_entity_types = response.json()['entity_types']
    assert sorted(response_entity_types) == _SUPPORTED_ENTITY_TYPES
