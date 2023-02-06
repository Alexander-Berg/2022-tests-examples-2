import bson
import pytest


@pytest.mark.parametrize(
    'phone, phone_type', [('phone-3', 'yandex'), ('phone-1', 'partner')],
)
async def test_user_phones_remove_not_found(taxi_user_api, phone, phone_type):
    response = await taxi_user_api.post(
        '/user_phones/remove',
        json={'phone': phone, 'type': phone_type, 'ticket': 'TAXIBACKEND-123'},
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'phone, phone_type',
    [('phone-1', 'yandex'), ('phone-2', 'yandex'), ('phone-1', 'uber')],
)
async def test_user_phones_remove(taxi_user_api, mongodb, phone, phone_type):
    response = await taxi_user_api.post(
        '/user_phones/remove',
        json={'phone': phone, 'type': phone_type, 'ticket': 'TAXIBACKEND-123'},
    )
    assert response.status_code == 200
    response_json = response.json()

    base_type = 'deleted:{}:TAXIBACKEND-123:'.format(phone_type or 'yandex')
    assert response_json['new_type'].startswith(base_type)
    assert len(response_json['new_type']) == len(base_type) + 32

    doc = mongodb.user_phones.find_one(
        {'_id': bson.ObjectId(response_json['phone_id'])},
    )
    assert doc['phone'] == phone
    assert doc['type'] == response_json['new_type']
