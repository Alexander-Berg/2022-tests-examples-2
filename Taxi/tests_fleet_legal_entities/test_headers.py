import pytest

COUNTRIES = {
    'rus': {'field_ids': ['work_hours'], 'registration_number_alias': 'ogrn'},
}

PARK_ID = 'park_id1'
PARK_ID_NOT_FOUND = '1111'

ENDPOINT = '/fleet/fleet-legal-entities/v1/carriers/headers'


def _build_headers(park_id):
    return {
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
        'Accept-Language': 'ro',
    }


RUS_RESPONSE = {
    'registration_number': 'ОГРН',
    'address': 'Адрес',
    'name': 'Название',
    'additional_headers': [
        {'field_id': 'work_hours', 'field_name': 'Часы работы'},
    ],
}

TRANSLATIONS = {
    'address': {'ru': 'Адрес'},
    'name': {'ru': 'Название'},
    'ogrn': {'ru': 'ОГРН'},
    'work_hours': {'ru': 'Часы работы'},
}


@pytest.mark.config(FLEET_LEGAL_ENTITIES_FIELDS_BY_COUNTRY=COUNTRIES)
@pytest.mark.translations(backend_fleet_legal_entities=TRANSLATIONS)
async def test_get_headers(taxi_fleet_legal_entities, mock_fleet_parks_list):
    response = await taxi_fleet_legal_entities.get(
        ENDPOINT, headers=_build_headers(PARK_ID),
    )

    assert response.status_code == 200
    assert response.json() == RUS_RESPONSE


async def test_get_headers_park_not_found(
        taxi_fleet_legal_entities, mock_fleet_parks_list,
):
    response = await taxi_fleet_legal_entities.get(
        ENDPOINT, headers=_build_headers(PARK_ID_NOT_FOUND),
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'park_not_found',
        'message': 'Park not found',
    }
