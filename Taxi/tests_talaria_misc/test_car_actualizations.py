import pytest


def get_photos(pgsql):
    fields = [
        'order_id',
        'photo_uuid',
        'md5',
        'personal_phone_id',
        'yandex_uid',
        'path',
    ]

    fields_str = ','.join(fields)
    cursor = pgsql['talaria_misc'].cursor()

    cursor.execute(f'SELECT {fields_str} FROM talaria_misc.photofixation;')
    photos = []
    rows = cursor.fetchall()
    for row in rows:
        row = list(row)
        photo = dict()
        for i, field in enumerate(fields):
            photo[field] = row[i]
        photos.append(photo)
    return photos


async def test_car_actualization(taxi_talaria_misc, default_pa_headers, pgsql):
    response = await taxi_talaria_misc.post(
        '/4.0/scooters/api/yandex/car/actualization',
        json={
            'photos': [{'uuid': 'uuid', 'md5': 'md5', 'marker': 'marker'}],
            'session_id': 'order_id',
        },
        headers=default_pa_headers('123'),
    )
    assert response.status_code == 200
    assert [
        {
            'order_id': 'order_id',
            'md5': 'md5',
            'photo_uuid': 'uuid',
            'personal_phone_id': '123',
            'yandex_uid': 'yandex_uid',
            'path': 'order_id/uuid',
        },
    ] == get_photos(pgsql)
