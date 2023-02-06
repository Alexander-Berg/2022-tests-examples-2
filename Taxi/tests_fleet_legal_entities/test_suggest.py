import pytest

from tests_fleet_legal_entities import utils

COUNTRIES = {
    'rus': {'field_ids': ['work_hours'], 'registration_number_alias': 'ogrn'},
    'blr': {'field_ids': [], 'registration_number_alias': 'unp'},
}

PARK_ID_RUS = 'park_id1'
PARK_ID_BLR = 'park_id4'
PARK_ID_COUNTRY_NOT_SUPPORTED = 'park_id3'

REGISTRATION_NUMBER = '5c223136de2a722c67dc3090'
REGISTRATION_NUMBER_INT = 12356

SERVICE_ENDPOINT = '/fleet/fleet-legal-entities/v1/carrier/suggest'


def _build_headers(park_id):
    return {
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
        'Accept-Language': 'ru',
    }


@pytest.mark.parametrize(
    ('park_id', 'registration_number', 'service_response'),
    [
        (
            PARK_ID_RUS,
            REGISTRATION_NUMBER,
            {
                'registration_number': REGISTRATION_NUMBER,
                'name': 'ООО рогаИкопыта',
            },
        ),
        (
            PARK_ID_BLR,
            REGISTRATION_NUMBER_INT,
            {
                'registration_number': str(REGISTRATION_NUMBER_INT),
                'name': 'КФХ \"ГречинкаАгро\"',
                'address': (
                    'Могилевская область Бобруйский район Горбацевичский '
                    'сельсовет аг. Горбацевичи, Клубная, 1А'
                ),
            },
        ),
    ],
)
@pytest.mark.config(FLEET_LEGAL_ENTITIES_FIELDS_BY_COUNTRY=COUNTRIES)
async def test_suggest(
        taxi_fleet_legal_entities,
        mock_fleet_parks_list,
        mock_dadata_suggestions,
        mockserver,
        mock_blr_api,
        park_id,
        registration_number,
        service_response,
):
    mock_dadata_suggestions.data.suggest_response = {
        'suggestions': [
            utils.make_suggest_item(
                REGISTRATION_NUMBER, 'ООО рогаИкопыта', None, 'LEGAL',
            ),
        ],
    }
    mock_blr_api.data.main_response = [
        {
            'vn': 'КФХ \"ГречинкаАгро\"',
            'ngrn': registration_number,
            'vfn': 'something',
            'nsi00219': {'vnsostk': 'Действующий', 'nksost': 1},
        },
    ]

    mock_blr_api.data.address_response = [
        {
            'vulitsa': 'Клубная',
            'vdom': '1А',
            'ngrn': registration_number,
            'nsi00202': {
                'vnsfull': (
                    'Могилевская область Бобруйский район'
                    ' Горбацевичский сельсовет аг. Горбацевичи'
                ),
            },
        },
    ]

    response = await taxi_fleet_legal_entities.post(
        SERVICE_ENDPOINT,
        headers=_build_headers(park_id),
        params={'registration_number': str(registration_number)},
    )

    assert response.status_code == 200
    assert response.json() == service_response


@pytest.mark.parametrize(
    ('park_id', 'registration_number', 'service_response'),
    [
        (
            PARK_ID_RUS,
            REGISTRATION_NUMBER,
            {'code': 'carrier_not_found', 'message': 'Carrier not found'},
        ),
        (
            PARK_ID_BLR,
            REGISTRATION_NUMBER_INT,
            {'code': 'carrier_not_found', 'message': 'Carrier not found'},
        ),
        (
            PARK_ID_COUNTRY_NOT_SUPPORTED,
            '12',
            {
                'code': 'country_not_supported',
                'message': 'Country not supported',
            },
        ),
        (
            PARK_ID_BLR,
            REGISTRATION_NUMBER,
            {'code': 'carrier_not_found', 'message': 'Carrier not found'},
        ),
    ],
)
@pytest.mark.config(FLEET_LEGAL_ENTITIES_FIELDS_BY_COUNTRY=COUNTRIES)
async def test_suggest_errors(
        taxi_fleet_legal_entities,
        mock_fleet_parks_list,
        mock_dadata_suggestions,
        mock_blr_api,
        park_id,
        registration_number,
        service_response,
):
    mock_dadata_suggestions.data.suggest_response = {'suggestions': []}

    response = await taxi_fleet_legal_entities.post(
        SERVICE_ENDPOINT,
        headers=_build_headers(park_id),
        params={'registration_number': registration_number},
    )

    assert response.status_code == 404
    assert response.json() == service_response
