import pytest

from tests_fleet_offers import utils

ENDPOINT = '/driver/v1/fleet-offers/v1/not-signed/list'
UNIQUE_DRIVERS_MOCK_ENDPOINT = (
    '/unique-drivers/v1/driver/uniques/retrieve_by_profiles'
)


def build_params(section_id):
    return {'section_id': section_id}


OK_PARAMS = [
    ('main', 'unique_driver1', False, 'test_ok_main_unique_driver1.json'),
    (
        'main',
        'unique_driver1',
        True,
        'test_ok_main_unique_driver1_checkbox.json',
    ),
    (
        'balance',
        'unique_driver1',
        False,
        'test_ok_balance_unique_driver1.json',
    ),
    (
        'balance',
        'unique_driver2',
        False,
        'test_ok_balance_unique_driver2.json',
    ),
]


@pytest.fixture
def _mock_mds(mockserver):
    @mockserver.handler(f'/park1/00000000-0000-0000-0000-000000000003/0')
    def _mock_mds_3_0(request):
        return mockserver.make_response('OK', 200)

    @mockserver.handler(f'/park1/00000000-0000-0000-0000-000000000004/1')
    def _mock_mds_4_1(request):
        return mockserver.make_response('OK', 200)

    @mockserver.handler(f'/park1/00000000-0000-0000-0000-000000000005/0')
    def _mock_mds_5_0(request):
        return mockserver.make_response('OK', 200)

    @mockserver.handler(f'/park1/00000000-0000-0000-0000-000000000006/0')
    def _mock_mds_6_0(request):
        return mockserver.make_response('OK', 200)


@pytest.mark.parametrize(
    'section_id, mock_unique_driver, '
    'need_service_agreemet_checkbox, expected_response',
    OK_PARAMS,
)
async def test_ok(
        taxi_fleet_offers,
        _mock_mds,
        mockserver,
        load_json,
        experiments3,
        section_id,
        mock_unique_driver,
        need_service_agreemet_checkbox,
        expected_response,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/identity-docs/retrieve_by_park_driver_profile_id',
    )
    def _mock_driver_profiles(request):
        return {
            'docs_by_park_driver_profile_id': [
                {
                    'park_driver_profile_id': 'park1_driver1',
                    'docs': [
                        {'data': {'data_pd_id': 'pd_id1'}, 'id': 'doc_id'},
                    ],
                },
            ],
        }

    @mockserver.json_handler('/personal/v1/identifications/retrieve')
    def _mock_personal(request):
        return {
            'id': request.json['id'],
            'value': (
                '{'
                '"last_name": "Иванов", '
                '"first_name": "Иван", '
                '"patronymic": "Иваныч", '
                '"number": "1221 123456", '
                '"issue_date": "2002-02-16T00:00:00.0000000"'
                '}'
            ),
        }

    @mockserver.json_handler(UNIQUE_DRIVERS_MOCK_ENDPOINT)
    def _mock_unique_drivers(request):
        return {
            'uniques': [
                {
                    'park_driver_profile_id': 'park1_driver1',
                    'data': {'unique_driver_id': mock_unique_driver},
                },
            ],
        }

    experiments3.add_config(
        name='fleet_offers_service_agreement_checkbox',
        consumers=['fleet-offers/driver/not-signed/list'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'enabled': need_service_agreemet_checkbox},
    )

    response = await taxi_fleet_offers.get(
        ENDPOINT,
        headers=utils.build_taximeter_headers(
            park_id='park1', driver_id='driver1',
        ),
        params=build_params(section_id=section_id),
    )

    assert response.status_code == 200, response.text
    assert response.json() == load_json(expected_response)


EMPTY_DRIVER_PROFILE_PARAMS = [
    {'docs_by_park_driver_profile_id': []},
    {
        'docs_by_park_driver_profile_id': [
            {'park_driver_profile_id': 'park1_driver1', 'docs': []},
        ],
    },
]


@pytest.mark.parametrize('mock_response', EMPTY_DRIVER_PROFILE_PARAMS)
async def test_empty_driver_profiles(
        taxi_fleet_offers, _mock_mds, mockserver, load_json, mock_response,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/identity-docs/retrieve_by_park_driver_profile_id',
    )
    def _mock_driver_profiles(request):
        return mock_response

    @mockserver.json_handler(UNIQUE_DRIVERS_MOCK_ENDPOINT)
    def _mock_unique_drivers(request):
        return {
            'uniques': [
                {
                    'park_driver_profile_id': 'park1_driver1',
                    'data': {'unique_driver_id': 'unique_driver1'},
                },
            ],
        }

    response = await taxi_fleet_offers.get(
        ENDPOINT,
        headers=utils.build_taximeter_headers(
            park_id='park1', driver_id='driver1',
        ),
        params=build_params(section_id='main'),
    )

    assert response.status_code == 200, response.text
    assert response.json() == load_json('test_empty_driver_profiles.json')


async def test_not_found(taxi_fleet_offers):
    response = await taxi_fleet_offers.get(
        ENDPOINT,
        headers=utils.build_taximeter_headers(
            park_id='park1', driver_id='driver1',
        ),
        params=build_params(section_id='invalid'),
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'section_not_found',
        'localized_message': 'Раздел не найден',
    }
