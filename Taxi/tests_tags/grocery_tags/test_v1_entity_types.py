import pytest

_SUPPORTED_ENTITY_TYPES = [
    'item_id',
    'personal_phone_id',
    'store_id',
    'store_item_id',
    'yandex_uid',
]


@pytest.mark.nofilldb()
async def test_entity_types(taxi_grocery_tags):
    await taxi_grocery_tags.invalidate_caches()
    response = await taxi_grocery_tags.get('v1/entity_types')
    assert response.status_code == 200
    response_entity_types = response.json()['entity_types']
    assert sorted(response_entity_types) == _SUPPORTED_ENTITY_TYPES
