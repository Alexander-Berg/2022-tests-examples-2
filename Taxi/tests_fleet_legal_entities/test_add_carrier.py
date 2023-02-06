import pytest

from tests_fleet_legal_entities import utils

COUNTRIES = {
    'rus': {'field_ids': ['work_hours'], 'registration_number_alias': 'ogrn'},
}

PARK_ID = 'park_id_add'
PARK_ID_BLR = 'park_id4'
PARK_ID_DOUBLE = 'park_id1'

REGISTRATION_NUMBER = '12356'
REGISTRATION_NUMBER_DOUBLE = '1173468000539'

ENDPOINT = '/fleet/fleet-legal-entities/v1/carrier'

DEFAULT_WORK_HOURS = '9:00 - 18:00'


def _wrong_param(registration_number):
    return {
        'registration_number': registration_number,
        'name': 'different',
        'address': 'not equal',
    }


def _build_headers(park_id):
    return {
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
        'Accept-Language': 'ru',
    }


ADDRESS = {
    'value': 'Что-нибудь',
    'unrestricted_value': '',
    'data': {'source': 'doesnt matter'},
}


@pytest.mark.parametrize(
    ('registration_number', 'park_id', 'name', 'address'),
    [
        (
            REGISTRATION_NUMBER,
            PARK_ID,
            'ИП Александрова Татьяна Борисовна',
            'Что-нибудь',
        ),
        (
            REGISTRATION_NUMBER,
            PARK_ID_BLR,
            'ИП Сухаревич Иван Филиппович',
            None,
        ),
    ],
)
@pytest.mark.config(FLEET_LEGAL_ENTITIES_FIELDS_BY_COUNTRY=COUNTRIES)
async def test_add_carrier(
        taxi_fleet_legal_entities,
        mock_fleet_parks_list,
        mock_dadata_suggestions,
        mock_blr_api,
        mongodb,
        registration_number,
        park_id,
        name,
        address,
):
    mock_dadata_suggestions.data.suggest_response = {
        'suggestions': [
            utils.make_suggest_item(
                registration_number, name, ADDRESS, 'INDIVIDUAL',
            ),
        ],
    }
    mock_blr_api.data.main_response = [
        {
            'vfio': 'Сухаревич Иван Филиппович',
            'ngrn': int(registration_number),
            'vfn': 'something',
            'nsi00219': {'vnsostk': 'Действующий', 'nksost': 1},
        },
    ]

    response = await taxi_fleet_legal_entities.post(
        ENDPOINT,
        headers=_build_headers(park_id),
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

    if address:
        assert mongo_response['address'] == address
    assert mongo_response['created_date'] == mongo_response['modified_date']
    assert mongo_response['registration_number'] == registration_number
    assert mongo_response['park_id'] == park_id
    assert mongo_response['type'] == 'carrier_permit_owner'
    assert mongo_response['name'] == name
    assert mongo_response['legal_type'] == 'private'
    assert mongo_response['work_hours'] == DEFAULT_WORK_HOURS


@pytest.mark.parametrize(
    (
        'registration_number',
        'park_id',
        'body',
        'dadata_response',
        'response_code',
    ),
    [
        (
            REGISTRATION_NUMBER,
            PARK_ID,
            _wrong_param(REGISTRATION_NUMBER),
            utils.make_suggest_item(
                REGISTRATION_NUMBER,
                'ИП Александрова Татьяна Борисовна',
                ADDRESS,
                'INDIVIDUAL',
            ),
            500,
        ),
        (
            REGISTRATION_NUMBER,
            PARK_ID_BLR,
            _wrong_param(REGISTRATION_NUMBER),
            None,
            500,
        ),
        (
            REGISTRATION_NUMBER_DOUBLE,
            'park_id1',
            {
                'registration_number': REGISTRATION_NUMBER_DOUBLE,
                'name': 'БИЗНЕС ГАРД ОА ООО',
                'address': 'Что-нибудь',
            },
            utils.make_suggest_item(
                REGISTRATION_NUMBER_DOUBLE,
                'БИЗНЕС ГАРД ОА ООО',
                ADDRESS,
                'INDIVIDUAL',
            ),
            400,
        ),
    ],
)
@pytest.mark.config(FLEET_LEGAL_ENTITIES_FIELDS_BY_COUNTRY=COUNTRIES)
async def test_errors(
        taxi_fleet_legal_entities,
        mock_dadata_suggestions,
        mock_blr_api,
        mock_fleet_parks_list,
        dadata_response,
        body,
        park_id,
        registration_number,
        response_code,
):
    mock_dadata_suggestions.data.suggest_response = {
        'suggestions': [dadata_response],
    }
    mock_blr_api.data.main_response = [
        {
            'vfio': 'a',
            'ngrn': int(registration_number),
            'vfn': 'something',
            'nsi00219': {'vnsostk': 'Действующий', 'nksost': 1},
        },
    ]

    response = await taxi_fleet_legal_entities.post(
        ENDPOINT, headers=_build_headers(park_id), json=body,
    )

    assert response.status_code == response_code


@pytest.mark.config(FLEET_LEGAL_ENTITIES_FIELDS_BY_COUNTRY=COUNTRIES)
async def test_add_carrier_not_found(
        taxi_fleet_legal_entities,
        mock_fleet_parks_list,
        mock_dadata_suggestions,
):
    response = await taxi_fleet_legal_entities.post(
        ENDPOINT,
        headers=_build_headers(PARK_ID),
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
