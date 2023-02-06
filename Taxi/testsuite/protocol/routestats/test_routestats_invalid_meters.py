import bson.objectid
import pytest


@pytest.mark.parametrize(
    'price',
    [
        (
            {'dmi': -2, 'dpi': [], 'tmi': -1, 'tpi': []},
            {'dmi': 0, 'dpi': [], 'tmi': 1, 'tpi': []},
            {'dmi': 1, 'dpi': [], 'tmi': 0, 'tpi': []},
        ),
    ],
)
def test_invalid_tariff_meters(
        local_services, taxi_protocol, load_json, db, price,
):
    poputka_tariff_id = bson.objectid.ObjectId('585a6f47201dd1b2017a0eab')

    cursor = db.tariffs.find({'_id': poputka_tariff_id})
    count = cursor.count()
    assert count == 1
    poputka_record = cursor[0]

    category = poputka_record['categories'][0]
    category['m'] = []
    category['st'][0]['p'] = price
    db.tariffs.update({'_id': poputka_tariff_id}, {'$set': poputka_record})

    request = load_json('simple_request.json')
    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 404
