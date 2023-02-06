import pytest

_SUPPORTED_ENTITY_TYPES = [
    'corp_client_id',
    'personal_phone_id',
    'phone_hash_id',
    'user_id',
    'user_phone_id',
    'yandex_uid',
]


@pytest.mark.nofilldb()
async def test_entity_types(taxi_passenger_tags):
    await taxi_passenger_tags.invalidate_caches()
    response = await taxi_passenger_tags.get('v1/entity_types')
    assert response.status_code == 200
    response_entity_types = response.json()['entity_types']
    assert sorted(response_entity_types) == _SUPPORTED_ENTITY_TYPES
