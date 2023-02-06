import pytest

from tests_fleet_offers import utils

ENDPOINT = '/driver/v1/fleet-offers/v1/offer/accept'
MOCK_ENDPOINT = '/personal/v1/identifications/store'


def build_body(offer_id, rev):
    return {'id': offer_id, 'rev': rev}


OK_PARAMS = [
    ('00000000-0000-0000-0000-000000000001', 1, 1, 0),
    ('00000000-0000-0000-0000-000000000001', 2, 101, 1),
    ('00000000-0000-0000-0000-000000000002', 0, 201, 1),
]


@pytest.fixture
def _mock_unique_drivers(mockserver):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _mock_unique_drivers(request):
        return {
            'uniques': [
                {
                    'park_driver_profile_id': 'park1_driver1',
                    'data': {'unique_driver_id': 'unique_driver1'},
                },
            ],
        }


@pytest.mark.parametrize(
    'offer_id, rev, number, personal_store_calls', OK_PARAMS,
)
async def test_ok(
        taxi_fleet_offers,
        _mock_unique_drivers,
        mockserver,
        pgsql,
        offer_id,
        rev,
        number,
        personal_store_calls,
):
    @mockserver.json_handler(MOCK_ENDPOINT)
    def mock_store(request):
        return mockserver.make_response(
            json={'id': 'pd_id1', 'value': 'some_value'}, status=200,
        )

    response = await taxi_fleet_offers.post(
        ENDPOINT,
        headers=utils.build_taximeter_headers(
            park_id='park1', driver_id='driver1',
        ),
        json=build_body(offer_id=offer_id, rev=rev),
    )

    assert response.status_code == 204, response.text

    assert mock_store.times_called == personal_store_calls

    cursor = pgsql['fleet_offers'].cursor()
    cursor.execute(
        f"""
        SELECT
            rev,
            passport_pd_id,
            number
        FROM
            fleet_offers.accepted_offers
        WHERE
            park_id = \'park1\'
            AND client_id = \'driver1\'
            AND id = \'{offer_id}\'
        """,
    )
    row = cursor.fetchone()
    assert row[0] == rev
    assert row[1] == 'pd_id1'
    assert row[2] == number


async def test_already_accepted(taxi_fleet_offers, _mock_unique_drivers):

    response = await taxi_fleet_offers.post(
        ENDPOINT,
        headers=utils.build_taximeter_headers(
            park_id='park1', driver_id='driver1',
        ),
        json=build_body(
            offer_id='00000000-0000-0000-0000-000000000001', rev=0,
        ),
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'offer_already_signed',
        'localized_message': 'Оферта уже принята',
    }


async def test_service_agreement_ok(
        taxi_fleet_offers, _mock_unique_drivers, mockserver, pgsql,
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

    response = await taxi_fleet_offers.post(
        ENDPOINT,
        headers=utils.build_taximeter_headers(
            park_id='park1', driver_id='driver1',
        ),
        json=build_body(
            offer_id='00000000-0000-0000-0000-000000000000', rev=0,
        ),
    )

    assert response.status_code == 204, response.text

    cursor = pgsql['fleet_offers'].cursor()
    cursor.execute(
        f"""
        SELECT
            COUNT(*)
        FROM
            fleet_offers.service_agrees
        WHERE
            unique_driver_id = \'unique_driver1\'
        """,
    )
    row = cursor.fetchone()
    assert row[0] == 1


NOT_FOUND_PARAMS = [
    ('00000000-0000-0000-0000-000000000001', 10),
    ('00000000-0000-0000-0000-100000000001', 0),
]


@pytest.mark.parametrize('offer_id, rev', NOT_FOUND_PARAMS)
async def test_not_found(
        taxi_fleet_offers, _mock_unique_drivers, offer_id, rev,
):
    response = await taxi_fleet_offers.post(
        ENDPOINT,
        headers=utils.build_taximeter_headers(
            park_id='park1', driver_id='driver1',
        ),
        json=build_body(offer_id=offer_id, rev=rev),
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'offer_not_found',
        'localized_message': 'Оферта не найдена',
    }
