from dateutil import parser
import pytest

from eats_catalog import storage


@pytest.mark.now('2021-05-07T10:00:00+00:00')
async def test_slug_time_zone(taxi_eats_catalog, eats_catalog_storage):
    """
    EDACAT-959: проверяет, что для отрисовки времен на слаге при запросе
    без координат используется временная зона заведения
    """

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-05-07T08:00:00+00:00'),
            end=parser.parse('2021-05-07T17:52:00+00:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            slug='some',
            region=storage.Region(time_zone='Australia/Eucla'),
            working_intervals=schedule,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(place_id=1, zone_id=1, working_intervals=schedule),
    )

    response = await taxi_eats_catalog.get(
        '/eats-catalog/v1/slug/some',
        headers={
            'x-device-id': 'test_simple',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data['payload']['availableTimePicker'] == [
        [
            '2021-05-07T19:00:00+08:45',
            '2021-05-07T19:30:00+08:45',
            '2021-05-07T20:00:00+08:45',
            '2021-05-07T20:30:00+08:45',
            '2021-05-07T21:00:00+08:45',
            '2021-05-07T21:30:00+08:45',
            '2021-05-07T22:00:00+08:45',
            '2021-05-07T22:30:00+08:45',
            '2021-05-07T23:00:00+08:45',
            '2021-05-07T23:30:00+08:45',
            '2021-05-08T00:00:00+08:45',
        ],
        [
            '2021-05-08T00:30:00+08:45',
            '2021-05-08T01:00:00+08:45',
            '2021-05-08T01:30:00+08:45',
            '2021-05-08T02:00:00+08:45',
            '2021-05-08T02:30:00+08:45',
        ],
    ]

    footer = data['payload']['foundPlace']['place']['footerDescription']
    assert footer == (
        'Исполнитель (продавец): '
        'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "КОФЕ БОЙ", '
        '127015, Москва, ул Вятская, д 27, стр 11, ИНН 7714457772, '
        'рег.номер 1207700043759.<br>Режим работы: с 16:45 до 24:00'
    )
