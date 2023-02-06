import pytest

COUNTRIES = {
    'rus': {'field_ids': ['work_hours'], 'registration_number_alias': 'ogrn'},
}

PARK_ID = 'park_id1'
CARRIER_ID = '5c223136de2a722c67dc3090'
CARRIER_ID_NOT_FOUND = '5c23cd56de2a722c67f5d000'

ENDPOINT = '/fleet/fleet-legal-entities/v1/carrier'


def _build_headers(park_id):
    return {
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
        'Accept-Language': 'ru',
    }


RUS_RESPONSE = {
    'id': '5c223136de2a722c67dc3090',
    'fields': {
        'registration_number': '1173468000539',
        'name': 'БИЗНЕС ГАРД ОА ООО',
        'address': 'г Красноярск, ул Красной Армии, д 10',
        'additional_fields': [
            {'alias': 'work_hours', 'value': '9:00 - 18:00'},
        ],
    },
}


@pytest.mark.config(FLEET_LEGAL_ENTITIES_FIELDS_BY_COUNTRY=COUNTRIES)
async def test_get_carrier(taxi_fleet_legal_entities, mock_fleet_parks_list):
    response = await taxi_fleet_legal_entities.get(
        ENDPOINT,
        headers=_build_headers(PARK_ID),
        params={'carrier_id': CARRIER_ID},
    )

    assert response.status_code == 200
    assert response.json() == RUS_RESPONSE


@pytest.mark.config(FLEET_LEGAL_ENTITIES_FIELDS_BY_COUNTRY=COUNTRIES)
async def test_get_carrier_not_found(
        taxi_fleet_legal_entities, mock_fleet_parks_list,
):
    response = await taxi_fleet_legal_entities.get(
        ENDPOINT,
        headers=_build_headers(PARK_ID),
        params={'carrier_id': CARRIER_ID_NOT_FOUND},
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'carrier_not_found',
        'message': 'Carrier not found',
    }
