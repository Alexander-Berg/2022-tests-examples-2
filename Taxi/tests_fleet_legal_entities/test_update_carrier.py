import datetime

import pytest
import pytz

from tests_fleet_legal_entities import utils

COUNTRIES = {
    'rus': {'field_ids': ['work_hours'], 'registration_number_alias': 'ogrn'},
}

REGISTRATION_NUMBER = '12356'
PARK_ID = 'park_id1'
PARK_ID_BLR = 'park_id4'
ENDPOINT = '/fleet/fleet-legal-entities/v1/carrier'


def _check_modified_date(modified_date):
    delta = datetime.datetime.now(datetime.timezone.utc) - modified_date
    assert datetime.timedelta() <= delta < datetime.timedelta(minutes=1), delta


def _build_headers(park_id):
    return {
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
        'Accept-Language': 'ru',
    }


ADDRESS = {
    'value': 'updated_address',
    'unrestricted_value': '',
    'data': {'source': 'doesnt matter'},
}


@pytest.mark.parametrize(
    ('carrier_id', 'registration_number', 'park_id', 'name', 'address'),
    [
        (
            '5c223136de2a722c67dc3090',
            REGISTRATION_NUMBER,
            PARK_ID,
            'updated_name',
            'updated_address',
        ),
        (
            '1c23cd56de2a722c67f5d111',
            REGISTRATION_NUMBER,
            PARK_ID_BLR,
            'updated_name',
            None,
        ),
    ],
)
@pytest.mark.config(FLEET_LEGAL_ENTITIES_FIELDS_BY_COUNTRY=COUNTRIES)
async def test_update_carrier(
        taxi_fleet_legal_entities,
        mock_fleet_parks_list,
        mock_dadata_suggestions,
        mock_blr_api,
        mongodb,
        carrier_id,
        registration_number,
        park_id,
        name,
        address,
):
    mock_dadata_suggestions.data.suggest_response = {
        'suggestions': [
            utils.make_suggest_item(
                registration_number, name, ADDRESS, 'LEGAL',
            ),
        ],
    }
    mock_blr_api.data.main_response = [
        {
            'vn': name,
            'ngrn': int(registration_number),
            'vfn': 'something',
            'nsi00219': {'vnsostk': 'Действующий', 'nksost': 1},
        },
    ]

    response = await taxi_fleet_legal_entities.put(
        ENDPOINT,
        headers=_build_headers(park_id),
        params={'carrier_id': carrier_id},
        json={
            'registration_number': registration_number,
            'name': name,
            'address': address,
        },
    )

    assert response.status_code == 204

    mongo_response = mongodb.dbparks_legal_entities.find_one(
        {'park_id': park_id, 'registration_number': registration_number},
    )

    assert mongo_response['registration_number'] == registration_number
    assert mongo_response['name'] == name
    if 'address' in mongo_response:
        assert mongo_response['address'] == address
    _check_modified_date(
        mongo_response['modified_date'].replace(tzinfo=pytz.utc),
    )


@pytest.mark.config(FLEET_LEGAL_ENTITIES_FIELDS_BY_COUNTRY=COUNTRIES)
async def test_update_carrier_not_found(
        taxi_fleet_legal_entities,
        mock_fleet_parks_list,
        mock_dadata_suggestions,
):
    response = await taxi_fleet_legal_entities.put(
        ENDPOINT,
        headers=_build_headers(PARK_ID),
        params={'carrier_id': id},
        json={
            'registration_number': 'some',
            'name': 'some',
            'address': 'some',
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'carrier_not_found',
        'message': 'Carrier not found',
    }
